import json
import os
import hashlib
from datetime import datetime, timedelta

DATA_FILE = "data/internships.json"

class Processor:
    def __init__(self):
        self.data_file = os.path.join(os.getcwd(), DATA_FILE)
        self.ensure_data_file()

    def ensure_data_file(self):
        if not os.path.exists(self.data_file):
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w') as f:
                json.dump([], f)

    def load_data(self):
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_data(self, data):
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def generate_id(self, internship):
        """Generates a unique hash based on title, company, and location."""
        raw_string = f"{internship['title']}{internship['company']}{internship['location']}".lower().replace(" ", "")
        return hashlib.md5(raw_string.encode()).hexdigest()

    def normalize_internship(self, raw_data):
        """
        Converts raw scraper output to strict schema.
        Expected keys in raw_data: title, company, location, link, source, etc.
        """
        # Field Classification (Simple Keyword Matching)
        title_lower = raw_data.get('title', '').lower()
        field = "STEM"
        if any(x in title_lower for x in ['data', 'ai', 'learning', 'analyst']):
            field = "Data Science / AI"
        elif any(x in title_lower for x in ['software', 'developer', 'engineer', 'web', 'backend', 'frontend']):
            field = "Computer Science / Engineering"
        elif any(x in title_lower for x in ['research', 'science', 'bio', 'chem']):
            field = "Research / Science"
        
        # Country Extraction
        location = raw_data.get('location', 'Remote')
        country = "Remote" 
        
        # Normalize location string for search
        loc_lower = location.lower()
        
        # Mapping for Target Countries (EU, US, CA, AU)
        # Priority: Exact code match or full name match
        country_map = {
            'united states': 'USA', 'usa': 'USA', 'us': 'USA',
            'united kingdom': 'UK', 'uk': 'UK', 'great britain': 'UK', 'gb': 'UK', 'london': 'UK',
            'canada': 'Canada', 'ca': 'Canada',
            'australia': 'Australia', 'au': 'Australia',
            'germany': 'Germany', 'de': 'Germany', 'berlin': 'Germany', 'munich': 'Germany',
            'france': 'France', 'fr': 'France', 'paris': 'France',
            'switzerland': 'Switzerland', 'ch': 'Switzerland', 'geneva': 'Switzerland', 'zurich': 'Switzerland',
            'netherlands': 'Netherlands', 'nl': 'Netherlands', 'amsterdam': 'Netherlands',
            'spain': 'Spain', 'es': 'Spain', 'madrid': 'Spain', 'barcelona': 'Spain',
            'italy': 'Italy', 'it': 'Italy',
            'sweden': 'Sweden', 'se': 'Sweden',
            'ireland': 'Ireland', 'ie': 'Ireland', 'dublin': 'Ireland',
            'austria': 'Austria', 'at': 'Austria',
            'belgium': 'Belgium', 'be': 'Belgium',
            'portugal': 'Portugal', 'pt': 'Portugal',
            'poland': 'Poland', 'pl': 'Poland',
            'denmark': 'Denmark', 'dk': 'Denmark',
            'norway': 'Norway', 'no': 'Norway',
            'finland': 'Finland', 'fi': 'Finland',
            'india': 'India', 'in': 'India'
        }
        
        # Check against map
        # 1. Check for whole words to avoid partial matches (e.g. 'us' in 'industry')
        import re
        found = False
        for key, val in country_map.items():
            # Regex for "\bkey\b"
            if re.search(r'\b' + re.escape(key) + r'\b', loc_lower):
                country = val
                found = True
                break
        
        # Fallback if no specific country found but location isn't empty
        if not found and location and location.lower() != "remote":
             # Use the location text itself if it looks like a country (simple heuristic)
             pass

        # Domain for Logo
        company_domain = raw_data.get('company', '').lower().replace(" ", "") + ".com" # Very naive, but functional fo clearbit often

        return {
            "id": self.generate_id(raw_data),
            "title": raw_data.get('title', 'Internship'),
            "company": raw_data.get('company', 'Unknown'),
            "location": location,
            "country": country,
            "field": field,
            "duration": raw_data.get('duration', 'Not specified'),
            "stipend": raw_data.get('stipend', 'Not specified'),
            "requirements": raw_data.get('tags', []),
            "apply_link": raw_data.get('link'),
            "source": raw_data.get('source', 'Web'),
            "logo": f"https://logo.clearbit.com/{company_domain}",
            "deadline": raw_data.get('deadline', 'Open'),
            "posted_at": datetime.now().isoformat(),
            "posted_to_telegram": False
        }

    def process_batch(self, new_internships):
        """
        Takes a list of raw dictionaries, normalizes them, and merges with existing data.
        Returns the number of new items added.
        """
        current_data = self.load_data()
        current_ids = {item['id'] for item in current_data}
        
        added_count = 0
        
        for raw in new_internships:
            normalized = self.normalize_internship(raw)
            
            # Deduplication
            if normalized['id'] not in current_ids:
                # Also check Apply Link uniqueness to be safe
                if not any(x['apply_link'] == normalized['apply_link'] for x in current_data):
                    current_data.append(normalized)
                    current_ids.add(normalized['id'])
                    added_count += 1
        
        self.save_data(current_data)
        return added_count

    def get_pending_posts(self, limit=5):
        """Returns internships that haven't been posted yet."""
        data = self.load_data()
        pending = [item for item in data if not item.get('posted_to_telegram')]
        # Sort by posted_at desc (newest first)? Or oldest first to catch up?
        # Usually newest first is better for a news feed.
        pending.sort(key=lambda x: x['posted_at'], reverse=True)
        return pending[:limit]

    def mark_as_posted(self, internship_id):
        data = self.load_data()
        for item in data:
            if item['id'] == internship_id:
                item['posted_to_telegram'] = True
                break
        self.save_data(data)
