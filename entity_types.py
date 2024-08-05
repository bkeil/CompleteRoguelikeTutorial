from __future__ import annotations

import copy
import dataclasses
from typing import Sequence, Type, TYPE_CHECKING

import attributes
import color
import dice
from components.ai import HostileEnemy
from components import consumable, equippable
from components.equipment import Equipment
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level, Monster, Warrior
from entity import Actor, Item

if TYPE_CHECKING:
    from components.level import ActorClass
    from components.ai import BaseAI
    from game_map import GameMap


class Spawner[T]:
    def spawn(self, dungeon: GameMap, x: int, y: int):
        raise NotImplementedError()


player = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=30, stats=attributes.roll(), base_ac=10),
    inventory=Inventory(capacity=26),
    level=Level(actor_class=Warrior(), level_up_base=200)
)

_POTION = "!"
_SCROLL = chr(9852)  # "?"

confusion_scroll = Item(
    char=_SCROLL,
    color=(207, 63, 255),
    name="Confusion Scroll",
    consumable=consumable.ConfusionConsumable(number_of_turns=10),
)
fireball_scroll = Item(
    char=_SCROLL,
    color=(255, 0, 0),
    name="Fireball Scroll",
    consumable=consumable.FireballDamageConsumable(damage=12, radius=3),
)
health_potion = Item(
    char=_POTION,
    color=(255, 0, 192),
    name="Health Potion",
    consumable=consumable.HealingConsumable(amount=4),
)
lightning_scroll = Item(
    char=_SCROLL,
    color=(255, 223, 32),
    name="Lightning Scroll",
    consumable=consumable.LightningDamageConsumable(damage=20, maximum_range=5),
)

dagger = Item(
    char="|", color=(0, 191, 255), name="Dagger", equippable=equippable.Dagger()
)

short_sword = Item(char="|", color=color.steel, name="Short Sword", equippable=equippable.ShortSword())

long_sword = Item(char="|", color=color.steel, name="Long Sword", equippable=equippable.LongSword())

war_axe = Item(char="/", color=(0x7E, 0x71, 0x71), name="War Axe", equippable=equippable.WarAxe())

war_shirt = Item(
    char="(",
    color=(148, 179, 89),
    name="War Shirt",
    equippable=equippable.WarShirt(),
)
padded_armor = Item(
    char="(",
    color=(128, 64, 255),
    name="Padded Armor",
    equippable=equippable.Linothorax(),
)
leather_armor = Item(
    char="[",
    color=color.leather,
    name="Leather Armor",
    equippable=equippable.WarRobe(),
)

chain_mail = Item(
    char="[", color=color.steel, name="Chain Mail", equippable=equippable.MailHauberk(),
)

small_shield = Item(
    char=")",
    color=color.steel,
    name="Small Metal Shield",
    equippable=equippable.SmallShield(),
)

large_shield = Item(
    char="]",
    color=color.birch1,
    name="Large Wooden Shield",
    equippable=equippable.LargeShield(),
)


@dataclasses.dataclass(frozen=True)
class MobSpawner(Spawner):
    char: str
    color: tuple[int, int, int]
    name: str
    hit_dice: int
    equipment: Sequence[Item] = ()
    ai_cls: Type[BaseAI] = HostileEnemy
    base_ac: int = 10
    base_attack_bonus: int = 0
    base_damage_bonus: int = 0
    base_damage: tuple[int, int, int] = (1, 2, 0)
    skills: tuple[tuple[str, int], ...] = ()

    def spawn(self, dungeon: GameMap, x: int, y: int):
        hp = dice.roll(self.hit_dice, 8)
        mob = Actor(char=self.char, color=self.color, name=self.name, ai_cls=self.ai_cls, equipment=Equipment(),
                    fighter=Fighter(hp=hp,
                                    stats=attributes.typical(),
                                    base_ac=self.base_ac,
                                    base_damage_bonus=self.base_damage_bonus,
                                    ),
                    inventory=Inventory(capacity=len(self.equipment)),
                    level=Level(actor_class=Monster(base_attack_bonus=self.base_attack_bonus),
                                current_level=self.hit_dice, xp_given=self.hit_dice * 35))
        for item in self.equipment:
            gear = copy.deepcopy(item)
            gear.parent = mob.inventory
            mob.inventory.items.append(gear)
            mob.equipment.toggle_equip(gear, add_message=False)
        mob.x, mob.y = x, y
        mob.parent = dungeon
        dungeon.entities.add(mob)
        return mob


goblin = MobSpawner(
    char="g",
    color=(125, 159, 95),
    name="Goblin",
    equipment=(short_sword, padded_armor),
    hit_dice=1,
    base_attack_bonus=1,
    base_damage_bonus=1,
    skills=(("stab", 0),)
)
orc = MobSpawner(
    char="o",
    color=(63, 127, 63),
    name="Orc",
    equipment=(leather_armor, war_axe),
    hit_dice=2,
    base_attack_bonus=4,
    base_damage_bonus=1,
    skills=(("stab", 0),)
)
bugbear = MobSpawner(
    char="G",
    color=(63, 127, 0),
    name="Bugbear",
    equipment=(leather_armor,),
    hit_dice=3,
    base_attack_bonus=5,
    base_damage=(1, 10, 3),
)
