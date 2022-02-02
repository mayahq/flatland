import argparse
import glob
import json
import os
import sys

import joblib
import numpy as np
import pandas as pd

import flatland.utils.config as CONFIG
from flatland.lang.primitives import resolve_scope
from flatland.lang.run import main as parse_and_run_flow
from flatland.library import set_internal_dir
from flatland.metrics import program_distance
from flatland.utils.misc import check_dir


def check_files(folder):
    folder = check_dir(folder)
    files = glob.glob(os.path.join(folder, "*.fbp")) + glob.glob(
        os.path.join(folder, "*.lisp")
    )
    if len(files) == 0:
        raise ValueError(f"{folder} contains no files")
    return files


def check_csv(fname):
    if os.path.splitext(fname)[-1] == ".csv":
        return fname
    raise ValueError(f"{fname} is not a .csv")


def get_data(filename):
    with open(filename) as f:
        _, fdata = parse_and_run_flow(f.read(), filename, env=None)
    return resolve_scope(fdata)


def run(train_set, test_set, output_fname):
    # print(train_set, test_set)
    final_scores = np.zeros((len(test_set), 1), np.float32)
    with joblib.Parallel(n_jobs=-1) as parallel:
        for i, t_dash in enumerate(test_set):
            p_dash = get_data(t_dash)
            scores = parallel(
                joblib.delayed(program_distance)(p_dash, get_data(t)) for t in train_set
            )
            final_scores[i] = np.min(scores)
    DD = np.mean(final_scores)
    score_df = pd.DataFrame(
        final_scores,
        columns=["domain_distance"],
        index=[os.path.basename(x) for x in test_set],
    )
    print("domain_distance is", DD)
    score_df.to_csv(output_fname, header=True, index=True)


def main():
    CONFIG.RUN = False
    parser = argparse.ArgumentParser(
        prog="flatland-ddist",
        description="find the domain distance between given sets by pairwise comparisons",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-a",
        "--train-set",
        type=check_files,
        help="folder containing training set programs",
    )
    parser.add_argument(
        "-b", "--test-set", type=check_files, help="folder containing test set programs"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=check_csv,
        default="results.csv",
        help="output score matrix to a CSV",
    )
    parser.add_argument(
        "-l",
        "--library",
        type=check_dir,
        default="./library",
        help="folder containing primitives of library",
    )

    d = parser.parse_args()
    set_internal_dir(d.library)
    run(d.train_set, d.test_set, d.output)


if __name__ == "__main__":
    main()
