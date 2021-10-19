from .binary import edge_indicator as ei_eq
from .binary import node_weighter as nw_eq
from .constants import LENIENCY
from .euclidean import edge_indicator as ei_2d
from .euclidean import node_weighter as nw_2d
from .inv_euclidean import edge_indicator as ei_2di
from .inv_euclidean import node_weighter as nw_2di
from .inv_taxicab import edge_indicator as ei_1di
from .inv_taxicab import node_weighter as nw_1di
from .recursive import edge_indicator as ei_rec
from .recursive import node_weighter as nw_rec
from .taxicab import edge_indicator as ei_1d
from .taxicab import node_weighter as nw_1d

FUNCTION_MAP = {
    "euclidean": (nw_2d, ei_2d),
    "taxicab": (nw_1d, ei_1d),
    "binary": (nw_eq, ei_eq),
    "inverse2d": (nw_2di, ei_2di),
    "inverse1d": (nw_1di, ei_1di),
    "recursive": (nw_rec, ei_rec),
}
