import pytest
from aihack.models import Hero, Field
from aihack.services.status import StatusService

def test_apply_field_bonus():
    hero = Hero(name="TestHero", attribute="Fire", hp=100, attack=10, defense=10, personality="")
    field = Field(name="Volcano", attribute="Fire")
    
    StatusService.apply_field_bonus(hero, field)
    
    assert hero.hp == 110
    assert hero.attack == 11
    assert hero.defense == 11

def test_apply_field_bonus_no_match():
    hero = Hero(name="TestHero", attribute="Water", hp=100, attack=10, defense=10, personality="")
    field = Field(name="Volcano", attribute="Fire")
    
    StatusService.apply_field_bonus(hero, field)
    
    assert hero.hp == 100
    assert hero.attack == 10
    assert hero.defense == 10