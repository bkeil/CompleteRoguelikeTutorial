from typing import Optional, Tuple

import numpy as np  # type: ignore

import color

# Tile graphics structure type compatible with Console.tiles_rbg.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),
        ("fg", "3B"),
        ("bg", "3B"),
    ]
)

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
    [
        ("walkable", np.bool),
        ("transparent", np.bool),
        ("dark", graphic_dt),
        ("light", graphic_dt),
        ("oov", graphic_dt),
    ]
)


def new_tile(
        *,
        walkable: int,
        transparent: int,
        dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
        light: Optional[Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]] = None,
        oov: Optional[Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]] = None,
) -> np.ndarray:
    """Helper function for defining individual tile types."""
    if not light:
        light = (dark[0], color.lit(dark[1]), color.lit(dark[2]))
    if not oov:
        oov = (dark[0], color.invisible(dark[1]), color.invisible(dark[2]))
    return np.array((walkable, transparent, dark, light, oov), dtype=tile_dt)


# SHROUD represents unexplored, unseen tiles
SHROUD = np.array((ord(" "), (255, 255, 255), (32, 32, 0)), dtype=graphic_dt)

floor = new_tile(
    walkable=True, transparent=True,
    dark=(ord("."), (75, 75, 82), (65, 65, 70)))
floor_oov_bg: Tuple[int, int, int] = tuple(floor["oov"]["bg"])

water = new_tile(
    walkable=True, transparent=True,
    dark=(8776, (65, 65, 130), (32, 32, 65)))
beach = new_tile(
    walkable=True, transparent=True,
    dark=(ord("~"), (160, 160, 190), (190, 190, 65))
)
grassland = new_tile(
    walkable=True, transparent=True,
    dark=(ord(","), (48, 130, 48), (24, 95, 24))
)
forest = new_tile(
    walkable=True, transparent=False,
    dark=(9827, (65, 130, 65), (16, 65, 16)))
desert = new_tile(
    walkable=True, transparent=True,
    dark=(ord("~"), (180, 160, 80), (200, 180, 100))
)

wall = new_tile(
    walkable=False, transparent=False,
    dark=(ord("#"), (80, 80, 100), (100, 80, 80)))

down_stairs = new_tile(
    walkable=True, transparent=True,
    dark=(ord(">"), (75, 225, 75), (65, 65, 70)),
    oov=(ord(">"), (75, 225, 75), floor_oov_bg))
