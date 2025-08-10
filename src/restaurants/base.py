"""
Base restaurant class for lunch menu scraping.
All restaurant scrapers should inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
import logging


class BaseRestaurant(ABC):
    """Base class for restaurant menu scrapers."""
    
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_page_content(self) -> Optional[BeautifulSoup]:
        """Fetch and parse the restaurant's webpage."""
        try:
            response = self.session.get(self.url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logging.error(f"Failed to fetch {self.name} page: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error fetching {self.name} page: {e}")
            return None
    
    @abstractmethod
    def scrape_menu(self) -> Dict[str, List[str]]:
        """
        Scrape the lunch menu from the restaurant's website.
        
        Returns:
            Dict with day names as keys and lists of menu items as values.
            Example: {'Monday': ['Soup', 'Main dish'], 'Tuesday': ['Another soup', 'Another main']}
        """
        pass
    
    def get_formatted_menu(self) -> str:
        """Get a formatted string representation of the menu."""
        menu_data = self.scrape_menu()
        if not menu_data:
            return f"❌ Unable to fetch menu from {self.name}"
        
        formatted = f"🍽️ **{self.name}**\n"
        formatted += f"📍 {self.url}\n\n"
        
        for day, items in menu_data.items():
            if items:
                formatted += f"**{day}:**\n"
                for item in items:
                    formatted += f"• {item}\n"
                formatted += "\n"
        
        return formatted
    
    def __str__(self) -> str:
        return f"{self.name} ({self.url})"
