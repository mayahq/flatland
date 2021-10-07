import random
from collections import namedtuple

from .utils import GENERATE_ID


TurnMove1Params = namedtuple("TurnMove1Params", ["start", "N", "step", "theta"])


def generate(N=None, xmin=-48, xmax=48, ymin=-48, ymax=48):
    if N is None:
        N = random.randint(5, 80)
    return {
        "items": TurnMove1Params(
            start=(random.randint(xmin, xmax), random.randint(ymin, ymax)),
            N=N,
            step=random.randint(20, 96),
            theta=random.randint(0, 181),
        ),
        "filename": f"tmp_rotline1_{GENERATE_ID()}.py",
    }
