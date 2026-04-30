import json
from datetime import datetime, timedelta
from core.database import db
from ai.ai_handler import AIHandler

class LocalCalendar:
    """Simple local calendar system (free alternative to Google Calendar)"""
    
    def __init__(self):
        self.ai_handler = AIHandler()
    
    def create_event(self, title, description, start_time, end_time, location=None, attendees=None):
        """Create a local calendar event"""
        try:
            # Validate inputs
            if not title or not start_time:
                return False, "Title and start time are required"
            
            # Convert string times to datetime objects
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            # Store event in database
            event_data = {
                'title': title,
                'description': description or '',
                'start_time': start_time,
                'end_time': end_time,
                'location': location,
                'attendees': json.dumps(attendees or []),
                'created_at': datetime.now()
            }
            
            # Store in database (using calendar_events table)
            event = db.add_calendar_event(
                gmail_id="local_event",  # Local events don't come from emails
                title=title,
                description=description or '',
                start_time=start_time,
                end_time=end_time,
                location=location,
                attendees=json.dumps(attendees or [])
            )
            
            return True, event
            
        except Exception as e:
            error_msg = f"Error creating calendar event: {e}"
            print(error_msg)
            return False, error_msg
    
    def get_events(self, days_ahead=7):
        """Get upcoming events"""
        try:
            # Calculate date range
            now = datetime.now()
            end_time = now + timedelta(days=days_ahead)
            
            # Get events from database
            events = db.get_calendar_events(status='created')
            
            # Filter for upcoming events
            upcoming_events = []
            for event in events:
                if event.start_time and event.start_time >= now and event.start_time <= end_time:
                    upcoming_events.append(event)
            
            # Sort by start time
            upcoming_events.sort(key=lambda x: x.start_time)
            
            return upcoming_events
            
        except Exception as e:
            print(f"Error getting events: {e}")
            return []
    
    def suggest_event_from_email(self, email):
        """Suggest calendar event from email content using AI"""
        if not email:
            return None
        
        try:
            # Extract meeting information using AI
            meeting_info = self.ai_handler.extract_meeting_info(email.get('body_text', ''))
            
            if not meeting_info or meeting_info.get('confidence_score', 0) < 50:
                return None
            
            # Generate complete event details
            event_data = self.ai_handler.generate_calendar_event_from_meeting(
                meeting_info, 
                email.get('body_text', '')
            )
            
            if not event_data:
                return None
            
            # Check for conflicts with existing events
            conflicts = []
            if event_data.get('start_time') and event_data.get('end_time'):
                conflicts = self.check_conflicts(
                    event_data['start_time'], 
                    event_data['end_time']
                )
            
            # Store suggestion in database
            suggestion = db.add_calendar_event(
                gmail_id=email.get('gmail_id', 'unknown'),
                title=event_data.get('title', 'Meeting'),
                description=event_data.get('description', ''),
                start_time=datetime.fromisoformat(event_data['start_time'].replace('Z', '+00:00')) if event_data.get('start_time') else None,
                end_time=datetime.fromisoformat(event_data['end_time'].replace('Z', '+00:00')) if event_data.get('end_time') else None,
                location=event_data.get('location'),
                attendees=json.dumps(event_data.get('attendees', []))
            )
            
            return {
                'suggestion_id': suggestion.id if suggestion else None,
                'event_data': event_data,
                'conflicts': conflicts,
                'confidence_score': meeting_info.get('confidence_score', 0),
                'source_email': {
                    'id': email.get('id'),
                    'gmail_id': email.get('gmail_id'),
                    'subject': email.get('subject'),
                    'sender': email.get('sender')
                }
            }
            
        except Exception as e:
            print(f"Error suggesting event from email: {e}")
            return None
    
    def check_conflicts(self, start_time, end_time):
        """Check for scheduling conflicts"""
        try:
            # Convert string times to datetime objects
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            # Get existing events
            existing_events = db.get_calendar_events(status='created')
            
            # Check for conflicts
            conflicting_events = []
            for event in existing_events:
                if event.start_time and event.end_time:
                    # Check if events overlap
                    if (event.start_time < end_time and event.end_time > start_time):
                        conflicting_events.append({
                            'title': event.title,
                            'start_time': event.start_time,
                            'end_time': event.end_time
                        })
            
            return conflicting_events
            
        except Exception as e:
            print(f"Error checking conflicts: {e}")
            return []
    
    def create_suggested_event(self, suggestion_id):
        """Create a calendar event from a suggestion"""
        if not suggestion_id:
            return False, "Invalid suggestion ID"
        
        try:
            # Get suggestion from database
            session = db.get_session()
            try:
                from core.database import CalendarEvent
                suggestion = session.query(CalendarEvent).filter_by(
                    id=suggestion_id, 
                    status='suggested'
                ).first()
                
                if not suggestion:
                    return False, "Suggestion not found or already processed"
                
                # Update suggestion status to created
                suggestion.status = 'created'
                suggestion.updated_at = datetime.utcnow()
                session.commit()
                
                return True, {
                    'message': 'Event created successfully',
                    'event': {
                        'id': suggestion.id,
                        'title': suggestion.title,
                        'start_time': suggestion.start_time,
                        'end_time': suggestion.end_time,
                        'location': suggestion.location
                    }
                }
                
            finally:
                session.close()
                
        except Exception as e:
            error_msg = f"Error creating suggested event: {e}"
            print(error_msg)
            return False, error_msg
    
    def reject_suggestion(self, suggestion_id):
        """Reject a calendar event suggestion"""
        if not suggestion_id:
            return False, "Invalid suggestion ID"
        
        try:
            session = db.get_session()
            try:
                from core.database import CalendarEvent
                suggestion = session.query(CalendarEvent).filter_by(
                    id=suggestion_id,
                    status='suggested'
                ).first()
                
                if not suggestion:
                    return False, "Suggestion not found or already processed"
                
                # Update suggestion status
                suggestion.status = 'rejected'
                suggestion.updated_at = datetime.utcnow()
                session.commit()
                
                return True, "Suggestion rejected"
                
            finally:
                session.close()
                
        except Exception as e:
            error_msg = f"Error rejecting suggestion: {e}"
            print(error_msg)
            return False, error_msg
    
    def get_suggested_events(self):
        """Get all pending event suggestions"""
        return db.get_calendar_events(status='suggested')
    
    def update_event(self, event_id, **kwargs):
        """Update an existing calendar event"""
        try:
            session = db.get_session()
            try:
                from core.database import CalendarEvent
                event = session.query(CalendarEvent).filter_by(id=event_id).first()
                
                if not event:
                    return False, "Event not found"
                
                # Update fields
                if 'title' in kwargs:
                    event.title = kwargs['title']
                if 'description' in kwargs:
                    event.description = kwargs['description']
                if 'start_time' in kwargs:
                    event.start_time = kwargs['start_time']
                if 'end_time' in kwargs:
                    event.end_time = kwargs['end_time']
                if 'location' in kwargs:
                    event.location = kwargs['location']
                if 'attendees' in kwargs:
                    event.attendees = json.dumps(kwargs['attendees'])
                
                event.updated_at = datetime.utcnow()
                session.commit()
                
                return True, event
                
            finally:
                session.close()
                
        except Exception as e:
            error_msg = f"Error updating calendar event: {e}"
            print(error_msg)
            return False, error_msg
    
    def delete_event(self, event_id):
        """Delete a calendar event"""
        try:
            session = db.get_session()
            try:
                from core.database import CalendarEvent
                event = session.query(CalendarEvent).filter_by(id=event_id).first()
                
                if not event:
                    return False, "Event not found"
                
                session.delete(event)
                session.commit()
                
                return True, "Event deleted successfully"
                
            finally:
                session.close()
                
        except Exception as e:
            error_msg = f"Error deleting calendar event: {e}"
            print(error_msg)
            return False, error_msg
    
    def get_events_for_date(self, date):
        """Get events for a specific date"""
        try:
            if isinstance(date, str):
                date = datetime.fromisoformat(date).date()
            
            # Get all events
            events = db.get_calendar_events(status='created')
            
            # Filter for the specific date
            date_events = []
            for event in events:
                if event.start_time and event.start_time.date() == date:
                    date_events.append(event)
            
            # Sort by start time
            date_events.sort(key=lambda x: x.start_time)
            
            return date_events
            
        except Exception as e:
            print(f"Error getting events for date: {e}")
            return []
