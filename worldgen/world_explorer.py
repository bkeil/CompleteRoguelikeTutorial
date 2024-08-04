import copy
import exceptions
import traceback

import tcod

import color
from engine import Engine
import entity_types
from game_map import GameWorld
import input_handlers
from input_handlers import MainGameEventHandler


def explore_world() -> MainGameEventHandler:
    """Return a brand new game session as an Engine instance."""
    map_width = 132
    map_height = 73

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    player = copy.deepcopy(entity_types.player)
    player.clairvoyant = True
    player.fighter.base_damage = (20, 2, 20)
    player.fighter.base_ac = 40

    engine = Engine(player=player)
    engine.game_world = GameWorld(
        max_rooms=max_rooms,
        room_min_size=room_max_size,
        room_max_size=room_min_size,
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


if __name__ == "__main__":
    screen_width = 132
    screen_height = 80

    tile_set = tcod.tileset.load_bdf("../data/14x14.bdf")

    world_explorer = explore_world()
    handler: input_handlers.BaseEventHandler = world_explorer
    eng = world_explorer.engine

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
                oy, ox = eng.game_world.offset
                px, py = eng.player.x, eng.player.y
                ax = ox + eng.game_world.scale * px
                ay = oy + eng.game_world.scale * py
                root_console.print(x=0, y=44, string=f"({ax}, {ay})")
                context.present(root_console)

                try:
                    for event in tcod.event.wait():
                        handler = handler.handle_event(context.convert_event(event))
                    eng.handle_exploration()
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
