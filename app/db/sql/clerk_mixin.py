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

    def get_all_doctors(self) -> list[dict]:
        query = '''
            SELECT person.SVNr, person.Name, arzt.Fachrichtung, arzt.Position, arzt.Abteilungsname
            FROM Person
            JOIN Arzt ON person.SVNr = arzt.SVNr
        '''
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        doctors = []
        for row in rows:
            doctors.append({
                "svnr": row[0],
                "name": row[1],
                "fachrichtung": row[2],
                "position": row[3],
                "abteilung": row[4]
            })
        return doctors