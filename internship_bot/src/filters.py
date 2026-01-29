
import re

COUNTRIES = [
    "United States", "India", "Germany", "United Kingdom", "Canada", 
    "Australia", "France", "Netherlands", "Singapore", "Remote"
]

STEM_FIELDS = {
    "Computer Science": ["software", "developer", "engineer", "web", "frontend", "backend", "full stack", "java", "python", "c++", "react", "node", "android", "ios", "app", "cloud", "devops", "security", "cyber"],
    "Data Science & AI": ["data", "analyst", "scientist", "machine learning", "ai", "deep learning", "nlp", "vision", "statistics", "analytics"],
    "Engineering": ["mechanical", "electrical", "civil", "chemical", "electronics", "robotics", "embedded", "hardware"],
    "Bio & Science": ["biology", "chemistry", "physics", "biotech", "pharma", "research", "lab"],
    "Mathematics": ["math", "cryptography", "actuarial"]
}

def extract_country(location: str):
    if not location:
        return "Unknown"
    
    if "remote" in location.lower():
        # Even if remote, sometimes it says "Remote in US". Let's try to find country first, otherwise default to "Remote" as top level if desired. 
        # But user wants country filter. "Remote" is often treated as a location. 
        # Let's check for specific countries first.
        pass

    for country in COUNTRIES:
        if country.lower() in location.lower():
            return country
    
    # Common mappings
    if "USA" in location or "US" in location.split(): # Safety check for separate word US
        return "United States"
    if "UK" in location or "London" in location:
        return "United Kingdom"
    if "Bangalore" in location or "Mumbai" in location or "Delhi" in location:
        return "India"
    
    if "remote" in location.lower():
        return "Remote"

    return "Other"

def classify_field(title: str):
    if not title:
        return "Other"
    
    title_lower = title.lower()
    
    for field, keywords in STEM_FIELDS.items():
        for keyword in keywords:
            if keyword in title_lower:
                return field
    
    return "Other"
