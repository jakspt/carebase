from abc import ABC, abstractmethod


class DatabaseStrategy(ABC):
    # DOCTOR USE CASE (Usecase 1)
    @abstractmethod
    def find_patients(self, query: str) -> list[dict]:
        pass

    @abstractmethod
    def get_patient_details(self, patient_id: int) -> dict:
        pass

    @abstractmethod
    def get_all_meds(self) -> list[dict]:
        pass

    @abstractmethod
    def add_treatment(
        self, patient_id: int, appt_id: int, desc: str, cost: float, meds: list[dict]
    ) -> bool:
        pass

    @abstractmethod
    def get_doctor_report(self, start_year: int) -> list[dict]:
        pass

    # Shared functionality, implemented in MongoBase/SQLBase
    # --- CLERK USE CASE (User B), examples ---
    @abstractmethod
    def get_all_clerks(self) -> list[dict]: pass

    @abstractmethod
    def get_all_patients(self) -> list[dict]: pass
    
    @abstractmethod
    def get_all_doctors(self) -> list[dict]: pass

    @abstractmethod
    def get_doctor_booked_slots(self, doctor_svnr: int, date: str) -> list[str]: pass
    
    @abstractmethod
    def get_patient_booked_slots(self, patient_svnr: int, date: str) -> list[str]: pass

    @abstractmethod
    def create_appointment(self, patient_svnr: int, doctor_svnr: int, date: str, time: str, reason: str, clerk_svnr: int) -> int: pass
    
    @abstractmethod
    def check_appointment_conflict(self, doctor_svnr: int, patient_svnr: int, date: str, time: str) -> dict | None: pass

    @abstractmethod
    def get_patients_doctor_visits(self, start_date: str, end_date: str) -> list[dict]: pass
    # --- Shared functionality, implement in MongoBase/SQLBase
    @abstractmethod
    def _get_connection(self):
        pass
