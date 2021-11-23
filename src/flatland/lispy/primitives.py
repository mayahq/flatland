# From Peter Norvig's (How to Write a (Lisp) Interpreter (in Python))
# https://norvig.com/lispy.html
# https://norvig.com/lis.py
import json
import math
import operator as op

import flatland.utils.config as config
from flatland.utils.modding import finalize
from flatland.utils.modding import initialize


class Symbol(str):
    pass


class Number(float):
    pass


class List(list):
    def __str__(self):
        if len(self) == 0:
            return ""
        else:
            ans = str(self[0]) + "("
            ans += ", ".join(str(x) for x in self[1:])
            ans += ")"
            return ans


class Env(dict):
    "An environment: a dict of {'var': val} pairs, with an outer Env."

    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer

    def find(self, var):
        "Find the innermost Env where var appears."
        return self if (var in self) else self.outer.find(var)


class Procedure:
    "A user-defined Scheme procedure."

    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env

    def __call__(self, *args):
        return evalf(self.body, Env(self.parms, args, self.env))


Atom = (Symbol, Number)
Exp = (Atom, List)


class DAG(Procedure):
    def __init__(self, body, env):
        super().__init__((), body, env)

    def __call__(self, node):
        env = Env((), (), self.env)
        for expr in self.body:
            evalf(expr, env)
        env[node].store()
        env[node]()


class Node(Procedure):
    def __init__(self, name, body, env):
        super().__init__((), body, env)
        self.name = name
        self.input = None
        self.outputs = []
        self.targets = []
        self.position = None
        self.heading = None

    def reset(self):
        pass

    def store(self):
        self.position = config.TURTLE.position()
        self.heading = config.TURTLE.heading()

    def restore(self):
        config.TURTLE.moveto(self.position)
        config.TURTLE.setheading(self.heading)

    def forward(self):
        self.store()

        l0 = len(self.outputs)
        # l1 = len(self.targets)
        for i, nodename in enumerate(self.targets):
            node = self.env[nodename]
            node.reset()
            if i > l0 - 1:
                node.input = self.input
            else:
                node.input = self.outputs[i]

            if node.position is None:
                node.position = self.position
            if node.heading is None:
                node.heading = self.heading

            node()
            self.restore()

    def __call__(self):
        answer = evalf(self.body, Env((), (), self.env))
        self.forward()
        return answer


def loop_reset(node):
    node.position = None
    node.heading = None
    for n2 in node.targets:
        loop_reset(node.env[n2])


class LoopNode(Node):
    def __init__(self, name, start, end, body, env):
        super().__init__(name, body, env)
        self.start = start
        self.end = end
        self.i = start

    def reset(self):
        self.i = self.start
        loop_reset(self)

    def __call__(self):
        env = Env(("i"), (self.i,), self.env)
        while self.i < self.end:
            for expr in self.body:
                evalf(expr, env)
            self.forward()
            self.i += 1
        return None


class MoveNode(Node):
    def __init__(self, name, dist, theta, body, env):
        super().__init__(name, body, env)
        self.dist = evalf(dist, env)
        self.theta = evalf(theta, env)

    def __call__(self):
        self.restore()
        config.TURTLE.left(self.theta)
        config.TURTLE.forward(self.dist)
        super().__call__()


class TurnNode(Node):
    def __init__(self, name, theta, body, env):
        super().__init__(name, body, env)
        self.theta = evalf(theta, env)

    def __call__(self):
        self.restore()
        config.TURTLE.left(self.theta)
        if len(self.targets) == 0:
            raise SystemError(f"TurnNode ({self.name}) at dead end")
        super().__call__()


def check_acyclic(dagenv, fromname, toname):
    if fromname in dagenv[toname].targets:
        return False
    for n2 in dagenv[toname].targets:
        if not check_acyclic(dagenv, fromname, n2):
            return False
    return True


def node_builder(name, tp, *args):
    if tp == "loop":
        return LoopNode(name, *args)
    elif tp == "move":
        return MoveNode(name, *args)
    elif tp == "turn":
        return TurnNode(name, *args)
    else:
        raise TypeError(f"invalid node type {tp}")


def standard_env() -> Env:
    "An environment with some Scheme standard procedures."
    env = Env()
    config.TURTLE.moveto((64, 64))
    config.TURTLE.setheading(0)
    env.update(vars(math))  # sin, cos, sqrt, pi, ...
    env.update(
        {
            "+": op.add,
            "-": op.sub,
            "*": op.mul,
            "/": op.truediv,
            "%": op.mod,
            "=": op.eq,
            ">": op.gt,
            "<": op.lt,
            ">=": op.ge,
            "<=": op.le,
            "begin": lambda *x: x[-1],
            "abs": abs,
            "apply": lambda proc, args: proc(*args),
            "expt": pow,
            "map": map,
            "max": max,
            "min": min,
            "not": op.not_,
            "null?": lambda x: x == [],
            "number?": lambda x: isinstance(x, Number),
            "print": print,
            "procedure?": callable,
            "round": round,
            "symbol?": lambda x: isinstance(x, Symbol),
        }
    )
    return env


def evalf(x, env):
    "Evaluate an expression in an environment."
    if isinstance(x, Symbol):  # variable reference
        return env.find(x)[x]
    elif not isinstance(x, List):  # constant
        return x
    if len(x) == 0:
        return
    op, *args = x
    if op == "quote":  # quotation
        return args[0]
    elif op == "if":  # conditional
        (test, conseq, alt) = args
        exp = conseq if evalf(test, env) else alt
        return evalf(exp, env)
    elif op == "define-node":
        name, tp, *tpargs = args
        node = node_builder(name, tp, *tpargs, env)
        env[name] = node
    elif op == "out!":
        env.outputs.append(eval(args[0]))
    elif op == "in!":
        return evalf(env.input, env)
    elif op == "define-dag":
        name, body = args
        env[name] = DAG(body, env)
    elif op == "link-node":
        fromnode, tonode = args
        assert check_acyclic(
            env, fromnode, tonode
        ), f"{fromnode} -> {tonode} causes loop in DAG"
        env[fromnode].targets.append(tonode)
    elif op == "run-dag":
        dagname, nodename = args
        d = env[dagname]
        assert isinstance(d, DAG)
        d(nodename)
    elif op == "define":  # definition
        (symbol, exp) = args
        env[symbol] = evalf(exp, env)
    elif op == "set":  # assignment
        (symbol, exp) = args
        env.find(symbol)[symbol] = evalf(exp, env)
    elif op == "lambda":  # procedure
        (parms, body) = args
        return Procedure(parms, body, env)
    else:  # procedure call
        proc = evalf(op, env)
        vals = [evalf(arg, env) for arg in args]
        answer = proc(*vals)
        return answer
