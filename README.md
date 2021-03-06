# Installation Guide (The Winograd Schema Challenge Project)

The installation script has been tested on Ubuntu 16.04.

## Prerequisite

1. A Java 8 environment is required to run Stanford CoreNLP.

2. A Python3 environment is required to run the scripts. A shell script `./create_python_env.sh` is provided to download Miniconda3 and install it locally.

## Installation

1. In the current directory, run `python -m pip install --user -r requirements.txt` to install all dependencies.

2. Download Stanford CoreNLP from <http://nlp.stanford.edu/software/stanford-corenlp-full-2017-06-09.zip> and unzip it into `./corenlp/`.

3. Download the model files <http://nlp.stanford.edu/software/stanford-english-corenlp-2017-06-09-models.jar> and <http://nlp.stanford.edu/software/stanford-english-kbp-corenlp-2017-06-09-models.jar> and save them in the same directory, e.g. `./corenlp/stanford-corenlp-full-2017-06-09/`.

## Running the script

1. Go to the Standord CoreNLP root directory, e.g. `./corenlp/stanford-corenlp-full-2017-06-09/`. Start the CoreNLP server by `java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000 &`

2. In the current directory, run the cases by
    1. Run the first test case: `./run.sh data/sample_0.xml`
    2. Run the second test case: `./run.sh data/sample_1.xml`
    3. Run the whole WSCollection: `./run.sh data/WSCollection.xml`

3. Output will be displayed in terminal directly.
