from madmom.features.onsets import SpectralOnsetProcessor, OnsetPeakPickingProcessor, CNNOnsetProcessor, RNNOnsetProcessor
from madmom.audio.filters import LogarithmicFilterbank
import numpy as np
from essentia.standard import MonoLoader,Windowing,Spectrum,RMS,Centroid,FrequencyBands,FrameGenerator,CartesianToPolar,FFT,OnsetDetection,Onsets, NoveltyCurve
from essentia import array

def hfc(filename):
    audio = MonoLoader(filename=filename, sampleRate=44100)()
    features = []
    for frame in FrameGenerator(audio, frameSize = 1024, hopSize = 512):
        mag, phase =CartesianToPolar()(FFT()(Windowing(type='hann')(frame)))
        features.append(OnsetDetection(method='hfc')(mag, phase))
    return Onsets()(array([features]),[1])
    
def complex(filename):
    audio = MonoLoader(filename=filename, sampleRate=44100)()
    features = []
    for frame in FrameGenerator(audio, frameSize = 1024, hopSize = 512):
        mag, phase =CartesianToPolar()(FFT()(Windowing(type='hann')(frame)))
        features.append(OnsetDetection(method='complex')(mag, phase))
    return Onsets()(array([features]),[1])
 
def complex_phase(filename):
    audio = MonoLoader(filename=filename, sampleRate=44100)()
    features = []
    for frame in FrameGenerator(audio, frameSize = 1024, hopSize = 512):
        mag, phase =CartesianToPolar()(FFT()(Windowing(type='hann')(frame)))
        features.append(OnsetDetection(method='complex_phase')(mag, phase))
    return Onsets()(array([features]),[1])

def flux(filename):
    audio = MonoLoader(filename=filename, sampleRate=44100)()
    features = []
    for frame in FrameGenerator(audio, frameSize = 1024, hopSize = 512):
        mag, phase =CartesianToPolar()(FFT()(Windowing(type='hann')(frame)))
        features.append(OnsetDetection(method='flux')(mag, phase))
    return Onsets()(array([features]),[1])
    
def melflux(filename):
    audio = MonoLoader(filename=filename, sampleRate=44100)()
    features = []
    for frame in FrameGenerator(audio, frameSize = 1024, hopSize = 512):
        mag, phase =CartesianToPolar()(FFT()(Windowing(type='hann')(frame)))
        features.append(OnsetDetection(method='melflux')(mag, phase))
    return Onsets()(array([features]),[1])
    
def rms(filename):
    audio = MonoLoader(filename=filename, sampleRate=44100)()
    features = []
    for frame in FrameGenerator(audio, frameSize = 1024, hopSize = 512):
        mag, phase =CartesianToPolar()(FFT()(Windowing(type='hann')(frame)))
        features.append(OnsetDetection(method='rms')(mag, phase))
    return Onsets()(array([features]),[1])
    
def superflux(filename):
    sodf = SpectralOnsetProcessor(onset_method='superflux', fps=180,
                                  filterbank=LogarithmicFilterbank,
                                  num_bands=24, log=np.log10)
    return sodf(filename)
	

def noveltycurve(filename):
    audio = MonoLoader(filename=filename, sampleRate=44100)()
    band_energy = []
    for frame in FrameGenerator(audio, frameSize = 1024, hopSize = 512):
        mag, phase, = CartesianToPolar()(FFT()(Windowing(type='hann')(frame)))
        band_energy.append(FrequencyBands()(mag))
    novelty = NoveltyCurve()(band_energy)
    return Onsets()(np.array([novelty]),[1])
 
def CNNOnsetDetector(filename):
     audio = MonoLoader(filename=filename, sampleRate=44100)()
     return OnsetPeakPickingProcessor()(CNNOnsetProcessor()(audio))
    
def RNNOnsetDetector(filename):
     audio = MonoLoader(filename=filename, sampleRate=44100)()
     return OnsetPeakPickingProcessor()(RNNOnsetProcessor()(audio))

def modifiedKL(filename):
     audio = MonoLoader(filename=filename, sampleRate=44100)()
     return OnsetPeakPickingProcessor()(SpectralOnsetProcessor(onset_method='modified_kullback_leibler')(audio))
     
def weightedPhaseDev(filename):
     audio = MonoLoader(filename=filename, sampleRate=44100)()
     return OnsetPeakPickingProcessor()(SpectralOnsetProcessor(onset_method='weighted_phase_deviation')(audio))
def PhaseDev(filename):
     audio = MonoLoader(filename=filename, sampleRate=44100)()
     return OnsetPeakPickingProcessor()(SpectralOnsetProcessor(onset_method='phase_deviation')(audio))
def rectifiedComplexDomain(filename):
     audio = MonoLoader(filename=filename, sampleRate=44100)()
     return OnsetPeakPickingProcessor()(SpectralOnsetProcessor(onset_method='rectified_complex_domain')(audio))

def ninos(filename,gamma=0.94):
    """
    reference: Mounir, M., Karsmakers, P., & Van Waterschoot, T. (2016). Guitar note onset detection based on a spectral sparsity measure. 
    European Signal Processing Conference. https://doi.org/10.1109/EUSIPCO.2016.7760394
    """
    N = 2048
    hopSize = int(N/10)
    J = int(N*gamma/2)
    audio = MonoLoader(filename=filename, sampleRate=44100)()
    mag = []
    for frame in FrameGenerator(audio, frameSize = N, hopSize = hopSize):
        m = CartesianToPolar()(FFT()(Windowing(type='hann')(frame)))[0]
        m = np.asarray(m)
        idx = np.argsort(m)[::-1][:J]
        mag.append(m[idx])
    mag = np.asarray(mag)
    x2 = mag*mag
    inos=np.sum(x2,axis=1)/(np.sum(x2*x2,axis=1)**(0.25))
    ninos = inos/(J**(0.25))
    return  OnsetPeakPickingProcessor(threshold=0.03,fps=44100/hopSize)(ninos)                          