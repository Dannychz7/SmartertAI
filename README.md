# Smarter Glass AI

Benefit of Smarter Glass AI is that all you need is a computer that can run a llm and you should be free to use it with voice
commands. Think of it like jarvis or friday, just not as samrt, yet.

* CURRENTLY UNDER DEVELOPMENT *

Smarter Glass AI will one day provide real-time information and interactive features. The application can include a variety of functions, such as:

- Augmented Reality (AR): Displaying virtual information overlaid on the real world, like navigation directions, product details, or maps.
- Voice Commands: Allowing users to interact hands-free through voice recognition, controlling the device, searching the web, or sending messages.
- Notifications and Alerts: Providing real-time notifications for messages, calls, calendar events, or other important updates directly to the glasses.
- Health and Fitness Tracking: Monitoring user activity, heart rate, and other health metrics, offering fitness insights and encouraging healthy habits.
- Camera Integration: Allowing users to capture photos or videos, or stream live feeds directly from their perspective.
- Gesture Control: Enabling hands-free control by recognizing head movements or specific gestures, enhancing user interaction.

* CURRENTLY UNDER DEVELOPMENT *

Notes for Testing Spotify Voice Commands:
    play_song | Works: [x]
    play_pause, | Works: [x]
    next_track, | works: [x] 
    previous_track, | works: [] 
        With next and previous, if no song is next or previous, play songs by the artist by using play_artist_by_name
    toggle_shuffle, | works: [x] 
    toggle_repeat, | works: [x] 
    volume_up, | works: [x] 
    volume_down,| works: [x] 
    skip_5_seconds, | works: [x] 
    go_back_5_seconds, | works: [x] 
    play_playlist, # Needs, gets playlists id, call get_playlist first to get id) Needs refinment
    play_artist, # needs get_artists id, call get_artists first to get id) | works: [x] 
    play_artist_by_name, | works: [x] 
    get_current_track, | works: [x] 

    - THEY ALL WORK, BUT ALL NEEDS REFINEMENT IN TERMS OF WHAT USER WANTS (I.E PLAY THE WEEKND, WILL PLAY SONGS, NOT THE ARTIST)


Features Implemented:
    - Implemented Murf AI for voice generation
    - Main.py holds the main execution of files
    - spotify Automation allows for commands to be executed via keyboard shortcuts
    - Murf AI clips used for busy wait audio
    - Created modular design, so prject is now being split into different chunks (spotify automation, playBusyWaitAudio, etc..)
    

Priorites: 
* - Low
** - Next in Line
*** - High/Working on actively


Thank you for taking the time to view my project! 