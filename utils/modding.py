from tkinter import Tk, Canvas
from turtle import TurtleScreen as BaseScreen, RawTurtle as BaseTurtle
from PIL import Image
from io import BytesIO

import utils.config as config


class Screen(BaseScreen):
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


class Turtle(BaseTurtle):
    def __init__(self, screen):
        super().__init__(screen)
        self.speed(0)
        self.width(2)
        self.hideturtle()

    def moveto(self, x, y=None):
        self.penup()
        self.goto(x, y)
        self.pendown()

    def moveby(self, x=0, y=0):
        self.penup()
        self.goto(self.x() + x, self.y() + y)
        self.pendown()


def initialize():
    if not config.inited:
        config.inited = True
        config.ROOT = Tk()
        config.ROOT.overrideredirect(1)
        config.ROOT.withdraw()

        config.CANVAS = Canvas(master=config.ROOT, width=256, height=256)
        config.CANVAS.configure(scrollregion=(-128, -128, 128, 128))
        BaseScreen._canvas = config.CANVAS
        BaseScreen._root = config.ROOT
        config.SCREEN = Screen(config.CANVAS)
        config.SCREEN.setworldcoordinates(-64, -64, 64, 64)
        config.TURTLE = Turtle(config.SCREEN)

        assert config.TURTLE.getscreen() == config.SCREEN
        assert config.SCREEN.getcanvas() == config.CANVAS


def finalize(fname):
    rawname = fname.split(".")[0]
    h, w = 512, 512
    ps = config.CANVAS.postscript(
        colormode="color", height=h, width=w, x=-h/2, y=-w/2
    )
    out = BytesIO(ps.encode("utf-8"))
    img = Image.open(out).convert("RGBA").resize((256,256))
    img.save(f"{rawname}.png", lossless=True)
