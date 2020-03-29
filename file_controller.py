import os
import json

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))

def read_json(path):
    path = path if ROOT_PATH in path else (ROOT_PATH + "/" + path)
    result = ""

    with open(path , 'r') as reader:
        result = json.loads(reader.read())

    return result

def write_json(path, data):
    path = path if ROOT_PATH in path else (ROOT_PATH + "/" + path)

    with open(path , 'w') as writer:
        data = json.dumps(data)
        writer.write(data)
        return True

    return False