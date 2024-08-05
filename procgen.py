from __future__ import annotations

import random
from typing import Any, Dict, Iterator, List, Optional, Tuple, TYPE_CHECKING

import tcod
from numpy import dtype, floating, ndarray

from entity import Actor
import entity_types
from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

max_items_by_floor = [
    (1, 1),
    (4, 2),
]

item_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_types.health_potion, 35), (entity_types.leather_armor, 15)],
    2: [(entity_types.confusion_scroll, 10)],
    4: [(entity_types.lightning_scroll, 25), (entity_types.short_sword, 5)],
    6: [(entity_types.fireball_scroll, 25), (entity_types.chain_mail, 15)],
    7: [(entity_types.long_sword, 35), (entity_types.health_potion, 70)],
}

max_monsters_by_floor = [
    (1, 2),
    (4, 3),
    (6, 5),
]

enemy_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_types.goblin, 80)],
    3: [(entity_types.orc, 15)],
    5: [(entity_types.orc, 30)],
    7: [(entity_types.bugbear, 60)],
}


def get_max_value_for_floor(
        max_value_by_floor: List[Tuple[int, int]], floor: int
) -> int:
    current_value = 0

    for floor_minimum, value in max_value_by_floor:
        if floor_minimum > floor:
            break
        else:
            current_value = value

    return current_value


def get_entities_at_random(
        weighted_chances_by_floor: Dict[int, List[Tuple[Entity, int]]],
        number_of_entities: int,
        floor: int,
        gen: random.Random,
) -> List[Entity]:
    entity_weighted_chances = {}

    for key, values in weighted_chances_by_floor.items():
        if key > floor:
            break
        else:
            for entity, weight in values:
                entity_weighted_chances[entity] = weight

    entities = list(entity_weighted_chances.keys())
    entity_weighted_chance_values = list(entity_weighted_chances.values())

    chosen_entities = gen.choices(
        entities, weights=entity_weighted_chance_values, k=number_of_entities
    )

    return chosen_entities


class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.x2 = x + width
        self.y1 = y
        self.y2 = y + height

    @property
    def center(self) -> Tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index."""
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: RectangularRoom) -> bool:
        """Return True just in case this room overlaps with another RectangularRoom."""
        return (
                self.x1 <= other.x2
                and self.x2 >= other.x1
                and self.y1 <= other.y2
                and self.y2 >= other.y1
        )


def tunnel_between(
        gen: random.Random,
        start: Tuple[int, int], end: Tuple[int, int]
) -> Iterator[Tuple[int, int]]:
    """Return an L-shaped tunner between `start` and `end`."""
    x1, y1 = start
    x2, y2 = end
    if gen.random() < 0.5:  # 50% chance.
        # Move horizontally, then vertically.
        corner_x, corner_y = x2, y1
    else:
        # Move vertically, then horizontally.
        corner_x, corner_y = x1, y2

    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y


def place_entities(room: RectangularRoom, dungeon: GameMap, floor_number: int,
                   gen: random.Random) -> None:
    entity_gen = random.Random(_next_seed(gen))
    number_of_monsters = entity_gen.randint(
        0, get_max_value_for_floor(max_monsters_by_floor, floor_number)
    )
    number_of_items = entity_gen.randint(
        0, get_max_value_for_floor(max_items_by_floor, floor_number)
    )

    items: List[Entity] = get_entities_at_random(
        item_chances, number_of_items, floor_number, entity_gen
    )
    monsters: List[Entity] = get_entities_at_random(
        enemy_chances, number_of_monsters, floor_number, entity_gen
    )

    for entity_type in monsters + items:
        x = entity_gen.randint(room.x1 + 1, room.x2 - 1)
        y = entity_gen.randint(room.y1 + 1, room.y2 - 1)
        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            entity = entity_type.spawn(dungeon, x, y)


def _next_seed(gen: random.Random) -> int:
    return gen.randint(0, 4294967295)


def make_room(dungeon: GameMap, node: tcod.bsp.BSP, node_rooms: Dict[tcod.bsp.BSP, RectangularRoom],
              current_floor: int,
              gen: random.Random) -> None:
    room_gen = random.Random(_next_seed(gen))

    # print('Dig a room for %s.' % node)
    room_width = room_gen.randint(node.width // 2, node.width - 2)
    room_height = room_gen.randint(node.height // 2, node.height - 2)

    x = node.x + (node.width - room_width) // 2
    y = node.y + (node.height - room_height) // 2

    # "RectangularRoom" class makes rectangles easier to work with
    new_room = RectangularRoom(x, y, room_width, room_height)
    # Run through the other rooms and see if they intersect with this one.
    if any(new_room.intersects(other_room) for other_room in node_rooms.values()):
        return  # This room intersects, so go to the next attempt.
    # If there are no intersections then the room is valid.

    # Dig out this room's inner area.
    dungeon.tiles[new_room.inner] = tile_types.floor

    place_entities(new_room, dungeon, current_floor, room_gen)

    node_rooms[node] = new_room


def terrain(e: floating) -> ndarray:
    if e < 0.225:
        return tile_types.water
    elif e < 0.35:
        return tile_types.beach
    elif e < 0.5:
        return tile_types.grassland
    elif e < 0.65:
        return tile_types.forest
    elif e < 0.85:
        return tile_types.desert
    elif e < 0.93:
        return tile_types.floor
    else:
        return tile_types.down_stairs


def connect_nodes(dungeon: GameMap, nodes: Tuple[tcod.bsp.BSP, tcod.bsp.BSP],
                  node_rooms: Dict[tcod.bsp.BSP, RectangularRoom],
                  gen: random.Random) -> None:
    # print('Connect the nodes:\n%s\n%s' % nodes)
    centers = (node_rooms[child].center for child in nodes)
    for x, y in tunnel_between(gen, *centers):
        dungeon.tiles[x, y] = tile_types.floor


def generate_dungeon(
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        map_width: int,
        map_height: int,
        engine: Engine,
        seed: int,
) -> GameMap:
    """Generate a new dungeon map."""
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    bsp = tcod.bsp.BSP(x=0, y=0, width=dungeon.width, height=dungeon.height)
    bsp.split_recursive(
        depth=4,
        min_width=8,
        min_height=8,
        max_horizontal_ratio=2,
        max_vertical_ratio=2,
        seed=tcod.random.Random(seed=seed).random_c,
    )

    gen = random.Random(seed)

    node_rooms = {}
    for node in bsp.inverted_level_order():
        if node.children:
            connect_nodes(dungeon, node.children, node_rooms, gen)
            node_rooms[node] = node_rooms[node.children[0]]
        else:
            make_room(dungeon, node, node_rooms, engine.game_world.current_floor, gen)

    # Add some extra tunnels to have a chance at making some shortcuts.
    nodes = list(node_rooms.keys())
    gen.shuffle(nodes)
    i = min(8, len(nodes) - 2)
    while i >= 0:
        connect_nodes(dungeon, (nodes[i], nodes[i + 1]), node_rooms, gen)
        i -= 2

    rooms = list(node_rooms.values())
    gen.shuffle(rooms)
    player.place(*rooms[0].center, dungeon)
    dungeon.tiles[rooms[-1].center] = tile_types.down_stairs

    return dungeon


def generate_overland(
        map_width: int,
        map_height: int,
        engine: Engine,
        offset: tuple[int, int],
        scale: float,
) -> GameMap:
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    gen = random.Random(engine.game_world.seed)

    noise = tcod.noise.Noise(
        dimensions=2,
        algorithm=tcod.noise.Algorithm.SIMPLEX,
        # implementation=tcod.noise.Implementation.TURBULENCE,
        seed=gen.randint(0, 4294967295),
    )
    samples = (noise[tcod.noise.grid(shape=(map_height, map_width), scale=scale, origin=offset)] + 1.0) * 0.5

    for y in range(map_height):
        for x in range(map_width):
            dungeon.tiles[x, y] = terrain(samples[x, y])

    px = gen.randint(1, map_width - 2)
    py = gen.randint(1, map_height - 2)
    player.place(px, py, dungeon)

    return dungeon
