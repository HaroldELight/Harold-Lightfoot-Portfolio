# %%
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import configparser
import json
import requests
import google.generativeai

# %%
class Application(tk.Frame):
    def __init__(self, master=None):
        if master is None:
            master = tk.Tk()
        super().__init__(master)
        self.master = master
        self.pack()

        # Load API keys from the configuration file
        self.config = self.load_config()
        self.weath_key = self.config['DEFAULT']['WEATHER_API_KEY']
        self.gog_key = self.config['DEFAULT']['GOOGLE_API_KEY']

        self.create_widgets()

    def load_config(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        return config

    def create_widgets(self):
        try:
            original_image = Image.open("weather_image.png")
            resized_image = original_image.resize((300, 300), Image.LANCZOS)
            image = ImageTk.PhotoImage(resized_image)
            image_label = tk.Label(self, image=image)
            image_label.image = image
            image_label.pack(side="left")
        except Exception as e:
            print(f"Error loading image: {e}")

        self.inquiry = tk.Button(self)
        self.inquiry["text"] = "What is the location?"
        self.inquiry["command"] = self.get_location
        self.inquiry.pack(side="top")

        # Text box for entry
        self.location_entry = tk.Entry(self, fg='grey')
        self.location_entry.pack(side="top")
        self.location_entry.insert(0, "City/Town...")
        self.location_entry.bind("<Return>", lambda event: self.get_location())
        self.location_entry.bind("<FocusIn>", self.on_entry_click)
        self.location_entry.bind("<FocusOut>", self.on_focusout)

        # Exit button
        self.exit = tk.Button(self, text="Exit", fg="red", command=self.master.destroy)
        self.exit.pack(side="bottom")

        # Output text
        self.output_text = tk.Text(self, height=16, width=40, wrap="word")
        self.output_text.pack(side="right")

        self.scrollbar = tk.Scrollbar(self, command=self.output_text.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.output_text.config(yscrollcommand=self.scrollbar.set)

    def on_entry_click(self, event):
        if self.location_entry.get() == "City/Town...":
            self.location_entry.delete(0, "end")  # Delete all the text in the entry
            self.location_entry.insert(0, '')  # Insert blank for user input
            self.location_entry.config(fg='black')

    def on_focusout(self, event):
        if self.location_entry.get() == '':
            self.location_entry.insert(0, "City/Town...")
            self.location_entry.config(fg='grey')

    def get_location(self):
        location = self.location_entry.get()
        self.clothing_advice(location)

    def get_weather(self, location):
        base_url = "http://api.weatherapi.com/v1/current.json"
        url = f"{base_url}?key={self.weath_key}&q={location}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get weather data: {response.status_code}")
            return None

    def gogo_weather(self, user_prompt):
        google.generativeai.configure(api_key=self.gog_key)
        gemini = google.generativeai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction='You give a short summary of the weather and Suggested clothing:'
            )
        response = gemini.generate_content(user_prompt)
        return response.text

    def clothing_advice(self, location):
        weather_data = self.get_weather(location)
        if (weather_data):
            user_prompt = json.dumps(weather_data, indent=4)
            advice = self.gogo_weather(user_prompt)
            self.output_text.insert(tk.END, advice)
        else:
            self.output_text.insert(tk.END, "Failed to get weather data\n")

    def run(self):
        self.master.mainloop()

if __name__ == "__main__":
    app = Application()
    app.run()
