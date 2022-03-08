# recursive comparison of properties
import numpy as np


def numdiff(a, b, normalize=128):
    return max(0, 1 - abs(a - b) / normalize)


def compare_subparts(part1, part2):
    if isinstance(part1, (int, float)):
        answer = numdiff(part1, part2)
    elif isinstance(part1, str):
        answer = float(part1 == part2)
    elif isinstance(part1, list):
        den = len(part1)
        if den != len(part2):
            return 0.0
        num = sum(compare_subparts(part1[i], part2[i]) for i in range(den))
        answer = num / den
    elif isinstance(part1, dict):
        common_keys = set(part1.keys()) & set(part2.keys())
        num = sum(compare_subparts(part1[k], part2[k]) for k in common_keys)
        answer = (num / len(part1)) * (num / len(part2))
    else:
        answer = 0
    return np.round(answer, 2)


def compare_loops(node1, node2):
    den = 2
    num = 0
    for k in ["start", "end"]:
        if node1[k] == node2[k]:
            num += 1
    return num / den


def compare_moves(node1, node2):
    den = 2
    num = 0
    for k in ["dist", "penup"]:
        if node1[k] == node2[k]:
            num += 1
    return num / den


def compare_turns(node1, node2):
    a = node1["theta"] % 360
    b = node2["theta"] % 360
    return numdiff(a, b, 360)


def compare_info(node1, node2):
    den = 2
    num = 0
    num += compare_subparts(node1["position"], node2["position"])
    num += compare_turns(node1, node2)
    return num / den


def node_weighter(node1, node2):
    if node1["type"] == node2["type"]:
        p1 = node1["params"]
        p2 = node2["params"]
        if node1["type"] == "loop":
            return compare_loops(p1, p2)
        elif node1["type"] == "move":
            return compare_moves(p1, p2)
        elif node1["type"] == "turn":
            return compare_turns(p1, p2)
        elif node1["type"] == "info":
            return compare_info(p1, p2)
        else:
            return 0
    else:
        return 0


def get_edgetype(node1, node2):
    for t, v in node1["targets"].items():
        if node2["id"] in v:
            return t  # edge exists and is of type t
    return ""


def edge_indicator(node1a, node1b, node2a, node2b):
    # check the edge between the corresponding nodes
    et1 = get_edgetype(node1a, node1b)
    et2 = get_edgetype(node2a, node2b)

    # check the "back-edge" between them, because cycle
    et1_r = get_edgetype(node1b, node1a)
    et2_r = get_edgetype(node2b, node2a)

    return (et1 == et2) and (et1_r == et2_r)
