"""
Pizza Buffa ABC Kolmenkulma Nokia restaurant scraper.
Scrapes lunch menu from Raflaamo.fi website.
"""

import re
from typing import Dict, List
from .base import BaseRestaurant


class PizzaBuffa(BaseRestaurant):
    def __init__(self):
        super().__init__(
            name="Pizza Buffa ABC Kolmenkulma",
            url="https://www.raflaamo.fi/fi/ravintola/nokia/pizza-buffa-abc-kolmenkulma-nokia/menu/lounas",
        )

    def scrape_menu(self) -> Dict[str, List[str]]:
        """Scrape the lunch menu from Pizza Buffa Raflaamo website."""
        soup = self.get_page_content()
        if not soup:
            return {}

        try:
            menu = {}
            
            # Find all day sections (h3 elements with day names)
            day_headers = soup.find_all('h3')
            
            for header in day_headers:
                day_text = header.get_text(strip=True)
                
                # Extract Finnish day name from headers like "Tiistai 12.8."
                day_match = re.match(r'^(Maanantai|Tiistai|Keskiviikko|Torstai|Perjantai|Lauantai|Sunnuntai)', day_text)
                if not day_match:
                    continue
                
                day_name = day_match.group(1)
                
                # Skip weekend days for lunch menu
                if day_name in ['Lauantai', 'Sunnuntai']:
                    continue
                
                # Find the content after this header - look for the parent container
                menu_items = []
                
                # Try to find the next sibling or parent's next sibling with content
                current = header
                content_found = False
                
                # Look through the next few siblings for content
                for _ in range(10):  # Limit search to avoid infinite loops
                    current = current.next_sibling
                    if not current:
                        break
                        
                    if hasattr(current, 'get_text'):
                        text = current.get_text()
                        
                        # Stop if we hit another day header
                        if re.match(r'^(Maanantai|Tiistai|Keskiviikko|Torstai|Perjantai|Lauantai|Sunnuntai)', text.strip()):
                            break
                        
                        # Look for menu content
                        if ('Buffantai' in text or 'Lounas:' in text) and len(text) > 50:
                            content_found = True
                            
                            # Extract dishes using multiple patterns
                            # Pattern 1: Look for dishes with dietary codes like (L), (M), (VEG), (G)
                            dish_pattern1 = r'([A-ZÄÖÅ][^€\n]*?(?:\([LMVEG, ]+\)))'
                            dishes1 = re.findall(dish_pattern1, text)
                            
                            # Pattern 2: Look for capitalized food items
                            dish_pattern2 = r'([A-ZÄÖÅ][a-zäöå\s-]{10,60}(?:\([^)]+\))?)'
                            dishes2 = re.findall(dish_pattern2, text)
                            
                            all_dishes = dishes1 + dishes2
                            
                            for dish in all_dishes:
                                dish = dish.strip()
                                
                                # Clean and filter dishes
                                if (dish and 
                                    len(dish) > 8 and 
                                    not re.match(r'^\d+[,.]?\d*\s*€', dish) and
                                    not dish.startswith('Buffantai') and
                                    not dish.startswith('Lasten') and
                                    not dish.startswith('Alle') and
                                    not dish.startswith('Lounas:') and
                                    'Pizzavalikoima' not in dish and
                                    'salaatti- ja leipäpöytä' not in dish and
                                    'ruokajuomat ja kahvi' not in dish):
                                    
                                    # Additional cleaning
                                    dish = re.sub(r'\s+', ' ', dish)
                                    dish = dish.replace('€', '').strip()
                                    
                                    if dish and dish not in menu_items:
                                        menu_items.append(dish)
                
                # If we found items for this day, add them
                if menu_items:
                    # Clean up and deduplicate items
                    cleaned_items = []
                    for item in menu_items:
                        # Additional cleaning
                        item = re.sub(r'^[•\-\*]\s*', '', item)  # Remove bullet points
                        item = re.sub(r'\s+', ' ', item).strip()
                        
                        if (item and 
                            len(item) > 8 and 
                            item not in cleaned_items and
                            not item.lower().startswith('pizzavalikoima')):
                            cleaned_items.append(item)
                    
                    if cleaned_items:
                        menu[day_name] = cleaned_items[:5]  # Limit to 5 main items
            
            # If still no menu found, try a simpler approach
            if not menu:
                # Get all text and try to parse it as one block
                full_text = soup.get_text()
                days = ['Maanantai', 'Tiistai', 'Keskiviikko', 'Torstai', 'Perjantai']
                
                for day in days:
                    if day in full_text:
                        # Find the day section
                        day_start = full_text.find(day)
                        
                        # Find the next day or end of relevant content
                        day_end = len(full_text)
                        for other_day in days:
                            if other_day != day:
                                other_start = full_text.find(other_day, day_start + 1)
                                if other_start != -1 and other_start < day_end:
                                    day_end = other_start
                        
                        day_content = full_text[day_start:day_end]
                        
                        # Extract dishes from this day's content
                        dishes = []
                        # Look for common Finnish food words and patterns
                        food_patterns = [
                            r'([A-ZÄÖÅ][a-zäöå\s-]{8,50}(?:stroganoff|kiusaus|laatikko|pata|vuoka))',
                            r'([A-ZÄÖÅ][a-zäöå\s-]{8,50}(?:broileri|kana|nauta|sika|kala|lohi))',
                            r'([A-ZÄÖÅ][a-zäöå\s-]{8,50}(?:kastike|keitto|salaatti))',
                            r'([A-ZÄÖÅ][a-zäöå\s-]{8,50}(?:\([LMVEG, ]+\)))'
                        ]
                        
                        for pattern in food_patterns:
                            matches = re.findall(pattern, day_content)
                            dishes.extend([match.strip() for match in matches])
                        
                        if dishes:
                            # Remove duplicates and clean
                            unique_dishes = []
                            for dish in dishes:
                                if dish not in unique_dishes and len(dish) > 8:
                                    unique_dishes.append(dish)
                            
                            if unique_dishes:
                                menu[day] = unique_dishes[:4]
            
            from .base import logging
            logging.info(f"Successfully extracted menu for {len(menu)} days from {self.name}")
            return menu
            
        except Exception as e:
            from .base import logging
            logging.error(f"Error parsing {self.name} menu: {e}")
            return {}
