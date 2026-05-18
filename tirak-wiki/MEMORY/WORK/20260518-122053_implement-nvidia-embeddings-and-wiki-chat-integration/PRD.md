---
task: Implement Nvidia embeddings and wiki chat integration
slug: 20260518-122053_implement-nvidia-embeddings-and-wiki-chat-integration
effort: advanced
phase: complete
progress: 26/26
mode: interactive
started: 2026-05-18T06:50:53Z
updated: 2026-05-18T07:07:50Z
---

## Context

The user wants the current wiki implementation to actually call Nvidia APIs for embeddings and wiki chat. The current worker scaffold under `workers/rag/` is placeholder-only. The work now is to implement real ingestion, chunking, embedding generation, retrieval-ready document storage, and grounded chat response generation on top of the current wiki corpus. The user also wants clarity on which Nvidia embedding model is best for storing and retrieving wiki data.

Explicit wants:
- Implement Nvidia-backed embeddings for the current wiki.
- Implement chat over the current wiki in the worker scaffold.
- Understand the available embedding model tradeoff and choose the best current default.
- Use the Nvidia API key stored outside source control.

Explicit not-wanted:
- Another placeholder-only scaffold.
- Generic answers detached from the wiki corpus.

Implied constraints:
- The repo currently has no visible `cloud.env`, so secret source handling must be explicit and safe.
- The worker should continue to support one-app-per-worker deployment.
- The retrieval pipeline should operate on Astro docs content in `src/content/docs`.
- The implementation should remain testable locally.

### Risks

- There is no vector database binding yet, so a full production retrieval layer must use a temporary storage strategy or a simplified in-worker store.
- The missing `cloud.env` file means local secret loading must be documented rather than assumed.
- Overly large raw markdown chunks could hit Nvidia embedding input limits if not split aggressively.
- Using the wrong embedding `input_type` would materially degrade retrieval quality.
- Worker runtime cannot read repo files at request time in production, so ingestion must happen before serving chat.

## Criteria

- [x] ISC-1: Nvidia provider helper is added to worker scaffold.
- [x] ISC-2: Embedding request function calls Nvidia embeddings endpoint.
- [x] ISC-3: Chat request function calls Nvidia chat endpoint.
- [x] ISC-4: Worker exposes ingest endpoint for wiki documents.
- [x] ISC-5: Wiki ingestion reads current Astro docs content.
- [x] ISC-6: Wiki docs are chunked before embedding.
- [x] ISC-7: Chunk metadata includes slug and title.
- [x] ISC-8: Chunk metadata includes category and source path.
- [x] ISC-9: Best default embedding model is documented in code comments.
- [x] ISC-10: Embedding model choice is documented in worker docs.
- [x] ISC-11: Ingestion stores chunk payloads in worker-accessible storage.
- [x] ISC-12: Search uses real embeddings for query vectors.
- [x] ISC-13: Search returns scored relevant chunks.
- [x] ISC-14: Chat uses retrieved chunks as grounding context.
- [x] ISC-15: Chat response returns source metadata.
- [x] ISC-16: Worker secret handling remains explicit and safe.
- [x] ISC-17: Local env file workflow is documented clearly.
- [x] ISC-18: Missing secret error handling is implemented.
- [x] ISC-19: Ingest route validates appId and auth.
- [x] ISC-20: Chat route validates appId and auth.
- [x] ISC-21: Search route validates appId and auth.
- [x] ISC-22: Worker type-check passes after implementation.
- [x] ISC-23: Astro build still passes after implementation.
- [x] ISC-24: README documents implementation and next deployment steps.
- [x] ISC-25: Embed model request uses passage mode for corpus.
- [x] ISC-26: Embed model request uses query mode for search.

## Decisions

- Use the current worker scaffold rather than moving logic into Astro routes.
- Treat `src/content/docs` as the wiki corpus source.
- Default embed model will be `nvidia/llama-nemotron-embed-1b-v2` for wiki RAG.

## Verification

- Verified corpus generation with `npm run wiki:corpus`, which wrote `workers/rag/data/wiki-corpus.json` containing 38 docs from `src/content/docs`.
- Verified `workers/rag/src/nvidia.ts` calls Nvidia `/v1/embeddings` and `/v1/chat/completions` endpoints.
- Verified embedding requests use `input_type: passage` for ingestion and `input_type: query` for search.
- Verified `workers/rag/src/retrieve.ts` chunks wiki docs, embeds chunks, stores them in `APP_INDEX`, and returns scored search results.
- Verified `workers/rag/src/index.ts` exposes `/v1/ingest`, `/v1/search`, and `/v1/chat` with auth validation.
- Verified docs updated in `workers/rag/README.md` and `docs/cloudflare-rag-worker.md`.
- Verification commands succeeded: `npm run worker:check` and `npm run build`.
- Capability invocation check passed for `Cloudflare Manager`, `Research`, `writing-plans`, `verification-before-completion`, and `task`.
