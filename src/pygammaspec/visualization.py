import matplotlib.pyplot as plt
from typing import Optional

from pygammaspec.spectrum import GammaSpectrum, Calibration
from pygammaspec.analysis import peak_search


def plot_spectrum(
    sample: GammaSpectrum,
    background: Optional[GammaSpectrum] = None,
    xlog: bool = False,
    ylog: bool = False,
    avg_size: int = 10,
    filename: Optional[str] = None,
    calibration: Optional[Calibration] = None,
):
    """
    The function plots the gamma spectrum of the sample. If a background spetrum is given, the function automatically
    computes the difference of the two spectra and also display the difference.

    Arguments
    ---------
    sample: GammaSpectrum
        The gamma spectrum recorded for the sample.
    background: Optional[GammaSpectrum]
        The gamma spectrum of the background.
    xlog: bool
        If set to True will set the x-scale to logarithmic form.
    ylog: bool
        If set to True will set the y-scale to logarithmic form.
    avg_size: int
        Size of the averaging window used to smooth out the difference spectrum (default: 10)
    filename: Optional[str]
        If not None, will indicate the path of the generated image file.
    calibration: Optional[Calibration]
        If not None, will apply energy scale to the x-axis
    """

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
        avg_difference = difference.average_smoothing(avg_size)

        ax2.plot(xscale(difference), difference.counts, c="#AAAAAA")
        ax2.plot(xscale(avg_difference), avg_difference.counts, c="black")

        ax2.set_ylabel("Activity (cps)", size=16)
        ax2.set_xlabel("Energy (keV)" if calibration else "Channel", size=16)

        ax2.grid(which="major", c="#DDDDDD")
        ax2.grid(which="minor", c="#EEEEEE")

    if xlog:
        xstart = 0
        for x, y1, y2 in zip(background.channels, background.counts, sample.counts):
            if y1 > 0 or y2 > 0:
                break
            xstart = x

        ax1.set_xscale("log")
        ax1.set_xlim(left=calibration.get_energy(xstart) if calibration else xstart)

        if background:
            ax2.set_xscale("log")
            ax2.set_xlim(left=calibration.get_energy(xstart) if calibration else xstart)

    else:
        ax1.set_xlim(left=0)

        if background:
            ax2.set_xlim(left=0)

    if ylog:
        ax1.set_yscale("log")

        if background:
            ax2.set_yscale("log")
            ax2.set_ylim(
                bottom=min(
                    [x if x > 0 else max(difference.counts) for x in difference.counts]
                )
            )

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
