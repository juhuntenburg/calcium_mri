
# Before running the first in-vivo experiment,
# acquire a noise measurement by setting your
# laser emission mode to continuous wave (ignoring
# all the settings on this page), then look at the
# power spectrum of your data (see Section 4: Data
# Processing) to determine a frequency range that is
# not contaminated by any noise in your environment.
# Note, that the values under Sampling Rate and
# Number of Samples should be a multiple of your
# selected frequency. Likewise, as a rule of thumb
# the sampling frequency in calcium recordings should
# be at least 5x the modulation frequency.

from PyDAQmx import Task
import PyDAQmx
import numpy as np
from ctypes import byref


class Laser(Task):
    def __init__(self):
        Task.__init__(self)
        # Modulation frequency in Hertz
        self.samp_frequency = 100 # sampling rate
        self.mod_frequency = 10 #1100
        self.mod_amplitude = 1.5
        self.mod_offset = 1.5
        self.samples = 1000
        self.i = 1
        # create the sine sinewave
        self.x = np.arange(samples)
        self.sinewave = mod_offset + mod_amplitude*(np.sin(2 * np.pi * mod_frequency * x / samp_frequency)).astype(np.float64)
        self.CreateAOVoltageChan("/Dev1/ao0","Laser",0,3,PyDAQmx.DAQmx_Val_Volts,None)
        self.CfgSampClkTiming(None,self.samp_frequency,PyDAQmx.DAQmx_Val_Rising,PyDAQmx.DAQmx_Val_ContSamps,self.samples)
        self.WriteAnalogF64(self.samples,0,10.0,PyDAQmx.DAQmx_Val_GroupByChannel,self.sinewave[(self.i-1)*self.samples:self.i*self.samples],None,None)
        self.AutoRegisterEveryNSamplesEvent(PyDAQmx.DAQmx_Val_Transferred_From_Buffer,self.samples,0) # Auto register the callback functions
        self.AutoRegisterDoneEvent(0)
    def EveryNCallback(self):
        self.i = self.i + 1
        write = daq.int32()
        self.WriteAnalogF64(self.samples,0,0,PyDAQmx.DAQmx_Val_GroupByChannel,self.sinewave[(self.i-1)*self.samples:self.i*self.samples],byref(write),None)
        return 0 # The function should return an integer
        # self.a.extend(np.concatenate((np.ones(500), np.zeros(500))))
        # extend to fit number of timepoints in ca trace
        return 0
    def DoneCallback(self, status):
        print("Status",status.value)
        return 0


laser = Laser()
laser.StartTask()
print("Modulating Laser")
laser.StopTask()
laser.ClearTask()
