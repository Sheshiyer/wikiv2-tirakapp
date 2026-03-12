"""
Validate ALL vendor URLs by actually fetching them.
Flags vendors as: LIVE, DEAD, REDIRECT, ERROR
Outputs a validation report.
"""
import json
import os
import ssl
import sys
import time
from collections import Counter
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

JSON_PATH = os.path.expanduser("~/tirak_thailand_vendors.json")
REPORT_PATH = os.path.expanduser("~/tirak_validation_report.json")

# Timeout per request (seconds)
TIMEOUT = 8


def check_url(url):
    """Check if a URL is reachable. Returns (status_code, final_url, error)."""
    if not url or not url.startswith("http"):
        return 0, "", "no_url"
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        })
        resp = urlopen(req, timeout=TIMEOUT, context=ctx)
        final_url = resp.geturl()
        return resp.status, final_url, None
    except HTTPError as e:
        return e.code, url, f"HTTP {e.code}"
    except URLError as e:
        reason = str(e.reason) if hasattr(e, 'reason') else str(e)
        return 0, url, f"URL_ERROR: {reason[:80]}"
    except Exception as e:
        return 0, url, f"ERROR: {str(e)[:80]}"


def classify_result(status, error):
    """Classify a URL check result."""
    if error == "no_url":
        return "NO_URL"
    if error is None and 200 <= status < 400:
        return "LIVE"
    if status in (301, 302, 307, 308):
        return "REDIRECT"
    if status == 403:
        return "BLOCKED"  # Site exists but blocks bots
    if status == 404:
        return "DEAD_404"
    if status in (500, 502, 503):
        return "SERVER_ERROR"
    if error and "timed out" in str(error).lower():
        return "TIMEOUT"
    if error and ("resolve" in str(error).lower() or "name" in str(error).lower()):
        return "DNS_FAIL"  # Domain doesn't exist
    if error:
        return "ERROR"
    return "UNKNOWN"


def main():
    with open(JSON_PATH) as f:
        vendors = json.load(f)

    # Identify AI-generated vs verified
    ai_generated = [
        (i, v) for i, v in enumerate(vendors)
        if not v.get("source") or v.get("source") == "pipeline-curated"
    ]
    verified = [
        (i, v) for i, v in enumerate(vendors)
        if v.get("source") and v.get("source") != "pipeline-curated"
    ]

    print(f"Total vendors: {len(vendors)}")
    print(f"AI-generated to validate: {len(ai_generated)}")
    print(f"Already verified (scrape/XLSX): {len(verified)}")
    print(f"\nValidating ALL {len(ai_generated)} AI-generated vendor URLs...\n")

    results = []
    live = 0
    dead = 0
    for idx, (i, v) in enumerate(ai_generated):
        url = v.get("url", "")
        name = v.get("name", "?")
        cat = v.get("category", "?")

        status, final_url, error = check_url(url)
        classification = classify_result(status, error)

        result = {
            "index": i,
            "name": name,
            "category": cat,
            "url": url,
            "status_code": status,
            "final_url": final_url,
            "classification": classification,
            "error": error,
            "source": v.get("source", "none"),
        }
        results.append(result)

        icon = {
            "LIVE": "✅", "REDIRECT": "↪️", "BLOCKED": "🔒",
            "DEAD_404": "💀", "DNS_FAIL": "🚫", "TIMEOUT": "⏰",
            "SERVER_ERROR": "🔥", "ERROR": "❌", "NO_URL": "❓",
            "UNKNOWN": "❓",
        }.get(classification, "?")

        if classification in ("LIVE", "REDIRECT", "BLOCKED"):
            live += 1
        else:
            dead += 1

        if (idx + 1) % 20 == 0 or classification not in ("LIVE",):
            print(f"  [{idx+1:3d}/{len(ai_generated)}] {icon} {classification:12s} {name[:35]:35s} {url[:55]}")

        time.sleep(0.3)  # Be polite

    # Save detailed report
    with open(REPORT_PATH, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Summary
    classifications = Counter(r["classification"] for r in results)

    print(f"\n{'='*70}")
    print("VALIDATION SUMMARY")
    print(f"{'='*70}")
    print(f"\nTotal AI-generated vendors checked: {len(results)}")
    for cls, count in classifications.most_common():
        icon = {"LIVE": "✅", "REDIRECT": "↪️", "BLOCKED": "🔒",
                "DEAD_404": "💀", "DNS_FAIL": "🚫", "TIMEOUT": "⏰",
                "SERVER_ERROR": "🔥", "ERROR": "❌", "NO_URL": "❓"}.get(cls, "?")
        print(f"  {icon} {cls:15s} {count:4d}")

    print(f"\n  LIVE/ACCESSIBLE: {live} ({100*live//len(results)}%)")
    print(f"  DEAD/UNREACHABLE: {dead} ({100*dead//len(results)}%)")

    # Break down dead ones by category
    dead_results = [r for r in results if r["classification"] not in ("LIVE", "REDIRECT", "BLOCKED")]
    if dead_results:
        print(f"\n{'='*70}")
        print("DEAD/UNREACHABLE BY CATEGORY")
        print(f"{'='*70}")
        dead_by_cat = Counter(r["category"] for r in dead_results)
        for cat, count in dead_by_cat.most_common():
            print(f"  {cat:45s} {count:4d}")
            for r in dead_results:
                if r["category"] == cat:
                    print(f"    {r['classification']:12s} {r['name'][:40]:40s} {r['url'][:50]}")

    print(f"\nDetailed report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
