import random
from playsound import playsound  # For playing audio files

def play_busy_wait_audioMusic():
    """Play a single random busy wait audio clip."""
    audio_files = [f"BusyWaitAudio/MusicBuffer/Music_buffer_audio_{i}.wav" for i in range(1, 7)]
    selected_audio = random.choice(audio_files)
    print(f"Playing busy wait audio: {selected_audio}")
    try:
        playsound(selected_audio)  # Play the audio once
        print("Busy wait audio finished")
    except Exception as e:
        print(f"Error playing busy wait audio: {e}")