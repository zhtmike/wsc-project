#!/usr/bin/env python3
import argparse
import logging

import nlp
import anl
from xml2json import xml2json


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description='Analyzing a xml file')
    parser.add_argument('path', help='input xml path')
    args = parser.parse_args()

    # Read the xml
    logging.info("Parsing the xml file")
    contents = xml2json(input=args.path)

    # Start the server
    logging.info("Starting the nlp server")
    nlp_parser = nlp.NLPFactory()

    # Create a sentence parser
    logging.info("Parsing the dependencies")
    sentence_parser = anl.SentenceParser()
    correct, valid, total = 0, 0, 0
    for content in contents:
        total += 1
        raw = nlp_parser.annotate(content['raw'][:-1])
        ans = sentence_parser.anal(
            raw, content['pron'], content['ans']['A'], content['ans']['B'])
        print("Question:  %s" % content['raw'])
        if ans:
            valid += 1
            print("Expected:  %s" % content['ans'][content['correct']])
            print("Predicted: %s" % ans)
            if ans == content['ans'][content['correct']]:
                correct += 1
        else:
            print("Cannot find result.")
        print("-------------------------------------------------------------------------------")
    print('Total number of questions:          %d' % total)
    print('Total number of valid predictions:  %d' % valid)
    print('Total number of correct predctions: %d' % correct)
    print('Percentage of valid ans:            %f' % (valid / total))
    print('Percentage of correct ans:          %f' % (correct / valid))
