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
from spotify_utils import (
    check_devices,
    get_playlists,
    get_artists,
    search_song,
    start_playback,
    play_pause,
    next_track,
    previous_track,
    toggle_shuffle,
    toggle_repeat,
    volume_up,
    volume_down,
    skip_5_seconds,
    go_back_5_seconds,
    play_playlist,
    play_artist,
    play_song,
    get_current_track,
)


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

def process_spotify_command(command):
    command = command.lower().strip()

    if command.startswith("play "):  # Matches "play" followed by a song name
        song_name = command[5:].strip()  # Everything after "play"
        if song_name:
            print(f"Playing song: {song_name}")
            play_song(song_name)
        else:
            print("Please specify a song to play.")
        return True

    elif command == "resume":
        play_pause()
    elif command == "pause":
        play_pause()
    elif command == "next":
        next_track()
    elif command == "previous" or command == "back":
        previous_track()
    elif command == "shuffle":
        toggle_shuffle()
    elif command == "repeat":
        toggle_repeat()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()
    elif command == "skip":
        skip_5_seconds()
    elif command == "rewind":
        go_back_5_seconds()
    else:
        print(f"Unrecognized command: '{command}'")
        return False

    return True


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