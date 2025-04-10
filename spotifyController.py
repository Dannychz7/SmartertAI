# spotify_controller.py
import platform
import pyautogui
import time
import logging
from typing import Dict, Tuple, Optional

from spotifyConfig import *
from logger import logger
from spotifyHelperFuncs import (
    OSNotSupportedError, 
    SpotifyNotFoundError, 
    CommandExecutionError,
    NetworkError,
    retry_decorator,
    check_system_compatibility,
    check_network_connectivity,
    check_pyautogui_functionality,
    is_spotify_process_running,
    launch_spotify,
    activate_spotify_window
)

def is_valid_song_name(song_name):
    """Validate song name input.
    
    Args:
        song_name: Song name to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not song_name or not isinstance(song_name, str):
        return False
        
    # Check for empty string or only whitespace
    if not song_name.strip():
        return False
        
    # Check for reasonable length (arbitrary limits)
    if len(song_name) > 200:
        return False
        
    # Could add more validation as needed
    
    return True


@retry_decorator(max_retries=2)
def playSong(song: str) -> bool:
    """Open Spotify and play a requested song.
    
    Args:
        song: The name of the song to play
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Attempting to play song: {song}")
    
    # Input validation
    if not is_valid_song_name(song):
        logger.error(f"Invalid song name: {song}")
        return False
    
    # Check network connectivity
    if not check_network_connectivity():
        logger.warning("Network connectivity issues detected. Spotify may not function properly.")
    
    # Check if PyAutoGUI is functional
    if not check_pyautogui_functionality():
        logger.error("PyAutoGUI functionality check failed")
        return False
    
    try:
        # Ensure Spotify is running
        if not is_spotify_process_running():
            logger.info("Spotify is not running, launching it...")
            launch_spotify()
        
        # Activate Spotify window
        if not activate_spotify_window():
            logger.error("Failed to activate Spotify window")
            return False
        
        logger.debug("Search command executed")
        pyautogui.hotkey('option', 'shift', 'q') 
        time.sleep(2.5)
        
        pyautogui.hotkey('command', 'k')  # Open search
        logger.debug("Command k executed")
        time.sleep(0.5)
        
        # Type song name directly (no select all/delete steps)
        logger.info(f"Searching for song: {song}")
        pyautogui.write(song, interval=0.1)
        time.sleep(2.5)
        
        # Use the specific key combination that works
        pyautogui.hotkey('shift', 'return')
        time.sleep(1.0)
        pyautogui.press('return')
        
        # In the event the search bar did not close
        pyautogui.press('esc')
        
        logger.info(f"Search executed for: {song}")
        logger.info(f"Song search completed")
        logger.debug("Song search completed")
        
        return True
        
    except pyautogui.FailSafeException:
        logger.error("PyAutoGUI failsafe triggered (mouse moved to corner)")
        return False
    except Exception as e:
        logger.error(f"Error in song search process: {e}", exc_info=True)
        return False


class SpotifyController:
    def __init__(self, failsafe=True, pause=DEFAULT_COMMAND_PAUSE):
        """Initialize the Spotify controller.
        
        Args:
            failsafe: Whether to enable PyAutoGUI failsafe
            pause: Pause between PyAutoGUI commands
        """
        # Check system compatibility
        try:
            compatible, platform_info = check_system_compatibility()
            logger.info(f"System compatibility check passed: {platform_info}")
        except OSNotSupportedError as e:
            logger.critical(f"System compatibility check failed: {e}")
            raise
        
        # Command mappings for different platforms
        self._init_commands()
        
        # Set up PyAutoGUI settings
        pyautogui.FAILSAFE = failsafe
        pyautogui.PAUSE = pause
        
        # Init state
        self.is_initialized = True
        logger.info("SpotifyController initialized successfully")
    
    def _init_commands(self):
        """Initialize command mappings based on platform."""
        system = platform.system()
        
        if system == "Darwin":  # macOS
            self.commands: Dict[str, Tuple[str, ...]] = {
                # Playback controls
                'play_pause': ('space',),
                'next': ('command', 'right'),
                'previous': ('command', 'left'),
                'shuffle': ('command', 's'),
                'repeat': ('command', 'r'),
                'volume_up': ('command', 'up'),
                'volume_down': ('command', 'down'),
                'skip_5_seconds': ('command', 'shift', 'right'),
                'go_back_5_seconds': ('command', 'shift', 'left'),
                
                # Navigation
                'home': ('option', 'shift', 'h'),
                'library': ('option', 'shift', '0'),
                'playlists': ('option', 'shift', '1'),
                'podcasts': ('option', 'shift', '2'),
                'artists': ('option', 'shift', '3'),
                'albums': ('option', 'shift', '4'),
                'audiobooks': ('option', 'shift', '5'),
                'search': ('command', 'k'),
                'now_playing': ('option', 'shift', 'j'),
                'liked_songs': ('option', 'shift', 's'),
                'made_for_you': ('option', 'shift', 'm'),
                'new_releases': ('option', 'shift', 'n'),
                'charts': ('option', 'shift', 'c'),
                'queue': ('option', 'shift', 'q'),
                
                # Song management
                'like': ('option', 'shift', 'b'),
                
                # Window controls
                'settings': ('command', ','),
                'toggle_now_playing': ('option', 'shift', 'r'),
                'toggle_library': ('option', 'shift', 'l'),
                
                # App controls
                'logout': ('option', 'shift', 'f6'),
                'select_all': ('command', 'a'),
                'filter': ('command', 'f')
            }
        elif system == "Windows":
            # Windows key mappings would go here if implemented
            self.commands = {}
            logger.warning("Windows key mappings not implemented")
        elif system == "Linux":
            # Linux key mappings would go here if implemented
            self.commands = {}
            logger.warning("Linux key mappings not implemented")
        else:
            self.commands = {}
            logger.warning(f"No key mappings available for {system}")
    
    @retry_decorator(max_retries=2)
    def ensure_spotify_running(self) -> bool:
        """Ensure Spotify is running and in focus.
        
        Returns:
            bool: True if Spotify is running and focused, False otherwise
        """
        try:
            # Check if Spotify is running
            if not is_spotify_process_running():
                launch_spotify()
            
            # Activate Spotify window
            activate_spotify_window()
            
            return True
            
        except (SpotifyNotFoundError, CommandExecutionError, TimeoutError) as e:
            logger.error(f"Failed to ensure Spotify is running: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error ensuring Spotify is running: {e}")
            return False
    
    def validate_command(self, command: str) -> bool:
        """Validate if a command is supported.
        
        Args:
            command: Command to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Special case for 'play' command
        if command == 'play':
            return True
            
        if command not in self.commands:
            logger.error(f"Command '{command}' not recognized")
            return False
            
        return True
    
    def validate_value(self, value: Optional[str], is_required: bool) -> bool:
        """Validate command value.
        
        Args:
            value: Value to validate
            is_required: Whether value is required
            
        Returns:
            bool: True if valid, False otherwise
        """
        if is_required and (value is None or not isinstance(value, str) or not value.strip()):
            logger.error(f"Invalid or missing required value: {value}")
            return False
            
        return True
    
    @retry_decorator(max_retries=2)
    def execute_command(self, command: str, value: Optional[str] = None) -> bool:
        """Execute a Spotify command with optional value.
        
        Args:
            command: The command to execute
            value: Optional value for commands that require it (e.g., song name)
            
        Returns:
            bool: True if command executed successfully, False otherwise
        """
        if not self.is_initialized:
            logger.error("SpotifyController not properly initialized")
            return False
            
        # Check network connectivity
        if not check_network_connectivity():
            logger.warning("Network connectivity issues detected. Spotify may not function properly.")
        
        # Validate command
        if not self.validate_command(command):
            return False
            
        # Special case for 'play' command with song search
        if command == 'play':
            if not self.validate_value(value, True):
                return False
            return playSong(value)
            
        # Ensure Spotify is running for other commands
        if not self.ensure_spotify_running():
            logger.error("Failed to ensure Spotify is running")
            return False
            
        try:
            # Execute standard command
            logger.info(f"Executing command: {command}")
            keys = self.commands[command]
            pyautogui.hotkey(*keys)
            time.sleep(DEFAULT_COMMAND_WAIT)
            logger.info(f"Command executed: {command}")
            return True
            
        except KeyError:
            logger.error(f"Command '{command}' not found in command list")
            return False
        except pyautogui.FailSafeException:
            logger.error("PyAutoGUI failsafe triggered (mouse moved to corner)")
            return False
        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}")
            return False
