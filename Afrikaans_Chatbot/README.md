
# Katrina - Afrikaans Speech-to-Text Chatbot

Katrina is a Python-based chatbot capable of recording speech, transcribing it to text, generating responses in Afrikaans using Google's Gemini model, and converting the response back to speech. Ideal for exploring conversational AI in a specific language.

## Features

- Records audio and converts it to text using Google Speech Recognition.
- Generates responses in Afrikaans using the Gemini generative AI model.
- Outputs responses as an audio file using text-to-speech (TTS).
- Designed as a one-loop conversational chatbot.

## Getting Started

### Prerequisites

- **Python 3.8+**: Make sure Python is installed on your system.
- **Google Generative AI API Key**: Add this to a `config.ini` file for secure access.

### Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/HaroldELight/Harold-Lightfoot-Portfolio.git
   cd Harold-Lightfoot-Portfolio/Afrikaans_Chatbot

   ```

2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your `config.ini` file:
   - Add your Google API key:

     ```ini
     [API_KEYS]
     google_api_key = YOUR_GOOGLE_API_KEY
     ```

### Usage

Run the chatbot:

```bash
python katrina.py
```

Speak into your microphone, and press `q` then ENTER to stop the recording. Katrina will respond in Afrikaans with both text and audio.

## File Structure

- `katrina.py`: Contains the chatbot code.
- `requirements.txt`: Lists the required Python packages.
- `config.ini`: Stores the API key (user needs to add this).
- `README.md`: Documentation.
- `LICENSE`: Licensing information.
- `Afrikaans_audio_chatbot.ipynb' : The process of creating the final Class (Included for reference)

## Contributing

Contributions are welcome! Feel free to fork the repository and create a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

**Harold E. Lightfoot**
