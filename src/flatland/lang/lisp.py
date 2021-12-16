# From Peter Norvig's
# (How to Write a (Lisp) Interpreter (in Python))
# https://norvig.com/lang.html
# https://norvig.com/lis.py
from flatland.lang.primitives import Atom
from flatland.lang.primitives import evalf
from flatland.lang.primitives import Exp
from flatland.lang.primitives import List
from flatland.lang.primitives import standard_env
from flatland.lang.primitives import Symbol


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
