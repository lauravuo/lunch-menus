"""
Telegram bot integration for posting lunch menus.
"""

import os
import logging
import asyncio
from typing import List
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

    async def post_message(self, message: str) -> bool:
        """Post a message to the configured Telegram channel."""
        try:
            await self.bot.send_message(
                chat_id=self.channel_id, text=message, parse_mode="Markdown"
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

    async def post_lunch_menus(self, menus: List[str]) -> bool:
        """Post multiple lunch menus with a delay between them."""
        if not menus:
            logging.warning("No menus to post")
            return True

        success_count = 0
        for i, menu in enumerate(menus):
            if await self.post_message(menu):
                success_count += 1

            # Add delay between posts to avoid rate limiting
            if i < len(menus) - 1:
                await asyncio.sleep(1)

        logging.info(f"Posted {success_count}/{len(menus)} menus successfully")
        return success_count == len(menus)

    def post_lunch_menus_sync(self, menus: List[str]) -> bool:
        """Synchronous wrapper for post_lunch_menus."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.post_lunch_menus(menus))
