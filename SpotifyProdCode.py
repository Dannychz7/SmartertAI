import os
import time
import platform
import pyautogui
import subprocess
import logging
from typing import Optional, Tuple, List, Dict, Any, Union
from pathlib import Path
import psutil  # Added for better process management
import socket  # Added for network connectivity checks
import signal  # Added for proper process termination
import sys
import argparse  # Added for command-line argument support
from contextlib import contextmanager  # Added for timeout context management
from functools import wraps  # Added for decorator support

# Constants for better maintainability
DEFAULT_TIMEOUT = 15  # seconds
DEFAULT_COMMAND_PAUSE = 0.1  # seconds
DEFAULT_COMMAND_WAIT = 2.5  # seconds
LOG_ROTATION_SIZE = 5 * 1024 * 1024  # 5MB
MAX_LOG_BACKUPS = 3
CONFIG_PATH = "spotify_config.json"
MAX_RETRIES = 3
PROCESS_CHECK_INTERVAL = 0.5  # seconds
SPOTIFY_INIT_WAIT = 5  # seconds
SEARCH_BAR_WAIT = 1  # seconds
SONG_SEARCH_INTERVAL = 0.1  # seconds
SEARCH_EXECUTE_WAIT = 1  # seconds


class OSNotSupportedError(Exception):
    """Exception raised when current OS is not supported."""
    pass


class SpotifyNotFoundError(Exception):
    """Exception raised when Spotify cannot be found or launched."""
    pass


class CommandExecutionError(Exception):
    """Exception raised when a command execution fails."""
    pass


class NetworkError(Exception):
    """Exception raised when network connectivity issues are detected."""
    pass


@contextmanager
def timeout_context(seconds):
    """Context manager for timeout operations.
    
    Args:
        seconds: Maximum time to wait in seconds
        
    Yields:
        None
        
    Raises:
        TimeoutError: If the operation times out
    """
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")

    original_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, original_handler)


def retry_decorator(max_retries=MAX_RETRIES, retry_delay=1):
    """Decorator to retry a function on failure.
    
    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            last_exception = None
            
            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except (subprocess.SubprocessError, pyautogui.PyAutoGUIException, TimeoutError) as e:
                    last_exception = e
                    attempts += 1
                    if attempts < max_retries:
                        logger.warning(f"Attempt {attempts} failed: {e}. Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        break
            
            logger.error(f"Function {func.__name__} failed after {max_retries} attempts. Last error: {last_exception}")
            raise last_exception
            
        return wrapper
    return decorator


# Set up logging with rotation
def setup_logging(log_file="spotify_automation.log", console_level=logging.INFO, file_level=logging.DEBUG):
    """Set up logging with file rotation and console output.
    
    Args:
        log_file: Path to log file
        console_level: Logging level for console output
        file_level: Logging level for file output
        
    Returns:
        Logger object
    """
    try:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create logger
        logger = logging.getLogger("spotify_automation")
        logger.setLevel(logging.DEBUG)  # Capture all levels
        logger.propagate = False  # Don't propagate to root logger
        
        # Clear any existing handlers
        if logger.handlers:
            logger.handlers.clear()
        
        # File handler with rotation
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=LOG_ROTATION_SIZE,
            backupCount=MAX_LOG_BACKUPS
        )
        file_handler.setLevel(file_level)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        return logger
    except Exception as e:
        # Fall back to basic logging if advanced setup fails
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        logging.error(f"Error setting up advanced logging: {e}. Using basic logging instead.")
        return logging.getLogger("spotify_automation")


# Initialize logger
logger = setup_logging()


def check_system_compatibility():
    """Check if the current system is compatible with this script.
    
    Returns:
        tuple: (is_compatible, platform_info)
        
    Raises:
        OSNotSupportedError: If the OS is not supported
    """
    system = platform.system()
    if system == "Darwin":  # macOS
        version = platform.mac_ver()[0]
        logger.info(f"Running on macOS version {version}")
        return True, f"macOS {version}"
    elif system == "Windows":
        # Current implementation only supports macOS
        logger.error("Windows support is not implemented")
        raise OSNotSupportedError("This script currently only supports macOS")
    elif system == "Linux":
        # Current implementation only supports macOS
        logger.error("Linux support is not implemented")
        raise OSNotSupportedError("This script currently only supports macOS")
    else:
        logger.error(f"Unsupported operating system: {system}")
        raise OSNotSupportedError(f"Unsupported operating system: {system}")


def check_network_connectivity(host="api.spotify.com", port=443, timeout=5):
    """Check if network connectivity to Spotify services is available.
    
    Args:
        host: Host to check connectivity to
        port: Port to connect on
        timeout: Connection timeout in seconds
        
    Returns:
        bool: True if connected, False otherwise
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as e:
        logger.warning(f"Network connectivity issue: {e}")
        return False


def check_pyautogui_functionality():
    """Check if PyAutoGUI can function properly.
    
    Returns:
        bool: True if functional, False otherwise
    """
    try:
        screen_size = pyautogui.size()
        logger.debug(f"Screen size detected: {screen_size}")
        
        # Check if we can get mouse position
        mouse_pos = pyautogui.position()
        logger.debug(f"Mouse position: {mouse_pos}")
        
        return True
    except Exception as e:
        logger.error(f"PyAutoGUI functionality check failed: {e}")
        return False


def is_spotify_process_running():
    """Check if Spotify process is running.
    
    Returns:
        bool: True if running, False otherwise
    """
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            result = subprocess.run(
                ["pgrep", "-x", "Spotify"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                timeout=5
            )
            return result.returncode == 0
        elif system == "Windows":
            # Windows implementation (if needed in future)
            procs = [p.name() for p in psutil.process_iter(['name'])]
            return "Spotify.exe" in procs
        elif system == "Linux":
            # Linux implementation (if needed in future)
            procs = [p.name() for p in psutil.process_iter(['name'])]
            return "spotify" in procs
        return False
    except (subprocess.SubprocessError, psutil.Error) as e:
        logger.error(f"Error checking if Spotify is running: {e}")
        return False


@retry_decorator(max_retries=3)
def launch_spotify():
    """Launch Spotify application.
    
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        SpotifyNotFoundError: If Spotify cannot be launched
        TimeoutError: If Spotify launch times out
    """
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            if is_spotify_process_running():
                logger.info("Spotify is already running")
                return True
                
            logger.info("Launching Spotify...")
            subprocess.run(["open", "-a", "Spotify"], check=True, timeout=5)
            
            # Wait for Spotify to launch
            start_time = time.time()
            while time.time() - start_time < DEFAULT_TIMEOUT:
                if is_spotify_process_running():
                    logger.info(f"Spotify launched successfully, waiting {SPOTIFY_INIT_WAIT}s for initialization")
                    time.sleep(SPOTIFY_INIT_WAIT)  # Wait for Spotify to initialize
                    return True
                time.sleep(PROCESS_CHECK_INTERVAL)
                
            raise TimeoutError(f"Spotify did not launch within {DEFAULT_TIMEOUT} seconds")
            
        else:
            raise OSNotSupportedError(f"Launching Spotify on {system} is not implemented")
            
    except subprocess.SubprocessError as e:
        logger.error(f"Error launching Spotify: {e}")
        raise SpotifyNotFoundError(f"Failed to launch Spotify: {e}")


@retry_decorator(max_retries=2)
def activate_spotify_window():
    """Bring Spotify window to foreground.
    
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        CommandExecutionError: If activation fails
    """
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            subprocess.run(
                ["osascript", "-e", 'tell application "Spotify" to activate'],
                check=True,
                timeout=5
            )
            time.sleep(1)  # Wait for window to gain focus
            return True
        else:
            raise OSNotSupportedError(f"Activating Spotify on {system} is not implemented")
            
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to activate Spotify window: {e}")
        raise CommandExecutionError(f"Failed to activate Spotify window: {e}")


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


def parse_arguments():
    """Parse command-line arguments.
    
    Returns:
        Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Spotify Automation Tool")
    parser.add_argument("--song", type=str, help="Song to play")
    parser.add_argument("--command", type=str, help="Command to execute")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--check-only", action="store_true", help="Check system compatibility and exit")
    parser.add_argument("--list-commands", action="store_true", help="List available commands and exit")
    parser.add_argument("--test", action="store_true", help="Run comprehensive test suite")  # Added here
    return parser.parse_args()


def list_commands():
    """List all available commands."""
    try:
        spotify = SpotifyController()
        print("\nAvailable Spotify Commands:")
        print("==========================")
        
        categories = {
            "Playback": ['play_pause', 'next', 'previous', 'shuffle', 'repeat', 
                        'volume_up', 'volume_down', 'skip_5_seconds', 'go_back_5_seconds'],
            "Navigation": ['home', 'library', 'playlists', 'podcasts', 'artists', 'albums', 
                          'audiobooks', 'search', 'now_playing', 'liked_songs', 'made_for_you', 
                          'new_releases', 'charts', 'queue'],
            "Song Management": ['like'],
            "Window Controls": ['settings', 'toggle_now_playing', 'toggle_library'],
            "App Controls": ['logout', 'select_all', 'filter'],
            "Special Commands": ['play']
        }
        
        for category, cmds in categories.items():
            print(f"\n{category}:")
            for cmd in cmds:
                if cmd == 'play':
                    print(f"  {cmd} <song_name> - Play a specific song")
                elif cmd in spotify.commands:
                    keys = spotify.commands[cmd]
                    print(f"  {cmd} - Keys: {' + '.join(keys)}")
                else:
                    print(f"  {cmd} - Not implemented for this platform")
    except Exception as e:
        print(f"Error listing commands: {e}")




def run_test_suite():
    """Run comprehensive test suite for Spotify automation."""
    try:
        spotify = SpotifyController()
        
        # Track test results
        results = {
            "passed": 0,
            "failed": 0,
            "skipped": 0
        }
        
        def log_test_result(test_name, result, error=None):
            """Log test result and update counts."""
            if result == "PASS":
                logger.info(f"✓ TEST PASSED: {test_name}")
                results["passed"] += 1
            elif result == "FAIL":
                logger.error(f"✗ TEST FAILED: {test_name}" + (f" - {error}" if error else ""))
                results["failed"] += 1
            elif result == "SKIP":
                logger.warning(f"⚠ TEST SKIPPED: {test_name}" + (f" - {error}" if error else ""))
                results["skipped"] += 1
                
        # ======= SYSTEM TESTS =======
        logger.info("\n========= SYSTEM TESTS =========")
        
        # Test 1: System compatibility
        try:
            compatible, platform_info = check_system_compatibility()
            log_test_result("System compatibility check", "PASS" if compatible else "FAIL")
        except Exception as e:
            log_test_result("System compatibility check", "FAIL", str(e))
            
        # Test 2: PyAutoGUI functionality
        try:
            pyautogui_functional = check_pyautogui_functionality()
            log_test_result("PyAutoGUI functionality", "PASS" if pyautogui_functional else "FAIL")
        except Exception as e:
            log_test_result("PyAutoGUI functionality", "FAIL", str(e))
            
        # Test 3: Network connectivity
        try:
            network_ok = check_network_connectivity()
            log_test_result("Network connectivity", "PASS" if network_ok else "FAIL")
        except Exception as e:
            log_test_result("Network connectivity", "FAIL", str(e))
            
        # ======= SPOTIFY PROCESS TESTS =======
        logger.info("\n========= SPOTIFY PROCESS TESTS =========")
        
        # Test 4: Spotify process detection
        try:
            spotify_running = is_spotify_process_running()
            log_test_result("Spotify process detection", "PASS", 
                          f"Spotify is {'running' if spotify_running else 'not running'}")
        except Exception as e:
            log_test_result("Spotify process detection", "FAIL", str(e))
            
        # Test 5: Spotify launch
        try:
            if not is_spotify_process_running():
                launch_success = launch_spotify()
                log_test_result("Spotify launch", "PASS" if launch_success else "FAIL")
            else:
                log_test_result("Spotify launch", "SKIP", "Spotify already running")
        except Exception as e:
            log_test_result("Spotify launch", "FAIL", str(e))
            
        # Test 6: Spotify window activation
        try:
            activate_success = activate_spotify_window()
            log_test_result("Spotify window activation", "PASS" if activate_success else "FAIL")
        except Exception as e:
            log_test_result("Spotify window activation", "FAIL", str(e))
            
        # ======= INPUT VALIDATION TESTS =======
        logger.info("\n========= INPUT VALIDATION TESTS =========")
        
        # Test 7: Song name validation
        invalid_songs = [
            None,                    # None value
            "",                      # Empty string
            "   ",                   # Whitespace only
            12345,                   # Wrong type (int)
            "a" * 300,               # Too long
            {"name": "Bad Input"},   # Wrong type (dict)
            "<script>alert(1)</script>"  # Potential injection
        ]
        
        for i, bad_song in enumerate(invalid_songs):
            try:
                result = is_valid_song_name(bad_song)
                should_be_invalid = not result
                log_test_result(f"Invalid song rejection #{i+1}", 
                              "PASS" if should_be_invalid else "FAIL",
                              f"Input: {type(bad_song).__name__}")
            except Exception as e:
                log_test_result(f"Invalid song rejection #{i+1}", "PASS", 
                              f"Exception raised as expected: {e}")
                
        # Test 8: Command validation
        invalid_commands = [
            None,                    # None value
            "",                      # Empty string
            "nonexistent_command",   # Unknown command
            123,                     # Wrong type
            ["play", "pause"],       # Wrong type
            "<script>alert(1)</script>"  # Potential injection
        ]
        
        for i, bad_command in enumerate(invalid_commands):
            try:
                result = spotify.validate_command(bad_command)
                log_test_result(f"Invalid command rejection #{i+1}", 
                              "PASS" if not result else "FAIL",
                              f"Input: {type(bad_command).__name__}")
            except Exception as e:
                # If it raises exception for invalid input, that's also acceptable
                log_test_result(f"Invalid command rejection #{i+1}", "PASS", 
                              f"Exception raised as expected: {e}")
                
        # ======= COMMAND EXECUTION TESTS =======
        logger.info("\n========= COMMAND EXECUTION TESTS =========")
        
        # Test 9: Basic commands (without Spotify control)
        basic_commands = [
            'home',
            'library',
            # 'search',
            'settings'
        ]
        
        for cmd in basic_commands:
            try:
                result = spotify.execute_command(cmd)
                log_test_result(f"Basic command: {cmd}", "PASS" if result else "FAIL")
                time.sleep(1)  # Brief pause between commands
            except Exception as e:
                log_test_result(f"Basic command: {cmd}", "FAIL", str(e))
                
        # ======= SONG PLAYBACK STRESS TESTS =======
        logger.info("\n========= SONG PLAYBACK STRESS TESTS =========")
        
        # Test 10: Valid song playback
        test_songs = [
            "Bohemian Rhapsody",         # Popular song
            "Die for you",               # Previous test song
            "Stairway to Heaven",        # Long title
            "Shape of You Ed Sheeran"    # Artist and title
        ]
        
        for song in test_songs:
            try:
                result = spotify.execute_command('play', song)
                log_test_result(f"Valid song play: '{song}'", "PASS" if result else "FAIL")
                # Wait a moment to see if playback starts
                time.sleep(5)
                
                # Try a playback control action if song play worked
                if result:
                    play_pause = spotify.execute_command('play_pause')
                    log_test_result(f"Play/pause after '{song}'", 
                                  "PASS" if play_pause else "FAIL")
                    time.sleep(1)
            except Exception as e:
                log_test_result(f"Valid song play: '{song}'", "FAIL", str(e))
                
        # Test 11: Special characters in song titles
        special_char_songs = [
            "AC/DC Highway to Hell",     # Forward slash
            "Pink Floyd - Another Brick in the Wall",  # Dash
            "Let's Go (Calvin Harris)",   # Apostrophe and parentheses
            "99 Problems"                 # Numbers
        ]
        
        for song in special_char_songs:
            try:
                result = spotify.execute_command('play', song)
                log_test_result(f"Special chars song: '{song}'", "PASS" if result else "FAIL")
                time.sleep(3)  # Shorter wait
            except Exception as e:
                log_test_result(f"Special chars song: '{song}'", "FAIL", str(e))
                
        # ======= RAPID COMMAND TESTS =======
        logger.info("\n========= RAPID COMMAND TESTS =========")
        
        # Test 12: Rapid command sequence (stress test)
        rapid_commands = [
            ('play_pause', "Rapid play/pause"),
            ('next', "Rapid next track"),
            ('volume_up', "Volume up"),
            ('volume_up', "Volume up again"),
            ('volume_down', "Volume down"),
            ('play_pause', "Play/pause again")
        ]
        
        logger.info("Starting rapid command sequence (stress test)")
        for cmd, desc in rapid_commands:
            try:
                result = spotify.execute_command(cmd)
                log_test_result(f"Rapid command: {desc}", "PASS" if result else "FAIL")
                time.sleep(0.5)  # Very short delay to stress test
            except Exception as e:
                log_test_result(f"Rapid command: {desc}", "FAIL", str(e))
                
        # ======= RECOVERY TESTS =======
        logger.info("\n========= RECOVERY TESTS =========")
        
        # Test 13: Recovery after potential errors
        try:
            # Force Spotify to background then try to use it
            pyautogui.hotkey('command', 'tab')  # Switch away from Spotify
            time.sleep(1)
            
            # Try to play song - should recover by activating window
            recovery_result = spotify.execute_command('play', "Telescope")
            log_test_result("Recovery after focus loss", "PASS" if recovery_result else "FAIL")
        except Exception as e:
            log_test_result("Recovery after focus loss", "FAIL", str(e))
            
        # ======= PRINT TEST SUMMARY =======
        logger.info("\n========= TEST SUMMARY =========")
        logger.info(f"Tests passed: {results['passed']}")
        logger.info(f"Tests failed: {results['failed']}")
        logger.info(f"Tests skipped: {results['skipped']}")
        logger.info(f"Total tests: {results['passed'] + results['failed'] + results['skipped']}")
        
        return results
    except Exception as e:
        logger.critical(f"Test suite execution failed: {e}", exc_info=True)
        return {"passed": 0, "failed": 1, "skipped": 0}


def main():
    """Main function."""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Add test suite argument
    # parser = argparse.ArgumentParser(description="Spotify Automation Tool")
    # parser.add_argument("--test", action="store_true", help="Run comprehensive test suite")
    
    # Configure logging level based on arguments
    if args.debug:
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    try:
        # Check system compatibility
        if args.check_only:
            compatible, platform_info = check_system_compatibility()
            print(f"System compatibility: {platform_info}")
            if compatible:
                print("PyAutoGUI functionality:", "OK" if check_pyautogui_functionality() else "FAILED")
                print("Network connectivity:", "OK" if check_network_connectivity() else "WARNING")
                print("Spotify installation:", "FOUND" if is_spotify_process_running() else "NOT RUNNING")
            sys.exit(0)
        
        # List commands if requested
        if args.list_commands:
            list_commands()
            sys.exit(0)
            
        # # Run test suite if requested
        # if args.test:
        #     logger.info("Running comprehensive test suite")
        #     results = run_test_suite()
        #     sys.exit(0 if results["failed"] == 0 else 1)
        
        logger.info("Starting Spotify automation")
        
        # Create controller instance
        spotify = SpotifyController()
        
        # Execute command if specified
        if args.command:
            if args.command == 'play' and args.song:
                if spotify.execute_command('play', args.song):
                    logger.info(f"Successfully played song: {args.song}")
                else:
                    logger.error(f"Failed to play song: {args.song}")
            elif spotify.execute_command(args.command):
                logger.info(f"Successfully executed command: {args.command}")
            else:
                logger.error(f"Failed to execute command: {args.command}")
            sys.exit(0)
        
        # # Default test routine
        # logger.info("Running default test routine")
        
        # # Test with a specific song first
        # logger.info("Testing play command with specific song")
        # if not spotify.execute_command('play', "Die for you"):
        #     logger.error("Initial song play test failed")
        # time.sleep(5)
        
        # # Test boundary cases
        # boundary_tests = [
        #     # Case: Empty string (should fail gracefully)
        #     {
        #         "action": lambda: spotify.execute_command('play', ""),
        #         "description": "Empty song name test",
        #         "expected": False
        #     },
        #     # Case: Very long song name
        #     {
        #         "action": lambda: spotify.execute_command('play', "This is an extremely long song name that might cause issues with the search functionality and potentially break something if the system doesn't handle it properly"),
        #         "description": "Very long song name test",
        #         "expected": False
        #     },
        #     # Case: Song with special characters
        #     {
        #         "action": lambda: spotify.execute_command('play', "AC/DC - Back in Black"),
        #         "description": "Special characters in song name",
        #         "expected": True
        #     },
        #     # Case: Non-existent command
        #     {
        #         "action": lambda: spotify.execute_command('nonexistent_command'),
        #         "description": "Non-existent command test",
        #         "expected": False
        #     },
        #     # Case: Valid song play
        #     {
        #         "action": lambda: spotify.execute_command('play', "Telescope"),
        #         "description": "Standard song play test",
        #         "expected": True
        #     }
        # ]
        
        # # Run boundary tests
        # for test in boundary_tests:
        #     logger.info(f"Running test: {test['description']}")
        #     try:
        #         result = test["action"]()
        #         if result == test["expected"]:
        #             logger.info(f"✓ Test passed: {test['description']}")
        #         else:
        #             logger.error(f"✗ Test failed: {test['description']} - Got {result}, expected {test['expected']}")
        #     except Exception as e:
        #         logger.error(f"✗ Test failed with exception: {test['description']} - {e}")
            
        #     # Brief pause between tests
        #     time.sleep(2)
        
        # # Test standard command sequence after successful song play
        # if spotify.execute_command('play', "Telescope"):
        #     logger.info("Song play successful, testing command sequence")
        #     time.sleep(5)
            
        #     # Test sequence of commands
        #     tests = [
        #         ('like', "Liking the song"),
        #         ('next', "Moving to next track"),
        #         ('previous', "Moving to previous track"),
        #         ('play_pause', "Toggle play/pause"),
        #         ('play_pause', "Toggle play/pause again"),
        #         ('volume_up', "Increasing volume"),
        #         ('volume_down', "Decreasing volume"),
        #         ('queue', "Show Queue")
        #     ]
            
        #     for cmd, desc in tests:
        #         logger.info(desc)
        #         if not spotify.execute_command(cmd):
        #             logger.error(f"{desc} failed")
        #         time.sleep(2)
                
        #     # Test potential error recovery
        #     logger.info("Testing error recovery")
        #     # Switch focus away from Spotify
        #     pyautogui.hotkey('command', 'tab')
        #     time.sleep(1)
        #     # Try to execute a command - should recover by refocusing Spotify
        #     if spotify.execute_command('play_pause'):
        #         logger.info("✓ Recovery test passed")
        #     else:
        #         logger.error("✗ Recovery test failed")
        # else:
        #     logger.error("Main song play test failed, skipping command sequence tests")
        
        # logger.info("Spotify automation testing completed")
        
    except KeyboardInterrupt:
        logger.info("Spotify automation interrupted by user")
    except OSNotSupportedError as e:
        logger.critical(f"OS not supported: {e}")
        sys.exit(1)
    except SpotifyNotFoundError as e:
        logger.critical(f"Spotify not found: {e}")
        sys.exit(2)
    except Exception as e:
        logger.critical(f"Unexpected error in main function: {e}", exc_info=True)
        sys.exit(3)