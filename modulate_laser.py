
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


# class Laser(Task):
#     def __init__(self):
#         Task.__init__(self)
#         # Modulation frequency in Hertz
#         self.samp_frequency = 1000 # sampling rate
#         self.mod_frequency = 1100
#         self.mod_amplitude = 2
#         self.mod_offset = 2
#         self.samples = 1000
#         # # create the sine sinewave
#         self.x = np.arange(self.samples)
#         self.sinewave = self.mod_offset + self.mod_amplitude*(np.sin(2 * np.pi * self.mod_frequency * self.x / self.samp_frequency)).astype(np.float64)
#         self.CreateAOVoltageChan("/Dev2/ao0","Laser",0,5,PyDAQmx.DAQmx_Val_Volts,None)
#         self.CfgSampClkTiming(None,self.samples,PyDAQmx.DAQmx_Val_Rising,PyDAQmx.DAQmx_Val_ContSamps,self.samples)
#         #self.AutoRegisterDoneEvent(0)
#         #self.CfgOutputBuffer(self.samples)
#         self.SetWriteRegenMode(PyDAQmx.DAQmx_Val_DoNotAllowRegen)
#         #self.CfgDigEdgeStartTrig("/Dev2/ai/StartTrigger",PyDAQmx.DAQmx_Val_Rising)
#     # def modulate(self, ao_data):
#         #write = PyDAQmx.int32()
#         self.WriteAnalogF64(self.samples,0,10.0,PyDAQmx.DAQmx_Val_GroupByChannel, self.sinewave, None, None) # self.sinewave[(self.i-1)*self.samples:self.i*self.samples],None,None)
#     #     self.AutoRegisterEveryNSamplesEvent(PyDAQmx.DAQmx_Val_Transferred_From_Buffer,self.samples,0) # Auto register the callback functions
#     #
#     # def EveryNCallback(self):
#     #     print("callback")
#     #     self.x = np.arange(self.samples)
#     #     self.sinewave = self.mod_offset + self.mod_amplitude*(np.sin(2 * np.pi * self.mod_frequency * self.x / self.samp_frequency)).astype(np.float64)
#     #     write = PyDAQmx.int32()
#     #     self.WriteAnalogF64(self.samples,0,10.0,PyDAQmx.DAQmx_Val_GroupByChannel, self.sinewave, None, None)
#     #     return 0
#     # def DoneCallback(self, status):
#     #     print("Status",status.value)
#     #     return 0
#
#
# laser = Laser()
# laser.StartTask()
# print("Modulating Laser")
#laser.StopTask()
#laser.ClearTask()




# samp_frequency = 44100 # sampling rate
# mod_frequency = 1100
# mod_amplitude = 2
# mod_offset = 2
# samples = 1000
# x = np.arange(samples)
# sinewave = mod_offset + mod_amplitude*(np.sin(2 * np.pi * mod_frequency * x / samp_frequency)).astype(np.float64)
# laser.modulate(sinewave)
# laser.StopTask()
# laser.ClearTask()


samp_frequency = 1000 # sampling rate
mod_frequency = 1100
mod_amplitude = 2
mod_offset = 2
samples = 1000
# create the sine sinewave
x = np.arange(samples)
sinewave = mod_offset + mod_amplitude*(np.sin(2 * np.pi * mod_frequency * x / samp_frequency)).astype(np.float64)

laser = Task()
laser.CreateAOVoltageChan("/Dev2/ao0","Laser",0,5,PyDAQmx.DAQmx_Val_Volts,None)
laser.CfgSampClkTiming(None,1000.0,PyDAQmx.DAQmx_Val_Rising,PyDAQmx.DAQmx_Val_ContSamps,1000)
laser.SetWriteRegenMode(PyDAQmx.DAQmx_Val_DoNotAllowRegen)
laser.WriteAnalogF64(1000,0,10.0,PyDAQmx.DAQmx_Val_GroupByChannel, sinewave, None, None)
laser.StartTask()
