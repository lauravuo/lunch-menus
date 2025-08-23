#!/usr/bin/env python3
"""
Test script for Telegram bot functionality, including message splitting.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from telegram_bot import TelegramBot


class TestTelegramBot(unittest.TestCase):
    """Test cases for TelegramBot functionality."""

    def setUp(self):
        """Set up test environment."""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'TELEGRAM_BOT_TOKEN': 'test_token_123',
            'TELEGRAM_CHANNEL_ID': 'test_channel_456'
        })
        self.env_patcher.start()
        
        # Mock the Bot import to avoid requiring telegram library in tests
        with patch('telegram_bot.Bot'):
            self.bot = TelegramBot()

    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()

    def test_split_message_short_message(self):
        """Test that short messages are not split."""
        short_message = "🍽️ Test Restaurant\n📅 Maanantai\n• Test menu item"
        parts = self.bot.split_message(short_message)
        
        self.assertEqual(len(parts), 1)
        self.assertEqual(parts[0], short_message)

    def test_split_message_long_message(self):
        """Test that long messages are properly split."""
        # Create a message that exceeds the limit
        long_message = "🍽️ Test Restaurant\n📅 Maanantai\n" + "• Very long menu item " * 200
        parts = self.bot.split_message(long_message, max_length=1000)
        
        # Should be split into multiple parts
        self.assertGreater(len(parts), 1)
        
        # Each part should be within the limit
        for part in parts:
            self.assertLessEqual(len(part), 1000)

    def test_split_message_preserves_content(self):
        """Test that splitting preserves all content."""
        original_message = "Line 1\nLine 2\nLine 3\n" + "Long content " * 100
        parts = self.bot.split_message(original_message, max_length=500)
        
        # Reconstruct the message from parts
        reconstructed = "\n".join(parts)
        
        # Should contain all original words (allowing for whitespace differences)
        original_words = original_message.split()
        reconstructed_words = reconstructed.split()
        
        self.assertEqual(len(original_words), len(reconstructed_words))

    def test_split_message_empty_input(self):
        """Test handling of empty input."""
        parts = self.bot.split_message("")
        self.assertEqual(len(parts), 1)
        self.assertEqual(parts[0], "")

    def test_split_message_exact_limit(self):
        """Test message that is exactly at the limit."""
        # Create message that is exactly 1000 characters
        message = "a" * 1000
        parts = self.bot.split_message(message, max_length=1000)
        
        self.assertEqual(len(parts), 1)
        self.assertEqual(len(parts[0]), 1000)

    def test_split_message_one_char_over_limit(self):
        """Test message that is one character over the limit."""
        # Create message that is 1001 characters
        message = "a" * 1001
        parts = self.bot.split_message(message, max_length=1000)
        
        self.assertGreater(len(parts), 1)
        for part in parts:
            self.assertLessEqual(len(part), 1000)

    def test_format_combined_menu_message(self):
        """Test formatting of combined menu messages."""
        test_menus = [
            "🍽️ **Restaurant 1**\n📅 **Maanantai**\n• Menu item 1\n• Menu item 2",
            "🍽️ **Restaurant 2**\n📅 **Maanantai**\n• Menu item 3\n• Menu item 4"
        ]
        
        formatted = self.bot.format_combined_menu_message(test_menus)
        
        # Should contain restaurant names
        self.assertIn("Restaurant 1", formatted)
        self.assertIn("Restaurant 2", formatted)
        
        # Should contain menu items
        self.assertIn("Menu item 1", formatted)
        self.assertIn("Menu item 4", formatted)
        
        # Should have proper HTML formatting
        self.assertIn("<b>", formatted)

    def test_format_combined_menu_message_empty(self):
        """Test formatting with empty menu list."""
        formatted = self.bot.format_combined_menu_message([])
        self.assertIn("No menus available", formatted)

    def test_format_combined_menu_message_with_errors(self):
        """Test formatting with error messages."""
        test_menus = [
            "🍽️ **Restaurant 1**\n📅 **Maanantai**\n• Menu item 1",
            "❌ Restaurant 2: Error scraping menu"
        ]
        
        formatted = self.bot.format_combined_menu_message(test_menus)
        
        # Should contain both successful and error messages
        self.assertIn("Restaurant 1", formatted)
        self.assertIn("Error scraping menu", formatted)

    def test_post_current_day_menus_sync_wrapper(self):
        """Test the synchronous wrapper for posting menus."""
        with patch('telegram_bot.TelegramBot.post_current_day_menus') as mock_async:
            mock_async.return_value = True
            
            test_menus = ["🍽️ **Restaurant 1**\n📅 **Maanantai**\n• Short menu"]
            
            # Test that sync wrapper calls the async method
            with patch('asyncio.get_event_loop') as mock_loop:
                mock_event_loop = Mock()
                mock_loop.return_value = mock_event_loop
                mock_event_loop.run_until_complete.return_value = True
                
                result = self.bot.post_current_day_menus_sync(test_menus)
                
                self.assertTrue(result)
                mock_event_loop.run_until_complete.assert_called_once()

    def test_message_splitting_integration(self):
        """Integration test for message splitting with realistic menu data."""
        # Simulate realistic restaurant menus that might cause length issues
        realistic_menus = [
            "🍽️ **Kahvila Epilä**\n📅 **Maanantai**\n• Lohikeitto leivän kera\n• Broileriwok riisillä\n• Kasvisbolognese pastalla\n• Salaattibuffet",
            "🍽️ **Kontukeittiö Nokia**\n📅 **Maanantai**\n• Jauhelihakastike perunoiden kera\n• Kalapuikot ranskalaisilla\n• Vegaaninen currywok\n• Salaattipöytä",
            "🍽️ **Nokian Kartano (FoodCo)**\n📅 **Maanantai**\n• Naudanlihagratiini\n• Kalakeitto\n• Falafel-wrap\n• Päivän salaatti\n• Jälkiruoka",
            "🍽️ **Pizza Buffa ABC Kolmenkulma**\n📅 **Maanantai**\n• Margherita pizza\n• Pepperoni pizza\n• Vegaaninen pizza\n• Salaattibuffet\n• Jäätelöannos"
        ]
        
        # Format combined message
        combined = self.bot.format_combined_menu_message(realistic_menus)
        
        # Test splitting
        parts = self.bot.split_message(combined, max_length=2000)
        
        # Should handle realistic data appropriately
        for part in parts:
            self.assertLessEqual(len(part), 2000)
            
        # Should preserve restaurant information
        all_content = " ".join(parts)
        self.assertIn("Kahvila Epilä", all_content)
        self.assertIn("Nokian Kartano", all_content)

    def test_telegram_bot_initialization_missing_token(self):
        """Test that initialization fails without bot token."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                TelegramBot()
            self.assertIn("TELEGRAM_BOT_TOKEN", str(context.exception))

    def test_telegram_bot_initialization_missing_channel(self):
        """Test that initialization fails without channel ID."""
        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'test'}, clear=True):
            with self.assertRaises(ValueError) as context:
                TelegramBot()
            self.assertIn("TELEGRAM_CHANNEL_ID", str(context.exception))


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
