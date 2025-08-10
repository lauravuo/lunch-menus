"""
Nokian Kartano (FoodCo) lunch menu scraper.
Website: https://www.compass-group.fi/ravintolat-ja-ruokalistat/foodco/kaupungit/nokia/nokian-kartano/
"""

import re
from typing import Dict, List
from .base import BaseRestaurant


class NokianKartano(BaseRestaurant):
    def __init__(self):
        super().__init__(
            name="Nokian Kartano (FoodCo)",
            url="https://www.compass-group.fi/ravintolat-ja-ruokalistat/foodco/kaupungit/nokia/nokian-kartano/",
        )

    def _extract_menu_with_regex(self, soup) -> Dict[str, List[str]]:
        """Extract menu using regex patterns."""
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

    def _extract_menu_from_lists(self, soup) -> Dict[str, List[str]]:
        """Extract menu from HTML lists."""
        menu = {}

        # Look for unordered and ordered lists
        lists = soup.find_all(["ul", "ol"])

        for lst in lists:
            items = []
            for item in lst.find_all("li"):
                text = item.get_text(strip=True)
                if text and len(text) > 3:
                    items.append(text)

            if items:
                # Try to determine if this is a daily menu
                parent_text = ""
                parent = lst.find_parent()
                if parent:
                    parent_text = parent.get_text().lower()

                if any(
                    day in parent_text
                    for day in [
                        "maanantai",
                        "tiistai",
                        "keskiviikko",
                        "torstai",
                        "perjantai",
                    ]
                ):
                    # Extract day name from parent
                    for day in [
                        "maanantai",
                        "tiistai",
                        "keskiviikko",
                        "torstai",
                        "perjantai",
                    ]:
                        if day in parent_text:
                            day_name = day.capitalize()
                            menu[day_name] = items
                            break
                else:
                    # Generic menu
                    menu["Lounas"] = items

        return menu

    def _extract_menu_from_content(self, soup) -> Dict[str, List[str]]:
        """Extract menu from general content areas."""
        menu = {}
        content_areas = soup.find_all(
            ["div", "section"], class_=re.compile(r"content|main|entry|menu")
        )

        for area in content_areas:
            text = area.get_text()
            if self._contains_menu_keywords(text):
                # Try to extract structured menu items
                items = self._extract_menu_items(area)
                if items:
                    # Assign to a generic day if we can't determine specific days
                    menu["Lounas"] = items
                    break

        return menu

    def _contains_menu_keywords(self, text: str) -> bool:
        """Check if text contains menu-related keywords."""
        keywords = [
            "lounas",
            "keitto",
            "pääruoka",
            "ruoka",
            "menu",
            "soup",
            "main",
            "foodco",
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)

    def _extract_menu_items(self, element) -> List[str]:
        """Extract menu items from an HTML element."""
        items = []

        # Look for list items
        list_items = element.find_all("li")
        for item in list_items:
            text = item.get_text(strip=True)
            if text and len(text) > 3:
                items.append(text)

        # Look for paragraphs
        if not items:
            paragraphs = element.find_all("p")
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 3 and not text.startswith("©"):
                    items.append(text)

        return items

    def scrape_menu(self) -> Dict[str, List[str]]:
        """Scrape the lunch menu from Nokian Kartano (FoodCo)."""
        soup = self.get_page_content()
        if not soup:
            return {}

        # Try regex approach first
        menu = self._extract_menu_with_regex(soup)

        # Try list extraction if regex didn't work
        if not menu:
            menu = self._extract_menu_from_lists(soup)

        # Fallback to content extraction if nothing else worked
        if not menu:
            menu = self._extract_menu_from_content(soup)

        return menu
