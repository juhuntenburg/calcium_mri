import os, time, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import animation
import seaborn as sns
from PyDAQmx import Task
import PyDAQmx
from ctypes import byref

buffer_size = 100
sampling_freq = 100

pmt1_gain_val=0.3
device="Dev1".encode()
out_dir="C:/Users/julia/data/test_objective/"

sns.set()
sns.set_style('ticks')
sns.set_context('talk')

def run_animation():
    running = True
    # define method to stop animation upon click
    def onClick(event):
        nonlocal running
        if running:
            anim.event_source.stop()
            running = False
        else:
            anim.event_source.start()
            running = True

    # main animation function
    def animate(i):
        xs = np.arange(pmt1_signal.n-sampling_freq*10,pmt1_signal.n)/sampling_freq
        ys = pmt1_signal.a[pmt1_signal.n-sampling_freq*10:pmt1_signal.n]
        ax1.clear()
        ax1.get_xaxis().get_major_formatter().set_useOffset(False)
        ax1.get_yaxis().get_major_formatter().set_useOffset(False)
        ax1.set_xlabel("Time [s]")
        ax1.set_ylabel("Signal [V]")
        ax1.set_title("PMT")
        #ax1.set_ylim(2.5,3.5)
        ax1.plot(xs, ys)
        sns.despine()

    fig.canvas.mpl_connect('button_press_event', onClick)
    anim = animation.FuncAnimation(fig, animate, interval=0.1)



# Class to read voltage from input channel and use callback function to interrupt upon input
# Can be modified to read data from multiple input channels
class ReadPMT1(Task):
    def __init__(self):
        Task.__init__(self)
        self.data = np.zeros(buffer_size) # dummy array to write data from current buffer
        self.n = 0 # counting sampling events
        self.a = [] # list to write all acquired data into
        self.CreateAIVoltageChan(b"/%s/ai13"%device,"PMT1_signal",PyDAQmx.DAQmx_Val_Cfg_Default,0,10.0,PyDAQmx.DAQmx_Val_Volts,None) # Create Voltage input channel to acquire between 0 and 10 Volts
        self.CfgSampClkTiming(None,sampling_freq,PyDAQmx.DAQmx_Val_Rising,PyDAQmx.DAQmx_Val_ContSamps,buffer_size) # Acquire samples continuously with a sampling frequency of 10000 Hz on the rising edge of the sampling of the onboard clock, buffer size of 1000
        self.AutoRegisterEveryNSamplesEvent(PyDAQmx.DAQmx_Val_Acquired_Into_Buffer,buffer_size,0) # Auto register the callback functions
        self.AutoRegisterDoneEvent(0) # Auto register the callback functions
    def EveryNCallback(self):
        read = PyDAQmx.int32()
        self.ReadAnalogF64(buffer_size,10.0,PyDAQmx.DAQmx_Val_GroupByScanNumber,self.data,buffer_size,byref(read),None) # sample 1000 data points into each buffer and then read them into the data array (size 1000), time out after 10 seconds
        self.a.extend(self.data.tolist()) # add current data to all acquired data
        self.n += buffer_size # count sample points
        #print(self.n, self.data[0])
        return 0
    def DoneCallback(self, status):
        print("Status",status.value)
        return 0


if __name__ == "__main__":
##################### Setting PMT gain ########################################
    pmt1_gain = Task()
    pmt1_gain.CreateAOVoltageChan(b"/%s/ao1"%device,"PMT1_voltage_gain",0,1.25,PyDAQmx.DAQmx_Val_Volts,None)
    pmt1_gain.StartTask()
    pmt1_gain.WriteAnalogScalarF64(1,0,pmt1_gain_val,None)
    pmt1_gain.StopTask()
    pmt1_gain.ClearTask()

##################### Start recording PMT for plotting ########################

    pmt1_signal = ReadPMT1()
    pmt1_signal.StartTask()
    print('Waiting for signal')
    while len(pmt1_signal.a) <= 10*sampling_freq:
        time.sleep(0.01)

    fig = plt.figure(figsize=(10,5))
    ax1 = fig.add_subplot(1,1,1)
    run_animation()
    plt.show()
    pmt1_signal.StopTask()
    pmt1_signal.ClearTask()
