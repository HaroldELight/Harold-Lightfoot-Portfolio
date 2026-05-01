import os
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mock-secret-key-for-testing')

# Set template folder to web/templates
app.template_folder = 'web/templates'

# SAFETY RESTRICTIONS - Bot is READ-ONLY for security
SAFETY_MODE = True  # Always enabled
ALLOWED_OPERATIONS = ['read', 'search', 'draft']  # No delete, send, or modify

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

import imaplib
import email
from email.header import decode_header

class SecureIMAPEmailProcessor:
    def __init__(self):
        self.gmail_email = os.getenv('GMAIL_EMAIL', '')
        self.gmail_app_password = os.getenv('GMAIL_APP_PASSWORD', '')
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993
        self.use_mock = not (self.gmail_email and self.gmail_app_password)
        
        # SAFETY: Always enforce read-only mode
        self.read_only = True
        self.safety_mode = SAFETY_MODE
        
        if self.use_mock:
            print("Using mock email data (no IMAP credentials provided)")
        else:
            print(f"Using READ-ONLY IMAP for {self.gmail_email}")
            print("SECURITY: Bot is in READ-ONLY mode - cannot delete or send emails")
    
    def _connect_imap(self):
        """Connect to IMAP server in read-only mode"""
        if self.use_mock:
            return None
            
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.gmail_email, self.gmail_app_password)
            return mail
        except Exception as e:
            print(f"IMAP connection error: {e}")
            return None
    
    def _decode_header(self, header):
        """Decode email header"""
        if header:
            decoded_parts = decode_header(header)
            header_str = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    header_str += part.decode(encoding or 'utf-8', errors='ignore')
                else:
                    header_str += part
            return header_str
        return ""
    
    def _parse_email(self, mail, email_id):
        """Parse email from IMAP"""
        try:
            # Fetch email
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            if status != 'OK':
                return None
            
            # Parse email content
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            # Extract headers
            subject = self._decode_header(msg['subject'])
            sender = self._decode_header(msg['from'])
            recipients = self._decode_header(msg['to'])
            date_str = msg['date']
            
            # Parse date
            date_received = None
            if date_str:
                try:
                    from email.utils import parsedate_to_datetime
                    date_received = parsedate_to_datetime(date_str)
                except:
                    date_received = datetime.now()
            else:
                date_received = datetime.now()
            
            # Extract body
            body_text = ""
            body_html = ""
            
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        try:
                            body_text = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        except:
                            body_text = str(part.get_payload(decode=True))
                    elif content_type == "text/html":
                        try:
                            body_html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        except:
                            body_html = str(part.get_payload(decode=True))
            else:
                content_type = msg.get_content_type()
                if content_type == "text/plain":
                    try:
                        body_text = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        body_text = str(msg.get_payload(decode=True))
                elif content_type == "text/html":
                    try:
                        body_html = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        body_html = str(msg.get_payload(decode=True))
            
            # Create snippet
            snippet = body_text[:100] + "..." if len(body_text) > 100 else body_text
            
            return {
                'id': int(email_id),
                'gmail_id': str(email_id),
                'subject': subject,
                'sender': sender,
                'recipients': recipients,
                'date_received': date_received,
                'body_text': body_text,
                'body_html': body_html,
                'snippet': snippet,
                'is_read': False,  # Will be updated based on IMAP flags
                'is_starred': False
            }
            
        except Exception as e:
            print(f"Error parsing email {email_id}: {e}")
            return None
    
    def fetch_emails(self, limit=50):
        """Fetch emails from IMAP or return mock data (READ-ONLY)"""
        if self.use_mock:
            return MOCK_EMAILS
        
        mail = self._connect_imap()
        if not mail:
            print("Failed to connect to IMAP, using mock data")
            return MOCK_EMAILS
        
        try:
            # Select inbox in read-only mode
            mail.select('inbox', readonly=True)
            
            # Search for all emails
            status, messages = mail.search(None, 'ALL')
            if status != 'OK':
                print("No messages found")
                return MOCK_EMAILS
            
            # Get email IDs
            email_ids = messages[0].split()
            
            # Fetch recent emails (limit to most recent)
            recent_emails = []
            for email_id in email_ids[-limit:]:
                email_data = self._parse_email(mail, email_id)
                if email_data:
                    recent_emails.append(email_data)
            
            # Sort by date (newest first)
            recent_emails.sort(key=lambda x: x['date_received'], reverse=True)
            
            mail.close()
            mail.logout()
            
            return recent_emails
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            try:
                mail.close()
                mail.logout()
            except:
                pass
            return MOCK_EMAILS
    
    def get_email_count(self):
        """Get total email count (READ-ONLY)"""
        if self.use_mock:
            return len(MOCK_EMAILS)
        
        mail = self._connect_imap()
        if not mail:
            return len(MOCK_EMAILS)
        
        try:
            mail.select('inbox', readonly=True)
            status, messages = mail.search(None, 'ALL')
            if status == 'OK':
                count = len(messages[0].split())
            else:
                count = len(MOCK_EMAILS)
            
            mail.close()
            mail.logout()
            return count
        except Exception as e:
            print(f"Error getting email count: {e}")
            return len(MOCK_EMAILS)
    
    def get_unread_count(self):
        """Get unread email count (READ-ONLY)"""
        if self.use_mock:
            return len([e for e in MOCK_EMAILS if not e['is_read']])
        
        mail = self._connect_imap()
        if not mail:
            return len([e for e in MOCK_EMAILS if not e['is_read']])
        
        try:
            mail.select('inbox', readonly=True)
            status, messages = mail.search(None, 'UNSEEN')
            if status == 'OK':
                count = len(messages[0].split())
            else:
                count = 0
            
            mail.close()
            mail.logout()
            return count
        except Exception as e:
            print(f"Error getting unread count: {e}")
            return 0
    
    def search_emails(self, query, limit=50, offset=0):
        """Search emails (READ-ONLY)"""
        emails = self.fetch_emails(limit=100)  # Fetch more for better search
        search_lower = query.lower()
        
        filtered_emails = []
        for e in emails:
            if (search_lower in e['subject'].lower() or 
                search_lower in e['sender'].lower() or 
                search_lower in e['body_text'].lower()):
                filtered_emails.append(e)
        
        return filtered_emails[offset:offset+limit]
    
    def get_email_by_id(self, email_id):
        """Get email by ID (READ-ONLY)"""
        emails = self.fetch_emails(limit=100)
        for email in emails:
            if email['id'] == email_id:
                return email
        return None
    
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
        """Create email draft (NO SENDING - DRAFT ONLY)"""
        try:
            conn = sqlite3.connect('data/drafts.db')
            cursor = conn.cursor()
            
            # Create drafts table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS drafts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    to_email TEXT NOT NULL,
                    cc_email TEXT,
                    bcc_email TEXT,
                    subject TEXT NOT NULL,
                    body TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert draft
            cursor.execute('''
                INSERT INTO drafts (to_email, cc_email, bcc_email, subject, body)
                VALUES (?, ?, ?, ?, ?)
            ''', (to, cc, bcc, subject, body))
            
            draft_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"Draft saved: ID {draft_id} - {subject} to {to}")
            return draft_id
            
        except Exception as e:
            print(f"Error saving draft: {e}")
            return None
    
    def get_drafts(self, limit=20):
        """Get saved drafts"""
        try:
            conn = sqlite3.connect('data/drafts.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, to_email, cc_email, bcc_email, subject, body, created_at, updated_at
                FROM drafts
                ORDER BY updated_at DESC
                LIMIT ?
            ''', (limit,))
            
            drafts = []
            for row in cursor.fetchall():
                draft = {
                    'id': row[0],
                    'to': row[1],
                    'cc': row[2],
                    'bcc': row[3],
                    'subject': row[4],
                    'body': row[5],
                    'created_at': row[6],
                    'updated_at': row[7]
                }
                drafts.append(draft)
            
            conn.close()
            return drafts
            
        except Exception as e:
            print(f"Error getting drafts: {e}")
            return []
    
    def delete_draft(self, draft_id):
        """Delete draft (SAFE - only deletes local draft)"""
        try:
            conn = sqlite3.connect('data/drafts.db')
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM drafts WHERE id = ?', (draft_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error deleting draft: {e}")
            return False

import sqlite3
import json

class LocalCalendar:
    def __init__(self):
        self.db_path = 'data/calendar.db'
        self.init_database()
    
    def init_database(self):
        """Initialize calendar database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                location TEXT,
                status TEXT DEFAULT 'created',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create suggestions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                location TEXT,
                status TEXT DEFAULT 'suggested',
                email_id TEXT,
                confidence_score INTEGER DEFAULT 50,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_events(self, days_ahead=7):
        """Get upcoming events"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate date range
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days_ahead)
        
        cursor.execute('''
            SELECT id, title, description, start_time, end_time, location, status
            FROM events 
            WHERE start_time >= ? AND start_time <= ?
            ORDER BY start_time ASC
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        events = []
        for row in cursor.fetchall():
            event = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'start_time': datetime.fromisoformat(row[3]),
                'end_time': datetime.fromisoformat(row[4]),
                'location': row[5],
                'status': row[6]
            }
            events.append(event)
        
        conn.close()
        
        # If no real events, return mock data for testing
        if not events:
            return MOCK_EVENTS
        
        return events
    
    def get_suggested_events(self):
        """Get event suggestions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, description, start_time, end_time, location, status, confidence_score
            FROM suggestions 
            WHERE status = 'suggested'
            ORDER BY created_at DESC
        ''')
        
        suggestions = []
        for row in cursor.fetchall():
            suggestion = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'start_time': datetime.fromisoformat(row[3]),
                'end_time': datetime.fromisoformat(row[4]),
                'location': row[5],
                'status': row[6],
                'confidence_score': row[7]
            }
            suggestions.append(suggestion)
        
        conn.close()
        
        # If no real suggestions, return mock data for testing
        if not suggestions:
            return MOCK_SUGGESTIONS
        
        return suggestions
    
    def suggest_event_from_email(self, email):
        """Suggest event from email using AI"""
        try:
            # Use AI to extract meeting info
            meeting_info = ai_handler.extract_meeting_info(email['body_text'])
            
            if meeting_info:
                # Generate event from meeting info
                event_data = ai_handler.generate_calendar_event_from_meeting(meeting_info, email['body_text'])
                
                # Save suggestion to database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO suggestions (title, description, start_time, end_time, location, email_id, confidence_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event_data['title'],
                    event_data['description'],
                    event_data['start_time'],
                    event_data['end_time'],
                    event_data['location'],
                    str(email['id']),
                    meeting_info.get('confidence_score', 50)
                ))
                
                suggestion_id = cursor.lastrowid
                conn.commit()
                conn.close()
                
                return {
                    'suggestion_id': suggestion_id,
                    'event_data': event_data,
                    'conflicts': [],  # TODO: Check for conflicts
                    'confidence_score': meeting_info.get('confidence_score', 50)
                }
            else:
                return None
                
        except Exception as e:
            print(f"Error suggesting event from email: {e}")
            return None
    
    def create_suggested_event(self, suggestion_id):
        """Create event from suggestion"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get suggestion
            cursor.execute('''
                SELECT title, description, start_time, end_time, location
                FROM suggestions 
                WHERE id = ? AND status = 'suggested'
            ''', (suggestion_id,))
            
            suggestion = cursor.fetchone()
            if not suggestion:
                conn.close()
                return False, {'error': 'Suggestion not found'}
            
            # Create event
            cursor.execute('''
                INSERT INTO events (title, description, start_time, end_time, location)
                VALUES (?, ?, ?, ?, ?)
            ''', suggestion)
            
            # Update suggestion status
            cursor.execute('''
                UPDATE suggestions 
                SET status = 'accepted' 
                WHERE id = ?
            ''', (suggestion_id,))
            
            conn.commit()
            conn.close()
            
            return True, {'message': 'Event created successfully'}
            
        except Exception as e:
            print(f"Error creating event from suggestion: {e}")
            return False, {'error': str(e)}
    
    def reject_suggestion(self, suggestion_id):
        """Reject event suggestion"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE suggestions 
                SET status = 'rejected' 
                WHERE id = ?
            ''', (suggestion_id,))
            
            conn.commit()
            conn.close()
            
            return True, 'Suggestion rejected'
            
        except Exception as e:
            print(f"Error rejecting suggestion: {e}")
            return False, str(e)
    
    def add_event(self, title, description, start_time, end_time, location=''):
        """Add event directly"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO events (title, description, start_time, end_time, location)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, description, start_time, end_time, location))
            
            event_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return event_id
            
        except Exception as e:
            print(f"Error adding event: {e}")
            return None

# Initialize components
db = MockDatabase()
email_processor = SecureIMAPEmailProcessor()
calendar_manager = LocalCalendar()

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
    """Create email draft (NO SENDING - DRAFT ONLY)"""
    data = request.get_json()
    to = data.get('to')
    subject = data.get('subject')
    body = data.get('body')
    cc = data.get('cc')
    bcc = data.get('bcc')
    
    if not to or not subject or not body:
        return jsonify({'error': 'To, subject, and body are required'}), 400
    
    try:
        draft_id = db.create_draft(to, subject, body, cc, bcc)
        
        if draft_id:
            return jsonify({
                'success': True,
                'draft_id': draft_id,
                'message': 'Draft saved successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save draft'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/drafts')
def api_get_drafts():
    """Get saved drafts"""
    try:
        drafts = db.get_drafts()
        return jsonify({
            'success': True,
            'drafts': drafts
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete_draft/<int:draft_id>', methods=['DELETE'])
def api_delete_draft(draft_id):
    """Delete draft (SAFE - only deletes local draft)"""
    try:
        success = db.delete_draft(draft_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Draft deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Draft not found'
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
