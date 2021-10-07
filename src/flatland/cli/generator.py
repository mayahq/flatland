from jinja2 import Environment, PackageLoader, select_autoescape


def write_template(tp, num_files):
    env = Environment(loader=PackageLoader("flatland.augment"), autoescape=select_autoescape())
    tmp = env.get_template(template_map[tp])

    subname = template_map[tp].split(".")[0]
    for i in range(1, num_files + 1):
        src = tmp.render(items=func_map[tp](N=random.randint(1, 15)))
        fname = f"tmp_{subname}_{GENERATE_NODEID()}.py"
        print(f"writing file {i}, {fname}")
        with open(fname, "w") as f:
            f.write(src)


def main():
    write_template("circles", 5)
    write_template("rectangles", 5)
    write_template("lines", 5)
    write_template("rotmove1", 5)


if __name__ == "__main__":
    main()
