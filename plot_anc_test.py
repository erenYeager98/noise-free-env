from scipy.fft import fft, fftfreq
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

noise, sr = sf.read("noise.wav")
anti_noise, _ = sf.read("anti_noise.wav")

t = np.linspace(0, 0.01, int(sr*0.01))  # first 10 ms

plt.figure()
plt.plot(t, noise[:len(t)], label="Noise Signal")
plt.plot(t, anti_noise[:len(t)], label="Anti-Noise Signal", linestyle="--")
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")
plt.title("Time-Domain Signal Comparison")
plt.legend()
plt.show()

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
