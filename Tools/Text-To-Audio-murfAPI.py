from murf import Murf
from config import Murf_API_key
import requests
import os
import subprocess
import platform

client = Murf(api_key=Murf_API_key)

Phrases = ["Loading...",
    "Please wait.",
    "Almost done.",]

# Initialize counter
i = 1

for phrase in Phrases:
    print(f"Processing phrase {i}: {phrase}")
    # Generate speech with Murf
    response = client.text_to_speech.generate(
        text=phrase,
        voice_id="en-US-amara",
        style="Conversational",
        pitch=0,
        rate=0
    )

    # Get the audio URL
    audio_url = response.audio_file
    print(f"Downloading audio from: {audio_url}")

    # Download the audio data
    audio_data = requests.get(audio_url).content
    print(f"Downloaded {len(audio_data)} bytes of audio data")

    # Save to a file with proper naming
    temp_file = f"Command_Buff_Short_{i}.wav"
    with open(temp_file, "wb") as f:
        f.write(audio_data)
    print(f"Saved audio data to {temp_file}")
    
    # Play audio using system's native player based on platform
    print("Playing audio with system player...")
    try:
        system = platform.system()
        if system == "Darwin":  # macOS
            subprocess.run(["afplay", temp_file])
        elif system == "Windows":
            os.system(f'start {temp_file}')
        elif system == "Linux":
            # Try different Linux players
            players = ["aplay", "paplay", "mplayer", "mpg123"]
            for player in players:
                try:
                    subprocess.run([player, temp_file], check=True)
                    print(f"Successfully played using {player}")
                    break
                except (subprocess.SubprocessError, FileNotFoundError):
                    continue
            else:
                print("Could not find a suitable audio player on your Linux system")
        print("Playback complete!")
    except Exception as e:
        print(f"Error playing audio: {e}")
    
    # Increment counter for next file
    i += 1

print(f"Generated {i-1} buffering phrase audio files")