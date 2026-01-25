# Internship Finder Bot

An automated Telegram bot that scrapes internship listings and posts them to a channel.

## Features
- **Automated Scraping**: Fetches internships from target websites.
- **Telegram Integration**: Posts new findings to a specified channel.
- **De-duplication**: Tracks history to avoid reposting the same internship.
- **GitHub Actions**: Runs on a schedule entirely within GitHub Actions.

## Setup
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Set environment variables: `BOT_TOKEN`, `CHANNEL_ID`.
4. Run: `python src/main.py`
