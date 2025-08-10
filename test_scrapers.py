#!/usr/bin/env python3
"""
Test script for restaurant scrapers.
Run this to test if the scrapers can fetch menus from the websites.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from restaurants.kahvila_epila import KahvilaEpila
from restaurants.kontukeittio import KontukeittioNokia
from restaurants.nokian_kartano import NokianKartano


def test_restaurant(restaurant_class, name):
    """Test a single restaurant scraper."""
    print(f"\n{'='*50}")
    print(f"Testing {name}")
    print(f"{'='*50}")
    
    try:
        restaurant = restaurant_class()
        print(f"Restaurant: {restaurant.name}")
        print(f"URL: {restaurant.url}")
        
        # Test page fetching
        print("\nTesting page fetch...")
        soup = restaurant.get_page_content()
        if soup:
            print("✅ Page fetched successfully")
            print(f"Page title: {soup.title.string if soup.title else 'No title'}")
        else:
            print("❌ Failed to fetch page")
            return False
        
        # Test menu scraping
        print("\nTesting menu scraping...")
        menu_data = restaurant.scrape_menu()
        if menu_data:
            print("✅ Menu scraped successfully")
            print(f"Found {len(menu_data)} day(s):")
            for day, items in menu_data.items():
                print(f"  {day}: {len(items)} items")
                for item in items[:3]:  # Show first 3 items
                    print(f"    - {item}")
                if len(items) > 3:
                    print(f"    ... and {len(items) - 3} more")
        else:
            print("❌ No menu data found")
            return False
        
        # Test formatted output
        print("\nTesting formatted output...")
        formatted = restaurant.get_formatted_menu()
        if formatted and not formatted.startswith("❌"):
            print("✅ Formatted output generated")
            print("Preview:")
            print(formatted[:200] + "..." if len(formatted) > 200 else formatted)
        else:
            print("❌ Formatted output failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing {name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run tests for all restaurant scrapers."""
    print("Lunch Menu Scraper - Test Suite")
    print("This script tests if the restaurant scrapers can fetch menus from their websites.")
    print("Note: Some websites may block automated requests or have changed their structure.")
    
    restaurants = [
        (KahvilaEpila, "Kahvila Epilä"),
        (KontukeittioNokia, "Kontukeittiö Nokia"),
        (NokianKartano, "Nokian Kartano (FoodCo)")
    ]
    
    results = []
    
    for restaurant_class, name in restaurants:
        success = test_restaurant(restaurant_class, name)
        results.append((name, success))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The scrapers are working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("This might be due to:")
        print("- Website structure changes")
        print("- Anti-bot protection")
        print("- Network issues")
        print("- Missing dependencies")


if __name__ == "__main__":
    main()
