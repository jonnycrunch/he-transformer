#!/usr/bin/env bash

NGRAPH_HE_HEAAN_CONFIG=heaan_config_13.json NGRAPH_TF_BACKEND=HE_HEAAN python test_squash.py;
NGRAPH_HE_HEAAN_CONFIG=heaan_config_14.json NGRAPH_TF_BACKEND=HE_HEAAN python test_squash.py;
