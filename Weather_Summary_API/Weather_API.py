# Weather API details
import configparser
import json
import requests

# Load the config file
config = configparser.ConfigParser()
config.read('config.ini')

# Reference the API key in the config
api_key = config['DEFAULT']['YOUR_API_KEY_NAME']

# URL
base_url = "http://api.weatherapi.com/v1/current.json"

# Get weather from weather API
def get_weather(location):
    url = f"{base_url}?key={api_key}&q={location}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None
