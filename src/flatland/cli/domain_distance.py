import argparse
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

from flatland.metrics import program_distance
from flatland.metrics.distances import FUNCTION_MAP


def check_folder(folder):
    if os.path.exists(folder) and os.path.isdir(folder):
        files = glob.glob(os.path.join(folder, "*.json"))
        if len(files) == 0:
            raise ValueError(f"{folder} contains no JSON files")
        return files
    raise ValueError(f"{folder} is invalid")


def check_csv(fname):
    if os.path.splitext(fname)[-1] == ".csv":
        return fname
    raise ValueError(f"{fname} is not a .csv")


def run(train_set, test_set, output_fname, metric_name):
    # print(train_set, test_set)
    final_scores = np.zeros((len(test_set), 1), np.float32)
    scores = np.zeros(len(train_set), np.float32)
    total = len(train_set) * len(test_set)
    count = 0
    for i, t_dash in enumerate(test_set):
        p_dash = json.load(open(t_dash))
        for j, t in enumerate(train_set):
            count += 1
            print(f"{count}/{total}: scoring {t_dash} and {t}", end="\r")
            p = json.load(open(t))
            scores[j] = program_distance(p_dash, p, metric_name)
        final_scores[i] = np.min(scores[j])
    DD = np.mean(final_scores)
    score_df = pd.DataFrame(
        final_scores,
        columns=["domain_distance"],
        index=[os.path.basename(x) for x in test_set],
    )
    print()
    print("domain domain_distance is", DD)
    score_df.to_csv(output_fname, header=True, index=True)


def main():
    parser = argparse.ArgumentParser(
        prog="flatland-ddist",
        description="find the domain distance between given sets by pairwise comparisons",
        epilog="available distance metrics:\n" + "\n".join(FUNCTION_MAP.keys()),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-a",
        "--train-set",
        type=check_folder,
        help="folder containing training set JSONs",
    )
    parser.add_argument(
        "-b", "--test-set", type=check_folder, help="folder containing test set JSONs"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=check_csv,
        default="results.csv",
        help="output score matrix to a CSV",
    )
    parser.add_argument(
        "-d", "--metric", default="euclidean", help="distance metric to use"
    )

    d = parser.parse_args()
    run(d.train_set, d.test_set, d.output, d.metric)


if __name__ == "__main__":
    main()
