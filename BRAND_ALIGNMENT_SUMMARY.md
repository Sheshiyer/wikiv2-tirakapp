# Brand Alignment Summary

## What Changed

The Tirak Dream Journeys wiki homepage drifted toward a generic partner/vendor portal. This pass re-aligned it with the companion-first positioning documented in the wiki.

## Issues Found and Fixed

1. **Homepage hero was supply-centric.** The original headline "Grow Your Business" and subcopy "Join 614+ Thailand experience vendors" positioned Tirak as a vendor SaaS tool. Rewrote to "Not a tour. A vibe." and centered the Thai companion experience.
2. **CTA pointed to vendor pipeline, not companion docs.** The primary button now leads to the companion persona; the secondary button leads to the voice guide.
3. **Benefit cards used partner/vendor language.** Rewrote all six cards to speak to companions (fair earnings, same-day approval, showing up as you are, own schedule/rates, verified travelers, community support).
4. **How-it-works copy assumed a business application.** Rewrote steps to describe a companion setting up their profile and sharing their Bangkok.
5. **Bottom CTA repeated partner framing.** Changed from "Ready to Grow Your Business?" to "Ready to earn on your own terms?" and linked to the wiki welcome page.
6. **README still contained scenario-selection and crowdfunding legacy.** Replaced with a clean wiki overview, local-dev instructions, and content standards.
7. **Missing icon support for new benefit cards.** Added `banknote`, `camera-off`, `calendar-clock`, `shield-check`, and `message-circle-heart` to `PartnerBenefitCard`.

## Verification

- `npm run build` passes.
- No "crowdfunding" or "scenario selection" language remains in `src/pages/` or `src/content/docs/`.
- All homepage icons render correctly.

## Files Modified

- `tirak-wiki/src/pages/index.astro`
- `tirak-wiki/src/components/PartnerBenefitCard.tsx`
- `README.md`
