from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from components.base_component import BaseComponent
from equipment_types import EquipmentType

if TYPE_CHECKING:
    from entity import Actor, Item


class Equipment(BaseComponent):
    parent: Actor

    def __init__(self, weapon: Optional[Item] = None, armor: Optional[Item] = None, shield: Optional[Item] = None):
        self.weapon = weapon
        self.armor = armor
        self.shield = shield

    @property
    def ac(self) -> int:
        ac = 10

        if self.armor is not None and self.armor.equippable is not None:
            if self.armor.equippable.ac > ac:
                ac = self.armor.equippable.ac

        if self.shield is not None and self.shield.equippable is not None:
            if self.shield.equippable.ac > ac:
                ac = self.shield.equippable.ac
            else:
                ac += 1

        return ac

    @property
    def damage(self) -> tuple[int, int]:
        dmg = (1, 2)

        if self.weapon is not None and self.weapon.equippable is not None:
            dmg = self.weapon.equippable.damage

        return dmg

    def item_is_equipped(self, item: Item) -> bool:
        return self.weapon == item or self.armor == item or self.shield == item

    def unequip_message(self, item_name: str) -> None:
        self.parent.game_map.engine.message_log.add_message(
            f"You remove the {item_name}."
        )

    def equip_message(self, item_name: str) -> None:
        self.parent.game_map.engine.message_log.add_message(
            f"You equip the {item_name}."
        )

    def equip_to_slot(self, slot: str, item: Item, add_message: bool) -> None:
        current_item = getattr(self, slot)

        if current_item is not None:
            self.unequip_from_slot(slot, add_message)

        setattr(self, slot, item)

        if add_message:
            self.equip_message(item.name)

    def unequip_from_slot(self, slot: str, add_message: bool) -> None:
        current_item = getattr(self, slot)

        if add_message:
            self.unequip_message(current_item.name)

        setattr(self, slot, None)

    def toggle_equip(self, equippable_item: Item, add_message: bool = True) -> None:
        if (
            equippable_item.equippable
            and equippable_item.equippable.equipment_type == EquipmentType.WEAPON
        ):
            slot = "weapon"
        elif (
            equippable_item.equippable
            and equippable_item.equippable.equipment_type == EquipmentType.ARMOR
        ):
            slot = "armor"
        else:
            slot = "shield"

        if getattr(self, slot) == equippable_item:
            self.unequip_from_slot(slot, add_message)
        else:
            self.equip_to_slot(slot, equippable_item, add_message)