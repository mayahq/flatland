import random
from collections import namedtuple


LineParams = namedtuple("LineParams", ["c1", "c2"])


def generate(N, xmin=-128, xmax=128, ymin=-128, ymax=128):
    return {
        "items": [
            LineParams(
                (random.randint(xmin, xmax), random.randint(ymin, ymax)),
                (random.randint(xmin, xmax), random.randint(ymin, ymax)),
            )
            for i in range(N)
        ]
    }
