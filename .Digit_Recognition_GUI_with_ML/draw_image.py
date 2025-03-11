import tkinter as tk
from PIL import Image, ImageDraw
import numpy as np
import matplotlib.pyplot as plt

# Create the main application class
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Draw a Number")
        self.canvas = tk.Canvas(self, width=200, height=200, bg='white')
        self.canvas.pack()
        self.image1 = Image.new("L", (200, 200), 'white')
        self.draw = ImageDraw.Draw(self.image1)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.button = tk.Button(self, text='Submit', command=self.on_submit)
        self.button.pack()
        self.img = None  # Instance attribute to store the image array

    def paint(self, event):
        x1, y1 = (event.x - 2), (event.y - 2)
        x2, y2 = (event.x + 2), (event.y + 2)
        self.canvas.create_oval(x1, y1, x2, y2, fill="black", width=10)
        self.draw.line([x1, y1, x2, y2], fill="black", width=17)

    def on_submit(self):
        self.get_array()
        self.destroy()  # Close the window properly

    def get_array(self):
        self.image1 = self.image1.resize((28, 28))
        self.img = np.array(self.image1)  # Store the image array in the instance attribute
        self.img = 255 - self.img
        print(self.img)

# Main execution
if __name__ == "__main__":
    app = App()
    app.mainloop()

    # Access the image array after the Tkinter main loop ends
    new_img = app.img
    print("Image array outside the function:", new_img)

    # Plot the number in MNIST format
    plt.imshow(new_img, cmap='gray')
    plt.title("Drawn Number in MNIST Format")
    plt.show()
