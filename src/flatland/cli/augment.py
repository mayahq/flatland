import argparse
import os
import sys
import json

from flatland.augment import Augmentor
from flatland.lispy.parser import runner

def check_dir(path):
    if os.path.exists(path) and os.path.isdir(path):
        return path
    raise NotADirectoryError(path)


def check_compl(val):
    if val is None:
        return val
    v2 = int(val)
    if v2 > 0:
        return v2
    raise ValueError("invalid complexity")



def main():

    parser = argparse.ArgumentParser(
        prog="flatland-augment",
        description="generate programs for the flatland dataset",
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
        "--num-files",
        default=1,
        type=int,
        help="number of files to generate per domain",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="./outputs",
        type=check_dir,
        help="Output directory to store generated data",
    )
    parser.add_argument(
        "-x",
        "--also-exec",
        dest="should_exec",
        default=False,
        action="store_true",
        help="Execute each generated program",
    )

    d = parser.parse_args()
    os.chdir(d.output_dir)
    data = d.file.read()
    augmentor = Augmentor(data)
    print(json.dumps(augmentor.templates, indent=2))
    augmentor.generate_data_bulk(d.num_files)
    # augmentor.generate_data_bulk(2)




if __name__ == "__main__":
    main()
