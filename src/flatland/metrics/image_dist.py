# distance between two images
# can be as complex as possible
import numpy as np


def normalize(img):
    return (img - np.min(img)) / (np.max(img) - np.min(img))


def metric(img1, img2):
    sim = np.mean(np.abs(normalize(img1) - normalize(img2)))
    return 1 - sim
