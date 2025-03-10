# Weather and Clothing Advice Application

This application provides weather information and clothing suggestions based on the current weather conditions for a given location. It utilizes WeatherAPI and Google's generative AI for generating the advice. The application is packaged into an executable for easy distribution and use.

## Features

- Fetches current weather data for a specified location.
- Provides clothing suggestions based on the weather.
- Simple GUI interface using Tkinter.

## Demo

Here's a GIF demonstrating the application in action:

![GUI Demo](GUI_demo.gif)

## How to Build the Executable

### Prerequisites

- Python 3.x
- `pillow` library for image processing.
- `requests` library for API requests.
- `configparser` library for configuration file handling.
- `google-generativeai` library for generating clothing advice.

### File Structure

Ensure your files are organized as follows:

```
your_project/
│
├── main_script.py
├── config.ini
├── weather_image.png
├── requirements.txt
```

### Terminal Command

Open your terminal or command prompt in the project directory and run the following command:

```sh
pyinstaller --onefile --windowed --add-data "config.ini;." --add-data "weather_image.png;." --clean -n Clothing_App Clothing_App.py
```

This will create a `dist` folder containing the EXE file. Make sure to add the Config and weather_image files to the same folder as the EXE before running it.

## How to Use the Executable

### Step 1: Create the EXE using Pypi

Ensure all files are ready and run the Terminal command mentioned.

### Step 2: Add API Keys to Configuration

Before running the application, you need to set up your API keys in the `config.ini` file.

1. Open the `config.ini` file in the `dist` folder.
2. Replace the placeholders with your actual API keys.

Example `config.ini` content:

```ini
[DEFAULT]
WEATHER_API_KEY = YOUR_WEATHER_API_KEY
GOOGLE_API_KEY = YOUR_GOOGLE_API_KEY
```

## Getting API Keys

### Weather API Key

1. Visit the [WeatherAPI website](https://www.weatherapi.com/).
2. Sign up for an account or log in if you already have one.
3. Navigate to the API section and create a new API key.
4. Copy the API key and paste it into the `YOUR_WEATHER_API_KEY` field in `config.ini`.

### Google API Key

1. Visit the [Google Cloud Platform Console](https://console.cloud.google.com/).
2. Create a new project or select an existing project.
3. Navigate to the "APIs & Services" section and enable the `Generative AI` API.
4. Create credentials to obtain an API key.
5. Copy the API key and paste it into the `YOUR_GOOGLE_API_KEY` field in `config.ini`.

### Step 3: Run the Executable

To run the application, simply double-click the `Clothing_App.exe` file.

## Additional Files

### `Clothing_App.py`

This is the main Python script that contains the application logic.

### `config.ini`

Configuration file for storing API keys. Replace the placeholders with your actual keys:

### `requirements.txt`

List of dependencies required for the project:

```
pillow
requests
configparser
google-generativeai
```

### `weather_image.png`

An image file used by the application. Ensure this file is in the same directory as the executable.

## License

This project is licensed under the MIT License.

---
