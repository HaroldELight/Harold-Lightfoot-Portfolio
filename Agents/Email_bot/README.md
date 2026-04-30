# Simple Email Bot - Free Version

A completely free AI-powered email assistant that reads your Gmail, answers questions about your emails, and manages your calendar using local AI.

## Features

- **Email Q&A**: Ask questions about your emails using natural language
- **Calendar Management**: Create events and check for conflicts
- **Email Drafts**: Generate email drafts with AI assistance
- **Web Interface**: Clean, responsive web UI
- **100% Free**: No API costs, no cloud services required

## Architecture

- **Email Access**: IMAP (Gmail) - completely free
- **AI Processing**: Local Qwen model via Ollama
- **Calendar**: Local calendar system
- **Database**: SQLite for email metadata
- **Web Interface**: Flask with Bootstrap

## Quick Start

### Prerequisites

1. **Ollama** (Local AI)
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Start Ollama
   ollama serve
   
   # Pull Qwen model
   ollama pull qwen2.5:3b
   ```

2. **Gmail App Password**
   - Enable 2-Step Verification in your Google Account
   - Go to Google Account settings > Security > App Passwords
   - Generate a new app password for "Mail"
   - Copy the 16-character password

### Installation

1. **Install Dependencies**
   ```bash
   cd Agents/Email_bot
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Edit .env file**
   ```env
   # Your Gmail address
   GMAIL_EMAIL=your_email@gmail.com
   
   # Your 16-character app password
   GMAIL_APP_PASSWORD=your_16_char_app_password
   
   # Ollama settings (usually these defaults work)
   OLLAMA_URL=http://localhost:11434
   OLLAMA_MODEL=qwen2.5:3b
   
   # Flask secret key (generate any random string)
   FLASK_SECRET_KEY=your_random_secret_key_here
   ```

4. **Run the Application**
   ```bash
   python simple_app.py
   ```
   
   Visit `http://localhost:5000` in your browser.

## Usage

### Email Questions
Ask natural language questions about your emails:
- "Show me emails from John"
- "What emails do I have about project X?"
- "Summarize my recent emails"
- "Find emails from last week"

### Calendar Management
- "What meetings do I have tomorrow?"
- "Create a meeting with the team at 2 PM tomorrow"
- "Check for conflicts on Friday"
- "Show me my upcoming events"

### Email Drafts
- "Draft an email to john@example.com about the meeting"
- "Write a follow-up email to Sarah"
- "Create a draft for the project update"

## Web Interface

The bot provides a clean web interface with:

- **Dashboard**: Email statistics and recent emails
- **Email List**: Browse and search emails
- **Chat Interface**: Natural language conversation
- **Calendar**: View and manage events

## File Structure

```
Email_bot/
simple_app.py              # Main application (free version)
core/
  imap_email_processor.py  # IMAP email access
  local_calendar.py        # Local calendar system
  database.py              # Database operations
ai/
  ai_handler.py            # Qwen AI integration
web/
  templates/               # HTML templates
  static/                  # CSS and JavaScript
config/
  settings.py              # Configuration
.env.example              # Environment template
requirements.txt          # Dependencies (no Google APIs)
SETUP.md                  # Detailed setup guide
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GMAIL_EMAIL` | Your Gmail address | Yes |
| `GMAIL_APP_PASSWORD` | Gmail app password (16 chars) | Yes |
| `OLLAMA_URL` | Ollama API URL | No (default: http://localhost:11434) |
| `OLLAMA_MODEL` | Ollama model name | No (default: qwen2.5:3b) |
| `FLASK_SECRET_KEY` | Flask secret key | Yes |
| `EMAIL_FETCH_LIMIT` | Number of emails to fetch | No (default: 100) |
| `EMAIL_FETCH_DAYS` | Days back to fetch | No (default: 30) |

## Security

- **Local Processing**: All AI processing happens on your machine
- **Secure IMAP**: SSL-encrypted connection to Gmail
- **No External APIs**: No Google Cloud services required
- **Privacy**: No data sent to external services

## Troubleshooting

### IMAP Connection Issues
1. Verify your Gmail app password is correct (16 characters)
2. Enable "Less secure app access" in Gmail settings
3. Make sure 2-Step Verification is enabled

### Ollama Issues
1. Ensure Ollama is running: `ollama serve`
2. Check if Qwen model is installed: `ollama list`
3. Pull the model: `ollama pull qwen2.5:3b`

### Database Issues
- The app creates a SQLite database automatically in `data/emails.db`
- If you get database errors, delete the `data/` folder and restart

### Common Errors
- **"Invalid credentials"**: Check your Gmail app password
- **"Connection failed"**: Ensure Ollama is running
- **"Configuration error"**: Verify all environment variables are set

## API Endpoints

### Email Operations
- `POST /api/fetch_emails` - Fetch new emails from Gmail
- `GET /emails` - View email list
- `GET /emails/<id>` - View email details

### AI Chat
- `POST /api/chat` - Send message to AI assistant

### Calendar Operations
- `POST /api/suggest_event` - Suggest event from email
- `POST /api/create_event` - Create calendar event
- `POST /api/reject_suggestion` - Reject event suggestion

### Email Drafts
- `POST /api/create_draft` - Create email draft

## Development

### Running in Development
```bash
# Set development environment
export FLASK_ENV=development

# Run with debug mode
python simple_app.py
```

### Project Structure
- **Modular Design**: Separate components for email, calendar, AI
- **SQLite Database**: Local data storage
- **Bootstrap UI**: Responsive web interface
- **Local AI**: No external AI services required

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the SETUP.md file for detailed instructions
3. Ensure all prerequisites are properly configured

## License

This project is licensed under the MIT License.

---

**Privacy Notice**: This application processes your emails locally using AI. No email content is sent to external services except for the local Ollama instance. Your Gmail credentials are stored locally and used only for IMAP access to your own account.
