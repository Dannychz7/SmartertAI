import time
import sys
import os
# Import your main Spotify functions here
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from spotify_utils import *

# Optional: Adjust sleeps for testing
helperSleep = 0.3
highLevelSleep = 0.5
playSongSleep = 1.0


def test_check_devices():
    try:
        check_devices()
        print("✅ check_devices passed")
        time.sleep(helperSleep)
    except Exception as e:
        print(f"❌ check_devices failed: {e}")

def test_get_playlists():
    try:
        playlists = get_playlists()
        assert isinstance(playlists, list)
        print("✅ get_playlists passed")
        time.sleep(helperSleep)
    except Exception as e:
        print(f"❌ get_playlists failed: {e}")

def test_get_artists():
    try:
        artists = get_artists()
        assert isinstance(artists, list)
        print("✅ get_artists passed")
        time.sleep(helperSleep)
    except Exception as e:
        print(f"❌ get_artists failed: {e}")

def test_search_song():
    try:
        uri, info = search_song("die for you")
        assert uri is not None
        assert "name" in info
        print("✅ search_song passed")
        time.sleep(helperSleep)
    except Exception as e:
        print(f"❌ search_song failed: {e}")

def test_start_playback():
    try:
        uri, _ = search_song("die for you")
        start_playback(uri)
        print("✅ start_playback passed")
        time.sleep(playSongSleep)
    except Exception as e:
        print(f"❌ start_playback failed: {e}")

def test_playback_controls():
    try:
        play_pause()
        next_track()
        previous_track()
        toggle_shuffle()
        toggle_repeat()
        volume_up()
        volume_down()
        skip_5_seconds()
        go_back_5_seconds()
        print("✅ playback controls passed")
        time.sleep(highLevelSleep)
    except Exception as e:
        print(f"❌ playback controls failed: {e}")

def test_play_playlist():
    try:
        playlists = get_playlists()
        if playlists:
            play_playlist(playlists[0]['id'])
            print("✅ play_playlist passed")
        else:
            print("⚠️ No playlists available for testing")
        time.sleep(highLevelSleep)
    except Exception as e:
        print(f"❌ play_playlist failed: {e}")

def test_play_artist():
    try:
        artists = get_artists()
        if artists:
            play_artist(artists[0]['id'])
            print("✅ play_artist passed")
        else:
            print("⚠️ No artists available for testing")
        time.sleep(highLevelSleep)
    except Exception as e:
        print(f"❌ play_artist failed: {e}")

def test_playsong():
    try:
        play_song("Up next 2")
        print("✅ playsong passed")
        time.sleep(playSongSleep)
    except Exception as e:
        print(f"❌ playsong failed: {e}")

def test_get_current_track():
    try:
        track, status = get_current_track()
        assert track is not None
        print(f"✅ get_current_track passed: Currently playing {track.get('name')}")
        time.sleep(helperSleep)
    except Exception as e:
        print(f"❌ get_current_track failed: {e}")


# === Run All Tests ===
if __name__ == "__main__":
    print("Running Spotify Control Tests...\n")

    test_check_devices()
    time.sleep(5.0)
    test_get_playlists()
    time.sleep(5.0)
    test_get_artists()
    time.sleep(5.0)
    test_search_song()
    time.sleep(5.0)
    test_start_playback()
    time.sleep(5.0)
    test_playback_controls()
    time.sleep(5.0)
    test_play_playlist()
    time.sleep(5.0)
    test_play_artist()
    time.sleep(5.0)
    test_playsong()
    time.sleep(5.0)
    test_get_current_track()

    print("\n✅ All tests completed.")
