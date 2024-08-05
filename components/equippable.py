from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

import attributes
from components.base_component import BaseComponent
from equipment_types import EquipmentType

if TYPE_CHECKING:
    from entity import Item


@dataclasses.dataclass(frozen=True)
class Shock:
    damage: int
    max_ac: int


class Equippable(BaseComponent):
    parent: Item

    def __init__(
            self,
            equipment_type: EquipmentType,
            damage: tuple[int, int, int] = (1, 2, 0),
            shock: Shock = Shock(0, 0),
            ac: int = 0,
            attribute: tuple[attributes.Stat, ...] = (attributes.STR, attributes.DEX,)
    ):
        self.equipment_type = equipment_type
        self.damage = damage
        self.shock = shock
        self.ac = ac
        self.attribute = attribute


class Dagger(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON, damage=(1, 4, 0), shock=Shock(1, 15))


class ShortSword(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON, damage=(1, 6, 0), shock=Shock(2, 15))


class LongSword(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON, damage=(1, 8, 0), shock=Shock(2, 13))


class WarAxe(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON, damage=(1, 10, 0), shock=Shock(3, 15),
                         attribute=(attributes.STR,))


class WarShirt(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOR, ac=11)


class Linothorax(Equippable):
    def __init__(self):
        super().__init__(equipment_type=EquipmentType.ARMOR, ac=13)


class WarRobe(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOR, ac=14)


class MailHauberk(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOR, ac=16)


class SmallShield(Equippable):
    def __init__(self):
        super().__init__(equipment_type=EquipmentType.SHIELD, ac=13)


class LargeShield(Equippable):
    def __init__(self):
        super().__init__(equipment_type=EquipmentType.SHIELD, ac=14)
