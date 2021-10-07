import random
from collections import namedtuple


CircleParams = namedtuple("CircleParams", ["x", "y", "r"])

def generate(N, xmin=-96, xmax=96, ymin=-96, ymax=96, rmin=3, rmax=50):
    return [
        CircleParams(
            random.randint(xmin, xmax),
            random.randint(ymin, ymax),
            random.randint(rmin, rmax),
        )
        for i in range(N)
    ]
