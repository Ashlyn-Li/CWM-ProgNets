# !/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt

# parameters to modify
filename="interval_0.0001.txt"
label='time_interval=0.01s'
xlabel = 'retrun trip time/ms'
ylabel = 'cumulative probability/ms'
title='Ping test'
fig_name='CDF.png'


t = np.loadtxt(filename, delimiter=" ", dtype="float")
data = t[:,1]
sorted_data = np.sort(data)

cdf = np.arange(1,len(sorted_data)+1)/len(sorted_data)

plt.plot(sorted_data, cdf)
plt.xlabel(xlabel)
plt.ylabel(ylabel)
plt.title(title)
plt.legend()
plt.savefig(fig_name)
plt.show()
