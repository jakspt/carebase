class SQLDoctorMixin:
    def _get_connection(self):
        raise NotImplementedError(
            "This class must be mixed into a class with a DB connection, implementing this method"
        )

    def find_patients(self, query: str) -> list[dict]:
        connection = self._get_connection()
        cursor = connection.cursor(dictionary=True)
        sql = self._get_find_patient_sql(query)

        search_string = f"%{query}%"

        cursor.execute(sql, (search_string,))
        results = cursor.fetchall()
        cursor.close()
        connection.close()

        print("Found patients")

        return [{"id": row["SVNr"], "name": row["Name"]} for row in results]

    def _get_find_patient_sql(self, query: str) -> str:
        if query.isdecimal():
            return """SELECT p.SVNr, per.Name
                      FROM Patient p
                               JOIN Person per ON p.SVNr = per.SVNr
                      WHERE p.SVNr LIKE ?
                   """
        else:
            return """
                   SELECT p.SVNr, per.Name
                   FROM Patient p
                            JOIN Person per ON p.SVNr = per.SVNr
                   WHERE per.Name LIKE ?
                   """

    def get_patient_details(self, patient_id: int) -> dict:
        connection = self._get_connection()
        cursor = connection.cursor(dictionary=True)

        patient_sql = """
                      SELECT p.SVNr, per.Name, p.Versicherungsträger
                      FROM Patient p
                               JOIN Person per ON p.SVNr = per.SVNr
                      WHERE p.SVNr = ?
                      """

        cursor.execute(patient_sql, (str(patient_id),))
        fetched_patient = cursor.fetchone()
        if not fetched_patient:
            raise ValueError("Patient not found")

        appointments_sql = """
                           SELECT t.TerminID,
                                  t.Datum,
                                  t.Uhrzeit,
                                  t.Grund,
                                  per.Name as DoctorName
                           FROM Termin t
                                    JOIN Arzt a ON t.SVNr_Arzt = a.SVNr
                                    JOIN Person per ON a.SVNr = per.SVNr
                           WHERE t.SVNr_Patient = ?
                           ORDER BY t.Datum DESC, t.Uhrzeit DESC
                           """

        cursor.execute(appointments_sql, (patient_id,))
        appointment_rows = cursor.fetchall()

        cursor.close()
        connection.close()

        return {
            "id": fetched_patient["SVNr"],
            "name": fetched_patient["Name"],
            "insurance": fetched_patient["Versicherungsträger"],
            "appointments": [
                {
                    "id": appt["TerminID"],
                    "date": str(appt["Datum"]),
                    "time": str(appt["Uhrzeit"]),
                    "doctor_name": appt["DoctorName"],
                    "reason": appt["Grund"],
                }
                for appt in appointment_rows
            ],
        }

    def get_all_meds(self) -> list[dict]:
        # actually changed this to return the whole med objects (well, the name + id)
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = "SELECT PZN, Name FROM Medikament"

        cursor.execute(sql)
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        return [{"name": row["Name"], "id": row["PZN"]} for row in results]

    def add_treatment(
        self, patient_id: str, appt_id: int, desc: str, cost: float, meds: list[dict]
    ) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # BehandlungsID needs to be created manually
            cursor.execute("SELECT COALESCE(MAX(BehandlungsID), 0) + 1 FROM Behandlung")
            new_treatment_id = cursor.fetchone()[0]

            sql_treatment = """
                            INSERT INTO Behandlung
                                (BehandlungsID, Beschreibung, Kosten, SVNr_Patient, TerminID)
                            VALUES (?, ?, ?, ?, ?)
                            """
            cursor.execute(
                sql_treatment, (new_treatment_id, desc, cost, patient_id, appt_id)
            )

            # only insert if provided
            if meds:
                sql_administrations = """
                           INSERT INTO Verabreichung (BehandlungsID, PZN)
                           VALUES (?, ?)
                           """
                administration_values = [(new_treatment_id, med["id"]) for med in meds]

                cursor.executemany(sql_administrations, administration_values)

            conn.commit()
            print(
                f"Successfully added treatment (ID: {new_treatment_id}) and administered medications"
            )
            return True

        except Exception as e:
            conn.rollback()
            print(f"Error adding treatment: {e}")
            return False

        finally:
            cursor.close()
            conn.close()

    def get_doctor_report(self, start_date: str) -> list[dict]:
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
              SELECT a.SVNr AS arzt_svnr,
                     p.Name AS arzt_name,
                     a.Fachrichtung,
                     a.Abteilungsname, YEAR(t.Datum) AS jahr,
                  SUM(b.Kosten) AS gesamt_behandlungskosten
              FROM
                  Behandlung b
                  JOIN Termin t
              ON b.SVNr_Patient = t.SVNr_Patient
                  AND b.TerminID = t.TerminID
                  JOIN Arzt a ON t.SVNr_Arzt = a.SVNr
                  JOIN Person p ON a.SVNr = p.SVNr
              WHERE
                  t.Datum >= ?
              GROUP BY
                  a.SVNr,
                  p.Name,
                  a.Fachrichtung,
                  a.Abteilungsname,
                  YEAR(t.Datum)
              ORDER BY
                  jahr DESC, gesamt_behandlungskosten DESC;
              """
        # TODO: also discuss the jahr DESC in report
        cursor.execute(sql, (start_date,))
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        # TODO: change the naming here to be English as well

        report = []
        for row in results:
            report.append(
                {
                    "id": row["arzt_svnr"],
                    "name": row["arzt_name"],
                    "specialty": row["Fachrichtung"],
                    "dept": row["Abteilungsname"],
                    "year": row["jahr"],
                    "total_costs": float(row["gesamt_behandlungskosten"] or 0.0),
                }
            )

        return report
