import random
from collections import namedtuple

from .utils import GENERATE_ID

LineParams = namedtuple("LineParams", ["c1", "c2"])


def generate(N=None, xmin=-128, xmax=128, ymin=-128, ymax=128):
    if N is None:
        N = random.randint(1, 25)
    return {
        "items": [
            LineParams(
                (random.randint(xmin, xmax), random.randint(ymin, ymax)),
                (random.randint(xmin, xmax), random.randint(ymin, ymax)),
            )
            for i in range(N)
        ],
        "filename": f"tmp_lines_only_{GENERATE_ID()}.py",
    }
