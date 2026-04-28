# Research AI

A desktop research assistant that fetches and summarizes web content using local LLMs.

## Features

- 🖥️ Clean GUI interface built with Tkinter
- 🤖 Local model support via Ollama (Qwen2.5)
- 🌐 Smart URL fetching from Wikipedia + OpenAlex or custom URLs
- 📝 Adjustable summary length (preview or 1-5 pages)
- 🔄 Real-time streaming output
- 📋 Copy to clipboard functionality
- 🧹 Clear output button for easy reset
- ⚡ Parallel URL fetching for faster results
- 🛡️ Falls back to model training data if web content unavailable
- 🔒 100% local processing - no external API dependencies

## Requirements

- Python 3.10+
- Ollama (for local models)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Agents
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your Ollama settings:
```env
# Ollama server URL (default is fine for most users)
OLLAMA_URL=http://localhost:11434

# Optional: Custom model name
OLLAMA_MODEL=qwen2.5:3b
```

## Usage

### Start the Application
```bash
python Research_AI.py
```

### Using the GUI

1. **Enter Research Topic**: Type your research question or topic
2. **Model**: Uses Qwen2.5 locally via Ollama
3. **Choose Summary Length**: 
   - `preview` - Quick overview
   - `1-5 pages` - Detailed summaries
4. **Select URL Sources**:
   - ✅ **Use default URLs** - Auto-finds Wikipedia + OpenAlex articles
   - ✅ **Use custom URLs** - Enter your own URLs (comma-separated)
   - ✅ **LLM Only** - Skip web search, use model knowledge only
5. **Generate**: Click "Generate Summary" to start

### Features in Action

- **Stop**: Cancel ongoing requests
- **Copy Output**: Copy results to clipboard
- **Clear Output**: Reset both progress and output areas

## Local Models Setup (Ollama)

### Install Ollama
```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: Download from https://ollama.ai/download
```

### Pull Models
```bash
# Recommended lightweight model
ollama pull qwen2.5:3b

# Alternative models
ollama pull llama3.1:8b
ollama pull mistral
```

### Start Ollama Server
```bash
ollama serve
```

## Troubleshooting

### Common Issues

**"Connection Error"**
- Ensure Ollama is running: `ollama serve`
- Check if model is pulled: `ollama list`

**"No relevant content found"**
- Try different URLs or enable "LLM Only" mode
- Check internet connectivity

**Performance Issues**
- Use shorter summary lengths for faster results
- Ensure Ollama has sufficient system resources

**Ollama Not Working**
```bash
# Check Ollama status
ollama list

# Restart Ollama service
ollama serve
```

## Development

### Project Structure
```
Agents/
├── Research_AI.py      # Main application
├── requirements.txt    # Python dependencies
├── .env.example       # Environment template
└── README.md          # This file
```

### Dependencies
- `python-dotenv` - Environment variable management
- `requests` - HTTP requests for web fetching
- `beautifulsoup4` - HTML parsing
- `ollama` - Local model client

## Benefits of Local Setup

- ✅ **Privacy**: All processing happens locally
- ✅ **No API Costs**: Free to use after setup
- ✅ **Offline Capability**: Works without internet (except for web fetching)
- ✅ **Customizable**: Use any Ollama-compatible model
- ✅ **Fast Response**: No network latency for model inference

## License

MIT License

## Contributing

Feel free to submit issues and enhancement requests!