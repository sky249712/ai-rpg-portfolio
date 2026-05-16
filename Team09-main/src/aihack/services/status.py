from ..models import Character, Field

class StatusService:
    @staticmethod
    def apply_field_bonus(character: Character, field: Field):
        if character.attribute == field.attribute:
            character.hp = int(character.hp * 1.1)
            character.attack = int(character.attack * 1.1)
            character.defense = int(character.defense * 1.1)
