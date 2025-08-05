#!/usr/bin/env python3
"""
Inventory Reconciliation MVP
Main script to run the inventory reconciliation process.
"""
import sys
import structlog
from datetime import datetime

from src.gmail_service import GmailService
from src.sheets_service import SheetsService
from src.parser_service import ParserService

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

def main():
    """Main function to run the inventory reconciliation MVP."""
    logger.info("Starting Inventory Reconciliation MVP")
    
    try:
        # Step 1: Initialize Services
        logger.info("Initializing services...")
        gmail_service = GmailService()
        sheets_service = SheetsService()
        parser_service = ParserService()
        logger.info("All services initialized successfully")
        
        # Step 2: Get the latest purchase email
        logger.info("Fetching latest purchase email...")
        email_data = gmail_service.get_latest_purchase_email()
        
        if not email_data:
            logger.warning("No purchase emails found")
            print("No purchase emails found matching your search criteria.")
            return
        
        logger.info(f"Found email: {email_data.get('subject', 'No subject')}")
        print(f"Processing email: {email_data.get('subject', 'No subject')}")
        
        # Step 3: Parse the purchase data from the email
        logger.info("Parsing email content...")
        parsed_items = parser_service.parse_email(email_data)
        
        if not parsed_items:
            logger.warning("No items could be parsed from the email")
            print("No purchase items could be parsed from the email.")
            print("This might mean the email format doesn't match our parsing patterns.")
            return
        
        # Step 4: Get parsing summary
        summary = parser_service.get_parsing_summary(parsed_items)
        logger.info(f"Parsing summary: {summary}")
        print(f"\nParsed {summary['total_items']} items:")
        for item in parsed_items:
            print(f"  - {item['item_name']} (SKU: {item['sku']}) x {item['quantity']}")
        
        # Step 5: Get current inventory from Google Sheets
        logger.info("Fetching current inventory...")
        inventory_df = sheets_service.get_inventory_data()
        
        if inventory_df.empty:
            logger.warning("No inventory data found in sheet")
            print("No inventory data found in the Google Sheet.")
            return
        
        print(f"\nCurrent inventory has {len(inventory_df)} items")
        print("Sheet structure:")
        print(f"  Headers: {list(inventory_df.columns)}")
        
        # Step 6: Process each parsed item
        logger.info("Processing inventory updates...")
        successful_updates = 0
        failed_updates = 0
        
        for item in parsed_items:
            sku = item['sku']
            quantity = item['quantity']
            
            # Find the item in our inventory
            inventory_row = inventory_df[inventory_df.iloc[:, 0] == sku]  # Assuming SKU is in first column
            
            if not inventory_row.empty:
                # Get current stock (assuming stock is in second column)
                current_stock = inventory_row.iloc[0, 1]  # Row 0, Column 1
                new_stock = current_stock + quantity
                
                print(f"Updating {sku}: {current_stock} + {quantity} = {new_stock}")
                
                # Update the sheet
                if sheets_service.find_and_update_stock(sku, new_stock):
                    successful_updates += 1
                    logger.info(f"Successfully updated {sku}")
                else:
                    failed_updates += 1
                    logger.error(f"Failed to update {sku}")
            else:
                print(f"WARNING: SKU '{sku}' not found in inventory sheet")
                failed_updates += 1
                logger.warning(f"SKU '{sku}' not found in inventory")
        
        # Step 7: Summary
        logger.info(f"Reconciliation complete. Success: {successful_updates}, Failed: {failed_updates}")
        print(f"\n=== RECONCILIATION COMPLETE ===")
        print(f"Successfully updated: {successful_updates} items")
        print(f"Failed updates: {failed_updates} items")
        print(f"Total items processed: {len(parsed_items)}")
        
        if failed_updates > 0:
            print("\nSome items could not be updated. This might be because:")
            print("- The SKU doesn't exist in your inventory sheet")
            print("- The sheet structure is different than expected")
            print("- There were API errors")
        
    except Exception as e:
        logger.error(f"Reconciliation failed: {str(e)}")
        print(f"ERROR: Reconciliation failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 