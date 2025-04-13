import logging
from logger import logger
from spotify_utils import (
    play_song, # Needs a string to work [x]
    play_pause, # Standalone [x]
    next_track, # Standalone 
    previous_track, # Standalone
    toggle_shuffle, # Standalone
    toggle_repeat, # standalone
    volume_up, # Standalone
    volume_down, # standalone
    skip_5_seconds, # standalone
    go_back_5_seconds, # standalone
    play_playlist, # Needs, gets playlists id, call get_playlist first to get id)
    play_artist, # needs get_artists id, call get_artists first to get id)
    play_artist_by_name, # standalone
    get_current_track, #standalone
)
from spotifyHelperFuncs import pre_check_spotify_environment

class SpotifyCommandHandler:
    """Handles processing and execution of Spotify voice commands."""
    
    # Dictionary mapping command keywords to functions
    SPOTIFY_COMMANDS = {
        "play": lambda args: play_song(args) if args else print("Please specify a song to play."),
        "resume": lambda _: play_pause(),
        "pause": lambda _: play_pause(),
        "next": lambda _: next_track(),
        "previous": lambda _: previous_track(),
        "back": lambda _: previous_track(),
        "shuffle": lambda _: toggle_shuffle(),
        "repeat": lambda _: toggle_repeat(),
        "volume up": lambda _: volume_up(),
        "volume down": lambda _: volume_down(),
        "skip": lambda _: skip_5_seconds(),
        "rewind": lambda _: go_back_5_seconds(),
        "playlist": lambda args: play_playlist(args) if args else print("Please specify a playlist."),
        "artist": lambda args: play_artist_by_name(args) if args else print("Please specify an artist."),
        "current": lambda _: get_current_track(),
    }
    
    @staticmethod
    def is_spotify_command(command):
        """
        Check if the command is Spotify-related.
        
        Args:
            command (str): The user's voice command as text
            
        Returns:
            bool: True if this is a Spotify command, False otherwise
        """
        command = command.lower()
        return ("spotify" in command or 
                "music" in command or 
                any(cmd in command for cmd in SpotifyCommandHandler.SPOTIFY_COMMANDS.keys()))
    
    @staticmethod
    def handle_command(command):
        """
        Process and execute a Spotify voice command.
        
        Args:
            command (str): The user's voice command as text
        
        Returns:
            bool: True if command was successfully processed, False otherwise
        """
        try:
            # Make sure Spotify environment is properly set up
            pre_check_spotify_environment()
            
            command = command.lower().strip()
            command = command.replace("on spotify", "").strip()
            logger.info(f"Processing Spotify command: {command}")
            
            # Handle play command with argument
            if "play " in command:
                cmd = "play"
                args = command.split("play ", 1)[1].strip()
                print(f"Playing: {args}")
                SpotifyCommandHandler.SPOTIFY_COMMANDS[cmd](args)
                return True
                
            # Handle playlist command
            elif "playlist " in command:
                cmd = "playlist"
                args = command.split("playlist ", 1)[1].strip()
                print(f"Playing playlist: {args}")
                SpotifyCommandHandler.SPOTIFY_COMMANDS[cmd](args)
                return True
                
            # Handle artist command
            elif "artist " in command:
                cmd = "artist"
                args = command.split("artist ", 1)[1].strip()
                print(f"Playing artist: {args}")
                SpotifyCommandHandler.SPOTIFY_COMMANDS[cmd](args)
                return True
                
            # Handle other commands without arguments
            else:
                for cmd_text in SpotifyCommandHandler.SPOTIFY_COMMANDS.keys():
                    if cmd_text in command:
                        print(f"Executing Spotify command: {cmd_text}")
                        SpotifyCommandHandler.SPOTIFY_COMMANDS[cmd_text](None)
                        return True
            
            # If we get here, we couldn't find a matching command
            print(f"Unrecognized Spotify command: '{command}'")
            return False
                
        except Exception as e:
            logger.error(f"Error processing Spotify command '{command}': {e}")
            print(f"Error with Spotify command: {str(e)}")
            return False