#!/bin/bash
set -e

echo "🚀 Running CI checks locally..."

echo "----------------------------------------------------------------------"
echo "📦 Installing dependencies..."
uv sync --frozen

echo "----------------------------------------------------------------------"
echo "🔍 Linting with flake8..."
# Stop the build if there are Python syntax errors or undefined names
uv run flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
# Check all linting rules and fail on violations
uv run flake8 src/ --count --max-complexity=10 --max-line-length=88 --extend-ignore=E203,W503 --statistics

echo "----------------------------------------------------------------------"
echo "🧪 Running scrapers tests..."
uv run pytest tests/test_scrapers.py -v

echo "----------------------------------------------------------------------"
echo "🧪 Testing current day menu functionality..."
uv run tests/test_current_day.py

echo "----------------------------------------------------------------------"
echo "🧪 Testing Telegram bot functionality..."
uv run pytest tests/test_telegram_bot.py -v

echo "----------------------------------------------------------------------"
echo "🧪 Testing Kahvila Epilä parsing..."
uv run pytest tests/test_kahvila_epila_parsing.py -v

echo "----------------------------------------------------------------------"
echo "🔌 Testing scraper imports..."
uv run python -c "
import sys
sys.path.insert(0, 'src')

from restaurants.base import BaseRestaurant
from restaurants.kahvila_epila import KahvilaEpila
from restaurants.kontukeittio import KontukeittioNokia
from restaurants.nokian_kartano import NokianKartano
from telegram_bot import TelegramBot
from scraper import get_restaurants, scrape_all_menus
print('✅ All imports successful')
"

echo "----------------------------------------------------------------------"
echo "🔌 Testing scraper initialization (Dry Run)..."
export TELEGRAM_BOT_TOKEN="test_token"
export TELEGRAM_CHANNEL_ID="test_channel"
uv run python -c "
import sys
sys.path.insert(0, 'src')

from restaurants.kahvila_epila import KahvilaEpila
from restaurants.kontukeittio import KontukeittioNokia
from restaurants.nokian_kartano import NokianKartano

# Test initialization
epila = KahvilaEpila()
kontu = KontukeittioNokia()
kartano = NokianKartano()

print(f'✅ Initialized: {epila.name}, {kontu.name}, {kartano.name}')
print('✅ All scrapers initialized successfully')
"

echo "----------------------------------------------------------------------"
echo "🎨 Checking code formatting with black..."
uv run black --check src/

echo "----------------------------------------------------------------------"
echo "🎉 All checks passed!"
