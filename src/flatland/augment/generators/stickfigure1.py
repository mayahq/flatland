import random
from collections import namedtuple

from .utils import GENERATE_ID

ThetaLength = namedtuple("ThetaLength", ["theta", "length"])
HeadParams = namedtuple("HeadParams", ["x", "y", "r"])
FigureParams = namedtuple("FigureParams", ["head", "torso1", "arms", "torso2", "legs"])


def generate(N=None, xmin=-96, xmax=96, ymin=-96, ymax=96):
    if N is None:
        N = random.randint(1, 6)
    return {
        "items": [
            FigureParams(
                head=dict(
                    HeadParams(
                        random.randint(xmin // 2, xmax // 2),
                        random.randint(ymin // 2, ymax // 2),
                        random.randint(10, 30),
                    )._asdict()
                ),
                torso1=dict(
                    ThetaLength(
                        random.randint(0, 180), random.randint(5, xmax // 2)
                    )._asdict()
                ),
                arms=dict(
                    ThetaLength(
                        random.randint(-90, 90), random.randint(5, xmax // 3)
                    )._asdict()
                ),
                torso2=dict(
                    ThetaLength(
                        random.randint(0, 180), random.randint(5, xmax // 2)
                    )._asdict()
                ),
                legs=dict(
                    ThetaLength(
                        random.randint(-90, 90), random.randint(5, int(xmax // 1.5))
                    )._asdict()
                ),
            )
            for i in range(N)
        ],
        "filename": f"tmp_stickfigure1_{GENERATE_ID()}.py",
    }
