import cv2
import matplotlib.pyplot as plt
import requests
import configparser
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import threading
from typing import Optional, Tuple

class CameraOCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Camera OCR - Text Extraction")
        self.root.geometry("900x700")
        
        self.camera_extractor = CameraTextExtractor()
        self.cap = None
        self.is_running = False
        self.current_frame = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Left panel - Controls
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Camera URL
        ttk.Label(control_frame, text="Camera URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar(value=self.camera_extractor.config.get('CAMERA', 'video_url'))
        url_entry = ttk.Entry(control_frame, textvariable=self.url_var, width=30)
        url_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # API Key
        ttk.Label(control_frame, text="API Key:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.api_key_var = tk.StringVar(value=self.camera_extractor.api_key)
        api_entry = ttk.Entry(control_frame, textvariable=self.api_key_var, width=30, show="*")
        api_entry.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Buttons
        self.start_btn = ttk.Button(control_frame, text="Start Camera", command=self.start_camera)
        self.start_btn.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=10)
        
        self.stop_btn = ttk.Button(control_frame, text="Stop Camera", command=self.stop_camera, state="disabled")
        self.stop_btn.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.capture_btn = ttk.Button(control_frame, text="Capture & Extract Text", command=self.capture_and_extract, state="disabled")
        self.capture_btn.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Status
        ttk.Label(control_frame, text="Status:").grid(row=7, column=0, sticky=tk.W, pady=(20, 5))
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(control_frame, textvariable=self.status_var, foreground="blue")
        status_label.grid(row=8, column=0, sticky=tk.W, pady=5)
        
        # Right panel - Video feed
        video_frame = ttk.LabelFrame(main_frame, text="Live Camera Feed", padding="10")
        video_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Video display
        self.video_label = ttk.Label(video_frame, text="Camera feed will appear here", background="black", foreground="white")
        self.video_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        video_frame.columnconfigure(0, weight=1)
        video_frame.rowconfigure(0, weight=1)
        
        # Bottom panel - Extracted text
        text_frame = ttk.LabelFrame(main_frame, text="Extracted Text", padding="10")
        text_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        text_frame.columnconfigure(0, weight=1)
        
        self.text_display = tk.Text(text_frame, height=6, wrap=tk.WORD)
        self.text_display.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Scrollbar for text
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_display.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.text_display.configure(yscrollcommand=scrollbar.set)
        
        # Configure control frame grid
        control_frame.columnconfigure(0, weight=1)
        
    def start_camera(self):
        try:
            # Update configuration
            self.camera_extractor.config.set('CAMERA', 'video_url', self.url_var.get())
            self.camera_extractor.api_key = self.api_key_var.get()
            
            video_url = self.url_var.get()
            if video_url == 'http://192.168.1.100:8080/video':
                messagebox.showwarning("Configuration Needed", 
                    "Please update the Camera URL with your phone's IP Webcam address.")
                return
            
            self.cap = cv2.VideoCapture(video_url)
            if not self.cap.isOpened():
                messagebox.showerror("Connection Error", 
                    f"Could not connect to camera at {video_url}\n\n"
                    "Please ensure:\n"
                    "1. Phone and computer are on the same WiFi\n"
                    "2. IP Webcam app is running\n"
                    "3. URL is correct")
                return
            
            self.is_running = True
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.capture_btn.config(state="normal")
            self.status_var.set("Camera running")
            
            # Start video thread
            self.video_thread = threading.Thread(target=self.update_video, daemon=True)
            self.video_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start camera: {str(e)}")
    
    def stop_camera(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.capture_btn.config(state="disabled")
        self.status_var.set("Camera stopped")
        self.video_label.config(image="", text="Camera feed will appear here")
    
    def update_video(self):
        while self.is_running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame.copy()
                
                # Rotate if configured
                if self.camera_extractor.config.getboolean('CAMERA', 'rotate_frame', fallback=True):
                    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                
                # Convert for display
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Resize for display
                height, width = frame_rgb.shape[:2]
                max_width = 640
                if width > max_width:
                    scale = max_width / width
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    frame_rgb = cv2.resize(frame_rgb, (new_width, new_height))
                
                # Convert to PIL Image and then to PhotoImage
                image = Image.fromarray(frame_rgb)
                photo = ImageTk.PhotoImage(image=image)
                
                # Update UI in main thread
                self.root.after(0, self.update_video_display, photo)
            else:
                self.root.after(0, self.show_camera_error)
                break
    
    def update_video_display(self, photo):
        if self.is_running:
            self.video_label.config(image=photo, text="")
            self.video_label.image = photo  # Keep a reference
    
    def show_camera_error(self):
        self.status_var.set("Camera connection lost")
        messagebox.showerror("Error", "Lost connection to camera")
        self.stop_camera()
    
    def capture_and_extract(self):
        if not self.current_frame is None:
            try:
                self.status_var.set("Capturing frame...")
                
                # Save frame
                image_name = self.camera_extractor.config.get('OUTPUT', 'saved_image_name', fallback='captured_image.jpg')
                cv2.imwrite(image_name, self.current_frame)
                
                self.status_var.set("Extracting text...")
                
                # Extract text in separate thread
                threading.Thread(target=self.extract_text_worker, args=(image_name,), daemon=True).start()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to capture frame: {str(e)}")
                self.status_var.set("Error")
        else:
            messagebox.showwarning("No Frame", "No frame available to capture")
    
    def extract_text_worker(self, image_path):
        try:
            extracted_text = self.camera_extractor.extract_text_from_image(image_path)
            
            if extracted_text is not None:
                # Update UI in main thread
                self.root.after(0, self.update_extracted_text, extracted_text)
                
                # Get recipe suggestions if text found
                if extracted_text.strip():
                    self.root.after(0, lambda: self.status_var.set("Getting recipe suggestions..."))
                    recipes = self.camera_extractor.get_recipe_suggestions(extracted_text)
                    if recipes:
                        self.root.after(0, lambda: self.append_to_text_display(f"\n\nRecipe Suggestions:\n{recipes}"))
                
                self.root.after(0, lambda: self.status_var.set("Extraction complete"))
            else:
                self.root.after(0, lambda: self.status_var.set("Extraction failed"))
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Extraction Error", f"Failed to extract text: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set("Error"))
    
    def update_extracted_text(self, text):
        self.text_display.delete(1.0, tk.END)
        self.text_display.insert(1.0, text)
    
    def append_to_text_display(self, text):
        self.text_display.insert(tk.END, text)
    
    def on_closing(self):
        self.stop_camera()
        self.root.destroy()

class CameraTextExtractor:
    def __init__(self, config_file: str = 'config.ini'):
        self.config = self._load_config(config_file)
        self.api_key = self.config.get('API', 'your_api_key')
        
    def _load_config(self, config_file: str) -> configparser.ConfigParser:
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file '{config_file}' not found.")
        
        config = configparser.ConfigParser()
        config.read(config_file)
        return config
    
    def _validate_api_key(self) -> bool:
        if not self.api_key or self.api_key == 'your_api_key_here':
            print("Error: API key not configured. Please set your_api_key in config.ini")
            return False
        return True
    
    def capture_and_process_frame(self) -> Optional[str]:
        if not self._validate_api_key():
            return None
            
        video_url = self.config.get('CAMERA', 'video_url')
        if video_url == 'http://192.168.1.100:8080/video':
            print("Warning: Using default IP address. Please update video_url in config.ini")
        
        cap = cv2.VideoCapture(video_url)
        if not cap.isOpened():
            print(f"Error: Could not open video stream at {video_url}")
            print("Please ensure:")
            print("1. Your phone and computer are on the same WiFi network")
            print("2. IP Webcam app is running on your phone")
            print("3. The video_url in config.ini matches your phone's IP address")
            return None
        
        try:
            width = self.config.getint('CAMERA', 'resolution_width')
            height = self.config.getint('CAMERA', 'resolution_height')
            fps = self.config.getint('CAMERA', 'fps')
            
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            cap.set(cv2.CAP_PROP_FPS, fps)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError) as e:
            print(f"Warning: Could not set camera parameters: {e}")
        
        print("Camera feed opened. Press 's' to capture frame, 'q' to quit.")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame from camera")
                break
            
            if self.config.getboolean('CAMERA', 'rotate_frame', fallback=True):
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            
            cv2.namedWindow('Phone Camera Feed', cv2.WINDOW_NORMAL)
            try:
                window_width = self.config.getint('CAMERA', 'window_width')
                window_height = self.config.getint('CAMERA', 'window_height')
                cv2.resizeWindow('Phone Camera Feed', window_width, window_height)
            except (configparser.NoOptionError, ValueError):
                pass
            
            cv2.imshow('Phone Camera Feed', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Quitting...")
                break
            elif key == ord('s'):
                image_name = self.config.get('OUTPUT', 'saved_image_name', fallback='captured_image.jpg')
                cv2.imwrite(image_name, frame)
                print(f"Frame saved as '{image_name}'")
                
                plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                plt.axis('off')
                plt.title('Captured Frame')
                plt.show()
                
                cap.release()
                cv2.destroyAllWindows()
                return image_name
        
        cap.release()
        cv2.destroyAllWindows()
        return None
    
    def extract_text_from_image(self, image_path: str) -> Optional[str]:
        if not os.path.exists(image_path):
            print(f"Error: Image file '{image_path}' not found")
            return None
        
        api_url = 'https://api.api-ninjas.com/v1/imagetotext'
        
        try:
            with open(image_path, 'rb') as image_file:
                files = {'image': image_file}
                headers = {'X-Api-Key': self.api_key}
                
                print("Extracting text from image...")
                response = requests.post(api_url, files=files, headers=headers, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                if not result:
                    print("No text found in the image")
                    return ""
                
                text_list = [item['text'] for item in result if 'text' in item]
                extracted_text = ' '.join(text_list)
                
                print(f"Extracted text: {extracted_text}")
                return extracted_text
                
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            return None
        except Exception as e:
            print(f"Error processing image: {e}")
            return None
    
    def get_recipe_suggestions(self, text: str) -> Optional[str]:
        try:
            from gogo_gemini import GeminiClient
            
            client = GeminiClient()
            prompt = f"Based on the following text extracted from an image, suggest some recipes: {text}"
            
            print("Getting recipe suggestions...")
            response = client.generate_content(prompt)
            
            print(f"Recipe suggestions: {response}")
            return response
            
        except ImportError:
            print("Warning: gogo-gemini not installed. Recipe suggestions unavailable.")
            print("Install with: pip install gogo-gemini")
            return None
        except Exception as e:
            print(f"Error getting recipe suggestions: {e}")
            return None
    
    def run(self) -> bool:
        print("Starting Phone Camera Text Extraction...")
        
        image_path = self.capture_and_process_frame()
        if not image_path:
            return False
        
        extracted_text = self.extract_text_from_image(image_path)
        if extracted_text is None:
            return False
        
        if extracted_text.strip():
            self.get_recipe_suggestions(extracted_text)
        
        print("Process completed successfully!")
        return True

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = CameraOCRApp(root)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application failed to start: {str(e)}")
        sys.exit(1)
