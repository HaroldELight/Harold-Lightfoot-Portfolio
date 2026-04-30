import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
from config.settings import Config

Base = declarative_base()

class Email(Base):
    """Email model for storing email metadata"""
    __tablename__ = 'emails'
    
    id = Column(Integer, primary_key=True)
    gmail_id = Column(String(255), unique=True, nullable=False)
    thread_id = Column(String(255), nullable=False)
    subject = Column(Text, nullable=False)
    sender = Column(String(255), nullable=False)
    recipients = Column(Text, nullable=True)  # JSON string of recipients
    date_received = Column(DateTime, nullable=False)
    body_text = Column(Text, nullable=True)
    body_html = Column(Text, nullable=True)
    snippet = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)
    is_starred = Column(Boolean, default=False)
    labels = Column(Text, nullable=True)  # JSON string of labels
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CalendarEvent(Base):
    """Calendar events suggested by the AI"""
    __tablename__ = 'calendar_events'
    
    id = Column(Integer, primary_key=True)
    gmail_id = Column(String(255), nullable=False)  # Link to source email
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String(255), nullable=True)
    attendees = Column(Text, nullable=True)  # JSON string of attendees
    status = Column(String(50), default='suggested')  # suggested, created, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Conversation(Base):
    """Conversation history for AI interactions"""
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), nullable=False)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    context_emails = Column(Text, nullable=True)  # JSON string of referenced email IDs
    created_at = Column(DateTime, default=datetime.utcnow)

class Database:
    """Database manager for the Email Bot"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._setup_database()
    
    def _setup_database(self):
        """Setup database connection and create tables"""
        # Ensure data directory exists
        db_path = Config.DATABASE_URL.replace('sqlite:///', '')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Create engine
        self.engine = create_engine(Config.DATABASE_URL, echo=False)
        
        # Create session factory
        self.SessionLocal = scoped_session(sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        ))
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get a database session"""
        return self.SessionLocal()
    
    def close_session(self):
        """Close all sessions"""
        self.SessionLocal.remove()
    
    def add_email(self, gmail_id, thread_id, subject, sender, recipients, 
                  date_received, body_text, body_html, snippet, is_read, 
                  is_starred, labels):
        """Add an email to the database"""
        session = self.get_session()
        try:
            # Check if email already exists
            existing = session.query(Email).filter_by(gmail_id=gmail_id).first()
            if existing:
                return existing
            
            email = Email(
                gmail_id=gmail_id,
                thread_id=thread_id,
                subject=subject,
                sender=sender,
                recipients=recipients,
                date_received=date_received,
                body_text=body_text,
                body_html=body_html,
                snippet=snippet,
                is_read=is_read,
                is_starred=is_starred,
                labels=labels
            )
            
            session.add(email)
            session.commit()
            return email
        except Exception as e:
            session.rollback()
            print(f"Error adding email: {e}")
            return None
        finally:
            session.close()
    
    def get_emails(self, limit=50, offset=0, search_query=None):
        """Get emails from database"""
        session = self.get_session()
        try:
            query = session.query(Email).order_by(Email.date_received.desc())
            
            if search_query:
                # Use parameterized queries to prevent SQL injection
                search_pattern = f"%{search_query}%"
                query = query.filter(
                    Email.subject.ilike(search_pattern) |
                    Email.body_text.ilike(search_pattern) |
                    Email.sender.ilike(search_pattern)
                )
            
            emails = query.offset(offset).limit(limit).all()
            return emails
        except Exception as e:
            print(f"Error getting emails: {e}")
            return []
        finally:
            session.close()
    
    def get_email_by_id(self, email_id):
        """Get a specific email by ID"""
        session = self.get_session()
        try:
            email = session.query(Email).filter_by(id=email_id).first()
            return email
        except Exception as e:
            print(f"Error getting email: {e}")
            return None
        finally:
            session.close()
    
    def get_email_by_gmail_id(self, gmail_id):
        """Get a specific email by Gmail ID"""
        session = self.get_session()
        try:
            email = session.query(Email).filter_by(gmail_id=gmail_id).first()
            return email
        except Exception as e:
            print(f"Error getting email: {e}")
            return None
        finally:
            session.close()
    
    def add_calendar_event(self, gmail_id, title, description, start_time, 
                          end_time, location, attendees):
        """Add a calendar event suggestion"""
        session = self.get_session()
        try:
            event = CalendarEvent(
                gmail_id=gmail_id,
                title=title,
                description=description,
                start_time=start_time,
                end_time=end_time,
                location=location,
                attendees=attendees
            )
            
            session.add(event)
            session.commit()
            return event
        except Exception as e:
            session.rollback()
            print(f"Error adding calendar event: {e}")
            return None
        finally:
            session.close()
    
    def get_calendar_events(self, status='suggested'):
        """Get calendar events by status"""
        session = self.get_session()
        try:
            events = session.query(CalendarEvent).filter_by(status=status).all()
            return events
        except Exception as e:
            print(f"Error getting calendar events: {e}")
            return []
        finally:
            session.close()
    
    def update_calendar_event_status(self, event_id, status):
        """Update calendar event status"""
        session = self.get_session()
        try:
            event = session.query(CalendarEvent).filter_by(id=event_id).first()
            if event:
                event.status = status
                event.updated_at = datetime.utcnow()
                session.commit()
                return event
            return None
        except Exception as e:
            session.rollback()
            print(f"Error updating calendar event: {e}")
            return None
        finally:
            session.close()
    
    def add_conversation(self, session_id, user_message, ai_response, context_emails):
        """Add a conversation entry"""
        session = self.get_session()
        try:
            conversation = Conversation(
                session_id=session_id,
                user_message=user_message,
                ai_response=ai_response,
                context_emails=context_emails
            )
            
            session.add(conversation)
            session.commit()
            return conversation
        except Exception as e:
            session.rollback()
            print(f"Error adding conversation: {e}")
            return None
        finally:
            session.close()
    
    def get_conversation_history(self, session_id, limit=10):
        """Get conversation history for a session"""
        session = self.get_session()
        try:
            conversations = session.query(Conversation).filter_by(
                session_id=session_id
            ).order_by(Conversation.created_at.desc()).limit(limit).all()
            
            return list(reversed(conversations))  # Return in chronological order
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []
        finally:
            session.close()

# Global database instance
db = Database()
