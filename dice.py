import random


def roll(num_dice: int, num_sides: int, advantage: int = 0) -> int:
    if advantage == 0:
        total = 0
        for die in range(num_dice):
            total += random.randint(1, num_sides)
        return total

    rolls = sorted([random.randint(1, num_sides) for _ in range(num_dice + abs(advantage))])
    if advantage > 0:
        return sum(rolls[advantage:])
    else:
        return sum(rolls[:(-advantage)])
