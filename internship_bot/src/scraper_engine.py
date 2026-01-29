
import requests
import feedparser
from bs4 import BeautifulSoup
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class ContentScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape_rss(self, url, source_name):
        """Scrapes standard RSS feeds"""
        logger.info(f"Scraping RSS: {url}")
        feed = feedparser.parse(url)
        results = []
        
        for entry in feed.entries:
            title = entry.title
            link = entry.link
            
            if "intern" in title.lower():
                results.append({
                    "title": title,
                    "company": getattr(entry, 'author', source_name),
                    "location": "Remote", 
                    "link": link,
                    "source": source_name,
                    "tags": [tag.term for tag in entry.tags] if hasattr(entry, 'tags') else [],
                    "posted_at": getattr(entry, 'published', 'Recently')
                })
        return results

    def scrape_cern_api(self):
        """Scrapes CERN jobs via SmartRecruiters API"""
        url = "https://api.smartrecruiters.com/v1/companies/CERN/postings"
        logger.info(f"Scraping CERN API: {url}")
        results = []
        try:
            r = requests.get(url) # No headers
            if r.status_code == 200:
                data = r.json()
                for job in data.get('content', []):
                    # Filter for STEM/Intern/Student
                    title = job['name']
                    # CERN posts often explicitly say "Student" or "Graph" etc.
                    # We will take all tech/student roles.
                    # Actually, for CERN, almost everything is STEM.
                    # Let's filter slightly for "Student", "Graduate", "Intern", "Fellow" to avoid senior stuff?
                    # Or just take everything as they are high quality. User said "CERN Careers" (implied all).
                    # But Processor filters for STEM fields.
                    
                    results.append({
                        "title": title,
                        "company": "CERN",
                        "location": job['location']['city'] + ", " + job['location']['country'],
                        "link": f"https://jobs.smartrecruiters.com/CERN/{job['id']}",
                        "source": "CERN Careers",
                        "tags": [],
                        "posted_at": job['releasedDate']
                    })
        except Exception as e:
            logger.error(f"CERN Scraper failed: {e}")
        return results

    def scrape_internshala(self):
        """Scrapes Internshala Computer Science Internships"""
        url = "https://internshala.com/internships/computer-science-internship/"
        logger.info(f"Scraping Internshala: {url}")
        results = []
        try:
            r = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(r.content, 'html.parser')
            
            # Internshala CSS classes change often. Using the logic from previous robust scraper.
            internships = soup.find_all('div', class_='individual_internship') or \
                          soup.find_all('div', id=lambda x: x and x.startswith('individual_internship_'))
            
            for i in internships:
                try:
                    title_elem = i.find('h3', class_='heading_4_5') or i.find('div', class_='heading_4_5')
                    company_elem = i.find('h4', class_='heading_6_company') or i.find('div', class_='company_name')
                    location_elem = i.find('a', class_='location_link') or i.find('span', class_='location_link')
                    
                    # Link logic
                    link = i.get('data-href')
                    if not link:
                         # Fallback search
                         title_a = i.find('a', class_='view_detail_button')
                         if title_a: link = title_a.get('href')

                    if not link: continue

                    full_link = f"https://internshala.com{link}" if link.startswith('/') else link
                    
                    results.append({
                        "title": title_elem.get_text(strip=True) if title_elem else "Internship",
                        "company": company_elem.get_text(strip=True) if company_elem else "Unknown",
                        "location": location_elem.get_text(strip=True) if location_elem else "India",
                        "link": full_link,
                        "source": "Internshala",
                        "tags": ["Computer Science"],
                        "stipend": i.find('span', class_='stipend').get_text(strip=True) if i.find('span', class_='stipend') else "N/A"
                    })
                except Exception:
                    continue
        except Exception as e:
            logger.error(f"Internshala failed: {e}")
        
        return results

    def run_all(self):
        internships = []
        
        # 1. CERN (API)
        try:
            logger.info("Debug: Starting CERN Scrape...")
            # Remove string headers for API to avoid potential anti-bot checks on User-Agent
            internships.extend(self.scrape_cern_api())
        except Exception as e:
            logger.error(f"CERN Scraper crashed: {e}", exc_info=True)

        # 2. Internshala (HTML)
        try:
            logger.info("Debug: Starting Internshala Scrape...")
            internships.extend(self.scrape_internshala())
        except Exception as e:
            logger.error(f"Internshala Scraper crashed: {e}")

        # 3. RSS Feeds
        try:
             logger.info("Debug: Starting WWR Scrape...")
             internships.extend(self.scrape_rss("https://weworkremotely.com/categories/remote-programming-jobs.rss", "WeWorkRemotely"))
        except Exception as e:
            logger.error(f"RSS Scraper crashed: {e}")

        # 4. Remotive (API)
        try:
            logger.info("Debug: Starting Remotive Scrape...")
            resp = requests.get("https://remotive.com/api/remote-jobs?category=software-dev", headers=self.headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                for job in data.get('jobs', []):
                    # Relax filter for testing
                    if "intern" in job['title'].lower():
                        internships.append({
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

        logger.info(f"Total Internships Found: {len(internships)}")
        return internships
