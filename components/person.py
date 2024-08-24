from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Dict, TYPE_CHECKING

from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor, Item


@dataclass(frozen=True)
class PersonType:
    article: str
    noun: str


@dataclass(frozen=True)
class Motivation:
    summary: str


WANT_TO_SURVIVE = Motivation("survive")


class Need:
    def __init__(self, properties: Dict[str, Any], summary_format: str):
        self.properties = properties
        self.summary_format = summary_format

    @property
    def summary(self):
        return self.summary_format.format_map(self.properties)


NEED_NOTHING = Need({}, "nothing")


class Person(BaseComponent):
    parent: Actor

    def __init__(self, background: PersonType, motivation: Motivation = WANT_TO_SURVIVE, need: Need = NEED_NOTHING):
        self.background = background
        self.motivation = motivation
        self.need = need

    def say(self, message: str) -> None:
        self.engine.message_log.add_message(
            f"{self.background.article.capitalize()} {self.background.noun} says: {message}.")

    def __str__(self):
        summary = f"{self.background.article} {self.background.noun}"
        if self.motivation is not WANT_TO_SURVIVE:
            summary += f" (needs {self.need.summary} to {self.motivation.summary})"
        return summary
