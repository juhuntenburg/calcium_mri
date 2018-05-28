from PyDAQmx import Task
import PyDAQmx
from ctypes import byref
import matplotlib.pyplot as plt
from matplotlib import animation
import seaborn as sns
import numpy as np
import os

# set plotting style and define animation function
sns.set()
sns.set_style('ticks')
sns.set_context('talk')
fig = plt.figure(figsize=(10,5))
ax1 = fig.add_subplot(1,1,1)

def run_animation():
    running = True

    def onClick(event):
        nonlocal running
        if running:
            anim.event_source.stop()
            running = False
        else:
            anim.event_source.start()
            running = True

    def animate(i):
        xs = np.arange(pmt1_signal.n,pmt1_signal.n+100)
        ys = pmt1_signal.data
        ax1.clear()
        ax1.set_xlabel("Time [ms]")
        ax1.set_ylabel("Signal [V]")
        ax1.set_title("PMT1")
        ax1.plot(xs, ys)
        sns.despine()

    fig.canvas.mpl_connect('button_press_event', onClick)
    anim = animation.FuncAnimation(fig, animate, interval=1)



# Set initial voltage gain value
pmt1_gain_val = 0.2

# Create an analog output channel with a range of 0-1.25 V range and write out the voltage value set above
pmt1_gain = Task()
pmt1_gain.CreateAOVoltageChan("/Dev1/ao0","PMT1_voltage_gain",0,1.25,PyDAQmx.DAQmx_Val_Volts,None)
pmt1_gain.StartTask()
pmt1_gain.WriteAnalogScalarF64(1,0,pmt1_gain_val,None)
pmt1_gain.StopTask()
pmt1_gain.ClearTask()

# Read voltage from input channel and use callback function to interrupt upon input
class ReadPMT1(Task):
    def __init__(self):
        Task.__init__(self)
        self.data = np.zeros(100)
        self.n = 0
        self.a = []
        self.CreateAIVoltageChan("Dev1/ai0","PMT1_signal",PyDAQmx.DAQmx_Val_Cfg_Default,0,10.0,PyDAQmx.DAQmx_Val_Volts,None)
        self.CfgSampClkTiming(None,1000.0,PyDAQmx.DAQmx_Val_Rising,PyDAQmx.DAQmx_Val_ContSamps,100)
        self.AutoRegisterEveryNSamplesEvent(PyDAQmx.DAQmx_Val_Acquired_Into_Buffer,100,0)
        self.AutoRegisterDoneEvent(0)
    def EveryNCallback(self):
        read = PyDAQmx.int32()
        self.ReadAnalogF64(100,10.0,PyDAQmx.DAQmx_Val_GroupByScanNumber,self.data,100,byref(read),None)
        self.a.extend(self.data.tolist())
        self.n += 100
        #print(self.n, self.data[0])
        return 0 # The function should return an integer
    def DoneCallback(self, status):
        print("Status",status.value)
        return 0 # The function should return an integer

pmt1_signal = ReadPMT1()
pmt1_signal.StartTask()
run_animation()
plt.show()
input('Acquiring PMT1 continuously. Press Enter to stop.\n')
pmt1_signal.StopTask()
save_array = np.column_stack((np.arange(0, len(pmt1_signal.a)), np.asarray(pmt1_signal.a)))
np.savetxt(os.path.join(os.curdir,"pmt1_trace.csv"), save_array, delimiter=",")
pmt1_signal.ClearTask()
