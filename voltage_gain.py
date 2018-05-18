from PyDAQmx import Task
import PyDAQmx
import numpy as np

pmt1_gain = 0.2
pmt2_gain = 0.2

pmt1 = Task()
pmt1.CreateAOVoltageChan("/Dev1/ao0","PMT1_voltage_gain",0,1.25,PyDAQmx.DAQmx_Val_Volts,None)
pmt1.StartTask()
pmt1.WriteAnalogScalarF64(1,0,pmt1_gain,None)
pmt1.StopTask()


pmt2 = Task()
pmt2.CreateAOVoltageChan("/Dev1/ao1","PMT2_voltage_gain",0,1.25,PyDAQmx.DAQmx_Val_Volts,None)
pmt2.StartTask()
pmt2.WriteAnalogScalarF64(1,0,pmt2_gain,None)
pmt2.StopTask()
