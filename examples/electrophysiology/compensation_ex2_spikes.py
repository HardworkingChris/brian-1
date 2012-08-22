"""
Example of spike detection method. Requires binary files 
"current.npy" and "rawtrace.npy".

    Rossant et al., "A calibration-free electrode compensation method"
    J. Neurophysiol 2012
"""
from brian import *
import numpy as np
from brian.library.electrophysiology import *

# load data
dt = 0.1*ms
current = np.load("current.npy")  # 10000-long vector, 1s duration
rawtrace = np.load("trace.npy")  # 10000-long vector, 1s duration
t = linspace(0., 1., len(current))

# find spikes and compute score
spikes, scores = find_spikes(rawtrace, dt=dt, check_quality=True)

# plot trace and spikes
plot(t, rawtrace, 'k')
plot(t[spikes], rawtrace[spikes], 'or')
show()
