"""
Base restaurant class for lunch menu scraping.
All restaurant scrapers should inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime


class BaseRestaurant(ABC):
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            }
        )

    def get_page_content(self) -> Optional[BeautifulSoup]:
        """Fetch and parse the restaurant's webpage."""
        try:
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            logging.error(f"Failed to fetch {self.name}: {e}")
            return None

    @abstractmethod
    def scrape_menu(self) -> Dict[str, List[str]]:
        """Scrape the lunch menu from the restaurant's website."""
        pass

    def get_current_day_menu(self) -> str:
        """Get only the current day's menu, or Monday's if it's the weekend."""
        menu = self.scrape_menu()
        if not menu:
            return f"❌ {self.name}: Unable to fetch menu"

        # Get current day name in Finnish
        current_date = datetime.now()
        weekday = current_date.weekday()  # 0=Monday, 6=Sunday

        # If it's weekend (Saturday=5, Sunday=6), use Monday
        if weekday >= 5:  # Saturday or Sunday
            target_day = "Maanantai"
        else:
            # Map weekday to Finnish day names
            day_names = ["Maanantai", "Tiistai", "Keskiviikko", "Torstai", "Perjantai"]
            target_day = day_names[weekday]

        # Get the menu for the target day
        if target_day in menu and menu[target_day]:
            formatted = f"🍽️ **{self.name}**\n"
            formatted += f"📅 **{target_day}**\n"
            for item in menu[target_day]:
                formatted += f"• {item}\n"
            return formatted
        else:
            return f"❌ {self.name}: No menu available for {target_day}"

    def get_formatted_menu(self) -> str:
        """Get a formatted string representation of the lunch menu."""
        menu = self.scrape_menu()
        if not menu:
            return f"❌ {self.name}: Unable to fetch menu"

        formatted = f"🍽️ **{self.name}**\n"
        for day, items in menu.items():
            if items:
                formatted += f"\n📅 **{day}**\n"
                for item in items:
                    formatted += f"• {item}\n"
            else:
                formatted += f"\n📅 **{day}**: No menu available\n"

        return formatted
