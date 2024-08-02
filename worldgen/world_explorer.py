import copy
import exceptions
import traceback
from typing import Optional

import tcod

from actions import Action
import color
from engine import Engine
import entity_types
from game_map import GameWorld
import input_handlers
from input_handlers import MainGameEventHandler


def explore_world() -> MainGameEventHandler:
    """Return a brand new game session as an Engine instance."""
    map_width = 80
    map_height = 43

    player = copy.deepcopy(entity_types.player)
    player.clairvoyant = True

    engine = Engine(player=player)
    engine.game_world = GameWorld(
        max_rooms=1,
        room_min_size=3,
        room_max_size=3,
        map_width=map_width,
        map_height=map_height,
        engine=engine,
    )

    engine.game_world.generate_overland()
    engine.update_fov()

    engine.message_log.add_message(
        "Let's explore!", color.welcome_text
    )
    return MainGameEventHandler(engine)


def handle_exploration(engine: Engine, ) -> None:
    px = engine.player.x
    py = engine.player.y
    dox, doy = 0, 0
    move = False
    if px == 0:
        dox = -5 * engine.game_world.scale
        px = 5
        move = True
    elif px == engine.game_map.width - 1:
        dox = 5 * engine.game_world.scale
        px -= 5
        move = True

    if py == 0:
        doy = -5 * engine.game_world.scale
        py = 5
        move = True
    elif py == engine.game_map.height - 1:
        doy = 5 * engine.game_world.scale
        py -= 5
        move = True

    if move:
        oy, ox = engine.game_world.offset
        ox += dox
        oy += doy
        engine.game_world.offset = (oy, ox)
        engine.game_world.generate_overland()
        engine.update_fov()
        engine.player.x = px
        engine.player.y = py


if __name__ == "__main__":
    screen_width = 80
    screen_height = 50

    tile_set = tcod.tileset.load_bdf("../data/14x14.bdf")

    world_explorer = explore_world()
    handler: input_handlers.BaseEventHandler = world_explorer
    engine = world_explorer.engine

    with tcod.context.new_terminal(
            screen_width,
            screen_height,
            tileset=tile_set,
            title="Hard Times"
    ) as context:
        root_console = tcod.console.Console(screen_width, screen_height, order="F")
        try:
            while True:
                root_console.clear()
                handler.on_render(console=root_console)
                oy, ox = engine.game_world.offset
                px, py = engine.player.x, engine.player.y
                ax = ox + engine.game_world.scale * px
                ay = oy + engine.game_world.scale * py
                root_console.print(x=0, y=44, string=f"({ax}, {ay})")
                context.present(root_console)

                try:
                    for event in tcod.event.wait():
                        handler = handler.handle_event(context.convert_event(event))
                    handle_exploration(engine)
                except Exception:  # Handle exceptions in game.
                    traceback.print_exc()  # Print error to stderr.
                    # Then print the error to the message log.
                    if isinstance(handler, input_handlers.EventHandler):
                        handler.engine.message_log.add_message(
                            traceback.format_exc(), color.error
                        )
        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit:  # Save and quit.
            raise
        except BaseException:  # Save on any other unexpected exception.
            raise
