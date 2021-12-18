# create randomized versions of a single program,
# provided as string input
import json
import os

import flatland.utils.config as CONFIG
from flatland.lang.run import main as runner
from flatland.utils.modding import finalize
from flatland.utils.modding import initialize
from flatland.utils.randomizer import GENERATE_FILEID


def main(program: str, filename: str, num_samples: int, outdir: str):
    outdir = os.path.abspath(outdir)
    CONFIG.RANDOMIZE = True
    CONFIG.RUN = True
    CONFIG.SHOWTURTLE = False

    initialize()
    basename = os.path.splitext(os.path.basename(filename))[0]
    for i in range(num_samples):
        newname = f"{basename}-{GENERATE_FILEID()}"
        CONFIG.SKIPIMAGE = True
        expr, info = runner(program, filename, env=None)

        newpath = os.path.join(outdir, newname)
        with open(newpath + ".lisp", "w") as f2:
            f2.write(str(expr))

        with open(newpath + ".json", "w") as f3:
            json.dump(info, f3, indent=4)

        CONFIG.SKIPIMAGE = False
        finalize(newpath + ".lisp")
