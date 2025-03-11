# Imports

import speech_recognition as sr
import os 
import pyaudio
from gtts import gTTS
import google.generativeai
import wave
import threading
import configparser

# Class for one loop conversation in Afrikaans

class Katrina:
    def __init__(self):
        self.is_recording = True
        self.audio_file = "Recording.wav"
        self.filename = "Katrina.mp3"

    def record_audio(self):
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 1024

        def record_audio_logic():
            audio = pyaudio.PyAudio()
            stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
            frames = []
            print("Recording... Press 'q' to stop.")

            while self.is_recording:
                frames.append(stream.read(CHUNK))

            stream.stop_stream()
            stream.close()
            audio.terminate()

            with wave.open(self.audio_file, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b"".join(frames))
            print(f"Saved audio to: {os.path.abspath(self.audio_file)}")

        def stop_recording():
            while input() != "q":
                pass
            self.is_recording = False

        thread = threading.Thread(target=record_audio_logic)
        thread.start()
        stop_recording()
        thread.join()

    def speech_to_text(self):
        recognizer = sr.Recognizer()
        with sr.AudioFile(self.audio_file) as source:
            audio = recognizer.record(source)
            return recognizer.recognize_google(audio, language="af-ZA")

    def Gogo_response(self, user_prompt):
        
        # Kept short and sweet
        system_message = 'You are Katrina, you respond in Afrikaans with less than 30 words.'

        # Read the API key from the config file
        config = configparser.ConfigParser()
        config.read('config.ini')

        # Get the Google API key from the config file
        gog_key = config.get('API_KEYS', 'google_api_key')

        # Configure the Google Generative AI library
        google.generativeai.configure(api_key=gog_key)

        # Create a Gemini model instance
        gemini = google.generativeai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction='This is Afrikaans text, you will respond in Afrikaans and you are a helpful assistant.'
        )

        # Generate content using the Gemini model
        response = gemini.generate_content(user_prompt)
        return response.text

    def text_to_audio(self, text):
        
        tts = gTTS(text=text, lang="af")
        tts.save(self.filename)
        os.system(f"start {self.filename}")

    def run(self):
        self.record_audio()
        user_prompt = self.speech_to_text()
        print(f"User said: {user_prompt}")
        response = self.Gogo_response(user_prompt)
        #print(f"Bot response: {response}")
        self.text_to_audio(response)

if __name__ == "__main__":
    Katrina().run()
