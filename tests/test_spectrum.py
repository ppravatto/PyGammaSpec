from os.path import abspath, dirname, join
from pygammaspec.spectrum import GammaSpectrum

# Get the path of the tests directory
DATA_DIR = join(dirname(abspath(__file__)), "data")

def test_GammaSpectrum_init():

    try:
        GammaSpectrum()
    except:
        assert False, "Exception raised on `GammaSpectrum` class construction"

