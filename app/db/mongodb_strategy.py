import pymongo
from database_strategy import DatabaseStrategy

class MongoStrategy(DatabaseStrategy):
    def __init__(self, uri, db_name):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None

    def connect(self):
        if not self.client:
            self.client = pymongo.MongoClient(self.uri)
            self.db = self.client[self.db_name]

    def get_by_id(self, table_name, record_id):
        self.connect()
        # Assuming you migrated 'id' as a field, or use _id if you mapped it
        return self.db[table_name].find_one({"id": record_id})

    def insert(self, table_name, data):
        self.connect()
        # MongoDB is schemaless, so we just insert the dict directly
        result = self.db[table_name].insert_one(data)
        return result.inserted_id
        
    def update(self, table_name, record_id, data):
        self.connect()
        self.db[table_name].update_one({"id": record_id}, {"$set": data})