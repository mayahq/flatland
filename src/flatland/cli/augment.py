import argparse
import json
import os
import sys

from flatland.augment import single_file
from flatland.lang.run import main as runner


def check_dir(path):
    if os.path.exists(path) and os.path.isdir(path):
        return path
    raise NotADirectoryError(path)


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

    d = parser.parse_args()
    program = d.file.read()
    d.file.close()
    single_file(program, d.file.name, d.num_samples, d.output_dir)


if __name__ == "__main__":
    main()
