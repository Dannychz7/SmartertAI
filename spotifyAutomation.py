# # Automation application for running a spotify song, right now it chooses the first option on search bar
# # Things to add: 
#     # [] Toggle using up and down keys for selecting option (playSongSelect())
#     # [] Play a user playlist
#     # [] Play a song from a user's playlist

import os
import time
import pyautogui

def playSong(song):
    """Open Spotify and play a requested song with busy wait audio."""
    try:
        result = os.popen("pgrep -x Spotify").read().strip()
        if not result:
            print("Opening Spotify...")
            os.system("open -a Spotify")
            time.sleep(5)  # Longer wait for initial launch
        else:
            print("Spotify is already running")
            os.system("osascript -e 'tell application \"Spotify\" to activate'")
            time.sleep(1)  # Increased delay to ensure focus
    except Exception as e:
            print(f"Error ensuring Spotify is running: {e}")
        
    time.sleep(1)

    print("Searching now")
    # Open search bar in Spotify
    pyautogui.hotkey('command', 'k')
    time.sleep(1)  # Let the search bar open

    print("Doing song name now")
    # Type song name
    pyautogui.write(song, interval=0.1)
    time.sleep(1)  # Give it time to type

    # Press Enter to search
    pyautogui.press('return')

class SpotifyController:
    def __init__(self):
        # Command mappings (Mac version - Alt is Option)
        self.commands = {
            # Playback controls
            'play_pause': ('space',),
            'next': ('down',),
            'previous': ('up',),
            'shuffle': ('option', 's'),
            'repeat': ('option', 'r'),
            'mute': ('m',),
            # Navigation
            'home': ('option', 'shift', 'h'),
            'library': ('option', 'shift', '0'),
            'playlists': ('option', 'shift', '1'),
            'podcasts': ('option', 'shift', '2'),
            'artists': ('option', 'shift', '3'),
            'albums': ('option', 'shift', '4'),
            'audiobooks': ('option', 'shift', '5'),
            'search': ('command', 'shift', 'l'),
            'now_playing': ('option', 'shift', 'j'),
            'liked_songs': ('option', 'shift', 's'),
            'made_for_you': ('option', 'shift', 'm'),
            'new_releases': ('option', 'shift', 'n'),
            'charts': ('option', 'shift', 'c'),
            'queue': ('option', 'shift', 'q'),
            # Song management
            'like': ('option', 'shift', 'b'),
            'add_library': ('left',),
            'add_queue': ('right',),
            # Window controls
            'preferences': ('command', ','),
            'context_menu': ('option', 'j'),
            'toggle_now_playing': ('option', 'shift', 'r'),
            'toggle_library': ('option', 'shift', 'l'),
            # App controls
            'logout': ('option', 'shift', 'f6'),
            'select_all': ('command', 'a'),
            'filter': ('command', 'f')
        }

    def ensure_spotify_running(self):
        """Ensure Spotify is running and in focus."""
        try:
            result = os.popen("pgrep -x Spotify").read().strip()
            if not result:
                print("Opening Spotify...")
                os.system("open -a Spotify")
                time.sleep(5)  # Longer wait for initial launch
            else:
                print("Spotify is already running")
                os.system("osascript -e 'tell application \"Spotify\" to activate'")
                time.sleep(1)  # Increased delay to ensure focus
            return True
        except Exception as e:
            print(f"Error ensuring Spotify is running: {e}")
            return False

    def execute_command(self, command, value=None):
        """Execute a Spotify command with optional value."""
        if command not in self.commands and command != 'play':
            print(f"Command '{command}' not recognized")
            return False

        if not self.ensure_spotify_running():
            return False

        if command == 'play' and value:
            # Special handling for play with song search
            time.sleep(0.5)
            pyautogui.hotkey('command', 'tab')  # Open 
            pyautogui.hotkey('command', 'k')  # Open search
            # print("Command k executed")
            time.sleep(0.5)
            pyautogui.write(value, interval=0.1)
            time.sleep(1)
            pyautogui.press('return')
            # print("Done now")
        else:
            print(f"Executing command: {command}")
            keys = self.commands[command]
            pyautogui.hotkey(*keys)
            time.sleep(0.5)

        return True
def main():
    spotify = SpotifyController()
    
    # Test some commands
    print("Testing play command")
    spotify.execute_command('play', 'Die for you')  # Play a song
    time.sleep(5)
    
    print("Attempting to like the song")
    spotify.execute_command('like')  # Like the song
    time.sleep(1)
    
    print("Moving to next track")
    spotify.execute_command('next')  # Next track
    time.sleep(1)
    
    print("Play/pause")
    spotify.execute_command('play_pause')  # Pause/play
    time.sleep(1)
    
    print("Show Queue")
    spotify.execute_command('queue')  # Show queue

if __name__ == "__main__":
    main()