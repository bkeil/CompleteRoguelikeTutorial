"""Handle the loading and initialization of game sessions."""
from __future__ import annotations

import copy
import lzma
import pickle
import traceback
from typing import Optional

import tcod
from tcod import libtcodpy

import abilities
import attributes
import color
from engine import Engine
import entity_types
from game_map import GameWorld
import input_handlers


# Load the background image and remove the alpha channel.
background_image = tcod.image.load("data/menu_background.png")[:, :, :3]


def new_game(screen_width: int, screen_height: int, clairvoyant: bool) -> Engine:
    """Return a brand new game session as an Engine instance."""
    map_width = screen_width
    map_height = screen_height - 7

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    player = copy.deepcopy(entity_types.player)
    player.fighter.skills["stab"] = 1
    if player.fighter.stats[attributes.DEX] < 14:
        player.fighter.stats[attributes.DEX] = 14
    elif player.fighter.stats[attributes.STR] < 14:
        player.fighter.stats[attributes.STR] = 14
    elif player.fighter.stats[attributes.CON] < 14:
        player.fighter.stats[attributes.CON] = 14
    player.fighter.abilities.append(abilities.KillingBlow())
    player.clairvoyant = clairvoyant
    if clairvoyant:
        player.fighter.base_ac = 40
        player.fighter.base_damage_bonus = 12
        player.fighter.hp = 3000

    dagger = copy.deepcopy(entity_types.dagger)
    war_shirt = copy.deepcopy(entity_types.war_shirt)

    dagger.parent = player.inventory
    war_shirt.parent = player.inventory

    player.inventory.items.append(dagger)
    player.equipment.toggle_equip(dagger, add_message=False)

    player.inventory.items.append(war_shirt)
    player.equipment.toggle_equip(war_shirt, add_message=False)

    engine = Engine(player=player)

    engine.game_world = GameWorld(
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        engine=engine,
    )

    engine.game_world.generate_overland()
    engine.update_fov()

    engine.message_log.add_message(
        "Hello and welcome, adventurer!", color.welcome_text
    )
    return engine


def load_game(filename: str) -> Engine:
    """Load an Engine instance from a file."""
    with open(filename, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine


class MainMenu(input_handlers.BaseEventHandler):
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
    """Handle the main menu rendering and input."""

    def on_render(self, console: tcod.Console) -> None:
        """Render the main menu on a background image."""
        console.draw_semigraphics(background_image, 0, 0)

        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "HARD TIMES",
            fg=color.menu_title,
            alignment=libtcodpy.CENTER,
        )
        console.print(
            console.width // 2,
            console.height - 2,
            "By Der Heiligste",
            fg=color.menu_title,
            alignment=libtcodpy.CENTER,
        )

        menu_width = 24
        for i, text in enumerate(
            ["[N] Play a new game", "[C] Continue last game", "[Q] Quit"]
        ):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=color.menu_text,
                bg=color.black,
                alignment=libtcodpy.CENTER,
                bg_blend=libtcodpy.BKGND_ALPHA(64),
            )

    def ev_keydown(
        self, event: tcod.event.KeyDown
    ) -> Optional[input_handlers.BaseEventHandler]:
        if event.sym in (tcod.event.KeySym.q, tcod.event.KeySym.ESCAPE):
            raise SystemExit()
        elif event.sym == tcod.event.KeySym.c:
            try:
                return input_handlers.MainGameEventHandler(load_game("savegame.sav"))
            except FileNotFoundError:
                return input_handlers.PopupMessage(self, "No saved game to load.")
            except Exception as exc:
                traceback.print_exc()  # Print to stderr.
                return input_handlers.PopupMessage(self, f"Failed to load save:\n{exc}")
        elif event.sym == tcod.event.KeySym.n:
            clairvoyant = event.mod & tcod.event.KMOD_LSHIFT
            return input_handlers.MainGameEventHandler(new_game(self.screen_width, self.screen_height, clairvoyant))

        return None
