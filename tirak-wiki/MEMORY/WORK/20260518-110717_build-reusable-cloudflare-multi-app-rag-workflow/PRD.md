---
task: Build reusable Cloudflare multi-app RAG workflow
slug: 20260518-110717_build-reusable-cloudflare-multi-app-rag-workflow
effort: advanced
phase: complete
progress: 26/26
mode: interactive
started: 2026-05-18T05:37:17Z
updated: 2026-05-18T05:43:44Z
---

## Context

The user clarified the intended architecture: each app should keep its own vector index, but the worker may be separate per app while still using a reusable shared Cloudflare pattern. The user wants build mode now, not just planning. The repo currently has no Cloudflare worker scaffold or Wrangler configuration, so the task is to add a reusable workflow template and documentation for a per-app Cloudflare RAG worker pattern that centralizes Cloudflare KV-based configuration while keeping app-specific vector bindings isolated.

Explicit wants:
- Build reusable Cloudflare workflow assets in this repo.
- Support one worker per app using a common pattern.
- Keep vectors per app rather than globally centralized.
- Store non-secret model and routing config in KV.
- Keep Nvidia API credentials out of app code and out of KV.

Explicit not-wanted:
- A single global vector index for all apps.
- Project-specific secret duplication in source control.

Implied constraints:
- Reusable assets should be easy to copy across projects.
- Cloudflare primitives should be used correctly: secrets as Worker secrets, config in KV.
- The workflow should support mixed app hosting environments.
- The repo should remain buildable after changes.

### Risks

- Adding worker code inside `src/` could accidentally couple Astro and Worker runtimes.
- Overdesigning the worker before choosing the actual vector backend could reduce reuse.
- Misplacing secrets in KV would create a security regression.
- Root package changes could break the current Astro-only workflow if not kept additive.
- Missing Wrangler local-state ignores could create noisy git diffs.

### Plan

1. Add a top-level `workers/rag/` scaffold with Worker entrypoint, config loader, and endpoint placeholders.
2. Add `wrangler.jsonc`, worker tsconfig, generated-types placeholder, and dev vars example.
3. Update root package scripts and dev dependencies for Wrangler-based workflows.
4. Add repo documentation covering KV config schema, worker secrets, per-app vectors, and deployment steps.
5. Verify both worker type-check and Astro build from the root project.

## Criteria

- [x] ISC-1: Reusable Cloudflare worker scaffold is added to repo.
- [x] ISC-2: Wrangler configuration template is added to repo.
- [x] ISC-3: Worker scaffold documents per-app vector isolation.
- [x] ISC-4: Worker scaffold reads app config from KV.
- [x] ISC-5: Worker scaffold expects Nvidia key from Worker secret.
- [x] ISC-6: Worker scaffold exposes health endpoint.
- [x] ISC-7: Worker scaffold exposes models endpoint.
- [x] ISC-8: Worker scaffold exposes search endpoint placeholder.
- [x] ISC-9: Worker scaffold exposes chat endpoint placeholder.
- [x] ISC-10: Request auth pattern is represented in code.
- [x] ISC-11: App identifier routing is represented in code.
- [x] ISC-12: KV config schema is documented.
- [x] ISC-13: Secret versus KV boundary is documented.
- [x] ISC-14: Per-app worker deployment model is documented.
- [x] ISC-15: Per-app vector binding model is documented.
- [x] ISC-16: Setup steps are documented in project docs.
- [x] ISC-17: Example env and secret names are documented.
- [x] ISC-18: Example API routes are documented.
- [x] ISC-19: Example app config payload is documented.
- [x] ISC-20: Repo package scripts support worker workflow.
- [x] ISC-21: Repo dependencies include Wrangler workflow tools.
- [x] ISC-22: Gitignore covers Wrangler local state.
- [x] ISC-23: TypeScript config supports worker files if needed.
- [x] ISC-24: Build verification command succeeds after changes.
- [x] ISC-25: Worker scaffold is isolated outside Astro src directory.
- [x] ISC-26: Worker local development vars example is added.

## Decisions

- Model config and app routing metadata belong in KV.
- Sensitive credentials belong in Cloudflare Worker secrets.
- Vector index remains app-specific even when workflow is shared.
- The reusable pattern will be delivered as a scaffold under a dedicated directory rather than merged into Astro runtime code.

## Verification

- Verified worker scaffold files exist under `workers/rag/` and are isolated from Astro `src/`.
- Verified root workflow updates in `package.json` add `worker:dev`, `worker:deploy`, `worker:typegen`, `worker:check`, and `check`.
- Verified git ignores cover `.wrangler/`, `workers/rag/.dev.vars`, and worker local state.
- Verified `workers/rag/src/index.ts` exposes `/health`, `/v1/models`, `/v1/search`, and `/v1/chat` placeholders.
- Verified `workers/rag/src/config.ts` reads app config and auth data from KV and expects `NVIDIA_API_KEY` from Worker secret.
- Verified `workers/rag/README.md` documents KV schema, secret boundary, per-app vectors, and endpoint contract.
- Verified `docs/cloudflare-rag-worker.md` documents deployment model and productionization steps.
- Verification commands succeeded: `npm run worker:check` and `npm run build`.
- Capability invocation check passed for `Cloudflare Manager`, `writing-plans`, `verification-before-completion`, and `task`.
