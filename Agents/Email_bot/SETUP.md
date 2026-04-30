# Simple Email Bot Setup - Free Version

## Overview
This is a completely free email chatbot that uses IMAP to access Gmail and local Qwen AI for processing.

## Prerequisites

### 1. Ollama (Local AI)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve

# Pull Qwen model (free)
ollama pull qwen2.5:3b
```

### 2. Gmail App Password (Free)
1. Enable 2-Step Verification in your Google Account
2. Go to Google Account settings > Security
3. Click on "App Passwords"
4. Generate a new app password for "Mail"
5. Copy the 16-character password

## Installation

### 1. Install Dependencies
```bash
cd Agents/Email_bot
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
```

### 3. Edit .env file
```env
# Your Gmail address
GMAIL_EMAIL=your_email@gmail.com

# Your 16-character app password (from Google Account settings)
GMAIL_APP_PASSWORD=your_16_char_app_password

# Ollama settings (usually these defaults work)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b

# Flask secret key (generate any random string)
FLASK_SECRET_KEY=your_random_secret_key_here
```

### 4. Run the Application
```bash
python simple_app.py
```

Visit `http://localhost:5000` in your browser.

## Features

### Email Q&A
- Ask questions about your emails
- "Show me emails from John"
- "What emails do I have about project X?"
- "Summarize my recent emails"

### Calendar Management
- Automatic meeting detection from emails
- Create calendar events
- View upcoming events
- Check scheduling conflicts

### Email Drafts
- "Draft an email to john@example.com about the meeting"
- "Write a follow-up email to Sarah"

## Usage Examples

### Email Questions
```
User: "What emails do I have from my boss?"
AI: "You have 3 emails from your boss this week..."

User: "Show me emails about the project deadline"
AI: "Found 2 emails about the project deadline..."
```

### Calendar Management
```
User: "What meetings do I have tomorrow?"
AI: "You have 2 meetings tomorrow..."

User: "Create a meeting with the team at 2 PM tomorrow"
AI: "I'll create a calendar event for that..."
```

### Email Drafts
```
User: "Draft an email to client@company.com about the proposal"
AI: "I've created a draft for the proposal email..."
```

## Troubleshooting

### IMAP Connection Issues
1. Check your Gmail app password (16 characters)
2. Enable "Less secure app access" in Gmail settings
3. Make sure 2-Step Verification is enabled

### Ollama Issues
1. Make sure Ollama is running: `ollama serve`
2. Check if Qwen model is installed: `ollama list`
3. Pull the model: `ollama pull qwen2.5:3b`

### Database Issues
- The app creates a SQLite database automatically in `data/emails.db`
- If you get database errors, delete the `data/` folder and restart

## Security Notes

- Your Gmail app password is stored locally in the .env file
- All AI processing happens locally on your machine
- No data is sent to external services except Ollama (local)
- IMAP connections are encrypted with SSL

## File Structure
```
Email_bot/
simple_app.py              # Main application (free version)
core/
  imap_email_processor.py  # IMAP email access
  local_calendar.py         # Local calendar system
  database.py              # Database operations
ai/
  ai_handler.py            # Qwen AI integration
web/
  templates/               # Web interface
  static/                  # CSS and JS
.env.example              # Environment template
requirements.txt          # Dependencies (no Google APIs)
```

## Next Steps

Once this is working, you can:
1. Add more email features (reply, forward)
2. Enhance calendar integration
3. Add file attachment support
4. Create mobile-friendly interface

## Support

If you encounter issues:
1. Check that Ollama is running and has the Qwen model
2. Verify your Gmail app password is correct
3. Make sure all environment variables are set in .env
4. Check the console output for error messages
