from app.db.sql.base import SQLBase


class SQLClerkMixin(SQLBase):
    def __init__(self) -> None:
        self.conn = self._get_connection()
        self.cursor = self.conn.cursor()

    def get_all_patients(self) -> list[dict]:
        query = '''
            SELECT person.SVNr, person.Name, patient.Versicherungsträger, patient.NACA_Score
            FROM Person
            JOIN Patient ON person.SVNr = patient.SVNr
        '''
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        patients = []
        for row in rows:
            patients.append({
                "svnr": row[0],
                "name": row[1],
                "versicherung": row[2],
                "naca_score": row[3]
            })
        return patients
