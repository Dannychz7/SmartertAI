import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET
from fuzzywuzzy import fuzz

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

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE
))

# --- Playback Controls ---
def play_liked_songs():
    # Initialize list to store track URIs
    track_uris = []
    
    # Fetch liked songs in pages
    offset = 0
    while True:
        results = sp.current_user_saved_tracks(limit=20, offset=offset)
        tracks = results['items']
        
        if not tracks:
            break
        
        # Extract the URI of each track and add to the list
        track_uris.extend([track['track']['uri'] for track in tracks])
        
        # Update offset for next page of results
        offset += 20
        
        # Stop if we have collected enough tracks (optional)
        if len(track_uris) >= 20:  # Limit to the first 100 liked songs
            break

    if track_uris:
        # Start playback of the liked songs
        sp.start_playback(uris=track_uris[:100])  # You can adjust the number as needed
        print("Starting playback of your liked songs...")
    else:
        print("No liked songs found.")


def play_pause():
    playback = sp.current_playback()
    if playback and playback['is_playing']:
        sp.pause_playback()  # Pause the track
    else:
        sp.start_playback()  # Start the track

# --- Playback Controls ---
def next_track():
    playback = sp.current_playback()
    if playback and 'next_tracks' in playback and playback['next_tracks']:
        sp.next_track()
    else:
        print("No next track available.")

def previous_track():
    playback = sp.current_playback()
    if playback and 'previous_tracks' in playback and playback['previous_tracks']:
        sp.previous_track()
    else:
        print("No previous track available.")

def toggle_shuffle():
    playback = sp.current_playback()
    sp.shuffle(not playback['shuffle_state'])  # Toggle shuffle

def toggle_repeat():
    playback = sp.current_playback()
    state = playback['repeat_state']
    new_state = 'track' if state == 'off' else 'context' if state == 'track' else 'off'
    sp.repeat(new_state)  # Toggle repeat mode

def volume_up(step=10):
    playback = sp.current_playback()
    current_volume = playback['device']['volume_percent']
    sp.volume(min(100, current_volume + step))  # Increase volume by the given step, max 100%

def volume_down(step=10):
    playback = sp.current_playback()
    current_volume = playback['device']['volume_percent']
    sp.volume(max(0, current_volume - step))  # Decrease volume by the given step, min 0%

def skip_5_seconds():
    playback = sp.current_playback()
    if playback:
        position = playback['progress_ms'] + 5000
        sp.seek_track(position)  # Skip 5 seconds forward

def go_back_5_seconds():
    playback = sp.current_playback()
    if playback:
        position = max(0, playback['progress_ms'] - 5000)
        sp.seek_track(position)  # Go back 5 seconds

def check_devices():
    devices = sp.devices()
    if devices['devices']:
        print("Active device found!")
        active_device = devices['devices'][0]  # Use the first active device
    else:
        print("No active devices found. Please make sure you have an active device with Spotify running.")
        exit()

def get_playlists():
    # Get the user's playlists
    playlists = sp.current_user_playlists()
    if playlists['items']:
        print("Available Playlists:")
        for idx, playlist in enumerate(playlists['items']):
            print(f"{idx + 1}. {playlist['name']} (ID: {playlist['id']})")
    else:
        print("No playlists found.")
        return []
    return playlists['items']

def play_playlist(playlist_id):
    context_uri = f"spotify:playlist:{playlist_id}"  # Correct URI format
    sp.start_playback(context_uri=context_uri)
    print(f"Playing playlist: {context_uri}")

def get_artists():
    # Search for top artists of the authenticated user
    artists = sp.current_user_top_artists(limit=5)
    if artists['items']:
        print("Top Artists:")
        for idx, artist in enumerate(artists['items']):
            print(f"{idx + 1}. {artist['name']} (ID: {artist['id']})")
    else:
        print("No artists found.")
        return []
    return artists['items']

def play_artist(artist_id):
    results = sp.artist_top_tracks(artist_id)
    track_uris = [track['uri'] for track in results['tracks']]
    if track_uris:
        sp.start_playback(uris=track_uris)
        print(f"Playing songs by artist: {artist_id}")
    else:
        print(f"No tracks found for artist: {artist_id}")

def search_song(query):
    results = sp.search(q=query, type='track', limit=10)  # Fetch multiple results
    
    if results['tracks']['items']:
        best_match = None
        highest_score = 0

        for track in results['tracks']['items']:
            song_name = track['name']
            print(song_name)
            score = fuzz.ratio(query.lower(), song_name.lower())  # Compare query with track name
            
            if score > highest_score:
                highest_score = score
                best_match = track
        
        if best_match:
            print(f"Best match: {best_match['name']} by {best_match['artists'][0]['name']}")
            return best_match['uri']  # Return the URI to play the track
        else:
            print("No suitable match found.")
            return None
    else:
        print("No tracks found.")
        return None

# --- Example usage ---
if __name__ == '__main__':
    print("Starting the script...")
    
    check_devices()

    # Search for a track
    print("Searching for 'Up Next 2'...")
    songUri = search_song("die for you")
    print(f"This is up next 2 by my func: {songUri}")
    # result = sp.search(q=songUri, type='track', limit=1)

    # if result['tracks']['items']:
    #     print("Track found!")
    #     track_uri = result['tracks']['items'][0]['uri']
    #     print(f"Track URI: {track_uri}")
    # else:
    #     print("No track found. Exiting.")
    #     exit()

    # Start playback
    print("Starting playback...")
    sp.start_playback(uris=[songUri])
    time.sleep(10)

    # # Playback Controls
    # print("Playing/Pausing track...")
    # play_pause()  # Play or Pause the track
    # time.sleep(2)

    # print("Skipping to the next track...")
    # next_track()  # Skip to the next track
    # time.sleep(2)

    # print("Going back to the previous track...")
    # previous_track()  # Go to the previous track
    # time.sleep(2)

    # print("Toggling shuffle...")
    # toggle_shuffle()  # Toggle shuffle
    # time.sleep(2)

    # print("Toggling repeat...")
    # toggle_repeat()  # Toggle repeat
    # time.sleep(2)

    # print("Increasing volume...")
    # volume_up()  # Increase volume
    # time.sleep(2)

    # print("Decreasing volume...")
    # volume_down()  # Decrease volume
    # time.sleep(2)

    print("Skipping 5 seconds forward...")
    skip_5_seconds()  # Skip forward by 5 seconds
    time.sleep(2)

    print("Going 5 seconds back...")
    go_back_5_seconds()  # Go back by 5 seconds
    time.sleep(2)
    
    # Play the liked songs
    play_liked_songs()
    
    playlists = get_playlists()
    if playlists:
        playlist_choice = int(input("Enter the playlist number you want to play: ")) - 1
        if 0 <= playlist_choice < len(playlists):
            play_playlist(playlists[playlist_choice]['id'])

    # Get artists and allow the user to choose one
    artists = get_artists()
    if artists:
        artist_choice = int(input("Enter the artist number you want to play: ")) - 1
        if 0 <= artist_choice < len(artists):
            play_artist(artists[artist_choice]['id'])

    print("Script completed.")
