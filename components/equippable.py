from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import BaseComponent
from equipment_types import EquipmentType

if TYPE_CHECKING:
    from entity import Item


class Equippable(BaseComponent):
    parent: Item

    def __init__(
            self,
            equipment_type: EquipmentType,
            damage: tuple[int, int, int] = (1, 2, 0),
            ac: int = 0,
    ):
        self.equipment_type = equipment_type
        self.damage = damage
        self.ac = ac


class Dagger(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON, damage=(1, 4, 0))


class ShortSword(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON, damage=(1, 6, 0))


class LongSword(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON, damage=(1, 8, 0))


class WarShirt(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOR, ac=11)


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
