import argparse
import json
import logging
import sys

from flatland.augment import single_file
from flatland.lang.run import main as runner
from flatland.library import set_internal_dir
from flatland.utils.misc import check_dir


def main():
    parser = argparse.ArgumentParser(
        prog="flatland-augment",
        description="generate random programs from a given file",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "file",
        type=argparse.FileType("r", encoding="UTF-8"),
        default=None,
        help="input file",
    )
    parser.add_argument(
        "-n",
        "--num-samples",
        default=1,
        type=int,
        help="number of files to generate",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="./outputs",
        type=check_dir,
        help="Output directory to store generated data",
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
    program = d.file.read()
    d.file.close()
    single_file(program, d.file.name, d.num_samples, d.output_dir)


if __name__ == "__main__":
    main()
