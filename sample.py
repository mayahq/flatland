from flatland.utils.modding import finalize
from flatland.utils.modding import initialize
from flatland.utils.primitives import Circle
from flatland.utils.primitives import Line
from flatland.utils.primitives import Rectangle
from flatland.utils.primitives import Stop

initialize()

# <> Program START

Circle((64, 64), 10)
Line((64, 64), (114, 114))
Rectangle((74, 74), length=15, breadth=22, theta=20)
Stop()

# <> Program END

finalize(fname=__file__)
