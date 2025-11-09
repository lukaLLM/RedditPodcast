"""
Email fetcher for retrieving AI newsletters and updates.
"""
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
from bs4 import BeautifulSoup
import re
import html

class EmailFetcher:
    """Fetch emails from specified senders via IMAP."""
    
    def __init__(
        self,
        email_address: str,
        password: str,
        imap_server: str = "imap.gmail.com",
        imap_port: int = 993
    ):
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.imap_port = imap_port
    
    def fetch_emails(
        self,
        allowed_senders: List[str],
        hours_back: int = 24,
        max_emails: int = 20
    ) -> List[Dict[str, str]]:
        """
        Fetch emails from allowed senders within specified time period.
        
        Args:
            allowed_senders: List of email addresses to fetch from
            hours_back: How many hours back to search
            max_emails: Maximum number of emails to fetch per sender
        
        Returns:
            List of dicts with email data: {subject, sender, date, body}
        """
        emails_data = []
        
        if not self.email_address or not self.password:
            print("❌ Email credentials not configured")
            return []
        
        try:
            print(f"📧 Connecting to {self.imap_server}...")
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            
            print(f"🔐 Logging in as {self.email_address}...")
            mail.login(self.email_address, self.password)
            
            print("📬 Selecting inbox...")
            mail.select("inbox")
            
            since_date = (datetime.now() - timedelta(hours=hours_back)).strftime("%d-%b-%Y")
            
            for sender in allowed_senders:
                print(f"🔍 Searching emails from {sender}...")
                search_criteria = f'(FROM "{sender}" SINCE {since_date})'
                status, messages = mail.search(None, search_criteria)
                
                if status != "OK":
                    continue
                
                email_ids = messages[0].split()
                print(f"   Found {len(email_ids)} emails")
                
                # Fetch most recent emails
                for email_id in email_ids[-max_emails:]:
                    try:
                        status, msg_data = mail.fetch(email_id, "(RFC822)")
                        
                        if status != "OK":
                            continue
                        
                        for response_part in msg_data:
                            if isinstance(response_part, tuple):
                                msg = email.message_from_bytes(response_part[1])
                                
                                subject = self._decode_subject(msg["Subject"])
                                from_header = msg.get("From", "")
                                date_header = msg.get("Date", "")
                                body = self._get_email_body(msg)
                                
                                emails_data.append({
                                    "subject": subject,
                                    "sender": from_header,
                                    "date": date_header,
                                    "body": body
                                })
                    
                    except Exception as e:
                        print(f"⚠️ Error fetching email {email_id}: {e}")
                        continue
            
            mail.close()
            mail.logout()
            
            print(f"✅ Fetched {len(emails_data)} emails total")
            return emails_data
        
        except Exception as e:
            print(f"❌ Email fetch error: {e}")
            return []
    
    def _decode_subject(self, subject: str) -> str:
        """Decode email subject with proper encoding handling."""
        if not subject:
            return "No Subject"
        
        decoded_parts = decode_header(subject)
        subject_parts = []
        
        for content, encoding in decoded_parts:
            if isinstance(content, bytes):
                try:
                    # Try specified encoding first
                    if encoding:
                        subject_parts.append(content.decode(encoding))
                    else:
                        # Try UTF-8, then Latin-1 as fallback
                        try:
                            subject_parts.append(content.decode("utf-8"))
                        except:
                            subject_parts.append(content.decode("latin-1"))
                except:
                    subject_parts.append(content.decode("utf-8", errors="replace"))
            else:
                subject_parts.append(str(content))
        
        return "".join(subject_parts)
    
    def _get_email_body(self, msg) -> str:
        """Extract email body with improved encoding and cleaning."""
        plain_body = ""
        html_body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if "attachment" in content_disposition:
                    continue
                
                try:
                    payload = part.get_payload(decode=True)
                    if not payload:
                        continue
                    
                    # Better encoding detection
                    charset = part.get_content_charset()
                    if not charset:
                        # Try to detect encoding
                        charset = 'utf-8'
                    
                    try:
                        decoded_payload = payload.decode(charset)
                    except (UnicodeDecodeError, LookupError):
                        # Fallback to utf-8 with replace
                        try:
                            decoded_payload = payload.decode('utf-8', errors='replace')
                        except:
                            decoded_payload = payload.decode('latin-1', errors='replace')
                    
                    if content_type == "text/plain":
                        plain_body = decoded_payload
                    elif content_type == "text/html":
                        html_body = decoded_payload
            
                except Exception as e:
                    print(f"⚠️ Error decoding email part: {e}")
                    continue
        else:
            try:
                payload = msg.get_payload(decode=True)
                charset = msg.get_content_charset() or 'utf-8'
                
                try:
                    content = payload.decode(charset)
                except (UnicodeDecodeError, LookupError):
                    content = payload.decode('utf-8', errors='replace')
                
                if msg.get_content_type() == "text/html":
                    html_body = content
                else:
                    plain_body = content
            except Exception as e:
                print(f"⚠️ Error decoding email body: {e}")
        
        # Prefer plain text, fallback to HTML
        if plain_body:
            print("✅ Using plain text body")
            return self._clean_text(plain_body)
        elif html_body:
            print("⚠️ Converting HTML to text")
            return self._html_to_text(html_body)
        else:
            return "Could not extract email content"
    
    def _clean_text(self, text: str) -> str:
        """
        Clean text content by removing URLs, navigation, and fixing encoding.
        """
        # Fix common HTML entities that weren't decoded properly
        text = html.unescape(text)
        
        # Remove URL patterns - both standalone and inline
        # Remove (https://...) patterns
        text = re.sub(r'\s*\(https?://[^\s\)]+\)', '', text)
        # Remove standalone URLs
        text = re.sub(r'https?://[^\s]+', '', text)
        
        # Remove common newsletter navigation patterns
        navigation_patterns = [
            r'View in browser.*?\n',
            r'Subscribe.*?\n',
            r'Unsubscribe.*?\n',
            r'Submit a tip.*?\n',
            r'Manage preferences.*?\n',
            r'Click here.*?\n',
            r'\[.*?\]',  # Remove [brackets] which often contain links
        ]
        
        for pattern in navigation_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Split into lines and clean
        lines = []
        prev_empty = False
        
        for line in text.splitlines():
            line = line.strip()
            
            # Skip empty lines (but keep single spacing)
            if not line:
                if not prev_empty and lines:  # Don't add at start
                    lines.append('')
                    prev_empty = True
                continue
            
            prev_empty = False
            
            # Skip very short lines that look like navigation
            if len(line) < 20:
                skip_keywords = ['view', 'browser', 'subscribe', 'unsubscribe', 
                               'click', 'here', 'manage', 'preferences', 'tip']
                if any(keyword in line.lower() for keyword in skip_keywords):
                    continue
            
            # Skip lines that are just punctuation/symbols
            if re.match(r'^[\(\)\[\]\{\}\-\=\+\*\s]+$', line):
                continue
            
            lines.append(line)
        
        # Join and final cleanup
        result = '\n'.join(lines)
        
        # Remove excessive whitespace
        result = re.sub(r'\n{3,}', '\n\n', result)  # Max 2 consecutive newlines
        result = re.sub(r' {2,}', ' ', result)  # Max 1 space
        result = re.sub(r'\t+', ' ', result)  # Tabs to spaces
        
        return result.strip()

    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML to clean plain text."""
        try:
            # Fix HTML entities first
            html_content = html.unescape(html_content)
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove non-content elements
            for element in soup(["script", "style", "head", "meta", "link", 
                               "img", "svg", "noscript", "iframe"]):
                element.decompose()
            
            # Remove all anchor tags but keep meaningful text
            for link in soup.find_all('a'):
                link_text = link.get_text().strip()
                # Keep text if it's meaningful (not a URL)
                if link_text and not link_text.startswith(('http', 'www')) and len(link_text) > 3:
                    link.replace_with(link_text + ' ')
                else:
                    link.decompose()
            
            # Remove common newsletter footer/header divs
            for div in soup.find_all(['div', 'table', 'td']):
                div_text = div.get_text().strip().lower()
                if any(word in div_text for word in ['unsubscribe', 'view in browser', 
                                                     'manage preferences', 'submit a tip']):
                    if len(div_text) < 100:  # Only remove short navigation elements
                        div.decompose()
            
            # Extract text
            text = soup.get_text(separator='\n')
            
            # Use the same cleaning as plain text
            return self._clean_text(text)
        
        except Exception as e:
            print(f"⚠️ Error converting HTML to text: {e}")
            # Fallback: strip tags and clean
            text = re.sub('<[^<]+?>', '', html_content)
            return self._clean_text(text)

    def format_emails_for_analysis(
        self, 
        emails: List[Dict[str, str]], 
        max_length_per_email: Optional[int] = None,
        include_metadata: bool = True
    ) -> str:
        """Format emails into readable text for AI analysis."""
        if not emails:
            return "No emails found."
        
        formatted = f"# AI NEWS EMAILS ({len(emails)} total)\n\n"
        
        for i, email_data in enumerate(emails, 1):
            if include_metadata:
                formatted += f"## EMAIL {i}\n"
                formatted += f"Subject: {email_data['subject']}\n"
                formatted += f"From: {email_data['sender']}\n"
                formatted += f"Date: {email_data['date']}\n\n"
            
            body = email_data['body']
            original_length = len(body)
            
            if max_length_per_email and len(body) > max_length_per_email:
                body = body[:max_length_per_email]
                last_period = body.rfind('.')
                if last_period > max_length_per_email * 0.8:
                    body = body[:last_period + 1]
                body += f"\n\n[Truncated: {original_length:,} → {len(body):,} chars]"
            
            formatted += f"{body}\n\n"
            if i < len(emails):
                formatted += "---\n\n"
        
        return formatted