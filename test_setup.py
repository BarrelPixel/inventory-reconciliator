#!/usr/bin/env python3
"""
Simple test script to verify the basic setup.
"""
import sys
import os

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import structlog
        print("✅ structlog imported successfully")
    except ImportError as e:
        print(f"❌ structlog import failed: {e}")
        return False
    
    try:
        from src.config import settings
        print("✅ src.config imported successfully")
    except ImportError as e:
        print(f"❌ src.config import failed: {e}")
        return False
    
    try:
        from src.gmail_service import GmailService
        print("✅ GmailService imported successfully")
    except ImportError as e:
        print(f"❌ GmailService import failed: {e}")
        return False
    
    try:
        from src.sheets_service import SheetsService
        print("✅ SheetsService imported successfully")
    except ImportError as e:
        print(f"❌ SheetsService import failed: {e}")
        return False
    
    try:
        from src.parser_service import ParserService
        print("✅ ParserService imported successfully")
    except ImportError as e:
        print(f"❌ ParserService import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from src.config import settings
        print(f"✅ Configuration loaded")
        print(f"   - Gmail search query: {settings.GMAIL_SEARCH_QUERY}")
        print(f"   - Max results: {settings.GMAIL_MAX_RESULTS}")
        print(f"   - Worksheet name: {settings.INVENTORY_WORKSHEET_NAME}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_credential_files():
    """Test if credential files exist."""
    print("\nTesting credential files...")
    
    from src.config import settings
    
    # Check if credential files exist
    sheets_creds = os.path.exists(settings.SHEETS_CREDENTIALS_PATH)
    gmail_creds = os.path.exists(settings.GMAIL_CREDENTIALS_PATH)
    
    print(f"   - Sheets credentials: {'✅ Found' if sheets_creds else '❌ Missing'}")
    print(f"   - Gmail credentials: {'✅ Found' if gmail_creds else '❌ Missing'}")
    
    if not sheets_creds:
        print(f"   📝 Download service account credentials and save as: {settings.SHEETS_CREDENTIALS_PATH}")
    
    if not gmail_creds:
        print(f"   📝 Download OAuth 2.0 credentials and save as: {settings.GMAIL_CREDENTIALS_PATH}")
    
    return sheets_creds and gmail_creds

def main():
    """Run all tests."""
    print("🧪 Inventory Reconciliation MVP - Setup Test")
    print("=" * 50)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test configuration
    if not test_config():
        all_passed = False
    
    # Test credential files
    if not test_credential_files():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All basic tests passed! You're ready to configure credentials.")
    else:
        print("⚠️  Some tests failed. Please address the issues above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 