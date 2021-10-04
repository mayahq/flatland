import random
from collections import namedtuple
from jinja2 import Environment, PackageLoader, select_autoescape

GENERATE_NODEID = lambda: "%08x" % (random.randrange(16 ** 8))

CircleParams = namedtuple("CircleParams", ["x", "y", "r"])
LineParams = namedtuple("LineParams", ["c1", "c2"])
RectangleParams = namedtuple("RectangleParams", ["c1", "c2"])
RotLine1Params = namedtuple("RotLine1Params", ["start", "N", "step", "theta"])


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


def get_rotmove1(N, xmin=-48, xmax=48, ymin=-48, ymax=48):
    return RotLine1Params(
        start=(random.randint(xmin, xmax), random.randint(ymin, ymax)),
        N=random.randint(5, 128),
        step=random.randint(5, 128),
        theta=random.randint(0, 180),
    )


def write_template(tp, num_files):
    template_map = {
        "circles": "circles_only.py.jinja",
        "lines": "lines_only.py.jinja",
        "rectangles": "rectangles_only.py.jinja",
        "rotmove1": "rotating_line1.py.jinja",
    }
    func_map = {
        "circles": get_circles,
        "lines": get_lines,
        "rectangles": get_rectangles,
        "rotmove1": get_rotmove1,
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
    write_template("circles", 1)
    write_template("rectangles", 1)
    write_template("lines", 1)
    write_template("rotmove1", 10)


if __name__ == "__main__":
    main()
