import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

from flatland.lispy.parser import runner as parse_and_run_flow
from flatland.lispy.primitives import standard_env
from flatland.metrics import program_distance
from flatland.metrics.distances import FUNCTION_MAP


def check_file(file):
    if os.path.exists(file) and os.path.isfile(file):
        return file
    raise ValueError(f"{file} is invalid")


def score_specs(path1, path2, metric_name):
    env = standard_env()
    with open(path1) as f1:
        spec1 = parse_and_run_flow(f1.read(), f1.name, run=False, env=env)
    with open(path2) as f2:
        spec2 = parse_and_run_flow(f2.read(), f2.name, run=False, env=env)
    return program_distance(spec1, spec2, metric_name)


def check_files(files):
    a, b = files
    check_file(a)
    check_file(b)
    ext_a = os.path.splitext(a)[-1]
    ext_b = os.path.splitext(b)[-1]
    if ext_a == ext_b and (ext_a == ".lisp" or ext_a == ".fbp"):
        return a, b
    raise ValueError(f"provided files are not both .fbp or .lisp {ext_a, ext_b}")


def run(file1, file2, metric_name):
    f1, f2 = check_files([file1, file2])
    return score_specs(f1, f2, metric_name)


def main():
    parser = argparse.ArgumentParser(
        prog="flatland-distance",
        description="find the distance between two FBP",
        # epilog="available distance metrics:\n" + "\n".join(FUNCTION_MAP.keys()),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("file1", type=str)
    parser.add_argument("file2", type=str)

    d = parser.parse_args()
    print("distance is:", run(d.file1, d.file2, "recursive"))


if __name__ == "__main__":
    main()
