import argparse
import logging

import flatland.utils.config as CONFIG
from flatland.lang.run import main as runner
from flatland.library import set_internal_dir
from flatland.utils.misc import check_dir


def main():
    parser = argparse.ArgumentParser(
        prog="flatland-draw",
        description="script to draw PNG from a given file",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "file",
        type=argparse.FileType("r", encoding="UTF-8"),
        default=None,
        help="input file",
    )
    parser.add_argument("-s", "--show", dest="show", default=False, action="store_true")
    parser.add_argument(
        "-r", "--randomize", dest="randomize", default=False, action="store_true"
    )
    parser.add_argument(
        "-l",
        "--library",
        default="./library",
        type=check_dir,
        help="folder containing library of flows",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        default=False,
        action="store_true",
        help="show debugging information",
    )

    d = parser.parse_args()
    if d.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger("PIL").propagate = False
    set_internal_dir(d.library)
    CONFIG.SHOWTURTLE = d.show
    CONFIG.RANDOMIZE = d.randomize
    CONFIG.RUN = True
    expr, fdata = runner(d.file.read(), d.file.name)

    if d.verbose and CONFIG.RANDOMIZE:
        print(expr)


if __name__ == "__main__":
    main()
