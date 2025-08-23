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
        day_name = day.get("dayName", {}).get("fi", "")
        day_mapping = {
            "Maanantai": "Maanantai",
            "Tiistai": "Tiistai",
            "Keskiviikko": "Keskiviikko",
            "Torstai": "Torstai",
            "Perjantai": "Perjantai",
        }
        return day_mapping.get(day_name, "")

    def _extract_menu_items(self, day: dict) -> List[str]:
        """Extract menu items from a day's data."""
        menu_items = []
        if day.get("menus"):
            for menu_item in day["menus"]:
                if menu_item.get("name", {}).get("fi"):
                    item_name = menu_item["name"]["fi"].strip()
                    if item_name and len(item_name) > 3:
                        menu_items.append(item_name)
        return menu_items

    def scrape_menu(self) -> Dict[str, List[str]]:
        """Scrape the lunch menu from Kontukeittiö Nokia JSON API."""
        json_data = self.get_page_content()
        if not json_data:
            return {}

        try:
            # Check JSON structure
            if not (
                json_data.get("success")
                and json_data.get("data", {}).get("week", {}).get("days")
            ):
                from .base import logging

                logging.warning(f"Unexpected JSON structure from {self.name}")
                return {}

            days = json_data["data"]["week"]["days"]
            menu = {}

            for day in days:
                if not self._is_valid_day(day):
                    continue

                day_name = self._get_day_name(day)
                if not day_name:
                    continue

                menu_items = self._extract_menu_items(day)
                if menu_items:
                    menu[day_name] = menu_items

            return menu

        except Exception as e:
            from .base import logging

            logging.error(f"Error parsing {self.name} menu: {e}")
            return {}
