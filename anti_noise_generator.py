import numpy as np
import soundfile as sf

noise, sr = sf.read("noise.wav")

# Anti-noise = phase inversion
anti_noise = -noise

sf.write("anti_noise.wav", anti_noise, sr)
print("Anti-noise generated")
