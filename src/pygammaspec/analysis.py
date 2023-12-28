from typing import Dict, Tuple, List
from scipy.signal import find_peaks

import numpy as np

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


class Calibration:
    """
    Simple calibration class capable of fitting a conversion function capable of converting channel
    index into energy values.

    Arguments
    ---------
    calibration_data: Dict[float, float]
        The dictionary containing the channels as keys and the energies (in keV) as values.
    order: int
        The order of the fitting polynomial (default: 1)
    """

    def __init__(self, calibration_data: Dict[float, float], order: int = 1) -> None:
        self.__channels, self.__energies = [], []

        for channel, energy in calibration_data.items():
            self.__channels.append(channel)
            self.__energies.append(energy)

        self.__coefficients = np.polyfit(self.__channels, self.__energies, deg=order)
     
    @property
    def channels(self) -> List[float]:
        """
        The list of channels used for the calibration.

        Returns
        -------
        List[float]
            The list of channels used for the calibration.                
        """
        return self.__channels
    
    @property
    def energies(self) -> List[float]:
        """
        The list of energies (in keV) used for the calibration.

        Returns
        -------
        List[float]
            The list of energies (in keV) used for the calibration.                
        """
        return self.__energies

    @property
    def order(self):
        """
        The order of the fitting polynomial

        Returns
        -------
        int
            The order of the fitting polynomial
        """
        return len(self.__coefficients) - 1    
    
    def get_energy(self, channel: float):
        """
        Conversion function that, from the calibration data, converts the channel index
        into energy value.

        Arguments
        ---------
        channel: float
            The index of the channel
        
        Returns
        -------
        float
            The energy in keV corresponding to the selected channel
        """
        energy = 0
        for n, cn in enumerate(self.__coefficients):
            energy += cn*(channel**(self.order-n))
            
        return energy