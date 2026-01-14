import pymongo
from app.db.mongo.base import MongoBase
from datetime import datetime

class MongoClerkMixin:
    def __init__(self) -> None:
        self.conn = self._get_connection()
        self.patient_collection = self.conn[MongoBase.collection_patient_name]
        self.doctor_collection = self.conn[MongoBase.collection_doctor_name]
        self.clerk_collection = self.conn[MongoBase.collection_clerk_name]
        self.appointment_collection = self.conn[MongoBase.collection_appointment_name]

        self.appointment_collection.create_index([
            ("patient.svnr", pymongo.ASCENDING),
            ("datum", pymongo.DESCENDING),
            ("uhrzeit", pymongo.DESCENDING)
            ])
        
        self.appointment_collection.create_index([
            ("arzt.svnr", pymongo.ASCENDING),
            ("datum", pymongo.DESCENDING),
            ("uhrzeit", pymongo.DESCENDING)
            ])
        
        self.appointment_collection.create_index([("termin_id", pymongo.DESCENDING)])

    def get_all_patients(self) -> list[dict]:
        result = []
        patients = self.patient_collection.find({}, {"name": 1, "versicherung": 1, "naca_score": 1})
        for patient in patients:
            result.append({
                "svnr": patient['_id'],
                "name": patient.get("name", ""),
                "versicherung": patient.get("versicherung", ""),
                "naca_score": patient.get("naca_score", None)
            })
        return result
    
    def get_all_doctors(self) -> list[dict]:
        result = []
        doctors = self.doctor_collection.find()
        for doctor in doctors:
            result.append({
                "svnr": doctor['_id'],
                "name": doctor.get("name", ""),
                "fachrichtung": doctor.get("fachrichtung", ""),
                "position": doctor.get("position", ""),
                "abteilung": doctor['abteilung'].get("name", "")
            })
        return result
    
    def get_all_clerks(self) -> list[dict]:
        result = []
        clerks = self.clerk_collection.find()
        for clerk in clerks:
            result.append({
                "svnr": clerk['_id'],
                "name": clerk.get("name", "")
            })
        return result
    
    def convert_date_str(self, date_str: str) -> datetime:
        return datetime.strptime(date_str, "%Y-%m-%d")
    
    def get_doctor_booked_slots(self, doctor_svnr: int, date: str) -> list[str]:
        """Get all booked time slots for a doctor on a specific date"""
        converted_date = self.convert_date_str(date)
        
        findquery = {
            "arzt.svnr": str(doctor_svnr),
            "datum": converted_date
        }

        # Projection to only get time slots
        projection = {"uhrzeit": 1, "_id": 0}
        searched_appointments = self.appointment_collection.find(findquery, projection)

        booked_slots = [
            appt["uhrzeit"][:5]           
            for appt in searched_appointments 
            if "uhrzeit" in appt
        ]
        print("Booked slots for doctor:", booked_slots)
        return booked_slots
    
    def get_patient_booked_slots(self, patient_svnr: int, date: str) -> list[str]:
        """Get all booked time slots for a patient on a specific date"""
        converted_date = self.convert_date_str(date)
    
        findquery = {
            "patient.svnr": str(patient_svnr),
            "datum": converted_date
        }

        # Projection to only get time slots
        projection = {"uhrzeit": 1, "_id": 0}
        
        searched_appointments = self.appointment_collection.find(findquery, projection)
        
        booked_slots = [
            appt["uhrzeit"][:5]           
            for appt in searched_appointments 
            if "uhrzeit" in appt
        ]
        print("Booked slots for patient:", booked_slots)
        return booked_slots
    
    def get_next_termin_id(self) -> int:
        biggest_termin_id = self.appointment_collection.find_one({}, {"termin_id": 1, "_id": 0}, sort=[("termin_id", -1)])
        
        if biggest_termin_id and "termin_id" in biggest_termin_id:
            return biggest_termin_id["termin_id"] + 1
        else:
            return 1

    def create_appointment(self, patient_svnr: int, doctor_svnr: int, date: str, time: str, reason: str, clerk_svnr: int) -> int:
        termin_id = self.get_next_termin_id()
        patient = self.patient_collection.find_one({"_id": patient_svnr})
        doctor = self.doctor_collection.find_one({"_id": doctor_svnr})
        converted_date = self.convert_date_str(date)

        self.appointment_collection.insert_one({
            "termin_id": termin_id,
            "datum": converted_date,
            "uhrzeit": time,
            "grund": reason,
            "patient": {
                "svnr": str(patient_svnr),
                "name": patient.get("name", "") if patient else "",
                "versicherung": patient.get("versicherung", "") if patient else ""
            },
            "arzt": {
                "svnr": str(doctor_svnr),
                "name": doctor.get("name", "") if doctor else "",
                "fachrichtung": doctor.get("fachrichtung", "") if doctor else ""
            },
            "sachbearbeiter": {
                "svnr": str(clerk_svnr)
            }
        })

        self.patient_collection.update_one(
            {"_id": str(patient_svnr)},
            {"$push": {"termine": {
                "termin_id": termin_id,
                "datum": converted_date,
                "uhrzeit": time,
                "grund": reason,
                "arzt": {
                    "svnr": str(doctor_svnr),
                    "name": doctor.get("name", "") if doctor else ""
                },
                "behandlungen": []   
            }}})
        return termin_id
    
    def check_appointment_conflict(self, doctor_svnr: int, patient_svnr: int, date: str, time: str) -> dict | None:
        converted_date = self.convert_date_str(date)

        patient_conflict = self.appointment_collection.find_one({
            "patient.svnr": str(patient_svnr),
            "datum": converted_date,
            "uhrzeit": time
        })

        if patient_conflict:
            return {
                "type": "patient_conflict",
                "message": "Der Patient hat bereits einen Termin zu dieser Zeit."
            }

        doctor_conflict = self.appointment_collection.find_one({
            "arzt.svnr": str(doctor_svnr),
            "datum": converted_date,
            "uhrzeit": time
        })

        if doctor_conflict:
            return {
                "type": "doctor_conflict",
                "message": "Der Arzt hat bereits einen Termin zu dieser Zeit."
            }
        
        return None
    
    def get_patients_doctor_visits(self, start_date: str, end_date: str) -> list[dict]:
        """Get patient visits per doctor within a date range"""
        converted_start_date = self.convert_date_str(start_date)
        converted_end_date = self.convert_date_str(end_date)

        pipeline = [
            # Filter by date range
            {
                "$match": {
                    "datum": {
                        "$gte": converted_start_date,
                        "$lte": converted_end_date
                    }
                }
            },
            # Group by patient and doctor combination
            {
                "$group": {
                    "_id": {
                        "patient_svnr": "$patient.svnr",
                        "arzt_svnr": "$arzt.svnr"
                    },
                    "patient_name": {"$first": "$patient.name"},
                    "versicherung": {"$first": "$patient.versicherung"},
                    "arzt_name": {"$first": "$arzt.name"},
                    "fachrichtung": {"$first": "$arzt.fachrichtung"},
                    "anzahl_termine": {"$sum": 1}
                }
            },
            # Reshape the output to match SQL format
            {
                "$project": {
                    "_id": 0,
                    "patient_svnr": "$_id.patient_svnr",
                    "patient_name": 1,
                    "versicherung": 1,
                    "arzt_svnr": "$_id.arzt_svnr",
                    "arzt_name": 1,
                    "fachrichtung": 1,
                    "anzahl_termine": 1
                }
            },
            # Sort by patient and doctor for consistent ordering
            {
                "$sort": {
                    "patient_svnr": 1,
                    "arzt_svnr": 1
                }
            }
        ]

        results = self.appointment_collection.aggregate(pipeline)
        return list(results)