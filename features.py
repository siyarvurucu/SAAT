import essentia.standard as ess
from essentia.standard import Windowing,Spectrum
import numpy as np

def Audio(audio,params):
    return audio,1

def rms(audio,params):
    """ hop size, frame size, window type """
    hopSize, frameSize, wtype = params
    w = Windowing(type=wtype)
    spec = Spectrum()
    result = []
    RMS = ess.RMS()
    for frame in ess.FrameGenerator(audio, frameSize = frameSize, hopSize = hopSize):
        sf = spec(w(frame))
        result.append(RMS(sf))
    return np.asarray(result),hopSize
    
def spectralCentroid(audio,params):
    """ hop size, frame size, window type """
    hopSize, frameSize, wtype = params
    w = Windowing(type=wtype)
    spec = Spectrum()
    result = []
    centroid = ess.Centroid(range=int(44100/2))
    for frame in ess.FrameGenerator(audio, frameSize = frameSize, hopSize = hopSize):
        sf = spec(w(frame))
        result.append(centroid(sf))
    return np.asarray(result),hopSize
    
def spectralRolloff(audio,params):
    """ hop size, frame size, window type """
    hopSize, frameSize, wtype = params
    w = Windowing(type=wtype)
    spec = Spectrum()
    result = []
    RollOff = ess.RollOff()
    for frame in ess.FrameGenerator(audio, frameSize = frameSize, hopSize = hopSize):
        sf = spec(w(frame))
        result.append(RollOff(sf))
    return np.asarray(result),hopSize
    
def zcr(audio,params):
    """ hop size, frame size """
    hopSize, frameSize = params
    result = []
    ZCR = ess.ZeroCrossingRate()
    for frame in ess.FrameGenerator(audio, frameSize = frameSize, hopSize = hopSize):
        result.append(ZCR(frame))
    return np.asarray(result),hopSize

def spectralFlux(audio,params):
    """ hop size, frame size, window type """
    hopSize, frameSize, wtype = params
    w = Windowing(type=wtype)
    spec = Spectrum()
    result = []
    Flux = ess.Flux()
    for frame in ess.FrameGenerator(audio, frameSize = frameSize, hopSize = hopSize):
        sf = spec(w(frame))
        result.append(Flux(sf))
    return np.asarray(result),hopSize
    
def spectralEntropy(audio,params):
    """ hop size, frame size, window type """
    hopSize, frameSize, wtype = params
    w = Windowing(type=wtype)
    spec = Spectrum()
    result = []
    Entropy = ess.Entropy()
    for frame in ess.FrameGenerator(audio, frameSize = frameSize, hopSize = hopSize):
        sf = spec(w(frame))
        result.append(Entropy(sf))
    return np.asarray(result),hopSize
    
def StrongDecay(audio,params):
    """ hop size, frame size """
    hopSize, frameSize = params                   
    result = []
    strongDecay = ess.StrongDecay()                                               
    for frame in ess.FrameGenerator(audio, frameSize = frameSize, hopSize = hopSize):                         
        result.append(strongDecay(frame))
    return np.asarray(result),hopSize
    
def stft(audio,params): # TODO: add fft size
    """ hop size, frame size"""
    hopSize, frameSize, wtype = params
                             
    result = []
    for frame in ess.FrameGenerator(audio, frameSize = frameSize, hopSize = hopSize):
        result.append(ess.FFT()(frame))
    return np.abs(np.asarray(result)),hopSize
