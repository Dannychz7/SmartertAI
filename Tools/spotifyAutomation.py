import os
import time
import pyautogui
import subprocess
import logging
from typing import Optional, Tuple, List, Dict, Any, Union

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("spotify_automation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def playSong(song: str) -> bool:
    """Open Spotify and play a requested song with busy wait audio.
    
    Args:
        song: The name of the song to play
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if Spotify is running
        result = os.popen("pgrep -x Spotify").read().strip()
        if not result:
            logger.info("Opening Spotify...")
            process = subprocess.Popen(["open", "-a", "Spotify"])
            
            # Wait for Spotify to open with timeout
            timeout = 15  # seconds
            start_time = time.time()
            while time.time() - start_time < timeout:
                if subprocess.run(["pgrep", "-x", "Spotify"], stdout=subprocess.PIPE).returncode == 0:
                    time.sleep(5)
                    logger.info("Spotify launched successfully")
                    # time.sleep(8)  # Additional wait for Spotify to fully initialize
                    break
                time.sleep(0.5)
            else:
                logger.error("Timeout waiting for Spotify to launch")
                return False
        else:
            logger.info("Spotify is already running")
            try:
                subprocess.run(["osascript", "-e", 'tell application "Spotify" to activate'], 
                              check=True, timeout=5)
                time.sleep(1)  # Ensure focus
            except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
                logger.error(f"Failed to activate Spotify: {e}")
                return False
    except Exception as e:
        logger.error(f"Error ensuring Spotify is running: {e}")
        return False
        
    try:
        logger.info("Opening search bar")
        # Open search bar in Spotify
        pyautogui.hotkey('command', 'k')
        time.sleep(1)  # Let the search bar open

        # Verify search is active (could implement a pixel check here)
        
        logger.info(f"Searching for song: {song}")
        # Type song name with error checking
        if not song or not isinstance(song, str):
            logger.error(f"Invalid song name: {song}")
            return False
            
        pyautogui.write(song, interval=0.1)
        time.sleep(1)  # Give it time to type

        # Press Enter to search
        pyautogui.press('return')
        logger.info(f"Search executed for: {song}")
        return True
        
    except pyautogui.FailSafeException:
        logger.error("PyAutoGUI failsafe triggered (mouse moved to corner)")
        return False
    except Exception as e:
        logger.error(f"Error in song search process: {e}")
        return False


class SpotifyController:
    def __init__(self):
        # Command mappings (Mac version - Alt is Option)
        self.commands: Dict[str, Tuple[str, ...]] = {
            # Playback controls
            'play_pause': ('space',),
            'next': ('command', 'right'),    # Corrected from ('command', 'right') - matches doc
            'previous': ('command', 'left'), # Corrected from ('command', 'left') - matches doc
            'shuffle': ('command', 's'),     # Matches doc
            'repeat': ('command', 'r'),      # Matches doc
            'Volume_Up': ('command', 'up'),  # Corrected from ('command', 'up') - matches doc
            'Volume_Down': ('command', 'down'), # Corrected from ('command', 'down') - matches doc
            'Skip_5_Seconds': ('command', 'shift', 'right'),  # Matches doc (seek forward)
            'Go_Back_5_Seconds': ('command', 'shift', 'left'), # Matches doc (seek backward)
            
            # Navigation
            'home': ('option', 'shift', 'h'),    # Matches doc
            'library': ('option', 'shift', '0'), # Matches doc
            'playlists': ('option', 'shift', '1'), # Matches doc
            'podcasts': ('option', 'shift', '2'),  # Matches doc
            'artists': ('option', 'shift', '3'),   # Matches doc
            'albums': ('option', 'shift', '4'),    # Matches doc
            'audiobooks': ('option', 'shift', '5'), # Matches doc
            'search': ('command', 'k'),           # Corrected from 'command, l' to match doc
            'now_playing': ('option', 'shift', 'j'), # Matches doc (currently playing)
            'liked_songs': ('option', 'shift', 's'), # Matches doc
            'made_for_you': ('option', 'shift', 'm'), # Matches doc
            'new_releases': ('option', 'shift', 'n'), # Matches doc
            'charts': ('option', 'shift', 'c'),      # Matches doc
            'queue': ('option', 'shift', 'q'),       # Matches doc
            
            # Song management
            'like': ('option', 'shift', 'b'),        # Matches doc
            
            # Window controls
            'settings': ('command', ','),            # Matches doc (Preferences)
            'toggle_now_playing': ('option', 'shift', 'r'), # Matches doc (toggle right sidebar)
            'toggle_library': ('option', 'shift', 'l'),    # Matches doc (toggle left sidebar)
            
            # App controls
            'logout': ('option', 'shift', 'f6'),     # Matches doc
            'select_all': ('command', 'a'),          # Matches doc
            'filter': ('command', 'f')              # Matches doc
        }
        # Set up PyAutoGUI failsafe
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1  # Add small delay between PyAutoGUI commands

    def ensure_spotify_running(self) -> bool:
        """Ensure Spotify is running and in focus.
        
        Returns:
            bool: True if Spotify is running and focused, False otherwise
        """
        try:
            # Check if Spotify is running
            process = subprocess.run(["pgrep", "-x", "Spotify"], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
            
            if process.returncode != 0:
                logger.info("Opening Spotify...")
                subprocess.run(["open", "-a", "Spotify"])
                
                # Wait for Spotify to open with timeout
                timeout = 15  # seconds
                start_time = time.time()
                while time.time() - start_time < timeout:
                    check_process = subprocess.run(["pgrep", "-x", "Spotify"], 
                                                 stdout=subprocess.PIPE)
                    if check_process.returncode == 0:
                        logger.info("Spotify launched successfully")
                        time.sleep(5)  # Additional wait for Spotify to fully initialize
                        break
                    time.sleep(0.5)
                else:
                    logger.error("Timeout waiting for Spotify to launch")
                    return False
            else:
                logger.info("Spotify is already running")
            
            # Bring Spotify to foreground
            try:
                subprocess.run(["osascript", "-e", 'tell application "Spotify" to activate'], 
                              check=True, timeout=5)
                time.sleep(1)  # Ensure focus
            except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
                logger.error(f"Failed to activate Spotify: {e}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error ensuring Spotify is running: {e}")
            return False

    def execute_command(self, command: str, value: Optional[str] = None) -> bool:
        """Execute a Spotify command with optional value.
        
        Args:
            command: The command to execute
            value: Optional value for commands that require it (e.g., song name)
            
        Returns:
            bool: True if command executed successfully, False otherwise
        """
        # Validate command
        if command not in self.commands and command != 'play':
            logger.error(f"Command '{command}' not recognized")
            return False

        # Ensure Spotify is running
        if not self.ensure_spotify_running():
            logger.error("Failed to ensure Spotify is running")
            return False

        try:
            if command == 'play' and value:
                # Special handling for play with song search
                time.sleep(0.5)
                pyautogui.hotkey('command', 'tab')  # Open 
                pyautogui.hotkey('command', 'k')  # Open search
                print("Command k executed")
                time.sleep(0.5)
                pyautogui.write(value, interval=0.1)
                time.sleep(1)
                pyautogui.hotkey('shift','return')
                pyautogui.press('esc')
                time.sleep(2.5)
                print("Done now")
            else:
                # Execute standard command
                if command not in self.commands:
                    logger.error(f"Command '{command}' not in command list")
                    return False
                    
                logger.info(f"Executing command: {command}")
                keys = self.commands[command]
                pyautogui.hotkey(*keys)
                time.sleep(2.5)
                logger.info(f"Command executed: {command}")
            return True
            
        except pyautogui.FailSafeException:
            logger.error("PyAutoGUI failsafe triggered (mouse moved to corner)")
            return False
        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}")
            return False


def main():
    try:
        logger.info("Starting Spotify automation")
        spotify = SpotifyController()
        
        # Test some commands with error handling
        logger.info("Testing play command")
        if not spotify.execute_command('play', 'Evil Jordan'):
            logger.error("Play command failed")
        else:
            time.sleep(5)
            
            logger.info("Attempting to like the song")
            if not spotify.execute_command('like'):
                logger.error("Like command failed")
            
            logger.info("Moving to next track")
            if not spotify.execute_command('next'):
                logger.error("Next track command failed")
            
            logger.info("Toggle play/pause")
            if not spotify.execute_command('play_pause'):
                logger.error("Play/pause command failed")
            
            logger.info("Show Queue")
            if not spotify.execute_command('queue'):
                logger.error("Queue command failed")
        
        logger.info("Spotify automation completed")
        
    except KeyboardInterrupt:
        logger.info("Spotify automation interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error in main function: {e}")


if __name__ == "__main__":
    main()