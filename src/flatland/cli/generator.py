import argparse
import os
import sys

from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2 import select_autoescape

from flatland.augment import FUNC_MAP
from flatland.augment import GENERATE_ID
from flatland.augment import TEMPLATE_MAP

KEYS = list(TEMPLATE_MAP.keys())


def check_domain(domain):
    if domain == "all":
        return KEYS
    elif domain in KEYS:
        return [domain]
    raise ValueError("invalid domain")


def check_dir(path):
    if os.path.exists(path) and os.path.isdir(path):
        return path
    raise NotADirectoryError(path)


def check_compl(val):
    if val is None:
        return val
    v2 = int(val)
    if v2 > 0:
        return v2
    raise ValueError("invalid complexity")


def write_template(tp, num_files, N=None, should_exec=False):
    env = Environment(
        loader=PackageLoader("flatland.augment"), autoescape=select_autoescape()
    )
    tmp = env.get_template(TEMPLATE_MAP[tp])
    func = FUNC_MAP[tp]

    for i in range(1, num_files + 1):
        params = func(N)
        fname = params["filename"]
        src = tmp.render(**params)
        print(f"Writing file {i}/{num_files}: {fname}", end="\r")
        with open(fname, "w") as f:
            f.write(src)
        if should_exec:
            exec(src, dict(), dict())

    print("")


def main():
    keys = list(TEMPLATE_MAP.keys())
    parser = argparse.ArgumentParser(
        prog="flatland-generate",
        description="generate programs for the flatland dataset",
        epilog="available domains:\n\t" + "\n\t".join(keys),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-d",
        "--domain",
        default="all",
        type=check_domain,
        help="domain from which programs should be generated",
    )
    parser.add_argument(
        "-n",
        "--num-files",
        default=1,
        type=int,
        help="number of files to generate per domain",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="./outputs",
        type=check_dir,
        help="Output directory to store generated data",
    )
    parser.add_argument(
        "-N",
        "--complexity",
        default=None,
        type=check_compl,
        help="complexity of generated image (randomized if None)",
    )
    parser.add_argument(
        "-x",
        "--also-exec",
        dest="should_exec",
        default=False,
        action="store_true",
        help="Execute each generated program",
    )

    d = parser.parse_args()
    os.chdir(d.output_dir)
    for domain in d.domain:
        write_template(domain, d.num_files, N=d.complexity, should_exec=d.should_exec)


if __name__ == "__main__":
    main()
