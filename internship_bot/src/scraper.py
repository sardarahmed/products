
import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InternshipScraper:
    def __init__(self):
         self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape(self) -> List[Dict]:
        """
        Main method to scrape internships.
        """
        return []

class InternshalaScraper(InternshipScraper):
    def scrape(self) -> List[Dict]:
        url = "https://internshala.com/internships/computer-science-internship/"
        logger.info(f"Scraping {url} with Request...")
        results = []
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Internshala structure variations
            # 1. Standard containers
            internships = soup.find_all('div', class_='individual_internship')
            if not internships:
                 # 2. Dynamic ID containers
                 internships = soup.find_all('div', id=lambda x: x and x.startswith('individual_internship_'))

            logger.info(f"Found {len(internships)} potential internship elements.")

            for internship in internships:
                try:
                    # Title
                    title_elem = internship.find('h3', class_='heading_4_5') or internship.find('div', class_='heading_4_5') or internship.find('a', class_='heading_4_5') or internship.find('h3')
                    
                    # Company
                    company_elem = internship.find('h4', class_='heading_6_company') or internship.find('div', class_='company_name') or internship.find('a', class_='link_display_like_text') or internship.find('div', class_='company_name') 
                    
                    # Location
                    location_elem = internship.find('a', class_='location_link') or internship.find('span', class_='location_link') or internship.find('div', id='location_names')
                    
                    # Link
                    link_elem = internship.get('data-href')
                    
                    # Check partial requirement
                    # Note: Sometimes title/company are missing in ad blocks inside list
                    if not title_elem and not company_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
                    company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
                    location = location_elem.get_text(strip=True) if location_elem else "Remote/Unspecified"
                    
                    link = None
                    if link_elem:
                        link = link_elem
                    else:
                        # Try to find a link inside title or surrounding anchor
                         # Often the title is an anchor or inside one
                         if title_elem and title_elem.name == 'a':
                             link = title_elem.get('href')
                         elif title_elem:
                             a_tag = title_elem.find_parent('a')
                             if a_tag: link = a_tag.get('href')
                    
                    # Fallback for link
                    if not link:
                         a_tags = internship.find_all('a')
                         for a in a_tags:
                             h = a.get('href')
                             if h and '/internship/detail/' in h:
                                 link = h
                                 break

                    # Stipend
                    stipend_elem = internship.find('span', class_='stipend')
                    stipend = stipend_elem.get_text(strip=True) if stipend_elem else "N/A"

                    if link:
                        full_link = f"https://internshala.com{link}" if link.startswith('/') else link
                        if "/internship/detail/" in full_link: # Ensure it is a valid detail link
                            results.append({
                                'title': title,
                                'company': company,
                                'location': location,
                                'link': full_link,
                                'stipend': stipend,
                                'source': 'Internshala'
                            })
                except Exception as inner_e:
                    logger.debug(f"Failed to parse an internship item: {inner_e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Internshala scraping failed: {e}")
            
        logger.info(f"Found {len(results)} internships from Internshala")
        return results

if __name__ == "__main__":
    scraper = InternshalaScraper()
    internships = scraper.scrape()
    for i in internships[:5]:
        print(i)
