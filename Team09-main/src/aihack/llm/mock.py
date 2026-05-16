import json
import os
from .abstract import LLMService

class MockLLMService(LLMService):
    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def generate_reaction(self, monster_personality: str, command: str) -> str:
        # personality.jsonを読み込んでLLMの反応をモック化
        path = os.path.join(self.data_dir, "personality.json")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("Personality", "反応なし")
        except FileNotFoundError:
            return "反応なし"
