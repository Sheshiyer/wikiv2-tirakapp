"""
Tirak Vendor Outreach Email Generator — Creates personalized, category-specific
outreach emails for 608 vendors using brand voice/tone guidelines.

Outputs:
  ~/tirak_outreach_emails/        — One .txt file per vendor
  ~/tirak_email_templates.json    — All 10 category templates
  ~/tirak_outreach_summary.csv    — Spreadsheet of vendor + email + status

Usage: python ~/tirak_outreach_emails.py
"""
import csv
import json
import os
import re
from collections import Counter

JSON_PATH = os.path.expanduser("~/tirak_thailand_vendors.json")
OUTPUT_DIR = os.path.expanduser("~/tirak_outreach_emails")
TEMPLATES_PATH = os.path.expanduser("~/tirak_email_templates.json")
SUMMARY_CSV = os.path.expanduser("~/tirak_outreach_summary.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════
# EMAIL TEMPLATES BY CATEGORY
# Brand voice: Direct, confident, respectful. Not corporate.
# Key messaging: 80-85% earnings, same-day approval, 600+ vendor network
# ═══════════════════════════════════════════════════════════════════

TEMPLATES = {
    "Leisure & Experience DMCs": {
        "subject": "{vendor_name} + Tirak — More bookings, 85% earnings, zero hassle",
        "hook": "DMCs know better than anyone: platforms take too much, deliver too little.",
        "value_props": [
            "Keep 80-85% of every booking — not the 60-70% other platforms offer",
            "We bring travelers directly to you — 80% of our marketing budget targets traveler acquisition for our vendors",
            "Same-day listing approval — no 3-month application purgatory",
            "Your rates, your availability, your terms",
        ],
        "category_specific": (
            "As a DMC, you're already running the operations. Tirak simply opens "
            "a new channel of high-intent travelers — digital nomads, solo explorers, "
            "and couples looking for authentic Thai experiences. No group tour aggregation, "
            "no race-to-the-bottom pricing. Your expertise, premium positioning."
        ),
        "social_proof": "153 DMCs already in our Thailand network",
    },
    "MICE & Event DMCs": {
        "subject": "{vendor_name} — Corporate travelers are searching for you on Tirak",
        "hook": "Event and MICE operators spend weeks chasing corporate leads. What if they came to you?",
        "value_props": [
            "Tirak features your venue/service to corporate groups and team retreats actively searching Thailand",
            "Keep 80-85% of bookings — transparent commission, no hidden fees",
            "Listed same-day — we handle the traveler marketing, you handle the experience",
            "Multi-day and group booking support built in",
        ],
        "category_specific": (
            "Corporate teams are ditching boring hotel conference rooms for authentic local experiences. "
            "Team retreats, incentive trips, product launches — they're all looking for MICE operators "
            "who can deliver something memorable in Thailand. Tirak connects you directly with those decision-makers."
        ),
        "social_proof": "50 MICE operators already in our Thailand network",
    },
    "Transport & Transfer Services": {
        "subject": "{vendor_name} — Fill empty seats with Tirak traveler bookings",
        "hook": "Every empty seat on a ferry, bus, or van is lost revenue. Tirak fills those seats.",
        "value_props": [
            "Direct exposure to travelers actively planning Thailand transport — ferries, vans, private transfers",
            "Keep 80-85% of every booking through our platform",
            "Instant listing — no paperwork marathon, go live today",
            "Travelers can book your service alongside experiences, creating bundle demand",
        ],
        "category_specific": (
            "Travelers land in Bangkok and immediately need transport: airport transfers, "
            "island ferry bookings, intercity vans. They're searching right now. "
            "Tirak puts your service in front of them at the moment of need — "
            "not buried on page 5 of a Google search."
        ),
        "social_proof": "50 transport operators already in our Thailand network",
    },
    "Adventure & Outdoor Operators": {
        "subject": "{vendor_name} — Adventure travelers are looking for exactly what you offer",
        "hook": "Ziplines, diving, kayaking, trekking — Thailand's adventure scene is booming. Are travelers finding YOU?",
        "value_props": [
            "Targeted exposure to adventure-seeking travelers (digital nomads, backpackers, couples)",
            "Keep 80-85% of bookings — not the 60% that aggregator platforms leave you",
            "Your pricing, your availability — charge premium for weekends, offer deals for locals",
            "No professional photo requirements — authentic action shots work better anyway",
        ],
        "category_specific": (
            "Adventure travelers don't want a Viator group tour with 25 strangers. "
            "They want YOUR zipline, YOUR dive shop, YOUR trekking route. "
            "Tirak positions you as the authentic local operator — not a generic listing "
            "in a sea of identical options. Your expertise is the product."
        ),
        "social_proof": "51 adventure operators already in our Thailand network",
    },
    "Food & Culinary Operators": {
        "subject": "{vendor_name} — Foodies are searching for authentic Thai cooking experiences",
        "hook": "Travelers don't want another generic cooking class. They want YOUR recipes, YOUR kitchen, YOUR story.",
        "value_props": [
            "Featured to food-obsessed travelers — digital nomads, solo explorers, couples seeking authentic Thai cuisine",
            "Keep 80-85% of every booking (compare to Cookly's 25-30% commission)",
            "Same-day approval — upload photos from your kitchen, go live today",
            "Set your own class sizes, pricing, and schedule",
        ],
        "category_specific": (
            "Food is the #1 reason travelers visit Thailand. Street food tours, cooking classes, "
            "market visits, farm-to-table experiences — demand is massive and growing. "
            "Tirak gives you a direct line to travelers who care about authentic food, "
            "not tourist-trap pad thai. Your grandmother's recipe IS the selling point."
        ),
        "social_proof": "50 food operators already in our Thailand network",
    },
    "Wellness & Spa Services": {
        "subject": "{vendor_name} — Wellness travelers are actively searching Thailand experiences",
        "hook": "Thailand is the world's wellness capital. Are the right travelers finding your spa?",
        "value_props": [
            "Direct exposure to wellness-focused travelers — yoga retreats, spa seekers, meditation enthusiasts",
            "Keep 80-85% of bookings — no exploitative platform fees eating your margins",
            "List your services same-day — no approval committees or photo audits",
            "Flexible booking options: one-off sessions, packages, multi-day retreats",
        ],
        "category_specific": (
            "Wellness tourism in Thailand is a $12B+ industry. "
            "Travelers fly specifically for Thai massage, yoga retreats, detox programs, "
            "and meditation experiences. Tirak connects you with high-intent wellness travelers "
            "who are ready to book — not window-shopping on TripAdvisor."
        ),
        "social_proof": "52 wellness operators already in our Thailand network",
    },
    "Boutique Hotels & Hostels": {
        "subject": "{vendor_name} — Turn empty beds into booked experiences",
        "hook": "OTAs take 15-25% commission and bury you behind chain hotels. There's a better channel.",
        "value_props": [
            "List unique accommodation experiences (not just rooms) — hostel tours, rooftop events, cultural stays",
            "Keep 80-85% of bookings — better than Booking.com's 15-25% or Agoda's commissions",
            "Reach travelers who specifically want boutique/independent over chain hotels",
            "Bundle accommodation with local experiences for higher total booking value",
        ],
        "category_specific": (
            "Boutique hotels and hostels ARE the experience. Travelers choose you for the vibe, "
            "the community, the rooftop bar, the neighborhood. Tirak markets exactly that — "
            "your unique character — to travelers who are tired of cookie-cutter chain hotels. "
            "Your personality is your competitive advantage."
        ),
        "social_proof": "50 boutique properties already in our Thailand network",
    },
    "Nightlife & Entertainment": {
        "subject": "{vendor_name} — Bangkok's nightlife scene is on Tirak. Are you?",
        "hook": "Travelers are searching for Bangkok's best bars, clubs, and live music. They should be finding you.",
        "value_props": [
            "Featured listing to nightlife-seeking travelers — cocktail lovers, live music fans, rooftop bar seekers",
            "Keep 80-85% of experience bookings through our platform",
            "Same-day listing — no approval wait, no professional photo requirements",
            "Promote special events, happy hours, and exclusive experiences directly to travelers",
        ],
        "category_specific": (
            "Bangkok's nightlife is world-famous, but travelers are overwhelmed by choices. "
            "They end up at the same 5 tourist bars because that's all Google shows them. "
            "Tirak gives YOUR venue visibility to travelers who specifically want hidden gems, "
            "rooftop cocktails, jazz bars, and live music — the real Bangkok nightlife that locals know."
        ),
        "social_proof": "51 nightlife venues already in our Thailand network",
    },
    "Cinema & Entertainment": {
        "subject": "{vendor_name} — Entertainment seekers are booking Thailand experiences on Tirak",
        "hook": "Theme parks, escape rooms, bowling, VR experiences — travelers want fun, not just temples.",
        "value_props": [
            "Exposure to travelers seeking entertainment activities beyond sightseeing",
            "Keep 80-85% of bookings — transparent, fair commission",
            "List multiple experience types under one profile — different activities, different prices",
            "Same-day approval, no bureaucratic hoops",
        ],
        "category_specific": (
            "Not every traveler wants temples and beaches. Many are looking for "
            "entertainment — escape rooms, go-karts, bowling, cinema, theme parks. "
            "Tirak surfaces YOUR entertainment venue to travelers who are actively "
            "searching for something fun to do tonight. That's high-intent, ready-to-book traffic."
        ),
        "social_proof": "50 entertainment venues already in our Thailand network",
    },
    "Lifestyle & Experiences": {
        "subject": "{vendor_name} — Lifestyle experiences are Thailand's fastest-growing travel category",
        "hook": "Coworking, fitness, language classes, tailoring — the 'live like a local' economy is exploding.",
        "value_props": [
            "Featured to digital nomads and long-stay travelers — the exact audience for lifestyle experiences",
            "Keep 80-85% of bookings — fair commission, fast payouts",
            "Same-day listing — no approval delays",
            "Reach travelers staying 1-6 months who need exactly what you offer",
        ],
        "category_specific": (
            "Digital nomads in Bangkok and Chiang Mai aren't just tourists — they're living here "
            "for months. They need coworking spaces, gyms, Thai language classes, tailors, "
            "and lifestyle experiences. Tirak is where they search. "
            "Your lifestyle service is exactly what 50,000+ digital nomads in Thailand are looking for."
        ),
        "social_proof": "51 lifestyle businesses already in our Thailand network",
    },
}


def generate_email(vendor, template):
    """Generate a personalized outreach email for a vendor."""
    name = vendor.get("name", "there")
    url = vendor.get("url", "")
    location = vendor.get("location", "Thailand")
    category = vendor.get("category", "")

    subject = template["subject"].replace("{vendor_name}", name)

    # Build email body
    lines = []
    lines.append(f"Subject: {subject}")
    lines.append("")
    lines.append(f"Hi {name} team,")
    lines.append("")
    lines.append(template["hook"])
    lines.append("")
    lines.append(
        "Tirak Dream Journeys is a travel companion marketplace connecting "
        "travelers with verified Thai businesses. We're building Thailand's "
        "largest network of authentic experience providers — and we'd love "
        f"to have {name} on board."
    )
    lines.append("")
    lines.append("Here's what's different about Tirak:")
    lines.append("")
    for prop in template["value_props"]:
        lines.append(f"  * {prop}")
    lines.append("")
    lines.append(template["category_specific"])
    lines.append("")
    lines.append(f"We already have {template['social_proof']}.")
    lines.append("")
    lines.append(
        "Getting listed is simple: reply to this email or visit tirak.app/partners. "
        "10-minute setup. Same-day approval. Start receiving traveler bookings immediately."
    )
    lines.append("")
    lines.append(
        "Would you be open to a quick 5-minute chat about how Tirak "
        f"can bring more travelers to {name}?"
    )
    lines.append("")
    lines.append("Best,")
    lines.append("The Tirak Team")
    lines.append("tirak.app | partners@tirak.app")
    lines.append("")
    lines.append("---")
    lines.append(f"You're receiving this because {name} ({url}) is listed in our ")
    lines.append(f"Thailand {category} directory. Not interested? No worries — just ignore this email.")

    return "\n".join(lines)


def safe_filename(name):
    """Convert vendor name to safe filename."""
    safe = re.sub(r'[^\w\s-]', '', name).strip()
    safe = re.sub(r'[\s]+', '_', safe)
    return safe[:80]


def main():
    print("=" * 60)
    print("TIRAK VENDOR OUTREACH EMAIL GENERATOR")
    print("=" * 60)

    # Load vendors
    with open(JSON_PATH, "r") as f:
        data = json.load(f)
    vendors = data.get("vendors", data) if isinstance(data, dict) else data
    print(f"Loaded {len(vendors)} vendors")

    # Save templates
    with open(TEMPLATES_PATH, "w") as f:
        json.dump(TEMPLATES, f, indent=2, ensure_ascii=False)
    print(f"Saved templates to {TEMPLATES_PATH}")

    # Generate emails
    stats = Counter()
    has_email = 0
    csv_rows = []

    for vendor in vendors:
        category = vendor.get("category", "")
        name = vendor.get("name", "Unknown")
        email = vendor.get("email", "")
        url = vendor.get("url", "")

        template = TEMPLATES.get(category)
        if not template:
            stats["skipped_no_template"] += 1
            continue

        email_text = generate_email(vendor, template)
        filename = safe_filename(name) + ".txt"
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, "w") as f:
            f.write(email_text)

        stats["generated"] += 1

        # Track for CSV
        status = "READY" if email else "NEEDS_EMAIL"
        if email:
            has_email += 1
        csv_rows.append({
            "name": name,
            "category": category,
            "email": email,
            "url": url,
            "location": vendor.get("location", ""),
            "phone": vendor.get("phone", ""),
            "status": status,
            "email_file": filename,
        })

    # Write summary CSV
    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "name", "category", "email", "url", "location", "phone", "status", "email_file"
        ])
        writer.writeheader()
        writer.writerows(csv_rows)

    # Category breakdown
    cat_counts = Counter()
    cat_ready = Counter()
    for row in csv_rows:
        cat_counts[row["category"]] += 1
        if row["status"] == "READY":
            cat_ready[row["category"]] += 1

    print(f"\n{'='*60}")
    print("RESULTS")
    print(f"{'='*60}")
    print(f"Total emails generated:   {stats['generated']}")
    print(f"Ready to send (has email): {has_email}")
    print(f"Needs email address:       {stats['generated'] - has_email}")
    print(f"")
    print(f"Per-Category Readiness:")
    for cat in sorted(cat_counts.keys()):
        total = cat_counts[cat]
        ready = cat_ready[cat]
        print(f"  {cat}: {ready}/{total} ready ({ready*100//total}%)")

    print(f"\nOutputs:")
    print(f"  Email files:   {OUTPUT_DIR}/")
    print(f"  Templates:     {TEMPLATES_PATH}")
    print(f"  Summary CSV:   {SUMMARY_CSV}")
    print(f"\nDone!")


if __name__ == "__main__":
    main()
