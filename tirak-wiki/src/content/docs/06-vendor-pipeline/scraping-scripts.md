---
title: "Scraping Scripts"
description: "Documentation for the 10 Python scripts powering the vendor data pipeline"
category: "vendor-pipeline"
order: 2
icon: "code"
tags: ["scripts", "scraping", "python", "automation"]
---

# Scraping Scripts

Ten Python scripts power the Tirak vendor pipeline. Each has a specific role in the data acquisition, enrichment, and outreach workflow.

## Core Orchestrator

### `tirak_pipeline.py` (603 lines)
The main orchestrator that runs a **circular audit-fill-enrich-validate-export loop**. Loops until all 10 categories reach ≥50 vendors (max 5 iterations).

- Contains `VendorStore` class — the canonical in-memory vendor database with name/URL deduplication
- Reads/writes `tirak_thailand_vendors.json` as the master data store
- Calls gap-filling, enrichment, and validation logic internally

## Data Acquisition Scripts

### `scrape_tirak_vendors.py` (728 lines)
The **primary multi-directory scraper**. Targets 7+ categories across multiple sources:
- dmcfinder.com, Hostelworld, TripAdvisor listings
- Uses both `StealthyFetcher` (headless browser for JS pages) and `Fetcher` (fast static)
- First scraper to run in the pipeline

### `scrape_dmcs.py` (148 lines)
Focused scraper for **DMC listings** from dmcfinder.com/listing_region/thailand/. Extracts:
- Name, tagline, profile URL, logo, location, regions, rating, listing type

### `scrape_directories.py` (478 lines)
Real Thailand **business directory scraper**. Targets Hostelworld and other specific directory pages. Each function targets a single scrapable directory with URL validation.

### `scrape_real_vendors.py` (454 lines)
**Backfill scraper** for categories below 50 vendors. Sources:
- TripAdvisor category pages, Google search results, directory sites
- Every vendor must have a **live-verified URL** (HEAD request check)

### `scrape_vendor_gaps.py` (808 lines)
**Gap filler** — fills 65+ vendor gaps across 8 categories via web scraping. Imports `VendorStore` from the pipeline. Targets BK Magazine and other Thailand-specific sources. Skips aggregator domains.

### `merge_xlsx_vendors.py` (280 lines)
Merges **XLSX spreadsheet data** into the master JSON. Features:
- Substring matching for partial name dedup
- Enriches existing entries with phone/email/address from the spreadsheet
- Maps XLSX categories to the canonical 10 categories

## Enrichment & Validation Scripts

### `enrich_vendor_contacts.py` (362 lines)
**Contact enrichment** — visits each vendor URL and scrapes:
- Email addresses (regex-based extraction)
- Phone numbers (Thai formats: +66, 0-2-xxx, international)
- Filters junk domains (example.com, wixpress.com, googleapis.com)
- 0.5s polite delay between requests

### `validate_vendors.py` (168 lines)
**URL validator** — fetches every vendor URL and classifies status:

| Status | Meaning |
|--------|---------|
| `LIVE` | URL responds successfully |
| `DEAD_404` | Returns 404 |
| `REDIRECT` | Redirects to different domain |
| `BLOCKED` | Access denied (403/Cloudflare) |
| `SERVER_ERROR` | 5xx response |
| `TIMEOUT` | No response within timeout |
| `DNS_FAIL` | Domain doesn't resolve |
| `NO_URL` | No URL on record |

Distinguishes AI-generated (`pipeline-curated`) vs. verified vendors.

## Outreach Script

### `tirak_outreach_emails.py` (358 lines)
**Personalized email generator** for all 608 vendors:
- Category-specific subject lines, hooks, value propositions
- Brand voice: direct, confident, not corporate
- Outputs: one `.txt` per vendor, `tirak_email_templates.json`, `tirak_outreach_summary.csv`

## Dependencies

```python
# Core scraping
scrapling          # StealthyFetcher (headless) + Fetcher (static)

# Standard library
csv, json, re, pathlib, urllib, concurrent.futures
```
