import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import concurrent.futures
from threading import Lock
import sys
import os
from datetime import datetime

# Setup Selenium with a headless browser and suppressed logs
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('--log-level=3')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(options=options)
driver_lock = Lock()

# Use a session to persist parameters across requests
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

def is_valid_link(link, base_url):
    parsed_url = urlparse(link)
    return (base_url in link and 
            not link.endswith(('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.js', '.css')) and 
            '/wp-content/' not in link and 
            '/wp-json/' not in link)

def get_all_links_selenium(url, base_url):
    links = set()
    try:
        with driver_lock:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "a"))
            )
            elements = driver.find_elements(By.TAG_NAME, "a")
            for element in elements:
                link = element.get_attribute('href')
                if link and is_valid_link(link, base_url):
                    links.add(link)
    except Exception:
        pass
    return links

def scrape_page(url):
    try:
        response = session.get(url, timeout=10)
        if response.status_code == 403:
            return ""
        soup = BeautifulSoup(response.text, 'html.parser')
        page_content = soup.get_text(separator=' ', strip=True)
    except Exception:
        return ""

    if not page_content.strip():
        page_content = scrape_page_with_selenium(url)
    
    return page_content

def scrape_page_with_selenium(url):
    try:
        with driver_lock:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
            )
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            page_content = soup.get_text(separator=' ', strip=True)
            return page_content
    except Exception:
        return ""

def process_url(url):
    print(f"Visiting: {url}")
    content = scrape_page(url)
    return f"URL: {url}\n{content}"  # Prepend the URL to the content

def scrape_website(start_url):
    to_visit = get_all_links_selenium(start_url, start_url)
    visited = set()
    all_content = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        
        while to_visit:
            url = to_visit.pop()
            if url not in visited:
                visited.add(url)
                futures.append(executor.submit(process_url, url))
                if url.count('/') <= 2:
                    new_links = get_all_links_selenium(url, start_url)
                    to_visit.update(new_links)
        
        for future in concurrent.futures.as_completed(futures):
            content = future.result()
            if content:
                all_content.append(content)
    
    return all_content

if __name__ == "__main__":
    # Get the start_url from command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python web_scraper_multithreaded.py <start_url>")
        sys.exit(1)

    start_url = sys.argv[1]

    # Scrape the website content
    all_content = scrape_website(start_url)

    # Create a subfolder to save the scraped content
    output_dir = "scraped_websites"
    os.makedirs(output_dir, exist_ok=True)

    # Generate a unique filename with date and hour
    webpage_name = re.sub(r'[^a-zA-Z0-9]', '_', start_url.split("//")[-1].split('/')[0])  # Extract the domain name
    timestamp = datetime.now().strftime('%Y%m%d_%H')  # Date and hour only
    filename = f"{webpage_name}_{timestamp}.txt"
    filepath = os.path.join(output_dir, filename)

    # Save the scraped content to the file
    with open(filepath, 'w', encoding='utf-8') as f:
        for content in all_content:
            f.write(content + "\n\n")

    print(f"Scraped content saved to {filepath}")

    driver.quit()