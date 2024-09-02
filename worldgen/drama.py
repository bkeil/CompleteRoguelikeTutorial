from __future__ import annotations

import random
from typing import Any, Dict

import components.person
import worldgen.motivations
import worldgen.people
import worldgen.seed


class Drama:
    def __init__(self, seed: int):
        self.seed = seed
        self.gen = random.Random(seed)
        self.people_gen = worldgen.seed.new_generator(self.gen)
        self.props: Dict[str, Any] = {}

    def generate(self):
        # Every drama starts with a Person who has a Need.  They will present their need to the player.
        self.props["main_role"] = main_role = {}

        # This person will have a particular background and motivation.
        main_role["background"] = worldgen.people.new_type(self.people_gen)
        main_role["motivation"] = self.people_gen.choice(worldgen.motivations.MOTIVATIONS)

        # For now, let's assume that they have some enemy that they need the player to kill.
        # For simplicity, let's even assume that it's an orc on the fifth floor.
        self.props["antagonist"] = antagonist = {}
        antagonist["location"] = {"floor": 5}
        antagonist["race"] = {"article": "an", "noun": "orc"}

        main_role["need"] = components.person.Need(properties=antagonist,
                                                   summary_format="someone to kill {race[article]} {race[noun]} on "
                                                                  "floor {location[floor]} of this dungeon")
