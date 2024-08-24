import random
from typing import Any

import worldgen.seed
from worldgen import motivations, needs
from components.person import Person, PersonType

_TYPES = [
    PersonType('a', 'bureaucrat'),
    PersonType('a', 'courier'),
    PersonType('a', 'criminal'),
    PersonType('a', 'day worker'),
    PersonType('a', 'dilettante'),
    PersonType('a', 'farmhand'),
    PersonType('a', 'healer'),
    PersonType('a', 'hunter'),
    PersonType('a', 'knight'),
    PersonType('a', 'mercenary'),
    PersonType('a', 'merchant'),
    PersonType('a', 'nomad'),
    PersonType('a', 'peasant'),
    PersonType('a', 'petty noble'),
    PersonType('a', 'physician'),
    PersonType('a', 'priest'),
    PersonType('a', 'sailor'),
    PersonType('a', 'scholar'),
    PersonType('a', 'sea captain'),
    PersonType('a', 'slave'),
    PersonType('a', 'soldier'),
    PersonType('a', 'strongman'),
    PersonType('a', 'thug'),
    PersonType('a', 'travelling merchant'),
    PersonType('a', 'wanderer'),
    PersonType('an', 'artisan'),
    PersonType('an', 'entertainer'),
]


def source(gen: random.Random, spec: tuple) -> Any:
    if spec[0] == "person":
        if spec[1] == "headliner":
            return new_headliner(gen)
        elif spec[1] == "extra":
            return new_extra(gen)
    raise NotImplementedError()


def new_headliner(gen: random.Random) -> Person:
    person_gen = worldgen.seed.new_generator(gen)
    return Person(background=person_gen.choice(_TYPES),
                  motivation=person_gen.choice(motivations.MOTIVATIONS),
                  need=person_gen.choice(needs.NEEDS).create(person_gen, source),
                  )


def new_extra(gen: random.Random) -> Person:
    person_gen = worldgen.seed.new_generator(gen)
    return Person(background=person_gen.choice(_TYPES))
