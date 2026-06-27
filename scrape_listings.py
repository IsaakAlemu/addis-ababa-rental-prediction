"""
scrape_listings.py

Scrapes rental listing cards from Jiji.com.et for Addis Ababa, across all
11 sub-cities, using Selenium (Jiji blocks simple HTTP requests with bot
detection, but loads normally in a real browser).

Sub-cities with more listings naturally yield more pages of data; sparse
sub-cities exit early once a page returns no results, avoiding wasted
requests. This produces a more geographically balanced dataset than
scraping only the general Addis Ababa search page, which is dominated by
Bole and Kirkos listings.

Output: raw_listings_balanced.csv (unstructured, ready for clean_data.py)
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import random
import csv

options = Options()
options.add_argument("--start-maximized")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(r"C:\Users\isaak\chromedriver\chromedriver.exe"), options=options)

# All 11 official sub-cities of Addis Ababa.
# Note: akaki-kaliti and lemi-kura returned 0 listings on Jiji at time of
# scraping (June 2026) — likely genuine low supply on this platform rather
# than incorrect slugs, since all other 9 slugs returned real results.
SUB_CITIES = [
    "bole",
    "kirkos",
    "nifas-silk-lafto",
    "yeka",
    "arada",
    "kolfe-keranio",
    "lideta",
    "addis-ketema",
    "akaki-kaliti",
    "gullele",
    "lemi-kura",
]

PAGES_PER_SUBCITY = 8

all_rows = []

for sub_city in SUB_CITIES:
    for page in range(1, PAGES_PER_SUBCITY + 1):
        url = f"https://jiji.com.et/{sub_city}/houses-apartments-for-rent?page={page}"
        print(f"Scraping {sub_city} page {page}...")
        driver.get(url)
         
        # Random delay between page loads to avoid hammering the server with an
        # obvious robotic, fixed-interval request pattern 
        wait_time = random.uniform(3, 6)
        time.sleep(wait_time)

        links = driver.find_elements("css selector", "a")
        listings = [l for l in links if l.get_attribute("href") and "-for-rent-" in l.get_attribute("href") and ".html" in l.get_attribute("href")]

        if not listings:
            print(f"  -> No listings found, likely ran out of pages (or invalid slug) for {sub_city}. Skipping rest.")
            break

        for l in listings:
            href = l.get_attribute("href")
            text = l.text
            all_rows.append({"url": href, "raw_text": text, "page": page, "target_subcity": sub_city})

        print(f"  -> {len(listings)} listings found (waited {wait_time:.1f}s)")

print(f"\nTotal listings collected: {len(all_rows)}")

with open("raw_listings_balanced.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["url", "raw_text", "page", "target_subcity"])
    writer.writeheader()
    writer.writerows(all_rows)

print("Saved to raw_listings_balanced.csv")
driver.quit()