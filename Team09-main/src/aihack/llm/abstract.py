from abc import ABC, abstractmethod
from typing import Optional

class LLMService(ABC):
    @abstractmethod
    def generate_reaction(self, monster_personality: str, command: str) -> str:
        """
        モンスターの性格と命令に基づいて反応を生成します。
        """
        pass
