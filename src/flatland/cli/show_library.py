import argparse
import logging
import tempfile

import flatland.utils.config as CONFIG
from flatland.lang.run import main as runner
from flatland.library import check_internal_dir
from flatland.library import get_internal_dir
from flatland.library import set_internal_dir
from flatland.library.base import create_library
from flatland.utils.misc import check_dir


def show_gv(lib):
    import graphviz

    G = graphviz.Digraph("library")
    G.attr(rankdir="LR", size="8,5")
    for ind, p in lib.primitives.items():
        G.node(str(ind), p.function)
    for src, dsts in lib.connections.items():
        for dst in dsts:
            G.edge(str(src), str(dst))
    G.format = "png"
    G.view(cleanup=True)


def main():
    parser = argparse.ArgumentParser(
        prog="flatland-library",
        description="script to show primitives and dependencies of library",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-l",
        "--library",
        type=check_dir,
        default="./library",
        help="folder containing primitives of library",
    )
    parser.add_argument(
        "-z",
        "--visualize",
        dest="visualize",
        default=False,
        action="store_true",
        help="visualize library dependencies with graphviz",
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
    a = create_library(d.library)
    print(a)
    if d.visualize:
        show_gv(a)


if __name__ == "__main__":
    main()
