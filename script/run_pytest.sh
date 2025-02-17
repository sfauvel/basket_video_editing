#!/bin/bash

# Launch pytest command on docker with all parameters given to the script
# Usage example: . run_pytest.sh -v 
# The owner of files in docs folder is change to the caller user to be able to edit approved and received files. 

PYTHON_DOCKER_IMAGE=basket_python

SCRIPT_PATH=$(dirname "$0")

function run_on_docker {
  COMMAND=$*

  docker run \
    -v $(pwd):/project \
    -v $(readlink -f "$SCRIPT_PATH/../libs"):/libs \
    -v $(readlink -f "$SCRIPT_PATH"):/script \
    -w /project \
    -it $PYTHON_DOCKER_IMAGE \
    bash -c "${COMMAND}"
}

run_on_docker "pytest $*"

# run_on_docker "chmod -R a+w /project/docs"
# run_on_docker "pip install moviepy"
