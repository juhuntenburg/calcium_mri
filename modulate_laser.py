
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
mod_frequency = 1100
mod_amplitude = 1.5
mod_offset = 1.5

laser_mod = Task()
laser_mod.CreateAOFuncGenChan("/Dev2/ao1","Laser_modulation", PyDAQmx.DAQmx_Val_Sine, mod_frequency, mod_amplitude, mod_offset)
laser_mod.StartTask()
laser_mod.StopTask()
laser_mod.ClearTask()


# test_Task = nidaqmx.Task()
# test_Task.ao_channels.add_ao_voltage_chan('myDAQ1/ao1')
# test_Task.timing.cfg_samp_clk_timing(rate= 80, sample_mode= AcquisitionType.FINITE, samps_per_chan= 40)
#
# test_Writer = nidaqmx.stream_writers.AnalogSingleChannelWriter(test_Task.out_stream, auto_start=True)
#
# samples = np.append(5*np.ones(30), np.zeros(10))
#
# test_Writer.write_many_sample(samples)
# test_Task.wait_until_done()
# test_Task.stop()
# test_Task.close()
