import random
from collections import namedtuple

from .utils import GENERATE_ID


TurnMove1Params = namedtuple("TurnMove1Params", ["start", "N", "step", "theta"])


def generate(N=None, xmin=32, xmax=96, ymin=32, ymax=96):
    if N is None:
        N = random.randint(5, 20)
    return {
        "items": TurnMove1Params(
            start=(random.randint(xmin, xmax), random.randint(ymin, ymax)),
            N=N,
            step=random.randint(20, 96),
            theta=random.randint(0, 181),
        ),
        "filename": f"tmp_rotline1_{GENERATE_ID()}.py",
    }
