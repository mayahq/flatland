import glob
import json
import os
from dataclasses import asdict
from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional

import flatland.utils.config as CONFIG
from flatland.lang.primitives import Flow
from flatland.lang.primitives import Node
from flatland.lang.primitives import standard_env
from flatland.lang.run import main as runner


@dataclass
class Primitive:
    function: str
    properties: List[str]
    path: Optional[str]
    rules: Dict[str, Dict]


class Library:
    def __init__(self):
        self.existing = []
        self.num_primitives = 0
        self.primitives = dict()
        self.connections = dict()

    def add_primitive(self, node: Node):
        if isinstance(node, Flow):
            tp = node.flowtype
        else:
            tp = node.tp

        if tp in self.existing:
            return tp

        self.existing.append(tp)
        self.primitives[self.num_primitives] = Primitive(**node.__random_details__())
        self.connections[self.num_primitives] = set()
        self.num_primitives += 1

        if isinstance(node, Flow):
            for k, v in node.env.items():
                if isinstance(v, Node):
                    vtp = self.add_primitive(v)
                    self.add_connection(vtp, tp)

        return tp

    def add_connection(self, tp1, tp2):
        ind1 = self.existing.index(tp1)
        ind2 = self.existing.index(tp2)
        self.connections[ind1].add(ind2)

    def to_dict(self):
        return {
            "primitives": self.primitives,
            "connections": self.connections,
        }

    def __repr__(self):
        return json.dumps(self, indent=4, cls=Encoder)


class Encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Library):
            return o.to_dict()
        elif isinstance(o, Primitive):
            return asdict(o)
        elif isinstance(o, set):
            return list(o)
        return super().default(o)


def create_library(directory):
    lib = Library()
    files = glob.glob(os.path.join(directory, "*.fbp"))

    env = standard_env()
    CONFIG.RANDOMIZE = False
    CONFIG.RUN = False
    for file in files:
        with open(file) as f:
            prog = f.read()
        runner(prog, file, env=env)

    for v in env.values():
        if isinstance(v, Node):
            lib.add_primitive(v)

    return lib
