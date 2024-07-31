from __future__ import annotations

from typing import Dict, TYPE_CHECKING
from dataclasses import dataclass

import dice


@dataclass(frozen=True)
class Stat:
    name: str
    nick: str


STR = Stat('strength', 'STR')
DEX = Stat('dexterity', 'DEX')
CON = Stat('constitution', 'CON')
INT = Stat('intelligence', 'INT')
WIS = Stat('wisdom', 'WIS')
CHR = Stat('charisma', 'CHR')

PHYSICAL = (STR, DEX, CON)
MENTAL = (INT, WIS, CHR)
ALL = PHYSICAL + MENTAL


def modifier(val: int) -> int:
    if val < 4:
        return -2
    elif val < 8:
        return -1
    elif val < 14:
        return 0
    elif val < 17:
        return 1
    else:
        return 2


def roll() -> Dict[Stat, int]:
    strength = dice.roll(3, 6)
    dexterity = dice.roll(3, 6)
    constitution = dice.roll(3, 6)
    intelligence = dice.roll(3, 6)
    wisdom = dice.roll(3, 6)
    charisma = dice.roll(3, 6)
    return {
        STR: strength, DEX: dexterity, CON: constitution, INT: intelligence, WIS: wisdom, CHR: charisma
    }


def typical() -> Dict[Stat, int]:
    return {STR: 10, DEX: 10, CON: 10, INT: 10, WIS: 10, CHR: 10}
