# imports
import tkinter as tk
from PIL import Image, ImageTk

# class for the GUI

class Application(tk.Frame):
    def __init__(self, master=None):
        if master is None:
            master = tk.Tk()
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        # Ensure the image file path is correct
        try:
            # Resize image
            original_image = Image.open("weather_image.png")
            resized_image = original_image.resize((300,300), Image.LANCZOS)
            image = ImageTk.PhotoImage(resized_image)
            image_label = tk.Label(self, image=image)
            image_label.image = image  # keep a reference to the image
            image_label.pack(side="left")
        except Exception as e:
            print(f"Error loading image: {e}")
    
        # Create a button to ask for the location
        self.inquiry = tk.Button(self)
        self.inquiry["text"] = "What is the location?\n(Area name only)"
        self.inquiry["command"] = self.get_location
        self.inquiry.pack(side="top")
    
        # Create a text entry field for the user to input the location
        self.location_entry = tk.Entry(self)
        self.location_entry.pack()
        self.location_entry.bind("<Return>", lambda event: self.get_location())
    
        # Create an exit button at the bottom of the window
        self.exit = tk.Button(self, text="Exit", fg="red",
                              command=self.master.destroy)
        self.exit.pack(side="bottom")

        # Create text box for output text
        self.output_text = tk.Text(self, height=16, width=40)
        self.output_text.pack(side="right")

    def get_location(self):
        location = self.location_entry.get()
        # print("You entered:", location) 
        self.output_text.insert(tk.END, f'You entered: {location}\n')
    def run(self):
        self.master.mainloop()