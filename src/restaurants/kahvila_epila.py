"""
Kahvila Epilä lunch menu scraper.
Website: https://www.kahvilaepila.com/lounaslista/
"""

import re
from typing import Dict, List
from .base import BaseRestaurant


class KahvilaEpila(BaseRestaurant):
    def __init__(self):
        super().__init__(
            name="Kahvila Epilä", url="https://www.kahvilaepila.com/lounaslista/"
        )

    def _extract_menu_from_structure(self, soup) -> Dict[str, List[str]]:
        """Extract menu using structured HTML elements."""
        menu = {}
        day_headers = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])

        for header in day_headers:
            day_text = header.get_text(strip=True)
            if self._is_day_header(day_text):
                day_name = self._normalize_day_name(day_text)
                items = self._get_items_for_day(header)
                if items:
                    menu[day_name] = items

        return menu

    def _is_day_header(self, text: str) -> bool:
        """Check if text represents a day header."""
        day_patterns = [
            r"maanantai",
            r"tiistai",
            r"keskiviikko",
            r"torstai",
            r"perjantai",
            r"monday",
            r"tuesday",
            r"wednesday",
            r"thursday",
            r"friday",
        ]
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in day_patterns)

    def _normalize_day_name(self, text: str) -> str:
        """Normalize day names to Finnish."""
        day_mapping = {
            "maanantai": "Maanantai",
            "monday": "Maanantai",
            "tiistai": "Tiistai",
            "tuesday": "Tiistai",
            "keskiviikko": "Keskiviikko",
            "wednesday": "Keskiviikko",
            "torstai": "Torstai",
            "thursday": "Torstai",
            "perjantai": "Perjantai",
            "friday": "Perjantai",
        }
        text_lower = text.lower()
        for pattern, normalized in day_mapping.items():
            if pattern in text_lower:
                return normalized
        return text

    def _get_items_for_day(self, header) -> List[str]:
        """Extract menu items for a specific day."""
        items = []
        current = header.find_next_sibling()

        while current and not self._is_next_day_header(current):
            if current.name in ["p", "li", "div"]:
                text = current.get_text(strip=True)
                if text and len(text) > 3:
                    items.append(text)
            current = current.find_next_sibling()

        return items

    def _is_next_day_header(self, element) -> bool:
        """Check if element is a day header."""
        if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            return self._is_day_header(element.get_text(strip=True))
        return False

    def _extract_menu_with_regex(self, soup) -> Dict[str, List[str]]:
        """Fallback: Extract menu using regex patterns."""
        menu = {}
        text = soup.get_text()

        # Look for day patterns followed by menu items
        day_patterns = [
            (
                r"maanantai[:\s]*(.*?)(?=tiistai|keskiviikko|torstai|perjantai|$)",
                "Maanantai",
            ),
            (r"tiistai[:\s]*(.*?)(?=keskiviikko|torstai|perjantai|$)", "Tiistai"),
            (r"keskiviikko[:\s]*(.*?)(?=torstai|perjantai|$)", "Keskiviikko"),
            (r"torstai[:\s]*(.*?)(?=perjantai|$)", "Torstai"),
            (r"perjantai[:\s]*(.*?)$", "Perjantai"),
        ]

        for pattern, day_name in day_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1).strip()
                items = [item.strip() for item in content.split("\n") if item.strip()]
                if items:
                    menu[day_name] = items

        return menu

    def scrape_menu(self) -> Dict[str, List[str]]:
        """Scrape the lunch menu from Kahvila Epilä."""
        soup = self.get_page_content()
        if not soup:
            return {}

        # Try structured approach first
        menu = self._extract_menu_from_structure(soup)

        # Fallback to regex if structured approach didn't work
        if not menu:
            menu = self._extract_menu_with_regex(soup)

        return menu
