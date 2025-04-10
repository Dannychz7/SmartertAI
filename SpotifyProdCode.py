# spotifyProdCode.py
import os
import time
import sys
import argparse
import logging
from spotifyConfig import *
from logger import logger
from spotifyHelperFuncs import (
    OSNotSupportedError,
    SpotifyNotFoundError,
    check_system_compatibility,
    check_network_connectivity,
    check_pyautogui_functionality,
    is_spotify_process_running
)
from spotifyController import SpotifyController
from spotifyTestProg import run_test_suite

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

def main():
    """Main function."""
    # Parse command-line arguments
    args = parse_arguments()
    logger.info(">>> main() <<< started")
    
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
            
        # Run test suite if requested
        if args.test:
            logger.info("Running comprehensive test suite")
            results = run_test_suite()
            sys.exit(0 if results["failed"] == 0 else 1)
        
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
        
        # Default test routine
        logger.info("Running default test routine")
        
        # Test with a specific song first
        logger.info("Testing play command with specific song")
        if not spotify.execute_command('play', "Die for you"):
            logger.error("Initial song play test failed")
        time.sleep(5)
        
        # Test boundary cases
        boundary_tests = [
            # Case: Empty string (should fail gracefully)
            {
                "action": lambda: spotify.execute_command('play', ""),
                "description": "Empty song name test",
                "expected": False
            },
            # Case: Very long song name
            {
                "action": lambda: spotify.execute_command('play', "This is an extremely long song name that might cause issues with the search functionality and potentially break something if the system doesn't handle it properly"),
                "description": "Very long song name test",
                "expected": False
            },
            # Case: Song with special characters
            {
                "action": lambda: spotify.execute_command('play', "AC/DC - Back in Black"),
                "description": "Special characters in song name",
                "expected": True
            },
            # Case: Non-existent command
            {
                "action": lambda: spotify.execute_command('nonexistent_command'),
                "description": "Non-existent command test",
                "expected": False
            },
            # Case: Valid song play
            {
                "action": lambda: spotify.execute_command('play', "Telescope"),
                "description": "Standard song play test",
                "expected": True
            }
        ]
        
        # Run boundary tests
        for test in boundary_tests:
            logger.info(f"Running test: {test['description']}")
            try:
                result = test["action"]()
                if result == test["expected"]:
                    logger.info(f"✓ Test passed: {test['description']}")
                else:
                    logger.error(f"✗ Test failed: {test['description']} - Got {result}, expected {test['expected']}")
            except Exception as e:
                logger.error(f"✗ Test failed with exception: {test['description']} - {e}")
            
            # Brief pause between tests
            time.sleep(2)
        
        # Test standard command sequence after successful song play
        if spotify.execute_command('play', "Telescope"):
            logger.info("Song play successful, testing command sequence")
            time.sleep(5)
            
            # Test sequence of commands
            tests = [
                ('like', "Liking the song"),
                ('next', "Moving to next track"),
                ('previous', "Moving to previous track"),
                ('play_pause', "Toggle play/pause"),
                ('play_pause', "Toggle play/pause again"),
                ('volume_up', "Increasing volume"),
                ('volume_down', "Decreasing volume"),
                ('queue', "Show Queue")
            ]
            
            for cmd, desc in tests:
                logger.info(desc)
                if not spotify.execute_command(cmd):
                    logger.error(f"{desc} failed")
                time.sleep(2)
                
            # Test potential error recovery
            logger.info("Testing error recovery")
            # Switch focus away from Spotify
            pyautogui.hotkey('command', 'tab')
            time.sleep(1)
            # Try to execute a command - should recover by refocusing Spotify
            if spotify.execute_command('play_pause'):
                logger.info("✓ Recovery test passed")
            else:
                logger.error("✗ Recovery test failed")
        else:
            logger.error("Main song play test failed, skipping command sequence tests")
        
        logger.info("Spotify automation testing completed")
        
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

if __name__ == "__main__":
    main()
