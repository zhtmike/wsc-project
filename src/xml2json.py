#!/usr/bin/env python3
import argparse
import json
import urllib.request
import xml.etree.ElementTree as ET

URL = "http://www.cs.nyu.edu/faculty/davise/papers/WinogradSchemas/WSCollection.xml"


def parse_xml(schema):
    """
    Parse each schema in xml
    Args:
        schema (xml.etree.ElementTree.Element): each schema block

    Returns:
        sche (dict): schma dictionary, e.g,
        {
            "raw": "Since it was raining, I carried the newspaper in my backpack to keep it dry.",
            "quote": "dry",
            "pron": "it",
            "ans": {
                "A": "The newspaper",
                "B": "The backpack"
            },
            "correct": "A"
        }

    """
    sche = {}
    for elements in schema:
        if elements.tag == "text":
            sche["raw"] = ' '.join(
                [u.text.replace('\n', '').strip() for u in elements])
        elif elements.tag == "quote":
            for element in elements:
                if element.tag == "pron":
                    sche["pron"] = element.text.strip()
                elif element.tag == "quote1" and element.text is not None:
                    sche["quote"] = element.text.strip()
                elif element.tag == "quote2" and element.text is not None:
                    sche["quote"] = element.text.strip()
        elif elements.tag == "answers":
            sche["ans"] = {"A": elements[0].text.strip(
            ), "B": elements[1].text.strip()}
        elif elements.tag == "correctAnswer":
            sche["correct"] = elements.text.strip().strip('.')
    return sche


def xml2json(input="", output=""):
    """
    Parse xml to json-like dictionary
    Args:
        output (str): if it is non-empty, the dictionary will be saved into output path

    Returns:
        questions (dict): json-like dictionary
    """
    content = None
    if input:
        with open(input, 'r') as f:
            content = f.read()
    else:
        with urllib.request.urlopen(URL) as response:
            content = response.read()
    root = ET.fromstring(content)

    questions = [parse_xml(schema) for schema in root]
    if output != "":
        with open(output, 'w') as f:
            json.dump(questions, f, indent=2)
    return questions


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert xml to json file.')
    parser.add_argument('--input', dest='input', help='xml file path')
    parser.add_argument('-o', '--output', dest='output',
                        required=True, help='output file path')
    args = parser.parse_args()
    xml2json(args.input, args.output)
