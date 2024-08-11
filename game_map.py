from __future__ import annotations

from typing import Iterable, Iterator, Optional, TYPE_CHECKING

import numpy as np  # type: ignore
from tcod.console import Console

import color
from entity import Actor, Item
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class GameMap:
    def __init__(
            self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = ()
    ):
        self.engine = engine
        self.width, self.height = width, height
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")
        self.entities = set(entities)

        self.lit = np.full(
            (width, height), fill_value=False, order="F"
        )  # Tiles that are currently lit
        self.visible = np.full(
            (width, height), fill_value=False, order="F"
        )  # Tiles the player can currently see
        self.explored = np.full(
            (width, height), fill_value=False, order="F"
        )  # Tiles the player has seen before

    @property
    def game_map(self) -> GameMap:
        return self

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over this map's living actors."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))

    def get_blocking_entity_at_location(
            self, location_x: int, location_y: int,
    ) -> Optional[Entity]:
        for entity in self.entities:
            if (
                    entity.blocks_movement
                    and entity.x == location_x
                    and entity.y == location_y
            ):
                return entity

        return None

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

        return None

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        console.rgb[0: self.width, 0: self.height] = np.select(

            condlist=[self.lit, self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"], self.tiles["oov"]],
            default=tile_types.SHROUD,
        )

        entities_sorted_for_rendering = sorted(
            self.entities, key=lambda x: x.render_order.value
        )

        for entity in entities_sorted_for_rendering:
            # Only print entities in the field of view.
            x, y = entity.x, entity.y
            if self.visible[x, y]:
                fg = entity.color if not self.lit[x, y] else color.lit(entity.color)
                console.print(x=x, y=y, string=entity.char, fg=fg)


class GameWorld:
    """
    Holds the settings for the GameMap, and generates new maps when moving down the stairs.
    """
    offset = (1, 1)
    # scale = .03125
    scale = 1/pow(2,7)
    seed = 42

    def __init__(
            self,
            *,
            engine: Engine,
            map_width: int,
            map_height: int,
            max_rooms: int,
            room_min_size: int,
            room_max_size: int,
            current_floor: int = 0
    ):
        self.engine = engine

        self.map_width = map_width
        self.map_height = map_height

        self.max_rooms = max_rooms

        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

        self.current_floor = current_floor

    def generate_floor(self) -> None:
        from procgen import generate_dungeon

        pwx, pwy = self.engine.player_world_location
        seed = (
                self.engine.game_world.seed
                + self.current_floor * 83
                + int(pwx) * 89
                + int(pwy) * 97
        )

        self.engine.game_map = generate_dungeon(
            max_rooms=self.max_rooms,
            room_min_size=self.room_min_size,
            room_max_size=self.room_max_size,
            map_width=self.map_width,
            map_height=self.map_height,
            engine=self.engine,
            seed=seed,
        )

    def generate_overland(self) -> None:
        from procgen import generate_overland
        self.engine.game_map = generate_overland(
            map_width=self.map_width,
            map_height=self.map_height,
            engine=self.engine,
            offset=self.offset,
            scale=self.scale,
        )
