
import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict
from .base import BaseScraper
# Absolute import or correct relative import if running as module vs script
# Since we run via src/main.py, we should ensure utils is accessible.
# Actually, the error `attempted relative import beyond top-level package` suggests how main.py is called.
# We are calling `python src/main.py`. `src` is not a package in that context unless we run `python -m src.main`.
# To fix this quickly without restructuring:
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import is_recent

logger = logging.getLogger(__name__)

class LinkedInScraper(BaseScraper):
    def scrape(self) -> List[Dict]:
        # Search for: Computer Science Intern, Worldwide, Past 24 Hours
        url = "https://www.linkedin.com/jobs/search?keywords=Computer%20Science%20Intern&location=Worldwide&f_TPR=r86400&position=1&pageNum=0"
        logger.info(f"Scraping {url}...")
        results = []
        
        try:
            # LinkedIn is very strict. We use standard headers, but might still get 999 or 429.
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            }, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"LinkedIn returned status {response.status_code}. Skipping.")
                return results

            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Public job page structure often changes. 
            # Currently items are often in <li> inside <ul class="jobs-search__results-list">
            
            jobs = soup.find_all('li')
            logger.info(f"Found {len(jobs)} potential LinkedIn elements (may include nav items).")

            for job in jobs:
                try:
                    # Look for specific job card structure
                    link_tag = job.find('a', class_='base-card__full-link') or job.find('a', class_='job-search-card__job-title')
                    if not link_tag:
                        continue
                        
                    link = link_tag.get('href')
                    # Clean link (remove tracking params)
                    if '?' in link:
                        link = link.split('?')[0]
                        
                    title = link_tag.get_text(strip=True)
                    
                    company_tag = job.find('h4', class_='base-search-card__subtitle') or job.find('a', class_='hidden-nested-link')
                    company = company_tag.get_text(strip=True) if company_tag else "Unknown Company"
                    
                    location_tag = job.find('span', class_='job-search-card__location')
                    location = location_tag.get_text(strip=True) if location_tag else "Remote/Global"
                    
                    date_tag = job.find('time')
                    date_str = date_tag.get('datetime') if date_tag else "Recently"
                    
                    # Filter for validity 
                    if not title or not link:
                        continue

                    results.append({
                        'title': title,
                        'company': company,
                        'location': location,
                        'link': link,
                        'stipend': "N/A (Check Link)", # LinkedIn public view rarely shows salary
                        'source': 'LinkedIn',
                        'date': date_str
                    })
                except Exception as inner_e:
                    continue
                    
        except Exception as e:
            logger.error(f"LinkedIn scraping failed: {e}")
            
        return results
