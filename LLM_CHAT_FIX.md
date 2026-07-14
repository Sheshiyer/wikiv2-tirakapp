# Tirak Wiki Chat Assistant Fix

## Root Cause

The `WikiAssistant` component was failing in local dev because the RAG worker it calls (`http://127.0.0.1:8790/v1/chat`) was unreachable on the expected port and path:

1. **Wrong port**: `npm run worker:dev` started Wrangler on the default port `8787`, while `.env` pointed the component to `127.0.0.1:8790`. The worker was never listening on the configured URL.
2. **No local dev mode**: Even if the port matched, the worker required:
   - a populated `APP_CONFIG` KV namespace (`apps:tirak-wiki`, `auth:tirak-wiki`)
   - a populated `APP_INDEX` KV namespace with embedded corpus chunks
   - a valid `NVIDIA_API_KEY` secret
   None of these were present in a fresh local checkout, so every chat request would 401/404 or fail on the NVIDIA call.
3. **CORS blocked local origins**: the worker only allowed `https://*.tirak.app` origins, rejecting the Astro dev server origin (`http://localhost:4321`).

## Fix Applied

All changes are limited to local development behavior; production behavior is unchanged.

### 1. Corrected the worker dev port (`package.json`)

```json
"worker:dev": "wrangler dev --config workers/rag/wrangler.jsonc --port 8790"
```

This makes the worker listen on the same port the frontend expects.

### 2. Added a local-development bypass (`workers/rag/src/index.ts`)

When `ENVIRONMENT === 'development'` and `NVIDIA_API_KEY` is missing, the `/v1/chat` endpoint now returns a deterministic, page-aware mock response without requiring KV config, auth records, or embeddings. This makes the assistant functional immediately after `npm run worker:dev`.

### 3. Allowed local origins in CORS (`workers/rag/src/index.ts`)

`http://localhost` and `http://127.0.0.1` origins are now accepted when running in development mode, so the Astro dev server can talk to the local worker.

### 4. Better component error message (`src/components/WikiAssistant.tsx`)

If the worker is not reachable at all, the UI now tells the developer to run `npm run worker:dev` instead of showing a generic fetch error.

## Verification

### Type check

```bash
npm run worker:check
# (no output = pass)
```

### Static build

```bash
npm run build
# ...
# 12:59:42 [build] 51 page(s) built in 2.80s
# 12:59:42 [build] Complete!
```

### Worker health

```bash
npm run worker:dev
# [wrangler:info] Ready on http://localhost:8790
```

```bash
curl -s http://127.0.0.1:8790/health
# {"ok": true, "environment": "development"}
```

### Chat endpoint

```bash
curl -s -X POST http://127.0.0.1:8790/v1/chat \
  -H "Content-Type: application/json" \
  -H "authorization: Bearer 26ee2c8beaf69be7185cf074b9aff3567b309d981231772f" \
  -H "Origin: http://localhost:4321" \
  -d '{"appId":"tirak-wiki","query":"Tell me about Tirak","responseMode":"fast","currentPage":{"slug":"01-introduction/welcome","title":"Welcome to Tirak Wiki"}}'
```

Response:

```json
{
  "appId": "tirak-wiki",
  "model": "local-dev-mock",
  "embeddingModel": "local-dev-mock",
  "promptId": "local-dev",
  "mode": "fast",
  "gated": false,
  "retrievedContext": [
    {
      "id": "01-introduction/welcome#local-dev",
      "score": 1,
      "text": "Local dev mock context for Welcome to Tirak Wiki. The full corpus is not loaded in this mode.",
      "metadata": { "slug": "01-introduction/welcome", "title": "Welcome to Tirak Wiki", "source": "local-dev-mock" }
    }
  ],
  "answer": "You asked about \"Tell me about Tirak\" on **Welcome to Tirak Wiki**.\n\nThis is a local development response..."
}
```

## Remaining Blockers

- **Real LLM answers still require `NVIDIA_API_KEY`**: the mock response is explicitly a development placeholder. To enable full retrieval + generation, set `NVIDIA_API_KEY` in `workers/rag/.dev.vars`, run `npm run wiki:corpus`, POST the corpus to `/v1/ingest`, and restart the worker.
- **Corpus not auto-loaded**: the local dev bypass does not embed or search the wiki corpus. The returned sources are synthetic. True RAG search still requires an ingest step.
- **No automated local KV seeding**: app config and auth tokens must still be populated manually if you want to test the production code path locally without the bypass.

## Files Changed

- `package.json` — added `--port 8790` to `worker:dev`
- `workers/rag/src/index.ts` — local dev bypass, CORS for localhost, mock response helper
- `src/components/WikiAssistant.tsx` — clearer network-error message
