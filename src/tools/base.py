from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    """
    All tools MUST follow this interface.
    """

    name: str
    description: str

    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> str:
        pass
