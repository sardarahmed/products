
import sys
import os
import logging

# Setup Logging to Console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fix path
sys.path.append(os.getcwd())

try:
    from src.scrapers_v2 import ContentScraper
except ImportError:
    print("Import Failed! Trying relative...")
    from scrapers_v2 import ContentScraper

def test_scraper_class():
    print("Initializing Scraper...")
    scraper = ContentScraper()
    
    print("Running run_all()...")
    results = scraper.run_all()
    
    print(f"Results Count: {len(results)}")
    if results:
        print(f"Sample: {results[0]}")

if __name__ == "__main__":
    test_scraper_class()
