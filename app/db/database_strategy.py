from abc import ABC, abstractmethod


class DatabaseStrategy(ABC):
    """
    The Interface: All database strategies must implement these methods.
    => Abstraktionen auf Domain-Level halten, u.a. wg. Embedding auf MongoDB dann (1 table != 1 Collection)
    """

    # --- DOCTOR USE CASE (User A), examples ---
    @abstractmethod
    def find_patients(self, query: str) -> list[dict]: pass

    # get details plus all appointments
    @abstractmethod
    def get_patient_details(self, patient_id: int) -> list: pass

    @abstractmethod
    def get_all_med_names(self) -> list[str]: pass

    @abstractmethod
    def get_med_id_by_name(self, name: str) -> int: pass

    @abstractmethod
    def add_treatment(self, patient_id: int, appt_id: int, desc: str, cost: float, meds: list[str]) -> bool: pass

    # --- CLERK USE CASE (User B), examples ---
    @abstractmethod
    def get_all_patients(self) -> list[dict]: pass
    
    @abstractmethod
    def get_all_doctors(self) -> list[dict]: pass

    @abstractmethod
    def get_booked_slots(self, doctor_svnr: str, date: str) -> list[str]: pass
    
    @abstractmethod
    def get_patient_booked_slots(self, patient_svnr: str, date: str) -> list[str]: pass
    # --- Shared functionality, implement in MongoBase/SQLBase
    @abstractmethod
    def _get_connection(self):
        pass

    """
    @abstractmethod
    def get_by_id(self, table_name: str, record_id: int):
        pass

    @abstractmethod
    def insert(self, table_name: str, data: dict):
        pass

    @abstractmethod
    def update(self, table_name: str, record_id: int, data: dict):
        pass
    """
