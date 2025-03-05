# %%
from PIL import Image
import sys
import requests
from io import BytesIO

# %%
def image_to_text():
    """
    Ask for the path to the image file and extract the text from it.

    """
    # API key and URL
    api_key_text = 'nKgCHfZhzONmP87t4mUuAw==UCwKCOxy8Gwfr6Sw'
    api_url = 'https://api.api-ninjas.com/v1/imagetotext'

    # input image path
    image_path = input("Enter the path to the image file without quotes: ")
    # Open the image file
    image = Image.open(image_path)

    # Save the image to a bytes string
    image_bytes = BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)  # Reset the file pointer to the beginning

    # Create a dictionary with the image bytes
    files = {'image': ('error.png', image_bytes, 'image/png')}

    # Make the POST request
    r = requests.post(api_url, files=files, headers={'X-Api-Key': api_key_text})

    # Extract the text from the JSON result
    text_list = [item['text'] for item in r.json()]

    # Join the text list into a single string
    extracted_text = ' '.join(text_list)

    return extracted_text