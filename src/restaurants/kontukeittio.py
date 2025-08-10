"""
Kontukeittiö Nokia lunch menu scraper.
Website: https://kontukoti.fi/kontukeittio/kontukeittio-nokia/
"""

from typing import Dict, List
from bs4 import BeautifulSoup
import re
from .base import BaseRestaurant


class KontukeittioNokia(BaseRestaurant):
    """Scraper for Kontukeittiö Nokia restaurant."""
    
    def __init__(self):
        super().__init__(
            name="Kontukeittiö Nokia",
            url="https://kontukoti.fi/kontukeittio/kontukeittio-nokia/"
        )
    
    def scrape_menu(self) -> Dict[str, List[str]]:
        """Scrape the lunch menu from Kontukeittiö Nokia website."""
        soup = self.get_page_content()
        if not soup:
            return {}
        
        menu_data = {}
        
        try:
            # Look for menu content - this site might have a separate menu page
            # First try to find any menu-related content on the main page
            content = soup.find('div', class_='entry-content') or soup.find('main') or soup
            
            # Look for menu items in the content
            menu_items = content.find_all(['p', 'li', 'div'], string=re.compile(r'.*'))
            
            # Try to find menu information in the text
            all_text = content.get_text()
            
            # Look for common Finnish menu patterns
            menu_patterns = [
                r'(maanantai[:\s]*)(.*?)(?=tiistai|keskiviikko|torstai|perjantai|$)',
                r'(tiistai[:\s]*)(.*?)(?=keskiviikko|torstai|perjantai|$)',
                r'(keskiviikko[:\s]*)(.*?)(?=torstai|perjantai|$)',
                r'(torstai[:\s]*)(.*?)(?=perjantai|$)',
                r'(perjantai[:\s]*)(.*?)(?=$)'
            ]
            
            for pattern in menu_patterns:
                match = re.search(pattern, all_text, re.IGNORECASE | re.DOTALL)
                if match:
                    day_name = match.group(1).strip().rstrip(':')
                    menu_text = match.group(2).strip()
                    
                    # Split menu text into items and clean them
                    items = []
                    for line in menu_text.split('\n'):
                        line = line.strip()
                        if line and len(line) > 3:  # Filter out very short lines
                            # Remove common non-menu text
                            if not any(skip in line.lower() for skip in [
                                'lounas', 'keitto', 'salaatti', 'buffet', 'hinta', '€', 'euro'
                            ]):
                                items.append(line)
                    
                    if items:
                        menu_data[day_name] = items
            
            # If no structured menu found, try to extract any food-related content
            if not menu_data:
                # Look for food-related keywords in the content
                food_keywords = ['keitto', 'lounas', 'ruoka', 'ateria', 'buffet']
                found_items = []
                
                for element in content.find_all(['p', 'li', 'div']):
                    text = element.get_text().strip()
                    if any(keyword in text.lower() for keyword in food_keywords):
                        if len(text) > 10 and len(text) < 200:  # Reasonable length for menu items
                            found_items.append(text)
                
                if found_items:
                    menu_data['Lounas'] = found_items[:5]  # Limit to 5 items
            
        except Exception as e:
            print(f"Error scraping Kontukeittiö Nokia menu: {e}")
        
        return menu_data
