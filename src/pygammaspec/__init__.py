import importlib.resources
from os.path import join

global DEFAULT_GAMMA_DATA
DEFAULT_GAMMA_DATA = []

with importlib.resources.path("pygammaspec", "data") as path:

    with open(join(path, "gamma_data.csv"), "r") as datafile:

        for line in datafile:

            sline = line.strip("\n").split(",")
            data = [float(x) if i in [0, 1, 3] else x for i, x in enumerate(sline)]
            DEFAULT_GAMMA_DATA.append(data)
