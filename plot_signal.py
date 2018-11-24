import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
import numpy as np

sns.set()
sns.set_style('ticks')
sns.set_context('talk')
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

def animate(i):
    xs = np.arange(1, 1001)
    ys = np.random.random_sample(1000)
    ax1.clear()
    ax1.plot(xs, ys)

ani = animation.FuncAnimation(fig, animate, interval=1)
sns.despine()
plt.show()
