# Weather API Script

This script fetches weather data from the Weather API using Python.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your_username/weather-api-script.git
    cd weather-api-script
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Add your API keys:
    - Open `config.ini` and replace `your_actual_api_key_here` with your actual API key.

## Getting API Keys

### Weather API Key

1. Visit the [WeatherAPI website](https://www.weatherapi.com/).
2. Sign up for an account or log in if you already have one.
3. Navigate to the API section and create a new API key.
4. Copy the API key and paste it into the `YOUR_API_KEY_NAME` field in `config.ini`.

## Usage

1. Run the script:
    ```bash
    python Weather_API.py
    ```

2. The script will fetch and display the weather data for the specified location.

## Files

- `main.py`: The main script for fetching weather data.
- `config.ini`: Configuration file for the API key.
- `requirements.txt`: List of required Python packages.
- `Gogo_weather.ipynb`: Shows the process of developing the script

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
