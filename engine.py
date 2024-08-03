from __future__ import annotations

import lzma
import math
import pickle
from typing import TYPE_CHECKING

from tcod.console import Console
from tcod.map import compute_fov

import exceptions
from message_log import MessageLog
import render_functions

if TYPE_CHECKING:
    from entity import Actor
    from game_map import GameMap, GameWorld


class Engine:
    game_map: GameMap
    game_world: GameWorld

    def __init__(self, player: Actor):
        self.message_log = MessageLog()
        self.mouse_location = (0, 0)
        self.player = player

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                try:
                    entity.ai.perform()
                except exceptions.Impossible:
                    pass  # Ignore impossible action exceptions from AI.

    @property
    def player_world_location(self) -> tuple[float, float]:
        oy, ox = self.game_world.offset
        py, px = self.player.y, self.player.x
        scale = self.game_world.scale
        return ox + px * scale, oy + py * scale

    def render(self, console: Console):
        self.game_map.render(console)
        self.message_log.render(console=console, x=21, y=45, width=40, height=5)
        render_functions.render_bar(
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20,
        )
        render_functions.render_dungeon_level(console=console, dungeon_level=self.game_world.current_floor,
                                              location=(0, 47))
        render_functions.render_names_at_mouse_location(console=console, x=21, y=44, engine=self)

    def update_fov(self) -> None:
        """Recompute the visible area based on the players point of view."""
        if self.player.clairvoyant:
            self.game_map.visible[:] = True
            self.game_map.lit[:] = False
        else:
            self.game_map.visible[:] = compute_fov(
                self.game_map.tiles["transparent"],
                (self.player.x, self.player.y),
                radius=12,
            )
            if self.game_world.current_floor > 0:
                self.game_map.lit[:] = compute_fov(
                    self.game_map.tiles["transparent"],
                    (self.player.x, self.player.y),
                    radius=2,
                )
            else:
                self.game_map.lit[:] = False

        self.game_map.explored |= self.game_map.visible

    def save_as(self, filename: str):
        """Save this Engine instance as a compressed file."""
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, "wb") as f:
            f.write(save_data)

    def handle_exploration(self) -> None:
        px = self.player.x
        py = self.player.y
        shift = 5
        dox, doy = 0, 0
        move = False
        isx = osx = slice(0, self.game_map.width)
        isy = osy = slice(0, self.game_map.height)

        if px == 0:
            dox = -shift * self.game_world.scale
            px = shift
            move = True
            osx = slice(shift, self.game_map.width)
            isx = slice(0, self.game_map.width - shift)
        elif px == self.game_map.width - 1:
            dox = shift * self.game_world.scale
            px -= shift
            move = True
            osx = slice(0, self.game_map.width - shift)
            isx = slice(shift, self.game_map.width)

        if py == 0:
            doy = -shift * self.game_world.scale
            py = shift
            move = True
            osy = slice(shift, self.game_map.height)
            isy = slice(0, self.game_map.height - shift)
        elif py == self.game_map.height - 1:
            doy = shift * self.game_world.scale
            py -= shift
            move = True
            osy = slice(0, self.game_map.height - shift)
            isy = slice(shift, self.game_map.height)

        if move:
            oy, ox = self.game_world.offset
            ox += dox
            oy += doy
            explored = self.game_map.explored[isx, isy]
            self.game_world.offset = (oy, ox)
            self.game_world.generate_overland()
            self.game_map.explored[osx, osy] = explored
            self.player.x = px
            self.player.y = py
            self.update_fov()
