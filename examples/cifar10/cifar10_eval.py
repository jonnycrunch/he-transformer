# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Evaluation for CIFAR-10.

Accuracy:
cifar10_train.py achieves 83.0% accuracy after 100K steps (256 epochs
of data) as judged by cifar10_eval.py.

Speed:
On a single Tesla K40, cifar10_train.py processes a single batch of 128 images
in 0.25-0.35 sec (i.e. 350 - 600 images /sec). The model reaches ~86%
accuracy after 100K steps in 8 hours of training time.

Usage:
Please see the tutorial and website for how to download the CIFAR-10
data set, compile the program and train the model.

http://tensorflow.org/tutorials/deep_cnn/
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import datetime
import math
import sys
import time

import numpy as np
import tensorflow as tf

import cifar10

FLAGS = None

import ngraph_bridge

import time

node_names = []

def eval_once(saver, summary_writer, top_k_op, summary_op):
  """Run Eval once.

  Args:
    saver: Saver.
    summary_writer: Summary writer.
    top_k_op: Top K op.
    summary_op: Summary op.
  """

  print("Calling eval once")
  with tf.Session() as sess:
    print('Creating session')


    ckpt = tf.train.get_checkpoint_state(FLAGS.checkpoint_dir)
    if ckpt and ckpt.model_checkpoint_path:
      # Restores from checkpoint
      saver.restore(sess, ckpt.model_checkpoint_path)
      # Assuming model_checkpoint_path looks something like:
      #   /my-favorite-path/cifar10_train/model.ckpt-0,
      # extract global_step from it.
      global_step = ckpt.model_checkpoint_path.split('/')[-1].split('-')[-1]
    else:
      print('No checkpoint file found')
      return


    # Convert variables to constants
    print('converting variables to constants')
    with tf.Graph().as_default() as g:
      tf.graph_util.convert_variables_to_constants(sess, g.as_graph_def(), node_names)
        # variable_names_whitelist=node_names)


    # Start the queue runners.
    if True:
      print("computing precision")
      coord = tf.train.Coordinator()
      try:
        threads = []
        for qr in tf.get_collection(tf.GraphKeys.QUEUE_RUNNERS):
          threads.extend(qr.create_threads(sess, coord=coord, daemon=True,
                                          start=True))

        num_iter = int(math.ceil(FLAGS.num_examples / 128))
        true_count = 0  # Counts the number of correct predictions.
        total_sample_count = num_iter * 128
        step = 0
        while step < num_iter and not coord.should_stop():
          predictions = sess.run([top_k_op])
          print('Sleeping')
          time.sleep(100)
          true_count += np.sum(predictions)
          step += 1

        # Compute precision @ 1.
        precision = true_count / total_sample_count


        print('%s: precision @ 1 = %.3f' % (datetime.datetime.now(), precision))

        summary = tf.Summary()
        summary.ParseFromString(sess.run(summary_op))
        summary.value.add(tag='Precision @ 1', simple_value=precision)
        summary_writer.add_summary(summary, global_step)
      except Exception as e:  # pylint: disable=broad-except
        coord.request_stop(e)
        print("Error in starting queue runners")

      coord.request_stop()
      coord.join(threads, stop_grace_period_secs=10)

      print("done computing precision")

    # Save variables
    for var in tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES):
      weight = (sess.run([var]))[0].flatten().tolist()
      filename = (str(var).split())[1].replace('/', '_')
      filename = filename.replace("'", "").replace(':0', '') + '.txt'

      print("saving", filename)
      np.savetxt(str(filename), weight)

def evaluate():
  """Eval CIFAR-10 for a number of steps."""
  with tf.Graph().as_default() as g:
    # Get images and labels for CIFAR-10.
    eval_data = FLAGS.eval_data == 'test'
    images, labels = cifar10.inputs(eval_data=eval_data)

    images = images[0:10]
    labels = labels[0:10]

    # Build a Graph that computes the logits predictions from the
    # inference model.
    logits = cifar10.he_inference(images)

    # Calculate predictions.
    top_k_op = tf.nn.in_top_k(logits, labels, 1)

    # Restore the moving average version of the learned variables for eval.
    variable_averages = tf.train.ExponentialMovingAverage(
        cifar10.MOVING_AVERAGE_DECAY)
    variables_to_restore = variable_averages.variables_to_restore()
    saver = tf.train.Saver(variables_to_restore)

    # Convert variables to constants
    node_names = [n.name for n in tf.get_default_graph().as_graph_def().node]
    node_names = [var.name for var in tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES)]
    print('node names', node_names)
    #get_node_names()
    #exit(1)
    '''
    node_names = [n.name for n in tf.get_default_graph().as_graph_def().node]
    print('node names', node_names)
    exit(1)
    with tf.Session() as sess:
      tf.graph_util.convert_variables_to_constants(sess, sess.graph.as_graph_def(), node_names)
    '''


    # Build the summary operation based on the TF collection of Summaries.
    summary_op = tf.summary.merge_all()

    summary_writer = tf.summary.FileWriter(FLAGS.eval_dir, g)

    while True:
      eval_once(saver, summary_writer, logits, summary_op)
      # eval_once(saver, summary_writer, top_k_op, summary_op)
      print('done with eval once')
      if FLAGS.run_once:
        break
      time.sleep(FLAGS.eval_interval_secs)



def main(argv=None):  # pylint: disable=unused-argument
  cifar10.maybe_download_and_extract()
  if tf.gfile.Exists(FLAGS.eval_dir):
    tf.gfile.DeleteRecursively(FLAGS.eval_dir)
  tf.gfile.MakeDirs(FLAGS.eval_dir)
  evaluate()


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--eval_dir',
      type=str,
      default='/tmp/cifar10_eval',
      help='Directory where to write event logs.')
  parser.add_argument(
      '--eval_data',
      type=str,
      default='test',
      help="""Either 'test' or 'train_eval'.""")
  parser.add_argument(
      '--checkpoint_dir',
      type=str,
      default='/tmp/cifar10_train',
      help="""Directory where to read model checkpoints.""")
  parser.add_argument(
      '--eval_interval_secs',
      type=int,
      default=60 * 5,
      help='How often to run the eval.')
  parser.add_argument(
      '--num_examples',
      type=int,
      default=10000,
      help='Number of examples to run.')
  parser.add_argument(
      '--run_once',
      type=bool,
      default=True,
      help='Whether to run eval only once.')

  FLAGS, unparsed = parser.parse_known_args()
  tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)