import pytest
from aihack.services.loader import DataLoader
from aihack.models import Hero, Maou, Monster, Field

def test_load_hero():
    loader = DataLoader("JsonFolder")
    hero = loader.load_hero()
    assert isinstance(hero, Hero)
    assert hero.name == "勇者"

def test_load_maou():
    loader = DataLoader("JsonFolder")
    maou = loader.load_maou()
    assert isinstance(maou, Maou)
    assert maou.name == "魔王"

def test_load_field():
    loader = DataLoader("JsonFolder")
    field = loader.load_field()
    assert isinstance(field, Field)
    assert field.name == "火山"

def test_load_monsters():
    loader = DataLoader("JsonFolder")
    monsters = loader.load_monsters()
    assert len(monsters) == 5