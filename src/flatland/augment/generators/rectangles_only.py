import random
from collections import namedtuple

from .utils import GENERATE_ID


RectangleParams = namedtuple("RectangleParams", ["c1", "l", "b", "theta"])


def generate(N=None, xmin=0, xmax=96, ymin=0, ymax=96):
    if N is None:
        N = random.randint(1, 5)
    return {
        "items": [
            RectangleParams(
                (random.randint(xmin, xmax), random.randint(ymin, ymax)),
                random.randint(xmin, xmax),
                random.randint(ymin, ymax),
                random.randint(0, 181),
            )
            for i in range(N)
        ],
        "filename": f"tmp_rectangles_only_{GENERATE_ID()}.py",
    }
