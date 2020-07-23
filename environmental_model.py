import socketio

import file_controller as fc


class EnvironmentalModel:
    def __init__(self, data):
        if type(data) is str:
            data = fc.read_json(data)
            self._data = data
        elif type(data) is list:
            self._data = data
        else:
            raise TypeError('data\'s type have to string or list.')

    def __str__(self):
        return self._data

    def __repr__(self):
        return self._data

    def get(self, index):
        return self._data[index]


class EnvironmentalModelSocket:
    def __init__(self, host, port):
        self._socket = socketio.Client()
        self._socket.connect(f'http://{host}:{port}')
        print('Environmental model socket is connecting.')

    def __enter__(self):
        return self

    def __exit__(self, type, value, trace):
        self.close()

    def close(self):
        print('Environmental model socket is closing.')
        self._socket.disconnect()

    def send(self, model):
        self._socket.emit(
            'receiveEnvironmentalModel', model)

_MODEL_SOCKET = EnvironmentalModelSocket('120.125.83.10', '8090')

def create_environmental_model(file_path, height, width, resolution, bboxes):
    _to_str = lambda dic: dict(zip(
            map(lambda k: k, dic.keys()),
            map(lambda v: str(v), dic.values())
        ))

    model = {
        'height': height,
        'width': width,
        'resolution': resolution, 
        'obstacles' : []
    }

    for bbox in bboxes:
        lt = _to_str(dict(bbox.coordinates.lt._asdict()))
        rt = _to_str(dict(bbox.coordinates.rt._asdict()))
        lb = _to_str(dict(bbox.coordinates.lb._asdict()))
        rb = _to_str(dict(bbox.coordinates.rb._asdict()))

        model['obstacles'].append({
            'class': bbox.clsName,
            'confidence': str(bbox.confidence),
            'distance': str(bbox.distance),
            'coordinate': {
                'lt': lt,
                'rt': rt,
                'lb': lb,
                'rb': rb,
            }
        })

    fc.write_json(file_path, model)
    _MODEL_SOCKET.send(model)

def disconnect_environmental_model_socket():
    _MODEL_SOCKET.close()