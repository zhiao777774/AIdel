import os
import json

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))

def read_json(path):
    path = path if ROOT_PATH in path else (ROOT_PATH + "/" + path)

    with open(path , 'r') as reader:
        result = json.loads(reader.read())

    return result