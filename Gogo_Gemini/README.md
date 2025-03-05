# Weather Clothing Advisor

This is a script for setting up and interacting with the Gemini API.
The API can be told how to respond via the System_message or system_instruction variable.
*Have Fun*

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/HaroldELight/Harold-Lightfoot-Portfolio.git
    cd Harold-Lightfoot-Portfolio/Gogo_Gemini_API
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Add your API key:
    - Open `config.ini` and replace `your_api_key_here` with your actual API key.

## Getting API Key

### Google API Key

1. Visit the [Google Cloud Platform Console](https://console.cloud.google.com/).
2. Create a new project or select an existing project.
3. Navigate to the "APIs & Services" section and enable the `Generative AI` API.
4. Create credentials to obtain an API key.
5. Copy the API key and paste it into the `GOOGLE_API_KEY` field in `config.ini`.

## Usage

1. Run the application:
    ```bash
    python Gogo.py
    ```

## Files

- `Gogo.py`: The main script for the application.
- `config.ini`: Configuration file for the API keys.
- `requirements.txt`: List of required Python packages.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

