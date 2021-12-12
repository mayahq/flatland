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


def parse_lisp(program: str) -> Exp:
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
    return parse_fbp(edges)


def parse_fbp(lines):
    def edge_cleaner(s):
        fnode, tnode = s.split("->")
        return fnode.strip(), tnode.strip()

    edges = []
    imports = []
    for line in lines:
        if len(line) == 0 or "@param" in line:
            continue
        if "#include" in line:
            imports.append(f"({line})")
        else:
            edges.append(edge_cleaner(line))
    # print("edges", edges)
    expr = (
        "(begin\n" + "\n".join(imports) + "".join(rewrite_edge(x) for x in edges) + ")"
    )
    # print(expr)
    return parse_lisp(expr)


def setdir(filename):
    fdir = os.path.abspath(os.path.dirname(filename))
    print(fdir)
    os.chdir(fdir)


class CurrentDir:
    def __init__(self, filename):
        self.prev_dir = os.path.abspath(os.getcwd())
        self.cur_dir = os.path.abspath(os.path.dirname(filename))

    def __enter__(self):
        # print("Switching to", self.cur_dir)
        os.chdir(self.cur_dir)

    def __exit__(self, type, value, traceback):
        # print("Switching back to", self.prev_dir)
        os.chdir(self.prev_dir)
        if type:
            print(type, value, traceback)


def runner(program: str, filename: str, env=None, run=True):
    initialize()
    with CurrentDir(filename):
        ext = os.path.splitext(filename)[1]
        if ".fbp" in ext:
            pgm = parse_fbp(program.split("\n"))
        elif ".lisp" in ext:
            pgm = parse_lisp(program)
        else:
            raise ValueError(f"Invalid file extension {ext}, expecting .fbp or .lisp")
        if env is None:
            env = standard_env()
        env.includes.add(filename)
        # print(f"evaluating {filename}")
        fdata = evalf(pgm, env, run)
        if run:  # drawing happened
            finalize(filename)
        return fdata


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
    runner(d.file.read(), os.path.abspath(d.file.name))


if __name__ == "__main__":
    main()
