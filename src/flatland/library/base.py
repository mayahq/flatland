import glob
import json
import os
import random
from dataclasses import asdict
from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional

import flatland.utils.config as CONFIG
from flatland.augment import single_file
from flatland.lang.primitives import Flow
from flatland.lang.primitives import Node
from flatland.lang.primitives import standard_env
from flatland.lang.run import main as runner
from flatland.utils.misc import check_dir


@dataclass
class Primitive:
    function: str
    properties: List[str]
    path: Optional[str]
    rules: Dict[str, Dict]


class Library:
    def __init__(self, directory):
        directory = check_dir(directory)
        self.files = glob.glob(os.path.join(directory, "*.fbp")) + glob.glob(
            os.path.join(directory, "*.lisp")
        )
        self.existing_primitives = []
        self.num_primitives = 0
        self.primitives = dict()
        self.connections = dict()

    def add_primitive(self, node: Node):
        if isinstance(node, Flow):
            tp = node.flowtype
        else:
            tp = node.tp

        if tp in self.existing_primitives:
            return tp

        self.existing_primitives.append(tp)
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
        ind1 = self.existing_primitives.index(tp1)
        ind2 = self.existing_primitives.index(tp2)
        self.connections[ind1].add(ind2)

    def to_dict(self):
        return {
            "primitives": self.primitives,
            "connections": self.connections,
        }

    def __repr__(self):
        return json.dumps(self, indent=4, cls=Encoder)

    def fill_dependencies(self):
        env = standard_env()
        CONFIG.RANDOMIZE = False
        CONFIG.RUN = False
        for file in self.files:
            with open(file) as f:
                prog = f.read()
            runner(prog, file, env=env)

        for v in env.values():
            if isinstance(v, Node):
                self.add_primitive(v)

    def _generate_programs(self, N, output_dir):
        rd, run = CONFIG.RANDOMIZE, CONFIG.RUN
        for i in range(N):
            file = random.choice(self.files)
            with open(file) as f:
                prog = f.read()
            single_file(prog, file, 1, output_dir)
        CONFIG.RANDOMIZE, CONFIG.RUN = rd, run


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
    lib = Library(directory)
    lib.fill_dependencies()
    return lib
