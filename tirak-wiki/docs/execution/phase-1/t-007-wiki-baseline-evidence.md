# T-007 Canonical Wiki Baseline Evidence

Status: source, corpus, deterministic build, and staged secret scan pass; commit pending
Captured: 2026-07-19 02:21–02:34 IST
Repository: `wikiv2-tirakapp`
Branch: `main`
Parent SHA: `1303dc72e466cb710875e35c81bb11c7a4574908`
Upstream divergence: `0 ahead / 0 behind`

## Classified inputs

| Classification | Paths | Handling |
| --- | --- | --- |
| Canonical product source | `src/content/docs/01-introduction/welcome.md`, three approved `02-foundation` documents | Include |
| Publication allowlist | `src/lib/approved-docs.mjs`, `scripts/build-wiki-corpus.mjs`, `tests/approved-docs.test.mjs` | Include |
| Wiki presentation/routes | `src/components/**`, `src/layouts/**`, `src/pages/**` | Include |
| RAG publication output | `workers/rag/data/wiki-corpus.json` | Include after source/hash verification |
| Static deployment output | `dist/**` | Include only as the deterministic output of the classified source tree |
| Build configuration | `package.json` | Include |
| Generated local cache | `node_modules/.astro/data-store.json` | Remove from version control; retain locally under existing `node_modules/` ignore rule |
| Execution evidence | `docs/execution/phase-1/**` | Include |

Initial snapshot contained 80 tracked changes and 8 untracked files. The large deletion set is intentional publication contraction: retired person-first audience, campaign, and resource pages no longer appear in the generated site.

## Automated proof

| Probe | Result |
| --- | --- |
| `npm test` | PASS — 3/3 allowlist and product-contract tests |
| `npm run build` | PASS — 17 pages generated |
| first complete `dist` hash | `9cb38573759c081b42a007ae88331c7f1f02aee79c28860bd53c3a8904d44410` |
| second complete `dist` hash | `9cb38573759c081b42a007ae88331c7f1f02aee79c28860bd53c3a8904d44410` |
| corpus SHA-256 | `2f48be3a385455874840ca8138216de05aa265eefe2cc1863aa99e1724fcd2c7` |
| approved corpus count | exactly 4 documents |
| `git diff --check` | PASS |
| staged secret-signature scan | PASS — no provider or platform token signature in 89 staged files |

Approved corpus slugs:

1. `01-introduction/welcome`
2. `02-foundation/messaging-framework`
3. `02-foundation/positioning`
4. `02-foundation/product-overview`

The generated legacy route `dist/docs/03-audience/companion-persona/index.html` is absent. This baseline remains no-deploy until staged secret scan, scoped commit, cross-repository manifest, and human approval pass.

## Reproduction commands

```sh
npm test
npm run build
find dist -type f -print0 | sort -z | xargs -0 shasum -a 256 | shasum -a 256
shasum -a 256 workers/rag/data/wiki-corpus.json
test ! -e dist/docs/03-audience/companion-persona/index.html
git diff --check
```
