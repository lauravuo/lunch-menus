#!/usr/bin/env python3
"""
Test script for restaurant scrapers.
Run this to test if the scrapers can fetch menus from the websites.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from restaurants.kahvila_epila import KahvilaEpila
from restaurants.kontukeittio import KontukeittioNokia
from restaurants.nokian_kartano import NokianKartano
from restaurants.pizza_buffa import PizzaBuffa
from restaurants.stahlberg_kolmenkulma import StahlbergKolmenkulma


def test_kahvila_epila():
    """Test Kahvila Epilä scraper."""
    restaurant = KahvilaEpila()
    
    # Test initialization
    assert restaurant.name == "Kahvila Epilä"
    assert "kahvilaepila.com" in restaurant.url
    
    # Test that we can get page content (this will fail for real sites without proper tokens)
    # but we can at least test the structure
    print(f"✅ Initialized: {restaurant.name}")
    print(f"{restaurant.get_formatted_menu()}")

def test_kontukeittio_nokia():
    """Test Kontukeittiö Nokia scraper."""
    restaurant = KontukeittioNokia()
    
    # Test initialization
    assert restaurant.name == "Kontukeittiö Nokia"
    assert "europe-west1-luncher-7cf76.cloudfunctions.net" in restaurant.url
    
    print(f"✅ Initialized: {restaurant.name}")


def test_nokian_kartano():
    """Test Nokian Kartano scraper."""
    restaurant = NokianKartano()
    
    # Test initialization
    assert restaurant.name == "Nokian Kartano (FoodCo)"
    assert "compass-group.fi" in restaurant.url
    
    print(f"✅ Initialized: {restaurant.name}")

    # Test menu scraping
    menu = restaurant.scrape_menu()
    print(f"📋 Found menu for {len(menu)} days")
    assert len(menu) > 0, "Menu should not be empty"
    
    # Test current day menu formatting
    current_menu = restaurant.get_current_day_menu()
    print(f"📅 Current day menu: {len(current_menu)} characters")
    assert "Unable to fetch menu" not in current_menu, "Should successfully format current day menu"


def test_pizza_buffa():
    """Test Pizza Buffa scraper."""
    restaurant = PizzaBuffa()
    
    # Test initialization
    assert restaurant.name == "Pizza Buffa ABC Kolmenkulma"
    assert "raflaamo.fi" in restaurant.url
    
    print(f"✅ Initialized: {restaurant.name}")
    
    # Test menu scraping
    menu = restaurant.scrape_menu()
    print(f"📋 Found menu for {len(menu)} days")
    
    # Test current day menu formatting
    current_menu = restaurant.get_current_day_menu()
    print(f"📅 Current day menu: {len(current_menu)} characters")


def test_stahlberg_kolmenkulma():
    """Test Ståhlberg Kolmenkulma scraper."""
    restaurant = StahlbergKolmenkulma()

    # Test initialization
    assert restaurant.name == "Ståhlberg Kolmenkulma"
    assert "stahlbergkahvilat.fi" in restaurant.url

    print(f"✅ Initialized: {restaurant.name}")
    print(f"{restaurant.get_formatted_menu()}")


def test_base_functionality():
    """Test base restaurant functionality."""
    from restaurants.base import BaseRestaurant
    
    # Test that base class can't be instantiated (it's abstract)
    try:
        BaseRestaurant("Test", "http://test.com")
        assert False, "BaseRestaurant should not be instantiable"
    except TypeError:
        pass  # Expected
    
    print("✅ Base class functionality verified")


if __name__ == "__main__":
    # Run tests manually if not using pytest
    print("Running scraper tests...")
    
    test_kahvila_epila()
    test_kontukeittio_nokia()
    test_nokian_kartano()
    test_pizza_buffa()
    test_stahlberg_kolmenkulma()
    test_base_functionality()
    
    print("\n🎉 All tests passed!")
