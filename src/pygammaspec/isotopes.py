import pygammaspec
from typing import Optional, List, Union

def search_gamma_line(
    energy: float,
    delta: float = 2.0,
    halflife_threshold: Optional[float] = None,
    intensity_threshold: Optional[float] = None,
) -> List[List[Union[float, float, str, float, str, str]]]:
    """
    Search gamma transitions located near the specified gamma energy.

    Arguments
    ---------
    energy: float
        The energy (in keV) of the transition of interest.
    delta: float
        The energy range (in keV) within which the gamma line should be searched.
    halflife_threshold: Optional[float]
        If set to a value different from None will include only gamma emitters with halflife
        greater than the set threshold.
    intensity_threshold: Optional[float]
        If set to a value different from None will include only gamma transitions with relative
        intensities greater than the set threshold.
    
    Returns
    -------
    List[List[Union[float, float, str, float, str, str]]]:
        A list of lists containing in order the energy, relative intensity, decay mode, isotope
        and notes about the gamma line responding to the search parameters
    """
    results = []

    for data in pygammaspec.DEFAULT_GAMMA_DATA:

        if data[0] < energy - delta or data[0] > energy + delta:
            continue

        if halflife_threshold and halflife_threshold > data[3]:
            continue

        if intensity_threshold and intensity_threshold > data[1]:
            continue

        results.append(data)

    return results




