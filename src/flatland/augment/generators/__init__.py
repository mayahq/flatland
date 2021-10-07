from .circles_only import generate as get_circles
from .lines_only import generate as get_lines
from .rectangles_only import generate as get_rectangles
from .rotating_line1 import generate as get_rotline1
from .utils import GENERATE_ID

TEMPLATE_MAP = {
    "circles": "circles_only.py.jinja",
    "lines": "lines_only.py.jinja",
    "rectangles": "rectangles_only.py.jinja",
    "rotline1": "rotating_line1.py.jinja",
}
FUNC_MAP = {
    "circles": get_circles,
    "lines": get_lines,
    "rectangles": get_rectangles,
    "rotline1": get_rotline1,
}
