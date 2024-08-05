from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entity import Actor


class Ability:
    def damage_bonus(self, actor: Actor) -> int:
        return 0


class KillingBlow(Ability):
    def damage_bonus(self, actor: Actor) -> int:
        return math.ceil(actor.level.current_level / 2)
