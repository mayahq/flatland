import random


def GENERATE_ID():
    return "%08x" % (random.randrange(16 ** 8))
