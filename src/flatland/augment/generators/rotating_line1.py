import random
from collections import namedtuple


TurnMove1Params = namedtuple("TurnMove1Params", ["start", "N", "step", "theta"])



def get_rotmove1(N, xmin=-48, xmax=48, ymin=-48, ymax=48):
    return TurnMove1Params(
        start=(random.randint(xmin, xmax), random.randint(ymin, ymax)),
        N=random.randint(20, 96),
        step=random.randint(20, 96),
        theta=random.randint(0, 181),
    )



