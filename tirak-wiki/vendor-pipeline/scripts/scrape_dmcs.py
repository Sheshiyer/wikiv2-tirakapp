"""Scrape DMC listings from dmcfinder.com/listing_region/thailand/"""
import csv
import json
import time
from scrapling import StealthyFetcher

BASE_URL = "https://dmcfinder.com/listing_region/thailand/"


def scrape_page(url):
    """Fetch a single page with a real browser."""
    page = StealthyFetcher.fetch(
        url, headless=True, timeout=30000
    )
    return page


def extract_listings(page):
    """Extract DMC listing data from the page."""
    listings = []
    cards = page.css("article.hubhood-listing-card")

    if not cards:
        print("  No listing cards found on this page.")
        return listings

    print(f"  Found {len(cards)} listing cards")

    for card in cards:
        listing = {}

        # Company name from h5.hubhood-listing-card-title
        titles = card.css("h5.hubhood-listing-card-title")
        if titles:
            listing["name"] = titles[0].text.strip() if titles[0].text else ""

        # Tagline
        taglines = card.css(".hubhood-listing-card-tagline")
        if taglines:
            listing["tagline"] = taglines[0].text.strip() if taglines[0].text else ""

        # Profile URL
        links = card.css("a.hubhood-listing-card-link")
        if links:
            listing["url"] = links[0].attrib.get("href", "")

        # Logo image URL
        logos = card.css(".hubhood-listing-card-logo")
        if logos:
            style = logos[0].attrib.get("style", "")
            if "url(" in style:
                logo_url = style.split("url(")[1].split(")")[0].strip("'\"")
                listing["logo_url"] = logo_url

        # Address/location
        addresses = card.css("address.hubhood-listing-address")
        if addresses:
            listing["location"] = addresses[0].text.strip() if addresses[0].text else ""

        # Region links
        region_links = card.css(".hubhood-card-listing-term-links a")
        if region_links:
            listing["regions"] = [
                r.text.strip() for r in region_links if r.text and r.text.strip()
            ]

        # Rating
        rating_labels = card.css(".hubhood-rating-stars-label")
        if rating_labels:
            listing["rating"] = rating_labels[0].text.strip() if rating_labels[0].text else ""

        # Listing type from article classes
        classes = card.attrib.get("class", "")
        if "job-type-" in classes:
            types = [
                c.replace("job-type-", "").replace("-", " ").title()
                for c in classes.split()
                if c.startswith("job-type-")
            ]
            listing["type"] = ", ".join(types)

        if listing.get("name"):
            listings.append(listing)

    return listings


def main():
    all_listings = []

    # The site has 3 pages
    for page_num in range(1, 4):
        if page_num == 1:
            url = BASE_URL
        else:
            url = f"{BASE_URL}page/{page_num}/"

        print(f"\n--- Scraping page {page_num}: {url} ---")
        try:
            page = scrape_page(url)
            listings = extract_listings(page)
            all_listings.extend(listings)
            print(f"  Total so far: {len(all_listings)}")
        except Exception as e:
            print(f"  Error on page {page_num}: {e}")

        if page_num < 3:
            time.sleep(2)

    # Save as JSON
    json_file = "thailand_dmcs.json"
    with open(json_file, "w") as f:
        json.dump(all_listings, f, indent=2, ensure_ascii=False)

    # Save as CSV
    csv_file = "thailand_dmcs.csv"
    if all_listings:
        fieldnames = ["name", "tagline", "url", "location", "regions", "type", "rating", "logo_url"]
        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for dmc in all_listings:
                row = dict(dmc)
                if "regions" in row and isinstance(row["regions"], list):
                    row["regions"] = ", ".join(row["regions"])
                writer.writerow(row)

    print(f"\n{'='*60}")
    print(f"Done! Saved {len(all_listings)} DMCs")
    print(f"  JSON: {json_file}")
    print(f"  CSV:  {csv_file}")
    print(f"{'='*60}")

    # Print summary table
    for i, dmc in enumerate(all_listings, 1):
        print(f"\n{i}. {dmc.get('name', 'N/A')}")
        if dmc.get("tagline"):
            print(f"   Tagline:  {dmc['tagline']}")
        if dmc.get("url"):
            print(f"   URL:      {dmc['url']}")
        if dmc.get("location"):
            print(f"   Location: {dmc['location']}")
        if dmc.get("type"):
            print(f"   Type:     {dmc['type']}")


if __name__ == "__main__":
    main()
