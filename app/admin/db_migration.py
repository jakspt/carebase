from app.db.mongo.base import MongoBase
from app.db.sql.base import SQLBase
from datetime import datetime


class DataMigrator(SQLBase, MongoBase):
    def __init__(self) -> None:
        self.sql_conn = SQLBase._get_connection(self)
        self.sql_cursor = self.sql_conn.cursor()

        self.mongo_db = MongoBase._get_connection(self)

    def delete_all_collections(self):
        """Delete all existing collections in MongoDB to start fresh"""
        collections = [
            MongoBase.collection_patient_name,
            MongoBase.collection_doctor_name,
            MongoBase.collection_medication_name,
            MongoBase.collection_clerk_name,
            MongoBase.collection_appointment_name
        ]
        for coll in collections:
            self.mongo_db[coll].drop()
        print("Deleted all existing collections in MongoDB.")
    
    def migrate_to_patient_collection(self):
        """Migrate Patient data from SQL to MongoDB with nested appointments"""
        
        # Get all patients with their person data
        self.sql_cursor.execute('''
            SELECT p.SVNr, p.Name, p.Adresse,
                   pat.Versicherungsträger, pat.NACA_Score
            FROM Person p
            JOIN Patient pat ON p.SVNr = pat.SVNr
        ''')
        patients = self.sql_cursor.fetchall()
        
        patient_collection = self.mongo_db[MongoBase.collection_patient_name]
        
        for patient in patients:
            patient_svnr = patient[0]
            
            # Get all appointments for this patient
            self.sql_cursor.execute('''
                SELECT t.TerminID, t.Datum, t.Uhrzeit, t.Grund,
                       a.SVNr, per.Name
                FROM Termin t
                JOIN Arzt a ON t.SVNr_Arzt = a.SVNr
                JOIN Person per ON a.SVNr = per.SVNr
                WHERE t.SVNr_Patient = ?
            ''', (patient_svnr,))
            appointments = self.sql_cursor.fetchall()
            
            appointments_list = []
            for appt in appointments:
                termin_id = appt[0]
                
                # Get all treatments for this appointment
                self.sql_cursor.execute('''
                    SELECT b.BehandlungsID, b.Beschreibung, b.Kosten
                    FROM Behandlung b
                    WHERE b.SVNr_Patient = ? AND b.TerminID = ?
                ''', (patient_svnr, termin_id))
                treatments = self.sql_cursor.fetchall()
                
                behandlungen_list = []
                for treatment in treatments:
                    behandlungs_id = treatment[0]
                    
                    # Get all medications for this treatment
                    self.sql_cursor.execute('''
                        SELECT m.PZN, m.Name
                        FROM Verabreichung v
                        JOIN Medikament m ON v.PZN = m.PZN
                        WHERE v.BehandlungsID = ?
                    ''', (behandlungs_id,))
                    medications = self.sql_cursor.fetchall()
                    
                    medikamente_list = [
                        {"pzn": med[0], "name": med[1]}
                        for med in medications
                    ]
                    
                    behandlungen_list.append({
                        "beschreibung": treatment[1],
                        "kosten": float(treatment[2]) if treatment[2] else 0.0,
                        "medikamente": medikamente_list
                    })
                
                # Convert date and time to proper formats
                appt_date = appt[1]
                appt_time = appt[2]
                
                # Handle time conversion (timedelta to string)
                if hasattr(appt_time, 'total_seconds'):
                    total_seconds = int(appt_time.total_seconds())
                    hours, remainder = divmod(total_seconds, 3600)
                    minutes, _ = divmod(remainder, 60)
                    time_str = f"{hours:02d}:{minutes:02d}"
                else:
                    time_str = str(appt_time)
                
                appointments_list.append({
                    "termin_id": termin_id,
                    # Combine date with minimal time for MongoDB storage
                    # MongoDB stores dates as full datetime objects
                    "date": datetime.combine(appt_date, datetime.min.time()), 
                    "time": time_str,
                    "reason": appt[3],
                    "doctor": {
                        "svnr": appt[4],
                        "name": appt[5]
                    },
                    "behandlungen": behandlungen_list
                })
            
            patient_doc = {
                "_id": patient_svnr,
                "name": patient[1],
                "adresse": patient[2],
                "versicherung": patient[3],
                "naca_score": patient[4],
                "appointments": appointments_list
            }
            
            patient_collection.insert_one(patient_doc)
        
        print(f"Migrated {len(patients)} patients to MongoDB 'patients' collection.")

    def migrate_to_doctor_collection(self):
        """Migrate Doctor data from SQL to MongoDB"""
        self.sql_cursor.execute('''
            SELECT Person.SVNr, Person.Name, Person.Adresse,
                    Arzt.Fachrichtung, Arzt.Position, Arzt.Vorgesetzter_SVNr,
                    Abteilung.Name, Abteilung.Gebäude, Abteilung.Stockwerk
            FROM Person
            JOIN Arzt ON Person.SVNr = Arzt.SVNr
            JOIN Abteilung ON Arzt.Abteilungsname = Abteilung.Name
        ''')
        rows = self.sql_cursor.fetchall()
        
        doctor_collection = self.mongo_db[MongoBase.collection_doctor_name]
        
        for row in rows:
            doctor_doc = {
                "_id": row[0], # SVNr as unique identifier
                "name": row[1],
                "adresse": row[2],
                "fachrichtung": row[3],
                "position": row[4],
                "vorgesetzter_svnr": row[5],
                "abteilung": {
                    "name": row[6],
                    "gebäude": row[7],
                    "stockwerk": row[8]
                }
            }
            doctor_collection.insert_one(doctor_doc)
        
        print(f"Migrated {len(rows)} doctors to MongoDB 'doctors' collection.")

    def migrate_to_medication_collection(self):
        """Migrate Medication data from SQL to MongoDB"""
        self.sql_cursor.execute('''
            SELECT PZN, Name, Wirkstoff
            FROM Medikament
        ''')
        rows = self.sql_cursor.fetchall()
        
        medication_collection = self.mongo_db[MongoBase.collection_medication_name]
        
        for row in rows:
            medication_doc = {
                "_id": row[0], # PZN as unique identifier
                "name": row[1],
                "wirkstoff": row[2]
            }
            medication_collection.insert_one(medication_doc)
        
        print(f"Migrated {len(rows)} medications to MongoDB 'medications' collection.")

    def migrate_to_clerk_collection(self):
        """Migrate Clerk data from SQL to MongoDB"""
        self.sql_cursor.execute('''
            SELECT Person.SVNr, Person.Name, Person.Adresse,
                   Sachbearbeiter.Rolle, Sachbearbeiter.Anstellungsverhältnis
            FROM Person
            JOIN Sachbearbeiter ON Person.SVNr = Sachbearbeiter.SVNr
        ''')
        rows = self.sql_cursor.fetchall()
        
        clerk_collection = self.mongo_db[MongoBase.collection_clerk_name]
        
        for row in rows:
            clerk_doc = {
                "_id": row[0], # SVNr as unique identifier
                "name": row[1],
                "adresse": row[2],
                "rolle": row[3],
                "anstellungsverhältnis": row[4]
            }
            clerk_collection.insert_one(clerk_doc)
        
        print(f"Migrated {len(rows)} clerks to MongoDB 'clerks' collection.")

    def migrate_to_appointment_collection(self):
        """Migrate Appointment data from SQL to MongoDB"""
        self.sql_cursor.execute('''
            SELECT Termin.Datum, Termin.Uhrzeit, Termin.Grund,
                    Termin.SVNr_Patient, PatientPerson.Name AS patient_name, Patient.Versicherungsträger,
                    Termin.SVNr_Arzt, ArztPerson.Name AS doctor_name, Arzt.Fachrichtung,
                    Termin.SVNr_Sachbearbeiter
                    
            FROM Termin
            JOIN Patient ON Termin.SVNr_Patient = Patient.SVNr
            JOIN Person AS PatientPerson ON Patient.SVNr = PatientPerson.SVNr
            JOIN Arzt ON Termin.SVNr_Arzt = Arzt.SVNr
            JOIN Person AS ArztPerson ON Arzt.SVNr = ArztPerson.SVNr
        ''')
        rows = self.sql_cursor.fetchall()
        
        appointment_collection = self.mongo_db[MongoBase.collection_appointment_name]
        
        for row in rows:
            appointment_doc = {
                "date": datetime.combine(row[0], datetime.min.time()), # Store date as datetime
                "time": str(row[1]),
                "reason": row[2],
                "patient": {
                    "svnr": row[3],
                    "name": row[4],
                    "versicherung": row[5]
                },
                "arzt": {
                    "svnr": row[6],
                    "name": row[7],
                    "fachrichtung": row[8]
                },
                "sachbearbeiter": {
                    "svnr": row[9]
                }
            }
            appointment_collection.insert_one(appointment_doc)
        
        print(f"Migrated {len(rows)} appointments to MongoDB 'appointments' collection.")

    def migrate_all(self):
        self.delete_all_collections()
        self.migrate_to_patient_collection()
        self.migrate_to_doctor_collection()
        self.migrate_to_medication_collection()
        self.migrate_to_clerk_collection()
        self.migrate_to_appointment_collection()