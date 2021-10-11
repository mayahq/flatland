import argparse
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

from flatland.metrics import program_distance


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


def run(train_set, test_set, output_fname):
    # print(train_set, test_set)
    scores = np.zeros((len(test_set), len(train_set)), np.float32)
    for i, t_dash in enumerate(test_set):
        p_dash = json.load(open(t_dash))
        for j, t in enumerate(train_set):
            print(f"scoring {t_dash} and {t}")
            p = json.load(open(t))
            scores[i, j] = program_distance(p_dash, p)
    # print(scores)
    GD = np.mean(np.min(scores, axis=0))
    score_df = pd.DataFrame(
        scores,
        columns=[os.path.basename(x) for x in train_set],
        index=[os.path.basename(x) for x in test_set],
    )
    print(GD)
    score_df.to_csv(output_fname, header=True, index=True)


def main():
    parser = argparse.ArgumentParser(
        prog="flatland-ddist",
        description="find the domain distance between given sets by pairwise comparisons",
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

    d = parser.parse_args()
    run(d.train_set, d.test_set, d.output)


if __name__ == "__main__":
    main()
