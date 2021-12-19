# From Peter Norvig's (How to Write a (Lisp) Interpreter (in Python))
# https://norvig.com/lang.html
# https://norvig.com/lis.py
import json
import math
import operator as op
import os
import random
from datetime import datetime

import flatland.utils.config as CONFIG
from flatland.library import check_internal_dir
from flatland.utils.randomizer import GENERATE_NODEID
from flatland.utils.randomizer import get_randomizer


def isconst(x):
    if isinstance(x, int) or isinstance(x, Number):
        return True
    return False


class Symbol(str):
    pass


class Number(float):
    pass


class List(list):
    def __str__(self):
        if len(self) == 0:
            return "()"
        else:
            ans = "(" + str(self[0])
            if len(self) > 1:
                ans += " "
            ans += " ".join(str(x) for x in self[1:])
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


def validate_message(callmethod):
    def wrapper(self, data0):
        if data0.get("position", None):
            CONFIG.TURTLE.moveto(data0["position"])
            if data0.get("theta", None) is not None:
                CONFIG.TURTLE.setheading(data0["theta"])
            # python objects are by reference
            # but we need a copy of data to avoid overwrites
            # so copy the dictionary
            data = dict(**data0)
            return callmethod(self, data)
        return []

    return wrapper


class Node(Procedure):
    tp = "<unk>"

    def __init__(self, name, parent_env):
        super().__init__((), (), Env((), (), parent_env))
        self.name = name
        self.sources = []
        self.targets = {"out": []}

    def forward(self, outdata):
        outdata["position"] = CONFIG.TURTLE.position()
        outdata["theta"] = CONFIG.TURTLE.heading()
        results = []
        for i, nodename in enumerate(self.targets["out"]):
            results.append((self.name, nodename, outdata))
        return results

    @validate_message
    def __call__(self, data):
        return self.forward(data)

    @property
    def id(self):
        return self.env.name

    @property
    def parameters(self):
        raise NotImplementedError()

    def to_dict(self):
        outer = self.env.outer
        return {
            "name": self.name,
            "id": self.env.name,
            "type": self.tp,
            "scope": outer.name,
            "sources": [outer[x].id for x in self.sources],
            "targets": {k: [outer[x].id for x in v] for k, v in self.targets.items()},
        }

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)

    def __random_details__(self):
        raise NotImplementedError()


class LoopNode(Node):
    randomizer = get_randomizer("int", [1, 360])
    tp = "loop"

    def __init__(self, name, varname, start, end, parent_env):
        super().__init__(name, parent_env)
        self.start = evalf(start, self.env)
        self.end = evalf(end, self.env)
        self.varname = varname
        self.resolved_name = f"{self.env.name}:{self.varname}"
        self.targets["body"] = []

        if CONFIG.RANDOMIZE and CONFIG.RUN and parent_env.outer.name == "__global__":
            if isconst(end) and isconst(start):
                self.start = 0
                self.end = self.randomizer()
                end = self.end
                start = self.start
                print("randomizing end for", self.name, self.end)

    @property
    def parameters(self):
        return self.varname, self.start, self.end

    def forward(self, outdata):
        outdata["position"] = CONFIG.TURTLE.position()
        outdata["theta"] = CONFIG.TURTLE.heading()
        results = []
        in_loop = outdata[self.resolved_name] < self.end
        targets = self.targets["body"] if in_loop else self.targets["out"]
        if not in_loop:
            outdata.pop(self.resolved_name)
        for i, nodename in enumerate(targets):
            results.append((self.name, nodename, outdata))
        return results

    @validate_message
    def __call__(self, data):
        data[self.resolved_name] = data.get(self.resolved_name, self.start - 1)
        if data[self.resolved_name] < self.end:
            data[self.resolved_name] = data[self.resolved_name] + 1
        return self.forward(data)

    def to_dict(self):
        a = super().to_dict()
        a["start"] = self.start
        a["end"] = self.end
        a["varname"] = self.varname
        return a

    def __random_details__(self):
        return {
            "function": self.tp,
            "properties": ["start", "end", "varname"],
            "path": None,
            "rules": {"end": self.randomizer.to_dict()},
        }


class MoveNode(Node):
    dist_randomizer = get_randomizer("float", [0, 60])
    penup_randomizer = get_randomizer("bool", 0.1)
    tp = "move"

    def __init__(self, name, dist, penup, parent_env):
        super().__init__(name, parent_env)
        self.dist = evalf(dist, self.env)
        self.penup = bool(evalf(penup, self.env))

        if CONFIG.RANDOMIZE and CONFIG.RUN and parent_env.outer.name == "__global__":
            if isconst(dist):
                self.dist = self.dist_randomizer()
                print("randomizing dist for", self.name, self.dist)
                dist = self.dist
            if isconst(penup):
                self.penup = self.penup_randomizer()
                print("randomizing penup for", self.name, self.penup)
                penup = self.penup

    @validate_message
    def __call__(self, data):
        if self.penup:
            CONFIG.TURTLE.penup()
        CONFIG.TURTLE.forward(self.dist)
        if self.penup:
            CONFIG.TURTLE.pendown()
        return self.forward(data)

    @property
    def parameters(self):
        return self.dist, int(self.penup)

    def to_dict(self):
        a = super().to_dict()
        a["dist"] = self.dist
        a["penup"] = self.penup
        return a

    def __random_details__(self):
        return {
            "function": self.tp,
            "properties": ["dist", "penup"],
            "path": None,
            "rules": {
                "dist": self.dist_randomizer.to_dict(),
                "penup": self.penup_randomizer.to_dict(),
            },
        }


class TurnNode(Node):
    randomizer = get_randomizer("int", [0, 360])
    tp = "turn"

    def __init__(self, name, theta, parent_env):
        super().__init__(name, parent_env)
        self.theta = evalf(theta, self.env)
        if CONFIG.RANDOMIZE and CONFIG.RUN and parent_env.outer.name == "__global__":
            if isconst(theta):
                self.theta = self.randomizer()
                print("randomizing theta for", self.name, self.theta)
                theta = self.theta

    @validate_message
    def __call__(self, data):
        CONFIG.TURTLE.left(self.theta)
        return self.forward(data)

    @property
    def parameters(self):
        return (self.theta,)

    def to_dict(self):
        a = super().to_dict()
        a["theta"] = self.theta
        return a

    @classmethod
    def __random_details__(self):
        return {
            "function": self.tp,
            "properties": ["theta"],
            "path": None,
            "rules": {"theta": self.randomizer.to_dict()},
        }


class Flow(Node):  # brain hurty
    tp = "flow"

    class Internal:
        def __init__(self, _id):
            self.entries = set()
            self.exits = dict()
            self.messages = dict()
            self.id = _id

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

        def to_dict(self, env):
            return {
                "entries": list(env[x].id for x in self.entries),
                "exits": {k: [env[x].id for x in v] for k, v in self.exits.items()},
            }

        def clear(self):
            for k, v in self.messages.items():
                v.clear()

    def __init__(self, name, creator, filename, tp, params, opts, body, parent_env):
        super().__init__(name, parent_env)
        optvals = [evalf(x, self.env) for x in opts]
        self.env.update(zip(params, optvals))
        self.creator = creator
        self.filename = filename
        self.flowtype = tp
        self.body = body
        self.internal = Flow.Internal(self.id)
        self.params = params
        self.env["__internal__"] = self.internal

    @property
    def parameters(self):
        return tuple(self.env[k] for k in self.params)

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
                results = self.env[tnode](data)
                messages.extend(results)
            if self.env.outer.name == "__global__":
                print("Processing:", msg)
                print("yet to process:", messages)
                print()
        return self.forward(None)

    def forward(self, data):
        results = []
        for k in self.targets:
            for nodename in self.targets[k]:
                for xdata in self.internal.messages[k]:
                    results.append((self.name, nodename, dict(**xdata)))
        self.internal.clear()
        return results

    def to_dict(self):
        a = super().to_dict()
        a["__internal__"] = self.internal.to_dict(self.env)
        a["params"] = {x: self.env[x] for x in self.params}
        a["flowtype"] = self.flowtype
        a["filename"] = self.filename
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

    def __random_details__(self):
        return self.creator.__random_details__()


class FlowCreator:
    def __init__(self, tp, params, randoms, body, filename):
        self.flowtype = tp
        self.params = list(params)
        self.randoms = randoms
        self.rfuncs = {k: get_randomizer(v) for k, v in randoms.items()}
        self.body = body
        self.filename = filename

    def __call__(self, name, opts, parent_env):
        if CONFIG.RANDOMIZE and self.randoms:
            new_opts = []
            for i, x in enumerate(opts):
                if not isconst(x):
                    new_opts.append(x)
                else:
                    opt = self.rfuncs[self.params[i]]()
                    print(f"randomizing {self.params[i]} for {name} {opt}")
                    new_opts.append(opt)
        else:
            new_opts = opts
        flow = Flow(
            name,
            self,
            self.filename,
            self.flowtype,
            self.params,
            new_opts,
            self.body,
            parent_env,
        )
        flow.install()
        return flow

    def __random_details__(self):
        return {
            "function": self.flowtype,
            "properties": self.params,
            "path": self.filename,
            "rules": {k: v.to_dict() for k, v in self.rfuncs.items()},
        }


def check_acyclic(flowenv, fromname, toname):
    if fromname in flowenv[toname].targets:
        return False
    for n2 in flowenv[toname].targets:
        if not check_acyclic(flowenv, fromname, n2):
            return False
    return True


def node_creator(env, name, tp, *args):
    if env.get(name):
        raise ValueError(f"node name {name} already exists")
    if tp == "loop":
        node = LoopNode(name, *args, env)
    elif tp == "move":
        node = MoveNode(name, *args, env)
    elif tp == "turn":
        node = TurnNode(name, *args, env)
    elif isinstance(env.find(tp)[tp], FlowCreator):
        fc = env.find(tp)[tp]
        node = fc(name, args, env)
    else:
        raise TypeError(f"invalid node type {tp}")

    return node


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
        bname = os.path.basename(d.filename)
        flowname = f"__{bname}:{d.flowtype}__"
        flow = d(flowname, opts, env)
        env[flow.name] = flow
    elif isinstance(d, Flow):
        flow = d
    else:
        raise TypeError(f"cannot create flow from {flowname}")

    if CONFIG.RUN and CONFIG.RANDOMIZE:
        pos = (pos[0] + MoveNode.dist_randomizer(), pos[1] + MoveNode.dist_randomizer())
        pos = (pos[0] % 128, pos[1] % 128)
        theta = TurnNode.randomizer()

    data = dict(position=pos, theta=theta)
    if CONFIG.RUN:
        flow(data)
        # print(flow)
        print("DONE.")
    data["id"] = "__START__"
    data["type"] = "info"
    data["targets"] = dict(out=[flow.id])
    data["sources"] = []
    data["scope"] = "__global__"
    data["name"] = "START"
    fdata = flow.to_dict()
    for x in fdata:
        if x["name"] == "_":
            x["sources"].append(data["id"])
    fdata.insert(0, data)
    return fdata


def resolve_scope(fdata):
    flow = {x["id"]: x for x in fdata}
    subflows = [x for x in fdata if x["type"] == "flow"]
    for sf in subflows:
        # for every subflow sf

        # we need to connect its internal entry nodes to its sources
        for dst_id in sf["__internal__"]["entries"]:
            dst = flow[dst_id]
            dst["sources"].remove(sf["id"])
            for src_id in sf["sources"]:
                src = flow[src_id]
                for k, v in src["targets"].items():
                    # a particular node can only be in one target location
                    # so check and break if found
                    if sf["id"] in v:
                        v.remove(sf["id"])
                        v.append(dst_id)
                        break
                dst["sources"].append(src_id)

        # we need to connect its internal exit nodes to its targets
        for k, v in sf["__internal__"]["exits"].items():
            for src_id in v:
                src = flow[src_id]
                src["targets"][k].remove(sf["id"])
                for dst_id in sf["targets"][k]:
                    dst = flow[dst_id]
                    dst["sources"].remove(sf["id"])
                    dst["sources"].append(src_id)
                    src["targets"][k].append(dst_id)

        # we need to change the scope for all its internal nodes
        # to the parent scope
        cur_scope = sf["id"]
        par_scope = sf["scope"]
        for v in flow.values():
            if v["scope"] == cur_scope:
                v["scope"] = par_scope

        # now the subflow node is no longer needed,
        # since all its internals have been resolved
        flow.pop(sf["id"])

    # if all subflows have been resolved
    # every node is now in the global scope,
    # and has a unique ID to distinguish itself
    for k, v in flow.items():
        assert v.pop("scope") == "__global__"
        v.pop("name")
        # source information is now redundant, because
        # targets define the entire flow anyway
        v.pop("sources")
    return flow


def include_file(filename, env):
    assert filename.startswith('"') and filename.endswith(
        '"'
    ), "Filename needs to be a double-quoted string"
    filename = filename.replace('"', "")
    globl = env.find("+")
    is_internal, fullname = check_internal_dir(filename)

    if is_internal:
        localname = filename
    else:
        localname = None

    if filename not in env.includes:
        from flatland.lang.run import main as runner

        with open(fullname) as f:
            subprogram = f.read()

        t = CONFIG.RUN
        CONFIG.RUN = False
        runner(subprogram, filename, globl, localname)
        CONFIG.RUN = t


def standard_env() -> Env:
    "An environment with some Scheme standard procedures."
    env = Env()
    env.name = "__global__"
    env.seed = datetime.now()
    env.includes = set()
    random.seed(env.seed)
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


def evalf(x, env):  # noqa: C901
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
    elif op == "#include":
        filename = args[0]
        include_file(filename, env)
    elif op == "if":  # conditional
        (test, conseq, alt) = args
        exp = conseq if evalf(test, env) else alt
        return evalf(exp, env)
    elif op == "create-node":
        name, tp, *tpargs = args
        node = node_creator(env, name, tp, *tpargs)
        env[name] = node
        if CONFIG.RANDOMIZE and CONFIG.RUN:
            x2 = List([op, name, tp, *node.parameters])
            x.clear()
            x.extend(x2)
    elif op == "define-flow":
        tp, params, randoms, body = args
        filename = env.find("__file__")["__file__"]
        rddict = dict()
        for rdp in randoms:
            parname, (rfunc, rparams) = rdp
            rparams = [evalf(bd, env) for bd in rparams]
            rddict[parname] = (rfunc, rparams)
        env[tp] = FlowCreator(tp, params, rddict, body, filename)
        if CONFIG.RANDOMIZE and CONFIG.RUN:
            x2 = List([op, tp, params, List(), body])
            x.clear()
            x.extend(x2)

    elif op == "create-entry":
        node = args[0]
        env["__internal__"].add_entry(node)
        env[node].sources.append("__internal__")
    elif op == "create-exit":
        np, *ports = args
        create_exit(env, np, ports)
    elif op == "create-link":
        fnp, tnp = args
        link_creator(env, fnp, tnp)
    elif op == "run-flow":
        flowname, *rest = args
        return run_flow(env, flowname, rest)
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
