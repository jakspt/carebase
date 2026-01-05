class SQLDoctorMixin:
    def find_patients(self, query: str) -> list[dict]:
        print("Found patients")
        # return []
        return [{"id": 1234, "name": "Herr drfsfds"}, {"id": 1235, "name": "Frau drfsfds"}]

    # TODO: Correctly implement everything!

    # get details plus all appointments
    def get_patient_details(self, patient_id: int) -> dict:
        # FIXME: See what happens if a termin is on same date + same time (collision)
        return {"id": 1234,
                "name": "Herr drfsfds",
                "insurance": "Versicherung A",
                "appointments": [
                    {
                        "id": 1,
                        "date": "2025-01-01",
                        "time": "12:00",
                        "doctor_name": "Doc dctorue",
                        "reason": "Zeitdruck"
                    },
                    {
                        "id": 2,
                        "date": "2025-02-01",
                        "time": "12:05",
                        "doctor_name": "Doc dctorue",
                        "reason": "Zeitdruck"
                    },
                    {
                        "id": 3,
                        "date": "2025-01-01",
                        "time": "12:10",
                        "doctor_name": "Doc dctorue",
                        "reason": "Zeitdruck"
                    },
                    {
                        "id": 4,
                        "date": "2025-02-01",
                        "time": "12:30",
                        "doctor_name": "Doc dctorue",
                        "reason": "Zeitdruck"
                    }
                ]}

    def get_all_med_names(self) -> list[str]:
        return ["medizin1", "medizin2", "medizin3", "medizin4"]

    # FIXME: should be private-only method
    def get_med_id_by_name(self, name: str) -> int:
        pass

    def add_treatment(self, patient_id: int, appt_id: int, desc: str, cost: float, meds: list[str]) -> bool:
        print("Successfully added treatment")
        return True

    def get_doctor_report(self, start_date: str) -> list[dict]:
        return [{"id": 1234, "name": "Herr Dokdok", "fach": "clown", "abt": "jokers", "jahr": 2025,
                 "gesamt_kosten": 500.45},
                {"id": 1235, "name": "Herr Dokdoki", "fach": "clown", "abt": "jokers", "jahr": 2025,
                 "gesamt_kosten": 500.45},
                {"id": 1234, "name": "Herr Dokdok", "fach": "clown", "abt": "jokers", "jahr": 2024,
                 "gesamt_kosten": 500.45},
                {"id": 1235, "name": "Herr Dokdoki", "fach": "clown", "abt": "jokers", "jahr": 2024,
                 "gesamt_kosten": 10000.45},
                {"id": 1234, "name": "Herr Dokdok", "fach": "clown", "abt": "jokers", "jahr": 2023,
                 "gesamt_kosten": 500.45},
                {"id": 1235, "name": "Herr Dokdoki", "fach": "clown", "abt": "jokers", "jahr": 2023,
                 "gesamt_kosten": 500.45}]
