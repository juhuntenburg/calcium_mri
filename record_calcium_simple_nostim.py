import os, time, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import animation
import seaborn as sns
from PyDAQmx import Task
import PyDAQmx
from ctypes import byref

buffer_size = 1000
sampling_freq = 1000

#visual stimulation
stim_off = 40 #80
stim_on = 1 #20
stim_freq = 2 #Hz
pulse_width = 10 # msec
cycles = 5

pmt1_gain_val=0.3
device="Dev1".encode()

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
        #ax1.set_ylim(1.8,2.1)
        ax1.set_title("PMT")
        ax1.set_ylim(0.02,0.04)
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

    # pmt1_signal.StopTask()
    # pmt1_signal.ClearTask()
    user_input = input('Enter x to exit and save: ')
    #user_input = input('Enter v to start the stimulation or x to exit: ')

    # if user_input == 'v':
    #
    #     pmt_stim = ReadPMT1()
    #     pulse = Task()
    #     pulse.CreateCOPulseChanFreq(b"/%s/ctr0"%device,"", PyDAQmx.DAQmx_Val_Hz, PyDAQmx.DAQmx_Val_Low, stim_off, stim_freq, pulse_width/((1/stim_freq)*1000))#initial delay, freq, duty cycle=pulse width over period (both in sec)
    #     pulse.CfgImplicitTiming(PyDAQmx.DAQmx_Val_FiniteSamps,stim_on*stim_freq) #last is the number of pulses to generate in Finite mode
    #     stim_data = []
    #
    #     pmt_stim.StartTask()
    #     for c in range(cycles):
    #         pulse.StartTask()
    #         pulse.WaitUntilTaskDone(-1)
    #         pulse.StopTask()
    #     time.sleep(stim_off)
    #     pmt_stim.StopTask()
    #     stim_data = cycles*(stim_off*sampling_freq*[0]+stim_on*sampling_freq*[1])+stim_off*sampling_freq*[0]
    #     print('Visual stimulation finished, saving data')
    #
    #     df = pd.DataFrame(np.column_stack((np.arange(0, len(pmt_stim.a)), np.asarray(pmt_stim.a), np.asarray(stim_data))),#, np.asarray(led_record))),
    #                       columns=['timepoint[ms]', 'signal[V]', 'stim'])
    #     timestamp = time.strftime('%Y%m%d_%H%M', time.localtime())
    #     s = os.path.join(os.curdir,"{0}_{1}_{2}_{3}_{4}_{5}.csv".format(timestamp, pmt1_gain_val, stim_off, stim_on, stim_freq, pulse_width))
    #     df.to_csv(s, sep=",", index=False)
    #     print("Data saved to {0}".format(s))
    #     # clear task
    #     pmt_stim.ClearTask()
    #     pulse.ClearTask()

    if user_input == 'x':
        print('Saving data')

        df = pd.DataFrame(np.column_stack((np.arange(0, len(pmt1_signal.a)), np.asarray(pmt1_signal.a), )),#, np.asarray(led_record))),
                          columns=['timepoint[ms]', 'signal[V]'])
        timestamp = time.strftime('%Y%m%d_%H%M', time.localtime())
        s = os.path.join(os.curdir,"{0}_{1}.csv".format(timestamp, pmt1_gain_val)) #, stim_off, stim_on, stim_freq, pulse_width))
        df.to_csv(s, sep=",", index=False)
        print("Data saved to {0}".format(s))
        pmt1_signal.StopTask()
        pmt1_signal.ClearTask()
