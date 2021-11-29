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

    def __call__(self, snode):
        env = Env((), (), self.env)
        for expr in self.body:
            evalf(expr, env)

        start = dict(position=(64, 64), theta=0)
        messages = [(snode, start)]

        while len(messages) > 0:
            msg = messages.pop(0)
            node, data = msg
            if data:
                print("Processing:", node, data)
                results = env[node](data)
                messages = messages + results


class Node(Procedure):
    def __init__(self, name, env):
        super().__init__((), (), env)
        self.name = name
        self.targets = []

    def forward(self, data):
        outdata = dict(**data)
        outdata["position"] = config.TURTLE.position()
        outdata["theta"] = config.TURTLE.heading()
        results = []
        for i, nodename in enumerate(self.targets):
            results.append((nodename, outdata))
        return results

    def valid_message(self, data):
        if data.get("position", None):
            config.TURTLE.moveto(data["position"])
            config.TURTLE.setheading(data["theta"])
            return True
        return False

    def __call__(self, data):
        if self.valid_message(data):
            results = self.forward(data)
            return results
        return []


def loop_reset(node):
    node.position = None
    node.heading = None
    for n2 in node.targets:
        loop_reset(node.env[n2])


class LoopNode(Node):
    def __init__(self, name, varname, start, end, env):
        super().__init__(name, env)
        self.start = start
        self.end = end
        self.varname = varname

    def reset(self):
        self.i = self.start
        loop_reset(self)

    def forward(self, data):
        outdata = dict(**data)
        outdata["position"] = config.TURTLE.position()
        outdata["theta"] = config.TURTLE.heading()
        results = []
        for i, nodename in enumerate(self.targets):
            loop_node = not check_acyclic(self.env, self.name, nodename)
            in_loop = outdata[self.varname] < self.end

            if not (loop_node ^ in_loop):
                results.append((nodename, outdata))
        return results

    def __call__(self, data):
        if self.valid_message(data):
            data[self.varname] = data.get(self.varname, self.start - 1)
            if data[self.varname] < self.end:
                data[self.varname] = data[self.varname] + 1
            return self.forward(data)
        return []


class MoveNode(Node):
    def __init__(self, name, dist, penup, env):
        super().__init__(name, env)
        self.dist = evalf(dist, env)
        self.penup = evalf(penup, env)

    def __call__(self, data):
        if self.valid_message(data):
            if self.penup:
                config.TURTLE.penup()
            config.TURTLE.forward(self.dist)
            if self.penup:
                config.TURTLE.pendown()
            return self.forward(data)
        return []


class TurnNode(Node):
    def __init__(self, name, theta, env):
        super().__init__(name, env)
        self.theta = evalf(theta, env)

    def __call__(self, data):
        if self.valid_message(data):
            config.TURTLE.left(self.theta)
            return self.forward(data)
        return []


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
        # assert check_acyclic(
        #    env, fromnode, tonode
        # ), f"{fromnode} -> {tonode} causes loop in DAG"
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
