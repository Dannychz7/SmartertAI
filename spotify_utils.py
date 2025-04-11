# Helper Functions
# check_devices() $
# get_playlists() $
# get_artists()   $
# search_song(str query) $
# start_playback(songUri) $
    
# High level Funcs
# play_pause() $
# next_track() $
# previous_track() $
# toggle_shuffle() $
# toggle_repeat() $ 
# volume_up() $
# volume_down() $
# skip_5_seconds() $
# go_back_5_seconds() $
# play_playlist(playlistId)    
# play_artist(artistID)
# playsong(str song name)
# get_current_track()

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET
from fuzzywuzzy import fuzz
from logger import logger
from spotifyHelperFuncs import pre_check_spotify_environment

# Global sleep durations (in seconds)
helperSleep = 0.3
highLevelSleep = 0.5
playSongSleep = 1.0

# Replace with your Spotify developer credentials
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8888/callback'

# Define the scope needed for playback control and accessing saved tracks
SCOPE = (
    'user-library-read '  # Required to read saved tracks
    'user-read-playback-state '  # Required to read the playback state
    'user-modify-playback-state '  # Required to modify playback state
    'playlist-read-private '  # Required to access private playlists (optional)
    'playlist-read-collaborative '  # Access to collaborative playlists
    'user-read-currently-playing '  # Required to access currently playing track
    'user-top-read '  # Required to access top artists/tracks
)

logger.info("Initializing Spotify API connection")
try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE
    ))
    logger.info("Spotify API connection established successfully")
except Exception as e:
    logger.error(f"Failed to initialize Spotify API connection: {e}")
    raise

def wait(category="helper"):
    if category == "helper":
        time.sleep(helperSleep)
    elif category == "high":
        time.sleep(highLevelSleep)
    elif category == "play":
        time.sleep(playSongSleep)

# --- Playback Controls ---
def play_liked_songs(limit=100):
    """
    Play user's liked songs with proper error handling
    
    Args:
        limit (int): Maximum number of liked songs to play (default: 100)
        
    Returns:
        bool: True if playback started successfully, False otherwise
    """
    logger.info(f"Attempting to play liked songs (limit: {limit})")
    # Initialize list to store track URIs
    track_uris = []
    
    try:
        # Fetch liked songs in pages
        offset = 0
        while True:
            logger.debug(f"Fetching liked songs batch with offset {offset}")
            results = sp.current_user_saved_tracks(limit=20, offset=offset)
            tracks = results['items']
            
            if not tracks:
                logger.debug("No more tracks found in liked songs")
                break
            
            # Extract the URI of each track and add to the list
            track_uris.extend([track['track']['uri'] for track in tracks])
            logger.debug(f"Added {len(tracks)} tracks, total tracks: {len(track_uris)}")
            
            # Update offset for next page of results
            offset += 20
            
            # Stop if we have collected enough tracks
            if len(track_uris) >= limit:
                logger.debug(f"Reached maximum track limit: {limit}")
                break

        if track_uris:
            # Start playback of the liked songs
            logger.info(f"Starting playback of {len(track_uris[:limit])} liked songs")
            sp.start_playback(uris=track_uris[:limit])
            print(f"Playing your top {len(track_uris[:limit])} liked songs")
            return True
        else:
            logger.warning("No liked songs found")
            print("No liked songs found in your library")
            return False
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify API error playing liked songs: {e}")
        print(f"Spotify error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error playing liked songs: {e}")
        print(f"Error playing liked songs: {e}")
        return False


def play_pause():
    """
    Toggle between play and pause states
    
    Returns:
        tuple: (bool, str) - Success status and state message
    """
    logger.info("Toggling play/pause")
    try:
        playback = sp.current_playback()
        if not playback:
            logger.warning("No active playback session found")
            print("No active playback session found")
            return False, "No active playback"
        
        if playback['is_playing']:
            logger.debug("Currently playing, pausing playback")
            sp.pause_playback()
            print("Playback paused")
            
            wait("high")
            return True, "paused"
        else:
            logger.debug("Currently paused, resuming playback")
            sp.start_playback()
            print("Playback resumed")
            wait("high")
            return True, "playing"
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify API error toggling play/pause: {e}")
        print(f"Spotify error: {e}")
        return False, str(e)
    except Exception as e:
        logger.error(f"Error toggling play/pause: {e}")
        print(f"Error toggling play/pause: {e}")
        return False, str(e)


def next_track():
    """
    Skip to the next track in the queue
    
    Returns:
        bool: True if skipped successfully, False otherwise
    """
    logger.info("Skipping to next track")
    try:
        playback = sp.current_playback()
        if not playback:
            logger.warning("No active playback session found")
            print("No active playback session found")
            return False
            
        if 'next_tracks' in playback and playback['next_tracks']:
            sp.next_track()
            logger.debug("Skipped to next track successfully")
            print("Skipped to next track")
            
            wait("high")
            return True
        else:
            logger.warning("No next track available")
            print("No next track available in the queue")
            return False
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify API error skipping to next track: {e}")
        print(f"Spotify error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error skipping to next track: {e}")
        print(f"Error skipping to next track: {e}")
        return False


def previous_track():
    """
    Go back to the previous track
    
    Returns:
        bool: True if operation was successful, False otherwise
    """
    logger.info("Going to previous track")
    try:
        playback = sp.current_playback()
        if not playback:
            logger.warning("No active playback session found")
            print("No active playback session found")
            return False
            
        if 'previous_tracks' in playback and playback['previous_tracks']:
            sp.previous_track()
            logger.debug("Went to previous track successfully")
            print("Went to previous track")
            
            wait("high")
            return True
        else:
            logger.warning("No previous track available")
            print("No previous track available in history")
            return False
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify API error going to previous track: {e}")
        print(f"Spotify error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error going to previous track: {e}")
        print(f"Error going to previous track: {e}")
        return False


def toggle_shuffle():
    """
    Toggle shuffle mode on/off
    
    Returns:
        tuple: (bool, bool) - Success status and new shuffle state
    """
    logger.info("Toggling shuffle mode")
    try:
        playback = sp.current_playback()
        if not playback:
            logger.warning("No active playback session found")
            print("No active playback session found")
            return False, None
            
        current_state = playback['shuffle_state']
        new_state = not current_state
        sp.shuffle(new_state)
        logger.debug(f"Shuffle mode changed from {current_state} to {new_state}")
        print(f"Shuffle mode {'enabled' if new_state else 'disabled'}")
        
        wait("high")
        return True, new_state
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify API error toggling shuffle mode: {e}")
        print(f"Spotify error: {e}")
        return False, None
    except Exception as e:
        logger.error(f"Error toggling shuffle mode: {e}")
        print(f"Error toggling shuffle mode: {e}")
        return False, None


def toggle_repeat():
    """
    Toggle repeat mode (off -> track -> context -> off)
    
    Returns:
        tuple: (bool, str) - Success status and new repeat state
    """
    logger.info("Toggling repeat mode")
    try:
        playback = sp.current_playback()
        if not playback:
            logger.warning("No active playback session found")
            print("No active playback session found")
            return False, None
            
        state = playback['repeat_state']
        new_state = 'track' if state == 'off' else 'context' if state == 'track' else 'off'
        sp.repeat(new_state)
        
        # Create user-friendly message
        state_message = {
            'off': 'Repeat off',
            'track': 'Repeating current track',
            'context': 'Repeating playlist/album'
        }
        
        logger.debug(f"Repeat mode changed from '{state}' to '{new_state}'")
        print(state_message[new_state])
        
        wait("high")
        return True, new_state
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify API error toggling repeat mode: {e}")
        print(f"Spotify error: {e}")
        return False, None
    except Exception as e:
        logger.error(f"Error toggling repeat mode: {e}")
        print(f"Error toggling repeat mode: {e}")
        return False, None


def volume_up(step=10):
    """
    Increase volume by specified percentage
    
    Args:
        step (int): Percentage to increase volume (default: 10)
        
    Returns:
        tuple: (bool, int) - Success status and new volume level
    """
    logger.info(f"Increasing volume by {step}%")
    try:
        playback = sp.current_playback()
        if not playback:
            logger.warning("No active playback session found")
            print("No active playback session found")
            return False, None
            
        current_volume = playback['device']['volume_percent']
        new_volume = min(100, current_volume + step)
        sp.volume(new_volume)
        logger.debug(f"Volume increased from {current_volume}% to {new_volume}%")
        print(f"Volume: {new_volume}%")
        
        wait("high")
        return True, new_volume
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify API error increasing volume: {e}")
        print(f"Spotify error: {e}")
        return False, None
    except Exception as e:
        logger.error(f"Error increasing volume: {e}")
        print(f"Error increasing volume: {e}")
        return False, None


def volume_down(step=10):
    """
    Decrease volume by specified percentage
    
    Args:
        step (int): Percentage to decrease volume (default: 10)
        
    Returns:
        tuple: (bool, int) - Success status and new volume level
    """
    logger.info(f"Decreasing volume by {step}%")
    try:
        playback = sp.current_playback()
        if not playback:
            logger.warning("No active playback session found")
            print("No active playback session found")
            return False, None
            
        current_volume = playback['device']['volume_percent']
        new_volume = max(0, current_volume - step)
        sp.volume(new_volume)
        logger.debug(f"Volume decreased from {current_volume}% to {new_volume}%")
        print(f"Volume: {new_volume}%")
        
        wait("high")
        return True, new_volume
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify API error decreasing volume: {e}")
        print(f"Spotify error: {e}")
        return False, None
    except Exception as e:
        logger.error(f"Error decreasing volume: {e}")
        print(f"Error decreasing volume: {e}")
        return False, None


def skip_5_seconds():
    """
    Skip forward 5 seconds in the current track
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Skipping forward 5 seconds")
    try:
        playback = sp.current_playback()
        if not playback:
            logger.warning("No active playback session found")
            print("No active playback session found")
            return False
            
        current_position = playback['progress_ms']
        new_position = current_position + 5000
        sp.seek_track(new_position)
        logger.debug(f"Position changed from {current_position}ms to {new_position}ms")
        print("Skipped forward 5 seconds")
        
        wait("high")
        return True
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify API error skipping forward: {e}")
        print(f"Spotify error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error skipping forward: {e}")
        print(f"Error skipping forward: {e}")
        return False


def go_back_5_seconds():
    """
    Go back 5 seconds in the current track
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Going back 5 seconds")
    try:
        playback = sp.current_playback()
        if not playback:
            logger.warning("No active playback session found")
            print("No active playback session found")
            return False
            
        current_position = playback['progress_ms']
        new_position = max(0, current_position - 5000)
        sp.seek_track(new_position)
        logger.debug(f"Position changed from {current_position}ms to {new_position}ms")
        print("Went back 5 seconds")
        
        wait("high")
        return True
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify API error going back: {e}")
        print(f"Spotify error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error going back: {e}")
        print(f"Error going back: {e}")
        return False


def check_devices():
    """
    Check for active Spotify devices
    
    Returns:
        tuple: (bool, list) - Success status and list of available devices
    """
    logger.info("Checking for active Spotify devices")
    try:
        devices = sp.devices()
        if devices['devices']:
            logger.info(f"Found {len(devices['devices'])} device(s)")
            
            # Print device info for the user
            print(f"Found {len(devices['devices'])} active Spotify device(s):")
            for i, device in enumerate(devices['devices']):
                print(f"{i+1}. {device['name']} ({device['type']}) - {'Active' if device['is_active'] else 'Inactive'}")
                logger.debug(f"Device {i+1}: {device['name']} (ID: {device['id']}, Type: {device['type']})")
            
            wait("helper")
            return True, devices['devices']
        else:
            logger.warning("No active devices found")
            print("No active Spotify devices found. Please open Spotify on a device.")
            return False, []
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify API error checking devices: {e}")
        print(f"Spotify error: {e}")
        return False, []
    except Exception as e:
        logger.error(f"Error checking devices: {e}")
        print(f"Error checking for Spotify devices: {e}")
        return False, []


def get_playlists(print_results=True):
    """
    Fetch user's playlists
    
    Args:
        print_results (bool): Whether to print playlists to console
        
    Returns:
        list: List of playlists or empty list if none found/error
    """
    logger.info("Fetching user playlists")
    try:
        # Get the user's playlists
        playlists = sp.current_user_playlists()
        if playlists['items']:
            logger.info(f"Found {len(playlists['items'])} playlists")
            
            if print_results:
                print("\nAvailable Playlists:")
                for idx, playlist in enumerate(playlists['items']):
                    print(f"{idx + 1}. {playlist['name']} ({playlist['tracks']['total']} tracks)")
                    logger.debug(f"Playlist {idx+1}: {playlist['name']} (ID: {playlist['id']})")
            
            wait("helper")
            return playlists['items']
        else:
            logger.warning("No playlists found")
            if print_results:
                print("No playlists found in your library")
            return []
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify API error fetching playlists: {e}")
        print(f"Spotify error: {e}")
        return []
    except Exception as e:
        logger.error(f"Error fetching playlists: {e}")
        print(f"Error fetching playlists: {e}")
        return []


def play_playlist(playlist_id):
    """
    Play a playlist by its ID
    
    Args:
        playlist_id (str): Spotify playlist ID
        
    Returns:
        bool: True if playback started successfully, False otherwise
    """
    logger.info(f"Playing playlist with ID: {playlist_id}")
    try:
        # First, try to get the playlist name for better user feedback
        try:
            playlist_info = sp.playlist(playlist_id, fields="name")
            playlist_name = playlist_info['name']
        except:
            playlist_name = "selected playlist"
        
        context_uri = f"spotify:playlist:{playlist_id}"  # Correct URI format
        sp.start_playback(context_uri=context_uri)
        logger.debug(f"Started playback of playlist: {context_uri}")
        print(f"Playing '{playlist_name}'")
        
        wait("high")
        return True
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify API error playing playlist: {e}")
        print(f"Spotify error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error playing playlist: {e}")
        print(f"Error playing playlist: {e}")
        return False


def get_artists(limit=5, print_results=True):
    """
    Fetch user's top artists
    
    Args:
        limit (int): Number of artists to fetch
        print_results (bool): Whether to print artists to console
        
    Returns:
        list: List of artists or empty list if none found/error
    """
    logger.info(f"Fetching user's top {limit} artists")
    try:
        # Search for top artists of the authenticated user
        artists = sp.current_user_top_artists(limit=limit)
        if artists['items']:
            logger.info(f"Found {len(artists['items'])} top artists")
            
            if print_results:
                print("\nYour Top Artists:")
                for idx, artist in enumerate(artists['items']):
                    print(f"{idx + 1}. {artist['name']} ({artist['popularity']} popularity)")
                    logger.debug(f"Artist {idx+1}: {artist['name']} (ID: {artist['id']})")
            
            wait("helper")
            return artists['items']
        else:
            logger.warning("No top artists found")
            if print_results:
                print("No top artists found in your listening history")
            return []
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify API error fetching top artists: {e}")
        print(f"Spotify error: {e}")
        return []
    except Exception as e:
        logger.error(f"Error fetching top artists: {e}")
        print(f"Error fetching top artists: {e}")
        return []


def play_artist(artist_id):
    """
    Play top tracks from an artist
    
    Args:
        artist_id (str): Spotify artist ID
        
    Returns:
        bool: True if playback started successfully, False otherwise
    """
    logger.info(f"Playing top tracks for artist with ID: {artist_id}")
    try:
        # First, try to get the artist name for better user feedback
        try:
            artist_info = sp.artist(artist_id)
            artist_name = artist_info['name']
        except:
            artist_name = "selected artist"
            
        results = sp.artist_top_tracks(artist_id)
        track_uris = [track['uri'] for track in results['tracks']]
        
        if track_uris:
            logger.debug(f"Found {len(track_uris)} tracks for artist")
            sp.start_playback(uris=track_uris)
            print(f"Playing top tracks by {artist_name}")
            
            wait("high")
            return True
        else:
            logger.warning(f"No tracks found for artist: {artist_id}")
            print(f"No tracks found for {artist_name}")
            return False
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify API error playing artist tracks: {e}")
        print(f"Spotify error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error playing artist tracks: {e}")
        print(f"Error playing artist tracks: {e}")
        return False


def search_song(query, print_results=True):
    """
    Search for a song and find the best match
    
    Args:
        query (str): Search query
        print_results (bool): Whether to print results to console
        
    Returns:
        tuple: (uri, track_info) - URI of the best match and track information or (None, None) if not found
    """
    logger.info(f"Searching for song: '{query}'")
    try:
        results = sp.search(q=query, type='track', limit=10)  # Fetch multiple results
        
        if results['tracks']['items']:
            logger.debug(f"Found {len(results['tracks']['items'])} potential matches")
            best_match = None
            highest_score = 0

            if print_results:
                print(f"\nSearching for '{query}'")
                print("Found matches:")
            
            for i, track in enumerate(results['tracks']['items']):
                song_name = track['name']
                artist_name = track['artists'][0]['name']
                
                if print_results:
                    print(f"{i+1}. '{song_name}' by {artist_name}")
                
                score = fuzz.ratio(query.lower(), song_name.lower())  # Compare query with track name
                logger.debug(f"Match: '{song_name}' with score {score}")
                
                if score > highest_score:
                    highest_score = score
                    best_match = track
            
            if best_match:
                track_info = {
                    'name': best_match['name'],
                    'artist': best_match['artists'][0]['name'],
                    'album': best_match['album']['name'],
                    'duration_ms': best_match['duration_ms'],
                    'popularity': best_match['popularity']
                }
                
                logger.info(f"Best match: '{best_match['name']}' by {best_match['artists'][0]['name']} (score: {highest_score})")
                if print_results:
                    print(f"\nBest match: '{best_match['name']}' by {best_match['artists'][0]['name']}")
                
                return best_match['uri'], track_info  # Return the URI and track info
            else:
                logger.warning("No suitable match found for the query")
                if print_results:
                    print("No suitable match found.")
                return None, None
        else:
            logger.warning(f"No tracks found for query: '{query}'")
            if print_results:
                print(f"No tracks found matching '{query}'")
            return None, None
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify API error searching for song: {e}")
        print(f"Spotify error: {e}")
        return None, None
    except Exception as e:
        logger.error(f"Error searching for song: {e}")
        print(f"Error searching for song: {e}")
        return None, None
    
    
def start_playback(song_uri, song_info=None):
    """
    Play a song by its URI with proper error handling
    
    Args:
        song_uri (str): Spotify URI for the track
        song_info (dict, optional): Song information for better logging/output
        
    Returns:
        bool: True if playback started successfully, False otherwise
    """
    if song_info:
        logger.info(f"Attempting to play song: '{song_info['name']}' by {song_info['artist']}")
        print(f"Playing '{song_info['name']}' by {song_info['artist']}")
    else:
        logger.info(f"Attempting to play song with URI: {song_uri}")
        print("Playing selected track")
    
    try:
        if not song_uri:
            logger.warning("Cannot play song: No URI provided")
            print("Cannot play song: No track selected")
            return False
            
        sp.start_playback(uris=[song_uri])
        logger.debug("Playback started successfully")
        return True
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify API error during playback: {e}")
        print(f"Spotify error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during playback: {e}")
        print(f"Error playing song: {e}")
        return False

def play_song(song):
    """
    Given a song name string, searches for it and starts playback.

    Args:
        song (str): The name of the song to play.

    Returns:
        bool: True if playback was started successfully, False otherwise.
    """
    if not isinstance(song, str) or not song.strip():
        logger.warning("Invalid song input provided")
        print("Please provide a valid song name.")
        return False

    try:
        uri, info = search_song(song)
        if uri:
            wait("play")
            return start_playback(uri, info)
        else:
            logger.warning("No matching song found to play")
            print("Couldn't find a matching song to play.")
            return False
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify API error in play_song: {e}")
        print(f"Spotify error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in play_song: {e}")
        print(f"An unexpected error occurred: {e}")
        return False


def get_current_track():
    """
    Get information about the currently playing track
    
    Returns:
        tuple: (bool, dict) - Success status and track information or None if error
    """
    logger.info("Getting current track information")
    try:
        current = sp.current_playback()
        if not current or not current.get('item'):
            logger.warning("No track currently playing")
            print("No track currently playing")
            return False, None
            
        track = current['item']
        track_info = {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name'],
            'progress_ms': current['progress_ms'],
            'duration_ms': track['duration_ms'],
            'is_playing': current['is_playing']
        }
        
        # Calculate progress percentage
        progress_pct = (track_info['progress_ms'] / track_info['duration_ms']) * 100
        
        # Format as min:sec
        progress_sec = track_info['progress_ms'] // 1000
        duration_sec = track_info['duration_ms'] // 1000
        progress_str = f"{progress_sec // 60}:{progress_sec % 60:02d}"
        duration_str = f"{duration_sec // 60}:{duration_sec % 60:02d}"
        
        logger.debug(f"Current track: {track_info['name']} by {track_info['artist']}")
        print(f"\nNow playing: '{track_info['name']}' by {track_info['artist']}")
        print(f"Album: {track_info['album']}")
        print(f"Time: {progress_str} / {duration_str} ({progress_pct:.1f}%)")
        print(f"Status: {'Playing' if track_info['is_playing'] else 'Paused'}")
        
        wait("high")
        return True, track_info
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify API error getting current track: {e}")
        print(f"Spotify error: {e}")
        return False, None
    except Exception as e:
        logger.error(f"Error getting current track: {e}")
        print(f"Error getting current track: {e}")
        return False, None

if __name__ == "__main__":
    pre_check_spotify_environment()
