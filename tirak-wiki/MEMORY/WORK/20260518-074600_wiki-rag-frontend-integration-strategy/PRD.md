---
task: wiki rag frontend integration strategy decisions
slug: 20260518-074600_wiki-rag-frontend-integration-strategy
effort: extended
phase: execute
progress: 18/18
mode: interactive
started: 2026-05-18T07:46:00Z
updated: 2026-05-18T07:54:00Z
---

## Context

The Tirak wiki already has a frontend UI and a working Cloudflare Worker RAG backend prototype. The remaining work here is not implementation-first. The immediate need is to define the product and technical operating model for wiki chat across embeddings, indexing, retrieval, response generation, brand-guided prompting, and frontend controls. The user specifically wants decisions that account for both backend behavior and how those behaviors surface in the existing wiki UI.

The current system already uses `nvidia/llama-nemotron-embed-1b-v2` for embeddings and `meta/llama-3.1-70b-instruct` for chat in the worker, with corpus generation from `src/content/docs` and a docs UI rendered through `src/layouts/DocLayout.astro`. The frontend does not yet expose any RAG controls, model state, or fallback UI. The task is to decide what the preferred model should be, how content should be processed, how querying and answer generation should behave, how Tirak brand rules should shape prompting, and whether the UI should permit model changes when responses fail.

What was requested: choose model preference, define embedding/indexing flow, define query and response behavior, define prompt guidelines using brand details, and think through frontend integration. What was not requested: ship a production refactor in this pass, expose raw infra complexity to users, or treat this as a backend-only architecture problem.

### Risks

- The current chat model may be too slow for remote-preview-like interactive UI unless response length is constrained.
- Exposing raw model IDs in the UI would create operator complexity and user confusion.
- Letting any user change embeddings from the UI would invalidate retrieval consistency.
- Frontend fallback controls could accidentally mask backend failures instead of surfacing them clearly.
- Prompt instructions may drift from brand documentation if not stored as versioned config.

### Plan

Answer this task as a product-and-architecture decision memo rather than code changes. Separate decisions into five layers: embedding model preference, corpus/indexing flow, retrieval/response flow, prompt and brand governance, and frontend UI controls. Use current codebase reality as the anchor: Worker endpoints already exist, docs render through `DocLayout.astro`, and model/provider details should stay mostly server-controlled. Recommend a default path, define a fallback path, and state clearly which controls belong in UI versus backend configuration.

## Criteria

- [x] ISC-1: Preferred embedding model is named and justified clearly.
- [x] ISC-2: Preferred chat model is named and justified clearly.
- [x] ISC-3: Embedding model choice stays separate from chat model choice.
- [x] ISC-4: Corpus ingestion source is defined as `src/content/docs`.
- [x] ISC-5: Indexing flow specifies chunking before embedding generation.
- [x] ISC-6: Indexing flow specifies `passage` mode for corpus embeddings.
- [x] ISC-7: Query flow specifies `query` mode for search embeddings.
- [x] ISC-8: Retrieval flow defines top-K behavior for grounded answers.
- [x] ISC-9: Response flow defines when model should refuse unsupported answers.
- [x] ISC-10: Prompt design includes Tirak brand voice constraints.
- [x] ISC-11: Prompt design includes sourcing and citation behavior.
- [x] ISC-12: Prompt design includes safety against fabricated wiki facts.
- [x] ISC-13: Frontend UI behavior is defined for normal chat use.
- [x] ISC-14: Frontend UI behavior is defined for failed query handling.
- [x] ISC-15: Frontend UI model-switching policy is recommended explicitly.
- [x] ISC-16: Frontend UI distinguishes user-facing labels from raw model IDs.
- [x] ISC-17: Recommended configuration ownership is split across backend and UI.
- [x] ISC-18: Output includes concrete next-step requests for implementation.

## Decisions

Current system context established:

- Embeddings currently use `nvidia/llama-nemotron-embed-1b-v2`.
- Chat currently uses `meta/llama-3.1-70b-instruct`.
- Wiki content source is `src/content/docs`.
- Docs UI currently lives in `src/layouts/DocLayout.astro` and `src/pages/docs/[...slug].astro`.

Additional decision made during planning:

- Internal wiki users may switch approved response models in the UI after a failure, but embedding model selection remains backend-controlled.
- `DocLayout.astro` is the primary frontend insertion point for a wiki assistant panel.
- `[...slug].astro` should pass current-doc context into the assistant.
- `Navigation.tsx` or a floating action entry can host a global launcher or status badge.

## Verification

Pending.

Think-phase refinements:

- UI should not expose embedding model switching to normal users.
- UI may expose response-mode fallback only after explicit failure.
- Brand prompt rules should be versioned server-side rather than hardcoded in UI.
