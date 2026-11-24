# Reusable RAG Worker Template

This worker is a reusable template for one-app-per-worker RAG deployments.

For the current wiki implementation, the recommended Nvidia embedding model is `nvidia/llama-nemotron-embed-1b-v2`.

Why this model:

- better fit for documentation and markdown retrieval than the older `nvidia/nv-embed-v1`
- supports long-input wiki chunks more comfortably
- uses explicit retrieval modes: `passage` for indexed corpus chunks and `query` for search requests

## Design Rules

- Deploy one worker per app.
- Keep the vector index per app.
- Store non-secret app and model config in Cloudflare KV.
- Store Nvidia credentials in Cloudflare Worker secrets.
- Reuse the same worker code and KV schema across apps.

## What Lives Where

### Worker Secret

- `NVIDIA_API_KEY`

Set it with:

```bash
npx wrangler secret put NVIDIA_API_KEY --config workers/rag/wrangler.jsonc
```

### KV Namespace

Bind one shared config namespace as `APP_CONFIG`.

Bind one app-specific index namespace as `APP_INDEX`.

Suggested keys:

- `rag:defaults`
- `apps:<appId>`
- `auth:<appId>`
- `models:chat:<alias>`
- `models:embed:<alias>`
- `prompts:<promptId>`

Example `rag:defaults` value:

```json
{
  "defaultChatModel": "meta/llama-3.1-8b-instruct",
  "defaultEmbeddingModel": "nvidia/nv-embedqa-e5-v5",
  "defaultSearchTopK": 6
}
```

Example `apps:tirak-wiki` value:

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

Example `auth:tirak-wiki` value:

```json
{
  "token": "replace-with-long-random-token"
}
```

## Per-App Vector Isolation

Each app should deploy this worker with its own vector binding implementation.

The scaffold keeps vector isolation by:

- storing app metadata in KV
- reading `vectorIndexBinding` from app config
- expecting the deployed app version to connect to its own vector backend

This template intentionally does not centralize vectors.

For the current wiki implementation, `APP_INDEX` temporarily stores embedded chunks in KV so the current site works end-to-end before switching to a dedicated vector store.

## Endpoints

- `GET /health`
- `GET /v1/models`
- `POST /v1/search`
- `POST /v1/ingest`
- `POST /v1/chat`

### Ingest Request

```json
{
  "appId": "tirak-wiki",
  "corpus": {
    "generatedAt": "2026-05-18T00:00:00Z",
    "docs": []
  }
}
```

### Search Request

```json
{
  "appId": "tirak-wiki",
  "query": "How does partner onboarding work?",
  "topK": 6
}
```

### Chat Request

```json
{
  "appId": "tirak-wiki",
  "query": "Summarize the partner approval process"
}
```

## Access Model

- `POST /v1/ingest` and `POST /v1/search` are admin calls and require the per-app bearer token stored in `auth:<appId>` (KV). Never put this token in a `PUBLIC_*` env var, a client bundle, or a committed doc.
- `POST /v1/chat` accepts either that bearer token (server-to-server) or a browser request whose `Origin` is on the exact allowlist:
  - `https://wiki.tirak.app` (always, see `src/access.ts`)
  - any exact origins listed in the `ALLOWED_ORIGINS` var (comma-separated, no wildcards), for example one Vercel preview URL
  - `http://localhost:*` and `http://127.0.0.1:*` only when `ENVIRONMENT=development`
- Public (no bearer) chat is rate limited per client IP by the `CHAT_RATE_LIMITER` Rate Limiting binding (10 requests / 60 s, see `wrangler.jsonc`) and queries are capped at 1000 characters.
- An `Origin` header can be forged by non-browser clients, so the allowlist only stops other websites from using the chat; the rate limit is what bounds cost. If abuse appears, add Cloudflare Turnstile in front of public chat.

### Environment variables

| Where | Name | Purpose |
| --- | --- | --- |
| Vercel (wiki build) | `PUBLIC_RAG_API_URL` | Worker base URL used by the browser |
| Vercel (wiki build) | `PUBLIC_RAG_APP_ID` | Defaults to `tirak-wiki` |
| Worker var | `ALLOWED_ORIGINS` | Extra exact origins (preview URLs) |
| Worker secret | `NVIDIA_API_KEY` | NVIDIA NIM credential |
| KV `APP_CONFIG` | `auth:tirak-wiki` | Admin bearer token for ingest/search |

`PUBLIC_RAG_TOKEN` is no longer read; remove it from Vercel.

## Local Development

```bash
cp workers/rag/.dev.vars.example workers/rag/.dev.vars
npm run wiki:corpus
npm run worker:dev
```

If you normally store secrets in `cloud.env`, copy the Nvidia key into `workers/rag/.dev.vars` for local worker development because `cloud.env` was not present in this repo.

## Type Generation

```bash
npm run worker:typegen
```

## Verification

```bash
npm run worker:check
```

## Current Wiki Flow

1. Run `npm run wiki:corpus` to generate `workers/rag/data/wiki-corpus.json` from `src/content/docs`.
2. Call `POST /v1/ingest` with that corpus payload.
3. Call `POST /v1/search` to retrieve wiki chunks.
4. Call `POST /v1/chat` to get grounded answers using retrieved chunks.

## Production Next Step

The current wiki implementation stores embeddings in `APP_INDEX` KV for simplicity.

For production scale, replace `APP_INDEX` storage in `src/retrieve.ts` with an app-specific vector backend while keeping:

- the same Nvidia embed model
- the same `passage` indexing mode
- the same `query` retrieval mode
- the same per-app worker deployment model
