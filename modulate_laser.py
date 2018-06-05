# sine wave
# 0-5V
# amplitude 2.5
# offset 2.5
# modulation frequency 1100 Hz
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

# Modulation frequency in Hertz
mod_freq = 1100

laser_mod = Task()
laser_mod.CreateAOVoltageChan("/Dev1/ao0","Laser_modulation",0,5,PyDAQmx.DAQmx_Val_Volts,None)
laser_mod.StartTask()
laser_mod.WriteAnalogScalarF64(1,0,voltage,None)
laser_mod.StopTask()
laser_mod.ClearTask()
