"""
Telegram bot integration for posting lunch menus.
"""

import os
import logging
import asyncio
from typing import List
from html import escape as html_escape
from telegram import Bot, error


class TelegramBot:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.channel_id = os.getenv("TELEGRAM_CHANNEL_ID")

        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

        if not self.channel_id:
            raise ValueError("TELEGRAM_CHANNEL_ID environment variable is required")

        self.bot = Bot(token=self.bot_token)

    def format_combined_menu_message(self, menus: List[str]) -> str:
        """Format all restaurant menus into a single, well-formatted HTML message.

        Uses Telegram parse_mode="HTML". All dynamic text is HTML-escaped to avoid
        entity parsing errors.
        """
        if not menus:
            return html_escape("❌ No menus available today")
        
        # Get current date info for the header
        from datetime import datetime
        current_date = datetime.now()
        weekday = current_date.weekday()
        day_names = ["Maanantai", "Tiistai", "Keskiviikko", "Torstai", "Perjantai"]
        
        if weekday >= 5:  # Weekend
            target_day = "Maanantai (seuraavana viikkona)"
        else:
            target_day = day_names[weekday]
        
        # Create the header
        message = f"🍽️ <b>{html_escape('Lounaslista - ' + target_day)}</b>\n"
        message += f"📅 {current_date.strftime('%d.%m.%Y')}\n"
        message += "=" * 40 + "\n\n"
        
        # Add each restaurant's menu
        for i, menu in enumerate(menus):
            if menu.startswith("❌"):
                # Error case - add the error message emphasized
                message += f"<b>{html_escape(menu)}</b>\n\n"
            else:
                # Extract restaurant name and menu content
                lines = menu.split('\n')
                if lines:
                    # First line should be the restaurant name with emoji
                    restaurant_line = lines[0]
                    if restaurant_line.startswith("🍽️"):
                        # Remove the emoji and format the restaurant name
                        restaurant_name = restaurant_line.replace("🍽️", "").strip()
                        # Remove common markdown bold markers if present
                        if restaurant_name.startswith("**") and restaurant_name.endswith("**"):
                            restaurant_name = restaurant_name.strip("*")
                        restaurant_name = restaurant_name.replace("**", "").strip()
                        message += f"🍽️ <b>{html_escape(restaurant_name)}</b>\n"
                        
                        # Add the menu content (skip the first line which is the restaurant name)
                        for line in lines[1:]:
                            if line.strip():  # Only add non-empty lines
                                # Skip weekday lines
                                if not line.strip().startswith("📅"):
                                    message += f"{html_escape(line)}\n"
                        
                        message += "\n"  # Add spacing between restaurants
                    else:
                        # Fallback if format is unexpected
                        message += f"{html_escape(menu)}\n\n"
        
        # Add footer
        message += "=" * 40 + "\n"
        message += html_escape("🕐 Päivitetty automaattisesti")
        
        return message

    async def post_message(self, message: str) -> bool:
        """Post a message to the configured Telegram channel."""
        try:
            await self.bot.send_message(
                chat_id=self.channel_id, text=message, parse_mode="HTML"
            )
            logging.info("Successfully posted message to Telegram channel")
            return True
        except error.TelegramError as e:
            logging.error(f"Telegram API error: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error posting to Telegram: {e}")
            return False

    def post_message_sync(self, message: str) -> bool:
        """Synchronous wrapper for post_message."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.post_message(message))

    async def post_current_day_menus(self, menus: List[str]) -> bool:
        """Post current day's lunch menus as a single, formatted message."""
        if not menus:
            logging.warning("No menus to post")
            return True

        try:
            # Format all menus into one message
            combined_message = self.format_combined_menu_message(menus)
            
            # Post the single, formatted message
            success = await self.post_message(combined_message)
            
            if success:
                logging.info(f"Successfully posted combined menu message with {len(menus)} restaurants")
            else:
                logging.error("Failed to post combined menu message")
            
            return success
            
        except Exception as e:
            logging.error(f"Error formatting or posting combined menu: {e}")
            return False

    def post_current_day_menus_sync(self, menus: List[str]) -> bool:
        """Synchronous wrapper for post_current_day_menus."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.post_current_day_menus(menus))
