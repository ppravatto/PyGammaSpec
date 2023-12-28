import matplotlib.pyplot as plt
from typing import Optional, List

from pygammaspec.spectrum import GammaSpectrum
from pygammaspec.analysis import Calibration


def plot_spectrum(
    sample: GammaSpectrum,
    background: GammaSpectrum,
    xlog: bool = False,
    ylog: bool = False,
    filename: Optional[str] = None,
    calibration: Optional[Calibration] = None,
):
    """
    The function plots the gamma spectrum of the sample together with that of the background and automatically computes the
    difference of the two spectra.

    Arguments
    ---------
    sample: GammaSpectrum
        The gamma spectrum recorded for the sample.
    background: GammaSpectrum
        The gamma spectrum of the background.
    xlog: bool
        If set to True will set the x-scale to logarithmic form.
    ylog: bool
        If set to True will set the y-scale to logarithmic form.
    filename: Optional[str]
        If not None, will indicate the path of the generated image file.
    calibration: Optional[Calibration]
        If not None, will apply energy scale to the x-axis
    """

    plt.rc("font", **{"size": 14})

    fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(12, 10))

    ax1.plot(
        [calibration.get_energy(c) if calibration else c for c in background.channels],
        background.counts,
        c="#00AAAA",
        label="Background",
    )
    ax1.plot(
        [calibration.get_energy(c) if calibration else c for c in sample.channels],
        sample.counts,
        c="black",
        label="Sample",
    )

    ax1.legend()
    ax1.set_ylabel("Activity (cps)", size=16)

    difference = sample - background
    avg_difference = difference.average_smoothing(10)

    ax2.plot(
        [calibration.get_energy(c) if calibration else c for c in difference.channels],
        difference.counts,
        c="#AAAAAA",
    )
    ax2.plot(
        [calibration.get_energy(c) if calibration else c for c in avg_difference.channels],
        avg_difference.counts,
        c="black",
    )

    # ax2.set_xlim(plot_range)
    ax2.set_ylabel("Activity (cps)", size=16)

    if calibration:
        ax2.set_xlabel("Energy (keV)", size=16)
    else:
        ax2.set_xlabel("Channel", size=16)    

    if xlog:
        ax1.set_xscale("log")
        ax2.set_xscale("log")

    if ylog:
        ax1.set_yscale("log")
        ax2.set_yscale("log")
        ax2.set_ylim(
            bottom=min(
                [x if x > 0 else max(difference.counts) for x in difference.counts]
            )
        )

    ax1.grid(which="major", c="#DDDDDD")
    ax1.grid(which="minor", c="#EEEEEE")
    ax2.grid(which="major", c="#DDDDDD")
    ax2.grid(which="minor", c="#EEEEEE")

    plt.tight_layout()

    if filename is not None:
        plt.savefig(filename, dpi=600)

    plt.show()


def plot_calibration(calibraton: Calibration) -> None:
    """
    Plot the calibration points together with the fitting curve.

    Arguments
    ---------
    calibration: Calibration
        The calibration object to plot.
    """
    plt.rc("font", **{"size": 14})

    fig = plt.figure(figsize=(6, 6))

    plt.scatter(calibraton.channels, calibraton.energies, marker="+", s=150, c="red")

    xfit, yfit = [], []
    for i in range(1000):
        x = (
            0.8 * min(calibraton.channels)
            + 1.4 * i * (max(calibraton.channels) - min(calibraton.channels)) / 1000
        )
        y = calibraton.get_energy(x)

        xfit.append(x)
        yfit.append(y)

    plt.plot(xfit, yfit, c="black", linestyle="--")

    plt.xlabel("Channel", size=16)
    plt.ylabel("Energy (keV)", size=16)

    plt.grid(which="major", c="#DDDDDD")
    plt.grid(which="minor", c="#EEEEEE")

    plt.tight_layout()
    plt.show()
