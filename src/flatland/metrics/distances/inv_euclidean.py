# euclidean distance with leniency factor,
# but degrading continuously
import math

import numpy as np

from flatland.metrics.distances import LENIENCY
from flatland.metrics.distances.euclidean import dist2d
from flatland.metrics.distances.euclidean import slope


def compare_circles(node1, node2):
    wt = 0
    dist = dist2d(node1["center"], node2["center"])
    wt += 0.2 / (1 + dist / LENIENCY)

    raddiff = np.abs(node1["radius"] - node2["radius"])
    wt += 0.1 / (1 + raddiff / LENIENCY)

    thetadiff = abs(node1.get("theta", 360) - node2.get("theta", 360))
    wt += 0.1 / (1 + thetadiff / LENIENCY)

    if wt != 0:
        wt += 0.6
    wt = np.round(wt, 2)
    return wt


def compare_lines(node1, node2):
    wt = 0
    dist_a = dist2d(node1["start"], node2["start"]) + dist2d(node1["end"], node2["end"])
    dist_b = dist2d(node1["start"], node2["end"]) + dist2d(node1["end"], node2["start"])

    distdiff = min(dist_a, dist_b)
    slopediff = np.abs(
        slope(node1["start"], node1["end"]) - slope(node2["start"], node2["end"])
    )
    lendiff = np.abs(
        dist2d(node1["start"], node1["end"]) - dist2d(node2["start"], node2["end"])
    )

    wt += 0.1 / (1 + distdiff / LENIENCY)
    wt += 0.1 / (1 + slopediff / LENIENCY)
    wt += 0.1 / (1 + lendiff / LENIENCY)

    if wt != 0:
        wt += 0.7
    wt = np.round(wt, 2)
    return wt


def node_weighter(node1, node2):
    if node1["type"] == node2["type"]:
        if node1["type"] == "circle":
            return compare_circles(node1, node2)
        elif node1["type"] == "line":
            return compare_lines(node1, node2)
    else:
        return 0


def edge_indicator(node1a, node1b, node2a, node2b):
    dist_1 = dist2d(node1a["center"], node1b["center"])
    dist_2 = dist2d(node2a["center"], node2b["center"])
    return abs(dist_1 - dist_2) <= LENIENCY