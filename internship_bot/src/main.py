
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

    # Determine path to history.json (in the parent directory of src)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    history_file = os.path.join(base_dir, 'history.json')
    
    # Initialize modules
    scraper = InternshalaScraper()
    storage = StorageManager(file_path=history_file)
    bot = TelegramBot(bot_token, channel_id)

    # Scrape
    logger.info("Starting scrape job...")
    internships = scraper.scrape()
    logger.info(f"Scraped {len(internships)} internships.")

    new_count = 0
    max_posts = 10
    
    for internship in internships:
        if new_count >= max_posts:
            logger.info(f"Reached limit of {max_posts} posts per run.")
            break

        link = internship.get('link')
        if not link:
            continue

        if storage.is_new(link):
            logger.info(f"New internship found: {internship['title']} at {internship['company']}")
            
            if not args.dry_run:
                # message = bot.format_internship(internship)
                # bot.send_message(message)
                # Updated main call signature matches new bot method
                message = bot.format_internship(internship)
                bot.send_message(message, link=link)
                
                storage.add(link)
                new_count += 1
                # Sleep to avoid hitting rate limits
                time.sleep(3)
            else:
                logger.info("[Dry Run] Would send message and save to history.")
                new_count += 1

    if not args.dry_run:
        storage.save_history()
        logger.info("History saved.")

    logger.info(f"Job completed. Processed {new_count} new internships.")

if __name__ == "__main__":
    main()
