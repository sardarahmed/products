
import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict
from .base import BaseScraper

logger = logging.getLogger(__name__)

class InternshalaScraper(BaseScraper):
    def __init__(self):
         self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape(self) -> List[Dict]:
        url = "https://internshala.com/internships/computer-science-internship/"
        logger.info(f"Scraping {url}...")
        results = []
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            internships = soup.find_all('div', class_='individual_internship')
            if not internships:
                 internships = soup.find_all('div', id=lambda x: x and x.startswith('individual_internship_'))

            logger.info(f"Found {len(internships)} potential internship elements.")

            for internship in internships:
                try:
                    title_elem = internship.find('h3', class_='heading_4_5') or internship.find('div', class_='heading_4_5') or internship.find('a', class_='heading_4_5') or internship.find('h3')
                    company_elem = internship.find('h4', class_='heading_6_company') or internship.find('div', class_='company_name') or internship.find('a', class_='link_display_like_text') or internship.find('div', class_='company_name') 
                    location_elem = internship.find('a', class_='location_link') or internship.find('span', class_='location_link') or internship.find('div', id='location_names')
                    link_elem = internship.get('data-href')
                    
                    if not title_elem and not company_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
                    company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
                    location = location_elem.get_text(strip=True) if location_elem else "Remote/Unspecified"
                    
                    link = None
                    if link_elem:
                        link = link_elem
                    else:
                         if title_elem and title_elem.name == 'a':
                             link = title_elem.get('href')
                         elif title_elem:
                             a_tag = title_elem.find_parent('a')
                             if a_tag: link = a_tag.get('href')
                    
                    if not link:
                         a_tags = internship.find_all('a')
                         for a in a_tags:
                             h = a.get('href')
                             if h and '/internship/detail/' in h:
                                 link = h
                                 break

                    stipend_elem = internship.find('span', class_='stipend')
                    stipend = stipend_elem.get_text(strip=True) if stipend_elem else "N/A"
                    
                    # Try to find start date or posted text, but Internshala listing often omits "Posted on"
                    # We'll default to "Freshly Posted" for scraped items
                    date = "Freshly Posted" 

                    if link:
                        full_link = f"https://internshala.com{link}" if link.startswith('/') else link
                        if "/internship/detail/" in full_link:
                            results.append({
                                'title': title,
                                'company': company,
                                'location': location,
                                'link': full_link,
                                'stipend': stipend,
                                'source': 'Internshala',
                                'date': date
                            })
                except Exception as inner_e:
                    continue
                    
        except Exception as e:
            logger.error(f"Internshala scraping failed: {e}")
            
        return results
