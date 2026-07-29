from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseMemory(ABC):
    @abstractmethod
    def store(self, patient_id: int, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Saves a key-value memory item linked to a patient."""
        pass

    @abstractmethod
    def retrieve(self, patient_id: int, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves items matching a query for a patient."""
        pass

    @abstractmethod
    def clear(self, patient_id: int) -> None:
        """Purges memory records for a specific patient context."""
        pass
