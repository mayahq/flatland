import json
import os
import turtle
from io import BytesIO
from tkinter import Canvas
from tkinter import Tk
from turtle import RawTurtle as BaseTurtle
from turtle import TurtleScreen as BaseScreen

from PIL import Image

import flatland.utils.config as CONFIG


class MyScreen(BaseScreen):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.tracer(1, 0)

    def setworldcoordinates(self, llx, lly, urx, ury):
        """Set up a user defined coordinate-system.
        Arguments:
        llx -- a number, x-coordinate of lower left corner of canvas
        lly -- a number, y-coordinate of lower left corner of canvas
        urx -- a number, x-coordinate of upper right corner of canvas
        ury -- a number, y-coordinate of upper right corner of canvas
        Set up user coodinat-system and switch to mode 'world' if necessary.
        This performs a screen.reset. If mode 'world' is already active,
        all drawings are redrawn according to the new coordinates.
        But ATTENTION: in user-defined coordinatesystems angles may appear
        distorted. (see Screen.mode())
        Example (for a TurtleScreen instance named screen):
        >>> screen.setworldcoordinates(-10,-0.5,50,1.5)
        >>> for _ in range(36):
        ...     left(10)
        ...     forward(0.5)
        """
        if self.mode() != "world":
            self.mode("world")
        xspan = float(urx - llx)
        yspan = float(ury - lly)
        wx, wy = self._window_size()
        self.screensize(int(wx) - 20, int(wy) - 20)
        oldxscale, oldyscale = self.xscale, self.yscale
        self.xscale = self.canvwidth / xspan
        self.yscale = self.canvheight / yspan
        srx1 = llx * self.xscale
        sry1 = -ury * self.yscale
        srx2 = self.canvwidth + srx1
        sry2 = self.canvheight + sry1
        self._setscrollregion(srx1, sry1, srx2, sry2)
        self._rescale(self.xscale / oldxscale, self.yscale / oldyscale)
        self.update()


class MyTurtle(BaseTurtle):
    def __init__(self, screen):
        super().__init__(screen)
        self.speed(0)
        self.width(1)
        self.hideturtle()
        self.assembly = []
        self.cur_id = 0

    def moveto(self, x, y=None):
        self.penup()
        self.goto(x, y)
        self.pendown()

    def moveby(self, x=0, y=0):
        sx, sy = self.position()
        self.penup()
        self.goto(sx + x, sy + y)
        self.pendown()

    def clear(self):
        BaseTurtle.clear(self)
        self.assembly = []
        self.cur_id = 0

    def updatelog(self, type_, **kwargs):
        obj = {"id": self.cur_id, "type": type_}
        obj.update(kwargs)
        self.cur_id += 1
        self.assembly.append(obj)


def initialize():
    if not CONFIG.inited:
        CONFIG.inited = True
        if CONFIG.SHOWTURTLE:
            CONFIG.TURTLE = turtle.Turtle()
            CONFIG.TURTLE.moveto = lambda *args: MyTurtle.moveto(CONFIG.TURTLE, *args)
            CONFIG.TURTLE.moveby = lambda *args: MyTurtle.moveby(CONFIG.TURTLE, *args)
            CONFIG.TURTLE.updatelog = lambda *args: MyTurtle.updatelog(
                CONFIG.TURTLE, *args
            )
            CONFIG.TURTLE.clear = lambda *args: MyTurtle.clear(CONFIG.TURTLE, *args)
            CONFIG.SCREEN = CONFIG.TURTLE.getscreen()
            CONFIG.SCREEN.tracer(1, 0)
            CONFIG.SCREEN.setworldcoordinates(0, 0, 128, 128)
            CONFIG.CANVAS = CONFIG.SCREEN.getcanvas()
        else:
            CONFIG.ROOT = Tk()
            CONFIG.ROOT.overrideredirect(1)
            CONFIG.ROOT.withdraw()

            CONFIG.CANVAS = Canvas(master=CONFIG.ROOT, width=256, height=256)
            CONFIG.CANVAS.configure(scrollregion=(0, 0, 256, 256))
            BaseScreen._canvas = CONFIG.CANVAS
            BaseScreen._root = CONFIG.ROOT
            CONFIG.SCREEN = MyScreen(CONFIG.CANVAS)
            CONFIG.SCREEN.setworldcoordinates(0, 0, 128, 128)
            CONFIG.TURTLE = MyTurtle(CONFIG.SCREEN)

            assert CONFIG.TURTLE.getscreen() == CONFIG.SCREEN
            assert CONFIG.SCREEN.getcanvas() == CONFIG.CANVAS


def finalize(fname):
    if CONFIG.SKIPIMAGE:
        return
    if CONFIG.SHOWTURTLE:
        input("Press Enter to exit")
    turtle = CONFIG.TURTLE
    rawname = fname.split(".")[0]
    h, w = 256, 256
    ps = (
        turtle.getscreen()
        .getcanvas()
        .postscript(
            colormode="color",
            height=h,
            width=w,
            y=-h,
        )
    )
    out = BytesIO(ps.encode("utf-8"))
    img = Image.open(out).convert("RGBA").resize((256, 256))
    img.save(f"{rawname}.png", lossless=True)
    turtle.clear()
