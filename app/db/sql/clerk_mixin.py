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
    
    def get_all_clerks(self) -> list[dict]:
        """Get all clerks (Sachbearbeiter)"""
        query = '''
            SELECT person.SVNr, person.Name
            FROM Person
            JOIN Sachbearbeiter ON person.SVNr = Sachbearbeiter.SVNr
        '''
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        clerks = []
        for row in rows:
            clerks.append({
                "svnr": row[0],
                "name": row[1]
            })
        return clerks

    def get_booked_slots(self, doctor_svnr: int, date: str) -> list[str]:
        """Get all booked time slots for a doctor on a specific date"""
        query = '''
            SELECT Uhrzeit
            FROM Termin
            WHERE SVNr_Arzt = ? AND Datum = ?
        '''
        self.cursor.execute(query, (doctor_svnr, date))
        rows = self.cursor.fetchall()
        # Convert time objects to string format "HH:MM"
        return [row[0].strftime("%H:%M") if hasattr(row[0], 'strftime') else str(row[0])[:5] for row in rows]

    def get_patient_booked_slots(self, patient_svnr: int, date: str) -> list[str]:
        """Get all booked time slots for a patient on a specific date"""
        query = '''
            SELECT Uhrzeit
            FROM Termin
            WHERE SVNr_Patient = ? AND Datum = ?
        '''
        self.cursor.execute(query, (patient_svnr, date))
        rows = self.cursor.fetchall()
        return [row[0].strftime("%H:%M") if hasattr(row[0], 'strftime') else str(row[0])[:5] for row in rows]

    def get_next_termin_id(self, patient_svnr: int) -> int:
        """Get the next available TerminID for a patient"""
        query = '''
            SELECT COALESCE(MAX(TerminID), 0) + 1
            FROM Termin
            WHERE SVNr_Patient = ?
        '''
        self.cursor.execute(query, (patient_svnr,))
        result = self.cursor.fetchone()
        return result[0] if result else 1

    def create_appointment(self, patient_svnr: int, doctor_svnr: int, date: str, time: str, reason: str, clerk_svnr: int) -> int:
        """Create a new appointment and return the TerminID"""
        termin_id = self.get_next_termin_id(patient_svnr)
        
        query = '''
            INSERT INTO Termin (TerminID, Datum, Uhrzeit, Grund, SVNr_Patient, SVNr_Arzt, SVNr_Sachbearbeiter)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        self.cursor.execute(query, (termin_id, date, time, reason, patient_svnr, doctor_svnr, clerk_svnr))
        self.conn.commit()
        
        return termin_id

    def check_appointment_conflict(self, doctor_svnr: int, patient_svnr: int, date: str, time: str) -> dict | None:
        """Check if there's a scheduling conflict. Returns conflict info or None if no conflict."""
        # Check doctor conflict
        query = '''
            SELECT TerminID FROM Termin
            WHERE SVNr_Arzt = ? AND Datum = ? AND Uhrzeit = ?
        '''
        self.cursor.execute(query, (doctor_svnr, date, time))
        if self.cursor.fetchone():
            return {"type": "doctor", "message": "Der Arzt hat bereits einen Termin zu dieser Zeit."}
        
        # Check patient conflict
        query = '''
            SELECT TerminID FROM Termin
            WHERE SVNr_Patient = ? AND Datum = ? AND Uhrzeit = ?
        '''
        self.cursor.execute(query, (patient_svnr, date, time))
        if self.cursor.fetchone():
            return {"type": "patient", "message": "Der Patient hat bereits einen Termin zu dieser Zeit."}
        
        return None
    
    def get_patients_doctor_visits(self, start_date: str, end_date: str) -> list[dict]:
        """Get patient visits per doctor within a date range"""
        query = ''' 
            SELECT
                Termin.`SVNr_Patient` AS Patient_SVNr,
                Patient_Person.`Name` AS Patient_Name,
                Patient.`Versicherungsträger` AS Patient_Versicherungsträger,
                Termin.`SVNr_Arzt` AS Arzt_SVNr,
                Arzt_Person.`Name` AS Arzt_Name,
                Arzt.`Fachrichtung` AS Arzt_Fachrichtung,
                COUNT(Termin.`TerminID`) AS Anzahl_Termine_Jeweiligen_Arzt
                FROM `Termin`
                JOIN `Patient` ON Termin.SVNr_Patient = Patient.SVNr
                JOIN `Person` AS Patient_Person ON Patient.SVNr = Patient_Person.SVNr
                JOIN `Arzt` ON Termin.SVNr_Arzt = Arzt.SVNr 
                JOIN `Person` AS Arzt_Person ON Arzt.SVNr = Arzt_Person.SVNr
                WHERE Termin.`Datum` BETWEEN ? AND ?
                GROUP BY Termin.`SVNr_Patient`, Termin.`SVNr_Arzt`;
        '''
        
        self.cursor.execute(query, (start_date, end_date))
        rows = self.cursor.fetchall()
        reports = []
        for row in rows:
            reports.append({
                "patient_svnr": row[0],
                "patient_name": row[1],
                "versicherung": row[2],
                "arzt_svnr": row[3],
                "arzt_name": row[4],
                "fachrichtung": row[5],
                "anzahl_termine": row[6]
            })
        return reports
