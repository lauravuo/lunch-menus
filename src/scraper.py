#!/usr/bin/env python3
import os
import sys
import logging
from typing import List

# Import restaurant scrapers
from restaurants.kahvila_epila import KahvilaEpila
from restaurants.kontukeittio import KontukeittioNokia
from restaurants.nokian_kartano import NokianKartano

# Import Telegram bot
from telegram_bot import TelegramBot


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def get_restaurants():
    """Get list of restaurant scrapers."""
    return [KahvilaEpila(), KontukeittioNokia(), NokianKartano()]


def scrape_all_menus(restaurants) -> List[str]:
    """Scrape menus from all restaurants and return formatted strings."""
    formatted_menus = []

    for restaurant in restaurants:
        try:
            logging.info(f"Scraping menu from {restaurant.name}")
            formatted_menu = restaurant.get_formatted_menu()
            formatted_menus.append(formatted_menu)
            logging.info(f"Successfully scraped {restaurant.name}")
        except Exception as e:
            logging.error(f"Failed to scrape {restaurant.name}: {e}")
            # Add error message to maintain consistent output
            formatted_menus.append(f"❌ {restaurant.name}: Error scraping menu")

    return formatted_menus


def main():
    """Main function to orchestrate the scraping and posting process."""
    setup_logging()

    # Check environment variables
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        logging.error("TELEGRAM_BOT_TOKEN environment variable is required")
        return False

    if not os.getenv("TELEGRAM_CHANNEL_ID"):
        logging.error("TELEGRAM_CHANNEL_ID environment variable is required")
        return False

    try:
        # Get restaurant scrapers
        restaurants = get_restaurants()
        logging.info(f"Initialized {len(restaurants)} restaurant scrapers")

        # Scrape all menus
        formatted_menus = scrape_all_menus(restaurants)
        logging.info(f"Scraped {len(formatted_menus)} menus")

        # Post to Telegram
        telegram_bot = TelegramBot()
        success = telegram_bot.post_lunch_menus_sync(formatted_menus)

        if success:
            logging.info("Successfully posted all menus to Telegram")
        else:
            logging.error("Failed to post some menus to Telegram")

        return success

    except Exception as e:
        logging.error(f"Unexpected error in main: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
