import time
import nidaqmx
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import seaborn as sns

pmt_gain = 0.5
device="Dev2"
sampling_freq = 1000
buffer_size = 1000
terminal_cfg = nidaqmx.constants.TerminalConfiguration.DEFAULT # is -1
rising_edge = nidaqmx.constants.Edge.RISING
cont_sampling = nidaqmx.constants.AcquisitionType.CONTINUOUS

def callback(task_handle, every_n_samples_event_type,
             number_of_samples, callback_data):
    samples = pmt.read(buffer_size)
    out['data'].extend(samples)
    out['n'] = out['n']+buffer_size
    print("{0}...".format(int(out['n']/buffer_size)) ,end="", flush=True)
    return 0

def done_callback(task_handle, status, callback_data):
    print("Status",status)
    return 0

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
        ax1.plot(xs, ys)
        sns.despine()

    fig.canvas.mpl_connect('button_press_event', onClick)
    anim = animation.FuncAnimation(fig, animate, interval=0.1)



if __name__ == "__main__":

    out = {'data': [], 'n': 0}

    # Set PMT gain
    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan("/%s/ao1"%device,"",0,1.25)
        task.write(pmt_gain)


    # Start PMT recording
    pmt = nidaqmx.Task()
    pmt.ai_channels.add_ai_voltage_chan("/%s/ai13"%device,"",terminal_cfg,0,10)
    pmt.timing.cfg_samp_clk_timing(sampling_freq, None, rising_edge,
                                   cont_sampling, buffer_size)
    pmt.register_every_n_samples_acquired_into_buffer_event(buffer_size, callback)
    pmt.register_done_event(done_callback)

    pmt.start()
    input('Running task. Press Enter to stop. Seconds elapsed: \n')
    pmt.stop()

    print(len(out['data']))
    print(out['n'])
