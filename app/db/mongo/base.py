from pymongo import MongoClient


class MongoBase:
    collection_patient_name = "patient"
    collection_doctor_name = "arzt"
    collection_medication_name = "medikament"
    collection_clerk_name = "sachbearbeiter"
    collection_appointment_name = "termin"

    def _get_connection(self):
        client = MongoClient("mongodb://localhost:27017/")
        return client["carebase"]  # Database name
