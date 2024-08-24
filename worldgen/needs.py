from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Any, Callable, Dict

import worldgen.seed
from components.person import Need


@dataclass(frozen=True)
class NeedFactory:
    recipe: tuple
    summary_format: str

    def create(self, gen: Random, source: Callable[[Random, Any], Any]) -> Need:
        need_gen = worldgen.seed.new_generator(gen)
        props: Dict[str, Any] = {}
        for slot in self.recipe:
            props[slot[0]] = source(need_gen, slot[1])
        return Need(props, self.summary_format)


NEEDS = [
    NeedFactory((), "a large sum of money"),
    NeedFactory((), "a piece of exotic workmanship"),
    NeedFactory((), "to be accompanied on a dangerous journey"),
    NeedFactory((), "to explore a dangerous location"),
    NeedFactory((), "to explore a remote location"),
    NeedFactory((("enemy", ("person", "headliner")),), "to get proof of someone's wrong doing"),
    NeedFactory((("person", ("person", "headliner")),), "to have a meeting arranged with {person}"),
    NeedFactory((), "to have a stolen object retrieved"),
    NeedFactory((("enemy", ("person", "headliner")),), "to have someone defend me from {enemy}"),
    NeedFactory((("enemy", ("person", "extra")),), "to have {enemy} kidnapped"),
    NeedFactory((("enemy", ("person", "extra")),), "to have {enemy} killed"),
    NeedFactory((("friend", ("person", "extra")),), "to have {friend} rescued from something"),
    NeedFactory((("person", ("person", "extra")),), "to have {person} stop doing something"),
    NeedFactory((), "to have something destroyed"),
    NeedFactory((("enemy", ("person", "extra")),), "to have something stolen from {enemy}"),
    NeedFactory((("friend", ("person", "extra")),), "to hire a travelling companion for {friend}"),
    NeedFactory((("rival", ("person", "headliner")),), "to intimidate {rival}"),
    NeedFactory((("friend", ("person", "extra")),), "to locate {friend}, who has gone missing"),
    NeedFactory((("enemy", ("person", "headliner")),), "to make someone leave"),
]
