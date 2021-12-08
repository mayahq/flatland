# From Peter Norvig's (How to Write a (Lisp) Interpreter (in Python))
# https://norvig.com/lispy.html
# https://norvig.com/lis.py
import json
import math
import operator as op
import random
import time

import flatland.utils.config as config
from flatland.utils.modding import finalize
from flatland.utils.modding import initialize


def GENERATE_NODEID():
    return "{:10x}.fed{:05x}".format(
        random.randrange(16 ** 10),
        random.randrange(16 ** 5),
    )


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
        self.name = GENERATE_NODEID()

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


class Node(Procedure):
    def __init__(self, name, env):
        super().__init__((), (), Env((), (), env))
        self.name = name
        self.sources = []
        self.targets = {"out": []}

    def forward(self, outdata):
        outdata["position"] = config.TURTLE.position()
        outdata["theta"] = config.TURTLE.heading()
        results = []
        for i, nodename in enumerate(self.targets["out"]):
            results.append((self.name, nodename, outdata))
        return results

    def valid_message(self, data):
        if data.get("position", None):
            config.TURTLE.moveto(data["position"])
            config.TURTLE.setheading(data["theta"])
            return True
        return False

    def __call__(self, data0):
        if self.valid_message(data0):
            data = dict(**data0)
            results = self.forward(data)
            return results
        return []

    def to_dict(self):
        return {
            "name": self.name,
            "id": self.env.name,
            "type": type(self).__name__,
            "scope": self.env.outer.name,
            "sources": self.sources,
            "targets": self.targets,
        }

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)


def loop_reset(node):
    node.position = None
    node.heading = None
    for n2 in node.targets:
        loop_reset(node.env[n2])


class LoopNode(Node):
    def __init__(self, name, varname, start, end, env):
        super().__init__(name, env)
        self.start = evalf(start, self.env)
        self.end = evalf(end, self.env)
        self.varname = varname
        self.resolved_name = f"{self.env.name}:{self.varname}"
        self.targets["body"] = []

    def reset(self):
        self.i = self.start
        loop_reset(self)

    def forward(self, outdata):
        outdata["position"] = config.TURTLE.position()
        outdata["theta"] = config.TURTLE.heading()
        results = []
        in_loop = outdata[self.resolved_name] < self.end
        targets = self.targets["body"] if in_loop else self.targets["out"]
        if not in_loop:
            outdata.pop(self.resolved_name)
        for i, nodename in enumerate(targets):
            results.append((self.name, nodename, outdata))
        return results

    def __call__(self, data0):
        if self.valid_message(data0):
            data = dict(**data0)
            data[self.resolved_name] = data.get(self.resolved_name, self.start - 1)
            if data[self.resolved_name] < self.end:
                data[self.resolved_name] = data[self.resolved_name] + 1
            return self.forward(data)
        return []

    def to_dict(self):
        a = super().to_dict()
        a["start"] = self.start
        a["end"] = self.end
        a["varname"] = self.varname
        return a


class MoveNode(Node):
    def __init__(self, name, dist, penup, env):
        super().__init__(name, env)
        self.dist = evalf(dist, self.env)
        self.penup = evalf(penup, self.env)

    def __call__(self, data):
        if self.valid_message(data):
            if self.penup:
                config.TURTLE.penup()
            config.TURTLE.forward(self.dist)
            if self.penup:
                config.TURTLE.pendown()
            return self.forward(data)
        return []

    def to_dict(self):
        a = super().to_dict()
        a["dist"] = self.dist
        a["penup"] = self.penup
        return a


class TurnNode(Node):
    def __init__(self, name, theta, env):
        super().__init__(name, env)
        self.theta = evalf(theta, env)

    def __call__(self, data):
        if self.valid_message(data):
            config.TURTLE.left(self.theta)
            return self.forward(data)
        return []

    def to_dict(self):
        a = super().to_dict()
        a["theta"] = self.theta
        return a


class Flow(Node):  # brain hurty
    class Internal:
        def __init__(self):
            self.entries = set()
            self.exits = dict()
            self.messages = dict()

        def add_entry(self, node):
            self.entries.add(node)

        def add_exit(self, node, port):
            if port not in self.exits:
                self.exits[port] = []
                self.messages[port] = []
            self.exits[port].append(node)

        def add_message(self, data, node):
            for port, names in self.exits.items():
                if node in names:
                    self.messages[port].append(data)

        def __call__(self, data, node):
            self.add_message(data, node)
            return []

    def __init__(self, name, tp, params, opts, body, env):
        optvals = [evalf(x, env) for x in opts]
        super().__init__(name, env)
        self.env = Env(params, optvals, env)
        self.tp = tp
        self.body = body
        self.internal = Flow.Internal()
        self.params = params
        self.env["__internal__"] = self.internal

    def install(self):
        for expr in self.body:
            evalf(expr, self.env)

    def __call__(self, data):
        messages = [("__internal__", snode, data) for snode in self.internal.entries]
        while len(messages) > 0:
            msg = messages.pop(0)
            fnode, tnode, data = msg
            if tnode == "__internal__":
                self.internal(data, fnode)
            elif data:
                if self.name == "_":
                    print("Processing:", msg)
                    print("yet to process:", messages)
                    print()
                results = self.env[tnode](data)
                messages.extend(results)
        return self.forward(None)

    def forward(self, data):
        results = []
        for k in self.targets:
            for nodename in self.targets[k]:
                for xdata in self.internal.messages[k]:
                    results.append((self.name, nodename, dict(**xdata)))
            self.internal.messages[k].clear()
        return results

    def to_dict(self):
        a = super().to_dict()
        for x in self.params:
            a[x] = self.env[x]
        nodes = [a]
        for k, obj in self.env.items():
            if isinstance(obj, Node):
                info = obj.to_dict()
                if isinstance(info, list):
                    nodes.extend(info)
                elif isinstance(info, dict):
                    nodes.append(info)
                else:
                    raise TypeError("invalid nodeinfo type: " + str(type(info)))
        return nodes

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)


class FlowCreator:
    def __init__(self, tp, params, body):
        self.tp = tp
        self.params = params
        self.body = body

    def __call__(self, name, opts, env):
        flow = Flow(name, self.tp, self.params, opts, self.body, env)
        flow.install()
        return flow


def check_acyclic(flowenv, fromname, toname):
    if fromname in flowenv[toname].targets:
        return False
    for n2 in flowenv[toname].targets:
        if not check_acyclic(flowenv, fromname, n2):
            return False
    return True


def node_creator(env, name, tp, *args):
    if env.get("name"):
        raise ValueError(f"node name {name} already exists")
    if tp == "loop":
        return LoopNode(name, *args, env)
    elif tp == "move":
        return MoveNode(name, *args, env)
    elif tp == "turn":
        return TurnNode(name, *args, env)
    elif isinstance(env.find(tp)[tp], FlowCreator):
        fc = env.find(tp)[tp]
        return fc(name, args, env)
    else:
        raise TypeError(f"invalid node type {tp}")


def split_node_port(z, src=True):
    a = z.split(":")
    default = "out" if src else "in"
    if len(a) >= 2:
        return a[0], a[1]
    elif len(a) == 1:
        return a[0], default
    else:
        raise ValueError(f"invalid port {z}")


def link_creator(env, fnp, tnp):
    fnode, fport = split_node_port(fnp, src=True)
    tnode, tport = split_node_port(tnp, src=False)
    # print((fnode, fport), (tnode, tport))
    # print(env)
    # assert check_acyclic(
    #    env, fromnode, tonode
    # ), f"{fromnode} -> {tonode} causes loop in Flow"
    env[fnode].targets[fport].append(tnode)
    env[tnode].sources.append(fnode)


def create_exit(env, np, ports):
    if ports:
        port = ports[0]
    else:
        port = "out"
    node, nport = split_node_port(np)
    env["__internal__"].add_exit(node, port)
    env[node].targets[port].append("__internal__")


def run_flow(env, flowname, rest):
    d = env[flowname]
    if isinstance(d, FlowCreator):
        opts, pos, theta = rest
        flow = d("_", opts, env)
    elif isinstance(d, Flow):
        flow = d
    else:
        raise TypeError(f"cannot create flow from {flowname}")
    data = dict(position=pos, theta=theta)
    print(flow)
    flow(data)
    # print("flow output", a)
    print("DONE.")


def standard_env() -> Env:
    "An environment with some Scheme standard procedures."
    env = Env()
    env.name = "__global__"
    seed = int(time.mktime(time.gmtime())) % 10000
    random.seed(seed)
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
            "randint": random.randint,
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
    elif op == "create-node":
        name, tp, *tpargs = args
        node = node_creator(env, name, tp, *tpargs)
        env[name] = node
    elif op == "out!":
        env.outputs.append(eval(args[0]))
    elif op == "in!":
        return evalf(env.input, env)
    elif op == "define-flow":
        tp, params, body = args
        env[tp] = FlowCreator(tp, params, body)
    elif op == "create-entry":
        node = args[0]
        env["__internal__"].add_entry(node)
    elif op == "create-exit":
        np, *ports = args
        create_exit(env, np, ports)
    elif op == "create-link":
        fnp, tnp = args
        link_creator(env, fnp, tnp)
    elif op == "run-flow":
        flowname, *rest = args
        run_flow(env, flowname, rest)
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
