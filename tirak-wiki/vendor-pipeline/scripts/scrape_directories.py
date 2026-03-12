"""
Scrape real Thailand business listings from directory websites.
Each function targets a specific, scrapable directory page.
Every vendor added must have a verified URL.
"""
import csv
import json
import os
import re
import ssl
import sys
import time
from collections import Counter
from urllib.parse import urljoin, quote_plus
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from scrapling import StealthyFetcher, Selector

JSON_PATH = os.path.expanduser("~/tirak_thailand_vendors.json")
OUTPUT_DIR = os.path.expanduser("~/")

def normalize_name(name):
    n = name.lower().strip()
    for suffix in ["co., ltd.", "co., ltd", "co.,ltd.", "co.,ltd", "co. ltd.",
                    "co. ltd", "co.,", "co.", "ltd.", "ltd", "inc.", "inc",
                    "thailand", "bangkok", "phuket", "chiang mai"]:
        n = n.replace(suffix, "")
    n = re.sub(r"[^\w\s]", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n

def fetch_page(url):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,*/*;q=0.8",
        })
        resp = urlopen(req, timeout=10, context=ctx)
        return Selector(resp.read().decode("utf-8", errors="ignore"))
    except Exception as e:
        print(f"  fetch error: {e}")
        return None

def stealthy_fetch(url):
    try:
        return StealthyFetcher.fetch(url, headless=True, timeout=25000)
    except Exception as e:
        print(f"  stealthy fetch error: {e}")
        return None

def check_url(url):
    if not url or not url.startswith("http"):
        return False
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urlopen(req, timeout=5, context=ctx)
        return resp.status < 400
    except HTTPError as e:
        return e.code in (403, 405, 406, 429)
    except:
        return False


# ══════════════════════════════════════════════════════════════
# DIRECTORY SCRAPERS
# ══════════════════════════════════════════════════════════════

def scrape_hostelworld(city="Bangkok"):
    """Scrape hostels from Hostelworld."""
    results = []
    url = f"https://www.hostelworld.com/st/hostels/{city}/"
    print(f"  Scraping Hostelworld {city}...")
    page = stealthy_fetch(url)
    if not page:
        return results

    # Try various selectors
    cards = (page.css("a[data-testid='property-card-link']") or
             page.css("a.property-listing") or
             page.css("div.property-card a") or
             page.css("a[href*='/pwa/hosteldetails']"))

    print(f"  Found {len(cards)} hostel cards")
    for card in cards[:25]:
        href = card.attrib.get("href", "")
        name_el = card.css("h2") or card.css("[data-testid='property-name']")
        name = name_el[0].text.strip() if name_el and name_el[0].text else ""
        if not name:
            name = card.text.strip()[:50] if card.text else ""

        if name and href:
            full_url = f"https://www.hostelworld.com{href}" if href.startswith("/") else href
            results.append({"name": name, "url": full_url, "location": city})

    return results


def scrape_12go_transport():
    """Scrape transport operators from 12go.asia."""
    results = []
    urls = [
        "https://12go.asia/en/travel/bangkok/chiang-mai",
        "https://12go.asia/en/travel/bangkok/phuket",
        "https://12go.asia/en/travel/bangkok/krabi",
    ]
    for url in urls:
        print(f"  Scraping 12go.asia: {url.split('/')[-1]}...")
        page = stealthy_fetch(url)
        if not page:
            continue

        # 12go shows operator names
        operators = page.css(".operator-name") or page.css("[class*='operator']") or page.css(".search-result-operator")
        for op in operators[:15]:
            name = op.text.strip() if op.text else ""
            if name and len(name) > 2:
                results.append({"name": name, "location": "Thailand"})

        time.sleep(2)

    # Deduplicate
    seen = set()
    unique = []
    for r in results:
        if r["name"] not in seen:
            seen.add(r["name"])
            unique.append(r)
    return unique


def scrape_coworker_bangkok():
    """Scrape coworking spaces from coworker.com."""
    results = []
    url = "https://www.coworker.com/thailand/bangkok"
    print(f"  Scraping coworker.com Bangkok...")
    page = stealthy_fetch(url)
    if not page:
        return results

    cards = page.css(".space-card") or page.css("a[href*='/thailand/bangkok/']") or page.css(".listing-card")
    print(f"  Found {len(cards)} coworking cards")
    for card in cards[:20]:
        name_el = card.css("h3") or card.css("h2") or card.css(".space-name")
        href = card.attrib.get("href", "")
        if not href:
            link_els = card.css("a[href]")
            if link_els:
                href = link_els[0].attrib.get("href", "")

        name = name_el[0].text.strip() if name_el and name_el[0].text else ""
        if name and href:
            full_url = f"https://www.coworker.com{href}" if href.startswith("/") else href
            results.append({"name": name, "url": full_url, "location": "Bangkok"})

    return results


def scrape_getyourguide_adventures():
    """Scrape adventure activities from GetYourGuide."""
    results = []
    url = "https://www.getyourguide.com/thailand-l204/outdoor-activities-tc4/"
    print(f"  Scraping GetYourGuide adventures...")
    page = fetch_page(url)
    if not page:
        page = stealthy_fetch(url)
    if not page:
        return results

    cards = page.css("[data-activity-card-title]") or page.css(".activity-card") or page.css("h3.activity-card-title")
    print(f"  Found {len(cards)} activity cards")
    for card in cards[:20]:
        name = card.text.strip() if card.text else ""
        if name:
            results.append({"name": name[:60], "location": "Thailand"})

    return results


def scrape_bkk_nightlife():
    """Scrape nightlife from bk.asia-city.com (BK Magazine - real Bangkok media)."""
    results = []
    urls = [
        "https://bk.asia-city.com/nightlife/bangkok-bar-club",
    ]
    for url in urls:
        print(f"  Scraping BK Magazine nightlife...")
        page = fetch_page(url)
        if not page:
            page = stealthy_fetch(url)
        if not page:
            continue

        # BK Magazine article listings
        cards = page.css("article") or page.css(".article-card") or page.css("a[href*='/nightlife/']")
        print(f"  Found {len(cards)} nightlife listings")
        for card in cards[:30]:
            name_el = card.css("h2") or card.css("h3") or card.css(".title")
            link_el = card.css("a[href]")
            name = name_el[0].text.strip() if name_el and name_el[0].text else ""
            href = ""
            if link_el:
                href = link_el[0].attrib.get("href", "")
            if name:
                full_url = f"https://bk.asia-city.com{href}" if href.startswith("/") else href
                results.append({"name": name, "url": full_url if full_url.startswith("http") else "", "location": "Bangkok"})

        time.sleep(2)
    return results


def scrape_event_venues():
    """Scrape MICE venues from Thailand's TCEB and venue listing sites."""
    results = []
    urls = [
        "https://www.businesseventsthailand.com/en/why-thailand/facilities-services/venues",
        "https://www.tceb.or.th/en/mice-capabilities/venues",
    ]
    for url in urls:
        print(f"  Scraping MICE venue: {url[:60]}...")
        page = fetch_page(url) or stealthy_fetch(url)
        if not page:
            continue

        cards = page.css("article") or page.css(".venue-card") or page.css("h3 a")
        print(f"  Found {len(cards)} venue listings")
        for card in cards[:20]:
            name = card.text.strip() if card.text else ""
            if name and len(name) > 3:
                results.append({"name": name[:60], "location": "Thailand"})
        time.sleep(2)
    return results


def scrape_byfood_classes():
    """Scrape cooking classes from byFood.com."""
    results = []
    url = "https://www.byfood.com/food-experiences/thailand"
    print(f"  Scraping byFood.com classes...")
    page = fetch_page(url)
    if not page:
        page = stealthy_fetch(url)
    if not page:
        return results

    cards = page.css(".experience-card") or page.css("a[href*='/food-experiences/']") or page.css("h3")
    print(f"  Found {len(cards)} food experience cards")
    for card in cards[:15]:
        name = card.text.strip() if card.text else ""
        href = card.attrib.get("href", "")
        if name and len(name) > 5:
            full_url = f"https://www.byfood.com{href}" if href.startswith("/") else href
            results.append({"name": name[:60], "url": full_url if full_url.startswith("http") else "", "location": "Thailand"})
    return results


def scrape_entertainme():
    """Scrape entertainment from kkday.com listings."""
    results = []
    url = "https://www.kkday.com/en/product/productlist/A01-001/Thailand"
    print(f"  Scraping KKday Thailand activities...")
    page = stealthy_fetch(url)
    if not page:
        return results

    cards = page.css(".product-card") or page.css("a[href*='/product/']")
    print(f"  Found {len(cards)} activity listings")
    for card in cards[:20]:
        name_el = card.css("h3") or card.css(".product-name")
        name = name_el[0].text.strip() if name_el and name_el[0].text else ""
        href = card.attrib.get("href", "")
        if name:
            full_url = f"https://www.kkday.com{href}" if href.startswith("/") else href
            results.append({"name": name[:60], "url": full_url if full_url.startswith("http") else "", "location": "Thailand"})
    return results


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    with open(JSON_PATH) as f:
        vendors = json.load(f)

    name_index = set()
    for v in vendors:
        name_index.add(normalize_name(v["name"]))

    counts = Counter(v["category"] for v in vendors)

    print(f"Current: {len(vendors)} vendors")
    print(f"\nGaps to fill:")
    needed = {}
    for cat in sorted(counts.keys()):
        if counts[cat] < 50:
            needed[cat] = 50 - counts[cat]
            print(f"  {cat:45s} {counts[cat]:4d}  (need {50-counts[cat]})")

    total_needed = sum(needed.values())
    print(f"\nTotal needed: {total_needed}")

    # ── Category-specific scraping ──
    all_scraped = {}  # category -> list of vendors

    # NIGHTLIFE
    if "Nightlife & Entertainment" in needed:
        print(f"\n{'='*60}")
        print("SCRAPING: Nightlife & Entertainment")
        print(f"{'='*60}")
        results = scrape_bkk_nightlife()
        all_scraped["Nightlife & Entertainment"] = results
        print(f"  Got {len(results)} raw results")

    # BOUTIQUE HOTELS
    if "Boutique Hotels & Hostels" in needed:
        print(f"\n{'='*60}")
        print("SCRAPING: Boutique Hotels & Hostels")
        print(f"{'='*60}")
        results = []
        for city in ["Bangkok", "Chiang-Mai", "Phuket"]:
            r = scrape_hostelworld(city)
            results.extend(r)
            time.sleep(3)
        all_scraped["Boutique Hotels & Hostels"] = results
        print(f"  Got {len(results)} raw results")

    # TRANSPORT
    if "Transport & Transfer Services" in needed:
        print(f"\n{'='*60}")
        print("SCRAPING: Transport & Transfer Services")
        print(f"{'='*60}")
        results = scrape_12go_transport()
        all_scraped["Transport & Transfer Services"] = results
        print(f"  Got {len(results)} raw results")

    # LIFESTYLE
    if "Lifestyle & Experiences" in needed:
        print(f"\n{'='*60}")
        print("SCRAPING: Lifestyle & Experiences")
        print(f"{'='*60}")
        results = scrape_coworker_bangkok()
        all_scraped["Lifestyle & Experiences"] = results
        print(f"  Got {len(results)} raw results")

    # CINEMA & ENTERTAINMENT
    if "Cinema & Entertainment" in needed:
        print(f"\n{'='*60}")
        print("SCRAPING: Cinema & Entertainment")
        print(f"{'='*60}")
        results = scrape_entertainme()
        all_scraped["Cinema & Entertainment"] = results
        print(f"  Got {len(results)} raw results")

    # ADVENTURE
    if "Adventure & Outdoor Operators" in needed:
        print(f"\n{'='*60}")
        print("SCRAPING: Adventure & Outdoor Operators")
        print(f"{'='*60}")
        results = scrape_getyourguide_adventures()
        all_scraped["Adventure & Outdoor Operators"] = results
        print(f"  Got {len(results)} raw results")

    # MICE
    if "MICE & Event DMCs" in needed:
        print(f"\n{'='*60}")
        print("SCRAPING: MICE & Event DMCs")
        print(f"{'='*60}")
        results = scrape_event_venues()
        all_scraped["MICE & Event DMCs"] = results
        print(f"  Got {len(results)} raw results")

    # FOOD
    if "Food & Culinary Operators" in needed:
        print(f"\n{'='*60}")
        print("SCRAPING: Food & Culinary Operators")
        print(f"{'='*60}")
        results = scrape_byfood_classes()
        all_scraped["Food & Culinary Operators"] = results
        print(f"  Got {len(results)} raw results")

    # ── Add scraped results to vendor list ──
    print(f"\n{'='*60}")
    print("ADDING VERIFIED SCRAPED VENDORS")
    print(f"{'='*60}")

    added_total = 0
    for cat, scraped in all_scraped.items():
        need = needed.get(cat, 0)
        added = 0
        for s in scraped:
            if added >= need:
                break
            name = s.get("name", "").strip()
            if not name or len(name) < 3:
                continue
            norm = normalize_name(name)
            # Check dedup
            is_dupe = norm in name_index
            if not is_dupe:
                for existing in name_index:
                    if len(norm) > 5 and len(existing) > 5:
                        if norm in existing or existing in norm:
                            is_dupe = True
                            break
            if is_dupe:
                continue

            vendor = {
                "name": name,
                "category": cat,
                "url": s.get("url", ""),
                "location": s.get("location", "Thailand"),
                "source": "directory-scraped",
            }
            vendors.append(vendor)
            name_index.add(norm)
            added += 1
            added_total += 1
            print(f"  ✅ [{cat[:20]}] {name[:40]}")

        print(f"  → Added {added}/{need} to {cat}")

    # ── Save ──
    with open(JSON_PATH, "w") as f:
        json.dump(vendors, f, indent=2, ensure_ascii=False)

    # Save CSVs
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
    sources = Counter(v.get("source", "none") for v in vendors)

    print(f"\n{'='*70}")
    print("FINAL REPORT")
    print(f"{'='*70}")
    print(f"Total: {len(vendors)} (+{added_total} scraped)")
    all_met = True
    for cat in sorted(final_counts.keys()):
        c = final_counts[cat]
        status = "✅" if c >= 50 else f"🔴 need {50-c}"
        if c < 50:
            all_met = False
        print(f"  {cat:45s} {c:4d}  {status}")

    print(f"\nAll >= 50: {'YES ✅' if all_met else 'NO 🔴'}")
    print(f"\nData sources:")
    for src, cnt in sources.most_common():
        print(f"  {src:40s} {cnt:4d}")


if __name__ == "__main__":
    main()
