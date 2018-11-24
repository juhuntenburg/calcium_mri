from PyDAQmx import Task
import PyDAQmx
import numpy as np
from ctypes import byref

class ReadPMT1(Task):
    def __init__(self):
        Task.__init__(self)
        self.data = np.zeros(1000)
        self.a = []
        self.CreateAIVoltageChan("Dev1/ai0","PMT1_signal",PyDAQmx.DAQmx_Val_Cfg_Default,0,10.0,PyDAQmx.DAQmx_Val_Volts,None)
        self.CfgSampClkTiming(None,1000.0,PyDAQmx.DAQmx_Val_Rising,PyDAQmx.DAQmx_Val_ContSamps,1000)
        self.AutoRegisterEveryNSamplesEvent(PyDAQmx.DAQmx_Val_Acquired_Into_Buffer,1000,0)
        self.AutoRegisterDoneEvent(0)
    def EveryNCallback(self):
        read = PyDAQmx.int32()
        self.ReadAnalogF64(1000,10.0,PyDAQmx.DAQmx_Val_GroupByScanNumber,self.data,1000,byref(read),None)
        self.a.extend(self.data.tolist())
        print(self.data[0])
        return 0 # The function should return an integer
    def DoneCallback(self, status):
        print("Status",status.value)
        return 0 # The function should return an integer

pmt1_signal=ReadPMT1()
pmt1_signal.StartTask()
input('Acquiring PMT1 continuously. Press Enter to interrupt\n')

pmt1_signal.StopTask()
pmt1_signal.ClearTask()
