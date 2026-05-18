---
task: backend timeout gates and clean exit
slug: 20260518-083300_backend-timeout-gates-and-clean-exit
effort: advanced
phase: observe
progress: 0/24
mode: interactive
started: 2026-05-18T08:33:00Z
updated: 2026-05-18T08:35:00Z
---

## Context

The integrated wiki assistant now exists in the frontend, but backend chat requests still time out too often. The current state is that the UI can render, submit, and fail cleanly, but the worker still attempts long-running chat generation that can exceed the dev gateway limit and yield `504 Gateway Time-out`. The user now wants the backend timeout fixed with explicit gating, limits, or a clean exit/entry path so the system avoids hanging and degrades predictably.

The current worker flow embeds the query, retrieves context, and then always attempts full chat generation. There is no worker-side budget gate that can decide to skip generation when the query/context size is too risky. There is also no clean backend fallback payload that says “retrieval succeeded but generation was skipped due to budget.” The fix should add explicit, deterministic gates and a clean response shape that the UI can use for retry/re-entry behavior.

## Criteria

- [ ] ISC-1: Worker defines explicit budget gate for chat generation.
- [ ] ISC-2: Budget gate uses deterministic input criteria.
- [ ] ISC-3: Fast mode uses stricter generation budget than best mode.
- [ ] ISC-4: Worker can skip chat generation before timeout risk.
- [ ] ISC-5: Worker returns clean structured fallback payload on skip.
- [ ] ISC-6: Fallback payload includes retrieval results.
- [ ] ISC-7: Fallback payload includes retry guidance metadata.
- [ ] ISC-8: Fallback payload avoids throwing 500 on gated skip.
- [ ] ISC-9: Worker catches slow generation path cleanly.
- [ ] ISC-10: Worker returns user-safe timeout message on failure.
- [ ] ISC-11: UI can distinguish gated exit from hard failure.
- [ ] ISC-12: UI can present clean re-entry path after gated exit.
- [ ] ISC-13: UI avoids indefinite loading on backend timeout.
- [ ] ISC-14: Response schema still supports successful answers.
- [ ] ISC-15: Response schema still supports retrieved sources.
- [ ] ISC-16: Fast mode path remains callable from UI.
- [ ] ISC-17: Build passes after worker and UI changes.
- [ ] ISC-18: Worker type check passes after changes.
- [ ] ISC-19: Direct worker request avoids 504 in gated case.
- [ ] ISC-20: Browser flow shows clean fallback state.
- [ ] ISC-21: Browser flow preserves retryable UI controls.
- [ ] ISC-22: Changes do not remove successful answer path.
- [ ] ISC-23: Final report distinguishes gate success from model success.
- [ ] ISC-24: Final report states remaining backend limitations clearly.

## Decisions

Initial root-cause findings:

- UI no longer hangs forever because browser timeout exists.
- Worker still attempts generation long enough to hit gateway timeouts.
- `fast` mode currently reduces tokens but still uses same provider path and can still 504.
- Needed change is a server-side gate and structured fallback, not UI-only handling.

## Verification

Pending.
