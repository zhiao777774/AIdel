# import pymongo
import socketio

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