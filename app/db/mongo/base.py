from pymongo import MongoClient


# TODO: Rename Connection String for Docker use (swap out localhost)
class MongoBase:
    collection_patient_name = "patient"
    collection_doctor_name = "arzt"
    collection_medication_name = "medikament"
    collection_clerk_name = "sachbearbeiter"
    collection_appointment_name = "termin"

    # Singleton pattern for MongoClient
    _client = None

    def _get_connection(self):
        if MongoBase._client is None:
            print("Initializing new MongoDB connection...")
            MongoBase._client = MongoClient("mongodb://localhost:27017/")
        return MongoBase._client["carebase"]
