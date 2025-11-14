"""
Kontukeittiö Nokia lunch menu scraper.
API: https://europe-west1-luncher-7cf76.cloudfunctions.net/api/v1/week/
1baa89be-11dc-4447-abb3-bbaef16cc6d1/active?language=fi
"""

from typing import Dict, List
from .base import BaseRestaurant


class KontukeittioNokia(BaseRestaurant):
    def __init__(self):
        super().__init__(
            name="Kontukeittiö Nokia",
            url="https://europe-west1-luncher-7cf76.cloudfunctions.net/api/v1/week/"
            "1baa89be-11dc-4447-abb3-bbaef16cc6d1/active?language=fi",
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

    def _is_valid_day(self, day: dict) -> bool:
        """Check if a day is valid for processing."""
        return not (day.get("isHidden") or day.get("isClosed"))

    def _get_day_name(self, day: dict) -> str:
        """Extract and validate day name from day data."""
        return day.get("dayName", {}).get("fi", "")

    def _format_allergens(self, allergens: list) -> str:
        """Format allergens list into a string."""
        if not allergens:
            return ""
        return " (" + ", ".join(a.get("abbreviation", {}).get("fi", "") for a in allergens) + ")"

    def _extract_menu_items(self, day: dict) -> List[str]:
        """Extract menu items from a day's data."""
        menu_items = []
        for lunch in day.get("lunches", []):
            title = lunch.get("title", {}).get("fi", "").strip()
            if not title:
                continue
                
            # Format allergens
            allergens = self._format_allergens(lunch.get("allergens", []))
            
            # Format price if available
            price = ""
            if "normalPrice" in lunch and "price" in lunch["normalPrice"]:
                price = f" {lunch['normalPrice']['price']}€"
                
            # Combine title, allergens, and price
            menu_item = f"{title}{allergens}{price}"
            if menu_item:
                menu_items.append(menu_item)
                
        return menu_items

    def scrape_menu(self) -> Dict[str, List[str]]:
        """Scrape the lunch menu from Kontukeittiö Nokia JSON API."""
        json_data = self.get_page_content()
        if not json_data:
            return {}

        try:
            # Check JSON structure
            if not isinstance(json_data, dict) or not json_data.get("success"):
                from .base import logging
                logging.warning(f"Unexpected JSON structure from {self.name}")
                return {}

            week_data = json_data.get("data", {}).get("week", {})
            days = week_data.get("days", [])
            
            menu = {}
            for day in days:
                if not self._is_valid_day(day):
                    continue
                    
                day_name = self._get_day_name(day)
                if not day_name or day_name in ["Lauantai", "Sunnuntai"]:
                    continue
                    
                menu_items = self._extract_menu_items(day)
                if menu_items:
                    menu[day_name] = menu_items

            return menu

        except Exception as e:
            from .base import logging
            logging.error(f"Error parsing {self.name} menu: {e}")
            return {}
