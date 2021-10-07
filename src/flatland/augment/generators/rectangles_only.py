import random
from collections import namedtuple



RectangleParams = namedtuple("RectangleParams", ["c1", "l", "b", "theta"])

def get_rectangles(N, xmin=-96, xmax=96, ymin=-96, ymax=96):
    return [
        RectangleParams(
            (random.randint(xmin, xmax), random.randint(ymin, ymax)),
            random.randint(xmin, xmax),
            random.randint(ymin, ymax),
            random.randint(0, 181),
        )
        for i in range(N)
    ]



