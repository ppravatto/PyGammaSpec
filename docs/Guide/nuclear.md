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

(Guide-Nuclear)=
# Using the `nuclear` module
The `nuclear` module provides the user with various type of nuclear data and can be useful in the interpretation and verification of gamma spectra. The module is constantly updated with new functions to help the user in various tasks.

The `nuclear` module uses various sources of data. Gamma energy transition have been obtained from the [The Lund/LBNL Nuclear Data Search](http://nucleardata.nuclear.lu.se/toi/index.asp) while decay chains and other data, such as decay branching ratios, have been taken directly from the [`radioactivedecay` python pacakge](https://radioactivedecay.github.io/).

## Searching for a nuclide
In the previous tutorials we showed how a gamma spectrum can be loaded, calibrated and how the user can perform a peak search allowing the individuation of the main gamma lines.

Once the energy of a peak has been determined, we can try to assign it to a particular gamma emitter. To do so, the `nuclear` module provides a `search_gamma_line` function that allows the user to search to all the gamma emitters having gamma energies close to the detected one. To show how this can be done, let us consider the spectrum used in the previous tutorials as an example:

```{code-cell} python
:tags: ["remove-input"]
from pygammaspec.spectrum import GammaSpectrum, Calibration
from pygammaspec.visualization import plot_spectrum

sample = GammaSpectrum.from_PRA_histogram("../utils/weak_radium.txt", 25851)
background = GammaSpectrum.from_PRA_histogram("../utils/background.txt", 25851)
calibration = Calibration.from_calibration_file("../utils/calibration.txt")

spectrum = (sample-background).average_smoothing(10)
spectrum.calibration = calibration

plot_spectrum(spectrum, enrange=(0, 750), yrange=(0, 0.009), prominence=0.001)
```

Let us look at the spectrum and try to identify the peak that has been located at $186.87 \mathrm{keV}$. To do so, let us interrogate the `search_gamma_line` function by looking for gamma lines of energy centered around that energy with a range of $\pm 1\mathrm{keV}$. This can be done as follows:

```{code-cell} python
from pygammaspec.nuclear import search_gamma_line

gamma_lines = search_gamma_line(186.87, delta=1)

print(f"{len(gamma_lines)} possible gamma emission have been found\n\n")
```

As can be seen 123 possible gamma emitters fall in the selected range. To help us out, let us apply some filering based on the nuclide halflife and gamma line intensity. This can be done acting directly on the `halflife_threshold` and `intensity_threshold` of the `search_gamma_line` function. Starting from the assumption that the sample has beeen acquired from a commonly existing item let us discard nuclides with short half-life smaller than, let's say, $60s$. Please notice how this hypothesis if valid only in the case of long-lived isotopes and would not work in the identification of those peaks associated with short lived decay daughters. Furthermore, given the small acitvity of the sample, let us exclude the low intensity bands, that would not contribute much to the spectrum, by setting $1\%$ as the lowest intensity:

```{code-cell} python
gamma_lines = search_gamma_line(186.87, delta=1, halflife_threshold=60, intensity_threshold=1)

print(f"{len(gamma_lines)} possible gamma emission have been found\n\n")


print("{:^8}  {:^6}  {:^10}   {:<10}{:^6}".format("E(keV)", "I(%)", "t1/2(s)", "nuclide", "decay"))
print("-------------------------------------------------------")
for line in gamma_lines:
  energy, intensity, decay, halflife, nuclide, _  = line
  print("{:>8}  {:>6}  {:>10}   {:<10}{:<6}".format(f"{energy:.3f}", f"{intensity:.2f}", f"{halflife:.2e}", nuclide, decay))
```

Looking at the list of possible gamma emitters one can now proceed by exclusion discarding exotic elements and decay modes. Among the possible candidates, $^{226}\mathrm{Ra}$, deriving from the decay of naturally occurring $^{238}\mathrm{U}$ appears to be the most plausible candidate with an energy of $186.211\mathrm{keV}$. 

## Searching for decay daughters
In the previous section we assigned the peak at $186.87\mathrm{keV}$ to the $^{226}\mathrm{Ra}$ nuclide. Such a nuclide can decay forming a series of radioactive daughters that, possibly, can in turn be source of other gamma ray peaks. It is wise, as such, to verify if those peaks are present in the spectrum.

to do so, we can use the `decay_products` function of the `nuclear` module. The function returns all the possible decay producto of a given nuclide and stops only when a stable isotope has been detected. To use the function, the following syntax can be used:

```{code-cell} python
from pygammaspec.nuclear import decay_products

daughters = decay_products("Ra-226", branching_ratio_threshold=0.01)

print(daughters)
```

where we used the `branching_ratio_threshold` to discard all the branches with less than $1\%$ probability.

Once a decay daughter has been found, possible gamma lines associated to the nuclide can be searched using the `nuclide_gamma_lines` function from the nuclear module. Let us proceed in order by considering the case of the `Pb-214` nuclide (`Po-218` is not a gamma emitter). 

```{code-cell} python
from pygammaspec.nuclear import nuclide_gamma_lines

energies, intensities = nuclide_gamma_lines("Pb-214")

print(f"A total of {len(energies)} gamma lines has been found")
print(f"Intensity range from {max(intensities):.2e} to {min(intensities):.2e}")
```

As can be seen a moltitude of transitions are possible for the nuclide. To obtain the most relevant gamma emissions we can filter by intensity either maually, by setting a threshold with the keyword `intensity_threshold`, or automatically by using the `limit_intensity` option. The latter automatically searches for the highest intensity transition for the nuclide and returns only those transition that are at least $10\%$ of the maximum intensity. Using the latter option we can obtain the following result:

```{code-cell} python
energies, intensities = nuclide_gamma_lines("Pb-214", limit_intensity=True)

print("E (keV) \tI (%)")
print("----------------------")
for energy, intensity in zip(energies, intensities):
  print(f"{energy:.3f}  \t{intensity:.2e}")
```

As can be seen, three transitions are possible for the $^{214}\mathrm{Pb}$ and can in fact be associated to the three peaks immediately of the right of the $^{226}\mathrm{Ra}$ peak.

### Predicting the position of decay daughters peaks

What has been done in the previous example can also be automated using the `decay_products_spectrum` function of the `nuclear` module. The function, once given a `father` nuclide, will automatically search for all gamma lines associated to the decay chain. Filtering of the obtained gamma lines can also be applied directly from the function call using the `branching_ratio_threshold`,`intensity_threshold` and `limit_intensity` keywords. As an example, for the case of `Ra-226` the following result can be obtained:

 ```{code-cell} python
from pygammaspec.nuclear import decay_products_spectrum

nuclides, energies = decay_products_spectrum("Ra-226", branching_ratio_threshold=0.1, limit_intensity=True)

for nuclide, energy in zip(nuclides, energies):

  # keep only energy within the recorded spectrum
  if energy > 800:
    continue

  print("{:<10}{:>8} keV".format(nuclide, f"{energy:.3f}"))
```

The result of the `decay_products_spectrum` function can also be examined graphically directly using the `plot_spectrum` function from the `pygammaspec.visualization` module. The function accepts a `nuclide` keyword that, when set, automatically provides some indication about the expected positions of the gamma lines of the various decay products:


 ```{code-cell} python
from pygammaspec.spectrum import GammaSpectrum, Calibration
from pygammaspec.visualization import plot_spectrum

sample = GammaSpectrum.from_PRA_histogram("../utils/weak_radium.txt", 25851)
background = GammaSpectrum.from_PRA_histogram("../utils/background.txt", 25851)
calibration = Calibration.from_calibration_file("../utils/calibration.txt")

spectrum = (sample-background).average_smoothing(10)
spectrum.calibration = calibration

plot_spectrum(spectrum, enrange=(0, 750), yrange=(0, 0.009), nuclide="Ra-226")
```