
from playwright.sync_api import sync_playwright

def dump_links():
    url = "https://internshala.com/internships/"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 720})
        print(f"Navigating to {url}")
        page.goto(url)
        page.wait_for_load_state("networkidle")
        
        print(f"Page Title: {page.title()}")
        
        links = page.query_selector_all("a")
        print(f"Found {len(links)} links.")
        
        with open("links_dump.txt", "w", encoding="utf-8") as f:
            for link in links:
                href = link.get_attribute("href")
                text = link.inner_text().replace('\n', ' ').strip()
                if href:
                    f.write(f"{text} -> {href}\n")
                    # Print first 10 for quick debug
                    
        browser.close()

if __name__ == "__main__":
    dump_links()
