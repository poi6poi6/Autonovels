from abc import ABC, abstractmethod
from typing import Any, Dict


class Agent(ABC):
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config

    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
