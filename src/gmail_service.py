"""
Gmail API service for reading purchase emails.
"""
import os
import base64
import email
from typing import List, Dict, Optional
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import structlog

from src.config import settings

logger = structlog.get_logger()

class GmailService:
    """Service for interacting with Gmail API."""
    
    def __init__(self):
        """Initialize Gmail API connection."""
        self.service = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with Gmail API using OAuth2."""
        creds = None
        
        # Load existing credentials
        if os.path.exists(settings.GMAIL_TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(settings.GMAIL_TOKEN_PATH, settings.GMAIL_SCOPES)
        
        # If no valid credentials, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(settings.GMAIL_CREDENTIALS_PATH):
                    raise FileNotFoundError(
                        f"Gmail credentials file not found: {settings.GMAIL_CREDENTIALS_PATH}. "
                        "Please download OAuth 2.0 credentials from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.GMAIL_CREDENTIALS_PATH, settings.GMAIL_SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(settings.GMAIL_TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Gmail service authenticated successfully")
    
    def get_purchase_emails(self, max_results: int = None) -> List[Dict]:
        """
        Retrieve purchase emails matching the search query.
        
        Args:
            max_results: Maximum number of emails to retrieve
            
        Returns:
            List of email data dictionaries
        """
        try:
            max_results = max_results or settings.GMAIL_MAX_RESULTS
            
            # Search for messages
            results = self.service.users().messages().list(
                userId='me', 
                q=settings.GMAIL_SEARCH_QUERY,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} emails matching query: {settings.GMAIL_SEARCH_QUERY}")
            
            email_data = []
            for message in messages:
                email_content = self._get_email_content(message['id'])
                if email_content:
                    email_data.append(email_content)
            
            return email_data
            
        except Exception as e:
            logger.error(f"Failed to retrieve emails: {str(e)}")
            raise
    
    def _get_email_content(self, message_id: str) -> Optional[Dict]:
        """Extract content from a specific email message."""
        try:
            message = self.service.users().messages().get(
                userId='me', id=message_id, format='full'
            ).execute()
            
            headers = message['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Extract email body
            body = self._extract_email_body(message['payload'])
            
            return {
                'id': message_id,
                'subject': subject,
                'sender': sender,
                'date': date,
                'body': body
            }
            
        except Exception as e:
            logger.error(f"Failed to extract email content for {message_id}: {str(e)}")
            return None
    
    def _extract_email_body(self, payload: dict) -> str:
        """Extract text body from email payload."""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
        elif payload['mimeType'] == 'text/plain':
            data = payload['body']['data']
            body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body
    
    def get_latest_purchase_email(self) -> Optional[Dict]:
        """
        Get the most recent purchase email.
        
        Returns:
            Email data dictionary or None if no emails found
        """
        emails = self.get_purchase_emails(max_results=1)
        return emails[0] if emails else None 