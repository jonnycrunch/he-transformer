# ******************************************************************************
# Copyright 2017-2018 Intel Corporation
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
# ******************************************************************************

include(ExternalProject)

set(EXTERNAL_NGRAPH_TF_INSTALL_DIR ${EXTERNAL_INSTALL_DIR})
set(NGRAPH_TF_CMAKE_PREFIX ext_ngraph_tf)

SET(NGRAPH_TF_REPO_URL https://github.com/NervanaSystems/ngraph-tf.git)
SET(NGRAPH_TF_GIT_LABEL a090ed8) # Nov. 28, 2018, commit #328

option(NGRAPH_TF_CXX11_ABI "Use CXX11 ABI for ngraph-tf" 0)

SET(COMPILE_FLAGS "${CMAKE_CXX_FLAGS} -DUSE_PRE_BUILT_NGRAPH=ON -DNGRAPH_ARTIFACTS_DIR=${CMAKE_INSTALL_PREFIX}")

ExternalProject_Add(
   ext_ngraph_tf DEPENDS install_tensorflow ext_ngraph
   GIT_REPOSITORY ${NGRAPH_TF_REPO_URL}
   GIT_TAG ${NGRAPH_TF_GIT_LABEL}
   PREFIX ${NGRAPH_TF_CMAKE_PREFIX}
   CMAKE_ARGS -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
                -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
                -DCMAKE_CXX_FLAGS=${COMPILE_FLAGS}
                -DNGRAPH_TF_CXX11_ABI=${NGRAPH_TF_CXX11_ABI}
   UPDATE_COMMAND ""
   INSTALL_COMMAND make install && pip install python/dist/ngraph_config-0.8.0rc0-py2.py3-none-linux_x86_64.whl
   TEST_COMMAND python -c "import tensorflow as tf; print('TensorFlow version: r',tf.__version__);import ngraph_bridge; print(ngraph_bridge.__version__)"
   #BUILD_ALWAYS 1
)