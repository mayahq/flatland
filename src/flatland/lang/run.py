# From Peter Norvig's
# (How to Write a (Lisp) Interpreter (in Python))
# https://norvig.com/lispy.html
# https://norvig.com/lis.py
import json
import os

from flatland.lang.fbp import parse as parse_fbp
from flatland.lang.lisp import parse as parse_lisp
from flatland.lang.primitives import evalf
from flatland.lang.primitives import standard_env
from flatland.utils.modding import finalize
from flatland.utils.modding import initialize


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


def parse_flow(program: str, filename: str):
    ext = os.path.splitext(filename)[1]
    if ".fbp" in ext:
        expr = parse_fbp(program.split("\n"))
    elif ".lisp" in ext:
        expr = parse_lisp(program)
    else:
        raise ValueError(f"Invalid file extension {ext}, expecting .fbp or .lisp")
    return expr


def exec_flow(expr, filename: str, env=None, run=True):
    initialize()
    if env is None:
        env = standard_env()

    env.includes.add(filename)
    t = env.get("__file__")
    env["__file__"] = filename

    # print(f"evaluating {filename}")
    flowdata = evalf(expr, env, run)
    if run:  # drawing happened
        finalize(filename)
    if t:
        env["__file__"] = t

    return flowdata


def main(program: str, filename: str, env=None, run=True):
    filename = os.path.abspath(filename)
    with CurrentDir(filename):
        expr = parse_flow(program, filename)
        flowdata = exec_flow(expr, filename, env, run)
        return flowdata
