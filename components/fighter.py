from __future__ import annotations

from attributes import Stat, STR, DEX, modifier
import color
from components.base_component import BaseComponent
from render_order import RenderOrder

from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from entity import Actor


class Fighter(BaseComponent):
    parent: Actor

    def __init__(self, hp: int, stats: Dict[Stat, int], base_defense: int, base_power: int):
        self.max_hp = hp
        self._hp = hp
        self.stats = stats
        self.base_defense = base_defense
        self.base_power = base_power

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.parent.ai:
            self.die()

    @property
    def defense(self) -> int:
        return self.base_defense + self.defense_bonus

    @property
    def power(self) -> int:
        return self.base_power + self.power_bonus

    @property
    def defense_bonus(self) -> int:
        return modifier(self.stats[DEX]) + self.parent.equipment.defense_bonus

    @property
    def power_bonus(self) -> int:
        return modifier(self.stats[STR]) + self.parent.equipment.power_bonus

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
        if self.engine.player is self.parent:
            death_message = "You died!"
            death_message_color = color.player_die
        else:
            death_message = f"{self.parent.name} is dead!"
            death_message_color = color.enemy_die
            self.engine.player.level.add_xp(self.parent.level.xp_given)

        self.parent.char = '%'
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f"remains of {self.parent.name}"
        self.parent.render_order = RenderOrder.CORPSE

        self.engine.message_log.add_message(death_message, death_message_color)
