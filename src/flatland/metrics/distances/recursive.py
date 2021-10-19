# recursive comparison of properties


def compare_subparts(part1, part2):
    if isinstance(part1, (int, float)):
        # adding 128 because
        # the image range starts at
        # (-128, -128)
        a = max(part1, part2) + 128
        b = min(part1, part2) + 128
        return b / a
    elif isinstance(part1, str):
        return part1 == part2
    elif isinstance(part1, list):
        den = len(part1)
        if den != len(part2):
            return 0
        num = sum(compare_subparts(part1[i], part2[i]) for i in range(den))
        return num / den
    elif isinstance(part1, dict):
        common_keys = set(part1.keys()) & set(part2.keys())
        num = sum(compare_subparts(part1[k], part2[k]) for k in common_keys)
        return (num / len(part1)) * (num / len(part2))
    else:
        return 0


def compare_nodes(node1, node2):
    num = 0
    den = 0
    for k in node1.keys():
        if k == "id":
            continue
        a = compare_subparts(node1[k], node2[k])
        num += a
        den += 1
    wt = num / den
    return wt


def node_weighter(node1, node2):
    if node1["type"] == node2["type"]:
        return compare_nodes(node1, node2)
    else:
        return 0


def edge_indicator(node1a, node1b, node2a, node2b):
    return True
