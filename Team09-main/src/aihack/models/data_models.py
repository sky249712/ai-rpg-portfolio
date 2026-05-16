from dataclasses import dataclass
from typing import Optional

@dataclass
class Stats:
    hp: int
    attack: int
    defense: int

    @property
    def hp_float(self) -> float:
        return float(self.hp)

@dataclass
class Character:
    name: str
    attribute: str
    hp: int
    attack: int
    defense: int
    personality: str

@dataclass
class Monster(Character):
    motivation: float = 1.0
    command: str = ""
    thought: str = ""

@dataclass
class Hero(Character):
    pass

@dataclass
class Maou(Character):
    pass

@dataclass
class Field:
    name: str
    attribute: str
