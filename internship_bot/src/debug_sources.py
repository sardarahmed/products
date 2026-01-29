
import feedparser
import requests
import json
import logging

def test_wwr():
    url = "https://weworkremotely.com/categories/remote-programming-jobs.rss"
    print(f"Testing WWR: {url}")
    f = feedparser.parse(url)
    print(f"  Entries: {len(f.entries)}")
    count = 0
    for e in f.entries:
        if "intern" in e.title.lower():
            count += 1
            print(f"  MATCH: {e.title}")
    print(f"  Total 'intern' matches: {count}")

def test_remotive():
    url = "https://remotive.com/api/remote-jobs?category=software-dev"
    print(f"Testing Remotive: {url}")
    try:
        r = requests.get(url)
        data = r.json()
        jobs = data.get('jobs', [])
        print(f"  Jobs: {len(jobs)}")
        count = 0
        for j in jobs:
            if "intern" in j['title'].lower():
                count += 1
                print(f"  MATCH: {j['title']}")
        print(f"  Total 'intern' matches: {count}")
    except Exception as e:
        print(f"  Error: {e}")

def test_cern():
    url = "https://api.smartrecruiters.com/v1/companies/CERN/postings"
    print(f"Testing CERN (SmartRecruiters): {url}")
    try:
        r = requests.get(url)
        print(f"  Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            content = data.get('content', [])
            print(f"  Postings: {len(content)}")
            if content:
                print(f"  Sample: {content[0]['name']}")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    test_wwr()
    print("-" * 20)
    test_remotive()
    print("-" * 20)
    test_cern()
