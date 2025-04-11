# logger.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_ROTATION_SIZE = 5 * 1024 * 1024  # 5MB
MAX_LOG_BACKUPS = 3
LOG_FILE = Path("logs/spotify_automation.log")

def setup_logging(log_file=LOG_FILE, console_level=logging.INFO, file_level=logging.DEBUG):
    """Set up logging with file rotation and console output."""
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
                logging.FileHandler(str(log_file)),
                logging.StreamHandler()
            ]
        )
        logging.error(f"Error setting up advanced logging: {e}. Using basic logging instead.")
        return logging.getLogger("spotify_automation")

# Create the default logger instance
logger = setup_logging()