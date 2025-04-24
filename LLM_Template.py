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
                    "Convert user requests into JSON. Example:\n"
                    "open youtube -> { \"action\": \"open_website\", \"url\": \"https://youtube.com\" }\n"
                    "search for dogs -> { \"action\": \"search_google\", \"query\": \"dogs\" }\n"
                    "weather in New York -> { \"action\": \"get_weather\", \"location\": \"New York\" }\n"
                    "Do not give any extra text or reasoning, or anything, just JSON"
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
        if not cmd or 'action' not in cmd:
            print("⚠️ Invalid or missing action.")
            return

        action = cmd['action']

        if action == "open_website" and "url" in cmd:
            webbrowser.open(cmd["url"])
            print(f"🌐 Opening {cmd['url']}")

        elif action == "search_google" and "query" in cmd:
            query = cmd["query"]
            webbrowser.open(f"https://www.google.com/search?q={query}")
            print(f"🔍 Searching Google: {query}")

        elif action == "get_weather" and "location" in cmd:
            location = cmd["location"]
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
        CommandProcessor._execute_command(command)
