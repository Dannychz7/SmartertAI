import speech_recognition as sr
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
from logger import logger

# Custom Built Functions 
from playBusyWaitAudio import play_busy_wait_audioMusic
from spotify_command_handler import SpotifyCommandHandler

# Global flags and queues
stop_speaking = False  # Still used for stopping busy wait audio
command_queue = queue.Queue()

class CommandProcessor:
    """Handles processing and execution of voice commands."""
    
    SYSTEM_COMMANDS = {
        "open browser": lambda _: webbrowser.open("https://www.google.com"),
        "open terminal": lambda _: os.system("open -a Terminal"),
        "open finder": lambda _: os.system("open /System/Library/CoreServices/Finder.app"),
    }
    
    @staticmethod
    def process_command(command):
        """
        Process and execute a voice command.
        
        Args:
            command (str): The user's voice command as text
        
        Returns:
            bool: True if program should exit, False otherwise
        """
        try:
            command = command.lower().strip()
            logger.info(f"Processing command: {command}")
            
            # Handle exit command
            if "exit" in command or "quit" in command:
                print("Exiting program")
                return True
                
            # Handle stop command
            if "stop" in command:
                global stop_speaking
                stop_speaking = True
                print("Stopping audio")
                return False
                
            # Handle Spotify commands
            if SpotifyCommandHandler.is_spotify_command(command):
                SpotifyCommandHandler.handle_command(command)
                return False
                
            # Handle system commands
            for cmd, func in CommandProcessor.SYSTEM_COMMANDS.items():
                if cmd in command:
                    print(f"Executing: {cmd}")
                    func(None)
                    return False
                    
            # Handle LLM queries
            if "what is" in command or "tell me about" in command:
                CommandProcessor._chat_with_llm(command)
                return False
                
            # Unrecognized command
            print(f"Unrecognized command: '{command}'")
            return False
            
        except Exception as e:
            logger.error(f"Error processing command '{command}': {e}")
            print(f"Error processing command: {str(e)}")
            return False

    
    @staticmethod
    def _spinning_cursor(stop_event):
        """Display a spinning cursor while the LLM is thinking."""
        spinner = itertools.cycle(["|", "/", "-", "\\"])
        while not stop_event.is_set():
            sys.stdout.write("\rThinking... " + next(spinner))
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r")
    
    @staticmethod
    def _chat_with_llm(text):
        """Send a query to the LLM and display the response."""
        try:
            stop_event = threading.Event()
            spinner_thread = threading.Thread(target=CommandProcessor._spinning_cursor, args=(stop_event,))
            spinner_thread.start()
            
            response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": text}])
            
            stop_event.set()
            spinner_thread.join()
            
            response_text = response["message"]["content"]
            print("\nAssistant:", response_text)
            
        except Exception as e:
            logger.error(f"Error communicating with LLM: {e}")
            print(f"Error getting response: {str(e)}")


def background_listener():
    """Listen for voice commands in the background and add them to the command queue."""
    recognizer = sr.Recognizer()
    
    while True:
        try:
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
                logger.error(f"Google Speech Recognition service error: {e}")
                print(f"Could not request results; {e}")
                
        except Exception as e:
            logger.error(f"Error in background listener: {e}")
            print(f"Listener error: {str(e)}")
            time.sleep(1)  # Prevent rapid error loops

def command_processor():
    """Process commands from the queue."""
    while True:
        try:
            command = command_queue.get(timeout=0.5)
            should_exit = CommandProcessor.process_command(command)
            command_queue.task_done()
            
            if should_exit:
                print("Exiting from command processor...")
                sys.exit(0)
                
        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"Error in command processor: {e}")
            print(f"Processor error: {str(e)}")

def main():
    """Main entry point for the application."""
    try:
        print("Starting voice assistant...")
        
        # Just some test cases without capturing audio
        # SpotifyCommandHandler.handle_command("Play Die for You")
        # time.sleep(5)
        # SpotifyCommandHandler.handle_command("Next")
        # time.sleep(5)
        # SpotifyCommandHandler.handle_command("Previous")
        
        # Start background threads
        listener_thread = threading.Thread(target=background_listener, daemon=True)
        listener_thread.start()
        
        processor_thread = threading.Thread(target=command_processor, daemon=True)
        processor_thread.start()
        
        print("Assistant ready! Say 'what is [topic]' to ask a question.")
        
        # Keep main thread alive
        while True:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nExiting program...")
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        print(f"Fatal error: {str(e)}")
    finally:
        sys.exit(0)

if __name__ == "__main__":
    main()