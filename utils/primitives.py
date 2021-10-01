import utils.config as config

def Circle(coord, r, turtle=None):
    if turtle is None:
        turtle = config.TURTLE
    turtle.moveto(*coord)
    turtle.circle(r)

def Line(coord1, coord2, turtle=None):
    if turtle is None:
        turtle = config.TURTLE
    turtle.moveto(*coord1)
    turtle.goto(*coord2)

def Rectangle(coord1, coord2, turtle=None):
    if turtle is None:
        turtle = config.TURTLE
    turtle.moveto(*coord1)
    turtle.goto(coord1[0], coord2[1])
    turtle.goto(coord2[0], coord2[1])
    turtle.goto(coord2[0], coord1[1])
    turtle.goto(coord1[0], coord1[1])

def Stop(turtle=None):
    if turtle is None:
        turtle = config.TURTLE

def Move(n, turtle=None):
    if turtle is None:
        turtle = config.TURTLE
    turtle.forward(n)

def Turn(degrees, turtle=None):
    if turtle is None:
        turtle = config.TURTLE
    turtle.left(degrees)
