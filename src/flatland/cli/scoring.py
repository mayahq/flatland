import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

from flatland.metrics import program_distance
from flatland.metrics.distances import FUNCTION_MAP


def check_file(file):
    if os.path.exists(file) and os.path.isfile(file):
        return file
    raise ValueError(f"{file} is invalid")


def score_specs(path1, path2, metric_name):
    with open(path1) as f1:
        spec1 = json.load(f1)
    with open(path2) as f2:
        spec2 = json.load(f2)
    return program_distance(spec1, spec2, metric_name)


def check_files(files):
    a, b = files
    check_file(a)
    check_file(b)
    ext_a = os.path.splitext(a)[-1]
    ext_b = os.path.splitext(b)[-1]
    if ext_a == ext_b and ext_a == ".json":
        return a, b
    raise ValueError("provided files are not JSON")


def run(file1, file2, metric_name):
    f1, f2 = check_files([file1, file2])
    return score_specs(f1, f2, metric_name)


def main():
    parser = argparse.ArgumentParser(
        prog="flatland-distance",
        description="find the distance between two given images or JSONs",
        epilog="available distance metrics:\n" + "\n".join(FUNCTION_MAP.keys()),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("file1", type=str)
    parser.add_argument("file2", type=str)
    parser.add_argument(
        "-d", "--metric", default="recursive", help="distance metric to use"
    )

    d = parser.parse_args()
    print("distance is:", run(d.file1, d.file2, d.metric))


if __name__ == "__main__":
    main()
