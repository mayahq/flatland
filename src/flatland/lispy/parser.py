# From Peter Norvig's
# (How to Write a (Lisp) Interpreter (in Python))
# https://norvig.com/lispy.html
# https://norvig.com/lis.py
import argparse
import json
import os
import sys

from flatland.lispy.primitives import Atom
from flatland.lispy.primitives import evalf
from flatland.lispy.primitives import Exp
from flatland.lispy.primitives import List
from flatland.lispy.primitives import standard_env
from flatland.lispy.primitives import Symbol
from flatland.utils.modding import finalize
from flatland.utils.modding import initialize


def atom(token: str) -> Atom:
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)


def read_from_tokens(tokens: List) -> Exp:
    if len(tokens) == 0:
        raise SyntaxError("unexpected EOF")
    token = tokens.pop(0)
    if token == "(":
        L = List()
        while tokens[0] != ")":
            L.append(read_from_tokens(tokens))
        tokens.pop(0)  # pop off ')'
        return L
    elif token == ")":
        raise SyntaxError("unexpected )")
    else:
        return atom(token)


def tokenize(chars: str) -> list:
    return chars.replace("(", " ( ").replace(")", " ) ").split()


def parse(program: str) -> Exp:
    tokenl = tokenize(program)
    expr = read_from_tokens(tokenl)
    return expr


def rewrite_edge(edge):
    fnode, tnode = edge
    answer = []
    if "(start" in fnode:  # define-flow open
        fname, fparams = fnode.split("(")
        fparams = fparams.replace("start", "(").replace("( ", "(")
        answer.append(f"(define-flow {fname} {fparams} (\n")
        tname, tprops = tnode.split("(")
        answer.append(f"(create-node {tname} {tprops}\n")
        answer.append(f"(create-entry {tname})\n")
    elif "{" in fnode:  # defining the main flow
        data = json.loads(fnode)
        x, y = data.get("position", (64, 64))
        theta = data.get("theta", 0)
        pos = f"{x} {y}"
        if "(" in tnode:
            ind = tnode.index("(")
            tname = tnode[:ind]
            tprops = tnode[ind + 1 :]
        else:
            tname = tnode
            tprops = "("
        answer.append(f"(run-flow {tname} ({tprops} ({pos}) {theta})\n")
    elif "(end" in tnode:  # define-flow closed
        answer.append(f"(create-exit {fnode}))\n)\n")
    else:  # just an edge
        fname, *port = fnode.split(" ")
        if len(port) == 0:
            port = "out"
        else:
            port = port[0]

        if "(" in tnode:
            ind = tnode.index("(")
            tname = tnode[:ind]
            tprops = tnode[ind + 1 :]
            answer.append(f"(create-node {tname} {tprops}\n")
        else:
            tname = tnode

        if port == "out":
            answer.append(f"(create-link {fname} {tname})\n")
        else:
            answer.append(f"(create-link {fname}:{port} {tname})\n")
    return "".join(answer)


def parse_edges(edges):
    expr = "(begin\n" + "".join(rewrite_edge(x) for x in edges) + ")"
    print(expr)
    return parse(expr)


def import_flow_from_file(flowname, filename):
    print(flowname, filename)
    with open(filename.strip('"')) as f:
        edges = f.readlines()
    start = 0
    end = len(edges)
    for i, edge in enumerate(edges):
        if f"{flowname}(start" in edge:
            start = i
            continue
        if f"{flowname}(end" in edge:
            end = i + 1
            break
    edges = edges[start:end]
    return parse0(edges)


def parse0(lines):
    def edge_cleaner(s):
        fnode, tnode = s.split("->")
        return fnode.strip(), tnode.strip()

    edges = []
    imports = []
    for line in lines:
        if len(line) == 0 or "@param" in line:
            continue
        if "import" in line:
            a = line.replace("import ", "").replace("from ", "")
            flowname, filename = a.split()
            imports.extend(import_flow_from_file(flowname, filename))
        else:
            edges.append(edge_cleaner(line))
    edges = imports + edges
    return edges


def setdir(filename):
    fdir = os.path.abspath(os.path.dirname(filename))
    print(fdir)
    os.chdir(fdir)


def runner(program: str, filename: str):
    initialize()
    setdir(filename)
    global_env = standard_env()
    edges = parse0(program.split("\n"))
    pgm = parse_edges(edges)
    evalf(pgm, global_env)
    finalize(filename)


def main():
    parser = argparse.ArgumentParser(
        prog="flatland-lispy",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "file",
        type=argparse.FileType("r", encoding="UTF-8"),
        default=None,
        help="input file",
    )
    d = parser.parse_args()
    runner(d.file.read(), d.file.name)


if __name__ == "__main__":
    main()
