---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

(Guide-Spectrum)=
# Using the `GammaSpectrum` class
The `GammaSpectrum` class from the `pygammaspec.spectrum` module allows the storage and manipulation of gamma spectroscopy data. The data can be loaded directly from experimental datafiles using dedicated classmethods. At the moment the following file format are supported:

* ASCII pulse height histogram exported by [PRA](https://www.gammaspectacular.com/marek/pra/index.html) (`from_PRA_histogram`)

As an example, the following snippet of code can be used to create an instance of the `GammaSpectrum` class starting from a PRA pulse height histogram file:

```{code-cell} python
from pygammaspec.spectrum import GammaSpectrum

background = GammaSpectrum.from_PRA_histogram("../utils/background.txt", 25851)

print(background)
```

The obtained class now contains as properties the total acquisition time, the total recorded activity, the list of recorded channels and the corresponding number of counts expressed as counts per second per channel. An example of how to access the properties if shown in the following exampls:

```{code-cell} python
print(f"Acquisition time: {background.acquisition_time} s")
print(f"Total activity of the sample: {background.total_activity:.2f} cps")

print("\nChannels:")
print(background.channels)

print("\nCounts:")
print(background.counts)
```

The data contained in a `GammaSpectrum` object can easily be represented using the `plot_spectrum` function from the `pygammaspec.visualization` module. The following syntax can be used:

```{code-cell} python
from pygammaspec.visualization import plot_spectrum

plot_spectrum(background, ylog=True)
```

The noisy raw data can be smoothed using the `average_smoothing` method. The method applies a moving average to the data returning a smoothed out `GammaSpectrum` object. The size of the averaging window can be set by the user using the `width` argument. The user specified `width` will set the extension ($w$) the windows from the center point. In ohter terms, the average window will have a size of $2\cdot w + 1$ centered around the cannel currently subject to the smoothing. As a consequence the first and last $w$ channel of the spectrum will be left empty. An example of smoothing, togheter with the resulting spectrum, is presented in the following code box:

```{code-cell} python
from pygammaspec.visualization import plot_spectrum

smoothed_background = background.average_smoothing(5)

plot_spectrum(smoothed_background, ylog=True)
```

The library also supports arithmetic operations between instances of the `GammaSpectrum` class. In particular given two different `GammaSpectrum` object, sum and subtractions can be performed using the `+` and `-` operators. The operations are allowed only between spectra having the same channel spacing/values and, if available, the same calibration. If the condition for running the operations are not met, a `RuntimeError` is raised. If one set of data has more channels than the other the longer spectrum will be cut to the size of the smaller one. 

To show how the operation works let us firstly load a new spectrum:

```{code-cell} python
sample = GammaSpectrum.from_PRA_histogram("../utils/weak_radium.txt", 25851)

plot_spectrum(sample, ylog=True)
```

The newly loded spectrum represents the spectrum of a very weak Ra-226 sample. Let us use the subtraction operator (`-`) to compute the difference of the sample spectrum and the background.

```{code-cell} python
difference = sample - background

print(f"Channels in the background: {len(background.channels)}")
print(f"Channels in the sample: {len(sample.channels)}")
print(f"Channels in the difference: {len(difference.channels)}")

plot_spectrum(difference, ylog=True)
```

Please notice how to visualize a sample together with its background and automatically computing the difference of the two, the `plot_spectrum` function can be used providing the `background` argument. The following syntax can be used:

```{code-cell} python
plot_spectrum(sample, background, ylog=True)
```