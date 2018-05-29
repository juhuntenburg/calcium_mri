import os, time, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import animation
import seaborn as sns
from PyDAQmx import Task
import PyDAQmx
from ctypes import byref

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

    # main animation
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

# Class to read voltage from input channel and use callback function to interrupt upon input
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
        return 0
    def DoneCallback(self, status):
        print("Status",status.value)
        return 0

if __name__ == "__main__":

        acq = True
        first_pass = True
        gains = []
        while acq == True:
            try:

                # Ask for voltage gain value
                pmt1_gain_val = float(input("Enter voltage gain between 0.1 and 1.25 V: "))
                print("Setting voltage gain to {0}".format(pmt1_gain_val))
                # Create an analog output channel with a range of 0-1.25 V range and write out the voltage value set above
                pmt1_gain = Task()
                pmt1_gain.CreateAOVoltageChan(b"/Dev1/ao0","PMT1_voltage_gain",0,1.25,PyDAQmx.DAQmx_Val_Volts,None)
                pmt1_gain.StartTask()
                print("Acquiring PMT1 continuously")
                pmt1_gain.WriteAnalogScalarF64(1,0,pmt1_gain_val,None)
                pmt1_gain.StopTask()
                pmt1_gain.ClearTask()

                if first_pass == True:
                    # Start the acquisition
                    pmt1_signal = ReadPMT1()
                    pmt1_signal.StartTask()
                    first_pass = False
                else:
                    gains.extend((len(pmt1_signal.a)-len(gains))*[old_pmt1_gain_val])

                user_input = input('Enter p to plot data, x to stop acquisition or c to change the voltage gain: ')

                while user_input == 'p':
                    # plot and keep waiting for input
                    fig = plt.figure(figsize=(10,5))
                    ax1 = fig.add_subplot(1,1,1)
                    run_animation()
                    plt.show()
                    user_input = input('')

                if user_input == 'c':
                    old_pmt1_gain_val = pmt1_gain_val
                    pass # go back to the beginning of the outer loop

                elif user_input == 'x':
                    # stop task
                    print("Stopped acquisition. Acquired {0} data points".format(len(pmt1_signal.a)))
                    pmt1_signal.StopTask()
                    gains.extend((len(pmt1_signal.a)-len(gains))*[pmt1_gain_val])
                    # save data
                    df = pd.DataFrame(np.column_stack((np.arange(0, len(pmt1_signal.a)), np.asarray(pmt1_signal.a), np.asarray(gains))), columns=['timepoint[ms]', 'signal[V]', 'gain[V]'])
                    s = input("To save data, enter absolute file path or press Enter to save data with time stamp in current directory: ")
                    if s == "":
                        timestamp = time.strftime('%Y_%m_%d_%H%M', time.localtime())
                        df.to_csv(os.path.join(os.curdir,"{0}_pmt1_trace.csv".format(timestamp)), sep=",", index=False)
                    else:
                        df.to_csv(s, sep=",", index=False)
                    # clear task
                    pmt1_signal.ClearTask()
                    acq = False # break the outer loop

            except Exception as e:
                pmt1_signal.StopTask()
                print("\n!!Unexpected error!!\nTrying to save data before exiting")
                timestamp = time.strftime('%Y_%m_%d_%H%M', time.localtime())
                gains.extend((len(pmt1_signal.a)-len(gains))*[pmt1_gain_val])
                df = pd.DataFrame(np.column_stack((np.arange(0, len(pmt1_signal.a)), np.asarray(pmt1_signal.a), np.asarray(gains))), columns=['timepoint[ms]', 'signal[V]', 'gain[V]'])
                df.to_csv(os.path.join(os.curdir,"{0}_pmt1_crash.csv".format(timestamp)), sep=",", index=False)
                print("Data saved to {0}_pmt1_crash.csv\n".format(timestamp))
                raise e
