from __future__ import annotations

from dataclasses import dataclass
from typing import List, TYPE_CHECKING

from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor, Item


@dataclass(frozen=True)
class PersonType:
    article: str
    noun: str


class Person(BaseComponent):
    parent: Actor

    def __init__(self, type: PersonType):
        self.type = type

    def say(self, message: str) -> None:
        self.engine.message_log.add_message(f"{self.type.article.capitalize()} {self.type.noun} says {message}.")
