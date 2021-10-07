from flatland.utils.primitives import Line, Circle, Rectangle, Stop
from flatland.utils.modding import initialize, finalize

initialize()

# <> Program START

Circle((0, 0), 10)
Line((0, 0), (50, 50))
Rectangle((20, 20), 15, 22, 20)
Stop()

# <> Program END

finalize(fname=__file__)
