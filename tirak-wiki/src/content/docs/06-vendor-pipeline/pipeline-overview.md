---
title: "Vendor Pipeline Overview"
description: "Architecture and execution flow of the Tirak vendor acquisition pipeline"
category: "vendor-pipeline"
order: 1
icon: "database"
tags: ["pipeline", "vendors", "scraping", "automation"]
---

# Vendor Pipeline Overview

The **Tirak Vendor Pipeline** is an automated data acquisition and outreach system that scrapes, validates, enriches, and contacts Thailand-based experience vendors across 10 categories. The pipeline operates in a circular loop until every category has ≥50 verified vendors.

## Pipeline Architecture

```
Phase 1: DATA ACQUISITION
  ┌─ scrape_dmcs.py            → DMC listings from dmcfinder.com
  ├─ scrape_tirak_vendors.py   → Multi-directory scraping (7 categories)
  ├─ scrape_directories.py     → Hostelworld, directory backfill
  ├─ scrape_real_vendors.py    → Backfill categories below 50
  └─ merge_xlsx_vendors.py     → Merge manual spreadsheet data

Phase 2: CIRCULAR PIPELINE (tirak_pipeline.py)
  ┌──→ AUDIT         — Count vendors per category
  │    FILL GAPS     — Scrape to fill categories < 50
  │    ENRICH        — Scrape contact info from websites
  │    VALIDATE      — Check all URLs are live
  │    EXPORT        — Write per-category CSVs + master CSV
  └──← CHECK         — All 10 categories ≥ 50? → Done (max 5 iterations)

Phase 3: VALIDATION
  └─ validate_vendors.py       → URL status classification

Phase 4: OUTREACH
  └─ tirak_outreach_emails.py  → 608 personalized vendor emails
```

## Key Statistics

| Metric | Value |
|--------|-------|
| **Total Vendors** | 614 across 10 categories |
| **Outreach Emails** | 608 personalized `.txt` files |
| **DMC Records** | 66 from dmcfinder.com |
| **Python Scripts** | 10 (4,387 lines total) |
| **Data Files** | 13 CSVs + 3 JSONs |

## Vendor Categories

| # | Category | Count |
|---|----------|-------|
| 1 | Leisure & Experience DMCs | 153 |
| 2 | MICE & Event DMCs | 56 |
| 3 | Transport & Transfer Services | 50 |
| 4 | Adventure & Outdoor Operators | 51 |
| 5 | Food & Culinary Operators | 50 |
| 6 | Wellness & Spa Services | 52 |
| 7 | Boutique Hotels & Hostels | 50 |
| 8 | Nightlife & Entertainment | 51 |
| 9 | Cinema & Entertainment | 50 |
| 10 | Lifestyle & Experiences | 51 |

## Data Model

### Master Vendor Record (10 fields)
```
category, name, url, location, description, type, source, phone, email, address
```

- **Deduplication**: Normalized name matching (strips Co., Ltd., Inc., Thailand, etc.)
- **URL normalization**: Strips protocol, `www.`, trailing slash
- **Source tracking**: Distinguishes scraped vs. `pipeline-curated` data

### Validation Classifications
`LIVE` · `DEAD_404` · `REDIRECT` · `BLOCKED` · `SERVER_ERROR` · `TIMEOUT` · `DNS_FAIL` · `NO_URL`

## Technology Stack

- **Python 3** with `scrapling` library (StealthyFetcher for JS pages, Fetcher for static)
- **URL verification** via HEAD requests with timeout handling
- **Contact enrichment** with regex patterns for Thai phone formats and email extraction
- **Polite scraping**: 0.5s delays, domain exclusion lists (TripAdvisor, Yelp, Booking, etc.)

## File Structure

```
vendor-pipeline/
├── scripts/          # 10 Python scripts
├── data/             # CSVs + JSONs (vendor data)
├── outreach/emails/  # 608 personalized outreach emails
├── templates/        # Email templates, WhatsApp scripts, objection handling
├── reports/          # Validation reports, dashboards
└── logs/             # Pipeline execution logs
```
