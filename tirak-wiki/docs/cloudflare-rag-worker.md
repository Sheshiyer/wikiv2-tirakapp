# Cloudflare Multi-App RAG Workflow

This repo now includes a reusable Cloudflare Worker scaffold for app-specific RAG deployments.

## Architecture

Use **one worker per app**.

Use **one vector index per app**.

For the current wiki implementation, use `nvidia/llama-nemotron-embed-1b-v2` as the default embedding model.

Reason:

- best current Nvidia-first default for wiki/document retrieval
- supports longer markdown chunks
- retrieval quality depends on using `input_type: passage` for indexed chunks and `input_type: query` for search

Reuse the same Cloudflare pattern across apps:

- Worker code scaffold stays the same
- KV config schema stays the same
- secret names stay the same
- vector implementation can change per app

## Why This Pattern

This gives you reuse without forcing all applications into one shared retrieval corpus.

The reusable part is the control plane pattern:

- auth
- config loading
- model aliasing
- prompt selection
- endpoint contract
- Nvidia secret handling

The app-specific part is:

- vector index
- corpus
- metadata schema
- retrieval adapter implementation

## Storage Boundary

### Put In KV

- app registry
- model aliases
- prompt identifiers
- search defaults
- corpus identifiers
- auth metadata

### Put In Worker Secrets

- `NVIDIA_API_KEY`
- external vector DB credentials
- admin signing tokens

Do not store sensitive secrets in KV.

## App Deployment Model

For each app:

1. Copy or reuse `workers/rag/`
2. Set worker name in `wrangler.jsonc`
3. Bind the shared config KV namespace
4. Set `NVIDIA_API_KEY` secret for that worker
5. Implement the retrieval adapter for that app's vector backend
6. Deploy

## Example App Config Schema

```json
{
  "displayName": "Tirak Wiki",
  "corpusId": "tirak-docs",
  "vectorIndexBinding": "VECTOR_INDEX",
  "chatModel": "meta/llama-3.1-8b-instruct",
  "embeddingModel": "nvidia/nv-embedqa-e5-v5",
  "searchTopK": 8,
  "promptId": "wiki-answering",
  "authMode": "bearer",
  "enabled": true
}
```

## Root Commands

```bash
npm run wiki:corpus
npm run worker:dev
npm run worker:check
npm run worker:typegen
npm run worker:deploy
```

## Next Step To Productionize

Replace the placeholder `searchAppCorpus()` implementation with either:

1. Cloudflare Vectorize per app
2. External vector store per app

The current wiki implementation already uses real Nvidia embedding and chat calls, but still stores indexed chunks in KV for simplicity.

Move off KV when you need better scale or ANN search performance.
