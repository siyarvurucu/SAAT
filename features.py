import essentia.standard as ess
from essentia.standard import Windowing,Spectrum
import numpy as np

def Audio(audio):
    return audio,1

def rms(audio):
    hopSize = 512
    w = Windowing()
    spec = Spectrum()
    result = []
    RMS = ess.RMS()
    for frame in ess.FrameGenerator(audio, frameSize = 1024, hopSize = hopSize):
        sf = spec(w(frame))
        result.append(RMS(sf))
    return np.asarray(result),hopSize
    
def spectralCentroid(audio):
    hopSize = 512
    frameSize = 1024
    w = Windowing()
    spec = Spectrum()
    result = []
    centroid = ess.Centroid(range=int(44100/2))
    for frame in ess.FrameGenerator(audio, frameSize = frameSize, hopSize = hopSize):
        sf = spec(w(frame))
        result.append(centroid(sf))
    return np.asarray(result),hopSize
    
def spectralRolloff(audio):
    hopSize = 512
    frameSize = 1024
    w = Windowing()
    spec = Spectrum()
    result = []
    RollOff = ess.RollOff()
    for frame in ess.FrameGenerator(audio, frameSize = frameSize, hopSize = hopSize):
        sf = spec(w(frame))
        result.append(RollOff(sf))
    return np.asarray(result),hopSize
    
def zcr(audio):
    hopSize = 512
    frameSize = 1024
    result = []
    ZCR = ess.ZeroCrossingRate()
    for frame in ess.FrameGenerator(audio, frameSize = frameSize, hopSize = hopSize):
        result.append(ZCR(frame))
    return np.asarray(result),hopSize

def spectralFlux(audio):
    hopSize = 512
    frameSize = 1024
    w = Windowing()
    spec = Spectrum()
    result = []
    Flux = ess.Flux()
    for frame in ess.FrameGenerator(audio, frameSize = frameSize, hopSize = hopSize):
        sf = spec(w(frame))
        result.append(Flux(sf))
    return np.asarray(result),hopSize
    
def spectralEntropy(audio):
    hopSize = 512
    frameSize = 1024
    w = Windowing()
    spec = Spectrum()
    result = []
    Entropy = ess.Entropy()
    for frame in ess.FrameGenerator(audio, frameSize = frameSize, hopSize = hopSize):
        sf = spec(w(frame))
        result.append(Entropy(sf))
    return np.asarray(result),hopSize
    
def CentroidDecrease(audio):
    hopSize = 512
    frameSize = 1024
    w = Windowing()
    spec = Spectrum()
    result = []
    centroid = ess.Centroid(range=int(44100/2))
    decrease = ess.Decrease(range=int(44100/2))
    for frame in ess.FrameGenerator(audio, frameSize = frameSize, hopSize = hopSize):
        sf = spec(w(frame))
        result.append(decrease(sf))
    return np.asarray(result),hopSize
    
def stft(audio):
    hopSize = 512
    frameSize = 1024
    result = []
    for frame in ess.FrameGenerator(audio, frameSize = frameSize, hopSize = hopSize):
        result.append(ess.FFT()(frame))
    return np.abs(np.asarray(result)),hopSize
