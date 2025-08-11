"""
Nokian Kartano (FoodCo) restaurant scraper using JSON API.
"""

import json
from typing import Dict, List
from .base import BaseRestaurant


class NokianKartano(BaseRestaurant):
    def __init__(self):
        super().__init__(
            name="Nokian Kartano (FoodCo)",
            url="https://www.compass-group.fi/menuapi/feed/json?costNumber=3443&language=fi",
        )

    def get_page_content(self):
        """Override to fetch JSON instead of HTML."""
        try:
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            from .base import logging
            logging.error(f"Failed to fetch {self.name} JSON: {e}")
            return None

    def scrape_menu(self) -> Dict[str, List[str]]:
        """Scrape the lunch menu from Nokian Kartano JSON API."""
        json_data = self.get_page_content()
        if not json_data:
            return {}

        try:
            if json_data.get("MenusForDays"):
                days = json_data["MenusForDays"]
                menu = {}
                
                # Map Finnish day names to standard format
                day_mapping = {
                    0: "Maanantai",  # Monday
                    1: "Tiistai",    # Tuesday
                    2: "Keskiviikko", # Wednesday
                    3: "Torstai",    # Thursday
                    4: "Perjantai"   # Friday
                }
                
                from .base import logging
                logging.info(f"Processing {len(days)} days from {self.name} JSON API")
                
                for day in days:
                    if not day.get("SetMenus"):
                        continue
                    
                    # Extract date and determine weekday
                    date_str = day.get("Date", "")
                    if not date_str:
                        continue
                    
                    # Parse the date to get weekday (0=Monday, 6=Sunday)
                    from datetime import datetime
                    try:
                        # Handle the timezone format from the API
                        if date_str.endswith("+00:00"):
                            date_obj = datetime.fromisoformat(date_str)
                        else:
                            # Try parsing without timezone info
                            date_obj = datetime.fromisoformat(date_str.replace("Z", ""))
                        
                        weekday = date_obj.weekday()
                        
                        if weekday < 5:  # Monday to Friday only
                            standard_day = day_mapping[weekday]
                            
                            # Extract menu components
                            menu_items = []
                            for set_menu in day["SetMenus"]:
                                menu_name = set_menu.get("Name")
                                if menu_name and menu_name.strip() == "Buffet lounas":
                                    components = set_menu.get("Components", [])
                                    for component in components:
                                        if component and component.strip():
                                            menu_items.append(component)
                            
                            if menu_items:
                                menu[standard_day] = menu_items
                                logging.info(f"Added {len(menu_items)} items for {standard_day}")
                            else:
                                logging.info(f"No menu items found for {standard_day}")
                        else:
                            logging.info(f"Skipping weekend day: {date_obj.strftime('%A')}")
                            
                    except (ValueError, KeyError) as e:
                        from .base import logging
                        logging.error(f"Error parsing date '{date_str}' for {self.name}: {e}")
                        continue
                
                logging.info(f"Successfully extracted menu for {len(menu)} days from {self.name}")
                return menu
            else:
                from .base import logging
                logging.error(f"Invalid JSON structure from {self.name} - no MenusForDays found")
                return {}
                
        except Exception as e:
            from .base import logging
            logging.error(f"Error parsing {self.name} JSON: {e}")
            return {}
