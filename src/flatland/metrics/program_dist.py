# distance between two programs
# compare the spec and generate a mapping using the association graph
#
import math

import networkx as nx
import numpy as np


LENIENCY = 32


def num_nodes(flow):
    return len(flow.keys())


def spec_as_dict(s):
    answer = dict()
    for node in s:
        if node["type"] == "line":
            node["center"] = {
                "x": 0.5 * (node["start"]["x"] + node["end"]["x"]),
                "y": 0.5 * (node["start"]["y"] + node["end"]["y"]),
            }
        answer[node["id"]] = node
    return answer


def dist2d(p1, p2):
    return math.sqrt((p1["x"] - p2["x"]) ** 2 + (p1["y"] - p2["y"]) ** 2)


def slope(p1, p2):
    num = p1["y"] - p2["y"]
    den = max(1e-10, p1["x"] - p2["x"])
    return num / den


def compare_circles(node1, node2):
    wt = 0
    dist = dist2d(node1["center"], node2["center"])
    wt += 0.15 * max(0, (1 - dist / LENIENCY))

    raddiff = np.abs(node1["radius"] - node2["radius"]) / max(
        node1["radius"], node2["radius"]
    )
    wt += 0.15 * max(0, (1 - raddiff / LENIENCY))

    if wt != 0:
        wt += 0.7
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

    wt += max(0, (1 - distdiff / LENIENCY)) * 0.1
    wt += max(0, (1 - slopediff / LENIENCY)) * 0.1
    wt += max(0, (1 - lendiff / LENIENCY)) * 0.1

    if wt != 0:
        wt += 0.7
    wt = np.round(wt, 2)
    # print(wt, node1, node2)
    return wt


def mapping_weight(node1, node2):
    if node1["type"] == node2["type"]:
        if node1["type"] == "circle":
            return compare_circles(node1, node2)
        elif node1["type"] == "line":
            return compare_lines(node1, node2)
    else:
        return 0


def get_nodemap(spec1, spec2):
    nodemap = []
    for k1, v1 in spec1.items():
        for k2, v2 in spec2.items():
            wt = mapping_weight(v1, v2)
            if wt > 0:
                nodemap.append((k1, k2, wt))
    nodemap.sort(key=lambda x: x[2])
    return nodemap


def create_product_graph(nmap, flow1, flow2):
    prodgraph = set()

    for k1a, k2a, wta in nmap:
        for k1b, k2b, wtb in nmap:
            # assert one-to-one mapping
            if k1a == k1b or k2a == k2b:
                continue

            # can't just map everything, so there needs to some check
            # of "common substructure" here
            dist_1 = dist2d(flow1[k1a]["center"], flow1[k1b]["center"])
            dist_2 = dist2d(flow2[k2a]["center"], flow2[k2b]["center"])
            if np.abs(dist_1 - dist_2) > LENIENCY:
                continue

            # add edge to product graph
            ind1 = nmap.index((k1a, k2a, wta))
            ind2 = nmap.index((k1b, k2b, wtb))
            edge = (min(ind1, ind2), max(ind1, ind2))
            prodgraph.add(edge)

    # print("prodgraph: V", len(nmap), "E", len(prodgraph), "ratio", density(prodgraph, nmap))
    return list(prodgraph)


def density(pgraph, nmap):
    return (2 * len(pgraph)) / (len(nmap) * (len(nmap) - 1))


def setup_weighted_clique(nmap, flow1, flow2):
    def clique_wt(clq):
        wts = [nmap[x - 1][2] for x in clq]
        return sum(wts)

    return clique_wt


def large_graph_corr(pgraph, nmap, flow1, flow2):
    pg_arr = np.array(pgraph, dtype=np.uint64) + 1
    # runtime error if vertex numbers has 0, so add 1 and subtract when finding subset
    import cliquematch

    G = cliquematch.Graph.from_edgelist(pg_arr, len(nmap))

    exact = True
    dens = density(pgraph, nmap)
    if dens > 0.7:
        # highly dense graphs => node mapping is not strict enough,
        # (too many nodes of same type) so computing the exact value is SLOW
        # hence approximate via heuristic (some form of penalty)
        clique0 = G.get_max_clique(use_heuristic=True, use_dfs=False)
        # note that the approximate clique is <= the exact clique
        exact = False
    else:
        clique0 = G.get_max_clique(use_heuristic=True, use_dfs=True)

    # TODO: weight-based cliques may need a C impl <07-09-21, ahgamut> #
    clique = max(
        G.all_cliques(size=len(clique0)), key=setup_weighted_clique(nmap, flow1, flow2)
    )
    subset = [nmap[i - 1] for i in clique]
    return subset, exact


def small_graph_corr(pgraph, nmap, flow1, flow2):
    G = nx.Graph()
    G.add_nodes_from(i + 1 for i in range(len(nmap)))
    G.add_edges_from([(a + 1, b + 1) for a, b in pgraph])
    clique = max(
        nx.algorithms.clique.find_cliques(G),
        key=setup_weighted_clique(nmap, flow1, flow2),
    )
    subset = [nmap[x - 1] for x in clique]
    # if len(subset) > 1:
    #    for x in subset:
    #        assert x[2] == 1
    return subset, True


def find_correspondence(pgraph, nmap, flow1, flow2):
    if len(pgraph) == 0 and len(nmap) == 0:
        return [], True
    elif len(pgraph) < 3000:
        return small_graph_corr(pgraph, nmap, flow1, flow2)
    else:
        # TODO: weight-based cliques may need a C impl <07-09-21, ahgamut> #
        print(
            "large graph computation",
            f"V = {len(nmap)}",
            f"E = {len(pgraph)}",
            density(pgraph, nmap),
        )
        return large_graph_corr(pgraph, nmap, flow1, flow2)


def node_similarity(subset, nodemap, flow1, flow2):
    if num_nodes(flow1) != 0 and num_nodes(flow2) != 0:
        score = sum(x[2] for x in subset)
        answer = (score / num_nodes(flow1)) * (score / num_nodes(flow2))
        return answer
    else:
        return 0


def compare_specs(s1, s2):
    flow1 = spec_as_dict(s1)
    flow2 = spec_as_dict(s2)
    nodemap = get_nodemap(flow1, flow2)
    # print("nodemap", nodemap)
    prodgraph = create_product_graph(nodemap, flow1, flow2)
    # print("prodgraph", prodgraph)
    corr, exact = find_correspondence(prodgraph, nodemap, flow1, flow2)
    # print("correspondence", corr, len(corr))
    similarity = node_similarity(corr, nodemap, flow1, flow2)
    # print("distance", 1- similarity)
    return 1 - similarity


def metric(spec1, spec2):
    return compare_specs(spec1, spec2)
