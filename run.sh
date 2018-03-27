#!/bin/bash

# This script is a wrapper allowing main.py to work with relative module import

OLD_DIR=$(pwd)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
FILEPATH=$(readlink -f $1)

cd "${SCRIPT_DIR}/src"
python3 main.py ${FILEPATH}
cd ${OLD_DIR}
