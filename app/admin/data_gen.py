import random
from datetime import date
from typing import Any

import mariadb
from faker import Faker
from faker.providers import ssn

from app.db.sql.base import SQLBase


class DataGenerator(SQLBase):
    def __init__(self):
        self.fake = Faker("de_AT")
        self.fake.add_provider(ssn)
        self.conn = self._get_connection()
        self.cursor = self.conn.cursor()

        # Store generated IDs for referential integrity
        self.cache = {
            "Abteilung": [],
            "Person": [],
            "Arzt": [],
            "Patient": [],
            "Sachbearbeiter": [],
            "Termin": [],
            "Behandlung": [],
            "Medikament": [],
        }

    def _execute_query(self, query, params):
        try:
            self.cursor.execute(query, params)
        except mariadb.Error as e:
            print(f"SQL Error: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")

    # allows for first generating the data in python, then inserting it once, minimizing network latency and DB overhead
    def _bulk_insert(self, sql, data_list):
        if not data_list:
            return
        try:
            self.cursor.executemany(sql, data_list)
        except mariadb.Error as e:
            print(f"Bulk Insert Error: {e}")

    def create_departments(self):
        batch_dept = []
        dept_names = [
            "Neurologie",
            "Unfallchirurgie",
            "Innere Medizin",
            "Radiologie",
            "Dermatologie",
            "Kardiologie",
            "Pädiatrie",
            "Onkologie",
        ]

        print(f"Generating {len(dept_names)} Departments...")

        sql = "INSERT INTO Abteilung (Name, Gebäude, Stockwerk) VALUES (?, ?, ?)"

        for name in dept_names:
            geb = f"Gebäude {random.choice(['A', 'B', 'C'])}"
            stock = f"{random.randint(1, 5)}. Stock"
            batch_dept.append((name, geb, stock))
            self.cache["Abteilung"].append(name)
        self._bulk_insert(sql, batch_dept)
        self.conn.commit()

    def create_meds(self, count=20):
        print(f"Generating {count} Medications...")
        med_sql = "INSERT INTO Medikament (PZN, Name, Wirkstoff) VALUES (?, ?, ?)"
        med_batch = []
        for i in range(count):
            pzn = 100000 + i
            name = self.fake.word().capitalize() + self.fake.random_element(
                ["in", "ol", "ex", "an"]
            )
            wirkstoff = self.fake.word().capitalize()
            med_batch.append((pzn, name, wirkstoff))
            self.cache["Medikament"].append(pzn)
        self._bulk_insert(med_sql, med_batch)
        self.conn.commit()

    def create_persons(self, count=100):
        print(f"Generating {count} Persons...")
        person_sql = "INSERT INTO Person (SVNr, Name, Adresse) VALUES (?, ?, ?)"
        person_batch = []
        for _ in range(count):
            birth_date = self.fake.date_of_birth(minimum_age=18, maximum_age=98)
            # faker's de_AT locale can produce realistic Austrian SSNs
            svnr = self.fake.unique.ssn(birthdate=birth_date)
            name = self.fake.name()
            address = self.fake.address().replace("\n", ", ")

            person_batch.append((svnr, name, address))
            self.cache["Person"].append({"SVNr": svnr, "Name": name})
        self._bulk_insert(person_sql, person_batch)
        self.conn.commit()

    # Assign roles, creating the specified numbers of doctors and clerks. The remaining persons become patients.
    def distribute_roles(self, num_doctors=10, num_clerk=5):
        print("Distributing roles...")

        people = self.cache["Person"][:]

        num_depts = len(self.cache["Abteilung"])
        if num_doctors < num_depts:
            print(
                f"Warning: Not enough doctors ({num_doctors}) to cover all departments ({num_depts}). Increasing doctors."
            )
            num_doctors = num_depts

        # Split lists
        doctors = people[:num_doctors]
        clerks = people[num_doctors : num_doctors + num_clerk]
        patients = people[num_doctors + num_clerk :]

        self.create_doctors(doctors)
        self.create_clerks(clerks)
        self.create_patients(patients)

        self.conn.commit()

    def create_patients(self, persons: list[dict]):
        sql_pat = "INSERT INTO Patient (SVNr, Versicherungsträger, NACA_Score) VALUES (?, ?, ?)"
        batch_pat = []
        versicherungen = ["ÖGK", "BVAEB", "SVS"]
        for pat in persons:
            vers = random.choice(versicherungen)
            naca = random.randint(0, 7)
            batch_pat.append((pat["SVNr"], vers, naca))
            self.cache["Patient"].append(pat["SVNr"])
        self._bulk_insert(sql_pat, batch_pat)

    def create_clerks(self, persons: list[dict]):
        sql_clerks = "INSERT INTO Sachbearbeiter (SVNr, Rolle, Anstellungsverhältnis) VALUES (?, ?, ?)"
        batch_clerks = []
        for clerk in persons:
            rolle = random.choice(["Aufnahme", "Verrechnung", "Archiv"])
            anstellung = random.choice(["Vollzeit", "Teilzeit", "Geringfügig"])
            batch_clerks.append((clerk["SVNr"], rolle, anstellung))
            self.cache["Sachbearbeiter"].append(clerk["SVNr"])
        self._bulk_insert(sql_clerks, batch_clerks)

    def create_doctors(self, persons: list[dict]):
        sql_doctor = """INSERT INTO Arzt (SVNr, Fachrichtung, Position, Abteilungsname, Vorgesetzter_SVNr)
                        VALUES (?, ?, ?, ?, ?)"""
        batch_arzt = []

        available_departments = self.cache["Abteilung"]
        fachrichtungen = ["Allgemeinmediziner", "Chirurg", "Internist"]

        department_chiefs = {}
        for i, dept_name in enumerate(available_departments):
            # Take the next doctor from the list
            chief_doc = persons[i]
            fach = random.choice(fachrichtungen)

            # Chief has no boss
            batch_arzt.append((chief_doc["SVNr"], fach, "Chefarzt", dept_name, None))
            department_chiefs[dept_name] = chief_doc["SVNr"]
            self.cache["Arzt"].append(chief_doc["SVNr"])

        remaining_doctors = persons[len(available_departments) :]

        for doc in remaining_doctors:
            dept_name = random.choice(available_departments)
            boss_svnr = department_chiefs[dept_name]
            fach = random.choice(fachrichtungen)
            batch_arzt.append(
                (doc["SVNr"], fach, "Assistenzarzt", dept_name, boss_svnr)
            )
            self.cache["Arzt"].append(doc["SVNr"])

        self._bulk_insert(sql_doctor, batch_arzt)

    def create_appointments(self, min_per_pat=1, max_per_pat=5):
        print(
            f"Generating Appointments (ensuring {min_per_pat}-{max_per_pat} per patient)..."
        )

        sql = """INSERT INTO Termin (TerminID, Datum, Uhrzeit, Grund, SVNr_Patient, SVNr_Arzt, SVNr_Sachbearbeiter)
                 VALUES (?, ?, ?, ?, ?, ?, ?)"""

        appt_batch = []
        generated_slots = set()
        appt_id_counter = 1

        for pat_svnr in self.cache["Patient"]:
            num_appts = random.randint(min_per_pat, max_per_pat)

            for _ in range(num_appts):
                # Try to find a free slot
                max_retries = 10
                for attempt in range(max_retries):
                    doc_svnr = random.choice(self.cache["Arzt"])
                    clerk_svnr = random.choice(self.cache["Sachbearbeiter"])
                    date_val = self.fake.date_between(
                        start_date="-2y", end_date="today"
                    )
                    time_val = self.gen_time()

                    # Doctor cannot be in two places
                    key_doc = (doc_svnr, date_val, time_val)
                    # Patient cannot be in two places
                    key_pat = (pat_svnr, date_val, time_val)

                    if self.no_collisions(generated_slots, key_doc, key_pat):
                        generated_slots.add(key_doc)
                        generated_slots.add(key_pat)

                        grund = random.choice(
                            [
                                "Kontrolle",
                                "Schmerzen",
                                "Impfung",
                                "Aufnahme",
                                "Gespräch",
                            ]
                        )

                        appt_batch.append(
                            (
                                appt_id_counter,
                                date_val,
                                time_val,
                                grund,
                                pat_svnr,
                                doc_svnr,
                                clerk_svnr,
                            )
                        )

                        # Cache for adding treatments later
                        self.cache["Termin"].append(
                            {"TerminID": appt_id_counter, "SVNr_Patient": pat_svnr}
                        )
                        appt_id_counter += 1
                        break  # move to next appointment

        print(f"Generated {len(appt_batch)} appointments in total.")
        self._bulk_insert(sql, appt_batch)
        self.conn.commit()

    def gen_time(self) -> str:
        hour = random.randint(8, 20)
        minute = random.choice([0, 30])
        time_val = f"{hour:02d}:{minute:02d}:00"
        return time_val

    def no_collisions(
        self,
        generated_slots: set[Any],
        key_doc: tuple[Any, date, str],
        key_pat: tuple[Any, date, str],
    ) -> bool:
        return key_doc not in generated_slots and key_pat not in generated_slots

    def create_treatment_details(self, count=40):
        print(f"Generating {count} Treatments...")

        possible_appts = self.cache["Termin"]
        count = min(count, len(possible_appts))

        selected_appts = random.sample(possible_appts, count)

        sql_treatment = """INSERT INTO Behandlung (BehandlungsID, Beschreibung, Kosten, SVNr_Patient, TerminID)
                     VALUES (?, ?, ?, ?, ?)"""
        sql_administration = (
            "INSERT INTO Verabreichung (BehandlungsID, PZN) VALUES (?, ?)"
        )
        batch_treatment = []
        batch_administration = []

        treatment_id_counter = 1

        for appt in selected_appts:
            treatment_id = treatment_id_counter
            desc = self.fake.sentence()
            cost = round(random.uniform(20.0, 2000.0), 2)

            """self._execute_query(
                sql_treatment,
                (treatment_id, desc, cost, appt["SVNr_Patient"], appt["TerminID"]),
            )"""
            batch_treatment.append(
                (treatment_id, desc, cost, appt["SVNr_Patient"], appt["TerminID"])
            )

            # Add random medications (Verabreichung)
            num_meds = random.randint(0, 3)
            if num_meds > 0:
                meds = random.sample(self.cache["Medikament"], num_meds)
                for pzn in meds:
                    batch_administration.append((treatment_id, pzn))

            treatment_id_counter += 1
        self._bulk_insert(sql_treatment, batch_treatment)
        self._bulk_insert(sql_administration, batch_administration)
        self.conn.commit()

    def generate_all(self):
        print("--- Starting Data Generation ---")
        self.clear_all_data()
        try:
            self.create_departments()
            self.create_meds(300)
            self.create_persons(count=1120)
            self.distribute_roles(num_doctors=100, num_clerk=20)
            self.create_appointments(min_per_pat=1, max_per_pat=5)
            self.create_treatment_details(count=500)
            print("--- Data Generation Complete ---")
        except Exception as e:
            print(f"An error occurred during generation: {e}")
            self.conn.rollback()
        finally:
            self.conn.close()

    def clear_all_data(self):
        if not self.conn:
            print("No connection available to clear data.")
            return

        print("Clearing all existing data...")
        tables = [
            "Verabreichung",
            "Medikament",
            "Behandlung",
            "Termin",
            "Sachbearbeiter",
            "Arzt",
            "Patient",
            "Person",
            "Abteilung"
        ]

        try:
            # Disabling foreign keys allows deleting in any order
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

            for table in tables:
                self.cursor.execute(f"TRUNCATE TABLE {table}")
                print(f"Cleared table: {table}")

            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

            self.conn.commit()

            self.cache = {
                "Abteilung": [],
                "Person": [],
                "Arzt": [],
                "Patient": [],
                "Sachbearbeiter": [],
                "Termin": [],
                "Behandlung": [],
                "Medikament": [],
            }
            print("Database cleared successfully.")

        except mariadb.Error as e:
            print(f"Error clearing data: {e}")
            # Re-enable checks in any case
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            self.conn.rollback()
