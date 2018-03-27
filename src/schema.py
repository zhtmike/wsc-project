import re

TEXTPATH = '../data/schemas-size12.txt'


def read_schemas(path=""):
    """
    Read the schemas from path
    """
    if not path:
        path = TEXTPATH
    with open(path, 'r') as f:
        raw = f.read()
        schema = [set(m.group(1).split())
                  for m in re.finditer("\[(.*?)\]", raw)]
    return schema


def read_verb(schema):
    """
    Read the verbs in the schema, will be used as a check method
    """
    verb_chain = []
    for chain in schema:
        verb_chain.append({u.split('-')[0] for u in chain})
    return verb_chain
