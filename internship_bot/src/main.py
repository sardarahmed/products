
import os
import argparse
import time
import logging
import random
from scrapers import InternshalaScraper, RemotiveScraper, RSSScraper, LinkedInScraper
from database import Database
from bot import TelegramBot
from filters import extract_country, classify_field
from utils import parse_date

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
    db = Database()
    bot = TelegramBot(bot_token, channel_id)

    # Initialize Scrapers
    scrapers = [
        LinkedInScraper(),
        InternshalaScraper(),
        RemotiveScraper(),
        RSSScraper(url="https://weworkremotely.com/categories/remote-programming-jobs.rss", source_name="WeWorkRemotely"),
        RSSScraper(url="https://stackoverflow.com/jobs/feed", source_name="StackOverflow") 
    ]

    # Run all scrapers
    scraped_data = []
    for scraper in scrapers:
        try:
            results = scraper.scrape()
            if results:
                scraped_data.append(results)
                logger.info(f"{scraper.__class__.__name__}: Found {len(results)} items")
        except Exception as e:
            logger.error(f"Scraper {scraper.__class__.__name__} failed: {e}")

    # Flatten results
    import itertools
    all_internships = [item for items in scraped_data for item in items]

    new_count = 0
    max_broadcast_posts = 5 # Limit for channel broadcasting
    processed_count = 0

    for i in all_internships:
        # Prepare data for DB
        title = i.get('title', 'N/A')
        location = i.get('location', 'Unknown')
        
        # Enrich data
        country = extract_country(location)
        field = classify_field(title)
        
        # Parse date
        date_str = i.get('date', '')
        date_obj = parse_date(date_str)
        
        internship_data = {
            'title': title,
            'company': i.get('company', 'N/A'),
            'location': location,
            'link': i.get('link'),
            'date_obj': date_obj,
            'source': i.get('source', 'Web'),
            'country': country,
            'field': field
        }

        # Add to Database
        # Returns True if it matches unique constraint (link) and was added
        is_new = db.add_internship(internship_data)
        
        if is_new:
            logger.info(f"New internship saved: {title} ({country}, {field})")
            
            # Broadcast to Channel (Limit to max_broadcast_posts per run for channel spam prevention)
            if processed_count < max_broadcast_posts:
                if not args.dry_run:
                    message = bot.format_internship(i)
                    bot.send_message(message, link=i.get('link'))
                    time.sleep(3) # Rate limit protection
                else:
                     logger.info("[Dry Run] Would send to channel")
                
                processed_count += 1
                new_count += 1
        
    logger.info(f"Job completed. Saved {new_count} new internships to DB. Broadcasted {processed_count}.")

if __name__ == "__main__":
    main()

