import speech_recognition as sr
import pyttsx3
import ollama
import threading
import itertools
import sys
import time
import webbrowser
import os
import queue
import pyautogui
 
# Initialize text-to-speech engine globally
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[19].id)  # Adjust voice index if needed 19

# Global flags and queues
stop_speaking = False
command_queue = queue.Queue()
is_speaking = False

import os
import time
import pyautogui

def speak(message):
    """Mock function to simulate speaking."""
    print(f"[Speak]: {message}")  # Placeholder for actual speech function

def open_spotify_and_play(song):
    """Open Spotify and play a requested song."""
    try:
        speak(f"Playing {song} on Spotify.")
        print(f"Attempting to play: {song}")

        # Check if Spotify is already running
        try:
            # For macOS: Check if Spotify is running
            result = os.popen("ps -A | grep -i spotify").read()
            if "Spotify" not in result:
                print("Opening Spotify...")
                os.system("open -a Spotify")  # macOS
                time.sleep(5)  # Wait for Spotify to launch
            else:
                print("Spotify is already running.")
                # Bring Spotify to the foreground
                os.system("open -a Spotify")
                time.sleep(5)  # Give time for Spotify to come to the front
        except Exception as e:
            print(f"Error checking Spotify status: {e}")
            return  # Exit the function if there's an issue starting Spotify

        # Give Spotify some time to load and be ready
        time.sleep(2)

        # Open search bar in Spotify
        print("Opening search bar...")
        try:
            pyautogui.hotkey('command', 'k')  # Open the search bar in Spotify
            time.sleep(1)  # Wait for search bar to open
        except Exception as e:
            print(f"Error opening search bar: {e}")
            return

        # Type the song name into the search bar
        print(f"Typing the song name: {song}")
        try:
            pyautogui.write(song, interval=0.1)  # Type the song name
            time.sleep(1)  # Allow time for typing
        except Exception as e:
            print(f"Error typing song name: {e}")
            return

        # Press Enter to start searching for the song
        print("Pressing Enter to search...")
        try:
            pyautogui.press('return')  # Press Enter to search for the song
        except Exception as e:
            print(f"Error pressing Enter: {e}")
            return

        print(f"Successfully initiated song search for: {song}")

    except Exception as e:
        print(f"An error occurred: {e}")


def speak(text):
    """Speak text aloud with reliable interruption capability."""
    global stop_speaking, is_speaking
    
    # If already speaking and asked to stop, just return
    if stop_speaking:
        stop_speaking = False
        return
    
    is_speaking = True
    
    try:
        # Create a separate thread to continuously check for stop commands
        def monitor_stop_flag():
            global stop_speaking
            while is_speaking:
                if stop_speaking:
                    try:
                        engine.stop()
                    except:
                        pass  # Ignore any errors when stopping
                    break
                time.sleep(0.01)  # Check very frequently
        
        # Start the monitor thread
        monitor = threading.Thread(target=monitor_stop_flag)
        monitor.daemon = True
        monitor.start()
        
        # Say the entire text at once
        engine.say(text)
        
        # Process the speech
        try:
            engine.runAndWait()
        except:
            # Ignore any errors
            pass
            
    finally:
        is_speaking = False
        stop_speaking = False  # Reset flag
        
# Spinner animation while waiting for LLM response
def spinning_cursor(stop_event):
    spinner = itertools.cycle(["|", "/", "-", "\\"])
    while not stop_event.is_set():
        sys.stdout.write("\rThinking... " + next(spinner))
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\r")  # Clear line when done

def chat_with_llm(text):
    """Send a text query to the LLM and return its response."""
    stop_event = threading.Event()
    spinner_thread = threading.Thread(target=spinning_cursor, args=(stop_event,))
    
    spinner_thread.start()  # Start spinner animation
    
    response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": text}])
    
    stop_event.set()  # Stop spinner
    spinner_thread.join()  # Wait for spinner to finish
    
    response_text = response["message"]["content"]
    print("\nAssistant:", response_text)
    
    # Speak the response in a separate thread to not block the main thread
    speech_thread = threading.Thread(target=speak, args=(response_text,))
    speech_thread.start()

def execute_command(command):
    """Perform actions based on recognized commands."""
    global stop_speaking

    if "open browser" in command:
        print("Opening browser")
        speak("Opening browser")
        webbrowser.open("https://www.google.com")

    elif "open terminal" in command:
        print("Opening terminal")
        speak("Opening terminal")
        os.system("open -a Terminal")

    elif "open finder" in command:
        print("Opening Finder")
        speak("Opening Finder")
        os.system("open /System/Library/CoreServices/Finder.app")

    elif "what is" in command or "tell me about" in command:
        chat_with_llm(command)
        
    elif "play" in command and "spotify" in command:
        song_name = command.replace("play", "").replace("on spotify", "").strip()
        open_spotify_and_play(song_name)

    elif "stop" in command:
        print("Stopping speech")
        stop_speaking = True  # Stop speaking immediately

    elif "exit" in command or "quit" in command:
        print("Exiting program")
        speak("Goodbye!")
        time.sleep(1)  # Give time for goodbye to be spoken
        sys.exit(0)  # Exit the script

def background_listener():
    """Continuously listens for commands in the background."""
    recognizer = sr.Recognizer()
    
    while True:
        with sr.Microphone() as source:
            print("Listening in background...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio).lower()
            print(f"\nDetected: {command}")
            
            # If we hear "stop", set the flag immediately
            if "stop" in command:
                global stop_speaking
                stop_speaking = True
                print("Stop command detected!")
            
            # Add command to queue for processing
            command_queue.put(command)
            
        except sr.UnknownValueError:
            pass  # Silently ignore when no speech is detected
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

def command_processor():
    """Process commands from the queue."""
    while True:
        try:
            command = command_queue.get(timeout=0.5)
            execute_command(command)
            command_queue.task_done()
        except queue.Empty:
            pass  # No commands to process

def main():
    pyautogui.hotkey('command', 'f')
    
    # Start background listener thread
    listener_thread = threading.Thread(target=background_listener, daemon=True)
    listener_thread.start()
    
    # Start command processor thread
    processor_thread = threading.Thread(target=command_processor, daemon=True)
    processor_thread.start()
    
    # Initial prompt
    print("Assistant ready! Say 'what is [topic]' to ask a question.")
    speak("Assistant ready! Say 'what is' followed by a topic to ask a question.")
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nExiting program...")
        sys.exit(0)

if __name__ == "__main__":
    main()