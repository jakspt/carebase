from app.db.sql.base import SQLBase


class SQLClerkMixin:
    def __init__(self) -> None:
        self.conn = self._get_connection()
        self.cursor = self.conn.cursor()


    def _init_new_connection(self):
        self.conn = self._get_connection()
        self.cursor = self.conn.cursor()


    def _close_connection(self):
        self.cursor.close()
        self.conn.close()


    def get_all_patients(self) -> list[dict]:
        self._init_new_connection()

        query = """
            SELECT Person.SVNr, Person.Name, Patient.Versicherungsträger, Patient.NACA_Score
            FROM Person
            JOIN Patient ON Person.SVNr = Patient.SVNr
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        patients = []
        for row in rows:
            patients.append(
                {
                    "svnr": row[0],
                    "name": row[1],
                    "versicherung": row[2],
                    "naca_score": row[3],
                }
            )
        self._close_connection()
        return patients


    def get_all_doctors(self) -> list[dict]:
        self._init_new_connection()
        query = """
            SELECT Person.SVNr, Person.Name, Arzt.Fachrichtung, Arzt.Position, Arzt.Abteilungsname
            FROM Person
            JOIN Arzt ON Person.SVNr = Arzt.SVNr
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        doctors = []
        for row in rows:
            doctors.append(
                {
                    "svnr": row[0],
                    "name": row[1],
                    "fachrichtung": row[2],
                    "position": row[3],
                    "abteilung": row[4],
                }
            )
        self._close_connection()
        return doctors


    def get_all_clerks(self) -> list[dict]:
        self._init_new_connection()
        query = """
            SELECT Person.SVNr, Person.Name
            FROM Person
            JOIN Sachbearbeiter ON Person.SVNr = Sachbearbeiter.SVNr
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        clerks = []
        for row in rows:
            clerks.append({"svnr": row[0], "name": row[1]})
        self._close_connection()
        return clerks


    def get_doctor_booked_slots(self, doctor_svnr: str, date: str) -> list[str]:
        self._init_new_connection()
        query = """
            SELECT Uhrzeit
            FROM Termin
            WHERE SVNr_Arzt = ? AND Datum = ?
        """
        self.cursor.execute(query, (str(doctor_svnr), date))
        rows = self.cursor.fetchall()
        self._close_connection()
        
        # Convert time objects to string format "HH:MM" with zero-padding
        result = []
        for row in rows:
            if hasattr(row[0], "strftime"):
                result.append(row[0].strftime("%H:%M"))
            else:
                # Parse and reformat to ensure zero-padding (e.g., "8:00" -> "08:00")
                parts = str(row[0]).split(":")
                result.append(f"{int(parts[0]):02d}:{int(parts[1]):02d}")
        return result


    def get_patient_booked_slots(self, patient_svnr: str, date: str) -> list[str]:
        self._init_new_connection()
        query = """
            SELECT Uhrzeit
            FROM Termin
            WHERE SVNr_Patient = ? AND Datum = ?
        """
        self.cursor.execute(query, (str(patient_svnr), date))
        rows = self.cursor.fetchall()
        self._close_connection()

        # Convert time objects to string format "HH:MM" with zero-padding
        result = []
        for row in rows:
            if hasattr(row[0], "strftime"):
                result.append(row[0].strftime("%H:%M"))
            else:
                # Parse and reformat to ensure zero-padding (e.g., "8:00" -> "08:00")
                parts = str(row[0]).split(":")
                result.append(f"{int(parts[0]):02d}:{int(parts[1]):02d}")
        return result

    def get_next_termin_id(self, patient_svnr: str) -> int:
        self._init_new_connection()
        query = """
            SELECT COALESCE(MAX(TerminID), 0) + 1
            FROM Termin
            WHERE SVNr_Patient = ?
        """
        self.cursor.execute(query, (str(patient_svnr),))
        result = self.cursor.fetchone()
        self._close_connection()

        return result[0] if result else 1

    def create_appointment(self, patient_svnr: str, doctor_svnr: str, date: str, time: str, reason: str, clerk_svnr: str) -> int:
        termin_id = self.get_next_termin_id(patient_svnr)

        self._init_new_connection()
        query = """
            INSERT INTO Termin (TerminID, Datum, Uhrzeit, Grund, SVNr_Patient, SVNr_Arzt, SVNr_Sachbearbeiter)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(
            query,
            (termin_id, date, time, reason, str(patient_svnr), str(doctor_svnr), str(clerk_svnr) if clerk_svnr else None),
        )
        self.conn.commit()
        self._close_connection()

        return termin_id

    def check_appointment_conflict(self, doctor_svnr: str, patient_svnr: str, date: str, time: str) -> dict | None:
        self._init_new_connection()

        # Check doctor conflict
        query = """
            SELECT TerminID FROM Termin
            WHERE SVNr_Arzt = ? AND Datum = ? AND Uhrzeit = ?
        """
        self.cursor.execute(query, (str(doctor_svnr), date, time))
        if self.cursor.fetchone():
            self._close_connection()
            return {
                "type": "doctor",
                "message": "Der Arzt hat bereits einen Termin zu dieser Zeit.",
            }

        # Check patient conflict
        query = """
            SELECT TerminID FROM Termin
            WHERE SVNr_Patient = ? AND Datum = ? AND Uhrzeit = ?
        """
        self.cursor.execute(query, (str(patient_svnr), date, time))
        if self.cursor.fetchone():
            self._close_connection()
            return {
                "type": "patient",
                "message": "Der Patient hat bereits einen Termin zu dieser Zeit.",
            }
        
        self._close_connection()

        return None

    def get_patients_doctor_visits(self, start_date: str, end_date: str) -> list[dict]:
        self._init_new_connection()

        query = """ 
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
        """

        self.cursor.execute(query, (start_date, end_date))
        rows = self.cursor.fetchall()
        reports = []
        for row in rows:
            reports.append(
                {
                    "patient_svnr": row[0],
                    "patient_name": row[1],
                    "versicherung": row[2],
                    "arzt_svnr": row[3],
                    "arzt_name": row[4],
                    "fachrichtung": row[5],
                    "anzahl_termine": row[6],
                }
            )
        self._close_connection()

        return reports
