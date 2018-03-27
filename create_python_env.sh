#!/bin/bash
set -e

# Download Miniconda
wget -N https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh

# Install Miniconda
bash Miniconda3-latest-Linux-x86_64.sh -b -u -p ./miniconda3

echo "Python 3 environment is successfully created."
