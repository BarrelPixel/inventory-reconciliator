"""
Configuration management for the inventory reconciliation MVP.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings with environment variable support."""
    
    # Google Sheets Configuration
    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
    INVENTORY_WORKSHEET_NAME = os.getenv("INVENTORY_WORKSHEET_NAME", "Inventory")
    
    # Credential file paths (OAuth 2.0 for both Gmail and Sheets)
    GMAIL_CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials_gmail.json")
    GMAIL_TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH", "token_gmail.json")
    SHEETS_TOKEN_PATH = os.getenv("SHEETS_TOKEN_PATH", "token_sheets.json")
    
    # Gmail search configuration
    GMAIL_SEARCH_QUERY = os.getenv("GMAIL_SEARCH_QUERY", "subject:Weekly Purchase Report")
    GMAIL_MAX_RESULTS = int(os.getenv("GMAIL_MAX_RESULTS", "5"))
    
    # Google API Scopes
    SHEETS_SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file"
    ]
    GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

settings = Settings() 