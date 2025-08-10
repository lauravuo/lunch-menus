"""
Kontukeittiö Nokia lunch menu scraper.
API: https://europe-west1-luncher-7cf76.cloudfunctions.net/api/v1/week/1baa89be-11dc-4447-abb3-bbaef16cc6d1/active?language=fi
"""

import json
from typing import Dict, List
from .base import BaseRestaurant


class KontukeittioNokia(BaseRestaurant):
    def __init__(self):
        super().__init__(
            name="Kontukeittiö Nokia",
            url="https://europe-west1-luncher-7cf76.cloudfunctions.net/api/v1/week/1baa89be-11dc-4447-abb3-bbaef16cc6d1/active?language=fi",
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
        """Scrape the lunch menu from Kontukeittiö Nokia JSON API."""
        json_data = self.get_page_content()
        if not json_data:
            return {}

        try:
            # Extract menu data from JSON structure
            if json_data.get("success") and json_data.get("data", {}).get("week", {}).get("days"):
                days = json_data["data"]["week"]["days"]
                menu = {}
                
                for day in days:
                    # Skip hidden or closed days
                    if day.get("isHidden") or day.get("isClosed"):
                        continue
                    
                    day_name = day.get("dayName", {}).get("fi", "")
                    if not day_name:
                        continue
                    
                    # Convert Finnish day names to our standard format
                    day_mapping = {
                        "Maanantai": "Maanantai",
                        "Tiistai": "Tiistai", 
                        "Keskiviikko": "Keskiviikko",
                        "Torstai": "Torstai",
                        "Perjantai": "Perjantai"
                    }
                    
                    if day_name in day_mapping:
                        standard_day = day_mapping[day_name]
                        lunches = day.get("lunches", [])
                        
                        if lunches:
                            menu_items = []
                            for lunch in lunches:
                                title = lunch.get("title", {}).get("fi", "")
                                if title:
                                    # Build menu item with allergens
                                    allergens = lunch.get("allergens", [])
                                    allergen_codes = []
                                    
                                    for allergen in allergens:
                                        code = allergen.get("abbreviation", {}).get("fi", "")
                                        if code:
                                            allergen_codes.append(code)
                                    
                                    # Format: "Menu Item (L, G)" or just "Menu Item"
                                    if allergen_codes:
                                        menu_item = f"{title} ({', '.join(allergen_codes)})"
                                    else:
                                        menu_item = title
                                    
                                    menu_items.append(menu_item)
                            
                            if menu_items:
                                menu[standard_day] = menu_items
                
                return menu
            else:
                from .base import logging
                logging.error(f"Invalid JSON structure from {self.name}")
                return {}
                
        except Exception as e:
            from .base import logging
            logging.error(f"Error parsing {self.name} JSON: {e}")
            return {}
