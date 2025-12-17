import numpy as np
import soundfile as sf

sr = 44100
duration = 5
freq = 400

t = np.linspace(0, duration, int(sr*duration), endpoint=False)
noise = 0.5 * np.sin(2 * np.pi * freq * t)

sf.write("noise.wav", noise, sr)
print("Noise generated")
