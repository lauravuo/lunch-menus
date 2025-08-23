# Lunch Menu Scraper

Automated lunch menu scraper that fetches daily menus from selected restaurants and posts them to a Telegram channel using GitHub Actions.

## Features

- **Automated scraping** of lunch menus from multiple restaurants
- **Scheduled updates** via GitHub Actions (runs daily at 7:30 AM UTC / 10:30 AM Finnish time)
- **Telegram integration** for automatic posting with intelligent message splitting
- **Multiple restaurant support** with extensible architecture
- **Robust error handling** and comprehensive test coverage

## Supported Restaurants

1. **Kahvila Epilä** - [https://www.kahvilaepila.com/lounaslista/](https://www.kahvilaepila.com/lounaslista/)
2. **Kontukeittiö Nokia** - [https://kontukoti.fi/kontukeittio/kontukeittio-nokia/](https://kontukoti.fi/kontukeittio/kontukeittio-nokia/)
3. **Nokian Kartano (FoodCo)** - [https://www.compass-group.fi/ravintolat-ja-ruokalistat/foodco/kaupungit/nokia/nokian-kartano/](https://www.compass-group.fi/ravintolat-ja-ruokalistat/foodco/kaupungit/nokia/nokian-kartano/)
4. **Pizza Buffa ABC Kolmenkulma** - [https://www.raflaamo.fi/fi/abc-kolmenkulma](https://www.raflaamo.fi/fi/abc-kolmenkulma)

## Setup

### Prerequisites

- Python 3.8+
- GitHub repository
- Telegram bot token and channel ID

### Configuration

1. **Fork or clone this repository**
2. **Set up Telegram Bot:**
   - Create a bot via [@BotFather](https://t.me/botfather)
   - Get your bot token
   - Add the bot to your target channel
   - Get the channel ID (e.g., `@channelname` or `-1001234567890`)

3. **Configure GitHub Secrets:**
   - Go to your repository Settings → Secrets and variables → Actions
   - Add the following secrets:
     - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
     - `TELEGRAM_CHANNEL_ID`: Your target channel ID

### Installation

```bash
pip install -r requirements.txt
```

## Usage

### Manual Run

```bash
python src/scraper.py
```

### Automated Run

The scraper runs automatically via GitHub Actions every weekday at 7:30 AM UTC (10:30 AM Finnish time).

### Testing

```bash
# Run the test suite
python test_scrapers.py

# Test current day menu functionality
python test_current_day.py

# Test Telegram bot functionality (including message splitting)
python test_telegram_bot.py

# Run with pytest (recommended)
pytest test_scrapers.py -v
pytest test_telegram_bot.py -v

# Run all tests
pytest -v

# Check code quality
flake8 src/
black --check src/

# Validate GitHub Actions workflows (optional)
curl -sSfL https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download.sh | sh -s -- -b .
./actionlint -color
```

## Project Structure

```
├── .github/
│   └── workflows/
│       ├── daily-scrape.yml      # Daily scraping workflow
│       └── test-pr.yml           # PR validation workflow
├── src/
│   ├── scraper.py               # Main scraping logic
│   ├── restaurants/
│   │   ├── __init__.py
│   │   ├── base.py              # Base restaurant class
│   │   ├── kahvila_epila.py     # Kahvila Epilä scraper
│   │   ├── kontukeittio.py      # Kontukeittiö Nokia scraper
│   │   └── nokian_kartano.py    # Nokian Kartano scraper
│   └── telegram_bot.py          # Telegram posting logic
├── requirements.txt              # Python dependencies
├── test_scrapers.py             # Restaurant scraper tests
├── test_current_day.py          # Current day menu functionality test
├── test_telegram_bot.py         # Telegram bot functionality tests
├── .gitignore                   # Git ignore file
└── README.md                    # This file
```

## How It Works

1. **Scheduled Execution**: GitHub Actions runs the scraper daily at 7:30 AM UTC (10:30 AM Finnish time)
2. **Menu Scraping**: Each restaurant's website is scraped for current lunch menus
3. **Data Processing**: Menu data is cleaned and formatted for the current day (or Monday if weekend)
4. **Telegram Posting**: Current day's formatted menu is posted to the configured Telegram channel with automatic message splitting for long content
5. **Error Handling**: Failed scrapes are logged and reported

## CI/CD

### Automated Testing
- **Pull Request Validation**: All PRs are automatically tested before merging
- **Code Quality**: Linting with flake8 and formatting checks with black
- **Import Validation**: Ensures all modules can be imported correctly
- **Telegram Bot Testing**: Message splitting and formatting functionality
- **Workflow Validation**: Verifies GitHub Actions workflow files are valid

### Quality Gates
- Code must pass linting checks
- All imports must be successful
- Scrapers must initialize without errors
- Telegram bot tests must pass (including message splitting)
- Workflow files must be valid YAML

## Customization

### Adding New Restaurants

1. Create a new scraper class in `src/restaurants/`
2. Inherit from `BaseRestaurant`
3. Implement the required methods
4. Add the restaurant to the main scraper

### Modifying Schedule

Edit `.github/workflows/daily-scrape.yml` to change the cron schedule.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Troubleshooting

### Common Issues

- **Telegram Bot Not Working**: Check bot token and channel ID in GitHub secrets
- **Message Too Long Error**: The bot automatically splits long messages, but check logs for any splitting issues
- **Scraping Fails**: Restaurant websites may have changed structure
- **GitHub Actions Not Running**: Check workflow file and repository permissions

### Debug Mode

Set `DEBUG=True` in the scraper to see detailed logging output.
