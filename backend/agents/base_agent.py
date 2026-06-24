from abc import ABC, abstractmethod

class BaseAgent(ABC):
    @abstractmethod
    async def run(self, query: str, context: dict) -> dict:
        """
        Returns:
            { response: str, sources: list, metadata?: dict }
        """
        pass
