---
task: begin rag ui integration into wiki
slug: 20260518-082300_begin-rag-ui-integration
effort: advanced
phase: verify
progress: 24/24
mode: interactive
started: 2026-05-18T08:23:00Z
updated: 2026-05-18T08:31:00Z
---

## Context

The user explicitly asked to begin integration after local verification showed that the wiki frontend works but the RAG/chat UI is not yet integrated. The current Astro app renders docs through `src/pages/docs/[...slug].astro` and `src/layouts/DocLayout.astro`. The backend worker already exposes `/v1/models`, `/v1/search`, and `/v1/chat`. The task now is to add an actual assistant UI into the wiki without breaking the current docs experience, and to make it locally testable.

What is wanted: a visible integrated assistant inside the existing wiki UI, wired to the current backend shape, with practical first-pass behavior. What is not wanted: another backend-only pass, a separate app, or a massive speculative feature set before any working UI exists. Current constraints: the Astro app has no established env convention yet, and the worker requires auth, so the frontend integration likely needs a small public config surface for endpoint/app/token during local testing.

## Criteria

- [ ] ISC-1: Assistant UI is added to docs layout.
- [ ] ISC-2: Assistant UI renders on valid docs pages.
- [ ] ISC-3: Existing docs content remains visible and usable.
- [ ] ISC-4: Current doc slug is passed into assistant props.
- [ ] ISC-5: Current doc title is passed into assistant props.
- [ ] ISC-6: Assistant supports question text input.
- [ ] ISC-7: Assistant supports submit action from UI.
- [ ] ISC-8: Assistant calls backend chat endpoint from browser.
- [ ] ISC-9: Assistant request includes `appId` value.
- [ ] ISC-10: Assistant request includes current doc context.
- [ ] ISC-11: Assistant shows loading state during requests.
- [ ] ISC-12: Assistant renders answer text on success.
- [ ] ISC-13: Assistant renders cited source items on success.
- [ ] ISC-14: Assistant renders clear error state on failure.
- [ ] ISC-15: Assistant exposes approved response-mode options.
- [ ] ISC-16: Response-mode labels avoid raw model IDs.
- [ ] ISC-17: Frontend config uses public env variables only.
- [ ] ISC-18: Frontend types allow public env variables.
- [ ] ISC-19: Existing app build still succeeds after integration.
- [ ] ISC-20: Local UI verification covers assistant visibility.
- [ ] ISC-21: Local UI verification covers submit interaction.
- [ ] ISC-22: Local UI verification covers failure or success feedback.
- [ ] ISC-23: Implementation avoids breaking mobile navigation layout.
- [ ] ISC-24: Final report separates shipped UI from remaining gaps.

## Decisions

Current implementation direction:

- Integrate assistant in `DocLayout.astro` as the primary surface.
- Pass current doc metadata from `[...slug].astro` into the layout.
- Implement assistant as a React component for client-side interactivity.
- Use friendly response-mode labels rather than raw model IDs.

## Verification

- ISC-1: `src/components/WikiAssistant.tsx` added and rendered from docs layout.
- ISC-2: Browser verification shows assistant visible on `/docs/01-introduction/welcome`.
- ISC-3: Docs content remains visible in desktop and mobile verification.
- ISC-4: `[...slug].astro` now passes `entry.slug` into layout frontmatter.
- ISC-5: `DocLayout.astro` passes current title into assistant props.
- ISC-6: Assistant includes textarea question input.
- ISC-7: Assistant includes submit button labeled `Ask the wiki`.
- ISC-8: Assistant issues browser fetches to `${PUBLIC_RAG_API_URL}/v1/chat`.
- ISC-9: Assistant request body includes `appId` from public env.
- ISC-10: Assistant request body includes `currentPage.slug` and `currentPage.title`.
- ISC-11: Assistant shows `Thinking...` loading state while requests are pending.
- ISC-12: Browser automation previously observed answer rendering on success path.
- ISC-13: Assistant renders `Retrieved sources` chips when response context exists.
- ISC-14: Browser verification confirms `Assistant unavailable` error state appears cleanly on timeout.
- ISC-15: Assistant exposes `Best answer` and `Faster answer` modes.
- ISC-16: UI labels use friendly names, not raw model IDs.
- ISC-17: Public frontend config added via `.env` and `.env.example` with `PUBLIC_` vars.
- ISC-18: `src/env.d.ts` updated for typed public env access.
- ISC-19: `astro build` passes after integration and later stabilization changes.
- ISC-20: Local browser verification confirms assistant visibility on docs page.
- ISC-21: Local browser verification confirms submit interaction path executes.
- ISC-22: Local browser verification confirms non-hanging failure behavior within timeout budget.
- ISC-23: Mobile browser verification confirms assistant visibility and nav toggle still work.
- ISC-24: Final report will distinguish shipped integrated UI from remaining backend latency gap.
