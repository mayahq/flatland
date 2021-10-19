# binary equality comparison


def compare_nodes(node1, node2):
    num = 0
    den = 0
    for k in node1.keys():
        if k == "id":
            continue
        if node1[k] == node2[k]:
            num += 1
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
