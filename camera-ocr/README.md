# Camera OCR

A Python application that captures live video feed from a phone's camera, extracts text from captured frames using OCR, and suggests recipes based on the extracted text.

## Features

- **Live Camera Feed**: Connect to your phone's camera via IP Webcam
- **Text Extraction**: Uses API Ninjas OCR service to extract text from captured images
- **Recipe Suggestions**: AI-powered recipe suggestions based on extracted text
- **Configurable Settings**: Customizable camera resolution, rotation, and output options
- **Error Handling**: Robust error handling with helpful user feedback

## Installation

1. **Clone the repository**:
   ```sh
   git clone https://github.com/HaroldELight/Harold-Lightfoot-Portfolio.git
   cd Harold-Lightfoot-Portfolio/camera-ocr
   ```

2. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

3. **Configure the application**:
   - Open `config.ini` and replace `your_api_key_here` with your API Ninjas API key
   - Update the `video_url` with your phone's IP Webcam address

## Setup Instructions

### 1. Install IP Webcam App
- Download and install **IP Webcam** from the Google Play Store on your Android phone

### 2. Configure Phone Camera
- Ensure your phone and computer are on the **same Wi-Fi network**
- Open IP Webcam and scroll down to "Start server"
- Choose your preferred settings and tap "Start server"
- Note the IP address displayed (e.g., `http://192.168.1.100:8080/video`)

### 3. Update Configuration
- Edit `config.ini` and update:
  ```ini
  [API]
  your_api_key = your_actual_api_key_here
  
  [CAMERA]
  video_url = http://your_phone_ip:8080/video
  ```

### 4. Get API Key
1. Visit [API Ninjas](https://api-ninjas.com/)
2. Sign up for a free account
3. Navigate to the API section and get your Image to Text API key
4. Add the key to `config.ini`

## Usage

Run the application:
```sh
python camera_ocr_app.py
```

**GUI Features:**
- **Live Camera Feed**: Real-time video display from your phone's camera
- **Configuration Panel**: Edit camera URL and API key directly in the interface
- **Capture Button**: Click to capture frame and extract text
- **Text Display**: Shows extracted text and recipe suggestions
- **Status Indicators**: Real-time status updates for all operations

**How to Use:**
1. Launch the application to open the GUI
2. Enter your phone's IP Webcam URL in the Camera URL field
3. Add your API Ninjas key in the API Key field
4. Click "Start Camera" to begin the live feed
5. Click "Capture & Extract Text" to process the current frame
6. View extracted text and recipe suggestions in the bottom panel

## Configuration Options

Edit `config.ini` to customize:

```ini
[CAMERA]
video_url = http://192.168.3.6:8080/video         # Your phone's IP Webcam URL
resolution_width = 1280                        # Camera resolution width
resolution_height = 720                         # Camera resolution height
fps = 60                                        # Frames per second
rotate_frame = true                            # Rotate frame 90° clockwise
window_width = 320                              # Display window width
window_height = 480                             # Display window height

[OUTPUT]
saved_image_name = captured_image.jpg          # Name for saved images
```

## Dependencies

- **opencv-python**: Computer vision and camera operations
- **matplotlib**: Image display
- **requests**: HTTP requests for API calls
- **pillow**: Image processing
- **gogo-gemini**: Recipe suggestions (optional)

## Troubleshooting

### Camera Connection Issues
- Ensure both devices are on the same Wi-Fi network
- Verify IP Webcam is running on your phone
- Check that the firewall isn't blocking the connection
- Try the URL in a web browser to test connectivity

### API Issues
- Verify your API Ninjas key is valid
- Check internet connection
- Ensure you haven't exceeded API limits

### Recipe Suggestions Not Working
- Install gogo-gemini: `pip install gogo-gemini`
- Check that the API key has sufficient permissions

## File Structure

```
camera-ocr/
├── camera_ocr_app.py                # Main GUI application
├── config.ini                       # Configuration file
├── requirements.txt                 # Python dependencies
├── README.md                       # This file
└── LICENSE                         # MIT License
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for improvements and bug fixes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
