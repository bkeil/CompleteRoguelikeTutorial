from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

import color
import dice
import exceptions
import input_handlers
import tile_types

if TYPE_CHECKING:
    import components.ai
    from engine import Engine
    from entity import Actor, Entity, Item
    from game_map import GameMap


class Action:
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to."""
        return self.entity.parent.engine

    @property
    def game_map(self) -> GameMap:
        """Return the game map this action belongs to."""
        return self.entity.parent

    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.

        `engine` is the scope this object is being performed in.

        `entity is the object performing the action.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class PickupAction(Action):
    """Pickup an item and add it to the inventory, if there is room for it."""

    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self) -> None:
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items) >= inventory.capacity:
                    raise exceptions.Impossible("Your inventory is full.")

                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.items.append(item)

                self.engine.message_log.add_message(f"You picked up the {item.name}!")
                return

        raise exceptions.Impossible("There is nothing here to pick up.")


class ItemAction(Action):
    def __init__(
        self, entity: Actor, item: Item, target_xy: Optional[Tuple[int, int]] = None
    ):
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this action's destination."""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        """Invoke the items ability, this action will be given to provide context."""
        if self.item.consumable:
            self.item.consumable.activate(self)


class DropItemAction(ItemAction):
    def perform(self) -> None:
        if self.entity.equipment.item_is_equipped(self.item):
            self.entity.equipment.toggle_equip(self.item)
        self.entity.inventory.drop(self.item)


class EquipItemAction(Action):
    def __init__(self, entity: Actor, item: Item):
        super().__init__(entity)

        self.item = item

    def perform(self) -> None:
        self.entity.equipment.toggle_equip(self.item)


class WaitAction(Action):
    def perform(self) -> None:
        pass


class TakeStairsAction(Action):
    def __init__(self, entity: Actor, down: bool):
        super().__init__(entity)
        self.down = down

    def perform(self) -> None:
        """
        Take the stairs, if any exist at the entity's location.
        """
        tile = self.game_map.tiles[self.entity.x, self.entity.y]
        if self.down and tile == tile_types.down_stairs:
            self.engine.game_world.current_floor += 1
            message = "You descend the staircase."
        elif (not self.down) and tile == tile_types.up_stairs:
            self.engine.game_world.current_floor -= 1
            message = "You ascend the staircase."
        else:
            raise exceptions.Impossible("There are no stairs here.")

        if self.engine.game_world.current_floor == 0:
            self.engine.game_world.generate_overland()
        else:
            self.engine.game_world.generate_floor()

        self.engine.message_log.add_message(message, color.descend)


class ActionWithDirection(Action):
    def __init__(self, entity: Actor, dx: int, dy:int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Tuple[int, int]:
        """Returns this actions destination."""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Optional[Entity]:
        """Return the blocking entity at this actions destination.."""
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)

    @property
    def target_actor(self) -> Optional[Actor]:
        return self.game_map.get_actor_at_location(*self.dest_xy)


class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.target_actor:
            if self.target_actor.ai.is_quest_giver:
                self.target_actor.person.say(self.target_actor.ai.quest_message)
            else:
                MeleeAction(self.entity, self.dx, self.dy).perform()
        else:
            MovementAction(self.entity, self.dx, self.dy).perform()


class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.target_actor
        if not target:
            raise exceptions.Impossible("Nothing to attack.")

        hit_roll = dice.roll(1, 20) + self.entity.fighter.hit_roll_modifier

        shock_damage = 0
        damage = 0
        hit = True

        if hit_roll == 1 or (hit_roll < target.fighter.ac and hit_roll != 20):
            # Miss, but check for shock
            if target.fighter.ac < self.entity.fighter.max_shock_ac:
                attack_desc = f"{self.entity.name.capitalize()} scrapes {target.name}"
                shock_damage = self.entity.fighter.shock_damage
            else:
                attack_desc = f"{self.entity.name.capitalize()} misses {target.name}"
                hit = False
        else:
            attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"
            num_sides, num_dice, bonus = self.entity.fighter.damage
            damage = dice.roll(num_sides, num_dice) + bonus

        damage = max(shock_damage, damage)

        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk

        if hit and damage == 0:
            attack_desc = f"{attack_desc} but does no damage."
        elif damage > 0:
            attack_desc = f"{attack_desc} for {damage} hit points."

        self.engine.message_log.add_message(attack_desc, attack_color)
        target.fighter.take_damage(damage)


class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            # Destination is out of bounds.
            raise exceptions.Impossible("Let's not stray too far.")
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            # Destination tile is not walkable.
            raise exceptions.Impossible("That way is blocked.")
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            # Destination is blocked by an entity.
            raise exceptions.Impossible("That way is blocked.")

        self.entity.move(self.dx, self.dy)
        if self.entity is self.engine.player and self.engine.game_world.current_floor == 0:
            self.engine.handle_exploration()
