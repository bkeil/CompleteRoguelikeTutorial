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


@dataclass(frozen=True)
class NeedFactory:
    recipe: tuple
    summary_format: str

    def create(self, gen: random.Random) -> Need:
        return Need({}, self.summary_format)


class Need:
    def __init__(self, properties: Dict[str, Any], summary_format: str):
        self.properties = properties
        self.summary_format = summary_format

    @property
    def summary(self):
        return self.summary_format.format_map(self.properties)


class Person(BaseComponent):
    parent: Actor

    def __init__(self, type: PersonType, motivation: Motivation, need: Need):
        self.type = type
        self.motivation = motivation
        self.need = need

    def say(self, message: str) -> None:
        self.engine.message_log.add_message(f"{self.type.article.capitalize()} {self.type.noun} says {message}.")
