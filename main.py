import speech_recognition as sr
# import pyttsx3  # Commented out
import ollama
import threading
import itertools
import sys
import time
import webbrowser
import os
import queue
import pyautogui
import pygame
import logging
import re


# Custom Built Functions 
from playBusyWaitAudio import play_busy_wait_audioMusic
from SpotifyProdCode import SpotifyController

# # Initialize text-to-speech engine globally
# engine = pyttsx3.init()
# voices = engine.getProperty("voices")
# engine.setProperty("voice", voices[19].id)  # Adjust voice index if needed

# Global flags and queues
stop_speaking = False  # Still used for stopping busy wait audio
command_queue = queue.Queue()
# is_speaking = False  # No longer needed without pyttsx3

# def speak(text):
#     """Speak text aloud with reliable interruption capability."""
#     global stop_speaking, is_speaking
#     
#     if stop_speaking:
#         stop_speaking = False
#         return
#     
#     is_speaking = True
#     
#     try:
#         def monitor_stop_flag():
#             global stop_speaking
#             while is_speaking:
#                 if stop_speaking:
#                     try:
#                         engine.stop()
#                     except:
#                         pass
#                     break
#                 time.sleep(0.01)
#         
#         monitor = threading.Thread(target=monitor_stop_flag)
#         monitor.daemon = True
#         monitor.start()
#         
#         engine.say(text)
#         try:
#             engine.runAndWait()
#         except:
#             pass
#             
#     finally:
#         is_speaking = False
#         stop_speaking = False

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Initialize Spotify controller
spotify = SpotifyController()

def process_spotify_command(command):
    """
    Process Spotify-related voice commands.
    
    Args:
        command (str): The user's voice command as text
    
    Returns:
        bool: True if a command was processed, False otherwise
    """
    
    # Dictionary mapping command keywords to Spotify functions
    command_mapping = {
        # Playback controls
        r"(pause|stop) (spotify|music)": 'play_pause',
        r"(play|resume|start) (spotify|music)": 'play_pause',
        r"(next|skip) (song|track|music)": 'next',
        r"previous (song|track)": 'previous',
        r"(shuffle|random)( mode)?( on| off)?": 'shuffle',
        r"repeat( mode)?( on| off)?": 'repeat',
        r"(volume|turn) up": 'volume_up',
        r"(volume|turn) down": 'volume_down',
        r"(forward|skip) (5 seconds|five seconds)": 'skip_5_seconds',
        r"(back|rewind) (5 seconds|five seconds)": 'go_back_5_seconds',
        
        # Navigation
        r"(go to |open |show )?(home|homepage)": 'home',
        r"(go to |open |show )?(my )?(library|collection)": 'library',
        r"(go to |open |show )?(my )?playlists": 'playlists',
        r"(go to |open |show )?(my )?podcasts": 'podcasts',
        r"(go to |open |show )?(my )?artists": 'artists',
        r"(go to |open |show )?(my )?albums": 'albums',
        r"(go to |open |show )?(my )?audiobooks": 'audiobooks',
        r"(open |show )?search": 'search',
        r"(go to |open |show )?now playing": 'now_playing',
        r"(go to |open |show )?(my )?liked songs": 'liked_songs',
        r"(go to |open |show )?made for you": 'made_for_you',
        r"(go to |open |show )?new releases": 'new_releases',
        r"(go to |open |show )?charts": 'charts',
        r"(go to |open |show )?(my )?queue": 'queue',
        
        # Song management
        r"like( this song| this track)?": 'like',
        
        # Window controls
        r"(open |show )?settings": 'settings',
        r"toggle now playing": 'toggle_now_playing',
        r"toggle library": 'toggle_library',
    }
    
    # Special case for playing specific songs
    play_song_pattern = r"play (.*?)( on spotify)?$"
    play_match = re.match(play_song_pattern, command.lower())
    
    if play_match:
        song_name = play_match.group(1).strip()
        logger.info(f"Playing song: {song_name}")
        return spotify.execute_command('play', song_name)
    
    # Check for other commands
    for pattern, action in command_mapping.items():
        if re.search(pattern, command.lower()):
            logger.info(f"Executing Spotify command: {action}")
            return spotify.execute_command(action)
    
    # No matching command found
    return False

def process_command(command):
    """
    Process all voice commands, including Spotify and other functions.
    
    Args:
        command (str): The user's voice command as text
    """
    try:
        # Check if this is a Spotify-related command
        if "spotify" in command.lower() or "music" in command.lower() or "play" in command.lower():
            if process_spotify_command(command):
                logger.info(f"Successfully processed Spotify command: {command}")
            else:
                logger.warning(f"Failed to process Spotify command: {command}")
        else:
            # Handle other types of commands here
            logger.info(f"Not a Spotify command: {command}")
            # Other command processing...
            
    except Exception as e:
        logger.error(f"Error processing command '{command}': {e}")

def spinning_cursor(stop_event):
    spinner = itertools.cycle(["|", "/", "-", "\\"])
    while not stop_event.is_set():
        sys.stdout.write("\rThinking... " + next(spinner))
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\r")

def chat_with_llm(text):
    stop_event = threading.Event()
    spinner_thread = threading.Thread(target=spinning_cursor, args=(stop_event,))
    spinner_thread.start()
    
    response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": text}])
    
    stop_event.set()
    spinner_thread.join()
    
    response_text = response["message"]["content"]
    print("\nAssistant:", response_text)
    
    # speech_thread = threading.Thread(target=speak, args=(response_text,))  # Commented out
    # speech_thread.start()

def execute_command(command):
    global stop_speaking
    process_command(command)

    # if "open browser" in command:
    #     print("Opening browser")
    #     # speak("Opening browser")  # Replaced with print
    #     webbrowser.open("https://www.google.com")

    # elif "open terminal" in command:
    #     print("Opening terminal")
    #     # speak("Opening terminal")  # Replaced with print
    #     os.system("open -a Terminal")

    # elif "open finder" in command:
    #     print("Opening Finder")
    #     # speak("Opening Finder")  # Replaced with print
    #     os.system("open /System/Library/CoreServices/Finder.app")

    # elif "what is" in command or "tell me about" in command:
    #     chat_with_llm(command)
        
    # elif "spotify" in command:
    #     process_command(command)

    # elif "stop" in command:
    #     print("Stopping audio")
    #     stop_speaking = True  # Still used to stop busy wait audio

    if "exit" in command or "quit" in command:
        print("Exiting program")
        # speak("Goodbye!")  # Replaced with print
        # time.sleep(1)  # Removed since no speech to wait for
        sys.exit(0)

def background_listener():
    recognizer = sr.Recognizer()
    
    while True:
        with sr.Microphone() as source:
            print("Listening in background...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio).lower()
            print(f"\nDetected: {command}")
            
            if "stop" in command:
                global stop_speaking
                stop_speaking = True
                print("Stop command detected!")
            
            command_queue.put(command)
            
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

def command_processor():
    while True:
        try:
            command = command_queue.get(timeout=0.5)
            execute_command(command)
            command_queue.task_done()
        except queue.Empty:
            pass

def main():
    listener_thread = threading.Thread(target=background_listener, daemon=True)
    listener_thread.start()
    
    processor_thread = threading.Thread(target=command_processor, daemon=True)
    processor_thread.start()
    
    print("Assistant ready! Say 'what is [topic]' to ask a question.")
    # speak("Assistant ready! Say 'what is' followed by a topic to ask a question.")  # Replaced with print
    
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nExiting program...")
        sys.exit(0)

if __name__ == "__main__":
    main()