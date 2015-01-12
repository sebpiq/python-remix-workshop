# SOURCE : https://gist.github.com/endolith/255291
import numpy
from matplotlib.mlab import find
from scipy.signal import blackmanharris, fftconvolve
from parabolic import parabolic 


def freq_from_crossings(sig):
    """Estimate frequency by counting zero crossings
    """
    indices = find((sig[1:] >= 0) & (sig[:-1] < 0))
    crossings = [i - sig[i] / (sig[i+1] - sig[i]) for i in indices]
    return 44100 / numpy.mean(numpy.diff(crossings)) 


def freq_from_autocorr(sig):
    """Estimate frequency using autocorrelation
    """
    corr = fftconvolve(sig, sig[::-1], mode='full')
    corr = corr[len(corr)/2:]
    d = numpy.diff(corr)
    start = find(d > 0)[0]
    peak = numpy.argmax(corr[start:]) + start
    px, py = parabolic(corr, peak)
    return 44100 / px

    
if __name__ == '__main__':
    phase = 2 * numpy.pi * 440 * numpy.arange(44100) * (1 / 44100.0)
    sine = numpy.sin(phase)
    print 'zero crossings', freq_from_crossings(sine)
    print 'autocorrelation', freq_from_autocorr(sine)