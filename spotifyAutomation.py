import pyautogui
import os
import time

try:
    # Check if Spotify is running
    result = os.popen("pgrep -x Spotify").read().strip()
    
    if not result:
        print("Opening Spotify...")
        os.system("open -a Spotify")  # macOS
        time.sleep(10)  # Wait longer for first launch
    else:
        print("Spotify is already running")
        # Bring Spotify to foreground
        os.system("osascript -e 'tell application \"Spotify\" to activate'")
        time.sleep(2)

except Exception as e:
    print(f"Error checking Spotify status: {e}")

# Give Spotify some time to load and be ready
time.sleep(2)

# Focus on the Spotify window
pyautogui.hotkey('command', 'tab')  # Switch to the next app, just in case

print("Searching now")
# Open search bar in Spotify
pyautogui.hotkey('command', 'k')
time.sleep(1)  # Let the search bar open

print("Doing song name now")
# Type song name
pyautogui.write('All I want', interval=0.1)
time.sleep(1)  # Give it time to type

# Press Enter to search
pyautogui.press('return')
