import attributes
import color
from components.ai import HostileEnemy
from components import consumable, equippable
from components.equipment import Equipment
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from entity import Actor, Item

player = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=30, stats=attributes.roll(), base_ac=10),
    inventory=Inventory(capacity=26),
    level=Level(level_up_base=200)
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

short_sword = Item(char="/", color=color.steel, name="Short Sword", equippable=equippable.ShortSword())

long_sword = Item(char=chr(9876), color=color.steel, name="Long Sword", equippable=equippable.LongSword())

war_shirt = Item(
    char="(",
    color=(148, 179, 89),
    name="War Shirt",
    equippable=equippable.WarShirt(),
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

goblin = Actor(
    char="g",
    color=(95, 159, 95),
    name="Goblin",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=5, stats=attributes.typical(), base_ac=13, base_damage=(1, 6, 1)),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=35),
)
orc = Actor(
    char="o",
    color=(63, 127, 63),
    name="Orc",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=9, stats=attributes.typical(), base_ac=14, base_damage=(1, 10, 1)),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=100),
)
troll = Actor(
    char="T",
    color=(63, 127, 0),
    name="Troll",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=14, stats=attributes.typical(), base_ac=14, base_damage=(1, 10, 1)),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=200),
)
