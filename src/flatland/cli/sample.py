import argparse

from flatland.utils.modding import finalize
from flatland.utils.modding import initialize
from flatland.utils.primitives import Circle
from flatland.utils.primitives import Line
from flatland.utils.primitives import Rectangle
from flatland.utils.primitives import Stop


def main():
    parser = argparse.ArgumentParser(
        prog="flatland-sample",
        description="sample script that generates PNG+JSON in the current directory",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    d = parser.parse_args()
    print("testing sample image...", d)
    initialize()

    Circle((64, 64), 10)
    Line((64, 64), (114, 114))
    Rectangle((74, 74), length=15, breadth=22, theta=42)
    Stop()

    finalize(fname="sample.py")


if __name__ == "__main__":
    main()
