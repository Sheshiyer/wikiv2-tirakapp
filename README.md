# Tirak Dream Journeys Wiki

## Overview

This repository contains the Astro-powered documentation site for **Tirak Dream Journeys**, a companion-first travel marketplace. The wiki is the canonical reference for brand positioning, audience understanding, campaign assets, and operational guidance.

## What's Inside

- **Companion-first positioning**: personas, messaging framework, and voice guidance.
- **Campaign assets**: pre-launch ads, email sequences, and social content calendars.
- **Operational reference**: onboarding, FAQs, glossary, and partner resources for consistent execution.

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
│   │       ├── 05-resources/
│   │       └── 06-vendor-pipeline/
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
- Vendor pipeline: `/docs/06-vendor-pipeline/pipeline-overview`

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

## Wiki Assistant

The site includes a page-aware `WikiAssistant` chat component. In local development it connects to a RAG worker:

```bash
cd tirak-wiki
npm run worker:dev
```

See `workers/rag/README.md` for the full worker setup, including how to ingest the wiki corpus and enable real LLM answers with an NVIDIA API key.

## Content Standards

- Use descriptive titles and keep headers concise.
- Preserve the companion-first emphasis across all sections.
- Link related docs using absolute paths under `/docs/...`.

## Tech Stack

- Astro
- React
- Tailwind CSS
- Framer Motion
- Lucide icons

## Status

Astro-powered, searchable wiki with companion-first positioning and an integrated assistant.
