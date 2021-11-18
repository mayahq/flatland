import argparse

from flatland.lispy.parser import runner
from flatland.utils.modding import finalize
from flatland.utils.modding import initialize


def main():
    parser = argparse.ArgumentParser(
        prog="flatland-sample",
        description="sample script that generates PNG+JSON in the current directory",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "file",
        type=argparse.FileType("r", encoding="UTF-8"),
        default=None,
        help="input file",
    )
    d = parser.parse_args()
    runner(d.file.read(), d.file.name)


if __name__ == "__main__":
    main()
