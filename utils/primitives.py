import utils.config as config

# only Circle, Line, and Turn are the actual primitives


def Circle(coord, r, turtle=None):
    if turtle is None:
        turtle = config.TURTLE
    turtle.moveto(*coord)
    turtle.moveby(0, -r)
    turtle.circle(r)
    turtle.updatelog(**{"type_": "circle", "center": list(coord), "radius": r})


def Line(coord1, coord2, turtle=None):
    if turtle is None:
        turtle = config.TURTLE
    turtle.moveto(*coord1)
    turtle.goto(*coord2)
    turtle.updatelog(**{"type_": "line", "start": list(coord1), "end": list(coord2)})


def Turn(degrees, turtle=None):
    if turtle is None:
        turtle = config.TURTLE
    turtle.left(degrees)

# Move is equivalent to Line
def Move(n, turtle=None):
    if turtle is None:
        turtle = config.TURTLE
    startpos = turtle.position()
    turtle.forward(n)
    endpos = turtle.position()
    turtle.updatelog(**{"type_": "line", "start": list(startpos), "end": list(endpos)})


def Stop(turtle=None):
    if turtle is None:
        turtle = config.TURTLE


def Warp(coord1, turtle=None):
    if turtle is None:
        turtle = config.TURTLE
    turtle.moveto(*coord1)


def Rectangle(coord1, l, b, theta=0, turtle=None):
    if turtle is None:
        turtle = config.TURTLE
    turtle.moveto(*coord1)
    turtle.setheading(theta)
    Move(l)
    Turn(90)
    Move(b)
    Turn(90)
    Move(l)
    Turn(90)
    Move(b)
