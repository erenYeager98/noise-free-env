Block overview of main DSP board under the hood:

```
+------------------+
|  Noise Source    |
| (Fan / Traffic)  |
+--------+---------+
         |
         v
+---------------------------+
|  Microphone / Audio Input |
+--------+------------------+
         |
         v
+---------------------------+
|  Preprocessing Stage      |
|  - Framing                |
|  - Windowing              |
|  - Normalization          |
+--------+------------------+
         |
         v
+---------------------------+
|  Frequency Analysis       |
|  - FFT                    |
|  - Noise Spectrum Est.    |
+--------+------------------+
         |
         v
+---------------------------+
|  Noise Band Isolation     |
|  - Low-Pass Filtering     |
|  - Target Frequency Sel. |
+--------+------------------+
         |
         v
+---------------------------+
|  Anti-Noise Generation    |
|  - Phase Inversion        |
|  - Gain Control           |
+--------+------------------+
         |
         v
+---------------------------+
|  Signal Reconstruction    |
|  - IFFT                   |
|  - Time-Domain Signal     |
+--------+------------------+
         |
         v
+---------------------------+
|  Speaker Output System    |
|  - Noise (Left Channel)   |
|  - Anti-Noise (Right)     |
+--------+------------------+
         |
         v
+---------------------------+
|  Localized Noise          |
|  Cancellation Zone        |
+---------------------------+
```

---

### Block-wise Functional Description

#### 1. Noise Source

This block represents real-world environmental noise such as fan noise, air-conditioner hum, or traffic disturbances. These noise sources are predominantly low-frequency and continuous, making them suitable targets for active noise control techniques.

---

#### 2. Microphone / Audio Input

The microphone subsystem acts as the sensory input of the system. In the simulation-based prototype, environmental noise is either captured using a USB microphone or loaded from pre-recorded audio files. The captured signal serves as the reference noise input for further digital signal processing.

---

#### 3. Preprocessing Stage

The preprocessing block prepares the raw audio signal for frequency-domain analysis. The input signal is segmented into fixed-size frames to emulate real-time processing behavior. Windowing functions, such as the Hanning window, are applied to each frame to minimize spectral leakage. Normalization ensures numerical stability and consistent amplitude scaling across frames.

---

#### 4. Frequency Analysis

The framed and windowed signal is transformed from the time domain into the frequency domain using the Fast Fourier Transform (FFT). This allows the system to identify dominant noise components and analyze the spectral distribution of the incoming sound.

---

#### 5. Noise Band Isolation

In this stage, frequency components corresponding to unwanted noise are isolated. A low-pass filtering strategy is applied to retain frequencies below a predefined cutoff (typically 800 Hz), as these low-frequency components are the most challenging to suppress using passive methods. Higher-frequency components are preserved to maintain speech intelligibility and environmental awareness.

---

#### 6. Anti-Noise Generation

The core ANC operation occurs in this block. The filtered noise spectrum undergoes phase inversion (180-degree phase shift), producing an anti-noise signal. Gain control is applied to prevent signal clipping and to maintain safe acoustic output levels.

---

#### 7. Signal Reconstruction

The anti-noise signal is converted back to the time domain using the Inverse Fast Fourier Transform (IFFT). This reconstructed waveform represents the sound that will be emitted by the speakers to counteract the original noise.

---

#### 8. Speaker Output System

The output stage drives the speakers with two separate audio streams: the original noise signal and the generated anti-noise signal. In the prototype implementation, stereo output is used, where the left channel represents the noise source and the right channel represents the anti-noise signal.

---

#### 9. Localized Noise Cancellation Zone

When the noise and anti-noise signals interact in physical space, destructive interference occurs in specific regions, creating a localized zone of reduced sound pressure. This region constitutes the Personal Silence Zone, providing noise relief without requiring headphones or permanent acoustic modifications.

---


### DSP Code:

```

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

```

### Analysis:
<img width="408" height="188" alt="Screenshot 2025-12-17 214757" src="https://github.com/user-attachments/assets/ee6a6a02-6460-4497-bbe2-35868fd50ba8" />


### Expected output under 100% simulated environment:
<img width="634" height="513" alt="Screenshot 2025-12-17 215434" src="https://github.com/user-attachments/assets/96234b3e-fe95-4748-ae12-a7aa2eb57437" />

### Expected FFT analysis:

<img width="646" height="473" alt="Screenshot 2025-12-17 215620" src="https://github.com/user-attachments/assets/1921192d-95a0-4ec3-9a1c-abba5efb5bb7" />

