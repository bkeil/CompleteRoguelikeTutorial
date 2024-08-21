import random


def rand_seed(gen: random.Random):
    """Returns a new random seed."""
    return gen.randint(0, 4294967295)


def new_generator(gen: random.Random):
    """Returns a new generator based on rand_seed(gen)"""
    return random.Random(rand_seed(gen))