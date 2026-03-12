"""
Tirak Vendor Contact Enrichment — Scrape emails & phones from vendor websites.
Reads ~/tirak_thailand_vendors.json, visits each vendor URL, extracts contact info,
and writes enriched data back.

Usage: source ~/scrapling-env/bin/activate && python ~/enrich_vendor_contacts.py
"""
import json
import logging
import os
import re
import ssl
import time
from collections import Counter
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen, Request

from scrapling import Selector

# ═══════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════

JSON_PATH = os.path.expanduser("~/tirak_thailand_vendors.json")
LOG_PATH = os.path.expanduser("~/enrich_vendor_contacts.log")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

# Delay between requests (be polite)
FETCH_DELAY = 0.5

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_PATH, mode="w"),
    ],
)
log = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
# PATTERNS
# ═══════════════════════════════════════════════════════════════════

# Email: match mailto: links and inline email patterns
EMAIL_RE = re.compile(
    r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',
    re.IGNORECASE
)

# Phone: match Thai phone numbers and international formats
PHONE_PATTERNS = [
    # Thai mobile: +66 followed by digits
    re.compile(r'\+66[\s\-.]?\d[\s\-.]?\d{3,4}[\s\-.]?\d{3,4}'),
    # Thai landline with area code: 0-2-xxx-xxxx or 02-xxx-xxxx
    re.compile(r'0[\s\-.]?[2-9][\s\-.]?\d{3,4}[\s\-.]?\d{3,4}'),
    # International format: +XX-XXX-XXX-XXXX
    re.compile(r'\+\d{1,3}[\s\-.]?\d{1,4}[\s\-.]?\d{3,4}[\s\-.]?\d{3,4}'),
    # General: (0XX) XXX-XXXX
    re.compile(r'\(\d{2,4}\)\s?\d{3,4}[\s\-.]?\d{3,4}'),
]

# Junk email patterns to skip (substring match on domain)
JUNK_EMAIL_DOMAINS = {
    'example.com', 'test.com', 'sentry.io', 'w3.org',
    'schema.org', 'googleapis.com', 'google.com', 'facebook.com',
    'wixpress.com', 'cloudflare.com', 'wordpress.org',
    'dmcfinder.co.uk', 'dmcfinder.com',  # aggregator contact, not vendor's
}

JUNK_EMAIL_PREFIXES = {
    'noreply', 'no-reply', 'donotreply', 'webmaster', 'admin',
    'postmaster', 'mailer-daemon', 'hostmaster', 'abuse',
}


def is_junk_email(email):
    """Filter out non-business emails."""
    email = email.lower().strip()
    # Skip image file extensions caught by regex
    if any(email.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.css', '.js']):
        return True
    domain = email.split('@')[-1]
    # Substring match: sentry.io matches o244205.ingest.sentry.io
    if any(junk in domain for junk in JUNK_EMAIL_DOMAINS):
        return True
    prefix = email.split('@')[0]
    if prefix in JUNK_EMAIL_PREFIXES:
        return True
    # Skip very long emails (likely false positives)
    if len(email) > 60:
        return True
    return False


def clean_phone(phone_str):
    """Normalize phone number string."""
    # Strip everything except digits, +, spaces, dashes
    cleaned = re.sub(r'[^\d+\-\s()]', '', phone_str).strip()
    # Must have at least 8 digits
    digits_only = re.sub(r'[^\d]', '', cleaned)
    if len(digits_only) < 8 or len(digits_only) > 15:
        return None
    # Skip suspicious patterns (repeated digits, clearly fake)
    if len(set(digits_only)) <= 2:  # e.g., 0666666666
        return None
    # Must look like a Thai number or start with +
    if not (cleaned.startswith('+66') or cleaned.startswith('0') or cleaned.startswith('+')):
        return None
    return cleaned


# ═══════════════════════════════════════════════════════════════════
# FETCHER
# ═══════════════════════════════════════════════════════════════════

def fetch_page(url, timeout=8):
    """Fetch URL and return raw HTML string, or None on failure."""
    try:
        req = Request(url, headers=HEADERS)
        resp = urlopen(req, timeout=timeout, context=SSL_CTX)
        html = resp.read().decode("utf-8", errors="ignore")
        return html
    except Exception as e:
        log.debug(f"  Fetch error {url}: {e}")
        return None


def find_contact_page_url(html, base_url):
    """Look for a link to a contact page in the HTML."""
    try:
        sel = Selector(html)
        for a in sel.css('a'):
            href = a.attrib.get('href', '')
            text = (a.text or '').lower().strip()
            href_lower = href.lower()
            # Match contact-related links
            if any(kw in href_lower for kw in ['contact', 'about', 'reach-us', 'get-in-touch']):
                return urljoin(base_url, href)
            if any(kw in text for kw in ['contact', 'about us', 'reach us', 'get in touch']):
                return urljoin(base_url, href)
    except Exception:
        pass
    return None


def extract_contacts_from_html(html):
    """Extract emails and phones from raw HTML string."""
    emails = set()
    phones = set()

    if not html:
        return emails, phones

    # Extract emails
    for match in EMAIL_RE.findall(html):
        if not is_junk_email(match):
            emails.add(match.lower().strip())

    # Extract phones
    for pattern in PHONE_PATTERNS:
        for match in pattern.findall(html):
            cleaned = clean_phone(match)
            if cleaned:
                phones.add(cleaned)

    return emails, phones


# ═══════════════════════════════════════════════════════════════════
# MAIN ENRICHMENT LOGIC
# ═══════════════════════════════════════════════════════════════════

def enrich_vendor(vendor):
    """Visit vendor URL and try to extract email/phone. Returns (email, phone) or (None, None)."""
    url = vendor.get('url', '')
    if not url or not url.startswith('http'):
        return None, None

    # Skip aggregator URLs (hostelworld, cookly, etc.) — contact info won't be theirs
    domain = urlparse(url).netloc.lower()
    skip_domains = [
        'hostelworld.com', 'cookly.me', 'thailandferrybooking.com',
        'siam2nite.com', 'bkmagazine.com', 'tripadvisor.com',
        'booking.com', 'agoda.com', 'klook.com', 'viator.com',
        'dmcfinder.co.uk', 'dmcfinder.com',  # directory pages, not vendor sites
    ]
    if any(sd in domain for sd in skip_domains):
        return None, None

    all_emails = set()
    all_phones = set()

    # Step 1: Fetch main page
    html = fetch_page(url)
    if html:
        emails, phones = extract_contacts_from_html(html)
        all_emails.update(emails)
        all_phones.update(phones)

        # Step 2: If we didn't find email, try the contact page
        if not all_emails:
            contact_url = find_contact_page_url(html, url)
            if contact_url and contact_url != url:
                time.sleep(0.3)
                contact_html = fetch_page(contact_url)
                if contact_html:
                    emails2, phones2 = extract_contacts_from_html(contact_html)
                    all_emails.update(emails2)
                    all_phones.update(phones2)

    # Pick best email (prefer info@, contact@, hello@, booking@ over random)
    best_email = None
    if all_emails:
        priority_prefixes = ['info', 'contact', 'hello', 'booking', 'enquir', 'reserv', 'sales']
        for prefix in priority_prefixes:
            for e in all_emails:
                if e.startswith(prefix):
                    best_email = e
                    break
            if best_email:
                break
        if not best_email:
            best_email = sorted(all_emails)[0]  # alphabetical fallback

    # Pick best phone (prefer +66 or 0X numbers)
    best_phone = None
    if all_phones:
        # Prefer Thai numbers
        thai_phones = [p for p in all_phones if p.startswith('+66') or p.startswith('0')]
        if thai_phones:
            best_phone = sorted(thai_phones, key=len, reverse=True)[0]
        else:
            best_phone = sorted(all_phones, key=len, reverse=True)[0]

    return best_email, best_phone


def main():
    log.info("=" * 60)
    log.info("TIRAK VENDOR CONTACT ENRICHMENT")
    log.info("=" * 60)

    # Load vendors
    with open(JSON_PATH, "r") as f:
        data = json.load(f)
    vendors = data.get("vendors", data) if isinstance(data, dict) else data
    log.info(f"Loaded {len(vendors)} vendors")

    # Pre-enrichment stats
    has_email_before = sum(1 for v in vendors if v.get('email'))
    has_phone_before = sum(1 for v in vendors if v.get('phone'))
    log.info(f"BEFORE: {has_email_before} emails ({has_email_before*100//len(vendors)}%), "
             f"{has_phone_before} phones ({has_phone_before*100//len(vendors)}%)")

    # Find vendors needing enrichment (no email OR no phone)
    needs_enrichment = []
    for i, v in enumerate(vendors):
        if not v.get('email') or not v.get('phone'):
            needs_enrichment.append(i)

    log.info(f"Vendors needing enrichment: {len(needs_enrichment)}")

    enriched_count = 0
    new_emails = 0
    new_phones = 0
    errors = 0

    for count, idx in enumerate(needs_enrichment, 1):
        v = vendors[idx]
        name = v.get('name', 'Unknown')
        url = v.get('url', '')

        if count % 25 == 0:
            log.info(f"Progress: {count}/{len(needs_enrichment)} "
                     f"(+{new_emails} emails, +{new_phones} phones)")

        try:
            email, phone = enrich_vendor(v)

            updated = False
            if email and not v.get('email'):
                vendors[idx]['email'] = email
                new_emails += 1
                updated = True

            if phone and not v.get('phone'):
                vendors[idx]['phone'] = phone
                new_phones += 1
                updated = True

            if updated:
                enriched_count += 1
                log.info(f"  [{count}] {name}: "
                         f"email={email or '—'}, phone={phone or '—'}")

        except Exception as e:
            errors += 1
            log.debug(f"  [{count}] Error on {name}: {e}")

        time.sleep(FETCH_DELAY)

    # Save updated data
    log.info("\nSaving enriched data...")
    save_data = {"vendors": vendors} if isinstance(data, dict) and "vendors" in data else vendors
    with open(JSON_PATH, "w") as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False)

    # Post-enrichment stats
    has_email_after = sum(1 for v in vendors if v.get('email'))
    has_phone_after = sum(1 for v in vendors if v.get('phone'))

    log.info("\n" + "=" * 60)
    log.info("ENRICHMENT RESULTS")
    log.info("=" * 60)
    log.info(f"Vendors processed: {len(needs_enrichment)}")
    log.info(f"Vendors enriched:  {enriched_count}")
    log.info(f"New emails found:  {new_emails}")
    log.info(f"New phones found:  {new_phones}")
    log.info(f"Errors:            {errors}")
    log.info(f"")
    log.info(f"BEFORE → AFTER:")
    log.info(f"  Emails: {has_email_before} → {has_email_after} "
             f"({has_email_before*100//len(vendors)}% → {has_email_after*100//len(vendors)}%)")
    log.info(f"  Phones: {has_phone_before} → {has_phone_after} "
             f"({has_phone_before*100//len(vendors)}% → {has_phone_after*100//len(vendors)}%)")

    # Category breakdown
    log.info(f"\nPer-Category Contact Coverage:")
    from collections import Counter
    cat_counts = Counter()
    cat_email = Counter()
    cat_phone = Counter()
    for v in vendors:
        cat = v.get('category', 'Unknown')
        cat_counts[cat] += 1
        if v.get('email'):
            cat_email[cat] += 1
        if v.get('phone'):
            cat_phone[cat] += 1

    for cat in sorted(cat_counts.keys()):
        total = cat_counts[cat]
        em = cat_email[cat]
        ph = cat_phone[cat]
        log.info(f"  {cat}: {em}/{total} emails ({em*100//total}%), "
                 f"{ph}/{total} phones ({ph*100//total}%)")


if __name__ == "__main__":
    main()
