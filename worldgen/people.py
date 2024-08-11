import random
from components.person import Person, PersonType

_TYPES = [
    PersonType('an', 'artisan'),
    PersonType('a', 'travelling merchant'),
    PersonType('a', 'courier'),
    PersonType('an', 'entertainer'),
    PersonType('a', 'criminal'),
    PersonType('a', 'hunter'),
    PersonType('a', 'farmhand'),
    PersonType('a', 'day worker'),
    PersonType('a', 'peasant'),
    PersonType('a', 'merchant'),
    PersonType('a', 'petty noble'),
    PersonType('a', 'nomad'),
    PersonType('a', 'physician'),
    PersonType('a', 'healer'),
    PersonType('a', 'priest'),
    PersonType('a', 'sailor'),
    PersonType('a', 'sea captain'),
    PersonType('a', 'scholar'),
    PersonType('a', 'slave'),
    PersonType('a', 'soldier'),
    PersonType('a', 'mercenary'),
    PersonType('a', 'knight'),
    PersonType('a', 'scholar'),
    PersonType('a', 'thug'),
    PersonType('a', 'strongman'),
    PersonType('a', 'wanderer')
]


def new_person(gen: random.Random) -> Person:
    return Person(type=gen.choice(_TYPES))

