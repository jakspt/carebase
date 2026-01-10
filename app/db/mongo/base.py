from pymongo import MongoClient


class MongoBase:
    collection_patient_name = "patient"
    collection_doctor_name = "doctor"
    collection_medication_name = "medication"
    collection_clerk_name = "clerk"

    def _get_connection(self):
        client = MongoClient("mongodb://localhost:27017/")
        return client["carebase"]  # Database name
