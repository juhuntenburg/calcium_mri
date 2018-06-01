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

    # main animation function
    def animate(i):
        xs = np.arange(pmt1_signal.n,pmt1_signal.n+100)
        ys = pmt1_signal.data
        ax1.clear()
        ax1.get_xaxis().get_major_formatter().set_useOffset(False)
        ax1.get_yaxis().get_major_formatter().set_useOffset(False)
        ax1.set_xlabel("Time [ms]")
        ax1.set_ylabel("Signal [V]")
        ax1.set_title("PMT1")
        ax1.plot(xs, ys)
        sns.despine()

    fig.canvas.mpl_connect('button_press_event', onClick)
    anim = animation.FuncAnimation(fig, animate, interval=1)

# Class to read voltage from input channel and use callback function to interrupt upon input
# Can be modified to read data from multiple input channels
class ReadPMT1(Task):
    def __init__(self):
        Task.__init__(self)
        self.data = np.zeros(1000) # dummy array to write data from current buffer
        self.n = 0 # counting sampling events
        self.a = [] # list to write all acquired data into
        self.CreateAIVoltageChan("/Dev2/ai13","PMT1_signal",PyDAQmx.DAQmx_Val_Cfg_Default,0,10.0,PyDAQmx.DAQmx_Val_Volts,None) # Create Voltage input channel to acquire between 0 and 10 Volts
        self.CfgSampClkTiming(None,10000.0,PyDAQmx.DAQmx_Val_Rising,PyDAQmx.DAQmx_Val_ContSamps,1000) # Acquire samples continuously with a sampling frequency of 1000 Hz on the rising edge of the sampling of the onboard clock, buffer size of 100
        self.AutoRegisterEveryNSamplesEvent(PyDAQmx.DAQmx_Val_Acquired_Into_Buffer,1000,0) # Auto register the callback functions
        self.AutoRegisterDoneEvent(0) # Auto register the callback functions
    def EveryNCallback(self):
        read = PyDAQmx.int32()
        self.ReadAnalogF64(1000,10.0,PyDAQmx.DAQmx_Val_GroupByScanNumber,self.data,1000,byref(read),None) # sample 100 data points into each buffer and then read them into the data array (size 100), time out after 10 seconds
        self.a.extend(self.data.tolist()) # add current data to all acquired data
        self.n += 100 # count sample points
        #print(self.n, self.data[0])
        return 0
    def DoneCallback(self, status):
        print("Status",status.value)
        return 0

class LED(Task):
    def __init__(self):
        Task.__init__(self)
        self.data = np.concatenate((np.ones(50000)*3, np.zeros(50000)))
        self.a = []
        self.CreateAOVoltageChan("/Dev2/ao0","LED",0,3,PyDAQmx.DAQmx_Val_Volts,None)
        self.CfgSampClkTiming(None,10000,PyDAQmx.DAQmx_Val_Rising,PyDAQmx.DAQmx_Val_ContSamps,10000)
        self.CfgDigEdgeStartTrig("/Dev2/ai/StartTrigger",PyDAQmx.DAQmx_Val_Rising)
        self.WriteAnalogF64(100000,0,10.0,PyDAQmx.DAQmx_Val_GroupByChannel,self.data,None,None)
        self.AutoRegisterEveryNSamplesEvent(PyDAQmx.DAQmx_Val_Transferred_From_Buffer,10000,0) # Auto register the callback functions
        self.AutoRegisterDoneEvent(0)
    def EveryNCallback(self):
        # self.a.extend(np.concatenate((np.ones(500), np.zeros(500))))
        # extend to fit number of timepoints in ca trace
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
                try:
                    pmt1_gain_val = float(input("Enter voltage gain between 0.1 and 1.25 V: "))
                except ValueError:
                    print("Please input an integer or float")
                    pmt1_gain_val = float(input("Enter voltage gain between 0.1 and 1.25 V: "))

                # Create an analog output channel with a range of 0-1.25 V range and write out the voltage value set above
                pmt1_gain = Task()
                pmt1_gain.CreateAOVoltageChan(b"/Dev2/ao1","PMT1_voltage_gain",0,1.25,PyDAQmx.DAQmx_Val_Volts,None)
                pmt1_gain.StartTask()
                try:
                    pmt1_gain.WriteAnalogScalarF64(1,0,pmt1_gain_val,None)
                    print("Setting voltage gain to {0}".format(pmt1_gain_val))
                    pmt1_gain.StopTask()
                    pmt1_gain.ClearTask()
                except PyDAQmx.DAQmxFunctions.InvalidAODataWriteError as a:
                    print(a.message)
                    pmt1_gain_val = float(input("Enter voltage gain between 0.1 and 1.25 V: "))

                if first_pass == True:
                    # Start the acquisition of the PMT signal using the class above
                    led = LED()
                    led.StartTask()
                    pmt1_signal = ReadPMT1()
                    pmt1_signal.StartTask()
                    print("Acquiring PMT1 continuously")
                    first_pass = False
                else:
                    # If the gain has been changed during running acqusition, keep record for how long the previous gain was used
                    gains.extend((len(pmt1_signal.a)-len(gains))*[old_pmt1_gain_val])

                invalid_input = True
                while invalid_input:
                    user_input = input('Enter p to plot data, x to stop acquisition or c to change the voltage gain: ')
                    while user_input == 'p':
                        invalid_input = False
                        # plot and keep waiting for input
                        fig = plt.figure(figsize=(10,5))
                        ax1 = fig.add_subplot(1,1,1)
                        run_animation()
                        plt.show() # This will block the command line until the figure is closed
                        user_input = input('Enter p to plot data, x to stop acquisition or c to change the voltage gain: ')

                    if user_input == 'c':
                        invalid_input = False
                        old_pmt1_gain_val = pmt1_gain_val # store the previous gain value before resetting it
                        pass # go back to the beginning of the outer loop

                    elif user_input == 'x':
                        invalid_input = False
                        # stop task
                        pmt1_signal.StopTask()
                        led.StopTask()
                        print("Stopping acquisition\nAcquired {0} data points".format(len(pmt1_signal.a)))
                        gains.extend((len(pmt1_signal.a)-len(gains))*[pmt1_gain_val]) # keep record of last gain value used
                        # create led data
                        led_record = int(np.floor(len(pmt1_signal.a)/len(led.data)))*led.data.tolist()
                        led_record.extend(led.data[:(len(pmt1_signal.a)-len(led_record))])
                        # save data
                        df = pd.DataFrame(np.column_stack((np.arange(0, len(pmt1_signal.a)), np.asarray(pmt1_signal.a), np.asarray(gains), np.asarray(led_record))), columns=['timepoint[ms]', 'signal[V]', 'gain[V]', 'LED[V]'])
                        s = input("Enter file name or press Enter to save timestamped file in current directory: ")
                        if s == "":
                            timestamp = time.strftime('%Y_%m_%d_%H%M', time.localtime())
                            s = os.path.join(os.curdir,"{0}_pmt1_trace.csv".format(timestamp))
                        else:
                            if not os.path.isabs(s):
                                s = os.path.join(os.curdir, s) # if no absolute path is entered, the file will just be written to the current directory
                        df.to_csv(s, sep=",", index=False)
                        print("Data saved to {0}".format(s))
                        # clear task
                        acq = False # break the outer loop
                        pmt1_signal.ClearTask()
                        led.ClearTask()

                    else:
                        invalid_input = True
                        print('You entered "{0}", which is not a valid input'.format(user_input))

            # catch all other exceptions and save data before aborting the program
            except Exception as e:
                pmt1_signal.StopTask()
                led.StopTask()
                print("\n!!Unexpected error!!\nTrying to save data before exiting")
                timestamp = time.strftime('%Y_%m_%d_%H%M', time.localtime())
                gains.extend((len(pmt1_signal.a)-len(gains))*[pmt1_gain_val])
                df = pd.DataFrame(np.column_stack((np.arange(0, len(pmt1_signal.a)), np.asarray(pmt1_signal.a), np.asarray(gains), np.asarray(led_record))), columns=['timepoint[ms]', 'signal[V]', 'gain[V]', 'LED[V]'])
                df.to_csv(os.path.join(os.curdir,"{0}_pmt1_crash.csv".format(timestamp)), sep=",", index=False)
                pmt1_signal.ClearTask()
                led.ClearTask()
                print("Data saved to {0}_pmt1_crash.csv\n".format(timestamp))
                raise e
