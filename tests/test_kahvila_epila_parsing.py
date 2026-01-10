import unittest
from unittest.mock import MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from restaurants.kahvila_epila import KahvilaEpila

class TestKahvilaEpilaParsing(unittest.TestCase):
    def setUp(self):
        self.scraper = KahvilaEpila()

    def test_friday_spam_filtering(self):
        """Test that the regex fallback correctly excludes footer spam on Fridays."""
        mock_text = """
        Viikko 2
        Maanantai:
        - Ruoka 1
        Tiistai:
        - Ruoka 2
        Keskiviikko:
        - Ruoka 3
        Torstai:
        - Ruoka 4
        Perjantai:
        Pinaattikeitto (L, G)
        Possunleike (L)
        Broileripasta (L)
        Lounas 12,50 €, keittolounas 10 €. Keitto-ja lounas sisältävät runsaan salaattipöydän.
        Lounas myös mukaan! Kiireisen päivän pelastaa...
        Kahvila Epilä
        Aukioloajat
        MA - PE: 08:00 - 15:00
        Seuraa meitä Facebookissa
        """
        
        mock_soup = MagicMock()
        # Ensure structured parsing fails so it falls back to regex
        mock_soup.find_all.return_value = [] 
        mock_soup.get_text.return_value = mock_text

        menu = self.scraper._extract_menu_with_regex(mock_soup)
        
        self.assertIn("Perjantai", menu)
        friday_items = menu["Perjantai"]
        
        # Verify valid items are present
        self.assertIn("Pinaattikeitto (L, G)", friday_items)
        self.assertIn("Possunleike (L)", friday_items)
        self.assertIn("Broileripasta (L)", friday_items)
        
        # Verify spam is NOT present
        full_text = " ".join(friday_items)
        self.assertNotIn("Lounas 12,50", full_text, "Should expect price info to be excluded")
        self.assertNotIn("Aukioloajat", full_text, "Should expect opening hours to be excluded")
        self.assertNotIn("Kahvila Epilä", full_text, "Should expect restaurant name to be excluded")

if __name__ == '__main__':
    unittest.main()
