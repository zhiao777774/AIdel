#import pymongo
import numpy as np
import cv2
import socketio
import base64
from PIL import Image
from io import BytesIO

'''
class MongoDB:
    def __init__(self, host, port=None):
        print('MongoDB client is opening.')
        self._client = pymongo.MongoClient(host, port)
        self.db = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, trace):
        self.close()

    def connect(self, db_name):
        print(f'MongoDB is connect to {db_name} database.')
        self.db = self._client[db_name]

    def close(self):
        print('MongoDB client is closing.')
        self._client.close()

    def _db_connected(self):
        if not self.db:
            raise BrokenPipeError('MongoDB database have been connecting.')

    def insert(self, col_name, data):
        self._db_connected()

        col = self.db[col_name]
        result_id = None

        if type(data) is dict:
            result_id = col.insert_one(data).inserted_id
        elif type(data) is list:
            result_id = col.insert_many(data).inserted_id

        return result_id

    def find(self, col_name):
        self._db_connected()
        return self.db[col_name].find_one()

    def select(self, col_name, query={}, condition={}):
        self._db_connected()

        # Change SQL grammar to MongoDB grammar
        if type(col_name) is str and \
            'SELECT' in col_name.upper() and \
                not query and not condition:

            strings = col_name.split(' ')
            uppers = [map(lambda e: e.upper(), strings)]

            if strings[1] == '*':
                condition = {}
            else:
                condition = {}

                start = uppers.index('SELECT') + 1
                end = uppers.index('FROM')

                for i, q in enumerate(strings[start: end]):
                    q = q.replace(',', '').strip()
                    strings[start + i] = q
                    condition[q] = 1

            col_name = strings[uppers.index('FROM') + 1]

            if 'WHERE' in uppers:
                query = {}

                start = col_name.upper().index('WHERE')
                end = start + 4
                temp = ''.join(col_name[end + 1:].split()).split('and')

                for q in temp:
                    key, value = q.split('=', 1)  # 第二個參數為預防值有包含=的存在，而被切割
                    query[key] = value

        col = self.db[col_name]

        if type(query) is dict and type(condition) is dict:
            return col.find(query, condition)

        return None

    def delete_one(self, col_name, condition):
        self._db_connected()

        if type(condition) is dict:
            return self.db[col_name].delete_one(condition)
        return None

    def delete(self, col_name, condition):
        self._db_connected()

        # Change SQL grammar to MongoDB grammar
        if type(col_name) is str and \
                'DELETE' in col_name.upper() and not condition:

            strings = col_name.split(' ')
            uppers = [map(lambda e: e.upper(), strings)]
            col_name = strings[uppers.index('FROM') + 1]
            condition = {}

            if 'WHERE' in uppers:
                start = col_name.upper().index('WHERE')
                end = start + 4
                temp = ''.join(col_name[end + 1:].split()).split('and')

                for q in temp:
                    key, value = q.split('=', 1)  # 第二個參數為預防值有包含=的存在，而被切割
                    condition[key] = value

        col = self.db[col_name]

        if type(condition) is dict:
            return col.delete_many(condition).deleted_count

        return 0

    def drop(self, col_name):
        self._db_connected()

        if type(col_name) is str and 'DROP' in col_name.upper():
            strings = col_name.split(' ')
            uppers = [map(lambda e: e.upper(), strings)]
            col_name = strings[uppers.index('TABLE') + 1]

        return self.db[col_name].drop()

    def collection(self, col_name):
        self._db_connected()
        return self.db[col_name]
'''
class MongoDB:
    def __init__(self, host, port):
        self._socket = socketio.Client()
        self._socket.connect(f'http://{host}:{port}')
        print('MongoDB client is connecting.')

    def __enter__(self):
        return self

    def __exit__(self, type, value, trace):
        self.close()

    def close(self):
        print('MongoDB client is closing.')
        self._socket.disconnect()

    def trigger(self, _type, event, query, callback=None):
        query['event'] = event
        self._event_route(_type, query, callback, event)

    def select(self, query, callback=None):
        self._event_route('get', query, callback)

    def insert(self, query, callback=None):
        self._event_route('insert', query, callback)

    def delete(self, query, callback=None):
        self._event_route('delete', query, callback)

    def update(self, query, callback=None):
        self._event_route('update', query, callback)

    def _event_route(self, req_event, query, callback, res_event=None):
        self._socket.emit(req_event, query)

        if callback and callable(callback):
            @self._socket.on(res_event or f'{req_event}Result')
            def _handler(data):
                callback(data)

def np_cvt_base64img(np_image, _format='JPEG'):
    buffered = BytesIO()
    img = Image.fromarray(np_image)
    img.save(buffered, format=_format)

    buffered.seek(0)
    base64img_str = base64.b64encode(buffered.getvalue()).decode()
    return base64img_str


if __name__ == '__main__':
    db = MongoDB('120.125.83.10', '8080')
    insert_data = {
        'date': '2020/07/20',
        'data': [
            {
                'time': '16:00',
                'data': []
            },
            {
                'time': '16:30',
                'data': []
            },
            {
                'time': '17:00',
                'data': []
            }
        ]
    }

    descriptions = [
        [
            '新北市永和區環河東路一段',
            '新北市永和區光復街30號',
            '新北市永和區光復街2巷',
            '新北市永和區光復街2巷2號',
            '新北市永和區永和路二段334號'
        ],
        [
            '宜蘭縣礁溪鄉德陽村溫泉路1號',
            '宜蘭縣礁溪鄉德陽街1號',
            '宜蘭縣礁溪鄉中山路二段117號',
            '宜蘭縣礁溪鄉礁溪路五段96號',
            '宜蘭縣礁溪鄉礁溪路五段82號'
        ],
        [
            '苗栗縣竹南鎮博愛街437巷',
            '苗栗縣竹南鎮博愛街396號',
            '苗栗縣竹南鎮博愛街367號',
            '苗栗縣竹南鎮新生路329號',
            '苗栗縣竹南鎮南寶街54號'
        ]
    ]

    locations = [
        [
            (25.0180847,121.5167606),
            (25.0173888,121.5159106),
            (25.0166382,121.5150595),
            (25.0160403,121.5165338),
            (25.0164153,121.5167504)
        ],
        [
            (24.8264472,121.7753794),
            (24.8269452,121.7740852),
            (24.8259578,121.7738968),
            (24.8258562,121.7728746),
            (24.8266045,121.7718516)
        ],
        [
            (24.6884289,120.8652432),
            (24.6887505,120.8660248),
            (24.6885609,120.8670637),
            (24.6880285,120.8677626),
            (24.6874622,120.8678239)
        ]
    ]

    for i, data in enumerate(insert_data['data']):
        locs = []
        for j in range(1, len(locations[0]) + 1):
            locs.append({
                'latitude' : locations[i][j - 1][0],
                'longitude' : locations[i][j - 1][1]
            })
        data['locations'] = locs

        inner_data = data['data']
        for j in range(1, len(descriptions[0]) + 1):
            buffered = BytesIO()
            img = Image.open(f'C:\\Users\\user\\Downloads\\G{i + 1}\\G{i + 1}-{j}.jpg')
            img.save(buffered, format='JPEG')
            buffered.seek(0)
            base64img_str = base64.b64encode(buffered.getvalue()).decode()

            inner_data.append({
                'id': j,
                'image': base64img_str,
                'description': descriptions[i][j - 1]
            })

    db.insert({
        'collection': 'historicalImage',
        'data': insert_data
    }, lambda data: print('inserted'))