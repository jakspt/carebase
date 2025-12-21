from pymongo import MongoClient


class MongoBase:
    def _get_connection(self):
        # TODO: Change credentials
        client = MongoClient("mongodb://root:root@mongodb:27017/")
        return client["hospital_db"]
