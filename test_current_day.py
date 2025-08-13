#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify current day menu functionality.
"""

import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, 'src')

from restaurants.kahvila_epila import KahvilaEpila
from restaurants.kontukeittio import KontukeittioNokia
from restaurants.nokian_kartano import NokianKartano
from restaurants.pizza_buffa import PizzaBuffa


def test_current_day_menu():
    """Test the current day menu functionality."""
    print("🧪 Testing Current Day Menu Functionality")
    print("=" * 50)
    
    # Get current date info
    current_date = datetime.now()
    weekday = current_date.weekday()
    day_names = ["Maanantai", "Tiistai", "Keskiviikko", "Torstai", "Perjantai"]
    
    print("📅 Current date: {}".format(current_date.strftime('%Y-%m-%d')))
    print("📅 Current weekday: {} ({})".format(weekday, day_names[weekday] if weekday < 5 else 'Weekend'))
    
    if weekday >= 5:
        print("📅 Weekend detected - will show Monday's menu")
        target_day = "Maanantai"
    else:
        target_day = day_names[weekday]
    
    print("🎯 Target day: {}".format(target_day))
    print()
    
    # Test each restaurant
    restaurants = [
        KahvilaEpila(),
        KontukeittioNokia(),
        NokianKartano(),
        PizzaBuffa()
    ]
    
    for restaurant in restaurants:
        print("🍽️  Testing {}:".format(restaurant.name))
        try:
            # Test current day menu
            current_menu = restaurant.get_current_day_menu()
            print("✅ Current day menu generated successfully")
            print("📝 Menu preview: {}...".format(current_menu[:200]))
            
            # Test full week menu (for comparison)
            full_menu = restaurant.get_formatted_menu()
            print("📅 Full week menu also available")
            
        except Exception as e:
            print("❌ Error: {}".format(e))
        
        print("-" * 30)
    
    print("🎉 Current day menu test completed!")


if __name__ == "__main__":
    test_current_day_menu()
