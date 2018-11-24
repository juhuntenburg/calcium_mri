from PyDAQmx import Task
import PyDAQmx
import numpy as np
from ctypes import byref

pulse = Task()
pulse.CreateCOPulseChanTime("/Dev2/ctr0", "LED pulse", PyDAQmx.DAQmx_Val_Seconds,PyDAQmx.DAQmx_Val_Low,1.00,10,10 )
pulse.StartTask()

voltage = Task()
voltage.CreateAOVoltageChan("/Dev2/ao1","LED",0,5,PyDAQmx.DAQmx_Val_Volts,None)
voltage.CfgImplicitTiming(PyDAQmx.DAQmx_Val_ContSamps,1000)
voltage.CfgDigEdgeStartTrig("/Dev2/pfi0",PyDAQmx.DAQmx_Val_Rising)
voltage.WriteAnalogScalarF64(1,0,3,None)


# voltage.CfgSampClkTiming(None,1000,PyDAQmx.DAQmx_Val_Rising,PyDAQmx.DAQmx_Val_ContSamps,4000)
# voltage.CfgDigEdgeStartTrig("/Dev2/pfi0",PyDAQmx.DAQmx_Val_Rising)
# voltage.StartTask()
# voltage.WriteAnalogF64(1,0,voltage_out,None)
# taskHandle,4000,0,10.0,DAQmx_Val_GroupByChannel,data,&written,NULL)


# class LED(Task):
#     def __init__(self):
#         Task.__init__(self)
#         self.CreateAOVoltageChan("/Dev2/ao1","LED",0,5,PyDAQmx.DAQmx_Val_Volts,None)
#         self.CfgSampClkTiming(None,1000,PyDAQmx.DAQmx_Val_Rising,PyDAQmx.DAQmx_Val_ContSamps,1000)
#         self.CfgDigEdgeStartTrig("/Dev2/pfi0",PyDAQmx.DAQmx_Val_Rising)
#         self.AutoRegisterDoneEvent(0)
#         self.WriteAnalogScalarF64(0,0,3,None)
#     def DoneCallback(self, status):
#         print("Status",status.value)
#         return 0
#
# led = LED()
# led.StartTask()
#led.StopTask()
