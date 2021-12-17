import argparse

import flatland.utils.config as CONFIG
from flatland.lang.run import main as runner


def main():
    parser = argparse.ArgumentParser(
        prog="flatland-sample",
        description="script to draw PNG from a given file",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "file",
        type=argparse.FileType("r", encoding="UTF-8"),
        default=None,
        help="input file",
    )
    parser.add_argument(
        "-s", "--show-turtle", dest="show", default=False, action="store_true"
    )
    parser.add_argument(
        "-r", "--randomize", dest="randomize", default=False, action="store_true"
    )

    d = parser.parse_args()
    CONFIG.SHOWTURTLE = d.show
    CONFIG.RANDOMIZE = d.randomize
    CONFIG.RUN = True
    runner(d.file.read(), d.file.name)


if __name__ == "__main__":
    main()
