import os
import json


ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
AUDIO_PATH = f'{ROOT_PATH}/data/audio'

def read_json(path):
    path = path if ROOT_PATH in path else (ROOT_PATH + '/' + path)
    result = None

    with open(path , 'r', encoding = 'UTF-8') as reader:
        result = json.loads(reader.read())

    return result

def write_json(path, data):
    path = path if ROOT_PATH in path else (ROOT_PATH + '/' + path)

    with open(path , 'w') as writer:
        data = json.dumps(data)
        writer.write(data)
        return True

    return False