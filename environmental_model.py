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