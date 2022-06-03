import sounddevice as sd
import librosa
import numpy as np
import scipy.fft, scipy.signal


class Recording:
    def __init__(self, frequency: int = 44100, channels = 2, duration = 5):
        self.__data = None
        self.__duration = duration
        self.__frequency = frequency
        self.__channels = channels
        self.__fingerprint = None
    
    @property
    def data(self):
        return self.__data    
    @property
    def fingerprint(self):
        return self.__fingerprint

    def record(self):
        self.__data = sd.rec(int(self.__duration * self.__frequency), self.__frequency, self.__channels)
        # self.__data = librosa.audio.to_mono(self.__data)
        # self.__data = librosa.util.normalize(self.__data)
        
    def play(self):
        # with sd.OutputStream(samplerate = self.__frequency, channels = self.__channels, callback = callback, finished_callback = finishCallback) as stream:
        #     sd.wait()
        sd.play(self.__data)
        
    def load(self, path: str):
        input, _ = librosa.load(path, sr = self.__frequency)
        self.__data = input
        if self.__duration != 0:
            self.__data = self.__data[:self.__duration * self.__frequency]
    def normalize(self):
        self.__data = librosa.util.normalize(self.__data)
    
    def plotFFT(self, plt):
        length = len(self.__data)
        fft = scipy.fft.fft(self.__data)
        y = 2.0 / length * np.abs(fft[0:length//2])
        x = scipy.fft.fftfreq(length, 1.0 / self.__frequency)[:length//2]
        plt.plot(x, y)
        
    def __generateFingerprint(self, plt = None):
        windowS = 0.5
        windowSpl = windowS * self.__frequency
        windowSpl += windowSpl % 2
        peaksN = 15
        
        padding = windowSpl - self.__data.size % windowSpl
        
        input = np.pad(self.__data, (0, int(padding)))
        
        freqs, times, stft = scipy.signal.stft(input, self.__frequency, nperseg=windowSpl, nfft=windowSpl, return_onesided=True)
        
        fingerprintMap = []
        
        for timeIndex, window in enumerate(stft.T):
            spectrum = abs(window)
            
            peaks, props = scipy.signal.find_peaks(spectrum, prominence=0, distance=200)
            
            peaksNum = min(peaksN, len(peaks))
            
            largerstPeaks = np.argpartition(props["prominences"], -peaksNum)[-peaksNum:]
            for peak in peaks[largerstPeaks]:
                freq = freqs[peak]
                fingerprintMap.append([timeIndex, freq])
        if plt is not None:
            plt.cla()
            plt.plot(*zip(*fingerprintMap))   
        return fingerprintMap
    
    def generateHash(self, plt = None, id = None):
        self.__fingerprint = {}
        
        upperFreq = 23000
        freqBits = 10
        
        fingerprintMap = self.__generateFingerprint(plt)
        
        for index, (time, freq) in enumerate(fingerprintMap):
            for otherTime, otherFreq in fingerprintMap[index: index + 100]:
                diff = otherTime - time
                if diff <= 1 or diff > 10:
                    continue
                
                freqBinned = freq / upperFreq * (2 ** freqBits)
                otherFreqBinned = otherFreq / upperFreq * (2 ** freqBits)
                hash = int(freqBinned) | (int(otherFreqBinned) << 10) | (int(diff) << 20)
                self.__fingerprint[hash] = (time, id)
        
    
        
        
        
    
    