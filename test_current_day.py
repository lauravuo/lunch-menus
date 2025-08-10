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


def test_current_day_menu():
    """Test the current day menu functionality."""
    print("🧪 Testing Current Day Menu Functionality")
    print("=" * 50)
    
    # Get current date info
    current_date = datetime.now()
    weekday = current_date.weekday()
    day_names = ["Maanantai", "Tiistai", "Keskiviikko", "Torstai", "Perjantai"]
    
    print(f"📅 Current date: {current_date.strftime('%Y-%m-%d')}")
    print(f"📅 Current weekday: {weekday} ({day_names[weekday] if weekday < 5 else 'Weekend'})")
    
    if weekday >= 5:
        print("📅 Weekend detected - will show Monday's menu")
        target_day = "Maanantai"
    else:
        target_day = day_names[weekday]
    
    print(f"🎯 Target day: {target_day}")
    print()
    
    # Test each restaurant
    restaurants = [
        KahvilaEpila(),
        KontukeittioNokia(),
        NokianKartano()
    ]
    
    for restaurant in restaurants:
        print(f"🍽️  Testing {restaurant.name}:")
        try:
            # Test current day menu
            current_menu = restaurant.get_current_day_menu()
            print(f"✅ Current day menu generated successfully")
            print(f"📝 Menu preview: {current_menu[:200]}...")
            
            # Test full week menu (for comparison)
            full_menu = restaurant.get_formatted_menu()
            print(f"📅 Full week menu also available")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 30)
    
    print("🎉 Current day menu test completed!")


if __name__ == "__main__":
    test_current_day_menu()
