import asyncio
import aiohttp
import aiofiles
import tempfile
import queue
import threading
from murf import Murf
from config import Murf_API_key
import platform
import subprocess
import os
import re

# Create a global Murf client
client = Murf(api_key=Murf_API_key)

# Audio queue for continuous playback
audio_queue = queue.Queue()
playing = threading.Event()

def split_into_natural_chunks(text, max_chunk_size=100):
    """Split text into natural chunks at sentence boundaries"""
    # Split by sentence endings (., !, ?)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chunk_size:
            current_chunk += " " + sentence if current_chunk else sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

async def download_audio(url):
    """Download audio data asynchronously"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()

async def generate_speech_chunk(text, voice_id="en-US-amara"):
    """Generate speech for a text chunk"""
    response = client.text_to_speech.generate(
        text=text,
        voice_id=voice_id,
        style="Conversational",
        pitch=0,
        rate=0
    )
    audio_data = await download_audio(response.audio_file)
    
    # Create a temporary file
    fd, temp_path = tempfile.mkstemp(suffix='.wav')
    os.close(fd)
    
    # Write audio data to file
    async with aiofiles.open(temp_path, 'wb') as f:
        await f.write(audio_data)
    
    return temp_path

def player_thread():
    """Thread function to continuously play audio from the queue"""
    while True:
        audio_file = audio_queue.get()
        if audio_file is None:  # Sentinel to stop the thread
            break
            
        playing.set()
        system = platform.system()
        try:
            if system == "Darwin":  # macOS
                subprocess.run(["afplay", audio_file], check=True)
            elif system == "Windows":
                os.system(f'start /wait {audio_file}')
            elif system == "Linux":
                players = ["aplay", "paplay", "mplayer", "mpg123"]
                for player in players:
                    try:
                        subprocess.run([player, audio_file], check=True)
                        break
                    except (subprocess.SubprocessError, FileNotFoundError):
                        continue
        finally:
            # Clean up temporary file after playing
            try:
                os.unlink(audio_file)
            except:
                pass
            playing.clear()
            audio_queue.task_done()

async def speak(text, voice_id="en-US-amara"):
    """Generate and queue speech in chunks to create illusion of live speech"""
    # Start player thread if not already started
    if not hasattr(speak, "player_started"):
        speak.player_started = True
        threading.Thread(target=player_thread, daemon=True).start()
    
    # Split text into natural chunks
    chunks = split_into_natural_chunks(text)
    
    # Generate speech for each chunk
    for i, chunk in enumerate(chunks):
        # Generate audio for current chunk
        audio_file = await generate_speech_chunk(chunk, voice_id)
        
        # Add to queue for playback
        audio_queue.put(audio_file)
        
        # If this is not the last chunk, start generating the next chunk in parallel
        # but wait for current chunk to start playing before proceeding
        if i < len(chunks) - 1:
            # Wait for player to start on current chunk before processing next
            playing.wait()

async def main():
    """Main function to demonstrate usage"""
    greeting = "Uhhhhhhhhhhhh"
    await speak(greeting)
    
    # In a real application, you would get user input here and respond
    response = "That's an interesting question. Let me think about it for a moment. I believe the answer is that artificial intelligence systems work by learning patterns from large amounts of data."
    await speak(response)

# Run the example
if __name__ == "__main__":
    asyncio.run(main())