# From Peter Norvig's
# (How to Write a (Lisp) Interpreter (in Python))
# https://norvig.com/lispy.html
# https://norvig.com/lis.py
import argparse
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


def runner(program: str, filename: str):
    initialize()
    global_env = standard_env()
    pgm = parse(program)
    # print(pgm)
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
