
import requests

url = "https://internshala.com/internships/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    if "internship/detail" in response.text:
        print("SUCCESS: Found internship links in source code!")
        print(f"Content length: {len(response.text)}")
    else:
        print("FAILURE: Internship links not found in source code.")
        print(f"Content preview: {response.text[:500]}")
except Exception as e:
    print(f"ERROR: {e}")
