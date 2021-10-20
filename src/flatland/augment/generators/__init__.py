from .circle_in_box import generate as get_circle_in_box
from .circles_only import generate as get_circles
from .lines_only import generate as get_lines
from .rectangles_only import generate as get_rectangles
from .rotating_line1 import generate as get_rotline1
from .stickfigure1 import generate as get_stickfigure1
from .utils import GENERATE_ID

TEMPLATE_MAP = {
    "circles": "circles_only.py.jinja",
    "lines": "lines_only.py.jinja",
    "rectangles": "rectangles_only.py.jinja",
    "rotline1": "rotating_line1.py.jinja",
    "stickfigure1": "stickfigure1.py.jinja",
    "circle_in_box": "circle_in_box.py.jinja",
}
FUNC_MAP = {
    "circles": get_circles,
    "lines": get_lines,
    "rectangles": get_rectangles,
    "rotline1": get_rotline1,
    "stickfigure1": get_stickfigure1,
    "circle_in_box": get_circle_in_box,
}
