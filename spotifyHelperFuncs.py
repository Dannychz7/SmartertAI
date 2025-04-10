# spotifyHelperFuncs.py
import platform
import subprocess
import socket
import signal
import time
import logging
import pyautogui
import psutil
from contextlib import contextmanager
from functools import wraps

from spotifyConfig import *
from logger import logger

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


