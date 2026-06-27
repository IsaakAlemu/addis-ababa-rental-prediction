"""
clean_data.py

Takes raw scraped listing data (from scrape_listings.py) and parses the
unstructured text of each listing card into structured columns: price,
bedrooms, property type, size, sub-city, and furnished status.

Also deduplicates listings (Jiji repeats some "pinned" listings across
multiple pages) and filters out price outliers likely caused by parsing
errors or mislabeled listings (e.g. "for sale" prices appearing in "for
rent" search results).

Input:  raw_listings_balanced.csv (from the scraper)
Output: clean_listings.csv (ready for EDA / modeling)
"""
import csv
import re

INPUT_FILE = "raw_listings_balanced.csv"
OUTPUT_FILE = "clean_listings.csv"

def clean_url(url):
    """Strip query parameters so duplicate listings can be detected."""
    return url.split("?")[0]

def parse_listing(raw_text):
    """
    Extract structured fields from a single listing's raw card text.
    Jiji's card text has no fixed format, so each field is extracted
    independently using regex/keyword matching, tolerating missing fields.
    """
    lines = raw_text.strip().split("\n")
    full_text = " ".join(lines)

    # --- Price ---
    price_match = re.search(r"ETB\s*([\d,]+)", full_text)
    price = int(price_match.group(1).replace(",", "")) if price_match else None

    # --- Bedrooms ---
    bedrooms = None
    bdrm_match = re.search(r"(\d+)\s*bdrm", full_text, re.IGNORECASE)
    if bdrm_match:
        bedrooms = int(bdrm_match.group(1))
    elif "studio" in full_text.lower():
        bedrooms = 0  # studio = 0 separate bedrooms

    # --- Property type ---
    # Only look at the title area (before the description starts) to avoid
    # matching words like "house" inside a Villa's description text
    title_area = full_text[:120]
    property_type = None
    for ptype in ["Penthouse", "Apartment", "Villa", "Duplex", "Studio", "House"]:
        if ptype.lower() in title_area.lower():
            property_type = ptype
            break

    # --- Size in square meters ---
    size_match = re.search(r"(\d+)\s*square meter", full_text, re.IGNORECASE)
    if not size_match:
        size_match = re.search(r"(\d+)\s*sqm", full_text, re.IGNORECASE)
    size_m2 = int(size_match.group(1)) if size_match else None

    # --- Sub-city: last line of the card is usually the sub-city ---
    sub_city = lines[-1].strip() if lines else None

    # --- Furnished flag ---
    furnished = "furnished" in full_text.lower() and "unfurnished" not in full_text.lower()

    return {
        "price_etb": price,
        "bedrooms": bedrooms,
        "property_type": property_type,
        "size_m2": size_m2,
        "sub_city": sub_city,
        "furnished": furnished,
    }

def main():
    rows = []
    seen_urls = set()

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            base_url = clean_url(row["url"])
            if base_url in seen_urls:
                continue  # skip duplicate listing
            seen_urls.add(base_url)

            parsed = parse_listing(row["raw_text"])
            parsed["url"] = base_url
            rows.append(parsed)

    print(f"Total raw rows: deduplicated to {len(rows)} unique listings")

    # Filter out missing prices and outliers outside a realistic monthly
    # rent range — values below 5,000 ETB are likely parsing errors, and
    # values above 1,000,000 ETB are likely "for sale" listings mislabeled
    # as "for rent" (a known data quality issue found during cleaning)
    before = len(rows)
    rows = [r for r in rows if r["price_etb"] and 5000 <= r["price_etb"] <= 1000000]
    
    print(f"Removed {before - len(rows)} rows with missing/outlier prices")

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["url", "price_etb", "bedrooms", "property_type", "size_m2", "sub_city", "furnished"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} clean rows to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()