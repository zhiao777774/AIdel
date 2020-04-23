import pymongo

class MongoDB:
    def __init__(self, location):
        self._client = pymongo.MongoClient(location)
        self.db = None

    def connect(self, db_name):
        self.db = self._client[db_name]

    def insert(self, col_name, data):
        col = self.db[col_name]
        result_id = None

        if type(data) is dict:
            result_id = col.insert_one(data).inserted_id
        elif type(data) is list:
            result_id = col.insert_many(data).inserted_id

        return result_id

    def find(self, col_name):
        return self.db[col_name].find_one()

    def select(self, col_name, query = {}, condition = {}):
        #Change SQL grammar to MongoDB grammar
        if type(col_name) is str and \
            "SELECT" in col_name.upper() and \
                not query and not condition:
            
            strings = col_name.split(" ")
            uppers = [map(lambda e: e.upper(), strings)]

            if strings[1] == "*":
                condition = {}
            else:
                condition = {}

                start = uppers.index("SELECT") + 1
                end = uppers.index("FROM")

                for i, q in enumerate(strings[start : end]):
                    q = q.replace(",", "").strip()
                    strings[start + i] = q
                    condition[q] = 1

            col_name = strings[uppers.index("FROM") + 1]

            if "WHERE" in uppers:
                query = {}

                start = col_name.upper().index("WHERE")
                end = start + 4
                temp = "".join(col_name[end + 1 :].split()).split("and")

                for q in temp:
                    key, value = q.split("=", 1) #第二個參數為預防值有包含=的存在，而被切割
                    query[key] = value

        col = self.db[col_name]

        if type(query) is dict & type(condition) is dict:
            return col.find(query, condition)
        
        return None

    def delete_one(self, col_name, condition):
        if type(condition) is dict:
            return self.db[col_name].delete_one(condition)
        return None

    def delete(self, col_name, condition):
        #Change SQL grammar to MongoDB grammar
        if type(col_name) is str and \
            "DELETE" in col_name.upper() and not condition:

            strings = col_name.split(" ")
            uppers = [map(lambda e: e.upper(), strings)]
            col_name = strings[uppers.index("FROM") + 1]
            condition = {}

            if "WHERE" in uppers:
                start = col_name.upper().index("WHERE")
                end = start + 4
                temp = "".join(col_name[end + 1 :].split()).split("and")

                for q in temp:
                    key, value = q.split("=", 1) #第二個參數為預防值有包含=的存在，而被切割
                    condition[key] = value

        col = self.db[col_name]

        if type(condition) is dict:
            return col.delete_many(condition).deleted_count

        return 0

    def drop(self, col_name):
        if type(col_name) is str and "DROP" in col_name.upper():
            strings = col_name.split(" ")
            uppers = [map(lambda e: e.upper(), strings)]
            col_name = strings[uppers.index("TABLE") + 1]

        return self.db[col_name].drop()