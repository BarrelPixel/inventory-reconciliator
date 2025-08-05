# Inventory Reconciliation MVP

A simple Python script that reads purchase emails from Gmail and updates inventory levels in Google Sheets.

## Overview

This MVP demonstrates the core functionality of automated inventory reconciliation:
1. **Read emails** from Gmail using the Gmail API
2. **Parse purchase data** from email content
3. **Update inventory** in Google Sheets using the Sheets API

## Project Structure

```
inventory-reconciliator/
├── requirements.txt          # Python dependencies
├── run.py                   # Main script
├── .env                     # Configuration (create this)
├── credentials_sheets.json  # Google Sheets API credentials (you provide)
├── credentials_gmail.json   # Gmail API credentials (you provide)
├── token_gmail.json         # Gmail OAuth token (auto-generated)
└── src/
    ├── __init__.py
    ├── config.py            # Configuration management
    ├── gmail_service.py     # Gmail API integration
    ├── sheets_service.py    # Google Sheets API integration
    └── parser_service.py    # Email content parsing
```

## Prerequisites

- Python 3.8 or higher
- Google Cloud Project with Gmail and Sheets APIs enabled
- Google Sheets document with inventory data
- Gmail account with purchase emails

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Google Cloud Setup

1. **Create a Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the **Gmail API** and **Google Sheets API**

2. **Create Service Account for Sheets:**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "Service Account"
   - Name it (e.g., "inventory-sheets")
   - Download the JSON key file
   - **Rename to `credentials_sheets.json`** and place in project root

3. **Create OAuth 2.0 Client for Gmail:**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the JSON file
   - **Rename to `credentials_gmail.json`** and place in project root

### 3. Google Sheets Setup

1. **Create/Prepare Your Sheet:**
   - Create a new Google Sheet or use existing one
   - Get the **Sheet ID** from the URL: `https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit`
   - Create a worksheet named "Inventory" (or customize in `.env`)
   - Set up columns (example):
     ```
     SKU         | Stock | Item Name
     ITEM-001    | 50    | Widget A
     ITEM-002    | 25    | Widget B
     ```

2. **Share the Sheet:**
   - Click "Share" button
   - Add the service account email (from `credentials_sheets.json`)
   - Give it "Editor" permissions

### 4. Configuration

Create a `.env` file in the project root:

```env
# Google Sheets Configuration
GOOGLE_SHEET_ID="your_sheet_id_here"
INVENTORY_WORKSHEET_NAME="Inventory"

# Gmail Configuration
GMAIL_SEARCH_QUERY="subject:Weekly Purchase Report"
GMAIL_MAX_RESULTS=5

# Optional: Custom credential paths
SHEETS_CREDENTIALS_PATH="credentials_sheets.json"
GMAIL_CREDENTIALS_PATH="credentials_gmail.json"
GMAIL_TOKEN_PATH="token_gmail.json"
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Test your setup:**
   ```bash
   python test_setup.py
   ```

3. **Set up Google Cloud credentials** (see Setup Instructions below)

4. **Create your `.env` file:**
   ```bash
   cp env.example .env
   # Edit .env with your actual values
   ```

5. **Run the reconciliation:**
   ```bash
   python run.py
   ```

## Usage

### Basic Usage

```bash
python run.py
```

The script will:
1. Search for emails matching your `GMAIL_SEARCH_QUERY`
2. Parse the most recent email for purchase data
3. Update inventory levels in your Google Sheet
4. Display a summary of the results

### Expected Email Format

The parser currently supports these formats:

1. **Simple SKU/Quantity:**
   ```
   SKU: ITEM-001, Quantity: 10
   SKU: ITEM-002, Quantity: 5
   ```

2. **Item with SKU:**
   ```
   Item: Widget A | SKU: ITEM-001 | Qty: 10
   Item: Widget B | SKU: ITEM-002 | Qty: 5
   ```

3. **Product with SKU:**
   ```
   Widget A (SKU: ITEM-001) - Quantity: 10
   Widget B (SKU: ITEM-002) - Quantity: 5
   ```

## Customization

### Email Parsing

To customize email parsing for your specific format, modify `src/parser_service.py`:

```python
def _parse_content(self, content: str) -> List[Dict[str, Any]]:
    # Add your custom parsing logic here
    # Look for patterns specific to your email format
    pass
```

### Sheet Structure

If your sheet has a different structure, update the column assumptions in `run.py`:

```python
# Find the item in our inventory
inventory_row = inventory_df[inventory_df.iloc[:, 0] == sku]  # SKU column
current_stock = inventory_row.iloc[0, 1]  # Stock column
```

## Troubleshooting

### Common Issues

1. **"Credentials file not found"**
   - Ensure `credentials_sheets.json` and `credentials_gmail.json` are in the project root
   - Check file names match exactly

2. **"Sheet not found"**
   - Verify `GOOGLE_SHEET_ID` in `.env` is correct
   - Ensure the service account has access to the sheet

3. **"No emails found"**
   - Check `GMAIL_SEARCH_QUERY` in `.env`
   - Verify you have emails matching the search criteria

4. **"No items parsed"**
   - Email format may not match parsing patterns
   - Check the email content manually
   - Customize parser in `src/parser_service.py`

5. **"SKU not found in inventory"**
   - Verify SKUs in emails match SKUs in your sheet
   - Check sheet structure and column positions

### Debug Mode

Set `LOG_LEVEL=DEBUG` in your `.env` file for detailed logging:

```env
LOG_LEVEL=DEBUG
```

## Next Steps

This MVP provides the foundation. Future enhancements could include:

- Web interface for configuration
- Support for multiple email formats
- Database storage for audit trails
- Automated scheduling
- Error handling and retry logic
- Email notifications for failures

## Security Notes

- Keep credential files secure and never commit them to version control
- Use environment variables for sensitive configuration
- Consider using Google Secret Manager for production deployments
- Regularly rotate API keys and tokens 