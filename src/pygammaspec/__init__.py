
from os.path import join, dirname

global DEFAULT_GAMMA_DATA
DEFAULT_GAMMA_DATA = []

gamma_datafile_path = join(dirname(__file__), 'data', 'gamma_data.csv')

with open(gamma_datafile_path, "r") as datafile:

        for line in datafile:

            sline = line.strip("\n").split(", ")
            data = [float(x) if i in [0, 1, 3] else x for i, x in enumerate(sline)]
            DEFAULT_GAMMA_DATA.append(data)


global DEFAULT_X_RAY_DATA
DEFAULT_X_RAY_DATA = []

x_ray_datafile_path = join(dirname(__file__), 'data', 'x_ray_data.csv')

with open(x_ray_datafile_path, "r") as datafile:

        for line in datafile:

            sline = line.strip("\n").split(", ")
            data = [float(x) if i == 0 else x for i, x in enumerate(sline)]
            DEFAULT_X_RAY_DATA.append(data)