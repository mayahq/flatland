import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

from flatland.metrics import image_distance
from flatland.metrics import program_distance


def check_file(file):
    if os.path.exists(file) and os.path.isfile(file):
        return file
    raise ValueError(f"{file} is invalid")


def score_specs(path1, path2):
    with open(path1) as f1:
        spec1 = json.load(f1)
    with open(path2) as f2:
        spec2 = json.load(f2)
    return program_distance(spec1, spec2)


def score_images(path1, path2):
    img1 = np.array(Image.open(path1).convert("L"))
    img2 = np.array(Image.open(path2).convert("L"))
    return image_distance(img1, img2)


def check_files(files):
    a, b = files
    check_file(a)
    check_file(b)
    ext_a = os.path.splitext(a)[-1]
    ext_b = os.path.splitext(b)[-1]
    if ext_a == ext_b and ext_a == ".json":
        return score_specs, a, b
    if ext_a == ext_b and ext_a == ".png":
        return score_images, a, b
    raise ValueError("provided files are not both PNG or JSON")


def run(file1, file2):
    func, f1, f2 = check_files([file1, file2])
    return func(f1, f2)


def main():
    parser = argparse.ArgumentParser(
        prog="flatland-distance",
        description="find the distance between two given images or JSONs",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("file1", type=str)
    parser.add_argument("file2", type=str)

    d = parser.parse_args()
    print("distance metric is:", run(d.file1, d.file2))


if __name__ == "__main__":
    main()
