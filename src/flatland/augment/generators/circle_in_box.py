import random
from collections import namedtuple

from .utils import GENERATE_ID

CBoxParams = namedtuple("CBoxParams", ["x", "y", "r"])


def generate(N=None, xmin=0, xmax=72, ymin=0, ymax=72, rmin=8, rmax=25):
    if N is None:
        N = random.randint(1, 5)
    return {
        "items": [
            CBoxParams(
                random.randint(xmin, xmax),
                random.randint(ymin, ymax),
                random.randint(rmin, rmax),
            )
            for i in range(N)
        ],
        "filename": f"tmp_circle_in_box_{GENERATE_ID()}.py",
    }
