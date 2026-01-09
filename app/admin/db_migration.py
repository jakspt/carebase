from imse.app.db.mongo.base import MongoBase
from imse.app.db.sql.base import SQLBase
from datetime import datetime


class DataMigrator(SQLBase, MongoBase):
    def __init__(self) -> None:
        self.sql_conn = SQLBase._get_connection(self)
        self.sql_cursor = self.sql_conn.cursor()

        self.mongo_db = MongoBase._get_connection(self)
    
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
                       a.SVNr, per.Name, a.Fachrichtung
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
                        {"id": med[0], "name": med[1]}
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
                    "date": datetime.combine(appt_date, datetime.min.time()),
                    "time": time_str,
                    "reason": appt[3],
                    "doctor": {
                        "id": appt[4],
                        "name": appt[5],
                        "fachrichtung": appt[6]
                    },
                    "behandlungen": behandlungen_list
                })
            
            patient_doc = {
                "_id": patient_svnr,
                "name": patient[1],
                "adresse": patient[2],
                "versicherungsträger": patient[3],
                "naca_score": patient[4],
                "appointments": appointments_list
            }
            
            patient_collection.insert_one(patient_doc)
        
        print(f"Migrated {len(patients)} patients to MongoDB 'patients' collection.")

    def migrate_to_doctor_collection(self):
        """Migrate Doctor data from SQL to MongoDB"""
        self.sql_cursor.execute('''
            SELECT person.SVNr, person.Name, person.Adresse,
                   doctor.Fachgebiet, doctor.Berufserfahrung
            FROM Person
            JOIN Doctor ON person.SVNr = doctor.SVNr
        ''')
        rows = self.sql_cursor.fetchall()
        
        doctor_collection = self.mongo_db[MongoBase.collection_doctor_name]
        
        for row in rows:
            doctor_doc = {
                "svnr": row[0],
                "name": row[1],
                "adresse": row[2],
                "fachgebiet": row[3],
                "berufserfahrung": row[4]
            }
            doctor_collection.insert_one(doctor_doc)
        
        print(f"Migrated {len(rows)} doctors to MongoDB 'doctors' collection.")

    def migrate_all(self):
        self.migrate_to_patient_collection()
        # Add more migration methods as needed