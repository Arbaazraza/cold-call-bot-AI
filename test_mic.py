import sounddevice as sd
import numpy as np

# Configuration
DURATION = 5  # Seconds to record
SAMPLE_RATE = 16000 # Standard rate

print("---------------------------------------")
print(f"1. Listing Input Devices...")
print(sd.query_devices())
print("---------------------------------------")

print(f"2. Recording for {DURATION} seconds...")
print(">> SPEAK INTO YOUR MICROPHONE NOW! <<")

try:
    # Record audio
    recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)
    sd.wait()  # Wait until recording is finished
    
    print("3. Recording finished. Playing it back...")
    sd.play(recording, SAMPLE_RATE)
    sd.wait()
    print("---------------------------------------")
    print("Did you hear yourself?")
    
    # Check if the audio was silent
    volume = np.linalg.norm(recording) * 10
    print(f"Audio Volume Detected: {volume:.2f}")
    if volume < 1:
        print("❌ ERROR: The recording is silent. Check your Mac Microphone permissions.")
    else:
        print("✅ SUCCESS: Microphone is working.")

except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")