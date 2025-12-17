from scipy.fft import fft, fftfreq
import soundfile as sf
import matplotlib.pyplot as plt
import numpy as np


noise, sr = sf.read("noise.wav")
anti_noise, _ = sf.read("anti_noise.wav")

N = len(noise)
yf = np.abs(fft(noise))
xf = fftfreq(N, 1/sr)

plt.figure()
plt.plot(xf[:N//2], yf[:N//2])
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.title("Frequency Spectrum of Noise Signal")
plt.xlim(0, 1000)
plt.show()
