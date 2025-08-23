"""
Nokian Kartano (FoodCo) restaurant scraper using JSON API.
"""

from typing import Dict, List
from .base import BaseRestaurant


class NokianKartano(BaseRestaurant):
    def __init__(self):
        super().__init__(
            name="Nokian Kartano (FoodCo)",
            url="https://www.compass-group.fi/menuapi/feed/json?"
            "costNumber=3443&language=fi",
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

    def _parse_date(self, date_str: str):
        """Parse date string and return datetime object."""
        from datetime import datetime

        if date_str.endswith("+00:00"):
            return datetime.fromisoformat(date_str)
        else:
            return datetime.fromisoformat(date_str.replace("Z", ""))

    def _get_day_mapping(self) -> Dict[int, str]:
        """Get mapping from weekday number to Finnish day name."""
        return {
            0: "Maanantai",  # Monday
            1: "Tiistai",  # Tuesday
            2: "Keskiviikko",  # Wednesday
            3: "Torstai",  # Thursday
            4: "Perjantai",  # Friday
        }

    def _extract_menu_items(self, day: dict) -> List[str]:
        """Extract menu items from a day's data."""
        menu_items = []
        for set_menu in day["SetMenus"]:
            menu_name = set_menu.get("Name")
            if menu_name and menu_name.strip() == "Buffet lounas":
                components = set_menu.get("Components", [])
                for component in components:
                    if component and component.strip():
                        menu_items.append(component)
        return menu_items

    def _process_day(self, day: dict, day_mapping: Dict[int, str]) -> tuple:
        """Process a single day's data and return (day_name, menu_items)."""
        from .base import logging

        if not day.get("SetMenus"):
            return None, None

        date_str = day.get("Date", "")
        if not date_str:
            return None, None

        try:
            date_obj = self._parse_date(date_str)
            weekday = date_obj.weekday()

            if weekday >= 5:  # Skip weekends
                logging.info(f"Skipping weekend day: {date_obj.strftime('%A')}")
                return None, None

            standard_day = day_mapping[weekday]
            menu_items = self._extract_menu_items(day)

            if menu_items:
                logging.info(f"Added {len(menu_items)} items for {standard_day}")
            else:
                logging.info(f"No menu items found for {standard_day}")

            return standard_day, menu_items

        except (ValueError, KeyError) as e:
            logging.error(f"Error parsing date '{date_str}' for {self.name}: {e}")
            return None, None

    def scrape_menu(self) -> Dict[str, List[str]]:
        """Scrape the lunch menu from Nokian Kartano JSON API."""
        json_data = self.get_page_content()
        if not json_data:
            return {}

        try:
            if not json_data.get("MenusForDays"):
                from .base import logging

                logging.error(
                    f"Invalid JSON structure from {self.name} - no MenusForDays found"
                )
                return {}

            days = json_data["MenusForDays"]
            menu = {}
            day_mapping = self._get_day_mapping()

            from .base import logging

            logging.info(f"Processing {len(days)} days from {self.name} JSON API")

            for day in days:
                day_name, menu_items = self._process_day(day, day_mapping)
                if day_name and menu_items:
                    menu[day_name] = menu_items

            logging.info(
                f"Successfully extracted menu for {len(menu)} days from {self.name}"
            )
            return menu

        except Exception as e:
            from .base import logging

            logging.error(f"Error parsing {self.name} JSON: {e}")
            return {}
