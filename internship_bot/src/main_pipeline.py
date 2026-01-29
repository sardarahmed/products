
import logging
import os
import sys

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.processor import Processor
from src.scrapers_v2 import ContentScraper
from src.poster import Poster

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Daily Internship Pipeline...")

    # 1. Initialize Components
    processor = Processor()
    scraper = ContentScraper()
    poster = Poster(os.getenv('BOT_TOKEN'), os.getenv('CHANNEL_ID'))

    # 2. Scrape Data
    logger.info("Step 1: Scraping...")
    raw_data = scraper.run_all()
    logger.info(f"Scraped {len(raw_data)} potential internships.")

    # 3. Process & Deduplicate
    logger.info("Step 2: Processing...")
    added_count = processor.process_batch(raw_data)
    logger.info(f"Added {added_count} new unique internships to database.")

    # 4. Post to Telegram (Rate Limited)
    logger.info("Step 3: Posting...")
    pending = processor.get_pending_posts(limit=4) # ~4 per run * 4 runs = 16/day (close to 15)
    
    posted_count = 0
    for internship in pending:
        success = poster.post_internship(internship)
        if success:
            processor.mark_as_posted(internship['id'])
            posted_count += 1
            import time
            time.sleep(5) # Delay between posts

    logger.info(f"Pipeline Complete. Posted {posted_count} internships.")

if __name__ == "__main__":
    main()
