"""
Email content parsing service for extracting purchase data.
"""
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import structlog

logger = structlog.get_logger()

class ParserService:
    """Service for parsing purchase data from email content."""
    
    def __init__(self):
        """Initialize the parser service."""
        self.parsed_items = []
    
    def parse_email(self, email_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse purchase data from email content.
        
        Args:
            email_data: Email data dictionary from Gmail service
            
        Returns:
            List of parsed purchase items
        """
        try:
            logger.info(f"Parsing email: {email_data.get('subject', 'No subject')}")
            
            # Extract the email body
            body = email_data.get('body', '')
            if not body:
                logger.warning("Email body is empty")
                return []
            
            # Clean the content
            cleaned_body = self._clean_content(body)
            
            # Parse the content (this will be customized based on email format)
            items = self._parse_content(cleaned_body)
            
            logger.info(f"Successfully parsed {len(items)} items from email")
            return items
            
        except Exception as e:
            logger.error(f"Failed to parse email: {str(e)}")
            return []
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize email content."""
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n', '\n', content)
        
        return content.strip()
    
    def _parse_content(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse the cleaned content to extract purchase items.
        
        This is a placeholder method that will be customized based on your email format.
        For now, it includes some common patterns that might work.
        """
        items = []
        
        # Common patterns for parsing purchase data
        patterns = [
            # Pattern 1: "SKU: ABC123, Quantity: 5"
            r'[Ss][Kk][Uu][:\s]+([A-Za-z0-9\-_]+)[,\s]+[Qq]uantity[:\s]+(\d+)',
            
            # Pattern 2: "Item: Product Name | SKU: ABC123 | Qty: 5"
            r'[Ii]tem[:\s]+([^|]+)\s*\|\s*[Ss][Kk][Uu][:\s]+([A-Za-z0-9\-_]+)\s*\|\s*[Qq]ty[:\s]+(\d+)',
            
            # Pattern 3: "Product Name (SKU: ABC123) - Quantity: 5"
            r'([^(]+)\s*\([Ss][Kk][Uu][:\s]+([A-Za-z0-9\-_]+)\)[^0-9]*(\d+)',
            
            # Pattern 4: Simple table format
            r'([A-Za-z0-9\s]+)\s+([A-Za-z0-9\-_]+)\s+(\d+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                try:
                    if len(match) == 2:
                        # Pattern 1: SKU and quantity
                        sku = match[0].strip()
                        quantity = int(match[1])
                        item_name = sku  # Use SKU as name if no name provided
                    elif len(match) == 3:
                        # Patterns 2, 3, 4: Name, SKU, and quantity
                        item_name = match[0].strip()
                        sku = match[1].strip()
                        quantity = int(match[2])
                    else:
                        continue
                    
                    # Validate the parsed data
                    if sku and quantity > 0:
                        items.append({
                            'sku': sku,
                            'item_name': item_name,
                            'quantity': quantity,
                            'parsed_at': datetime.now().isoformat()
                        })
                        
                except (ValueError, IndexError) as e:
                    logger.warning(f"Failed to parse match {match}: {str(e)}")
                    continue
        
        return items
    
    def get_parsing_summary(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of the parsing results.
        
        Args:
            items: List of parsed items
            
        Returns:
            Dictionary with parsing summary
        """
        if not items:
            return {
                'total_items': 0,
                'total_quantity': 0,
                'unique_skus': 0,
                'parsing_success': False
            }
        
        total_quantity = sum(item.get('quantity', 0) for item in items)
        unique_skus = len(set(item.get('sku', '') for item in items))
        
        return {
            'total_items': len(items),
            'total_quantity': total_quantity,
            'unique_skus': unique_skus,
            'parsing_success': True,
            'items': items
        } 