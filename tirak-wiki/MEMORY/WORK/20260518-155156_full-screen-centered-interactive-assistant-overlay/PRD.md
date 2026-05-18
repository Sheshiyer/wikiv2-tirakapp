---
task: Full-screen centered interactive assistant overlay
slug: 20260518-155156_full-screen-centered-interactive-assistant-overlay
effort: extended
phase: complete
progress: 18/18
mode: interactive
started: 2026-05-18T15:51:56+0530
updated: 2026-05-18T15:58:41+0530
---

## Context

The current assistant was recently moved into a global overlay launched from the floating bottom-right icon. The user now wants that overlay upgraded into a stronger chat experience: full-screen, centered, more immersive, and more interactive. The current implementation still reads as a compact form card dropped into an overlay container, not as a primary conversational surface.

What was requested: make the overlay full-screen and centered, add a visible thinking chat bubble, and make the interaction feel more alive. What was not requested: change the backend contract, reintroduce WhatsApp behavior, or replace the existing assistant logic. The correct move is to keep the working fetch flow and evolve the presentation into a richer chat interface.

### Risks

- A full-screen overlay can become cramped on mobile if the internal layout does not collapse cleanly.
- A chat-style presentation can accidentally hide controls like response mode and sources.
- A more animated interface can feel gimmicky if the thinking state is not tied to real request state.

### Plan

- Expand the modal shell in `ContactButtons.tsx` to a centered full-screen overlay with a larger content frame.
- Refactor `WikiAssistant.tsx` from form-card layout into chat layout while preserving fetch logic.
- Render the current user query, a live thinking bubble, and the assistant answer as transcript rows.
- Add quick prompt chips and a stronger header so the overlay feels active before the first message.
- Keep mode controls and sources visible inside the new composition.

## Criteria

- [x] ISC-1: Overlay opens centered in the viewport.
- [x] ISC-2: Overlay uses near full-screen desktop layout.
- [x] ISC-3: Overlay uses full-height mobile-friendly layout.
- [x] ISC-4: Background page remains visually dimmed behind overlay.
- [x] ISC-5: Floating launcher still opens and closes overlay.
- [x] ISC-6: Close control remains visible in overlay.
- [x] ISC-7: Assistant layout reads as chat interface.
- [x] ISC-8: User question appears as chat bubble.
- [x] ISC-9: Thinking state renders as assistant bubble.
- [x] ISC-10: Thinking bubble animates while request is pending.
- [x] ISC-11: Final answer renders as assistant chat bubble.
- [x] ISC-12: Sources remain accessible after answer renders.
- [x] ISC-13: Mode selection remains usable in updated layout.
- [x] ISC-14: Submit action remains obvious in updated layout.
- [x] ISC-15: Overlay includes at least one interactive prompt shortcut.
- [x] ISC-16: Overlay includes contextual status or page cue.
- [x] ISC-17: Existing request and timeout behavior still works.
- [x] ISC-18: Site builds successfully after UI changes.

## Decisions

- Use the existing `WikiAssistant` fetch flow and state rather than creating a second chat implementation.
- Keep the floating launcher as the only entry point.
- Upgrade the assistant UI into a conversational two-pane or stacked layout inside the current overlay.
- Render the user query and assistant output as transcript bubbles instead of plain panels.
- Use shortcut prompts for low-friction interaction before first submission.

## Verification

- `npm run build` completed successfully after the redesign.
- Desktop browser check confirmed centered large overlay, visible shortcuts, conversation section, and composer.
- Desktop browser check confirmed visible user bubble and animated thinking bubble during request.
- Mobile browser check confirmed overlay visibility, close control visibility, and textarea visibility.
