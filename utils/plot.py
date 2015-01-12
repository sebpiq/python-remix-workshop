import numpy
from pylab import plt

def samples_mono(samples):
    frame_count = samples.shape[0]
    times = numpy.arange(0, frame_count) / 44100.0
    plt.plot(times, samples[:, 0])

def points(points):
    plt.scatter(points[:, 0], points[:, 1], c='green')

def show():
    plt.show()