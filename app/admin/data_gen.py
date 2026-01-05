import random
from datetime import datetime, timedelta

import mariadb
from faker import Faker
from faker.providers import ssn

from app.db.sql.base import SQLBase


class DataGenerator(SQLBase):
    def __init__(self):
        self.fake = Faker('de_AT')
        self.fake.add_provider(ssn)
        self.conn = self._get_connection()
        self.cursor = self.conn.cursor() if self.conn else None

        # Cache generated IDs to maintain referential integrity in memory
        self.cache = {
            'Abteilung': [],
            'Person': [],
            'Arzt': [],
            'Patient': [],
            'Sachbearbeiter': [],
            'Termin': [],  # Stores dicts with composite keys
            'Behandlung': [],
            'Medikament': []
        }

    """def _generate_svnr(self, birthdate):
        # Generates a pseudo-valid Austrian SVNr (10 digits).
        check_digits = str(random.randint(1000, 9999))
        dob_str = birthdate.strftime('%d%m%y')
        return f"{check_digits}{dob_str}"""""

    def _execute_query(self, query, params):
        try:
            self.cursor.execute(query, params)
        except mariadb.Error as e:
            print(f"SQL Error: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")

    def create_abteilungen(self, count=5):
        print(f"Generating {count} Abteilungen...")
        dept_names = ['Kardiologie', 'Neurologie', 'Unfallchirurgie', 'Innere Medizin',
                      'Radiologie', 'Dermatologie', 'Pädiatrie', 'Onkologie']

        # Ensure we don't try to create more unique departments than we have names for
        count = min(count, len(dept_names))
        selected = dept_names[:count]

        sql = "INSERT INTO Abteilung (Name, Gebäude, Stockwerk) VALUES (?, ?, ?)"

        for name in selected:
            geb = f"Gebäude {random.choice(['A', 'B', 'C'])}"
            stock = f"{random.randint(1, 5)}. Stock"
            self._execute_query(sql, (name, geb, stock))
            self.cache['Abteilung'].append(name)

        self.conn.commit()

    def create_medikamente(self, count=20):
        print(f"Generating {count} Medikamente...")
        sql = "INSERT INTO Medikament (PZN, Name, Wirkstoff) VALUES (?, ?, ?)"

        for i in range(count):
            pzn = 100000 + i
            name = self.fake.word().capitalize() + "in"
            wirkstoff = self.fake.word().capitalize()
            self._execute_query(sql, (pzn, name, wirkstoff))
            self.cache['Medikament'].append(pzn)

        self.conn.commit()

    def create_personen(self, count=100):
        print(f"Generating {count} Personen...")
        sql = "INSERT INTO Person (SVNr, Name, Adresse) VALUES (?, ?, ?)"

        for _ in range(count):
            dob = self.fake.date_of_birth(minimum_age=18, maximum_age=90)
            svnr = self.fake.unique.ssn(dob)

            # Simple collision check
            # while svnr in [p['SVNr'] for p in self.cache['Person']]:
            #   svnr = self.fake.ssn(str(dob))

            name = self.fake.name()
            adresse = self.fake.address().replace('\n', ', ')

            self._execute_query(sql, (svnr, name, adresse))
            self.cache['Person'].append({'SVNr': svnr, 'Name': name})

        self.conn.commit()

    def distribute_roles(self, num_doctors=10, num_admin=5):
        """Assigns the generated Persons to specific roles (Arzt, Patient, etc.)"""
        print("Distributing roles...")

        # Shuffle the cached people
        people = self.cache['Person'][:]
        random.shuffle(people)

        # Split lists
        doctors = people[:num_doctors]
        admins = people[num_doctors:num_doctors + num_admin]
        patients = people[num_doctors + num_admin:]

        # 1. Create Doctors
        sql_arzt = """INSERT INTO Arzt (SVNr, Fachrichtung, Position, Abteilungsname, Vorgesetzter_SVNr)
                      VALUES (?, ?, ?, ?, ?)"""

        # Pick a chief
        chief = doctors[0]
        self._execute_query(sql_arzt, (
            chief['SVNr'], 'Leitender Arzt', 'Chefarzt',
            random.choice(self.cache['Abteilung']), None
        ))
        self.cache['Arzt'].append(chief['SVNr'])

        fachrichtungen = ['Allgemeinmediziner', 'Chirurg', 'Internist']

        for doc in doctors[1:]:
            fach = random.choice(fachrichtungen)
            abt = random.choice(self.cache['Abteilung'])
            # 80% chance to report to chief
            boss = chief['SVNr'] if random.random() > 0.2 else None

            self._execute_query(sql_arzt, (doc['SVNr'], fach, 'Assistenzarzt', abt, boss))
            self.cache['Arzt'].append(doc['SVNr'])

        # 2. Create Admins (Sachbearbeiter)
        sql_sach = "INSERT INTO Sachbearbeiter (SVNr, Rolle, Anstellungsverhältnis) VALUES (?, ?, ?)"
        for admin in admins:
            rolle = random.choice(['Aufnahme', 'Verrechnung', 'Archiv'])
            verh = random.choice(['Vollzeit', 'Teilzeit'])
            self._execute_query(sql_sach, (admin['SVNr'], rolle, verh))
            self.cache['Sachbearbeiter'].append(admin['SVNr'])

        # 3. Create Patients
        sql_pat = "INSERT INTO Patient (SVNr, Versicherungsträger, NACA_Score) VALUES (?, ?, ?)"
        versicherungen = ['ÖGK', 'BVAEB', 'SVS']
        for pat in patients:
            vers = random.choice(versicherungen)
            naca = random.randint(0, 7)
            self._execute_query(sql_pat, (pat['SVNr'], vers, naca))
            self.cache['Patient'].append(pat['SVNr'])

        self.conn.commit()

    def create_termin_transaction(self, count=50):
        print(f"Generating {count} Termine...")
        sql = """INSERT INTO Termin (TerminID, Datum, Uhrzeit, Grund, SVNr_Patient, SVNr_Arzt, SVNr_Sachbearbeiter)
                 VALUES (?, ?, ?, ?, ?, ?, ?)"""

        generated_slots = set()
        c = 0

        while c < count:
            pat = random.choice(self.cache['Patient'])
            doc = random.choice(self.cache['Arzt'])
            admin = random.choice(self.cache['Sachbearbeiter']) if random.random() > 0.5 else None

            # Random time in last 30 days
            day_offset = random.randint(0, 30)
            date_val = datetime.now().date() - timedelta(days=day_offset)
            time_val = f"{random.randint(8, 16):02d}:00:00"

            # Unique Constraint Check (Arzt+Time OR Patient+Time)
            key_doc = (doc, date_val, time_val)
            key_pat = (pat, date_val, time_val)

            if key_doc not in generated_slots and key_pat not in generated_slots:
                generated_slots.add(key_doc)
                generated_slots.add(key_pat)

                # TerminID (assuming unique int)
                t_id = c + 1
                grund = random.choice(['Kontrolle', 'Schmerzen', 'Impfung'])

                self._execute_query(sql, (t_id, date_val, time_val, grund, pat, doc, admin))

                # Cache for next step (Behandlung)
                self.cache['Termin'].append({'TerminID': t_id, 'SVNr_Patient': pat})
                c += 1

        self.conn.commit()

    def create_behandlung_details(self, count=40):
        print(f"Generating {count} Behandlungen & Verabreichungen...")

        # We can only create treatments for existing appointments
        possible_termins = self.cache['Termin']
        count = min(count, len(possible_termins))

        selected_termins = random.sample(possible_termins, count)

        sql_beh = """INSERT INTO Behandlung (BehandlungsID, Beschreibung, Kosten, SVNr_Patient, TerminID)
                     VALUES (?, ?, ?, ?, ?)"""
        sql_ver = "INSERT INTO Verabreichung (BehandlungsID, PZN) VALUES (?, ?)"

        b_id_counter = 1

        for t in selected_termins:
            b_id = b_id_counter
            desc = self.fake.sentence()
            cost = round(random.uniform(50.0, 2000.0), 2)

            self._execute_query(sql_beh, (b_id, desc, cost, t['SVNr_Patient'], t['TerminID']))

            # Add random medications (Verabreichung)
            num_meds = random.randint(0, 3)
            if num_meds > 0:
                meds = random.sample(self.cache['Medikament'], num_meds)
                for pzn in meds:
                    self._execute_query(sql_ver, (b_id, pzn))

            b_id_counter += 1

        self.conn.commit()

    def generate_all(self):
        """Master function to run the full pipeline."""
        if not self.conn:
            print("No DB Connection. Exiting.")
            return

        print("--- Starting Data Generation ---")
        self.clear_all_data()
        try:
            self.create_abteilungen()
            self.create_medikamente()
            self.create_personen(count=100)
            self.distribute_roles(num_doctors=10, num_admin=5)
            self.create_termin_transaction(count=50)
            self.create_behandlung_details(count=40)
            print("--- Data Generation Complete ---")
        except Exception as e:
            print(f"An error occurred during generation: {e}")
            self.conn.rollback()
        finally:
            self.conn.close()

    def clear_all_data(self):
        """
        Clears all data from the tables while keeping the table structure.
        Uses FOREIGN_KEY_CHECKS=0 to bypass constraint ordering issues.
        """
        if not self.conn:
            print("No connection available to clear data.")
            return

        print("--- Clearing all existing data ---")
        tables = [
            'Verabreichung', 'Behandlung', 'Termin',
            'Patient', 'Arzt', 'Sachbearbeiter',
            'Person', 'Abteilung', 'Medikament'
        ]

        try:
            # 1. Disable Foreign Key Checks so we can delete in any order
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

            # 2. Truncate all tables (faster and cleaner than DELETE FROM)
            for table in tables:
                self.cursor.execute(f"TRUNCATE TABLE {table}")
                print(f"Cleared table: {table}")

            # 3. Re-enable Foreign Key Checks
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

            self.conn.commit()

            # 4. Clear the internal cache so we don't try to reuse deleted IDs
            self.cache = {
                'Abteilung': [],
                'Person': [],
                'Arzt': [],
                'Patient': [],
                'Sachbearbeiter': [],
                'Termin': [],
                'Behandlung': [],
                'Medikament': []
            }
            print("--- Database cleared successfully ---")

        except mariadb.Error as e:
            print(f"Error clearing data: {e}")
            # Ensure checks are re-enabled even if something fails
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            self.conn.rollback()
