import random
from collections import namedtuple
from jinja2 import Environment, PackageLoader, select_autoescape

GENERATE_NODEID = lambda: "%08x" % (random.randrange(16 ** 8))

CircleParams = namedtuple("CircleParams", ["x", "y", "r"])
LineParams = namedtuple("LineParams", ["c1", "c2"])
RectangleParams = namedtuple("RectangleParams", ["c1", "c2"])


def get_circles(N, xmin=-128, xmax=128, ymin=-128, ymax=128, rmin=1, rmax=50):
    return [
        CircleParams(
            random.randint(xmin, xmax),
            random.randint(ymin, ymax),
            random.randint(rmin, rmax),
        )
        for i in range(N)
    ]


def get_lines(N, xmin=-128, xmax=128, ymin=-128, ymax=128):
    return [
        LineParams(
            (random.randint(xmin, xmax), random.randint(ymin, ymax)),
            (random.randint(xmin, xmax), random.randint(ymin, ymax)),
        )
        for i in range(N)
    ]


def get_rectangles(N, xmin=-128, xmax=128, ymin=-128, ymax=128):
    return [
        RectangleParams(
            (random.randint(xmin, xmax), random.randint(ymin, ymax)),
            (random.randint(xmin, xmax), random.randint(ymin, ymax)),
        )
        for i in range(N)
    ]


def write_template(tp, num_files):
    template_map = {
        "circles": "circles_only.py.jinja",
        "lines": "lines_only.py.jinja",
        "rectangles": "rectangles_only.py.jinja",
    }
    func_map = {
        "circles": get_circles,
        "lines": get_lines,
        "rectangles": get_rectangles,
    }
    env = Environment(loader=PackageLoader("sample"), autoescape=select_autoescape())
    tmp = env.get_template(template_map[tp])

    subname = template_map[tp].split(".")[0]
    for i in range(1, num_files + 1):
        src = tmp.render(items=func_map[tp](N=random.randint(1, 25)))
        fname = f"tmp_{subname}_{GENERATE_NODEID()}.py"
        print(f"writing file {i}, {fname}")
        with open(fname, "w") as f:
            f.write(src)


def main():
    write_template("circles", 5)
    write_template("rectangles", 5)
    write_template("lines", 5)


if __name__ == "__main__":
    main()
