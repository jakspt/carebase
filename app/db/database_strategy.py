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
    @abstractmethod
    def _get_connection(self):
        pass
