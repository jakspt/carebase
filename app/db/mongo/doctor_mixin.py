import re


class MongoDoctorMixin:
    # these become available at runtime, via the MongoBase class
    collection_patient_name: str
    collection_doctor_name: str
    collection_medication_name: str
    collection_clerk_name: str
    collection_appointment_name: str

    def _get_connection(self):
        raise NotImplementedError(
            "This class must be mixed into a class with a DB connection, implementing this method"
        )

    def find_patients(self, query: str) -> list[dict]:
        db = self._get_connection()

        # Regex that allows for partial match similar to the LIKE %query%
        regex_query = {"$regex": re.escape(query), "$options": "i"}

        # Search by _id (SVNr) OR Name
        patient_results = db[self.collection_patient_name].find(
            {"$or": [{"_id": regex_query}, {"name": regex_query}]},
            {"_id": 1, "name": 1},
        )

        return [{"id": doc["_id"], "name": doc["name"]} for doc in patient_results]

    def get_patient_details(self, patient_id: int) -> dict:
        db = self._get_connection()
        patient = db[self.collection_patient_name].find_one({"_id": str(patient_id)})

        if not patient:
            raise ValueError("Patient not found")

        formatted_appointments = []
        for term in patient.get("termine", []):
            formatted_appointments.append(
                {
                    "id": term["termin_id"],
                    "date": term["datum"].strftime("%Y-%m-%d"),
                    "time": term["uhrzeit"],
                    "doctor_name": term["arzt"]["name"],
                    "reason": term["grund"],
                }
            )

        formatted_appointments.sort(key=lambda x: (x["date"], x["time"]), reverse=True)

        return {
            "id": patient["_id"],
            "name": patient["name"],
            "insurance": patient.get("versicherung", ""),
            "appointments": formatted_appointments,
        }

    def get_all_meds(self) -> list[dict]:
        db = self._get_connection()
        retrieved_meds = db[self.collection_medication_name].find({})
        return [{"name": doc["name"], "id": doc["_id"]} for doc in retrieved_meds]

    def add_treatment(
        self, patient_id: int, appt_id: int, desc: str, cost: float, meds: list[dict]
    ) -> bool:
        db = self._get_connection()

        med_objects = []
        if meds:
            med_objects = [{"pzn": m["id"], "name": m["name"]} for m in meds]

        treatment_doc = {
            "beschreibung": desc,
            "kosten": cost,
            "medikamente": med_objects,
        }

        # Find Doctor + Year for Computed Pattern
        patient_data = db[self.collection_patient_name].find_one(
            {"_id": str(patient_id), "termine.termin_id": appt_id},
            {"termine.$": 1},  # fetch only the matching appt
        )

        if not patient_data or not patient_data.get("termine"):
            print("Appointment not found")
            return False

        appointment = patient_data["termine"][0]
        doctor_svnr = appointment["arzt"]["svnr"]
        year = appointment["datum"].year  # Extract year

        result = db[self.collection_patient_name].update_one(
            {"_id": str(patient_id), "termine.termin_id": appt_id},
            {"$push": {"termine.$.behandlungen": treatment_doc}},
        )

        if result.modified_count == 0:
            return False

        # Update Doctor Stats (Computed Pattern). This allows for a more efficient report
        cost_field = f"kosten_{year}"

        db[self.collection_doctor_name].update_one(
            {"_id": doctor_svnr}, {"$inc": {cost_field: cost}}
        )

        print(
            f"Successfully added treatment and updated {cost_field} for doctor {doctor_svnr}"
        )
        return True

    def get_doctor_report(self, start_year: int) -> list[dict]:
        db = self._get_connection()

        # [cite_start]Fetch all doctors [cite: 2]
        doctors = db[self.collection_doctor_name].find({})
        report = []

        for doc in doctors:
            # Scan document for computed cost fields (e.g., "kosten_2025")
            for key, value in doc.items():
                if key.startswith("kosten_"):
                    year_str = key.split("_")[1]
                    if year_str.isdigit():
                        year = int(year_str)

                        if year >= start_year:
                            report.append(
                                {
                                    "id": doc["_id"],
                                    "name": doc["name"],
                                    "specialty": doc.get("fachrichtung", ""),
                                    "dept": doc.get("abteilung", {}).get("name", ""),
                                    "year": year,
                                    "total_costs": float(value),
                                }
                            )

        # Sort by year DESC, then total_costs DESC, matching SQL logic
        report.sort(key=lambda x: (x["year"], x["total_costs"]), reverse=True)
        return report
