class MongoDoctorMixin:
    def find_patients(self, query: str) -> list[dict]:
        pass

    # get details plus all appointments
    def get_patient_details(self, patient_id: int) -> list:
        pass

    def get_all_meds(self) -> list[dict]:
        pass

    def get_med_id_by_name(self, name: str) -> int:
        pass

    def add_treatment(
        self, patient_id: int, appt_id: int, desc: str, cost: float, meds: list[str]
    ) -> bool:
        pass
