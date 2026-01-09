from imse.app.db.mongo.base import MongoBase
from imse.app.db.sql.base import SQLBase


class DataMigrator(SQLBase, MongoBase):
    def __init__(self) -> None:
        self.sql_conn = SQLBase._get_connection(self)
        self.sql_cursor = self.sql_conn.cursor()

        self.mongo_db = MongoBase._get_connection(self)
    
    def migrate_to_patient_collection(self):
        """Migrate Patient data from SQL to MongoDB"""
        self.sql_cursor.execute('''
            SELECT person.SVNr, person.Name, person.Adresse,
                   patient.Versicherungsträger, patient.NACA_Score
            FROM Person
            JOIN Patient ON person.SVNr = patient.SVNr
        ''')
        rows = self.sql_cursor.fetchall()
        
        patient_collection = self.mongo_db["patients"]
        
        for row in rows:
            patient_doc = {
                "svnr": row[0],
                "name": row[1],
                "geburtsdatum": row[2].isoformat(),
                "adresse": row[3],
                "versicherungstraeger": row[4],
                "naca_score": row[5]
            }
            patient_collection.insert_one(patient_doc)
        
        print(f"Migrated {len(rows)} patients to MongoDB 'patients' collection.")