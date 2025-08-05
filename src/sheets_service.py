"""
Google Sheets service for inventory management.
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import structlog
from typing import List, Dict, Any, Optional
import os

from src.config import settings

logger = structlog.get_logger()

class SheetsService:
    """Service for interacting with Google Sheets API."""
    
    def __init__(self):
        """Initialize Google Sheets connection."""
        self.client = None
        self.sheet = None
        self.worksheet = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with Google Sheets API using service account."""
        try:
            if not os.path.exists(settings.SHEETS_CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"Sheets credentials file not found: {settings.SHEETS_CREDENTIALS_PATH}. "
                    "Please download service account credentials from Google Cloud Console."
                )
            
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                settings.SHEETS_CREDENTIALS_PATH, settings.SHEETS_SCOPES
            )
            self.client = gspread.authorize(creds)
            
            if not settings.GOOGLE_SHEET_ID:
                raise ValueError(
                    "GOOGLE_SHEET_ID not configured. Please set it in your .env file."
                )
            
            self.sheet = self.client.open_by_key(settings.GOOGLE_SHEET_ID)
            self.worksheet = self.sheet.worksheet(settings.INVENTORY_WORKSHEET_NAME)
            
            logger.info("Google Sheets service authenticated successfully")
            
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Sheets: {str(e)}")
            raise
    
    def get_inventory_data(self) -> pd.DataFrame:
        """
        Retrieve all inventory data from the worksheet.
        
        Returns:
            DataFrame with inventory data
        """
        try:
            records = self.worksheet.get_all_records()
            df = pd.DataFrame(records)
            
            logger.info(f"Retrieved {len(df)} inventory records from sheets")
            return df
            
        except Exception as e:
            logger.error(f"Failed to retrieve inventory data: {str(e)}")
            raise
    
    def find_item_by_sku(self, sku: str) -> Optional[Dict]:
        """
        Find an inventory item by SKU.
        
        Args:
            sku: The SKU to search for
            
        Returns:
            Dictionary with item data or None if not found
        """
        try:
            # Find the cell containing the SKU
            cell = self.worksheet.find(sku)
            if not cell:
                return None
            
            # Get the entire row
            row_data = self.worksheet.row_values(cell.row)
            headers = self.worksheet.row_values(1)  # Assuming first row is headers
            
            # Create dictionary from headers and row data
            item_data = dict(zip(headers, row_data))
            return item_data
            
        except gspread.exceptions.CellNotFound:
            return None
        except Exception as e:
            logger.error(f"Error finding item by SKU {sku}: {str(e)}")
            return None
    
    def update_cell_value(self, row: int, col: int, value: Any) -> bool:
        """
        Update a specific cell in the worksheet.
        
        Args:
            row: Row number (1-indexed)
            col: Column number (1-indexed)
            value: New value to set
            
        Returns:
            True if update was successful
        """
        try:
            self.worksheet.update_cell(row, col, value)
            logger.info(f"Updated cell ({row}, {col}) with value: {value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update cell ({row}, {col}): {str(e)}")
            return False
    
    def find_and_update_stock(self, sku: str, new_stock_level: int) -> bool:
        """
        Find an item by SKU and update its stock level.
        
        Args:
            sku: The SKU of the item to update
            new_stock_level: The new stock quantity
            
        Returns:
            True if update was successful
        """
        try:
            # Find the cell containing the SKU
            cell = self.worksheet.find(sku)
            if not cell:
                logger.warning(f"SKU '{sku}' not found in the sheet")
                return False
            
            # Assuming stock column is next to SKU column
            # This will need to be customized based on your sheet structure
            stock_col = cell.col + 1
            success = self.update_cell_value(cell.row, stock_col, new_stock_level)
            
            if success:
                logger.info(f"Successfully updated stock for SKU '{sku}' to {new_stock_level}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update stock for SKU '{sku}': {str(e)}")
            return False
    
    def get_sheet_structure(self) -> Dict[str, Any]:
        """
        Get information about the sheet structure.
        
        Returns:
            Dictionary with sheet metadata
        """
        try:
            headers = self.worksheet.row_values(1)
            num_rows = len(self.worksheet.get_all_values())
            num_cols = len(headers) if headers else 0
            
            return {
                'headers': headers,
                'num_rows': num_rows,
                'num_cols': num_cols,
                'worksheet_name': settings.INVENTORY_WORKSHEET_NAME,
                'sheet_title': self.sheet.title
            }
            
        except Exception as e:
            logger.error(f"Failed to get sheet structure: {str(e)}")
            raise 