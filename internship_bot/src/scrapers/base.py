
from abc import ABC, abstractmethod
from typing import List, Dict

class BaseScraper(ABC):
    @abstractmethod
    def scrape(self) -> List[Dict]:
        """
        Scrapes internships and returns a list of dictionaries.
        Each dict must have: title, company, location, link, stipend, source.
        """
        pass
