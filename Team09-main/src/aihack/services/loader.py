import json
import os
import random
from typing import List
from ..models import Hero, Maou, Monster, Field

class DataLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def _read_json(self, filename: str):
        path = os.path.join(self.data_dir, filename)
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_hero(self) -> Hero:
        data = self._read_json("yuusya.json")
        return Hero(
            name="勇者",
            attribute=data["Type"],
            hp=data["HP"],
            attack=data["Attack"],
            defense=data["Defense"],
            personality=data["Personality"]
        )

    def load_maou(self) -> Maou:
        data = self._read_json("maou.json")
        return Maou(
            name="魔王",
            attribute=data["Type"],
            hp=data["HP"],
            attack=data["Attack"],
            defense=data["Defense"],
            personality=data["Personality"]
        )

    def load_field(self) -> Field:
        data = self._read_json("field.json")
        field_data = random.choice(data["fields"])
        return Field(
            name=field_data["name"],
            attribute=field_data["Type"]
        )

    def load_monsters(self) -> List[Monster]:
        data = self._read_json("monster.json")
        monsters = []
        for m in data["monsters"]:
            monsters.append(Monster(
                name=m["name"],
                attribute=m["attribute"],
                hp=m["stats"]["HP"],
                attack=m["stats"]["Attack"],
                defense=m["stats"]["Defense"],
                personality=m["personality"]
            ))
        return monsters
    
    def load_story(self, filename: str):
         return self._read_json(filename)
