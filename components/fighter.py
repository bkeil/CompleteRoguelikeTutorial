from __future__ import annotations

from typing import Callable, Dict, List, Optional, TYPE_CHECKING

import components.equippable
from attributes import Stat, STR, DEX, best_modifier, modifier
import color
from components.base_component import BaseComponent
from components.equippable import Equippable, EquipmentType
from render_order import RenderOrder

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity
    import abilities

UNARMED = Equippable(equipment_type=EquipmentType.WEAPON)


class Fighter(BaseComponent):
    parent: Actor

    def __init__(self, hp: int,
                 stats: Dict[Stat, int],
                 base_ac: int = 10,
                 base_damage: tuple[int, int, int] = (1, 2, 0),
                 base_damage_bonus: int = 0,
                 skills: tuple[tuple[str, int], ...] = (),
                 on_die: Callable[[Engine, Entity], None] | None = None,
                 ):
        self.max_hp = hp
        self._hp = hp
        self.stats = stats
        self.base_ac = base_ac
        self.base_damage = base_damage
        self.base_damage_bonus = base_damage_bonus
        self.skills: Dict[str, int] = {}
        self.on_die = on_die
        for skill, level in skills:
            self.skills[skill] = level
        self.abilities: List[abilities.Ability] = []

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.parent.ai:
            self.die()

    @property
    def ac(self) -> int:
        eq = self.parent.equipment
        ac = self.base_ac
        if eq.armor is not None:
            ac = max(ac, eq.armor.equippable.ac)
        if eq.shield is not None:
            if eq.shield.equippable.ac > ac:
                ac = eq.shield.equippable.ac
            else:
                ac += 1

        return ac + self.ac_bonus

    @property
    def weapon(self) -> components.equippable.Equippable:
        if self.parent.equipment.weapon is not None and self.parent.equipment.weapon.equippable is not None:
            return self.parent.equipment.weapon.equippable
        return UNARMED

    @property
    def shield(self) -> Optional[components.equippable.Equippable]:
        if self.parent.equipment.shield is not None:
            return self.parent.equipment.shield.equippable
        return None

    @property
    def weapon_modifier(self) -> int:
        return best_modifier(map(lambda att: self.stats[att], self.weapon.attribute))

    @property
    def hit_roll_modifier(self) -> int:
        mod = self.parent.level.actor_class.base_attack_bonus(self.parent)
        if "stab" in self.skills:
            mod += self.skills["stab"]
        mod += self.weapon_modifier
        return mod

    @property
    def max_shock_ac(self) -> int:
        return self.weapon.shock.max_ac

    @property
    def damage(self) -> tuple[int, int, int]:
        s, d, b = self.base_damage
        if self.parent.equipment.weapon is not None:
            s, d, b = self.parent.equipment.weapon.equippable.damage
        return s, d, b + self.damage_bonus

    @property
    def shock_damage(self) -> int:
        return self.weapon.shock.damage + self.damage_bonus

    @property
    def ac_bonus(self) -> int:
        return modifier(self.stats[DEX])

    @property
    def damage_bonus(self) -> int:
        mod = self.base_damage_bonus + self.weapon_modifier
        for ability in self.abilities:
            mod += ability.damage_bonus(self.parent)
        return mod

    def heal(self, amount: int) -> int:
        if self.hp == self.max_hp:
            return 0

        old_hp = self.hp
        self.hp += amount
        amount_recovered = self.hp - old_hp

        return amount_recovered

    def take_damage(self, amount: int) -> None:
        self.hp -= amount

    def die(self) -> None:
        if self.on_die:
            self.on_die(self.engine, self.parent)

        if self.engine.player is self.parent:
            death_message = "You died!"
            death_message_color = color.player_die
        else:
            death_message = f"{self.parent.name} is dead!"
            death_message_color = color.enemy_die
            self.engine.player.level.add_xp(self.parent.level.xp_given)
            for i in reversed(range(len(self.parent.inventory.items))):
                item = self.parent.inventory.items[i]
                if self.parent.equipment.item_is_equipped(item):
                    self.parent.equipment.toggle_equip(item, add_message=False)
                self.parent.inventory.drop(item)

        self.parent.char = '%'
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f"remains of {self.parent.name}"
        self.parent.render_order = RenderOrder.CORPSE

        self.engine.message_log.add_message(death_message, death_message_color)
