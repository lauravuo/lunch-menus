# -*- coding: utf-8 -*-
"""
Ståhlberg Lielahti lunch menu scraper.
Website: https://stahlbergkahvilat.fi/stahlberg-lielahti/
"""

from typing import Dict, List, Optional
from .base import BaseRestaurant


class StahlbergLielahti(BaseRestaurant):
    def __init__(self):
        super().__init__(
            name="Ståhlberg Lielahti",
            url="https://stahlbergkahvilat.fi/stahlberg-lielahti/",
        )

    def scrape_menu(self) -> Dict[str, List[str]]:
        """Scrape the lunch menu from Ståhlberg Lielahti."""
        soup = self.get_page_content()
        if not soup:
            return {}

        menu = {}
        day_names = [
            "Maanantai",
            "Tiistai",
            "Keskiviikko",
            "Torstai",
            "Perjantai",
            "Lauantai",
            "Sunnuntai",
        ]

        headers = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])

        for header in headers:
            matched_day = self._match_day(header.get_text(strip=True), day_names)
            if matched_day:
                table = self._find_table_for_day(header, day_names)
                if table:
                    items = self._extract_items_from_table(table)
                    if items:
                        menu[matched_day] = items

        return menu

    def _match_day(self, text: str, day_names: List[str]) -> Optional[str]:
        """Match text against Finnish day names."""
        for day in day_names:
            if day.lower() in text.lower():
                return day
        return None

    def _find_table_for_day(self, header, day_names: List[str]):
        """Find the menu table following a day header."""
        next_elements = header.find_all_next()
        for el in next_elements:
            if el.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                if self._match_day(el.get_text(strip=True), day_names):
                    # Hit next day header before finding a table
                    break

            if el.name == "table" and "ruokalista" in el.get("class", []):
                return el
        return None

    def _extract_items_from_table(self, table) -> List[str]:
        """Extract menu items from the table's column-1 cells."""
        items = []
        cells = table.find_all("td", class_="column-1")
        for cell in cells:
            text = cell.get_text(strip=True)
            if text and len(text) > 2:
                # Clean up double spaces or weird chars
                clean_text = " ".join(text.split())
                items.append(clean_text)
        return items
