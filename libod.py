import numpy as np
from essentia.standard import *
#import madmom.audio.signal as signal
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
    audio = MonoLoader(filename=filename, sampleRate=44100)()
    return SuperFluxExtractor()(audio)

def noveltycurve(filename):
    audio = MonoLoader(filename=filename, sampleRate=44100)()
    band_energy = []
    for frame in FrameGenerator(audio, frameSize = 1024, hopSize = 512):
        mag, phase, = CartesianToPolar()(FFT()(Windowing(type='hann')(frame)))
        band_energy.append(FrequencyBands()(mag))
    novelty = NoveltyCurve()(band_energy)
    return Onsets()(np.array([novelty]),[1])