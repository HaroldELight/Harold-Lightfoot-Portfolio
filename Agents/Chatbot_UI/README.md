# 🤖 Qwen Personal Assistant

A sophisticated Personal Assistant with continuous learning memory, built with Python/Tkinter and powered by Qwen AI via Ollama.

## ✨ Features

- 🧠 **Continuous Learning** - Learns from every conversation automatically
- 💭 **Smart Memory** - Remembers your name, preferences, and conversation topics
- 🔍 **Memory Search** - Find any past conversation instantly
- 📱 **Modern GUI** - Clean, responsive interface with streaming responses
- 💾 **Auto-Save** - Conversations saved automatically to local files
- 🎯 **Context-Aware** - Uses past conversations to provide personalized responses

## 🚀 Quick Start

### Prerequisites

1. **Install Python 3.8+**
2. **Install Ollama**: [https://ollama.ai](https://ollama.ai)
3. **Start Ollama**: `ollama serve`
4. **Install Qwen model**: `ollama pull qwen2.5:3b`

### Installation

```bash
# Clone or download this repository
git clone <repository-url>
cd Chatbot_UI

# Install dependencies
pip install -r requirements.txt

# Run the Personal Assistant
python Qwentin.py
```

### Usage

1. **Launch**: Run `python Qwentin.py` - GUI opens automatically (no terminal)
2. **Chat**: Start talking to your AI assistant
3. **Memory**: Click "Memory" button to see what it learned about you
4. **History**: Browse past conversations with the "History" button

## 🧠 Memory System

Your PA automatically builds three types of memory:

### Personal Facts
- Learns your name when you say "My name is..."
- Remembers preferences ("I like...", "I don't like...")
- Tracks personal facts ("I am...")

### Topic Memory
- Categorizes conversations (technology, science, business, etc.)
- Tracks discussion frequency and key points
- Provides topic-relevant context

### Global Memory
- All conversations indexed and searchable
- Smart context retrieval for better responses
- Continuous learning from every interaction

## 📁 File Structure

```
Chatbot_UI/
├── Qwentin.py           # Main Personal Assistant (run this)
├── memory_manager.py    # Memory management system
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .gitignore          # Excludes personal data
└── memory/             # Personal data (auto-created, gitignored)
    ├── global_memory.json
    ├── personal_facts.json
    └── topics.json
```

## 🔧 Configuration

The Personal Assistant works out-of-the-box with these settings:

- **Model**: `qwen2.5:3b` (via Ollama)
- **Memory**: Automatic, stored locally in `memory/` folder
- **Context**: Last 10 messages + relevant memories
- **UI**: 800x600 window, streaming responses

## 🛡️ Privacy

- **100% Local**: All data stored on your machine
- **No Cloud**: Works offline once Ollama is running
- **Private Memory**: Personal data excluded from Git via `.gitignore`
- **Open Source**: Transparent, auditable code

## 🎯 Tips for Best Results

1. **Be Natural**: Talk normally - the PA learns from patterns
2. **Share Preferences**: Say "I like..." or "I don't like..."
3. **Use Memory Button**: Check what it learned about you
4. **Search Memory**: Find past conversations easily
5. **Continuous Learning**: Gets smarter with every conversation

## 🔍 Memory Management

Click the **Memory** button to:
- View personal facts learned
- See topic discussions
- Search conversation history
- Check memory statistics

## 🤝 Contributing

Feel free to:
- Report issues
- Suggest features
- Submit pull requests
- Share improvements

## 📄 License

Open source - use, modify, and share freely.

## 🆘 Troubleshooting

**Q: "Ollama not running" error**
- Run `ollama serve` in terminal

**Q: "Qwen not found" error**  
- Run `ollama pull qwen2.5:3b`

**Q: Import errors**
- Ensure all files are present
- Install requirements: `pip install -r requirements.txt`

**Q: GUI doesn't open**
- Run `Qwentin.py` directly
- Check Python version (3.8+ required)

---

**Enjoy your Personal Assistant!** 🚀
