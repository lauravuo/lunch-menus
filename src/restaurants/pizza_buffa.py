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
            url="https://www.raflaamo.fi/fi/tampere/"
            "pizza-buffa-abc-kolmenkulma/menu/lunch",
        )

    def _extract_dishes(self, text: str) -> List[str]:
        """Extract dish names from text using a single comprehensive pattern."""
        # Single pattern to catch Finnish dishes with optional dietary codes
        pattern = r"([A-ZÄÖÅ][a-zäöå\s-]{8,60}(?:\([LMVEG, ]+\))?)"
        dishes = re.findall(pattern, text)

        return [dish.strip() for dish in dishes if self._is_valid_dish(dish)]

    def _is_valid_dish(self, dish: str) -> bool:
        """Check if a dish is valid and should be included."""
        dish = dish.strip()

        # Basic length and content checks
        if len(dish) < 8:
            return False

        # Exclude unwanted items
        exclude_patterns = [
            r"^\d+[,.]?\d*\s*€",  # Prices
            r"^(Buffantai|Lasten|Alle|Lounas:|Pizzavalikoima)",
            r"(salaatti- ja leipäpöytä|ruokajuomat ja kahvi)",
        ]

        for pattern in exclude_patterns:
            if re.search(pattern, dish, re.IGNORECASE):
                return False

        return True

    def _deduplicate_dishes(self, dishes: List[str]) -> List[str]:
        """Remove duplicate dishes using similarity checking."""
        unique_dishes = []

        for dish in dishes:
            # Clean the dish
            cleaned = re.sub(r"^[•\-\*]\s*", "", dish)  # Remove bullets
            cleaned = re.sub(r"\s+", " ", cleaned).strip()  # Normalize whitespace
            cleaned = cleaned.replace("€", "").strip()  # Remove euro signs

            if not cleaned or len(cleaned) < 8:
                continue

            # Check for similarity with existing dishes
            is_duplicate = any(
                self._dishes_similar(cleaned, existing) for existing in unique_dishes
            )

            if not is_duplicate:
                unique_dishes.append(cleaned)

        return unique_dishes

    def _dishes_similar(self, dish1: str, dish2: str) -> bool:
        """Check if two dishes are similar enough to be considered duplicates."""
        # Remove dietary codes and normalize
        clean1 = re.sub(r"\([LMVEG, ]+\)", "", dish1).strip().lower()
        clean2 = re.sub(r"\([LMVEG, ]+\)", "", dish2).strip().lower()

        # Check substring containment
        if clean1 in clean2 or clean2 in clean1:
            return True

        # Check word overlap (70% threshold)
        words1 = set(clean1.split())
        words2 = set(clean2.split())

        if not words1 or not words2:
            return False

        overlap = len(words1.intersection(words2))
        similarity = overlap / max(len(words1), len(words2))

        return similarity > 0.7

    def _find_day_boundaries(
        self, full_text: str, day: str, weekdays: List[str]
    ) -> tuple:
        """Find start and end positions for a day's content."""
        day_start = full_text.find(day)
        day_end = len(full_text)

        # Find next day to limit section
        for other_day in weekdays:
            if other_day != day:
                next_start = full_text.find(other_day, day_start + 1)
                if next_start != -1 and next_start < day_end:
                    day_end = next_start

        return day_start, day_end

    def _process_day_content(
        self, day: str, full_text: str, weekdays: List[str]
    ) -> List[str]:
        """Process content for a single day and return unique dishes."""
        if day not in full_text:
            return []

        day_start, day_end = self._find_day_boundaries(full_text, day, weekdays)
        day_content = full_text[day_start:day_end]

        # Skip if no substantial content
        if len(day_content) < 100:
            return []

        # Extract and process dishes
        raw_dishes = self._extract_dishes(day_content)
        unique_dishes = self._deduplicate_dishes(raw_dishes)

        return unique_dishes[:4] if unique_dishes else []  # Limit to 4 items

    def scrape_menu(self) -> Dict[str, List[str]]:
        """Scrape the lunch menu from Pizza Buffa Raflaamo website."""
        soup = self.get_page_content()
        if not soup:
            return {}

        try:
            full_text = soup.get_text()
            menu = {}
            weekdays = ["Maanantai", "Tiistai", "Keskiviikko", "Torstai", "Perjantai"]

            for day in weekdays:
                dishes = self._process_day_content(day, full_text, weekdays)
                if dishes:
                    menu[day] = dishes

            from .base import logging

            logging.info(
                f"Successfully extracted menu for {len(menu)} days from {self.name}"
            )
            return menu

        except Exception as e:
            from .base import logging

            logging.error(f"Error parsing {self.name} menu: {e}")
            return {}
