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

Bugs to Fix: ***
[] Listning threads do not let speech LLM talk, fix speech function in application or create another one taylored for llm speech reponse
[] Quitting command takes time as all not all threads quit once user says exit
[x] Change AI voice, maybe using Murf API or eleven labs, find free solution
    - Done, implemented voice snippets from Murf API and used that as a basic voice command structure. Currently does not support
        live text-to-speach, I have a solution ready but not yet implemented. Added voice snippets 
[] Voice detection needs to be refined, small time between listening and switiching to another listening makes it so that some is
audio is cut off or not properly working, maybe new mic or software if necessary
[] Spotify voice commands needs work, but spotify has been fully integrated into the codebase with error checking and production
level code. Logging is now in place. 
    - SOLUTION: USING AN LLM TO PROCESS COMMANDS

Features to Add: **
[] Add refined error checking 
[] Add more functionality to app, youtube.com, google.com, web searches, voice scrolling, etc... 
[] Add camera for LLM image explaination
[] Find local LLM for looking and processing images
[] Do some other work in the meantime while LLM is thinking (Maybe talk about the news or something like that)
[x] begin splitting project into modular pieces, cannot have it all in one file


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