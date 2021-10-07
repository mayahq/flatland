import random
from collections import namedtuple

from .utils import GENERATE_ID


CircleParams = namedtuple("CircleParams", ["x", "y", "r"])


def generate(N=None, xmin=-96, xmax=96, ymin=-96, ymax=96, rmin=3, rmax=50):
    if N is None:
        N = random.randint(1, 25)
    return {
        "items": [
            CircleParams(
                random.randint(xmin, xmax),
                random.randint(ymin, ymax),
                random.randint(rmin, rmax),
            )
            for i in range(N)
        ],
        "filename": f"tmp_circles_only_{GENERATE_ID()}.py",
    }
