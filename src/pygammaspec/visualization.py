import warnings
import matplotlib.pyplot as plt
from typing import Optional, Tuple

from pygammaspec.spectrum import GammaSpectrum, Calibration
from pygammaspec.analysis import peak_search


def plot_spectrum(
    sample: GammaSpectrum,
    background: Optional[GammaSpectrum] = None,
    xlog: bool = False,
    ylog: bool = False,
    chrange: Optional[Tuple[float, float]] = None,
    enrange: Optional[Tuple[float, float]] = None,
    yrange: Optional[Tuple[float, float]] = None,
    smoothing_size: int = 10,
    prominence: Optional[float] = None,
    filename: Optional[str] = None,
    external_calibration: Optional[Calibration] = None,
):
    """
    The function plots the gamma spectrum of the sample. If a background spetrum is given, the function automatically
    computes the difference of the two spectra and also displays the difference between the two spectra. If calibration
    has been applied to the given spectra the plot will automatically show energy as the x-scale.

    Arguments
    ---------
    sample: GammaSpectrum
        The gamma spectrum recorded for the sample.
    background: Optional[GammaSpectrum]
        The gamma spectrum of the background.
    xlog: bool
        If set to `True` will set the x-scale to logarithmic form (default: `False`).
    ylog: bool
        If set to `True` will set the y-scale to logarithmic form (default: `False`).
    chrange: Optional[Tuple[float, float]]
        The tuple of float values setting the left and right limits of the x-scale based on channel index.
        If set to `None` (default) will apply automatic scaling of the x-axis.
    enrange: Optional[Tuple[float, float]]
        The tuple of float values setting the left and right limits of the x-scale based on energy values (in keV).
        If set to `None` (default) will apply automatic scaling of the x-axis.
    yrange: Optional[Tuple[float, float]]
        The tuple of float values setting the bottom and top of the y-scale. If set to `None` (default)
        will apply automatic scaling of the y-axis.
    smoothing_size: int
        Size of the averaging window used to smooth out the difference spectrum (default: 10)
    prominence: Optional[float]
        If set to a value different from `None` (default), will automatically apply the `peak_search` function
        from the `pygammaspec.analysis` to mark the main peaks using the user defined prominence value.
    filename: Optional[str]
        If not `None`, will indicate the path of the generated image file.
    external_calibration: Optional[Calibration]
        If not `None`, will apply energy scale to the x-axis. If a calibration is applied to the spectra the new calibration
        will override it during plotting.

    Raises
    ------
    RuntimeError
        Exception raised if the x-axis range is specified with `enrange` without a valid calibration.
    """
    # If available, select the proper calibration object.
    calibration = None
    if external_calibration:
        calibration = external_calibration
    elif sample.calibration:
        if background:
            if background.calibration != sample.calibration:
                warnings.warn(
                    "Background calibration is absent or does not match the sample one. Calibration will not be applied.",
                    RuntimeWarning,
                )
            else:
                calibration = sample.calibration
        else:
            calibration = sample.calibration

    if enrange is not None and calibration is None:
        raise RuntimeError(
            "Energy range has been specified but not valid calibration has been found."
        )

    # Define compact helper function to create the xaxis scale based on presence or absence of calibration
    def xscale(s: GammaSpectrum):
        return [calibration.get_energy(c) if calibration else c for c in s.channels]

    plt.rc("font", **{"size": 14})

    if background:
        fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(12, 10))
    else:
        fig, ax1 = plt.subplots(figsize=(12, 5))
        ax1.set_xlabel("Energy (keV)" if calibration else "Channel", size=16)

    ax1.plot(xscale(sample), sample.counts, c="black", label="Sample")
    ax1.set_ylabel("Activity (cps)", size=16)
    ax1.grid(which="major", c="#DDDDDD")
    ax1.grid(which="minor", c="#EEEEEE")

    if background:
        ax1.plot(xscale(background), background.counts, c="#00AAAA", label="Background")
        ax1.legend()

        difference = sample - background
        avg_difference = difference.average_smoothing(smoothing_size)

        ax2.plot(xscale(difference), difference.counts, c="#AAAAAA")
        ax2.plot(xscale(avg_difference), avg_difference.counts, c="black")

        ax2.set_ylabel("Activity (cps)", size=16)
        ax2.set_xlabel("Energy (keV)" if calibration else "Channel", size=16)

        ax2.grid(which="major", c="#DDDDDD")
        ax2.grid(which="minor", c="#EEEEEE")

    # If available apply user-specified x-axis ranges
    if enrange:
        ax1.set_xlim(enrange)
        if background:
            ax2.set_xlim(enrange)

    elif chrange:
        xrange = [calibration.get_energy(ch) if calibration else ch for ch in chrange]
        ax1.set_xlim(xrange)
        if background:
            ax2.set_xlim(xrange)

    if xlog:
        ax1.set_xscale("log")
        if background:
            ax2.set_xscale("log")

        elif enrange is None and chrange is None:
            # Determine the starting point of the spectra on the x-axis to avoid blanck region at low energy
            xstart = 0
            background_counts = (background.counts if background else [0 for _ in sample.channels])
            for x, y1, y2 in zip(sample.channels, background_counts, sample.counts):
                if y1 > 0 or y2 > 0:
                    break
                xstart = x

            ax1.set_xlim(left=calibration.get_energy(xstart) if calibration else xstart)
            if background:
                ax2.set_xlim(
                    left=calibration.get_energy(xstart) if calibration else xstart
                )

    else:
        ax1.set_xlim(left=0)

        if background:
            ax2.set_xlim(left=0)

    if ylog:
        ax1.set_yscale("log")

        if background:
            ax2.set_yscale("log")

            if yrange is None:
                ax2.set_ylim(
                    bottom=min(
                        [
                            x if x > 0 else max(difference.counts)
                            for x in difference.counts
                        ]
                    )
                )

    if yrange:
        ax1.set_ylim(yrange)

        if background:
            ax2.set_ylim(yrange)

    if prominence:
        peak_dict = peak_search(difference if background else sample, prominence)

        # Define a common y-offset for all the markers and labels
        moffset = max(sample.counts) / 15

        for index, (channel, counts, energy) in peak_dict.items():
            x = calibration.get_energy(channel) if calibration else channel

            if background:
                ax2.scatter(x, counts + moffset, marker=11, c="#CC0000", s=40, zorder=3)
                ax2.text(
                    x,
                    counts + 2 * moffset,
                    f"{x:.2f}",
                    size=12,
                    rotation=90.0,
                    ha="center",
                    va="bottom",
                )

            else:
                ax1.scatter(x, counts + moffset, marker=11, c="#CC0000", s=40, zorder=3)
                ax1.text(
                    x,
                    counts + 1.3 * moffset,
                    f"{x:.2f}",
                    size=12,
                    rotation=90.0,
                    ha="center",
                    va="bottom",
                )

    plt.tight_layout()

    if filename is not None:
        plt.savefig(filename, dpi=600)

    plt.show()


def plot_calibration(calibration: Calibration) -> None:
    """
    Plot the calibration points together with the fitting curve.

    Arguments
    ---------
    calibration: Calibration
        The calibration object to plot.
    """
    plt.rc("font", **{"size": 14})

    fig = plt.figure(figsize=(6, 6))

    plt.scatter(calibration.channels, calibration.energies, marker="+", s=150, c="red")

    xfit, yfit = [], []
    for i in range(1000):
        x = (
            0.8 * min(calibration.channels)
            + 1.4 * i * (max(calibration.channels) - min(calibration.channels)) / 1000
        )
        y = calibration.get_energy(x)

        xfit.append(x)
        yfit.append(y)

    plt.plot(xfit, yfit, c="black", linestyle="--")

    plt.xlabel("Channel", size=16)
    plt.ylabel("Energy (keV)", size=16)

    plt.grid(which="major", c="#DDDDDD")
    plt.grid(which="minor", c="#EEEEEE")

    plt.tight_layout()
    plt.show()
