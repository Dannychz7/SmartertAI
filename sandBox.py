import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer

WAKE_WORDS = ["hey nova", "hey atlas", "yo nova"]

# Load the Vosk model
model = Model("vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)

# Setup the queue to store audio data
q = queue.Queue()

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

def listen():
    print("Listening for wake words... (say 'hey nova', 'hey atlas', or 'yo nova')")
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=audio_callback):
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").lower()
                if any(phrase in text for phrase in WAKE_WORDS):
                    print(f"Wake word detected: \"{text}\"")
                    respond_to_wake_word(text)

def respond_to_wake_word(trigger):
    print(f"🔊 Activated by '{trigger}' - Ready to process command...")

if __name__ == "__main__":
    listen()
