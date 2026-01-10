from app.db.mongo.base import MongoBase

class MongoClerkMixin(MongoBase):
    def __init__(self) -> None:
        self.conn = self._get_connection()
        self.patient_collection = self.conn[MongoBase.collection_patient_name]
        self.doctor_collection = self.conn[MongoBase.collection_doctor_name]
        self.clerk_collection = self.conn[MongoBase.collection_clerk_name]
        self.appointment_collection = self.conn[MongoBase.collection_appointment_name]

    def get_all_patients(self) -> list[dict]:
        patients = self.patient_collection.find()
        return list({})
    
    def get_all_doctors(self) -> list[dict]:
        return list({})
    
    def get_all_clerks(self) -> list[dict]:
        return list({})
    
    def get_booked_slots(self, doctor_svnr: int, date: str) -> list[str]:
        return list({})
    
    def get_patient_booked_slots(self, patient_svnr: int, date: str) -> list[str]:
        return list({})
    
    def create_appointment(self, patient_svnr: int, doctor_svnr: int, date: str, time: str, reason: str, clerk_svnr: int) -> int:
        return 0
    
    def check_appointment_conflict(self, doctor_svnr: int, patient_svnr: int, date: str, time: str) -> dict | None:
        return None
    
    def get_patients_doctor_visits(self, start_date: str, end_date: str) -> list[dict]:
        return list({})