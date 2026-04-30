import os
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from config.settings import Config

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Set template folder to web/templates
app.template_folder = 'web/templates'

# Simple AI Handler that connects to Ollama directly
import requests
import json
import subprocess
import time
import platform
import os

class SimpleAIHandler:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.model = "qwen2.5:3b"
        self.is_ollama_available = self._ensure_ollama_running()
        
    def _ensure_ollama_running(self):
        """Check if Ollama is running, start it if not"""
        print("Checking Ollama status...")
        
        # First check if Ollama is already running
        if self._check_ollama():
            print("Ollama is already running!")
            self._ensure_model_available()
            return True
        
        print("Ollama is not running. Starting Ollama...")
        
        # Try to start Ollama
        try:
            # Start Ollama in background
            if platform.system() == "Windows":
                # Windows - run silently without creating new console
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                subprocess.Popen(["ollama", "serve"], 
                               startupinfo=startupinfo,
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            else:
                # Linux/Mac
                subprocess.Popen(["ollama", "serve"], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            
            # Wait a bit for Ollama to start
            print("Waiting for Ollama to start...")
            for i in range(10):  # Wait up to 10 seconds
                time.sleep(1)
                if self._check_ollama():
                    print("Ollama started successfully!")
                    self._ensure_model_available()
                    return True
                print(f"Waiting... ({i+1}/10)")
            
            print("Failed to start Ollama automatically.")
            return False
            
        except FileNotFoundError:
            print("Ollama not found. Please install Ollama first:")
            print("1. Visit https://ollama.ai")
            print("2. Download and install Ollama")
            print("3. Run: ollama pull qwen2.5:3b")
            return False
        except Exception as e:
            print(f"Error starting Ollama: {e}")
            return False
    
    def _check_ollama(self):
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _ensure_model_available(self):
        """Check if the required model is available, pull if not"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model.get("name", "") for model in models]
                
                if self.model not in model_names:
                    print(f"Model {self.model} not found. Pulling model...")
                    try:
                        pull_response = requests.post(
                            f"{self.ollama_url}/api/pull",
                            json={"name": self.model},
                            timeout=300  # 5 minutes timeout for pulling
                        )
                        if pull_response.status_code == 200:
                            print(f"Model {self.model} pulled successfully!")
                        else:
                            print(f"Failed to pull model {self.model}")
                    except Exception as e:
                        print(f"Error pulling model: {e}")
                else:
                    print(f"Model {self.model} is available!")
        except Exception as e:
            print(f"Error checking model availability: {e}")
    
    def _call_ollama(self, prompt, stream=False):
        """Call Ollama API"""
        if not self.is_ollama_available:
            return "AI service is not available. Please make sure Ollama is running."
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": stream
                },
                timeout=30,
                stream=stream
            )
            
            if response.status_code == 200:
                if stream:
                    return response  # Return response object for streaming
                else:
                    result = response.json()
                    return result.get("response", "I couldn't process that request.")
            else:
                return "AI service error. Please try again."
                
        except Exception as e:
            return f"AI service error: {str(e)}"
    
    def answer_email_question(self, message, emails, session_id):
        """Answer questions about emails"""
        if not emails:
            return "I don't have any emails to analyze."
        
        # Create context from emails
        email_context = "Recent emails:\n"
        for i, email in enumerate(emails[:5]):  # Limit to 5 emails
            email_context += f"{i+1}. From: {email['sender']}, Subject: {email['subject']}\n"
            email_context += f"   Content: {email['body_text'][:200]}...\n\n"
        
        prompt = f"""You are an email assistant. Based on these emails, answer the user's question.

{email_context}

User question: {message}

Provide a helpful, concise answer:"""
        
        return self._call_ollama(prompt)
    
    def answer_about_specific_email(self, message, email, session_id):
        """Answer questions about a specific email"""
        if not email:
            return "I don't have that email to analyze."
        
        # Create context from the specific email
        email_context = f"""Email Details:
From: {email['sender']}
Subject: {email['subject']}
Date: {email['date_received'].strftime('%B %d, %Y at %I:%M %p') if email['date_received'] else 'Unknown'}
To: {email['recipients']}

Content:
{email['body_text']}
"""
        
        prompt = f"""You are an email assistant. The user is viewing a specific email and asking questions about it. Answer their question based ONLY on this email content.

{email_context}

User question: {message}

Important: Only use information from this specific email. Do not reference other emails or make assumptions about other messages.

Provide a helpful, concise answer:"""
        
        return self._call_ollama(prompt)
    
    def chat_with_context(self, message, session_id):
        """General chat with AI"""
        prompt = f"""You are a helpful email assistant. You can help users with:
- Finding and organizing emails
- Summarizing email content
- Drafting emails
- Managing calendar events
- Answering questions about their inbox

User message: {message}

Provide a helpful response:"""
        
        return self._call_ollama(prompt)
    
    def summarize_emails(self, emails):
        """Summarize emails"""
        if not emails:
            return "No emails to summarize."
        
        email_text = "Emails to summarize:\n"
        for email in emails:
            email_text += f"From: {email['sender']}\nSubject: {email['subject']}\nContent: {email['body_text'][:300]}...\n\n"
        
        prompt = f"""Summarize these emails in a concise way. Focus on key topics, action items, and important information.

{email_text}

Summary:"""
        
        return self._call_ollama(prompt)
    
    def extract_meeting_info(self, text):
        """Extract meeting information from text"""
        prompt = f"""Extract meeting information from this text. Look for:
- Meeting title/subject
- Date and time
- Location
- Attendees
- Purpose

Text: {text}

Return JSON format with keys: title, date_time, location, attendees, purpose. If no meeting found, return empty JSON."""
        
        try:
            result = self._call_ollama(prompt)
            # Try to parse as JSON
            return json.loads(result)
        except:
            return None
    
    def generate_calendar_event_from_meeting(self, meeting_info, text):
        """Generate calendar event from meeting info"""
        return {
            'title': meeting_info.get('title', 'Meeting'),
            'start_time': meeting_info.get('date_time', (datetime.now() + timedelta(days=1)).isoformat()),
            'end_time': (datetime.now() + timedelta(days=1, hours=1)).isoformat(),
            'description': meeting_info.get('purpose', 'Meeting'),
            'location': meeting_info.get('location', 'TBD')
        }

# Initialize AI Handler
ai_handler = SimpleAIHandler()

if ai_handler.is_ollama_available:
    print("AI Handler loaded successfully - using real Ollama AI")
else:
    print("Ollama not available - using fallback responses")

# Mock data for testing
MOCK_EMAILS = [
    {
        'id': 1,
        'gmail_id': 'mock1',
        'subject': 'Team Meeting Tomorrow',
        'sender': 'john.doe@example.com',
        'recipients': '["you@example.com"]',
        'date_received': datetime.now() - timedelta(hours=2),
        'body_text': 'Hi, just a reminder about our team meeting tomorrow at 2 PM. We\'ll discuss the Q3 roadmap and budget allocations. Please bring your project status updates.',
        'body_html': '<p>Hi, just a reminder about our team meeting tomorrow at 2 PM. We\'ll discuss the Q3 roadmap and budget allocations. Please bring your project status updates.</p>',
        'snippet': 'Hi, just a reminder about our team meeting tomorrow at 2 PM...',
        'is_read': False,
        'is_starred': False
    },
    {
        'id': 2,
        'gmail_id': 'mock2',
        'subject': 'Project Update Required',
        'sender': 'sarah.smith@company.com',
        'recipients': '["you@example.com", "manager@example.com"]',
        'date_received': datetime.now() - timedelta(hours=5),
        'body_text': 'Could you please provide an update on the current project status? The client is asking for progress reports and we need to have something ready by end of day.',
        'body_html': '<p>Could you please provide an update on the current project status? The client is asking for progress reports and we need to have something ready by end of day.</p>',
        'snippet': 'Could you please provide an update on the current project status?...',
        'is_read': True,
        'is_starred': True
    },
    {
        'id': 3,
        'gmail_id': 'mock3',
        'subject': 'Lunch Meeting Friday',
        'sender': 'client@business.com',
        'recipients': '["you@example.com"]',
        'date_received': datetime.now() - timedelta(days=1),
        'body_text': 'Would you be available for lunch this Friday at 12:30 PM? I\'d like to discuss the new contract and go over the terms. There\'s a great restaurant downtown that would be perfect.',
        'body_html': '<p>Would you be available for lunch this Friday at 12:30 PM? I\'d like to discuss the new contract and go over the terms.</p>',
        'snippet': 'Would you be available for lunch this Friday at 12:30 PM?...',
        'is_read': True,
        'is_starred': False
    }
]

MOCK_EVENTS = [
    {
        'id': 1,
        'title': 'Team Meeting',
        'description': 'Q3 roadmap discussion',
        'start_time': datetime.now() + timedelta(hours=22),  # Tomorrow 2 PM
        'end_time': datetime.now() + timedelta(hours=23.5),
        'location': 'Conference Room A',
        'status': 'created'
    },
    {
        'id': 2,
        'title': 'Client Call',
        'description': 'Project status update',
        'start_time': datetime.now() + timedelta(days=2, hours=14),
        'end_time': datetime.now() + timedelta(days=2, hours=15),
        'location': 'Virtual - Zoom',
        'status': 'created'
    }
]

MOCK_SUGGESTIONS = [
    {
        'id': 1,
        'title': 'Lunch Meeting',
        'description': 'Discuss new contract terms',
        'start_time': datetime.now() + timedelta(days=4, hours=12.5),  # Friday 12:30 PM
        'end_time': datetime.now() + timedelta(days=4, hours=14),
        'location': 'Downtown Restaurant',
        'status': 'suggested'
    }
]

class MockDatabase:
    def get_emails(self, limit=20, offset=0, search_query=''):
        emails = MOCK_EMAILS
        if search_query:
            search_lower = search_query.lower()
            emails = [e for e in emails if 
                     search_lower in e['subject'].lower() or 
                     search_lower in e['sender'].lower() or 
                     search_lower in e['body_text'].lower()]
        return emails[offset:offset+limit]
    
    def get_email_by_id(self, email_id):
        for email in MOCK_EMAILS:
            if email['id'] == email_id:
                return email
        return None
    
    def get_email_count(self):
        return len(MOCK_EMAILS)
    
    def get_unread_count(self):
        return len([e for e in MOCK_EMAILS if not e['is_read']])
    
    def add_email(self, **kwargs):
        new_email = {
            'id': len(MOCK_EMAILS) + 1,
            'gmail_id': f"mock{len(MOCK_EMAILS) + 1}",
            **kwargs
        }
        MOCK_EMAILS.append(new_email)
        return new_email
    
    def get_calendar_events(self, status=None):
        events = MOCK_EVENTS
        if status:
            events = [e for e in events if e['status'] == status]
        return events
    
    def add_calendar_event(self, **kwargs):
        new_event = {
            'id': len(MOCK_EVENTS) + 1,
            **kwargs
        }
        MOCK_EVENTS.append(new_event)
        return new_event

class MockEmailProcessor:
    def fetch_emails(self):
        return MOCK_EMAILS
    
    def get_email_count(self):
        return len(MOCK_EMAILS)
    
    def get_unread_count(self):
        return len([e for e in MOCK_EMAILS if not e['is_read']])
    
    def search_emails(self, query, limit=50):
        return [e for e in MOCK_EMAILS if query.lower() in e['subject'].lower()][:limit]
    
    def create_draft(self, to, subject, body, cc=None, bcc=None):
        print(f"Mock draft created: {subject} to {to}")
        return True

class MockCalendar:
    def get_events(self, days_ahead=7):
        return MOCK_EVENTS
    
    def get_suggested_events(self):
        return MOCK_SUGGESTIONS
    
    def suggest_event_from_email(self, email):
        return {
            'suggestion_id': 1,
            'event_data': {
                'title': 'Meeting from email',
                'start_time': (datetime.now() + timedelta(days=2)).isoformat(),
                'end_time': (datetime.now() + timedelta(days=2, hours=1)).isoformat(),
                'location': 'Conference Room',
                'description': 'Meeting extracted from email'
            },
            'conflicts': [],
            'confidence_score': 75
        }
    
    def create_suggested_event(self, suggestion_id):
        return True, {'message': 'Event created successfully'}
    
    def reject_suggestion(self, suggestion_id):
        return True, 'Suggestion rejected'

# Initialize components
db = MockDatabase()
email_processor = MockEmailProcessor()
calendar_manager = MockCalendar()

@app.route('/')
def index():
    """Main dashboard page"""
    email_count = email_processor.get_email_count()
    unread_count = email_processor.get_unread_count()
    recent_emails = db.get_emails(limit=10)
    calendar_suggestions = calendar_manager.get_suggested_events()
    
    return render_template('dashboard.html', 
                         email_count=email_count,
                         unread_count=unread_count,
                         recent_emails=recent_emails,
                         calendar_suggestions=calendar_suggestions)

@app.route('/emails')
def emails():
    """Email list page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    search = request.args.get('search', '')
    
    emails = db.get_emails(limit=per_page, offset=offset, search_query=search)
    
    return render_template('emails.html', emails=emails, page=page, search=search)

@app.route('/emails/<int:email_id>')
def email_detail(email_id):
    """Email detail page"""
    email = db.get_email_by_id(email_id)
    if not email:
        return "Email not found", 404
    
    return render_template('email_detail.html', email=email)

@app.route('/fetch_emails', methods=['POST'])
def fetch_emails():
    """Fetch new emails (mock)"""
    try:
        emails = email_processor.fetch_emails()
        return jsonify({
            'success': True,
            'message': f'Fetched {len(emails)} mock emails',
            'count': len(emails)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat')
def chat():
    """Chat interface page"""
    session_id = session.get('chat_session', str(uuid.uuid4()))
    session['chat_session'] = session_id
    
    return render_template('chat.html', session_id=session_id)

from flask import Response
import json

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Chat API endpoint"""
    data = request.get_json()
    message = data.get('message', '')
    session_id = data.get('session_id', '')
    email_id = data.get('email_id')  # Get email_id if on email detail page
    stream = data.get('stream', True)  # Default to streaming
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    try:
        # Check if we're on an email detail page and should analyze that specific email
        if email_id:
            email = db.get_email_by_id(email_id)
            if email:
                if stream:
                    return Response(
                        stream_ai_response(ai_handler, 'answer_about_specific_email', message, email, session_id),
                        mimetype='text/plain'
                    )
                else:
                    response = ai_handler.answer_about_specific_email(message, email, session_id)
                    return jsonify({'response': response})
            else:
                response = "Email not found."
        # Check if this is a general question about emails
        elif any(keyword in message.lower() for keyword in ['email', 'emails', 'mail', 'message']):
            recent_emails = db.get_emails(limit=10)
            email_dicts = []
            for email in recent_emails:
                email_dicts.append({
                    'id': email['id'],
                    'gmail_id': email['gmail_id'],
                    'subject': email['subject'],
                    'sender': email['sender'],
                    'date_received': email['date_received'].isoformat(),
                    'body_text': email['body_text'],
                    'snippet': email['snippet']
                })
            
            if stream:
                return Response(
                    stream_ai_response(ai_handler, 'answer_email_question', message, email_dicts, session_id),
                    mimetype='text/plain'
                )
            else:
                response = ai_handler.answer_email_question(message, email_dicts, session_id)
        elif any(keyword in message.lower() for keyword in ['calendar', 'event', 'meeting', 'schedule']):
            response = handle_calendar_question(message, session_id)
        elif any(keyword in message.lower() for keyword in ['draft', 'compose', 'write', 'send']):
            response = handle_draft_creation(message, session_id)
        else:
            if stream:
                return Response(
                    stream_ai_response(ai_handler, 'chat_with_context', message, None, session_id),
                    mimetype='text/plain'
                )
            else:
                response = ai_handler.chat_with_context(message, session_id)
        
        return jsonify({'response': response})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def stream_ai_response(ai_handler, method_name, message, context, session_id):
    """Stream AI response word by word"""
    try:
        # Get the appropriate prompt based on method
        if method_name == 'answer_about_specific_email':
            email = context
            email_context = f"""Email Details:
From: {email['sender']}
Subject: {email['subject']}
Date: {email['date_received'].strftime('%B %d, %Y at %I:%M %p') if email['date_received'] else 'Unknown'}
To: {email['recipients']}

Content:
{email['body_text']}
"""
            prompt = f"""You are an email assistant. The user is viewing a specific email and asking questions about it. Answer their question based ONLY on this email content.

{email_context}

User question: {message}

Important: Only use information from this specific email. Do not reference other emails or make assumptions about other messages.

Provide a helpful, concise answer:"""
        elif method_name == 'answer_email_question':
            emails = context
            email_context = "Recent emails:\n"
            for i, email in enumerate(emails[:5]):
                email_context += f"{i+1}. From: {email['sender']}, Subject: {email['subject']}\n"
                email_context += f"   Content: {email['body_text'][:200]}...\n\n"
            prompt = f"""You are an email assistant. Based on these emails, answer the user's question.

{email_context}

User question: {message}

Provide a helpful, concise answer:"""
        else:  # chat_with_context
            prompt = f"""You are a helpful email assistant. You can help users with:
- Finding and organizing emails
- Summarizing email content
- Drafting emails
- Managing calendar events
- Answering questions about their inbox

User message: {message}

Provide a helpful response:"""
        
        # Call Ollama with streaming
        response = ai_handler._call_ollama(prompt, stream=True)
        
        if isinstance(response, str):  # Error occurred
            yield f"data: {json.dumps({'error': response})}\n\n"
        else:
            # Stream the response
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if 'response' in data:
                            yield f"data: {json.dumps({'content': data['response']})}\n\n"
                        elif 'done' in data and data['done']:
                            yield f"data: {json.dumps({'done': True})}\n\n"
                            break
                    except json.JSONDecodeError:
                        continue
                        
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

@app.route('/calendar')
def calendar():
    """Calendar page"""
    upcoming_events = calendar_manager.get_events(days_ahead=7)
    suggested_events = calendar_manager.get_suggested_events()
    
    return render_template('calendar.html', 
                         upcoming_events=upcoming_events,
                         suggested_events=suggested_events)

@app.route('/api/suggest_event', methods=['POST'])
def api_suggest_event():
    """Suggest calendar event from email"""
    data = request.get_json()
    email_id = data.get('email_id')
    
    if not email_id:
        return jsonify({'error': 'Email ID is required'}), 400
    
    try:
        email = db.get_email_by_id(email_id)
        if not email:
            return jsonify({'error': 'Email not found'}), 404
        
        suggestion = calendar_manager.suggest_event_from_email(email)
        
        if suggestion:
            return jsonify({
                'success': True,
                'suggestion': suggestion
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No meeting information found in email'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/create_event', methods=['POST'])
def api_create_event():
    """Create calendar event from suggestion"""
    data = request.get_json()
    suggestion_id = data.get('suggestion_id')
    
    if not suggestion_id:
        return jsonify({'error': 'Suggestion ID is required'}), 400
    
    try:
        success, result = calendar_manager.create_suggested_event(suggestion_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Event created successfully',
                'event': result
            })
        else:
            return jsonify({
                'success': False,
                'error': result
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reject_suggestion', methods=['POST'])
def api_reject_suggestion():
    """Reject calendar event suggestion"""
    data = request.get_json()
    suggestion_id = data.get('suggestion_id')
    
    if not suggestion_id:
        return jsonify({'error': 'Suggestion ID is required'}), 400
    
    try:
        success, result = calendar_manager.reject_suggestion(suggestion_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': result
            })
        else:
            return jsonify({
                'success': False,
                'error': result
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/create_draft', methods=['POST'])
def api_create_draft():
    """Create email draft"""
    data = request.get_json()
    
    try:
        success = email_processor.create_draft(
            to=data.get('to', ''),
            subject=data.get('subject', ''),
            body=data.get('body', ''),
            cc=data.get('cc'),
            bcc=data.get('bcc')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Draft created successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create draft'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/summarize_emails', methods=['POST'])
def api_summarize_emails():
    """Summarize recent emails"""
    try:
        recent_emails = db.get_emails(limit=20)
        email_dicts = []
        for email in recent_emails:
            email_dicts.append({
                'id': email['id'],
                'gmail_id': email['gmail_id'],
                'subject': email['subject'],
                'sender': email['sender'],
                'date_received': email['date_received'].isoformat(),
                'body_text': email['body_text'],
                'snippet': email['snippet']
            })
        
        summary = ai_handler.summarize_emails(email_dicts)
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def handle_calendar_question(message, session_id):
    """Handle calendar-related questions"""
    try:
        events = calendar_manager.get_events(days_ahead=7)
        
        if not events:
            return "You don't have any upcoming events in the next 7 days."
        
        events_text = "Upcoming events:\n"
        for event in events:
            events_text += f"- {event['title']} on {event['start_time'].strftime('%B %d at %I:%M %p')}\n"
        
        return f"Here are your upcoming events:\n{events_text}"
        
    except Exception as e:
        return f"Error handling calendar question: {str(e)}"

def handle_draft_creation(message, session_id):
    """Handle email draft creation"""
    return "I've created a draft for your email. You can check it in your drafts folder."

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    import webbrowser
    import threading
    import time
    
    def open_browser():
        """Open browser after a short delay to ensure server is running"""
        time.sleep(1.5)  # Wait for server to start
        webbrowser.open('http://localhost:5000')
    
    print("🚀 Starting Mock Email Bot (for testing)")
    print("📧 This version uses mock data - no real credentials needed!")
    print("🌐 Opening web interface at: http://localhost:5000")
    print("💭 Try asking: 'Show me emails about meetings' or 'What meetings do I have?'")
    
    # Start browser in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
