# Tirak-Orchestrated: OrchV2 Campaign Setup

## What This Folder Contains

This is a **clean, orchestrated setup** for the Tirak Dream Journeys campaign, generated using the **orchv2 skill** (Context-Aware Agentic Orchestrator).

### Files Created

1. **`product.md`** - Complete product input file extracted from existing tirak campaign materials
   - Reverse-engineered from completed persona, MDS, and positioning outputs
   - Includes: brand snapshot, product specs, dual audiences (companions + travelers), competitive landscape, pricing, launch context
   - Required input for orchv2 orchestration

2. **`orchv2-recommendations.md`** - OrchV2 analysis and scenario recommendations
   - Context detection (budget: bootstrapped, channel: DTC, stage: pre-launch)
   - 3 ranked scenario recommendations with match scores
   - Cost breakdowns (corrected for actual Claude API pricing)
   - Execution timeline and next steps

## What OrchV2 Did

### Phase 1: Context Detection
Analyzed your product.md and detected:
- **Budget Tier:** Bootstrapped (<$5K) - based on "$3,000 initial ad budget"
- **Launch Channel:** DTC (Direct-to-Consumer platform launch)
- **Brand Maturity:** Pre-launch (building supply before demand)
- **Timeline:** Rushed (60-day sprint with aggressive goals)
- **Team:** Solo founder + part-time support
- **Content Depth:** Focused (not exhaustive - budget/timeline constrained)

### Phase 2: Scenario Matching
Generated 3 scenarios ranked by match score:

1. **🛒 Bootstrapped DTC** (92% match) ← RECOMMENDED
   - 9 skills | $650 | 1-2 days
   - Complete foundation + execution assets (emails, ads, social content)
   - Perfect for platform launches with tight budget

2. **🏗️ Brand Genesis** (78% match) - Alternative if you want to DIY
   - 5 skills | $360 | 4-6 hours
   - Foundation only (personas, positioning, voice)
   - You write your own emails/ads

3. **⚙️ Custom Hybrid** (85% match) - Companion-first focus
   - 7 skills | $585 | 1 day
   - Laser-focused on supply-side (companion recruitment)
   - Defers traveler assets to later phase

### Phase 3: Cost Analysis
**Key Finding:** Skills execution is MUCH cheaper than expected!
- Initial estimate using wrong pricing: $8,000
- Corrected using actual Claude API rates: **$650-$850**
- **Result:** Massive budget remaining ($2,350+) for paid ads

### Phase 4: Recommendations
**Recommended path:** Bootstrapped DTC
- Execute 9 skills for $650
- Use remaining $2,350 for Facebook/Instagram companion recruitment ads
- Timeline: 1-2 days for skills execution + 3-4 days for review/customization

## How This Differs from Original `/tirak` Folder

### Original `/tirak` Folder
- ✅ Has completed outputs (persona, MDS, voice, ads, emails)
- ❌ Missing structured product.md input
- ❌ No orchestration plan or cost estimates
- ❌ Ad-hoc execution (no dependency tracking)
- ❌ Partial coverage (some skills missing)

### This `/tirak-orchestrated` Folder
- ✅ Has structured product.md input (required for orchv2)
- ✅ Has orchv2 recommendations with context detection
- ✅ Shows 3 scenario options with tradeoffs
- ✅ Accurate cost estimates ($650 vs. $8K initial guess)
- ✅ Clear execution order and dependencies
- ✅ Budget optimization (leaves $2.3K for ads)
- ✅ Ready for systematic execution

## Next Steps

### 1. Review Recommendations
Read `orchv2-recommendations.md` and choose a scenario:
- **Scenario 1:** Bootstrapped DTC (comprehensive, best ROI)
- **Scenario 2:** Brand Genesis (foundation only, DIY execution)
- **Scenario 3:** Custom Hybrid (companion-first laser focus)

### 2. Answer Clarifying Questions
From orchv2-recommendations.md:
- Is $3K total budget or just ads budget?
- Include traveler persona now or defer?
- Sequential review or parallel execution?
- English outputs or Thai language examples?
- Markdown files or Google Docs?

### 3. Execute Selected Scenario
Once you confirm, I'll:
- Generate detailed execution plan with skill-by-skill breakdown
- Identify Tirak-specific adaptations (Thai market, dual personas, etc.)
- Create handoff documents between skills
- Run skills in optimal order (foundation → execution assets)

### 4. Deploy Campaign
After skills complete:
- Compile outputs into campaign folder
- Cross-reference for consistency
- Adapt for Thai market context
- Deploy to Facebook Ads Manager, email platform, social channels

## Key Insights

### Budget Revelation
**Before orchv2:** Thought skills would cost $8K-$12K (Scenario 2 from old tirak plan)  
**After orchv2:** Actual cost is $650-$850 (8x cheaper!)  
**Impact:** Can allocate 78% of budget to paid ads instead of skills execution

### Platform Launch Optimization
OrchV2 correctly identified that Tirak doesn't need:
- Campaign page copy (for crowdfunding platforms)
- Campaign video script (Kickstarter-specific)
- Press release (optional for bootstrapped launch)

Instead, prioritizes:
- Dual persona development (companions + travelers)
- Supply-side acquisition (companion recruitment focus)
- Email nurture sequences (onboarding + recruitment)
- Pre-launch ads (Facebook/Instagram for Thai millennials)

### Supply Creates Demand Philosophy
OrchV2 adapted to your 80/20 strategy:
- Foundation skills cover BOTH personas (even though execution is 80% companion-focused)
- Pre-launch ads can be split: 80% companion recruitment / 20% traveler waitlist
- Email sequences prioritize companion onboarding and nurture
- Social content builds community on both sides

## Questions Answered

### Q: What was missing from original tirak folder?
**A:** The structured product.md input file. It had outputs but no single source of truth for product context.

### Q: Why create a new folder instead of updating tirak?
**A:** Clean separation. Original tirak has partial work; this folder is orchestrated from scratch with proper dependencies.

### Q: Can I use outputs from original tirak?
**A:** Yes! You can compare them to orchv2 recommendations. Some outputs (persona, MDS, voice) can be reused if they match the recommended skills.

### Q: What does orchv2 add beyond the manifest.yaml orchestrator?
**A:** Context awareness! OrchV2:
- Auto-detects budget/channel/timeline from product.md
- Recommends scenarios based on YOUR context (not generic)
- Calculates costs and budget utilization
- Shows tradeoffs (pros/cons for each scenario)
- Optimizes for ROI (suggests lean variants if over-budget)

### Q: How long does execution take?
**A:** 
- Skills execution: 1-2 days (9 skills × 10-15 min each = 90-135 min total)
- Review & customization: 2-3 days (adapt for Thai market, translate, finalize creative)
- Total time to launch: 3-5 days from orchv2 analysis to deployed campaign

## File Structure After Execution

```
tirak-orchestrated/
├── README.md (this file)
├── product.md (input)
├── orchv2-recommendations.md (analysis)
├── execution-plan.md (generated after scenario selection)
│
├── foundation/
│   ├── companion-persona.md
│   ├── traveler-persona.md
│   ├── competitive-landscape.md
│   ├── product-positioning-summary.md
│   ├── mds.md
│   └── voice-and-tone.md
│
├── email-campaigns/
│   ├── pre-launch-email-sequence.md (companion recruitment)
│   ├── welcome-email-sequence.md (companion onboarding)
│   └── launch-email-sequence.md (traveler demand - optional)
│
├── ad-campaigns/
│   ├── pre-launch-ads.md (Facebook/Instagram - companion focus)
│   └── live-campaign-ads.md (traveler acquisition - optional)
│
└── social-content/
    └── social-content-calendar.md (30-day warmup)
```

## Comparison: Original vs. Orchestrated

| Aspect | Original `/tirak` | Orchestrated `/tirak-orchestrated` |
|--------|-------------------|-----------------------------------|
| **Input** | ❌ Missing product.md | ✅ Complete product.md |
| **Planning** | Ad-hoc master plan | ✅ OrchV2 context-aware recommendations |
| **Cost Estimate** | ~$12.5K (wrong) | ✅ $650 (correct) |
| **Scenario Options** | 1 fixed path | ✅ 3 ranked scenarios with tradeoffs |
| **Budget Optimization** | No analysis | ✅ Shows 78% budget available for ads |
| **Execution Order** | Manual dependencies | ✅ Auto-generated from manifest.yaml |
| **Context Detection** | Manual | ✅ Auto-detected (6 dimensions) |

## Tirak Wiki Cleanup and Structure

### Cleanup Actions
- Removed duplicate source markdown files from the repository root after migrating content into the Astro wiki.
- Standardized documentation paths under `tirak-wiki/src/content/docs` and verified all internal links.
- Added redirects for legacy routes and section roots to prevent navigation 404s.

### Current Wiki Structure

```
tirak-wiki/
├── src/
│   ├── pages/
│   │   ├── index.astro
│   │   ├── 404.astro
│   │   └── docs/
│   │       ├── [...slug].astro
│   │       ├── index.astro
│   │       ├── 01-introduction/index.astro
│   │       ├── 02-foundation/index.astro
│   │       ├── 03-audience/index.astro
│   │       ├── 03-audiences/index.astro
│   │       ├── 04-campaign/index.astro
│   │       ├── 04-campaigns/index.astro
│   │       └── 05-resources/index.astro
│   └── content/
│       └── docs/
│           ├── 01-introduction/
│           ├── 02-foundation/
│           ├── 03-audience/
│           ├── 04-campaign/
│           └── 05-resources/
```

### Canonical Routes
- Introduction: `/docs/01-introduction/welcome`
- Foundation: `/docs/02-foundation/positioning`
- Audiences: `/docs/03-audience/companion-persona`
- Campaigns: `/docs/04-campaign/pre-launch-ads`
- Resources: `/docs/05-resources/faq`
| **Adaptations** | Generic crowdfunding | ✅ Platform-launch optimized |

## Technical Notes

### OrchV2 Pricing Correction
Initial recommendations used $0.25/1K tokens (10x inflated). Corrected to actual Claude API pricing:
- **Claude Sonnet 3.5:** ~$3 input / ~$15 output per million tokens
- **Blended average:** ~$9 per million tokens (50/50 input/output mix)
- **Per 1K tokens:** ~$0.009 (~0.9 cents)

**Result:** Skills that seemed like $2,500 are actually $225.

### Why the Pricing Error?
OrchV2 skill template uses placeholder pricing. Real-world execution costs depend on:
- Model used (Sonnet 3.5 vs. Opus vs. Haiku)
- Prompt complexity (simple vs. exhaustive protocols)
- Output format (minimal vs. maximum)

**Lesson:** Always validate cost estimates against current API pricing.

### Manifest.yaml Integration
OrchV2 reads from `/Volumes/madara/2026/claude-skills/skills/manifest.yaml` to:
- Know which skills exist
- Understand dependencies (upstream array)
- Estimate token counts (metadata.estimated_tokens)
- Build execution order (dependency DAG)

**Result:** Recommendations are grounded in actual skill availability, not theoretical scenarios.

## Ready to Execute?

Reply with:
1. **Scenario selection** (1, 2, or 3)
2. **Answers to clarifying questions** (budget breakdown, traveler persona timing, etc.)
3. **Confirmation to proceed** ("execute scenario 1")

I'll generate the detailed execution plan and start running skills in optimal order.

---

**Generated:** 2026-01-21  
**OrchV2 Version:** 2.0.0  
**Product:** Tirak Dream Journeys  
**Status:** Awaiting scenario selection
