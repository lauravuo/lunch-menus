# Deployment Guide

This guide will help you deploy the Lunch Menu Scraper to GitHub and set up automated daily scraping.

## Prerequisites

- GitHub account
- Python 3.8+ installed locally
- Telegram account

## Step 1: Set Up Telegram Bot

1. **Create a Telegram Bot:**
   - Open Telegram and search for [@BotFather](https://t.me/botfather)
   - Send `/newbot` command
   - Follow the instructions to create your bot
   - Save the bot token (you'll need this later)

2. **Create a Telegram Channel:**
   - In Telegram, tap the menu button (☰) → "New Channel"
   - Give it a name (e.g., "Lunch Menus")
   - Make it public or private (your choice)
   - Save the channel username (e.g., `@lunchmenus`)

3. **Add Bot to Channel:**
   - In your channel, tap the channel name at the top
   - Tap "Administrators" → "Add Admin"
   - Search for your bot username and add it
   - Give it permission to post messages

4. **Get Channel ID:**
   - For public channels: Use `@channelname` (e.g., `@lunchmenus`)
   - For private channels: Use the numeric ID (e.g., `-1001234567890`)
   - You can get the numeric ID by forwarding a message from your channel to [@userinfobot](https://t.me/userinfobot)

## Step 2: Push to GitHub

1. **Initialize Git Repository (if not already done):**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Lunch Menu Scraper"
   ```

2. **Create GitHub Repository:**
   - Go to [GitHub](https://github.com) and click "New repository"
   - Name it `lunch-menus` (or your preferred name)
   - Make it public or private
   - Don't initialize with README (we already have one)
   - Click "Create repository"

3. **Push to GitHub:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/lunch-menus.git
   git branch -M main
   git push -u origin main
   ```

## Step 3: Configure GitHub Secrets

1. **Go to Repository Settings:**
   - In your GitHub repository, click "Settings" tab
   - Click "Secrets and variables" → "Actions" in the left sidebar

2. **Add Required Secrets:**
   - Click "New repository secret"
   - Add `TELEGRAM_BOT_TOKEN` with your bot token
   - Click "New repository secret" again
   - Add `TELEGRAM_CHANNEL_ID` with your channel ID

## Step 4: Test the Setup

1. **Test Locally (Optional):**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Set environment variables
   export TELEGRAM_BOT_TOKEN="your_bot_token"
   export TELEGRAM_CHANNEL_ID="your_channel_id"
   
   # Test scrapers
   python test_scrapers.py
   
   # Test main scraper
   python src/scraper.py
   ```

2. **Test GitHub Actions:**
   - Go to "Actions" tab in your repository
   - Click "Daily Lunch Menu Scrape" workflow
   - Click "Run workflow" → "Run workflow"
   - Monitor the execution

## Step 5: Verify Automation

1. **Check Schedule:**
   - The workflow runs every weekday at 7:30 AM UTC (10:30 AM Finnish time)
   - You can modify the schedule in `.github/workflows/daily-scrape.yml`

2. **Monitor Execution:**
   - Check the "Actions" tab daily to see if the workflow ran
   - Check your Telegram channel for new menu posts
   - Check the workflow logs if something fails

## Troubleshooting

### Common Issues

1. **GitHub Actions Not Running:**
   - Check if the workflow file is in `.github/workflows/`
   - Verify the cron schedule syntax
   - Check repository permissions

2. **Telegram Bot Not Working:**
   - Verify bot token in GitHub secrets
   - Check channel ID format
   - Ensure bot has permission to post in channel

3. **Scraping Fails:**
   - Restaurant websites may have changed structure
   - Check workflow logs for specific errors
   - Some sites may block automated requests

### Debug Mode

To enable debug logging, modify the workflow file:
```yaml
- name: Run lunch menu scraper
  env:
    TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
    TELEGRAM_CHANNEL_ID: ${{ secrets.TELEGRAM_CHANNEL_ID }}
    DEBUG: "true"
  run: |
    python src/scraper.py
```

## Customization

### Adding New Restaurants

1. Create a new scraper class in `src/restaurants/`
2. Inherit from `BaseRestaurant`
3. Implement the `scrape_menu()` method
4. Add the restaurant to `src/scraper.py`

### Changing Schedule

Edit `.github/workflows/daily-scrape.yml`:
```yaml
schedule:
  # Run every weekday at 7:30 AM UTC (10:30 AM Finnish time)
  - cron: '30 7 * * 1-5'
```

### Multiple Channels

To post to multiple channels, modify the Telegram bot to loop through multiple channel IDs.

## Support

If you encounter issues:
1. Check the workflow logs in GitHub Actions
2. Verify your configuration
3. Test locally first
4. Check if restaurant websites have changed

## Security Notes

- Never commit your bot token to the repository
- Use GitHub Secrets for sensitive information
- Regularly rotate your bot token if needed
- Monitor your bot's usage and permissions
