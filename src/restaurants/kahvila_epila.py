"""
Kahvila Epilä lunch menu scraper.
Website: https://www.kahvilaepila.com/lounaslista/
"""

from typing import Dict, List
from bs4 import BeautifulSoup
import re
from .base import BaseRestaurant


class KahvilaEpila(BaseRestaurant):
    """Scraper for Kahvila Epilä restaurant."""
    
    def __init__(self):
        super().__init__(
            name="Kahvila Epilä",
            url="https://www.kahvilaepila.com/lounaslista/"
        )
    
    def scrape_menu(self) -> Dict[str, List[str]]:
        """Scrape the lunch menu from Kahvila Epilä website."""
        soup = self.get_page_content()
        if not soup:
            return {}
        
        menu_data = {}
        
        try:
            # Find the main content area
            content = soup.find('div', class_='entry-content') or soup.find('main') or soup
            
            # Look for week information
            week_header = content.find('h2')
            if week_header and 'viikko' in week_header.get_text().lower():
                # Find all day sections
                day_sections = content.find_all(['h3', 'h4', 'strong'])
                
                current_day = None
                current_items = []
                
                for element in day_sections:
                    text = element.get_text().strip()
                    
                    # Check if this is a day header
                    if any(day in text.lower() for day in ['maanantai', 'tiistai', 'keskiviikko', 'torstai', 'perjantai']):
                        # Save previous day's data
                        if current_day and current_items:
                            menu_data[current_day] = current_items
                        
                        # Start new day
                        current_day = text
                        current_items = []
                        
                        # Look for menu items in the next sibling elements
                        next_elem = element.find_next_sibling()
                        while next_elem and next_elem.name not in ['h3', 'h4', 'strong']:
                            if next_elem.name == 'ul':
                                # Found a list of menu items
                                items = next_elem.find_all('li')
                                for item in items:
                                    item_text = item.get_text().strip()
                                    if item_text:
                                        current_items.append(item_text)
                                break
                            elif next_elem.name == 'p':
                                # Check if paragraph contains menu items
                                p_text = next_elem.get_text().strip()
                                if p_text and not p_text.startswith('Lounas') and not p_text.startswith('Keitto'):
                                    current_items.append(p_text)
                            
                            next_elem = next_elem.find_next_sibling()
                
                # Save the last day's data
                if current_day and current_items:
                    menu_data[current_day] = current_items
            
            # If the above method didn't work, try alternative approach
            if not menu_data:
                # Look for any text that might contain menu information
                all_text = content.get_text()
                
                # Try to find menu items using regex patterns
                day_patterns = [
                    r'(maanantai[:\s]*)(.*?)(?=tiistai|keskiviikko|torstai|perjantai|$)',
                    r'(tiistai[:\s]*)(.*?)(?=keskiviikko|torstai|perjantai|$)',
                    r'(keskiviikko[:\s]*)(.*?)(?=torstai|perjantai|$)',
                    r'(torstai[:\s]*)(.*?)(?=perjantai|$)',
                    r'(perjantai[:\s]*)(.*?)(?=$)'
                ]
                
                for pattern in day_patterns:
                    match = re.search(pattern, all_text, re.IGNORECASE | re.DOTALL)
                    if match:
                        day_name = match.group(1).strip().rstrip(':')
                        menu_text = match.group(2).strip()
                        
                        # Split menu text into items
                        items = [item.strip() for item in menu_text.split('\n') if item.strip()]
                        if items:
                            menu_data[day_name] = items
            
        except Exception as e:
            print(f"Error scraping Kahvila Epilä menu: {e}")
        
        return menu_data
