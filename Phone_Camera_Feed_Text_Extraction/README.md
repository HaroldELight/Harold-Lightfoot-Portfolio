# Phone Camera Feed and Text Extraction

This Python script captures a live video feed from a phone's camera, saves frames, extracts text from the saved image using an API, and suggests recipes based on the extracted text. The script utilizes several libraries including OpenCV, Matplotlib, Requests, and configparser.

## Features

- Captures live video feed from a phone's camera
- Saves frames upon pressing 's'
- Rotates the video display for correct orientation
- Extracts text from the saved image using an external API

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/HaroldELight/Harold-Lightfoot-Portfolio.git
    cd Harold-Lightfoot-Portfolio/Phone_Camera_Feed_Text_Extraction
   ```

2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Add your API key:
    - Open `config.ini` and replace `your_api_key` with your actual API key.

4. ### Obtain an API key from API Ninjas:

1. Go to the [API Ninjas website](https://api-ninjas.com/).
2. Sign up or log in to your account.
3. Navigate to the "API" section and generate a new API key.
4. Replace `your_api_key_here` in the `config.ini` file with your actual API key.


# Cellphone Camera Text Extraction Script

This script captures text from a live feed from your phone's camera using IP Webcam and Optical Character Recognition (OCR).

## Steps to Use:

### 1. Install the IP Webcam App:
- Download and install the **IP Webcam** app from the Google Play Store on your phone.

### 2. Set Up the Server:
- Ensure your phone and computer are connected to the **same Wi-Fi network**.
- Open the IP Webcam app on your phone and **start the server**.
- After the server is started, **share the IP address** displayed in the app.

### 3. Update the Code:
- Add the IP address of your phone into the code where specified.

### 4. Run the Script:
- On your computer, run the script using the following command:
  ```sh
  python cellphone_camera_read_text.py

### 5. View Live Feed:
- A new window will open displaying the live feed from your phone's camera.

### 6. Save a Frame:
- Press s on your keyboard to save a frame of the live feed.

### 7. Extract and Display Text:
-The saved image will be processed, and the extracted text will be displayed in the console.

## Dependencies

- OpenCV
- Matplotlib
- Requests
- Configparser
- Gogo Gemini (for recipe suggestions)

## Files

- `cellphone_camera_read_text.py`: The main script for the application.
- `config.ini`: Configuration file for the API keys.
- `requirements.txt`: List of required Python packages.
- `image_to_text.py`: Function for getting text from an image.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you have any improvements or bug fixes.

## License

This project is licensed under the MIT License.
