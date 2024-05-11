import pygammaspec
import radioactivedecay as rd

from typing import Optional, List, Union, Tuple
from copy import deepcopy


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
        greater than the set threshold (in seconds).
    intensity_threshold: Optional[float]
        If set to a value different from None will include only gamma transitions with relative
        intensities greater than the set threshold (as % values).

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


def search_x_ray_line(
    energy: float,
    delta: float = 2.0,
) -> List[List[Union[float, float, str, float, str, str]]]:
    """
    Search X-ray transitions located near the specified energy.

    Arguments
    ---------
    energy: float
        The energy (in keV) of the transition of interest.
    delta: float
        The energy range (in keV) within which the X-ray line should be searched.

    Returns
    -------
    List[List[Union[float, str, str]]]:
        A list of lists containing in order the energy, element and shell of the
        X-ray responding to the search parameters
    """
    results = []

    for data in pygammaspec.DEFAULT_X_RAY_DATA:

        if data[0] < energy - delta or data[0] > energy + delta:
            continue

        results.append(data)

    return results


def nuclide_gamma_lines(
    nuclide: str,
    limit_intensity: bool = False,
    intensity_threshold: Optional[float] = None,
) -> Tuple[List[float]]:
    """
    Returns the gamma lines associated to a given nuclide.

    Arguments
    ---------
    nuclide: str
        The nuclide name
    limit_intensity: bool
        If set to true will return only the highest intensity transitions. The function will
        discard all the transition with relative intensity lower than 10% of the highest one.
    intensity_threshold: Optional[float]
        If set to a value different from `None` will discard all the energy lines of relative intensity
        lower than the threshold. If limit_intensity is set to `True` this keyword will be ignored.

    Returns
    -------
    List[float]
        The list of gamma energies (in keV) associated to the gamma linea
    List[float]
        The list of relative intensities (in %)
    """

    gamma_energy, relative_intensity = [], []

    for data in pygammaspec.DEFAULT_GAMMA_DATA:

        if data[4] == nuclide:

            if limit_intensity is False:
                if intensity_threshold and intensity_threshold > data[1]:
                    continue

            gamma_energy.append(data[0])
            relative_intensity.append(data[1])

    if limit_intensity is True and gamma_energy != []:

        max_intensity = max(relative_intensity)
        new_gamma_energy, new_relative_intensity = [], []

        for energy, intensity in zip(gamma_energy, relative_intensity):
            if intensity > 0.1 * max_intensity:
                new_gamma_energy.append(energy)
                new_relative_intensity.append(intensity)

        return new_gamma_energy, new_relative_intensity

    else:
        return gamma_energy, relative_intensity


def element_x_ray_lines(
    element: str,
) -> Tuple[List[float], List[str]]:
    """
    Returns the X-ray lines associated to a given element.

    Arguments
    ---------
    element: str
        The element symbol.

    Returns
    -------
    List[float]
        The list of X-ray energies (in keV) associated to the element
    List[str]
        The type of shell transition associated to the characteristic X-ray emission 
    """
    x_ray_energy, shell = [], []

    for data in pygammaspec.DEFAULT_X_RAY_DATA:

        if data[1] == element:

            x_ray_energy.append(data[0])
            shell.append(data[2])

    return x_ray_energy, shell


def decay_products(
    father: str, branching_ratio_threshold: Optional[float] = None
) -> List[str]:
    """
    Returns a list of nuclides generated by the radioactive decay chain of the user-specified
    `father` nuclide.

    Arguments
    ---------
    father: str
        The string indicating the name of the isotope using the format element-antomic number (e.g. Ra-226)
    branching_ratio_threshold: Optional[float]
        If set to a value different from None, will limit the decay products based on the branching ratio.

    Returns
    -------
    List[str]
        The list of nuclides produced by the decay chain
    """

    daughters = [father]
    current = [father]

    while True:

        new = []

        for nuclide_name in current:

            nuclide = rd.Nuclide(nuclide_name)

            for daughter, branch_ratio in zip(
                nuclide.progeny(), nuclide.branching_fractions()
            ):

                if (
                    branching_ratio_threshold
                    and branching_ratio_threshold > branch_ratio
                ):
                    continue

                if daughter not in new:
                    new.append(daughter)

                if daughter not in daughters:
                    daughters.append(daughter)

        if new == []:
            break

        current = deepcopy(new)

    return daughters


def decay_products_spectrum(
    father: str,
    branching_ratio_threshold: Optional[float] = None,
    limit_intensity: bool = False,
    intensity_threshold: Optional[float] = None,
) -> Tuple[List[str], List[float]]:
    """
    Given a `father` nuclide computes all the decay products and search the associated gamma lines.

    Arguments
    ---------
    father: str
        The father isotope from which the decay chain starts.
    branching_ratio_threshold: Optional[float]
        If set to a value different from None, will limit the decay products based on the branching ratio.
    limit_intensity: bool
        If set to true will return only the highest intensity transitions. The function will
        discard all the transition with relative intensity lower than 10% of the highest one.
    intensity_threshold: Optional[float]
        If set to a value different from `None` will discard all the energy lines of relative intensity
        lower than the threshold. If limit_intensity is set to `True` this keyword will be ignored.

    Returns
    -------
    List[str]
        The list of nuclides acting as gamma emitters.
    List[float]
        The energy of each gamma line in keV.
    """
    emitters, energies = [], []

    nuclides = decay_products(
        father, branching_ratio_threshold=branching_ratio_threshold
    )

    for nuclide in nuclides:

        lines, _ = nuclide_gamma_lines(
            nuclide,
            limit_intensity=limit_intensity,
            intensity_threshold=intensity_threshold,
        )

        for energy in lines:
            emitters.append(nuclide)
            energies.append(energy)

    return emitters, energies
