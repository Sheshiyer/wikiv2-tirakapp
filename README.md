# Tirak Dream Journeys Wiki

## Overview
This repository contains the Astro-powered documentation site for Tirak Dream Journeys, a companion-first travel marketplace. The wiki consolidates strategy, audience research, and campaign assets into a structured, searchable reference.

## What’s Inside
- **Companion-first positioning**: personas, messaging framework, and voice guidance.
- **Campaign assets**: pre-launch ads, email sequences, and social content calendars.
- **Operational reference**: onboarding, FAQs, and glossary for consistent execution.

## Site Structure
```
tirak-wiki/
├── src/
│   ├── content/
│   │   └── docs/
│   │       ├── 01-introduction/
│   │       ├── 02-foundation/
│   │       ├── 03-audience/
│   │       ├── 04-campaign/
│   │       └── 05-resources/
│   ├── layouts/
│   ├── pages/
│   └── styles/
└── public/
```

## Canonical Routes
- Introduction: `/docs/01-introduction/welcome`
- Foundation: `/docs/02-foundation/positioning`
- Audiences: `/docs/03-audience/companion-persona`
- Campaigns: `/docs/04-campaign/pre-launch-ads`
- Resources: `/docs/05-resources/faq`

## Local Development
```bash
cd tirak-wiki
npm install
npm run dev
```

## Build
```bash
cd tirak-wiki
npm run build
npm run preview
```

## Content Standards
- Use descriptive titles and keep headers concise.
- Preserve the companion-first emphasis across all sections.
- Link related docs using absolute paths under `/docs/...`.

## Tech Stack
- Astro
- React
- Tailwind CSS
- Framer Motion
- Resources: `/docs/05-resources/faq`
| **Adaptations** | Generic crowdfunding | ✅ Platform-launch optimized |

## Technical Notes

### OrchV2 Pricing Correction
Initial recommendations used $0.25/1K tokens (10x inflated). Corrected to actual Claude API pricing:
- **Claude Sonnet 3.5:** ~$3 input / ~$15 output per million tokens
- **Blended average:** ~$9 per million tokens (50/50 input/output mix)
- **Per 1K tokens:** ~$0.009 (~0.9 cents)

**Result:** Skills that seemed like $2,500 are actually $225.

### Why the Pricing Error?
OrchV2 skill template uses placeholder pricing. Real-world execution costs depend on:
- Model used (Sonnet 3.5 vs. Opus vs. Haiku)
- Prompt complexity (simple vs. exhaustive protocols)
- Output format (minimal vs. maximum)

**Lesson:** Always validate cost estimates against current API pricing.

### Manifest.yaml Integration
OrchV2 reads from `/Volumes/madara/2026/claude-skills/skills/manifest.yaml` to:
- Know which skills exist
- Understand dependencies (upstream array)
- Estimate token counts (metadata.estimated_tokens)
- Build execution order (dependency DAG)

**Result:** Recommendations are grounded in actual skill availability, not theoretical scenarios.

## Ready to Execute?

Reply with:
1. **Scenario selection** (1, 2, or 3)
2. **Answers to clarifying questions** (budget breakdown, traveler persona timing, etc.)
3. **Confirmation to proceed** ("execute scenario 1")

I'll generate the detailed execution plan and start running skills in optimal order.

---

**Generated:** 2026-01-21  
**OrchV2 Version:** 2.0.0  
**Product:** Tirak Dream Journeys  
**Status:** Awaiting scenario selection
