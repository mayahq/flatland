import argparse
import json
import logging
import os
import sys

import numpy as np
from PIL import Image

import flatland.utils.config as CONFIG
from flatland.lang.primitives import resolve_scope
from flatland.lang.primitives import standard_env
from flatland.lang.run import main as parse_and_run_flow
from flatland.library import set_internal_dir
from flatland.metrics import program_distance
from flatland.utils.misc import check_dir
from flatland.utils.misc import check_file


def score_specs(path1, path2):
    env = standard_env()
    with open(path1) as f1:
        _, spec1 = parse_and_run_flow(f1.read(), f1.name, env=env)
        spec1 = resolve_scope(spec1)
    with open(path2) as f2:
        _, spec2 = parse_and_run_flow(f2.read(), f2.name, env=env)
        spec2 = resolve_scope(spec2)
    return program_distance(spec1, spec2)


def check_files(files):
    a, b = files
    check_file(a)
    check_file(b)
    ext_a = os.path.splitext(a)[-1]
    ext_b = os.path.splitext(b)[-1]
    valid_exts = (".lisp", ".fbp")
    if ext_a in valid_exts and ext_b in valid_exts:
        return a, b
    raise ValueError(f"provided files are not .fbp or .lisp {ext_a, ext_b}")


def run(file1, file2):
    f1, f2 = check_files([file1, file2])
    return score_specs(f1, f2)


def main():
    CONFIG.RUN = False
    parser = argparse.ArgumentParser(
        prog="flatland-scoring",
        description="find the distance between two FBP",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-l", "--library", default="./library", type=check_dir, help="library of flows"
    )
    parser.add_argument("file1", type=str)
    parser.add_argument("file2", type=str)
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
    print("distance is:", run(d.file1, d.file2))


if __name__ == "__main__":
    main()
