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

    def _get_target_day(self) -> str:
        """Get the target day name for the menu header."""
        from datetime import datetime

        current_date = datetime.now()
        weekday = current_date.weekday()
        day_names = ["Maanantai", "Tiistai", "Keskiviikko", "Torstai", "Perjantai"]

        if weekday >= 5:  # Weekend
            return "Maanantai (seuraavana viikkona)"
        else:
            return day_names[weekday]

    def _clean_restaurant_name(self, restaurant_line: str) -> str:
        """Clean and format restaurant name from menu line."""
        restaurant_name = restaurant_line.replace("🍽️", "").strip()
        # Remove common markdown bold markers if present
        if restaurant_name.startswith("**") and restaurant_name.endswith("**"):
            restaurant_name = restaurant_name.strip("*")
        return restaurant_name.replace("**", "").strip()

    def _format_menu_content(self, lines: List[str]) -> str:
        """Format menu content lines into HTML."""
        content = ""
        for line in lines[1:]:  # Skip first line (restaurant name)
            if line.strip() and not line.strip().startswith("📅"):
                content += f"{html_escape(line)}\n"
        return content

    def _format_single_menu(self, menu: str) -> str:
        """Format a single restaurant menu."""
        if menu.startswith("❌"):
            return f"<b>{html_escape(menu)}</b>\n\n"

        lines = menu.split("\n")
        if not lines:
            return f"{html_escape(menu)}\n\n"

        restaurant_line = lines[0]
        if restaurant_line.startswith("🍽️"):
            restaurant_name = self._clean_restaurant_name(restaurant_line)
            content = f"🍽️ <b>{html_escape(restaurant_name)}</b>\n"
            content += self._format_menu_content(lines)
            content += "\n"  # Add spacing between restaurants
            return content
        else:
            return f"{html_escape(menu)}\n\n"

    def format_combined_menu_message(self, menus: List[str]) -> str:
        """Format all restaurant menus into a single, well-formatted HTML message."""
        if not menus:
            return html_escape("❌ No menus available today")

        from datetime import datetime

        target_day = self._get_target_day()
        current_date = datetime.now()

        # Create the header
        message = f"🍽️ <b>{html_escape('Lounaslista - ' + target_day)}</b>\n"
        message += f"📅 {current_date.strftime('%d.%m.%Y')}\n"
        message += "=" * 40 + "\n\n"

        # Add each restaurant's menu
        for menu in menus:
            message += self._format_single_menu(menu)

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

    def _find_break_point(self, text: str, max_length: int) -> int:
        """Find optimal break point for splitting text."""
        break_point = max_length
        while break_point > 0 and text[break_point] != " ":
            break_point -= 1
        return max_length if break_point == 0 else break_point

    def _split_long_line(self, line: str, max_length: int) -> List[str]:
        """Split a single long line into multiple parts."""
        parts = []
        remaining = line
        while len(remaining) > max_length:
            break_point = self._find_break_point(remaining, max_length)
            parts.append(remaining[:break_point].rstrip())
            remaining = remaining[break_point:].lstrip()
        if remaining.strip():
            parts.append(remaining)
        return parts

    def split_message(self, message: str, max_length: int = 4000) -> List[str]:
        """Split a long message into smaller chunks that fit Telegram's limits."""
        if len(message) <= max_length:
            return [message]

        parts = []
        lines = message.split("\n")
        current_part = ""

        for line in lines:
            test_part = current_part + line + "\n" if current_part else line + "\n"

            if len(test_part) > max_length and current_part:
                parts.append(current_part.rstrip())
                current_part = line + "\n"
            else:
                current_part = test_part

            # Handle very long single lines
            if len(current_part) > max_length:
                line_parts = self._split_long_line(current_part.rstrip(), max_length)
                parts.extend(line_parts[:-1])
                current_part = line_parts[-1] + "\n" if line_parts else ""

        if current_part.strip():
            parts.append(current_part.rstrip())

        return parts

    async def post_current_day_menus(self, menus: List[str]) -> bool:
        """Post current day's lunch menus, splitting into multiple messages."""
        if not menus:
            logging.warning("No menus to post")
            return True

        try:
            # Format all menus into one message
            combined_message = self.format_combined_menu_message(menus)

            # Split message if it's too long
            message_parts = self.split_message(combined_message)

            # Post all message parts
            all_success = True
            for i, part in enumerate(message_parts):
                success = await self.post_message(part)
                if success:
                    logging.info(
                        f"Successfully posted message part {i+1}/{len(message_parts)}"
                    )
                else:
                    logging.error(
                        f"Failed to post message part {i+1}/{len(message_parts)}"
                    )
                    all_success = False

            if all_success:
                logging.info(
                    f"Successfully posted all menu messages "
                    f"({len(message_parts)} parts, {len(menus)} restaurants)"
                )
            else:
                logging.error("Failed to post some menu message parts")

            return all_success

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
