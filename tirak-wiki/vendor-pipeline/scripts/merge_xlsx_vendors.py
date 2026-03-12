"""
Merge XLSX vendor data into existing tirak_thailand_vendors.json.
- Deduplicates by normalized name
- Enriches existing entries with phone/email/address from XLSX
- Adds new vendors with proper category mapping
- Exports updated JSON + per-category CSVs
"""
import csv
import json
import re
import pandas as pd

XLSX_PATH = "/Users/sheshnarayaniyer/Downloads/Tirak Vendors List (1).xlsx"
JSON_PATH = "/Users/sheshnarayaniyer/tirak_thailand_vendors.json"
OUTPUT_JSON = "/Users/sheshnarayaniyer/tirak_thailand_vendors.json"
OUTPUT_CSV = "/Users/sheshnarayaniyer/tirak_thailand_vendors.csv"

# Category mapping: XLSX category → JSON category
CATEGORY_MAP = {
    "Culture": "Leisure & Experience DMCs",  # default; cooking schools → Food & Culinary
    "Adventure": "Adventure & Outdoor Operators",
    "Wellness": "Wellness & Spa Services",
    "Nightlife": "Nightlife & Entertainment",
    "Lifestyle": "Lifestyle & Experiences",
    "Cinema": "Cinema & Entertainment",
    "Food & Drink": "Food & Culinary Operators",
    "Events": "MICE & Event DMCs",
}

# Culture entries that should go to Food & Culinary instead
COOKING_KEYWORDS = ["cooking", "culinary", "food", "feast", "taste of thailand"]


def normalize_name(name):
    """Normalize a vendor name for dedup comparison."""
    n = name.lower().strip()
    # Remove common suffixes
    for suffix in [
        "co., ltd.", "co., ltd", "co.,ltd.", "co.,ltd", "co. ltd.",
        "co. ltd", "co.,", "co.", "ltd.", "ltd", "inc.", "inc",
        "thailand", "bangkok", "phuket", "chiang mai",
        "(thonglor branch)", "(siam paragon branch)",
        "& mma training camp", "international health resort",
        "wellness sanctuary & holistic spa", "integrative wellness",
    ]:
        n = n.replace(suffix, "")
    # Remove punctuation and extra whitespace
    n = re.sub(r"[^\w\s]", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n


def is_duplicate(name, existing_normalized):
    """Check if a name matches any existing normalized name."""
    norm = normalize_name(name)
    for existing_norm, existing_idx in existing_normalized.items():
        if norm == existing_norm:
            return True, existing_idx
        # Substring match for longer names
        if len(norm) > 5 and len(existing_norm) > 5:
            if norm in existing_norm or existing_norm in norm:
                return True, existing_idx
    return False, -1


def ensure_url(website):
    """Ensure URL has https:// prefix."""
    if not website or str(website) == "nan":
        return ""
    website = str(website).strip()
    if website.startswith("http"):
        return website
    return f"https://{website}"


def main():
    # Load existing data
    with open(JSON_PATH) as f:
        vendors = json.load(f)

    print(f"Existing vendors: {len(vendors)}")

    # Build normalized name index
    existing_normalized = {}
    for i, v in enumerate(vendors):
        norm = normalize_name(v["name"])
        existing_normalized[norm] = i

    # Track stats
    enriched = []
    skipped_dupes = []
    added = []

    # ── SHEET 1: 80 vendors with phone/email/website/address ──
    df1 = pd.read_excel(XLSX_PATH, sheet_name="Sheet1")

    for _, row in df1.iterrows():
        name = str(row["Name"]).strip()
        category = str(row["Category"]).strip()
        phone = str(row.get("Phone", "")).strip() if pd.notna(row.get("Phone")) else ""
        email = str(row.get("Email", "")).strip() if pd.notna(row.get("Email")) else ""
        website = ensure_url(row.get("Website", ""))
        address = str(row.get("Address", "")).strip() if pd.notna(row.get("Address")) else ""

        # Map category
        json_category = CATEGORY_MAP.get(category, category)
        # Culture → check if it's a cooking/food entry
        if category == "Culture":
            if any(kw in name.lower() for kw in COOKING_KEYWORDS):
                json_category = "Food & Culinary Operators"

        is_dupe, dupe_idx = is_duplicate(name, existing_normalized)

        if is_dupe:
            # Enrich existing entry with new data
            existing = vendors[dupe_idx]
            enriched_fields = []
            if phone and not existing.get("phone"):
                existing["phone"] = phone
                enriched_fields.append("phone")
            if email and not existing.get("email"):
                existing["email"] = email
                enriched_fields.append("email")
            if address and not existing.get("address"):
                existing["address"] = address
                enriched_fields.append("address")
            if enriched_fields:
                enriched.append(f"{existing['name']} (+{', '.join(enriched_fields)})")
            else:
                skipped_dupes.append(f"{name} ↔ {existing['name']}")
        else:
            # Add new vendor
            vendor = {
                "name": name,
                "category": json_category,
                "url": website,
                "location": address,
                "source": "xlsx-tirak-vendors",
            }
            if phone:
                vendor["phone"] = phone
            if email:
                vendor["email"] = email
            if address:
                vendor["address"] = address
            vendors.append(vendor)
            existing_normalized[normalize_name(name)] = len(vendors) - 1
            added.append(f"[{json_category}] {name}")

    # ── SHEET 2: 60 DMCs ──
    df2 = pd.read_excel(XLSX_PATH, sheet_name="Sheet2")

    for _, row in df2.iterrows():
        name = str(row["Name of the DMC"]).strip()
        phone = str(row.get("Contact number", "")).strip() if pd.notna(row.get("Contact number")) else ""
        website = ensure_url(row.get("Website link", ""))

        is_dupe, dupe_idx = is_duplicate(name, existing_normalized)

        if is_dupe:
            existing = vendors[dupe_idx]
            enriched_fields = []
            if phone and not existing.get("phone"):
                existing["phone"] = phone
                enriched_fields.append("phone")
            if website and not existing.get("url"):
                existing["url"] = website
                enriched_fields.append("url")
            if enriched_fields:
                enriched.append(f"{existing['name']} (+{', '.join(enriched_fields)})")
            else:
                skipped_dupes.append(f"{name} ↔ {existing['name']}")
        else:
            vendor = {
                "name": name,
                "category": "Leisure & Experience DMCs",
                "url": website,
                "source": "xlsx-tirak-vendors-sheet2",
            }
            if phone:
                vendor["phone"] = phone
            vendors.append(vendor)
            existing_normalized[normalize_name(name)] = len(vendors) - 1
            added.append(f"[Leisure & Experience DMCs] {name}")

    # ── FINAL DEDUP CHECK ──
    seen_names = {}
    final_vendors = []
    final_dupes = 0
    for v in vendors:
        norm = normalize_name(v["name"])
        if norm not in seen_names:
            seen_names[norm] = True
            final_vendors.append(v)
        else:
            final_dupes += 1

    # ── SAVE JSON ──
    with open(OUTPUT_JSON, "w") as f:
        json.dump(final_vendors, f, indent=2, ensure_ascii=False)

    # ── SAVE MASTER CSV ──
    fieldnames = ["category", "name", "url", "location", "description", "type",
                   "source", "phone", "email", "address"]
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for v in final_vendors:
            writer.writerow(v)

    # ── SAVE PER-CATEGORY CSVs ──
    categories = {}
    for v in final_vendors:
        cat = v.get("category", "Uncategorized")
        categories.setdefault(cat, []).append(v)

    for cat, cat_vendors in categories.items():
        safe_name = cat.lower().replace(" & ", "_").replace(" ", "_")
        filename = f"/Users/sheshnarayaniyer/tirak_vendors_{safe_name}.csv"
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for v in cat_vendors:
                writer.writerow(v)

    # ── REPORT ──
    print("\n" + "=" * 70)
    print("MERGE REPORT")
    print("=" * 70)

    print(f"\n📊 ENRICHED (existing vendors gained new contact data): {len(enriched)}")
    for e in enriched:
        print(f"  ✅ {e}")

    print(f"\n⏭️  SKIPPED DUPLICATES: {len(skipped_dupes)}")
    for s in skipped_dupes:
        print(f"  ⏭️  {s}")

    print(f"\n➕ ADDED NEW VENDORS: {len(added)}")
    for a in added:
        print(f"  ➕ {a}")

    if final_dupes > 0:
        print(f"\n🧹 Removed {final_dupes} remaining duplicates in final pass")

    print(f"\n{'=' * 70}")
    print("FINAL COUNTS BY CATEGORY")
    print(f"{'=' * 70}")
    total = 0
    for cat in sorted(categories.keys()):
        count = len(categories[cat])
        total += count
        safe_name = cat.lower().replace(" & ", "_").replace(" ", "_")
        print(f"  {cat:40s} {count:4d}  → tirak_vendors_{safe_name}.csv")
    print(f"  {'TOTAL':40s} {total:4d}")

    print(f"\n{'=' * 70}")
    print("FILES SAVED")
    print(f"{'=' * 70}")
    print(f"  {OUTPUT_JSON}")
    print(f"  {OUTPUT_CSV}")
    for cat in sorted(categories.keys()):
        safe_name = cat.lower().replace(" & ", "_").replace(" ", "_")
        print(f"  tirak_vendors_{safe_name}.csv")

    # Verify no dupes in final
    all_norms = [normalize_name(v["name"]) for v in final_vendors]
    if len(all_norms) != len(set(all_norms)):
        print("\n⚠️  WARNING: Duplicate names still exist in final output!")
        from collections import Counter
        for name, count in Counter(all_norms).items():
            if count > 1:
                matches = [v["name"] for v in final_vendors if normalize_name(v["name"]) == name]
                print(f"    {matches}")
    else:
        print(f"\n✅ No duplicate names in final output ({len(final_vendors)} unique vendors)")


if __name__ == "__main__":
    main()
