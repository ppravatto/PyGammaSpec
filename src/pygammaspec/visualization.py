import matplotlib.pyplot as plt
from typing import Optional

from pygammaspec.spectrum import GammaSpectrum

def plot_spectrum(sample: GammaSpectrum, background: GammaSpectrum, xlog: bool = False, ylog: bool = False, filename: Optional[str] = None):
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
    """
    fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(16, 10))

    ax1.plot(background.spectrum[0], background.spectrum[1], c='#00AAAA', label="Background")
    ax1.plot(sample.spectrum[0], sample.spectrum[1], c="black", label="Sample")

    ax1.legend()
    ax1.set_ylabel("cps")

    difference = sample - background
    averaged_difference = difference.average_smoothing(10)

    ax2.plot(difference.spectrum[0], difference.spectrum[1], c='#AAAAAA')
    ax2.plot(averaged_difference.spectrum[0], averaged_difference.spectrum[1], c="black")

    #ax2.set_xlim(plot_range)
    ax2.set_xlabel("Bins")
    ax2.set_ylabel("cps")

    if xlog:
        ax1.set_xscale("log")
        ax2.set_xscale("log")
    
    if ylog:
        ax1.set_yscale("log")
        ax2.set_yscale("log")
        ax2.set_ylim(bottom=min([x if x>0 else max(difference.counts) for x in difference.counts ]))

    plt.tight_layout()

    if filename is not None:
        plt.savefig(filename, dpi=600)
    
    plt.show()
