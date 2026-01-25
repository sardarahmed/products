
import logging
from typing import List, Dict
from playwright.sync_api import sync_playwright

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InternshipScraper:
    def scrape(self) -> List[Dict]:
        """
        Main method to scrape internships.
        """
        return []

class InternshalaScraper(InternshipScraper):

    def scrape(self) -> List[Dict]:
        url = "https://internshala.com/internships/"
        logger.info(f"Scraping {url} with Playwright...")
        results = []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_viewport_size({"width": 1280, "height": 720})
                
                page.goto(url)
                page.wait_for_load_state("networkidle")
                
                page.screenshot(path="debug_screenshot.png")
                logger.info(f"Page title: {page.title()}")
                
                # Robust strategy: Find all internship containers by looking for 'internship_meta' or specific link patterns
                # Based on previous robust findings, we look for anchor tags with detail links if classes fail
                
                container_selector = '.individual_internship'
                if page.query_selector(container_selector):
                    logger.info(f"Found containers with selector: {container_selector}")
                else:
                    logger.warning(f"Selector {container_selector} not found. Trying fallback.")
                    # Fallback: finding all divs that look like containers (e.g. have a unique ID starting with individual_internship)
                    container_selector = 'div[id^="individual_internship_"]'
                
                internships = page.query_selector_all(container_selector)
                logger.info(f"Found {len(internships)} potential internship elements.")
                
                for internship in internships:
                    try:
                        # Extract details
                        title_elem = internship.query_selector('h3') or internship.query_selector('.profile')
                        company_elem = internship.query_selector('.company_name') or internship.query_selector('.link_display_like_text')
                        location_elem = internship.query_selector('.location_link') or internship.query_selector('a.location_link')
                        
                        # Link
                        link = internship.get_attribute('data-href')
                        if not link:
                            # Try to find the title link
                            if title_elem:
                                parent_a = title_elem.query_selector('xpath=..') # parent if title is inside a
                                if parent_a and parent_a.get_attribute('href'):
                                    link = parent_a.get_attribute('href')
                        
                        if not link:
                             # Try any link inside
                             any_link = internship.query_selector('a')
                             if any_link: link = any_link.get_attribute('href')

                        # Stipend
                        stipend_elem = internship.query_selector('.stipend')
                        
                        title = title_elem.inner_text().strip() if title_elem else "Unknown Title"
                        company = company_elem.inner_text().strip() if company_elem else "Unknown Company"
                        location = location_elem.inner_text().strip() if location_elem else "Remote/Unspecified"
                        stipend = stipend_elem.inner_text().strip() if stipend_elem else "N/A"
                        
                        if link and "/internship/detail/" in link:
                            full_link = f"https://internshala.com{link}" if link.startswith('/') else link
                            
                            results.append({
                                'title': title,
                                'company': company,
                                'location': location,
                                'link': full_link,
                                'stipend': stipend,
                                'source': 'Internshala'
                            })
                                
                    except Exception as inner_e:
                        continue
                        
                browser.close()
                
        except Exception as e:
            logger.error(f"Internshala scraping failed: {e}")
            
        logger.info(f"Found {len(results)} internships from Internshala")
        return results

if __name__ == "__main__":
    scraper = InternshalaScraper()
    internships = scraper.scrape()
    for i in internships[:5]:
        print(i)
