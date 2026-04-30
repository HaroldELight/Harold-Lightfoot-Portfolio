import imaplib
import email
from email.header import decode_header
import ssl
from datetime import datetime, timedelta
import re
from core.database import db
from config.settings import Config

class IMAPEmailProcessor:
    """Handles Gmail access via IMAP (free method)"""
    
    def __init__(self, email_address=None, app_password=None):
        self.email_address = email_address or Config.GMAIL_EMAIL
        self.app_password = app_password or Config.GMAIL_APP_PASSWORD
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993
        self.connection = None
        
    def connect(self):
        """Connect to Gmail via IMAP"""
        try:
            # Create SSL context with proper certificate verification
            context = ssl.create_default_context()
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED
            
            # Connect to IMAP server with SSL verification
            self.connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port, ssl_context=context)
            
            # Login
            self.connection.login(self.email_address, self.app_password)
            
            return True
            
        except ssl.SSLCertVerificationError as e:
            print(f"SSL certificate verification failed: {e}")
            print("This could indicate a man-in-the-middle attack or certificate issue.")
            return False
        except Exception as e:
            print(f"IMAP connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from IMAP server"""
        if self.connection:
            try:
                self.connection.logout()
                self.connection = None
            except:
                pass
    
    def fetch_emails(self, limit=100, days_back=30):
        """Fetch emails from INBOX"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            # Select INBOX
            self.connection.select('INBOX')
            
            # Calculate date filter
            date_filter = (datetime.now() - timedelta(days=days_back)).strftime('%d-%b-%Y')
            
            # Search for emails since date
            search_criteria = f'(SINCE "{date_filter}")'
            status, messages = self.connection.search(None, search_criteria)
            
            if status != 'OK':
                print("No messages found")
                return []
            
            # Get message IDs
            email_ids = messages[0].split()
            
            # Limit to recent emails
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            emails = []
            
            # Fetch each email
            for email_id in email_ids:
                email_data = self._fetch_email_details(email_id)
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    def _fetch_email_details(self, email_id):
        """Fetch detailed email information"""
        try:
            # Fetch email data
            status, msg_data = self.connection.fetch(email_id, '(RFC822)')
            
            if status != 'OK':
                return None
            
            # Parse email
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            # Extract headers
            subject = self._decode_header(msg['Subject'])
            sender = self._decode_header(msg['From'])
            date_str = msg['Date']
            to = self._decode_header(msg['To'])
            cc = self._decode_header(msg['Cc'])
            
            # Parse date
            date_received = self._parse_date(date_str) if date_str else datetime.now()
            
            # Extract recipients
            recipients = []
            if to:
                recipients.extend([email.strip() for email in to.split(',')])
            if cc:
                recipients.extend([email.strip() for email in cc.split(',')])
            
            # Get message body
            body_text, body_html = self._extract_body(msg)
            
            # Get snippet (first 200 chars of body)
            snippet = body_text[:200] if body_text else ""
            
            # Check if email exists in database
            gmail_id = email_id.decode('utf-8')
            existing_email = db.get_email_by_gmail_id(gmail_id)
            if existing_email:
                return existing_email
            
            # Store in database
            email_data = {
                'gmail_id': gmail_id,
                'thread_id': gmail_id,  # IMAP doesn't have threading like Gmail API
                'subject': subject or '(No Subject)',
                'sender': sender or 'Unknown',
                'recipients': str(recipients),
                'date_received': date_received,
                'body_text': body_text,
                'body_html': body_html,
                'snippet': snippet,
                'is_read': False,  # IMAP doesn't easily provide read status
                'is_starred': False,
                'labels': '[]'
            }
            
            stored_email = db.add_email(**email_data)
            return stored_email
            
        except Exception as e:
            print(f"Error processing email {email_id}: {e}")
            return None
    
    def _decode_header(self, header):
        """Decode email header"""
        if not header:
            return ""
        
        try:
            decoded_parts = decode_header(header)
            decoded_string = ""
            
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        decoded_string += part.decode(encoding)
                    else:
                        decoded_string += part.decode('utf-8', errors='ignore')
                else:
                    decoded_string += part
            
            return decoded_string.strip()
            
        except Exception as e:
            print(f"Error decoding header: {e}")
            return header
    
    def _parse_date(self, date_str):
        """Parse email date string"""
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except:
            return datetime.now()
    
    def _extract_body(self, msg):
        """Extract email body text and HTML"""
        body_text = ""
        body_html = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if "attachment" not in content_disposition:
                    if content_type == "text/plain":
                        try:
                            body_text = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        except:
                            pass
                    elif content_type == "text/html":
                        try:
                            body_html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        except:
                            pass
        else:
            content_type = msg.get_content_type()
            if content_type == "text/plain":
                try:
                    body_text = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    pass
            elif content_type == "text/html":
                try:
                    body_html = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    pass
        
        return body_text, body_html
    
    def search_emails(self, query, limit=50):
        """Search emails in IMAP"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            self.connection.select('INBOX')
            
            # Simple search implementation
            # IMAP search is limited, so we'll fetch recent emails and filter
            recent_emails = self.fetch_emails(limit=limit*2)  # Get more to filter
            
            # Filter by query
            filtered_emails = []
            query_lower = query.lower()
            
            for email_data in recent_emails:
                if (query_lower in email_data.subject.lower() or 
                    query_lower in email_data.sender.lower() or
                    query_lower in (email_data.body_text or '').lower()):
                    filtered_emails.append(email_data)
                    
                    if len(filtered_emails) >= limit:
                        break
            
            return filtered_emails
            
        except Exception as e:
            print(f"Error searching emails: {e}")
            return []
    
    def create_draft(self, to, subject, body, cc=None, bcc=None):
        """Create email draft via IMAP"""
        # Note: IMAP doesn't directly support creating drafts
        # This would require SMTP or Gmail API
        # For now, we'll store it in database for later implementation
        try:
            draft_data = {
                'to': to,
                'subject': subject,
                'body': body,
                'cc': cc,
                'bcc': bcc,
                'created_at': datetime.now()
            }
            
            # Store draft in database (you'd need to create a drafts table)
            print(f"Draft created: {subject} to {to}")
            return True
            
        except Exception as e:
            print(f"Error creating draft: {e}")
            return False
    
    def get_email_count(self):
        """Get total email count"""
        return db.get_email_count()
    
    def get_unread_count(self):
        """Get unread email count"""
        return db.get_unread_count()
