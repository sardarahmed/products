
import requests
import logging
from typing import List, Dict
from .base import BaseScraper

logger = logging.getLogger(__name__)

class RemotiveScraper(BaseScraper):
    def scrape(self) -> List[Dict]:
        url = "https://remotive.com/api/remote-jobs?category=software-dev&search=internship"
        logger.info(f"Scraping {url}...")
        results = []
        
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            jobs = data.get('jobs', [])
            logger.info(f"Found {len(jobs)} potential jobs from Remotive.")
            
            for job in jobs:
                # Remotive returns jobs, we filter for "intern" in title if API param wasn't strict enough
                title = job.get('title', '')
                if 'intern' not in title.lower():
                    continue
                    
                company = job.get('company_name', 'Unknown')
                location = job.get('candidate_required_location', 'Remote')
                link = job.get('url')
                salary = job.get('salary', 'N/A')
                date_posted = job.get('publication_date', '')[:10] # YYYY-MM-DD
                
                if link:
                    results.append({
                        'title': title,
                        'company': company,
                        'location': location,
                        'link': link,
                        'stipend': salary if salary else "N/A",
                        'source': 'Remotive',
                        'date': date_posted
                    })
                    
        except Exception as e:
            logger.error(f"Remotive scraping failed: {e}")
            
        return results
