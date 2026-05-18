---
task: Summarize wiki and plan AI chat integration
slug: 20260518-102924_summarize-wiki-and-plan-ai-chat-integration
effort: extended
phase: complete
progress: 22/22
mode: interactive
started: 2026-05-18T04:59:24Z
updated: 2026-05-18T05:03:32Z
---

## Context

The user asked for three connected outcomes on top of the existing Astro wiki: a walkthrough and summary of the current wiki, a clearer onboarding flow, and a plan for integrating Nvidia API key based AI chat using inference and embedding models to interpret user queries against the wiki content. The user explicitly asked to hear my understanding first before implementation.

The current site is an Astro content site driven by the `docs` collection in `src/content/config.ts`. Content is organized into introduction, foundation, audience, campaign, resources, and vendor-pipeline sections. The homepage already contains partner marketing and a simplified onboarding journey. The vendor-pipeline docs contain a more explicit partner onboarding guide and partner communication model. The wiki mixes two narratives: a companion-first travel marketplace strategy corpus and a partner/vendor onboarding corpus.

What was requested:
- Summarize the current wiki structure and main themes.
- Create a coherent onboarding flow from existing content.
- Explain how an Nvidia-backed AI chat and retrieval layer should fit on this Astro site.
- Reflect back understanding before making larger implementation changes.

What was not requested:
- Immediate production deployment.
- A specific Nvidia model choice mandated by the user.
- A database vendor or hosting platform choice.

Implied constraints:
- Reuse the Astro content collection instead of inventing a parallel CMS.
- Keep the AI layer grounded in the current wiki corpus.
- Design for secure API key handling server-side, not in client code.
- Preserve the current site's content-first structure.

### Risks

- The content corpus currently mixes two product stories: companion marketplace strategy and partner onboarding materials.
- The user may want implementation next, but the current ask explicitly prioritizes explanation first.
- Nvidia model availability may differ between embedding and generation endpoints, so exact model names should be selected against current API support at implementation time.
- Pure static Astro pages cannot safely call Nvidia APIs directly from the client with a private API key.
- Retrieval quality will suffer if raw markdown is embedded without chunking and metadata normalization.

### Plan

1. Synthesize the current wiki into a concise explanation of structure, content themes, and narrative overlaps.
2. Derive a concrete onboarding flow from homepage and vendor-pipeline content, noting missing states and content gaps.
3. Explain an Astro-compatible RAG architecture using `src/content/docs` as source-of-truth, server-side Nvidia-backed generation, and a separate embedding/indexing pipeline.
4. End with what I understand first, plus the likely next implementation sequence if the user wants me to proceed.

## Criteria

- [x] ISC-1: Repo content architecture is summarized from actual Astro files.
- [x] ISC-2: Top-level wiki sections are enumerated with purpose.
- [x] ISC-3: Core Tirak product thesis is summarized accurately.
- [x] ISC-4: Partner and vendor pipeline narrative is summarized accurately.
- [x] ISC-5: Audience persona layer is summarized accurately.
- [x] ISC-6: Campaign asset layer is summarized accurately.
- [x] ISC-7: Existing homepage onboarding touchpoints are identified.
- [x] ISC-8: Existing vendor-pipeline onboarding touchpoints are identified.
- [x] ISC-9: Content overlap between marketplace and partner narratives is identified.
- [x] ISC-10: A proposed onboarding flow lists clear sequential stages.
- [x] ISC-11: The onboarding flow defines user goal at each stage.
- [x] ISC-12: The onboarding flow maps each stage to existing content.
- [x] ISC-13: The onboarding flow identifies missing content or product gaps.
- [x] ISC-14: AI chat use case is scoped to this wiki.
- [x] ISC-15: Retrieval source of truth is mapped to Astro docs content.
- [x] ISC-16: Embedding pipeline is described at system level.
- [x] ISC-17: Nvidia inference model role is described separately from embeddings.
- [x] ISC-18: Secure API key handling boundary is described.
- [x] ISC-19: Astro integration path is described with server-side components.
- [x] ISC-20: Recommended next implementation steps are sequenced clearly.
- [x] ISC-21: Mixed companion and partner narratives are called out explicitly.
- [x] ISC-22: Need for server-side API boundary is explained explicitly.

## Decisions

- Use the existing `src/content/docs` collection as the canonical retrieval corpus.
- Treat this turn as understanding, summary, and architecture direction first.
- Recommend separating source ingestion, embedding generation, vector storage, and chat response generation into explicit stages.
- Recommend preserving Astro as presentation and API orchestration layer, not as the vector database itself.

## Verification

- Verified repo architecture from `package.json`, `astro.config.mjs`, `src/content/config.ts`, and `src/pages/docs/[...slug].astro`.
- Verified current onboarding touchpoints from `src/pages/index.astro`, `src/components/OnboardingChecklist.tsx`, and `src/content/docs/06-vendor-pipeline/pipeline-overview.md`.
- Verified partner communication flow from `src/content/docs/06-vendor-pipeline/outreach-system.md`.
- Verified product and persona narratives from `src/content/docs/01-introduction/welcome.md`, `src/content/docs/02-foundation/product-overview.md`, `src/content/docs/03-audience/companion-persona.md`, and `src/content/docs/04-campaign/product-positioning-summary.md`.
- Verified resource and objection handling layer from `src/content/docs/05-resources/faq.md`.
- Capability invocation check passed for `brainstorming`, `writing-plans`, and `verification-before-completion` via tool calls in this session.
