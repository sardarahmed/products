
import requests
import xml.etree.ElementTree as ET
import logging
from typing import List, Dict
from .base import BaseScraper

logger = logging.getLogger(__name__)

class RSSScraper(BaseScraper):
    def __init__(self, url: str, source_name: str):
        self.url = url
        self.source_name = source_name

    def scrape(self) -> List[Dict]:
        logger.info(f"Scraping RSS {self.url}...")
        results = []
        
        try:
            response = requests.get(self.url, timeout=15)
            response.raise_for_status()
            
            # Simple XML parsing (could be robustified with feedparser lib if added)
            root = ET.fromstring(response.content)
            
            # Handle Atom or RSS 2.0
            # Very basic assumption: 'item' tags
            items = root.findall('.//item')
            if not items:
                # Try atom 'entry'
                items = root.findall('.//{http://www.w3.org/2005/Atom}entry')

            logger.info(f"Found {len(items)} items in RSS.")

            for item in items:
                title = item.find('title').text if item.find('title') is not None else "Unknown"
                link = item.find('link').text if item.find('link') is not None else ""
                pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ""
                
                # Check for CS keywords
                if not any(k in title.lower() for k in ['software', 'developer', 'engineer', 'data', 'web', 'intern']):
                    continue
                
                results.append({
                    'title': title,
                    'company': self.source_name + " Listing", # RSS often lacks structured company field
                    'location': "Remote/Global",
                    'link': link,
                    'stipend': "See details",
                    'source': self.source_name,
                    'date': pubDate[:16] # Truncate time
                })
                    
        except Exception as e:
            logger.error(f"RSS scraping failed for {self.source_name}: {e}")
            
        return results
