# spotify_config.py
from pathlib import Path

# Timing constants
DEFAULT_TIMEOUT = 15  # seconds
DEFAULT_COMMAND_PAUSE = 0.1  # seconds
DEFAULT_COMMAND_WAIT = 2.5  # seconds
PROCESS_CHECK_INTERVAL = 0.5  # seconds
SPOTIFY_INIT_WAIT = 5  # seconds
SEARCH_BAR_WAIT = 1  # seconds
SONG_SEARCH_INTERVAL = 0.1  # seconds
SEARCH_EXECUTE_WAIT = 1  # seconds

# Logging constants
LOG_ROTATION_SIZE = 5 * 1024 * 1024  # 5MB
MAX_LOG_BACKUPS = 3
LOG_FILE = Path("logs/spotify_automation.log")

# File paths
CONFIG_PATH = "spotify_config.json"

# Retry logic
MAX_RETRIES = 3