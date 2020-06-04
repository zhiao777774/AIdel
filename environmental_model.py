import file_controller as fc

class EnvironmentalModel:
    def __init__(self, data):
        if isinstance(data, str):
            data = fc.read_json(data)

        self._data = data

    def __repr__(self):
        return self._data

    def get(self, index):
        return self._data[index]

def write_environmental_model(file_path, bboxes):
    _to_str = lambda dic: dict(zip(
            map(lambda k: k, dic.keys()),
            map(lambda v: str(v), dic.values())
        ))

    json = []
    for bbox in bboxes:
        lt = _to_str(dict(bbox.coordinates.lt._asdict()))
        rt = _to_str(dict(bbox.coordinates.rt._asdict()))
        lb = _to_str(dict(bbox.coordinates.lb._asdict()))
        rb = _to_str(dict(bbox.coordinates.rb._asdict()))

        json.append({
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

    fc.write_json(file_path, json)