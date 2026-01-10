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
        return list(patients)
    
    def get_all_doctors(self) -> list[dict]:
        doctors = self.doctor_collection.find()
        return list(doctors)
    
    def get_all_clerks(self) -> list[dict]:
        clerks = self.clerk_collection.find()
        return list(clerks)
    
    def get_booked_slots(self, doctor_svnr: int, date: str) -> list[str]:
        return list({})
    
    def get_patient_booked_slots(self, patient_svnr: int, date: str) -> list[str]:
        return list({})
    
    def get_next_termin_id(self, patient_svnr: int) -> int:
        searched_patient = self.patient_collection.find_one({"svnr": patient_svnr})
        
        if not searched_patient or "appointments" not in searched_patient:
            return 1  # Start with 1 if no appointments exist
        
        appointments = searched_patient["appointments"]
        
        if not appointments:
            return 1  # Start with 1 if appointments list is empty
        
        max_termin_id = 0
        for appointment in appointments:
            termin_id = appointment.get("terminID", 0)
            if termin_id > max_termin_id:
                max_termin_id = termin_id
        
        return max_termin_id + 1  # Return next available ID

    def create_appointment(self, patient_svnr: int, doctor_svnr: int, date: str, time: str, reason: str, clerk_svnr: int) -> int:
        return 0
    
    def check_appointment_conflict(self, doctor_svnr: int, patient_svnr: int, date: str, time: str) -> dict | None:
        return None
    
    def get_patients_doctor_visits(self, start_date: str, end_date: str) -> list[dict]:
        return list({})