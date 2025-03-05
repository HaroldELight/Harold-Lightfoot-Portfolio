# Imports:

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import configparser
import json
import requests
import google.generativeai

# GUI class that displays the weather and clothing advice
# with own keys

class Application(tk.Frame):
    def __init__(self, master=None):
        if master is None:
            master = tk.Tk()
        super().__init__(master)
        self.master = master
        self.pack()
        
        # Load API keys directly from the config file
        self.config = self.load_config()
        self.weath_key = self.config['WEATHER_API_KEY']
        self.gog_key = self.config['GOOGLE_API_KEY']

        # Create the widgets for the GUI
        self.create_widgets()

    def create_widgets(self):
        """
        Create and arrange the GUI elements.
        """
        try:
            # Load and display image
            original_image = Image.open("weather_image.png")
            resized_image = original_image.resize((300, 300), Image.LANCZOS)
            image = ImageTk.PhotoImage(resized_image)
            image_label = tk.Label(self, image=image)
            image_label.image = image
            image_label.pack(side="left")
        except Exception as e:
            print(f"Error loading image: {e}")

        # Add button to inquire about location
        self.inquiry = tk.Button(self)
        self.inquiry["text"] = "What is the location?\n(Area name only)"
        self.inquiry["command"] = self.get_location
        self.inquiry.pack(side="top")

        # Add entry field for location input
        self.location_entry = tk.Entry(self)
        self.location_entry.pack()
        self.location_entry.bind("<Return>", lambda event: self.get_location())

        # Add exit button
        self.exit = tk.Button(self, text="Exit", fg="red", command=self.master.destroy)
        self.exit.pack(side="bottom")

        # Add text field for displaying output
        self.output_text = tk.Text(self, height=16, width=40, wrap="word")
        self.output_text.pack(side="right")

        # Add scrollbar for the text field
        self.scrollbar = tk.Scrollbar(self, command=self.output_text.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.output_text.config(yscrollcommand=self.scrollbar.set)

    def get_location(self):
        """
        Retrieve the location input and fetch clothing advice.
        """
        location = self.location_entry.get()
        self.clothing_advice(location)

    def get_weather(self, location):
        """
        Fetch weather data for the specified location using the Weather API.
        """
        base_url = "http://api.weatherapi.com/v1/current.json"
        url = f"{base_url}?key={self.weath_key}&q={location}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get weather data: {response.status_code}")
            return None

    def gogo_weather(self, user_prompt):
        """
        Generate weather advice using Google's generative AI.
        """
        google.generativeai.configure(api_key=self.gog_key)
        gemini = google.generativeai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction='You give a short summary of the weather and \
            Suggested clothing:'
            )
        response = gemini.generate_content(user_prompt)
        return response.text

    def clothing_advice(self, location):
        """
        Fetch weather data and generate clothing advice.
        """
        weather_data = self.get_weather(location)
        if weather_data:
            user_prompt = json.dumps(weather_data, indent=4)
            advice = self.gogo_weather(user_prompt)
            self.output_text.insert(tk.END, advice)
        else:
            self.output_text.insert(tk.END, "Failed to get weather data\n")

    def run(self):
        """
        Start the Tkinter main loop.
        """
        self.master.mainloop()

if __name__ == "__main__":
    app = Application()
    app.run()
