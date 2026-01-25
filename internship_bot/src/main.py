
import os
import argparse
import time
import logging
import random
from scrapers import InternshalaScraper, RemotiveScraper, RSSScraper
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
    storage = StorageManager(file_path=history_file)
    bot = TelegramBot(bot_token, channel_id)

    # Initialize Scrapers
    scrapers = [
        InternshalaScraper(),
        RemotiveScraper(),
        RSSScraper(url="https://weworkremotely.com/categories/remote-programming-jobs.rss", source_name="WeWorkRemotely"),
        RSSScraper(url="https://stackoverflow.com/jobs/feed", source_name="StackOverflow") 
    ]

    # Run all scrapers and collect results by source
    scraped_data = [] # List of lists
    for scraper in scrapers:
        try:
            results = scraper.scrape()
            if results:
                scraped_data.append(results)
                logger.info(f"{scraper.__class__.__name__}: Found {len(results)} items")
        except Exception as e:
            logger.error(f"Scraper {scraper.__class__.__name__} failed: {e}")

    # Round-robin interleave
    import itertools
    all_internships = [item for items in itertools.zip_longest(*scraped_data) for item in items if item is not None]

    logger.info(f"Total unique internships found: {len(all_internships)}")
    
    # Optional: shuffle slightly or prioritize specific sources? 
    # Round-robin is fair.
    
    new_count = 0
    max_posts = 5  # UPDATED LIMIT
    
    for internship in all_internships:
        if new_count >= max_posts:
            logger.info(f"Reached limit of {max_posts} posts per run.")
            break

        link = internship.get('link')
        if not link:
            continue

        if storage.is_new(link):
            logger.info(f"New internship found: {internship['title']} at {internship['company']}")
            
            if not args.dry_run:
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
