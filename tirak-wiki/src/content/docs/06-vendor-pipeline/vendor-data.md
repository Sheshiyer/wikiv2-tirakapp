---
title: "Vendor Data & Categories"
description: "Vendor data model, 10 category breakdown, and validation report"
category: "vendor-pipeline"
order: 4
icon: "bar-chart"
tags: ["data", "vendors", "categories", "validation"]
---

# Vendor Data & Categories

## Category Breakdown

The pipeline targets **10 vendor categories** spanning Thailand's experience economy:

| # | Category | Vendors | Key Sources |
|---|----------|---------|-------------|
| 1 | **Leisure & Experience DMCs** | 153 | dmcfinder.com, TripAdvisor, Google |
| 2 | **MICE & Event DMCs** | 56 | dmcfinder.com, event directories |
| 3 | **Transport & Transfer** | 50 | Airport links, ferry/bus operators |
| 4 | **Adventure & Outdoor** | 51 | TripAdvisor, activity directories |
| 5 | **Food & Culinary** | 50 | BK Magazine, Cookly, food blogs |
| 6 | **Wellness & Spa** | 52 | Hostelworld, spa directories |
| 7 | **Boutique Hotels & Hostels** | 50 | Hostelworld, booking sites |
| 8 | **Nightlife & Entertainment** | 51 | BK Magazine, venue listings |
| 9 | **Cinema & Entertainment** | 50 | Entertainment directories |
| 10 | **Lifestyle Experiences** | 51 | Various directories, Google |

**Total: 614 vendors** with verified web presence.

## Data Files

### Master Data
| File | Format | Records | Description |
|------|--------|---------|-------------|
| `tirak_thailand_vendors.json` | JSON | 614 | Canonical vendor store |
| `tirak_thailand_vendors.csv` | CSV | 614 | Master export (10 fields) |
| `thailand_dmcs.json` | JSON | 66 | DMC-specific records |
| `thailand_dmcs.csv` | CSV | 66 | DMC export (8 fields) |

### Per-Category CSVs
One CSV per category with identical schema: `category, name, url, location, description, type, source, phone, email, address`

### Reports
| File | Description |
|------|-------------|
| `tirak_validation_report.json` | URL status for every vendor |
| `tirak_enrichment_log.json` | URLs visited during contact enrichment |
| `tirak_outreach_summary.csv` | Outreach status per vendor |
| `tirak_vendor_signup_dashboard.html` | Visual dashboard for signup tracking |
| `tirak_why_tirak_onepager.html` | Partner-facing sales one-pager |

## Validation Results

Every vendor URL is classified:

| Classification | Meaning | Action |
|---------------|---------|--------|
| ✅ **LIVE** | URL responds 200 | Ready for outreach |
| ↪️ **REDIRECT** | Redirects to new URL | Update URL, then outreach |
| 🚫 **BLOCKED** | 403 / Cloudflare | Manual verification needed |
| ❌ **DEAD_404** | Returns 404 | Remove or find new URL |
| 💥 **SERVER_ERROR** | 5xx response | Retry later |
| ⏱️ **TIMEOUT** | No response | Retry with longer timeout |
| 🔌 **DNS_FAIL** | Domain unresolvable | Remove vendor |
| ❓ **NO_URL** | No URL on record | Needs manual research |

## Deduplication Logic

The pipeline prevents duplicates through:

1. **Name normalization** — Strips suffixes (Co., Ltd., Inc., Thailand, Bangkok), lowercases, removes punctuation
2. **Substring matching** — Catches partial name variants
3. **URL normalization** — Strips protocol, `www.` prefix, trailing slash
4. **Domain exclusion** — Rejects aggregator domains: TripAdvisor, Yelp, Booking.com, Facebook, Instagram

## Data Quality Rules

- Every vendor must have a **verifiable URL** (HEAD request validated)
- Minimum **50 vendors per category** (pipeline loops until met)
- Contact enrichment uses **polite 0.5s delays** between requests
- Email regex filters out junk domains (example.com, wixpress.com, googleapis.com)
- Phone extraction supports Thai formats (+66, 0-2-xxx, international)
