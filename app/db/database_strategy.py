from abc import ABC, abstractmethod

class DatabaseStrategy(ABC):
    """
    The Interface: All database strategies must implement these methods.
    """
    
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def get_by_id(self, table_name: str, record_id: int):
        pass

    @abstractmethod
    def insert(self, table_name: str, data: dict):
        pass

    @abstractmethod
    def update(self, table_name: str, record_id: int, data: dict):
        pass