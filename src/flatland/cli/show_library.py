import argparse
import os
import tempfile

import flatland.utils.config as CONFIG
from flatland.lang.run import main as runner
from flatland.library import check_internal_dir
from flatland.library import get_internal_dir
from flatland.library import set_internal_dir
from flatland.library.base import create_library


def check_dir(s):
    if os.path.exists(s) and os.path.isdir(s):
        return os.path.abspath(s)
    raise NotADirectoryError(f"{s} is not a valid directory")


def show_gv(lib):
    import graphviz

    G = graphviz.Digraph("sample")
    G.attr(rankdir="LR", size="8,5")
    for ind, p in lib.primitives.items():
        G.node(str(ind), p.function)
    for src, dsts in lib.connections.items():
        for dst in dsts:
            G.edge(str(src), str(dst))
    G.view()


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
        default=None,
        help="folder containing primitives of library"
        "(if None, uses internal library)",
    )
    parser.add_argument(
        "-z",
        "--visualize",
        dest="visualize",
        default=False,
        action="store_true",
        help="visualize library dependencies with graphviz",
    )

    d = parser.parse_args()
    if d.library is None:
        d.library = get_internal_dir()
    a = create_library(d.library)
    print(a)
    if d.visualize:
        show_gv(a)


if __name__ == "__main__":
    main()
