from __future__ import annotations

import os, warnings
import numpy as np

from copy import deepcopy
from typing import List, Optional, Dict, Tuple


class GammaSpectrum:
    """
    The `GammaSpectrum` class provide a simple object allowing the manipulation and analysis of
    pulse height histogram data collected from gamma spectroscopy experiments. An instance of the class can be
    created from a PRA histogram file using the `from_PRA_histogram` function. The class supports various
    operations such as addition and subrtaction. The class supports an energy calibration capable of correlating
    channel indices to gamma photon energies.

    Properties
    ----------
    calibration: Calibration
        The calibraton object using to correlate channel indices to energy values (in keV)
    acquisition_time: Optional[float]
        The acquisition time (in seconds) used for the measurement.
    channels: List[float]
        The list of channel indeces
    energies: List[float]
        The list of gamma photon energies associated to each channel (in keV)
    counts: List[float]
        The list of counts for each channel in counts per second (cps)
    total_activity: float
        The total activity in counts per second (cps) recoded by the detector
    """

    def __init__(self) -> None:
        self.__acquisition_time: Optional[float] = None
        self.__channels: List[float] = []
        self.__counts: List[float] = []
        self.__calibration: Optional[Calibration] = None
    
    @property
    def calibration(self) -> Calibration:
        """
        The energy calibation object associated to the measurement.

        Returns
        -------
        Calibration
            The calibration object.
        """
        return self.__calibration

    @calibration.setter
    def calibration(self, calibration: Calibration) -> None:
        if type(calibration) != Calibration:
            raise TypeError("The calibration property must be of type Calibration")
        self.__calibration = calibration
    
    @calibration.deleter
    def calibration(self) -> None:
        self.__calibration = None
    
    def __setup_operation(self, other: GammaSpectrum) -> Tuple[GammaSpectrum, List[float], List[float]]:
        """
        Validate and setup a binary operation between spectrum objects. The function
        checks if the existing channel labels are compatible within the limit imposed by the shortest
        spectrum. When the operation is carried out between spectra of different length, the shortest spectrum
        is augmented by adding the missing channels with zero counts associated. If compatible the function
        returns a partially initialized GammaSpectrum object together with the augmented counts lists.

        Raises
        ------
        RuntimeError
            Exception raised if the two spectra are not compatible.
        
        Returns
        -------
        GammaSpectrum
            The partially initialized object containing the list of channels. The acquisition time is set to None.
        List[float]
            The list encoding the number of counts for the left object in the operation.
        List[float]
            The list encoding the number of counts for the right object in the operation.
        """

        limit = min(len(self.__channels), len(other.__channels))
        if not np.allclose(self.__channels[0:limit], other.__channels[0:limit], rtol=1e-5):
            raise RuntimeError("Cannot perform operation on two spectra characterized by different channels labels")

        obj = GammaSpectrum()

        if self.calibration != other.calibration:
            warnings.warn("Operation between specra with different calibrations. Calibration will be dropped in the result.", RuntimeWarning)
            obj.__calibration = None
        else:
            obj.__calibration = self.__calibration
        
        left_counts = deepcopy(self.__counts)
        right_counts = deepcopy(other.__counts)
        
        if len(self.__channels) > len(other.__channels):
            obj.__channels = self.__channels
            for _ in self.__channels[limit::]:
                right_counts.append(0)
        else:
            obj.__channels = other.__channels
            for _ in other.__channels[limit::]:
                left_counts.append(0)
        
        return obj, left_counts, right_counts
    
    def __add__(self, other: GammaSpectrum) -> GammaSpectrum:
        obj, left, right = self.__setup_operation(other)
        obj.__counts = [x + y for x, y in zip(left, right)]
        return obj
    
    def __sub__(self, other: GammaSpectrum) -> GammaSpectrum:
        obj, left, right = self.__setup_operation(other)
        obj.__counts = [x - y for x, y in zip(left, right)]
        return obj
    
    @classmethod
    def from_PRA_histogram(self, path: str, acqisition_time: float) -> GammaSpectrum:
        """
        Construct a GammaSpectrum object from a PRA histogram file and the total acquisition time.

        Arguments
        ---------
        path: str
            The path to the histogram file generated by PRA.
        acquisition_time: float
            The acquisition time in seconds (positive integer or float).
        
        Raises
        ------
        ValueError
            Exception raised if the arguments given are deemed invalid.

        Returns
        -------
        GammaSpectrum
            A fully initialized GammaSpectrum object containing the measured data.
        """

        if not os.path.isfile(path):
            raise ValueError(f"The path '{path}' does not point to a valid file")
        
        if acqisition_time <= 0:
            raise ValueError(f"The acquisition time must be a positive integer or float")

        obj = GammaSpectrum()
        obj.__acquisition_time = acqisition_time
        obj.__counts = []
        
        with open(path, 'r') as file:
            
            _ = file.readline()

            for line in file:
                sline = line.split()
                obj.__channels.append(float(sline[0]))
                obj.__counts.append(float(sline[1])/acqisition_time)
        
        return obj

    @property
    def acquisition_time(self) -> Optional[float]:
        """
        The total acquisition time used in the measurement. If the object is derived from a
        binary operation between different spectra objects, the acquisition time will be set
        to None.

        Returns
        -------
        Optional[float]
            The acquisition time in seconds. If `None` the spectrum has been obtained form
            operations between spectra.
        """
        return self.__acquisition_time
    
    @property
    def channels(self) -> List[float]:
        """
        The list of acquisition channels.

        Returns
        -------
        List[float]
            The list of channels.
        """
        return self.__channels
    
    @property
    def energy(self) -> List[float]:
        """
        The list of energy values (in keV) associated to each acquisition channel. Requires the definition of
        an energy calibration object.
        
        Raises
        ------
        RuntimeError
            Exception raised if an energy calibration has not been given.

        Returns
        -------
        List[float]
            The list of energy values (in keV) associated to each datapoint.
        """
        if self.__calibration is None:
            raise RuntimeError("Cannot access the `energy` property when calibration has not been set.")

        return [self.__calibration.get_energy(channel) for channel in self.__channels]
    
    @property
    def counts(self) -> List[float]:
        """
        The activity in counts per second for each channel.

        Returns
        -------
        List[float]
            The conting rate for each channel.
        """
        return self.__counts
    
    @property
    def total_activity(self) -> float:
        """
        The total activity of the sample, as pulse per second, recorded over all channels.

        Returns
        -------
        float
            The total activity of the sample, as pulse per second, recorded over all channels.
        """
        return sum(self.__counts)

    def average_smoothing(self, width: int) -> GammaSpectrum:
        """
        Applies an average smoothing filter to the gamma spectrum.

        Argument
        --------
        width: int
            The excursion of the averaging windows (the total number of points is `2*width + 1`)

        Returns
        -------
        GammaSpectrum
            The smoothed gamma spectrum.
        """
        if width<=0:
            raise ValueError("The average window width must be a positive integer")
        
        obj = GammaSpectrum()
        obj.__acquisition_time = None
        obj.__calibration = self.__calibration

        obj.__channels = self.__channels[width:-width]

        current = 0
        for i in range(len(obj.__channels)):
            
            if i==0:
                current = sum([x for x in self.__counts[0:2*width+1]])
            else:
                current += self.__counts[2*width+i] - self.__counts[i-1]
            
            obj.__counts.append(current/(2*width+1))

        #obj.__channels, obj.__histogram = [], []
        # for i, channel in enumerate(self.__channels[width:-width]):
        #     avg = self.scaled_histogram[i+width]
        #     for j in range(width):
        #         avg += self.scaled_histogram[i+width+j+1] + self.scaled_histogram[i+width-j-1]
        #     obj.__channels.append(channel)
        #     obj.__histogram.append(avg/(2.*width+1))
        
        return obj


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
    
    def __eq__(self, other: Calibration) -> bool:
        if type(other) != Calibration:
            return False
        
        if len(self.__channels) != len(other.__channels) or len(self.__energies) != len(other.__energies):
            return False
        
        if any([a!=b for a, b in zip(self.__channels, other.__channels)]):
            return False
        
        if any([a!=b for a, b in zip(self.__energies, other.__energies)]):
            return False
        
        if len(self.__coefficients) != len(other.__coefficients):
            return False
        
        if any([a!=b for a, b in zip(self.__coefficients, other.__coefficients)]):
            return False
        
        return True
    
    def save_calibration_file(self, path: str) -> None:
        """
        Save the calibration data in a file defined by the user specified path.

        Arguments
        ---------
        path: str
            The path to the calibration datafile
        """
        with open(path, "w") as file:

            file.write(f"# Calibration points: {len(self.__channels)}\n")
            
            for channel, energy in zip(self.__channels, self.__energies):
                file.write(f"  {channel}\t{energy}\n")

            file.write(f"# Polynomial fitting: (order: {self.order})\n")
            for coefficient in self.__coefficients:
                file.write(f"  {coefficient}\n")
    
    @classmethod
    def from_calibration_file(self, path: str) -> Calibration:
        """
        Classmethod capable of generating an instance of the `Calibration` class starting
        from a calibration file.

        Arguments
        ---------
        path: str
            The path to the calibration datafile.
        
        Returns
        -------
        Calibration
            The loaded calibration object
        """
        with open(path, "r") as file:
            npt = int(file.readline().split(":")[-1].strip("\n"))

            data = {}
            for _ in range(npt):
                line = file.readline().split()
                data[float(line[0])] = float(line[1])
            
            order = int(file.readline().split(":")[-1].strip(")\n"))
            
            obj = Calibration(data, order)

            coefficents = []
            for _ in range(order+1):
                coefficents.append(float(file.readline()))
            
            obj.__coefficients = coefficents

            return obj
     
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