import unittest
from unittest.mock import MagicMock
import sys
import os
from bs4 import BeautifulSoup

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from restaurants.stahlberg_lielahti import StahlbergLielahti

class TestStahlbergLielahtiParsing(unittest.TestCase):
    def setUp(self):
        self.scraper = StahlbergLielahti()

    def test_menu_parsing(self):
        """Test that the scraper correctly parses the HTML table structure."""
        html_content = """
        <div class="et_pb_module et_pb_text et_pb_text_2  et_pb_text_align_left et_pb_bg_layout_light">
            <div class="et_pb_text_inner">
                <h3>Maanantai 10:30-15:00</h3>
            </div>
        </div>
        <div class="et_pb_module et_pb_code et_pb_code_0">
            <div class="et_pb_code_inner">
                <table id="tablepress-75" class="tablepress tablepress-id-75 ruokalista">
                    <tbody>
                        <tr class="row-1">
                            <td class="column-1">Kermassa haudutettuja kaalikääryleitä (L, G)</td>
                        </tr>
                        <tr class="row-2">
                            <td class="column-1">Appelsiini-chilibroileria (M, G)</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        <div class="et_pb_module et_pb_text et_pb_text_3">
            <div class="et_pb_text_inner">
                <h3>Tiistai 10:30-15:00</h3>
            </div>
        </div>
        <table class="ruokalista">
            <tbody>
                <tr class="row-1">
                    <td class="column-1">Sitruunaista uunilohta (L, G)</td>
                </tr>
            </tbody>
        </table>
        """
        
        # Mock get_page_content to return our test HTML
        self.scraper.get_page_content = MagicMock(return_value=BeautifulSoup(html_content, "html.parser"))

        menu = self.scraper.scrape_menu()
        
        self.assertIn("Maanantai", menu)
        self.assertIn("Tiistai", menu)
        
        self.assertEqual(len(menu["Maanantai"]), 2)
        self.assertEqual(menu["Maanantai"][0], "Kermassa haudutettuja kaalikääryleitä (L, G)")
        self.assertEqual(menu["Maanantai"][1], "Appelsiini-chilibroileria (M, G)")
        
        self.assertEqual(len(menu["Tiistai"]), 1)
        self.assertEqual(menu["Tiistai"][0], "Sitruunaista uunilohta (L, G)")

if __name__ == '__main__':
    unittest.main()
