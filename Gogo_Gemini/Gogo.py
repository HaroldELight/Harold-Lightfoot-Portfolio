# Import required libraries
import google.generativeai
import configparser

# Have fun by playing with the system instruction
system_message = "You are a helpful assistant."

# Load the config file
config = configparser.ConfigParser()
try:
    config.read('config.ini')
except Exception as e:
    print(f"Error loading config file: {e}")
    exit()

# Reference the API key in the config
try:
    gog_key = config['DEFAULT']['YOUR_API_KEY_NAME']
except KeyError:
    print("API key not found in config file.")
    exit()

# Configure the Google Generative AI library with the API key
google.generativeai.configure(api_key=gog_key)

# Define a function to generate a response using the Gemini model
def Gogo(user_prompt):
    """
    Generate a response to the user's prompt using the Gemini model.

    Args:
        user_prompt (str): The user's prompt or question.

    Returns:
        str: The generated response.
    """
    try:
        # Create a Gemini model instance with the system instruction
        gemini = google.generativeai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=system_message
        )
        # Generate content using the Gemini model
        response = gemini.generate_content(user_prompt)
        return response.text
    except Exception as e:
        return f"Error generating response: {e}"

# Prompt the user for input
user_prompt = 'Hello, how are you?'
generated_response = Gogo(user_prompt)
print(generated_response)
