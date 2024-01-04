from __future__ import annotations

import numpy as np

from typing import Dict, Tuple, Optional, List
from scipy.signal import find_peaks
from scipy.optimize import curve_fit

from pygammaspec.spectrum import GammaSpectrum


def peak_search(
    spectrum: GammaSpectrum, prominence: float = 0.01
) -> Dict[int, Tuple[float, float, Optional[float]]]:
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
    Dict[int, Tuple[float, float, Optional[float]]]
        The dictionary containing the index of the peak as the key and the tuple containing the channel, intensity
        energy (in keV) as the value. If the spectrum is not calibrated the energy field will be filled with `None`.
    """
    idx_list = find_peaks(spectrum.counts, prominence=prominence)[0]

    peak_dict = {}
    for i, idx in enumerate(idx_list):
        channel = spectrum.channels[idx]
        counts = spectrum.counts[idx]
        energy = (
            spectrum.calibration.get_energy(channel)
            if spectrum.calibration is not None
            else None
        )
        peak_dict[i] = (channel, counts, energy)

    return peak_dict


def unitary_height_gaussian(x: float, x0: float, sigma: float) -> float:
    """
    Unitary height Gaussian function centered in `x0` and having a standar deviation of `sigma`

    Arguments
    ---------
    x: float
        The point in which the function must be evaluated.
    x0: float
        The center of the Gaussian function.
    sigma: float
        The standard deviation of the Gaussian.

    Retruns
    -------
    float
        The value of the funciont in `x`.
    """
    return np.exp(-((x - x0) ** 2) / (2 * sigma**2))


def fit_peak(
    spectrum: GammaSpectrum,
    emin: float,
    emax: float,
    baseline_order: int = 1,
    maxfev: int = 1000000,
) -> Tuple[List[float], List[float], List[float], List[float], float]:
    """
    The function perform a Gaussian fit of a single photopeak using a polynomial baseline of variable order.

    Arguments
    ---------
    spectrum: GammaSpectrum
        The spectrum object containing the data to be fitted. The spectrum must contain an energy calibration.
    emin: float
        The minimum energy defining the region to fit.
    emax: float
        The maximum energy defining the region to fit.
    baseline_order: int
        The order of the baseline function to be used.
    maxfev: int
        The maximum number of functon evaluation during optimization.

    Raises
    ------
    RuntimeError
        Exception raised if the given spectrum has no energy calibration.

    Returns
    -------
    List[float]
        The optimized fitting parameters. The array lists in order the height of the gaussian, its center and its standard
        deviation and it ends with the coefficients of the baseline polynomial listed in ascending order. The lenght of the
        list is `3 + b + 1` where `b` is the `basline_order`.

    List[float]
        The list of energy datapoints used in the fitting.
    List[float]
        The list of counts associated with the fitted function.
    List[float]
        The list of counts associated with the baseline function.
    float
        The estimated efficiency for the peak as 100*FWHM(E)/E.
    """
    if spectrum.calibration is None:
        raise RuntimeError("Cannot use fit_peak on uncalibrated spectra.")

    def baseline(x, *args):
        value = 0
        for n, cn in enumerate(args):
            value += cn * (x**n)
        return value

    def fit_function(x, c0, x0, sigma, *args):
        value = c0 * unitary_height_gaussian(x, x0, sigma)
        value += baseline(x, *args)
        return value

    xlist, ylist = [], []
    for energy, counts in zip(spectrum.energy, spectrum.counts):
        if energy >= emin and energy <= emax:
            xlist.append(energy)
            ylist.append(counts)

    guess = [0, 0.5 * (emax + emin), 0.1 * (emax - emin)]
    for _ in range(baseline_order + 1):
        guess.append(0)

    popt, pcov, infodict, mesg, ier = curve_fit(
        fit_function,
        xlist,
        ylist,
        p0=guess,
        maxfev=maxfev,
        full_output=True,
    )

    yfit, ybaseline = [], []
    for x in xlist:
        yfit.append(fit_function(x, *popt))
        ybaseline.append(baseline(x, *popt[3::]))

    fwhm = 2 * popt[2] * np.sqrt(2 * np.log(2))
    efficiency = 100 * fwhm / popt[1]

    return popt, xlist, yfit, ybaseline, efficiency
