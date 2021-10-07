import random
from collections import namedtuple


LineParams = namedtuple("LineParams", ["c1", "c2"])

def get_lines(N, xmin=-128, xmax=128, ymin=-128, ymax=128):
    return [
        LineParams(
            (random.randint(xmin, xmax), random.randint(ymin, ymax)),
            (random.randint(xmin, xmax), random.randint(ymin, ymax)),
        )
        for i in range(N)
    ]
