#!/usr/bin/env python3
"""
Main lunch menu scraper script.
Scrapes menus from multiple restaurants and posts them to Telegram.
"""

import os
import sys
import logging
from datetime import datetime
from typing import List
import traceback

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from restaurants.kahvila_epila import KahvilaEpila
from restaurants.kontukeittio import KontukeittioNokia
from restaurants.nokian_kartano import NokianKartano
from telegram_bot import TelegramBot


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('lunch_scraper.log')
        ]
    )


def get_restaurants():
    """Get list of restaurant scrapers."""
    return [
        KahvilaEpila(),
        KontukeittioNokia(),
        NokianKartano()
    ]


def scrape_all_menus(restaurants) -> List[str]:
    """
    Scrape menus from all restaurants.
    
    Args:
        restaurants: List of restaurant scraper instances
        
    Returns:
        List of formatted menu strings
    """
    menus = []
    
    for restaurant in restaurants:
        try:
            logging.info(f"Scraping menu from {restaurant.name}")
            menu_text = restaurant.get_formatted_menu()
            
            if menu_text and not menu_text.startswith("❌"):
                menus.append(menu_text)
                logging.info(f"Successfully scraped menu from {restaurant.name}")
            else:
                logging.warning(f"Failed to get menu from {restaurant.name}")
                
        except Exception as e:
            logging.error(f"Error scraping {restaurant.name}: {e}")
            logging.error(traceback.format_exc())
    
    return menus


def main():
    """Main function to run the lunch menu scraper."""
    setup_logging()
    
    logging.info("Starting lunch menu scraper")
    
    try:
        # Check environment variables
        if not os.getenv('TELEGRAM_BOT_TOKEN'):
            logging.error("TELEGRAM_BOT_TOKEN environment variable not set")
            return False
        
        if not os.getenv('TELEGRAM_CHANNEL_ID'):
            logging.error("TELEGRAM_CHANNEL_ID environment variable not set")
            return False
        
        # Get restaurant scrapers
        restaurants = get_restaurants()
        logging.info(f"Initialized {len(restaurants)} restaurant scrapers")
        
        # Scrape all menus
        menus = scrape_all_menus(restaurants)
        
        if not menus:
            logging.warning("No menus were successfully scraped")
            return False
        
        logging.info(f"Successfully scraped {len(menus)} menus")
        
        # Post to Telegram
        telegram_bot = TelegramBot()
        success = telegram_bot.post_lunch_menus_sync(menus)
        
        if success:
            logging.info("Successfully posted all menus to Telegram")
            return True
        else:
            logging.error("Failed to post some menus to Telegram")
            return False
            
    except Exception as e:
        logging.error(f"Unexpected error in main: {e}")
        logging.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
