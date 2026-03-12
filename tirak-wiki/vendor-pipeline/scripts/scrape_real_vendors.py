"""
Scrape REAL vendors from verified web sources to backfill categories below 50.
Uses live scraping with URL validation — every vendor added must have a working URL.

Sources:
- TripAdvisor category pages (real businesses)
- Google search results (to find real URLs for known businesses)
- Specific directory sites per category
"""
import csv
import json
import os
import re
import ssl
import sys
import time
from collections import Counter
from urllib.parse import urljoin, urlparse, quote_plus
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from scrapling import Fetcher, StealthyFetcher, Selector

JSON_PATH = os.path.expanduser("~/tirak_thailand_vendors.json")
OUTPUT_DIR = os.path.expanduser("~/")

TIMEOUT = 8

# ══════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════════════

def normalize_name(name):
    n = name.lower().strip()
    for suffix in [
        "co., ltd.", "co., ltd", "co.,ltd.", "co.,ltd", "co. ltd.",
        "co. ltd", "co.,", "co.", "ltd.", "ltd", "inc.", "inc",
        "thailand", "bangkok", "phuket", "chiang mai",
    ]:
        n = n.replace(suffix, "")
    n = re.sub(r"[^\w\s]", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n


def fetch_page(url):
    """Fetch a page with urllib (fast, no retries)."""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        })
        resp = urlopen(req, timeout=TIMEOUT, context=ctx)
        html = resp.read().decode("utf-8", errors="ignore")
        return Selector(html)
    except Exception:
        return None


def check_url_live(url):
    """Quick check if URL is live (returns True/False)."""
    if not url or not url.startswith("http"):
        return False
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = Request(url, method="HEAD", headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        })
        resp = urlopen(req, timeout=5, context=ctx)
        return resp.status < 400
    except HTTPError as e:
        # 403 = blocked but exists, 405 = method not allowed but exists
        return e.code in (403, 405, 406, 429)
    except Exception:
        # Try GET as fallback
        try:
            req = Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                              "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            })
            resp = urlopen(req, timeout=5, context=ctx)
            return resp.status < 400
        except HTTPError as e2:
            return e2.code in (403, 405, 406, 429)
        except Exception:
            return False


def fetch_stealthy(url):
    """Fetch with StealthyFetcher for JS-heavy pages."""
    try:
        return StealthyFetcher.fetch(url, headless=True, timeout=20000)
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════
# SCRAPER: Google Search for real business URLs
# ══════════════════════════════════════════════════════════════

def google_search_url(business_name, location="Thailand"):
    """Search Google for a business to find its real URL."""
    query = f"{business_name} {location} official website"
    search_url = f"https://www.google.com/search?q={quote_plus(query)}&num=5"
    try:
        page = StealthyFetcher.fetch(search_url, headless=True, timeout=15000)
        if not page:
            return None
        # Extract first non-google, non-ad result
        links = page.css("a[href]")
        for link in links:
            href = link.attrib.get("href", "")
            if href.startswith("http") and "google" not in href and "youtube" not in href:
                parsed = urlparse(href)
                if parsed.scheme in ("http", "https") and "." in parsed.netloc:
                    if check_url_live(href):
                        return href
    except Exception:
        pass
    return None


# ══════════════════════════════════════════════════════════════
# SCRAPER: TripAdvisor Thailand listings
# ══════════════════════════════════════════════════════════════

def scrape_tripadvisor_listings(category_url, max_items=30):
    """Scrape TripAdvisor listing pages for business names and URLs."""
    results = []
    try:
        page = fetch_stealthy(category_url)
        if not page:
            return results
        # TripAdvisor listing cards
        cards = page.css("[data-automation='listItem']") or page.css(".listing_title") or page.css("div[data-test-target='attraction-list-card']")
        for card in cards[:max_items]:
            links = card.css("a[href]")
            name = ""
            url = ""
            for link in links:
                href = link.attrib.get("href", "")
                text = link.text.strip() if link.text else ""
                if text and len(text) > 3 and "/Attraction_Review" in href or "/Hotel_Review" in href or "/Restaurant_Review" in href:
                    name = text
                    url = f"https://www.tripadvisor.com{href}" if href.startswith("/") else href
                    break
            if name and url:
                results.append({"name": name, "url": url})
    except Exception as e:
        print(f"  TripAdvisor error: {e}")
    return results


# ══════════════════════════════════════════════════════════════
# SCRAPER: Specific category scrapers
# ══════════════════════════════════════════════════════════════

def scrape_hostelworld_bangkok():
    """Scrape Hostelworld for Bangkok hostels with verified URLs."""
    results = []
    url = "https://www.hostelworld.com/hostels/Bangkok"
    page = fetch_stealthy(url)
    if not page:
        return results
    cards = page.css("[data-testid='property-card']") or page.css(".property-card") or page.css("a.property-listing")
    for card in cards[:30]:
        name_el = card.css("h2") or card.css("[data-testid='property-name']") or card.css(".property-name")
        link_el = card.css("a[href]")
        if name_el and link_el:
            name = name_el[0].text.strip() if name_el[0].text else ""
            href = link_el[0].attrib.get("href", "")
            if name and href:
                full_url = f"https://www.hostelworld.com{href}" if href.startswith("/") else href
                results.append({"name": name, "url": full_url, "location": "Bangkok"})
    return results


def scrape_eventbrite_thailand():
    """Scrape Eventbrite for event venues in Thailand."""
    results = []
    url = "https://www.eventbrite.com/d/thailand/events/"
    page = fetch_page(url)
    if not page:
        return results
    cards = page.css("[data-testid='event-card']") or page.css(".eds-event-card-content")
    for card in cards[:20]:
        name_el = card.css("h2") or card.css(".eds-event-card__formatted-name--is-clamped")
        if name_el:
            name = name_el[0].text.strip() if name_el[0].text else ""
            if name:
                results.append({"name": name})
    return results


# ══════════════════════════════════════════════════════════════
# KNOWN REAL BUSINESSES (with verified URLs from web search)
# These are real businesses I will verify URLs for at runtime
# ══════════════════════════════════════════════════════════════

# Businesses that definitely exist but I need to find/verify their real URLs
BUSINESSES_TO_VERIFY = {
    "Nightlife & Entertainment": [
        # Well-known real venues — will verify URLs via web search
        {"name": "Char Rooftop Bar Bangkok", "search": "Char Rooftop Bar Hotel Indigo Bangkok"},
        {"name": "Scarlett Wine Bar Bangkok", "search": "Scarlett Wine Bar Pullman Bangkok"},
        {"name": "RedBar Bangkok", "search": "RedBar Thonglor Bangkok"},
        {"name": "The Iron Fairies Bangkok", "search": "Iron Fairies Thonglor Bangkok"},
        {"name": "Silom Soi 4 Bangkok", "search": "Silom Soi 4 nightlife Bangkok"},
        {"name": "Khao San Road Bangkok", "search": "Khao San Road nightlife Bangkok"},
        {"name": "Nana Plaza Bangkok", "search": "Nana Plaza nightlife Bangkok"},
        {"name": "Soi Cowboy Bangkok", "search": "Soi Cowboy nightlife Bangkok"},
        {"name": "Bangla Road Phuket", "search": "Bangla Road nightlife Phuket"},
        {"name": "Tiger Bar Phuket", "search": "Tiger Bar Bangla Road Phuket"},
        {"name": "White Night Phuket", "search": "White Night club Phuket"},
        {"name": "Nicky's Handlebar Chiang Mai", "search": "Nicky's Handlebar Chiang Mai bar"},
        {"name": "Boy Blues Bar Chiang Mai", "search": "Boy Blues Bar Chiang Mai"},
        {"name": "Reggae Bar Koh Phi Phi", "search": "Reggae Bar Koh Phi Phi"},
        {"name": "Slippery Club Koh Phi Phi", "search": "Slippery Club Koh Phi Phi"},
        {"name": "The Roof Gastrobar Bangkok", "search": "The Roof Gastrobar Siam@Siam Bangkok"},
        {"name": "Sing Sing Phuket", "search": "Sing Sing bar Phuket nightlife"},
        {"name": "Sound Phuket", "search": "Sound nightclub Phuket Patong"},
        {"name": "Ba Ba Beach Club Phuket", "search": "Baba Beach Club Natai Phuket"},
        {"name": "Illuzion Phuket", "search": "Illuzion nightclub Patong Phuket"},
    ],
    "Cinema & Entertainment": [
        {"name": "SF Cinema City", "search": "SF Cinema City Thailand official"},
        {"name": "Major Cineplex Thailand", "search": "Major Cineplex Thailand official"},
        {"name": "Paragon Cineplex", "search": "Paragon Cineplex Siam Paragon Bangkok"},
        {"name": "Icon Cineconic", "search": "Icon Cineconic IconSiam Bangkok cinema"},
        {"name": "House RCA", "search": "House RCA cinema Bangkok"},
        {"name": "Escape Room by Komnata", "search": "Komnata Quest escape room Bangkok"},
        {"name": "Brain Out Escape Room", "search": "Brain Out escape room Bangkok"},
        {"name": "The Great Hornbills Zipline", "search": "Great Hornbills Zipline Chiang Mai"},
        {"name": "Mekhala River Cruise", "search": "Mekhala River Cruise Bangkok"},
        {"name": "Chao Phraya Princess Cruise", "search": "Chao Phraya Princess dinner cruise Bangkok"},
        {"name": "White Orchid Dinner Cruise", "search": "White Orchid River Cruise Bangkok"},
        {"name": "Muay Thai Live Show", "search": "Muay Thai Live show Asiatique Bangkok"},
        {"name": "Siam Amazing Park", "search": "Siam Amazing Park Bangkok"},
        {"name": "Flight Experience Bangkok", "search": "Flight Experience flight simulator Bangkok"},
        {"name": "Harborland Thailand", "search": "Harbor Land playground Thailand"},
        {"name": "SuperPark Thailand", "search": "SuperPark Thailand indoor activity"},
        {"name": "Macao Imperial Tea House", "search": "Macao Imperial tea house Bangkok entertainment"},
        {"name": "Funarium Bangkok", "search": "Funarium Bangkok kids playground"},
        {"name": "Snow Town Bangkok", "search": "Snow Town Gateway Ekkamai Bangkok"},
        {"name": "Lazgam Laser Game Bangkok", "search": "Lazgam laser tag Bangkok"},
    ],
    "Lifestyle & Experiences": [
        {"name": "True Digital Park", "search": "True Digital Park coworking Bangkok"},
        {"name": "Glowfish Coworking", "search": "Glowfish coworking Bangkok"},
        {"name": "The Work Loft", "search": "The Work Loft coworking Bangkok Sathorn"},
        {"name": "Garage Society Bangkok", "search": "Garage Society coworking Bangkok"},
        {"name": "MATCH Fit Bangkok", "search": "MATCH Fit gym Bangkok"},
        {"name": "Absolute Muay Thai", "search": "Absolute Muay Thai Bangkok gym"},
        {"name": "Baan Orapin Chiang Mai", "search": "Baan Orapin boutique Chiang Mai"},
        {"name": "Siam Center Bangkok", "search": "Siam Center shopping Bangkok official"},
        {"name": "Central Embassy Bangkok", "search": "Central Embassy luxury mall Bangkok official"},
        {"name": "The Crystal SB Ratchapruek", "search": "The Crystal SB Ratchapruek Bangkok"},
        {"name": "Union Space Coworking", "search": "Union Space coworking Bangkok"},
        {"name": "AW Space Bangkok", "search": "AW Space coworking Bangkok"},
        {"name": "Draper Startup House Bangkok", "search": "Draper Startup House Bangkok coworking"},
    ],
    "Transport & Transfer Services": [
        {"name": "BTS Skytrain", "search": "BTS Skytrain Bangkok official website"},
        {"name": "MRT Bangkok", "search": "MRT Bangkok metro official website"},
        {"name": "Airport Rail Link Bangkok", "search": "Airport Rail Link Bangkok official"},
        {"name": "Thai Lion Air", "search": "Thai Lion Air official website"},
        {"name": "VietJet Air Thailand", "search": "VietJet Air Thailand flights official"},
        {"name": "Chao Phraya Express Boat", "search": "Chao Phraya Express Boat official"},
        {"name": "BKK Taxi 24", "search": "BKK Taxi 24 Bangkok taxi service"},
        {"name": "Seatran Ferry Koh Samui", "search": "Seatran Discovery ferry Koh Samui official"},
        {"name": "Lomprayah Ferry", "search": "Lomprayah catamaran ferry Thailand official"},
        {"name": "Songserm Express", "search": "Songserm Express boat Thailand"},
        {"name": "Thai Railway", "search": "State Railway Thailand official website"},
        {"name": "Avis Thailand", "search": "Avis car rental Thailand official"},
    ],
    "MICE & Event DMCs": [
        {"name": "TCEB Thailand", "search": "Thailand Convention Exhibition Bureau official"},
        {"name": "Centara Grand Convention Centre", "search": "Centara Grand convention centre Bangkok official"},
        {"name": "BITEC Bangkok", "search": "BITEC Bangkok International Trade Exhibition Centre official"},
        {"name": "IMPACT Exhibition Centre", "search": "IMPACT Muang Thong Thani exhibition Bangkok official"},
        {"name": "Royal Paragon Hall", "search": "Royal Paragon Hall Siam Paragon Bangkok events"},
        {"name": "True Icon Hall", "search": "True Icon Hall IconSiam Bangkok events"},
        {"name": "Avani Riverside Bangkok Events", "search": "Avani Riverside Bangkok hotel meetings events"},
    ],
    "Adventure & Outdoor Operators": [
        {"name": "Phuket Elephant Sanctuary", "search": "Phuket Elephant Sanctuary official"},
        {"name": "Elephant Nature Park", "search": "Elephant Nature Park Chiang Mai official"},
        {"name": "Simba Sea Trips", "search": "Simba Sea Trips Phuket boat tours"},
        {"name": "John Gray Sea Canoe", "search": "John Gray Sea Canoe Phuket Phang Nga"},
        {"name": "Santana Biking Chiang Mai", "search": "Santana Biking Adventures Chiang Mai"},
    ],
    "Food & Culinary Operators": [
        {"name": "Silom Thai Cooking School", "search": "Silom Thai Cooking School Bangkok official"},
        {"name": "Manohra Cruises", "search": "Manohra Cruises dinner Bangkok Anantara"},
        {"name": "Issaya Siamese Club", "search": "Issaya Siamese Club restaurant Bangkok official"},
        {"name": "Nahm Restaurant", "search": "Nahm restaurant Bangkok COMO official"},
        {"name": "Paste Bangkok", "search": "Paste Bangkok restaurant official"},
    ],
    "Boutique Hotels & Hostels": [
        {"name": "Once Again Hostel Bangkok", "search": "Once Again Hostel Bangkok official"},
        {"name": "NapPark Hostel Bangkok", "search": "NapPark Hostel Khao San Bangkok official"},
        {"name": "Chillax Heritage Bangkok", "search": "Chillax Heritage boutique hotel Bangkok"},
        {"name": "Tara Mantra Cha-Am", "search": "Tara Mantra resort Cha-Am"},
        {"name": "Makkasan Hostel Bangkok", "search": "Makkasan Hostel Bangkok official"},
        {"name": "Phranakorn Nornlen Bangkok", "search": "Phranakorn Nornlen boutique hotel Bangkok"},
        {"name": "Old Capital Bike Inn", "search": "Old Capital Bike Inn Bangkok hotel"},
        {"name": "Chern Hostel Bangkok", "search": "Chern Hostel Bangkok official"},
        {"name": "Hom Hostel Bangkok", "search": "Hom Hostel and Cooking Club Bangkok"},
    ],
}


# ══════════════════════════════════════════════════════════════
# MAIN PIPELINE: Search, verify, and add real vendors
# ══════════════════════════════════════════════════════════════

def main():
    # Load current data
    with open(JSON_PATH) as f:
        vendors = json.load(f)

    # Build name index for dedup
    name_index = {}
    for i, v in enumerate(vendors):
        name_index[normalize_name(v["name"])] = i

    counts = Counter(v["category"] for v in vendors)
    print(f"Current vendors: {len(vendors)}")
    print(f"\nCategories needing vendors:")
    needed = {}
    for cat in sorted(counts.keys()):
        c = counts[cat]
        if c < 50:
            needed[cat] = 50 - c
            print(f"  {cat:45s} {c:4d}  (need {50-c})")

    if not needed:
        print("All categories >= 50!")
        return

    total_needed = sum(needed.values())
    print(f"\nTotal vendors needed: {total_needed}")
    print(f"\n{'='*70}")
    print("PHASE 1: Search & Verify Real Business URLs")
    print(f"{'='*70}")

    added_total = 0

    for cat, need_count in needed.items():
        print(f"\n--- {cat} (need {need_count}) ---")
        businesses = BUSINESSES_TO_VERIFY.get(cat, [])
        added_this_cat = 0

        for biz in businesses:
            if added_this_cat >= need_count:
                break

            name = biz["name"]
            search_query = biz.get("search", f"{name} Thailand official website")

            # Check if already exists
            norm = normalize_name(name)
            is_dupe = False
            for existing_norm in name_index:
                if norm == existing_norm:
                    is_dupe = True
                    break
                if len(norm) > 5 and len(existing_norm) > 5:
                    if norm in existing_norm or existing_norm in norm:
                        is_dupe = True
                        break
            if is_dupe:
                print(f"  ⏭️  {name} (already exists)")
                continue

            # Search Google for real URL
            print(f"  🔍 Searching: {name}...")
            url = google_search_url(name, "Thailand")
            time.sleep(2)

            if url:
                vendor = {
                    "name": name,
                    "category": cat,
                    "url": url,
                    "location": "Thailand",
                    "source": "google-verified",
                }
                vendors.append(vendor)
                name_index[norm] = len(vendors) - 1
                added_this_cat += 1
                added_total += 1
                print(f"  ✅ {name} → {url[:60]}")
            else:
                print(f"  ❌ {name} — no valid URL found, skipping")

        print(f"  → Added {added_this_cat}/{need_count} to {cat}")

    # Save
    with open(JSON_PATH, "w") as f:
        json.dump(vendors, f, indent=2, ensure_ascii=False)

    # Re-export CSVs
    fieldnames = ["category", "name", "url", "location", "description",
                  "type", "source", "phone", "email", "address"]
    master_csv = os.path.join(OUTPUT_DIR, "tirak_thailand_vendors.csv")
    with open(master_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for v in vendors:
            writer.writerow(v)

    by_cat = {}
    for v in vendors:
        by_cat.setdefault(v.get("category", "Uncategorized"), []).append(v)
    for cat, cat_vendors in by_cat.items():
        safe = cat.lower().replace(" & ", "_").replace(" ", "_")
        path = os.path.join(OUTPUT_DIR, f"tirak_vendors_{safe}.csv")
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for v in cat_vendors:
                writer.writerow(v)

    # Final report
    final_counts = Counter(v["category"] for v in vendors)
    print(f"\n{'='*70}")
    print("FINAL REPORT")
    print(f"{'='*70}")
    print(f"Total vendors: {len(vendors)} (+{added_total} verified)")
    all_met = True
    for cat in sorted(final_counts.keys()):
        c = final_counts[cat]
        status = "✅" if c >= 50 else f"🔴 need {50-c}"
        if c < 50:
            all_met = False
        print(f"  {cat:45s} {c:4d}  {status}")
    print(f"\nAll categories >= 50: {'YES ✅' if all_met else 'NO — need more scraping 🔴'}")

    # Source breakdown
    sources = Counter(v.get("source", "none") for v in vendors)
    print(f"\nData sources:")
    for src, count in sources.most_common():
        print(f"  {src:40s} {count:4d}")


if __name__ == "__main__":
    main()
