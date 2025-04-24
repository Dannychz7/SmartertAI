# import webbrowser
# import json
# import requests

# # Function to execute commands based on parsed JSON
# def execute_command(command_json):
#     # Parse the JSON
#     command = command_json.get("command")
    
#     if command == "open_url":
#         # Open the provided URL in the default web browser
#         url = command_json.get("url")
#         if url:
#             print(f"Opening URL: {url}")
#             webbrowser.open(url)  # Open the URL in the default browser
    
#     elif command == "search":
#         # Perform a Google search
#         query = command_json.get("query")
#         if query:
#             search_url = f"https://www.google.com/search?q={query}"
#             print(f"Performing search: {query}")
#             webbrowser.open(search_url)  # Perform Google search
    
#     elif command == "weather":
#         # Fetch weather information based on location
#         location = command_json.get("location")
#         if location:
#             # Using OpenWeatherMap API (replace with your own API key)
#             api_key = "your_weather_api_key_here"  # Replace with your API key
#             weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
#             response = requests.get(weather_url)
#             data = response.json()

#             if response.status_code == 200:
#                 # Parse weather information
#                 weather_info = {
#                     "location": location,
#                     "temperature": data['main']['temp'],
#                     "description": data['weather'][0]['description']
#                 }
#                 print(f"Weather Info for {location}: {weather_info}")
#                 return weather_info  # Return weather info in JSON format
#             else:
#                 print(f"Error fetching weather: {data.get('message', 'Unknown error')}")
#                 return {"error": "Unable to fetch weather information"}
#         else:
#             return {"error": "No location specified"}
    
#     else:
#         print("Unknown command.")
#         return {"error": "Unknown command"}

# # Sample Commands (Example JSON commands)

# # 1. Open YouTube
# command_json = {
#     "command": "open_url",
#     "url": "https://www.youtube.com"
# }
# execute_command(command_json)

# # 2. Search Google (e.g., "weather in Worcester, MA")
# command_json = {
#     "command": "search",
#     "query": "weather in Worcester, MA"
# }
# execute_command(command_json)

# # 3. Fetch Weather Information (e.g., "Worcester, MA")
# command_json = {
#     "command": "weather",
#     "location": "Worcester, MA"
# }
# weather_info = execute_command(command_json)
# print(json.dumps(weather_info, indent=4))  # Display the weather info in a formatted JSON

import json
import threading
import webbrowser
import requests
import ollama  # Your local LLM
import logging

# Optional logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

WEATHER_API_KEY = "your_openweathermap_api_key"  # Replace with your key


class CommandProcessor:
    @staticmethod
    def _spinning_cursor(stop_event):
        while not stop_event.is_set():
            for cursor in '|/-\\':
                print(f'\rThinking... {cursor}', end='', flush=True)
                if stop_event.wait(0.1):
                    break

    @staticmethod
    def _chat_with_llm(text):
        """Get structured JSON command from local LLM."""
        try:
            stop_event = threading.Event()
            spinner_thread = threading.Thread(target=CommandProcessor._spinning_cursor, args=(stop_event,))
            spinner_thread.start()

            response = ollama.chat(model="llama3.2", messages=[
                {"role": "system", "content": (
                    "You are an assistant that converts user commands into JSON for system execution.\n"
                    "Respond ONLY with a JSON object. Use the following format:\n\n"
                    "{\n"
                    "  \"intent\": \"string\",         # general intent (e.g. open_website, get_weather)\n"
                    "  \"action\": \"string\",         # specific action the system can run\n"
                    "  \"parameters\": {              # any relevant parameters for the action\n"
                    "    ...                         # key-value pairs like \"url\", \"query\", etc.\n"
                    "  }\n"
                    "}\n\n"
                    "Supported intents and actions:\n"
                    "- open_website → navigate → { \"url\": \"https://example.com\" }\n"
                    "- search → search_google → { \"query\": \"dogs\" }\n"
                    "- get_weather → fetch_weather → { \"location\": \"New York\" }\n"
                    "- get_news → fetch_news → { \"topic\": \"technology\" } (optional)\n"
                    "- play_music → play_song → { \"song\": \"Bohemian Rhapsody\" } (optional: \"artist\")\n"
                    "- launch_app → open_application → { \"app_name\": \"calculator\" }\n"
                    "- send_message → send_text → { \"recipient\": \"John\", \"message\": \"Hi there!\" }\n\n"
                    "Examples:\n"
                    "- open youtube -> { \"intent\": \"open_website\", \"action\": \"navigate\", \"parameters\": { \"url\": \"https://youtube.com\" } }\n"
                    "- search for dogs -> { \"intent\": \"search\", \"action\": \"search_google\", \"parameters\": { \"query\": \"dogs\" } }\n"
                    "- weather in Paris -> { \"intent\": \"get_weather\", \"action\": \"fetch_weather\", \"parameters\": { \"location\": \"Paris\" } }\n"
                    "- play despacito -> { \"intent\": \"play_music\", \"action\": \"play_song\", \"parameters\": { \"song\": \"Despacito\" } }\n"
                    "- open spotify -> { \"intent\": \"launch_app\", \"action\": \"open_application\", \"parameters\": { \"app_name\": \"spotify\" } }\n"
                    "- message John saying hi -> { \"intent\": \"send_message\", \"action\": \"send_text\", \"parameters\": { \"recipient\": \"John\", \"message\": \"hi\" } }\n\n"
                    "Do NOT provide any reasoning, do NOT explain. Just output the JSON object."
                )},
                {"role": "user", "content": text}
            ])


            stop_event.set()
            spinner_thread.join()

            raw_output = response["message"]["content"]
            return json.loads(raw_output.strip())
        except Exception as e:
            logger.error(f"LLM error: {e}")
            print("\n❌ LLM error:", str(e))
            return None

    @staticmethod
    def _execute_command(cmd):
        if not cmd or 'action' not in cmd or 'parameters' not in cmd:
            print("⚠️ Invalid or missing action or parameters.")
            return

        action = cmd['action']
        params = cmd['parameters']

        if action == "navigate" and "url" in params:
            webbrowser.open(params["url"])
            print(f"🌐 Opening {params['url']}")

        elif action == "search_google" and "query" in params:
            query = params["query"]
            webbrowser.open(f"https://www.google.com/search?q={query}")
            print(f"🔍 Searching Google: {query}")

        elif action == "fetch_weather" and "location" in params:
            location = params["location"]
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}&units=metric"
            try:
                res = requests.get(url)
                data = res.json()
                if res.status_code == 200:
                    temp = data['main']['temp']
                    desc = data['weather'][0]['description']
                    print(f"🌤️ {location.title()}: {temp}°C, {desc}")
                else:
                    print(f"❌ Weather error: {data.get('message', 'Unknown error')}")
            except Exception as e:
                print("❌ Weather fetch failed:", str(e))

        elif action == "fetch_news":
            topic = params.get("topic", "world")
            webbrowser.open(f"https://news.google.com/search?q={topic}")
            print(f"🗞️ Opening news for topic: {topic}")

        elif action == "play_song" and "song" in params:
            song = params["song"]
            artist = params.get("artist", "")
            query = f"{song} {artist}".strip()
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            print(f"🎵 Playing song: {query}")

        elif action == "open_application" and "app_name" in params:
            import subprocess
            try:
                subprocess.Popen(params["app_name"])  # for Windows you may want to add `.exe`
                print(f"📂 Launching application: {params['app_name']}")
            except Exception as e:
                print(f"❌ Failed to launch application: {e}")

        elif action == "send_text" and "recipient" in params and "message" in params:
            print(f"📩 Sending message to {params['recipient']}: {params['message']}")
            # Stub for sending a message — integrate messaging API here if desired

        else:
            print("🤖 Unknown action or missing data.")

if __name__ == "__main__":
    print("🧠 Type a command (or 'exit'):")
    while True:
        user_input = input(">> ").strip()
        if user_input.lower() == "exit":
            print("👋 Goodbye!")
            break

        command = CommandProcessor._chat_with_llm(user_input)
        logger.debug(f"Debug command output: {command}")
        CommandProcessor._execute_command(command)
