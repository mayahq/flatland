from flatland.utils.modding import finalize
from flatland.utils.modding import initialize
from flatland.utils.primitives import Circle
from flatland.utils.primitives import Line
from flatland.utils.primitives import Rectangle
from flatland.utils.primitives import Stop

initialize()

# <> Program START

Circle((0, 0), 10)
Line((0, 0), (50, 50))
Rectangle((20, 20), l=15, b=22, theta=20)
Stop()

# <> Program END

finalize(fname=__file__)
