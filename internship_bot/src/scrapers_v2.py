
import requests
import feedparser
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class ContentScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape_rss(self, url, source_name):
        """Scrapes standard RSS feeds (WeWorkRemotely, StackOverflow, etc.)"""
        logger.info(f"Scraping RSS: {url}")
        feed = feedparser.parse(url)
        results = []
        
        for entry in feed.entries:
            title = entry.title
            link = entry.link
            
            # Simple Filter for "Intern"
            if "intern" in title.lower():
                results.append({
                    "title": title,
                    "company": entry.get('author', source_name), # Fallback to source name
                    "location": "Remote", # RSS usually implies remote or unspecified
                    "link": link,
                    "source": source_name,
                    "tags": [tag.term for tag in entry.tags] if hasattr(entry, 'tags') else []
                })
        return results

    def scrape_google_careers_mock(self):
        """
        Mock for Google Careers. 
        Real scraping requires complex Selenium/Playwright or private APIs.
        For a reliable GitHub Action, we often use an RSS feed or a known API endpoint if available.
        Since valid "safe" scraping of Big Tech is hard without getting blocked, 
        we will simulate or use a very specific open endpoint if found.
        
        For now, let's return a static list to demonstrate the pipeline, 
        or use a public aggregating RSS feed for 'Google'.
        """
        # Placeholder for demonstration of "Company" scraping structure
        # In a real scenario, you might use specific reliable endpoints
        return []

    def run_all(self):
        interships = []
        
        # 1. WeWorkRemotely (Great for Remote STEM)
        wwr = self.scrape_rss("https://weworkremotely.com/categories/remote-programming-jobs.rss", "WeWorkRemotely")
        interships.extend(wwr)
        
        # 2. Remotive (API)
        try:
            resp = requests.get("https://remotive.com/api/remote-jobs?category=software-dev", headers=self.headers)
            if resp.status_code == 200:
                data = resp.json()
                for job in data.get('jobs', []):
                    if "intern" in job['title'].lower():
                        interships.append({
                            "title": job['title'],
                            "company": job['company_name'],
                            "location": job['candidate_required_location'],
                            "link": job['url'],
                            "source": "Remotive",
                            "tags": job.get('tags', []),
                            "posted_at": job['publication_date']
                        })
        except Exception as e:
            logger.error(f"Remotive failed: {e}")

        return interships
