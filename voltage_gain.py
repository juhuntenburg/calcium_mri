from PyDAQmx import Task
import PyDAQmx
import numpy as np

# Set initial voltage gain values
pmt1_gain_val = 0.2
pmt2_gain_val = 0.2

# Create an analog output channel with a range of 0-1.25 V range and write out the voltage value set above
pmt1_gain = Task()
pmt1_gain.CreateAOVoltageChan("/Dev1/ao0","PMT1_voltage_gain",0,1.25,PyDAQmx.DAQmx_Val_Volts,None)
pmt1_gain.StartTask()
pmt1_gain.WriteAnalogScalarF64(1,0,pmt1_gain_val,None)
pmt1_gain.StopTask()
pmt1_gain.ClearTask()

# Same for second PMT
pmt2_gain = Task()
pmt2_gain.CreateAOVoltageChan("/Dev1/ao1","PMT2_voltage_gain",0,1.25,PyDAQmx.DAQmx_Val_Volts,None)
pmt2_gain.StartTask()
pmt2_gain.WriteAnalogScalarF64(1,0,pmt2_gain_val,None)
pmt2_gain.StopTask()
pmt2_gain.ClearTask()
