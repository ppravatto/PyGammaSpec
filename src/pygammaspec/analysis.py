from __future__ import annotations

from typing import Dict, Tuple
from scipy.signal import find_peaks

from pygammaspec.spectrum import GammaSpectrum


def peak_search(spectrum: GammaSpectrum, prominence: float = 0.01) -> Dict[int, Tuple[float, float]]:
    """
    Function running the `scipy.signal.find_peaks` funciton to detect peaks in the gamma spectrum.

    Arguments
    ---------
    prominence: float
        The prominence threshold to be used in the peak search (default: 0.01). The prominence of a peak measures
        how much a peak stands out from the surrounding baseline of the signal and is defined as the vertical
        distance between the peak and its lowest contour line.

    Returns
    -------
    Dict[int, Tuple[float, float]]
        The dictionary containing the index of the peak as the key and the tuple containing the channel and
        intensity as the value.
    """
    idx_list = find_peaks(spectrum.counts, prominence=prominence)[0]

    peak_dict = {}
    for i, idx in enumerate(idx_list):
        peak_dict[i] = (spectrum.channels[idx], spectrum.counts[idx])

    return peak_dict
