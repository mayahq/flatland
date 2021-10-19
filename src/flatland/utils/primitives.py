import flatland.utils.config as config


def Circle(coord, r, theta=360, turtle=None):
    if turtle is None:
        turtle = config.TURTLE
    turtle.moveto(*coord)
    turtle.moveby(0, -r)
    turtle.circle(r, theta)
    turtle.moveto(*coord)
    turtle.updatelog(
        **{
            "type_": "circle",
            "center": {"x": coord[0], "y": coord[1]},
            "radius": r,
            "theta": theta,
        }
    )


def Line(coord1, coord2, turtle=None):
    if turtle is None:
        turtle = config.TURTLE
    turtle.moveto(*coord1)
    turtle.goto(*coord2)
    turtle.updatelog(
        **{
            "type_": "line",
            "start": {"x": coord1[0], "y": coord1[1]},
            "end": {"x": coord2[0], "y": coord2[1]},
        }
    )


def Turn(degrees, turtle=None):
    if turtle is None:
        turtle = config.TURTLE
    turtle.left(degrees)


# Move is equivalent to Line
def Move(n, turtle=None):
    if turtle is None:
        turtle = config.TURTLE
    coord1 = turtle.position()
    turtle.forward(n)
    coord2 = turtle.position()
    turtle.updatelog(
        **{
            "type_": "line",
            "start": {"x": coord1[0], "y": coord1[1]},
            "end": {"x": coord2[0], "y": coord2[1]},
        }
    )


def Stop(turtle=None):
    if turtle is None:
        turtle = config.TURTLE


def Warp(coord1, turtle=None):
    if turtle is None:
        turtle = config.TURTLE
    turtle.moveto(*coord1)


def Rectangle(coord1, length, breadth, theta=0, turtle=None):
    if turtle is None:
        turtle = config.TURTLE
    turtle.moveto(*coord1)
    turtle.setheading(theta)
    Move(length)
    Turn(90)
    Move(breadth)
    Turn(90)
    Move(length)
    Turn(90)
    Move(breadth)


def StickFigure(head, torso1, arms, torso2, legs, turtle=None):
    if turtle is None:
        turtle = config.TURTLE
    Circle((head["x"], head["y"]), head["r"])
    Warp((head["x"], head["y"] - head["r"]))
    Turn(torso1["theta"])
    Move(torso1["length"])
    curpos = turtle.position()
    turtle.setheading(0)
    Turn(arms["theta"])
    Move(arms["length"])
    Warp(curpos)
    Turn(-2 * arms["theta"])
    Move(arms["length"])
    Warp(curpos)
    turtle.setheading(0)
    Turn(torso2["theta"])
    Move(torso2["length"])
    curpos = turtle.position()
    turtle.setheading(0)
    Turn(legs["theta"])
    Move(legs["length"])
    Warp(curpos)
    Turn(-2 * legs["theta"])
    Move(legs["length"])
    Warp(curpos)
    turtle.setheading(0)
