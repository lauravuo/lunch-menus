"""
Telegram bot integration for posting lunch menus.
"""

import os
import logging
from typing import List, Optional
import asyncio
from telegram import Bot
from telegram.error import TelegramError


class TelegramBot:
    """Telegram bot for posting lunch menus."""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        if not self.channel_id:
            raise ValueError("TELEGRAM_CHANNEL_ID environment variable is required")
        
        self.bot = Bot(token=self.bot_token)
        
    async def post_message(self, message: str) -> bool:
        """
        Post a message to the configured Telegram channel.
        
        Args:
            message: The message to post
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode='Markdown'
            )
            logging.info(f"Successfully posted message to Telegram channel {self.channel_id}")
            return True
            
        except TelegramError as e:
            logging.error(f"Failed to post message to Telegram: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error posting to Telegram: {e}")
            return False
    
    def post_message_sync(self, message: str) -> bool:
        """
        Synchronous wrapper for posting messages.
        
        Args:
            message: The message to post
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.post_message(message))
            loop.close()
            return result
        except Exception as e:
            logging.error(f"Error in sync wrapper: {e}")
            return False
    
    async def post_lunch_menus(self, menus: List[str]) -> bool:
        """
        Post multiple lunch menus to Telegram.
        
        Args:
            menus: List of formatted menu strings
            
        Returns:
            bool: True if all messages were posted successfully
        """
        if not menus:
            logging.warning("No menus to post")
            return False
        
        success_count = 0
        total_count = len(menus)
        
        for menu in menus:
            if await self.post_message(menu):
                success_count += 1
            else:
                logging.error(f"Failed to post menu: {menu[:100]}...")
            
            # Add a small delay between messages to avoid rate limiting
            await asyncio.sleep(1)
        
        logging.info(f"Posted {success_count}/{total_count} menus successfully")
        return success_count == total_count
    
    def post_lunch_menus_sync(self, menus: List[str]) -> bool:
        """
        Synchronous wrapper for posting multiple lunch menus.
        
        Args:
            menus: List of formatted menu strings
            
        Returns:
            bool: True if all messages were posted successfully
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.post_lunch_menus(menus))
            loop.close()
            return result
        except Exception as e:
            logging.error(f"Error in sync wrapper: {e}")
            return False
