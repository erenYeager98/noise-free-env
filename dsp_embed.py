import numpy as np
import soundfile as sf
import sounddevice as sd
from scipy.signal import butter, lfilter
from scipy.fft import fft, ifft
import time

# ==========================
# SYSTEM PARAMETERS
# ==========================
SAMPLE_RATE = 44100           # Hz
FRAME_SIZE = 1024             # Samples per frame (~23 ms)
LOW_FREQ_CUTOFF = 800         # Target low-frequency noise (Hz)
AMPLITUDE = 0.6

# ==========================
# LOAD INPUT NOISE
# ==========================
noise_signal, sr = sf.read("noise.wav")
assert sr == SAMPLE_RATE, "Sample rate mismatch"

# Mono enforcement
if noise_signal.ndim > 1:
    noise_signal = noise_signal[:, 0]

print("[INFO] Noise signal loaded")

# ==========================
# DIGITAL FILTER DESIGN
# ==========================
def low_pass_filter(data, cutoff, fs, order=4):
    """Butterworth low-pass filter"""
    nyquist = 0.5 * fs
    norm_cutoff = cutoff / nyquist
    b, a = butter(order, norm_cutoff, btype='low')
    return lfilter(b, a, data)

# ==========================
# FRAME-BASED ANC PIPELINE
# ==========================
anti_noise_output = np.zeros_like(noise_signal)
residual_output = np.zeros_like(noise_signal)

num_frames = len(noise_signal) // FRAME_SIZE

start_time = time.time()

for frame_idx in range(num_frames):
    start = frame_idx * FRAME_SIZE
    end = start + FRAME_SIZE

    # --------------------------
    # Frame Acquisition (Mic)
    # --------------------------
    frame = noise_signal[start:end]

    # Windowing (reduces spectral leakage)
    window = np.hanning(FRAME_SIZE)
    frame_windowed = frame * window

    # --------------------------
    # Frequency Domain Analysis
    # --------------------------
    spectrum = fft(frame_windowed)

    # --------------------------
    # Low-Frequency Isolation
    # --------------------------
    freqs = np.fft.fftfreq(FRAME_SIZE, 1 / SAMPLE_RATE)
    spectrum[np.abs(freqs) > LOW_FREQ_CUTOFF] = 0

    # --------------------------
    # Phase Inversion (Anti-noise)
    # --------------------------
    anti_spectrum = -spectrum

    # --------------------------
    # Signal Reconstruction
    # --------------------------
    anti_frame = np.real(ifft(anti_spectrum))

    # Gain control (stability)
    anti_frame *= AMPLITUDE

    # Store output
    anti_noise_output[start:end] = anti_frame

    # Residual (ideal cancellation model)
    residual_output[start:end] = frame + anti_frame

end_time = time.time()

# ==========================
# PERFORMANCE METRICS
# ==========================
processing_time = end_time - start_time
latency_per_frame = (processing_time / num_frames) * 1000

def rms(signal):
    return np.sqrt(np.mean(signal**2))

spl_before = 20 * np.log10(rms(noise_signal) + 1e-6)
spl_after = 20 * np.log10(rms(residual_output) + 1e-6)

print("\n===== SIMULATION RESULTS =====")
print(f"Frames processed        : {num_frames}")
print(f"Avg processing latency  : {latency_per_frame:.2f} ms/frame")
print(f"SPL before ANC          : {spl_before:.2f} dB")
print(f"SPL after ANC           : {spl_after:.2f} dB")
print(f"Estimated reduction     : {spl_before - spl_after:.2f} dB")

# ==========================
# STEREO OUTPUT GENERATION
# ==========================
stereo_output = np.column_stack((noise_signal, anti_noise_output))
sf.write("personal_silence_zone_output.wav", stereo_output, SAMPLE_RATE)

print("[INFO] Stereo ANC output saved")

# ==========================
# PLAYBACK (OPTIONAL)
# ==========================
print("[INFO] Playing ANC output...")
sd.play(stereo_output, SAMPLE_RATE)
sd.wait()