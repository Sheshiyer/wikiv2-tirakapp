---
title: "Outreach System"
description: "Multi-channel vendor outreach: email templates, WhatsApp scripts, and objection handling"
category: "vendor-pipeline"
order: 3
icon: "mail"
tags: ["outreach", "email", "whatsapp", "vendor-acquisition"]
---

# Outreach System

The Tirak outreach system is a **multi-channel vendor acquisition toolkit** generating personalized communications for 608 Thailand-based vendors across email, WhatsApp/LINE, and phone.

## Email Campaign

### Generation
`tirak_outreach_emails.py` generates **608 personalized `.txt` emails**, one per vendor:
- **Category-specific** subject lines, hooks, and value propositions
- **Brand voice**: Direct, confident, peer-to-peer (not corporate)
- Key selling points in every email:
  - **80–85% vendor earnings** (vs. 60–70% on competitors)
  - Same-day listing approval
  - 600+ vendor network
  - `tirak.app/partners` signup link

### Email Structure
```
Subject: {vendor_name} + Tirak — [category-specific hook]

Body:
  → Hook (category-relevant opening)
  → Introduction paragraph
  → 4 bullet value propositions
  → Category-specific social proof paragraph
  → Clear CTA with signup link
  → Footer with unsubscribe
```

### Competitive Positioning in Emails

| Platform | Commission | Tirak Advantage |
|----------|-----------|-----------------|
| Withlocals | 30% | 80–85% earnings |
| ToursByLocals | 40% | 80–85% earnings |
| Cookly | 25–30% | 80–85% earnings |
| Booking.com | 15–25% | 80–85% + no exclusivity |
| GetYourGuide | 25–30% | 80–85% + same-day approval |

## WhatsApp / LINE Scripts

A **3-touch messaging sequence** designed for peer-to-peer tone:

### Touch 1 — Day 1 (Cold Intro)
Brief, casual introduction. Category-aware hook. "Reply 'interested' for details" CTA.

### Touch 2 — Day 3–4 (Value Follow-up)
Specific stat or benefit reminder. Link to partner signup. Low-pressure.

### Touch 3 — Day 7 (Final Gentle Nudge)
"No pressure" closer with time-limited early-adopter incentive.

Category-specific variants exist for: Food, Nightlife, Transport, Adventure, Wellness, Hotels, MICE.

## Objection Handling

Scripted rebuttals organized by objection theme:

### Commission & Pricing
- *"15–20% is too good to be true"* → Platform subsidy model, scale economics
- *"How do you make money?"* → Service fee to travelers, not vendors

### Trust & Legitimacy
- *"Never heard of Tirak"* → TAT partnership, 600+ vendors, backed by [details]
- *"What if Tirak shuts down?"* → Data export, no exclusivity lock-in

### Effort & Setup
- *"Don't have time"* → 15-minute onboarding, team handles listing
- *"No professional photos"* → Free photo shoot for early adopters

### Logistics
- *Payment concerns* → 24–48hr payouts via bank transfer
- *Schedule control* → Full blackout date control
- *Pricing freedom* → Vendors set their own prices

### Category-Specific
- **Food vendors** → Cookly comparison, same customers better cut
- **Hotels** → Booking.com comparison, no exclusivity required
- **Transport** → Complement (not replace) your website
- **MICE** → We bring you event leads, you keep your direct sales

### Closing "Maybe" Responses
- Offer trial period with guaranteed payout
- Connect with existing vendor reference
- Follow up in 2 weeks with new stats

## Data Outputs

| File | Description |
|------|-------------|
| `outreach/emails/*.txt` | 608 personalized vendor emails |
| `templates/tirak_email_templates.json` | 10 category-specific templates |
| `templates/tirak_whatsapp_scripts.md` | 3-touch WhatsApp/LINE sequences |
| `templates/tirak_objection_handling.md` | Full objection handling playbook |
| `data/tirak_outreach_summary.csv` | Vendor contact status tracker |
| `reports/tirak_vendor_signup_dashboard.html` | Visual signup tracking dashboard |
| `reports/tirak_why_tirak_onepager.html` | Partner-facing one-pager |
