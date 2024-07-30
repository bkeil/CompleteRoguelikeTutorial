from __future__ import annotations

import dice
from components.base_component import BaseComponent

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entity import Actor

class Attributes(BaseComponent):
    parent: Actor

    def __init__(self,
                 strength: int, dexterity: int, constitution: int,
                 intelligence: int, wisdom: int, charisma: int):
        self.strength = strength
        self.dexterity = dexterity
        self.constitution = constitution
        self.intelligence = intelligence
        self.wisdom = wisdom
        self.charisma = charisma

    @staticmethod
    def modifier(stat: int) -> int:
        if stat < 4:
            return -2
        elif stat < 8:
            return -1
        elif stat < 14:
            return 0
        elif stat < 17:
            return 1
        else:
            return 2


def roll() -> Attributes:
    strength = dice.roll(3, 6)
    dexterity = dice.roll(3, 6)
    constitution = dice.roll(3, 6)
    intelligence = dice.roll(3, 6)
    wisdom = dice.roll(3, 6)
    charisma = dice.roll(3, 6)
    return Attributes(strength, dexterity, constitution, intelligence, wisdom, charisma)
