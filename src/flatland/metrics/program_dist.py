# distance between two programs
# compare the JSON and generate a subset mapping using the association graph
import logging
import math
from typing import NamedTuple

import networkx as nx
import numpy as np

from flatland.lang.primitives import resolve_scope
from flatland.metrics.distance import edge_indicator
from flatland.metrics.distance import node_weighter

logger = logging.getLogger("flatland.metrics.program_dist")


class NodeMapping(NamedTuple):
    first: str
    second: str
    weight: float


def get_nodemap(spec1, spec2):
    nodemap = []
    for k1, v1 in spec1.items():
        for k2, v2 in spec2.items():
            wt = node_weighter(v1, v2)
            if wt > 0:  # if SLOW, use > 0.5
                nodemap.append(NodeMapping(k1, k2, wt))
    return nodemap


def check_valid_mapping(corr, nmap, flow1, flow2):
    for i, (k1a, k2a, wta) in enumerate(corr):
        for j in range(i + 1, len(corr)):
            k1b, k2b, wtb = corr[j]
            if (
                k1a == k1b
                or k2a == k2b
                or not edge_indicator(flow1[k1a], flow1[k1b], flow2[k2a], flow2[k2b])
            ):
                raise AssertionError(f"mapping is not valid {corr[i], corr[j]}")
                return False
    return True


def simple_corr(nmap, flow1, flow2):
    keys1 = set(flow1.keys())
    keys2 = set(flow2.keys())
    answer = []
    awt = 0
    for k1, k2, wt in sorted(nmap, key=lambda x: x[2], reverse=True):
        if k1 in keys1 and k2 in keys2:
            valid = sum(
                edge_indicator(flow1[k1], flow1[k1x], flow2[k2], flow2[k2x])
                for (k1x, k2x, wtx) in answer
            )
            if valid == len(answer):
                keys1.remove(k1)
                keys2.remove(k2)
                awt += wt
                answer.append(NodeMapping(k1, k2, wt))
    logger.info(
        f"simple method gets a mapping of size {len(answer)}, with weight {awt}"
    )
    return answer, awt


def trim_node_mappings(nmap, basic, flow1, flow2):
    smallermap = []
    num_mappings = 5
    map_count1 = {x: 0 for x in flow1.keys()}
    map_count2 = {x: 0 for x in flow2.keys()}
    for x in sorted(nmap, key=lambda x: x[2], reverse=True):
        if x in basic or (
            map_count1[x[0]] < num_mappings and map_count2[x[1]] < num_mappings
        ):
            map_count1[x[0]] += 1
            map_count2[x[1]] += 1
            smallermap.append(x)
    logger.info(f"reduced nodes to {len(smallermap)} from {len(nmap)}")
    return smallermap


def create_product_graph(nmap, flow1, flow2):
    prodgraph = set()

    for i, (k1a, k2a, wta) in enumerate(nmap):
        for j in range(i + 1, len(nmap)):
            k1b, k2b, wtb = nmap[j]
            # assert one-to-one mapping
            if k1a == k1b or k2a == k2b:
                continue

            # can't just map everything, so there needs to some check of "common substructure"
            if edge_indicator(flow1[k1a], flow1[k1b], flow2[k2a], flow2[k2b]):
                prodgraph.add((i, j))

    return list(prodgraph)


def density(pgraph, nmap):
    return (2 * len(pgraph)) / (len(nmap) * (len(nmap) - 1))


def setup_weighted_clique(nmap, flow1, flow2, lower_bound=0):
    def clique_wt(clq):
        wts = [nmap[x - 1][2] for x in clq]
        return sum(wts)

    return clique_wt


def large_graph_corr(pgraph, nmap, flow1, flow2, lower_bound=0):
    pg_arr = np.array(pgraph, dtype=np.uint64) + 1
    # runtime error if vertex numbers has 0, so add 1 and subtract when finding subset
    weights = np.array([x[2] for x in nmap], dtype=np.float64)
    import cliquematch

    G = cliquematch.NWGraph.from_edgelist(pg_arr, len(nmap), weights)

    exact = True
    dens = density(pgraph, nmap)
    upper_bound = min([len(flow1), len(flow2)])
    logger.info(f"bounds for the clique search is [{lower_bound-1},{upper_bound}]")
    if dens > 0.85:
        # highly dense graphs => node mapping is not strict enough,
        # (too many nodes of same type) so computing the exact value is SLOW
        # hence approximate via heuristic (some form of penalty)
        clique0 = G.get_max_clique(
            lower_bound=lower_bound - 1,
            upper_bound=upper_bound,
            use_heuristic=True,
            use_dfs=False,
        )
        # note that the approximate clique is <= the exact clique
        exact = False
    else:
        clique0 = G.get_max_clique(
            lower_bound=lower_bound - 1,
            upper_bound=upper_bound,
            use_heuristic=True,
            use_dfs=True,
        )
    # since we are getting the weight-based maximum clique,
    # it is not mandatory to enumerate over
    # the multiple possible maxima wrt weights,
    # but it can be done if needed
    subset = [nmap[i - 1] for i in clique0]
    logger.info(
        f"obtained clique of size {len(subset)}, weight = {G.get_clique_weight(clique0)}"
    )
    return subset, exact


def small_graph_corr(pgraph, nmap, flow1, flow2, lower_bound=0):
    G = nx.Graph()
    G.add_nodes_from(i + 1 for i in range(len(nmap)))
    G.add_edges_from([(a + 1, b + 1) for a, b in pgraph])
    clique = max(
        nx.algorithms.clique.find_cliques(G),
        key=setup_weighted_clique(nmap, flow1, flow2, lower_bound=lower_bound),
    )
    subset = [nmap[x - 1] for x in clique]
    return subset, True


def find_correspondence(pgraph, nmap, flow1, flow2, lower_bound=0):
    if len(pgraph) == 0 or len(nmap) == 0:
        return [], True
    if len(pgraph) < 1000:
        return small_graph_corr(pgraph, nmap, flow1, flow2, lower_bound)
    else:
        logger.info(
            f"large graph: V = {len(nmap)}, E = {len(pgraph)} density = {density(pgraph, nmap)}"
        )
        return large_graph_corr(pgraph, nmap, flow1, flow2, lower_bound)


def node_similarity(subset, nodemap, flow1, flow2):
    if len(flow1) != 0 and len(flow2) != 0:
        score = sum(x[2] for x in subset)
        answer = (score / len(flow1)) * (score / len(flow2))
        return answer
    else:
        return 0


def compare_specs(flow1, flow2):
    nodemap = get_nodemap(flow1, flow2)
    # print("nodemap", nodemap)

    # obtain a heuristic mapping based on
    # best one-to-one map for each node
    # in the smaller flow
    basic, basic_wt = simple_corr(nodemap, flow1, flow2)
    # this heuristic mapping is NOT 100% OPTIMAL,
    # but it is a useful lower bound to find the optimal
    upper_bound = min([len(flow1), len(flow2)])
    if len(basic) == upper_bound and basic_wt > upper_bound * 0.95:
        # all nodes have been mapped
        # and this is an almost optimal mapping
        corr = basic
        exact = False
    else:
        nodemap = trim_node_mappings(nodemap, basic, flow1, flow2)
        prodgraph = create_product_graph(nodemap, flow1, flow2)
        # print("prodgraph", prodgraph)
        corr, exact = find_correspondence(
            prodgraph, nodemap, flow1, flow2, lower_bound=basic_wt
        )
        # print("correspondence", corr, len(corr))
    # while debugging check if the mapping is valid
    # check_valid_mapping(basic, nodemap, flow1, flow2)
    similarity = node_similarity(corr, nodemap, flow1, flow2)
    # print("distance", 1- similarity)
    return 1 - similarity


def metric(spec1, spec2):
    # print(spec1)
    # print(spec2)
    return compare_specs(spec1, spec2)
