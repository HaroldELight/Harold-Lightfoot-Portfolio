import requests
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from core.database import db
from config.settings import Config

class AIHandler:
    """Handles AI interactions with local Qwen model via Ollama"""
    
    def __init__(self):
        self.ollama_url = Config.OLLAMA_URL
        self.model = Config.OLLAMA_MODEL
        self._ensure_ollama_ready()
    
    def _ensure_ollama_ready(self):
        """Ensure Ollama is running and model is available"""
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code != 200:
                print("Ollama is not running. Please start Ollama service.")
                return False
            
            # Check if model is available
            models = response.json().get('models', [])
            model_available = any(
                model.get('name', '').startswith(self.model.split(':')[0]) 
                for model in models
            )
            
            if not model_available:
                print(f"Model {self.model} not found in Ollama. Please pull it first.")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error checking Ollama status: {e}")
            return False
    
    def _call_ollama(self, prompt: str, stream: bool = False) -> str:
        """Make API call to Ollama"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream
        }
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            if stream:
                # Handle streaming response
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        chunk = data.get('response', '')
                        full_response += chunk
                return full_response
            else:
                # Handle non-streaming response
                data = response.json()
                return data.get('response', '')
                
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return f"Error: Unable to process request - {str(e)}"
    
    def answer_email_question(self, question: str, email_context: List[Dict] = None, 
                              session_id: str = None) -> str:
        """Answer questions about emails using AI"""
        
        # Build context from emails
        email_text = self._build_email_context(email_context) if email_context else ""
        
        # Build prompt for email Q&A
        prompt = f"""You are an email assistant helping the user understand their emails. 
Answer the user's question based on the provided email context.

User Question: {question}

Email Context:
{email_text}

Instructions:
1. Answer based only on the provided email context
2. Be concise and helpful
3. If the context doesn't contain enough information to answer, say so clearly
4. Include relevant details like dates, names, and specific information from emails
5. Format your response in a clear, readable way

Answer:"""
        
        response = self._call_ollama(prompt)
        
        # Save conversation to database
        if session_id:
            context_emails = json.dumps([email.get('id') for email in email_context]) if email_context else None
            db.add_conversation(session_id, question, response, context_emails)
        
        return response
    
    def extract_meeting_info(self, email_content: str) -> Dict[str, Any]:
        """Extract meeting information from email content"""
        
        prompt = f"""Extract meeting information from the following email content.
Look for:
- Meeting title/subject
- Date and time
- Duration or end time
- Location (physical or virtual)
- Attendees mentioned
- Meeting purpose/agenda

Email Content:
{email_content}

Return the information in JSON format with these keys:
- title (string)
- start_time (ISO datetime string or null if not found)
- end_time (ISO datetime string or null if not found)
- duration_minutes (integer or null)
- location (string or null)
- attendees (array of strings)
- description (string with meeting details)
- confidence_score (0-100, how confident you are this is a meeting)

If no meeting information is found, return null.

JSON Response:"""
        
        response = self._call_ollama(prompt)
        
        try:
            # Try to parse JSON response
            meeting_info = json.loads(response)
            
            # Validate and clean the data
            if meeting_info and isinstance(meeting_info, dict):
                return {
                    'title': meeting_info.get('title', 'Meeting'),
                    'start_time': meeting_info.get('start_time'),
                    'end_time': meeting_info.get('end_time'),
                    'duration_minutes': meeting_info.get('duration_minutes'),
                    'location': meeting_info.get('location'),
                    'attendees': meeting_info.get('attendees', []),
                    'description': meeting_info.get('description', ''),
                    'confidence_score': min(100, max(0, meeting_info.get('confidence_score', 0)))
                }
        
        except json.JSONDecodeError:
            print(f"Failed to parse AI response as JSON: {response}")
        
        return None
    
    def summarize_emails(self, emails: List[Dict], max_length: int = 500) -> str:
        """Summarize a list of emails"""
        
        if not emails:
            return "No emails to summarize."
        
        # Build email summaries
        email_summaries = []
        for email in emails:
            summary = f"From: {email.get('sender', 'Unknown')}\n"
            summary += f"Subject: {email.get('subject', 'No Subject')}\n"
            summary += f"Date: {email.get('date_received', 'Unknown')}\n"
            summary += f"Content: {email.get('snippet', email.get('body_text', ''))[:200]}...\n"
            email_summaries.append(summary)
        
        emails_text = "\n---\n".join(email_summaries)
        
        prompt = f"""Summarize the following emails in a concise way. 
Focus on the most important information, action items, and key details.

Emails:
{emails_text}

Provide a summary that:
1. Highlights the most important emails
2. Identifies any action items or deadlines
3. Groups related information together
4. Is no more than {max_length} words

Summary:"""
        
        return self._call_ollama(prompt)
    
    def suggest_email_actions(self, emails: List[Dict]) -> List[Dict]:
        """Suggest actions for emails"""
        
        actions = []
        
        for email in emails:
            prompt = f"""Analyze this email and suggest appropriate actions.

Email:
From: {email.get('sender', 'Unknown')}
Subject: {email.get('subject', 'No Subject')}
Date: {email.get('date_received', 'Unknown')}
Content: {email.get('body_text', email.get('snippet', ''))}

Suggest actions in JSON format with:
- action_type (one of: reply, archive, flag, calendar, none)
- priority (high, medium, low)
- brief_reason (why this action)
- calendar_suggestion (if action_type is 'calendar', include meeting details)

JSON Response:"""
            
            response = self._call_ollama(prompt)
            
            try:
                action_data = json.loads(response)
                if action_data and isinstance(action_data, dict):
                    actions.append({
                        'email_id': email.get('id'),
                        'gmail_id': email.get('gmail_id'),
                        'action_type': action_data.get('action_type', 'none'),
                        'priority': action_data.get('priority', 'low'),
                        'reason': action_data.get('brief_reason', ''),
                        'calendar_suggestion': action_data.get('calendar_suggestion')
                    })
            except json.JSONDecodeError:
                print(f"Failed to parse action suggestion for email {email.get('id')}")
        
        return actions
    
    def _build_email_context(self, emails: List[Dict]) -> str:
        """Build context string from email list"""
        if not emails:
            return "No email context available."
        
        context_parts = []
        for i, email in enumerate(emails, 1):
            context = f"Email {i}:\n"
            context += f"From: {email.get('sender', 'Unknown')}\n"
            context += f"Subject: {email.get('subject', 'No Subject')}\n"
            context += f"Date: {email.get('date_received', 'Unknown')}\n"
            context += f"Content: {email.get('body_text', email.get('snippet', ''))}\n"
            context_parts.append(context)
        
        return "\n---\n".join(context_parts)
    
    def generate_calendar_event_from_meeting(self, meeting_info: Dict, email_content: str) -> Dict:
        """Generate a complete calendar event from meeting information"""
        
        if not meeting_info:
            return None
        
        # If we have start_time but not end_time, calculate default duration
        if meeting_info.get('start_time') and not meeting_info.get('end_time'):
            duration = meeting_info.get('duration_minutes', 60)
            start_dt = datetime.fromisoformat(meeting_info['start_time'].replace('Z', '+00:00'))
            end_dt = start_dt + timedelta(minutes=duration)
            meeting_info['end_time'] = end_dt.isoformat()
        
        # Generate a more detailed description
        prompt = f"""Create a detailed calendar event description based on this meeting information and email content.

Meeting Info:
{json.dumps(meeting_info, indent=2)}

Original Email Content:
{email_content}

Create a comprehensive description that includes:
1. Meeting purpose and agenda
2. Key discussion points from the email
3. Any preparation needed
4. Next steps or follow-ups

Description:"""
        
        detailed_description = self._call_ollama(prompt)
        
        return {
            'title': meeting_info.get('title', 'Meeting'),
            'description': detailed_description,
            'start_time': meeting_info.get('start_time'),
            'end_time': meeting_info.get('end_time'),
            'location': meeting_info.get('location'),
            'attendees': meeting_info.get('attendees', []),
            'confidence_score': meeting_info.get('confidence_score', 0)
        }
    
    def chat_with_context(self, message: str, session_id: str = None) -> str:
        """General chat functionality with conversation history"""
        
        # Get conversation history if session_id provided
        history = []
        if session_id:
            history = db.get_conversation_history(session_id, limit=5)
        
        # Build context from history
        history_context = ""
        if history:
            history_parts = []
            for conv in history:
                history_parts.append(f"User: {conv.user_message}")
                history_parts.append(f"Assistant: {conv.ai_response}")
            history_context = "\n".join(history_parts)
        
        prompt = f"""You are an email assistant helping the user manage their emails and schedule.
Be helpful, concise, and professional.

Conversation History:
{history_context}

Current User Message: {message}

Instructions:
1. Respond helpfully to the user's message
2. If they ask about emails, suggest they ask specific questions
3. If they mention scheduling, offer to help extract meeting information
4. Keep responses conversational but professional

Response:"""
        
        response = self._call_ollama(prompt)
        
        # Save conversation to database
        if session_id:
            db.add_conversation(session_id, message, response, None)
        
        return response
