# spotifyTestProg.py
import time
import sys
from spotifyConfig import *
import pyautogui
from logger import logger
from spotifyHelperFuncs import (
    check_system_compatibility,
    check_network_connectivity,
    check_pyautogui_functionality,
    is_spotify_process_running,
    launch_spotify,
    activate_spotify_window
    
)
from spotifyController import SpotifyController, is_valid_song_name

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
