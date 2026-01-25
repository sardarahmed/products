
import os
import argparse
import time
import logging
from scraper import InternshalaScraper
from storage import StorageManager
from bot import TelegramBot

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Internship Finder Bot")
    parser.add_argument('--dry-run', action='store_true', help="Run without sending messages or saving history")
    args = parser.parse_args()

    # Load configuration
    bot_token = os.getenv('BOT_TOKEN')
    channel_id = os.getenv('CHANNEL_ID')

    if not args.dry_run and (not bot_token or not channel_id):
        logger.error("BOT_TOKEN and CHANNEL_ID environment variables are required.")
        return

    # Initialize modules
    scraper = InternshalaScraper()
    storage = StorageManager(file_path='history.json')
    bot = TelegramBot(bot_token, channel_id)

    # Scrape
    logger.info("Starting scrape job...")
    internships = scraper.scrape()
    logger.info(f"Scraped {len(internships)} internships.")

    new_count = 0
    for internship in internships:
        link = internship.get('link')
        if not link:
            continue

        if storage.is_new(link):
            new_count += 1
            logger.info(f"New internship found: {internship['title']} at {internship['company']}")
            
            if not args.dry_run:
                message = bot.format_internship(internship)
                bot.send_message(message)
                storage.add(link)
                # Sleep to avoid hitting rate limits
                time.sleep(3)
            else:
                logger.info("[Dry Run] Would send message and save to history.")

    if not args.dry_run:
        storage.save_history()
        logger.info("History saved.")

    logger.info(f"Job completed. Processed {new_count} new internships.")

if __name__ == "__main__":
    main()
