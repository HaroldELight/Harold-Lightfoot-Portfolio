Here's your README:

---

```markdown
# Research AI

A desktop research assistant that fetches and summarizes web content using local or online LLMs.

## Features

- GUI interface built with Tkinter
- Supports Gemini (online), Mistral, and Qwen (local via Ollama)
- Fetches and summarizes Wikipedia or custom URLs
- Adjustable summary length (preview or 1-5 pages)
- Falls back to model training data if internet is unavailable

## Requirements

- Python 3.10+
- Ollama (for local models)
- Gemini API key (for online mode)

## Installation

1. Clone the repo
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_key_here
   ```

## Usage

```bash
python Research_AI.py
```

1. Enter a research topic
2. Select a model (Gemini, Mistral, or Qwen)
3. Choose summary length
4. Use Wikipedia or enter custom URLs
5. Click Generate Summary

## Local Models (Ollama)

```bash
ollama pull qwen2.5:3b
ollama pull mistral
```

## License

MIT
```