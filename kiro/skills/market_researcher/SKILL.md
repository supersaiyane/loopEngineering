---
name: Market Researcher
description: Market analysis, TAM/SAM/SOM, competitive intelligence, personas, positioning
---

# Market Researcher

## Description
Skill files for the Market Researcher role in the Elite Engineering Team orchestration system.

## Usage
These skills are loaded selectively based on the current activity. See `.kiro/steering/skill-selection-matrix.md` for the loading rules.

## Files
- competitive_teardown.md
- jtbd_interviews.md
- market_sizing_tam_sam_som.md
- positioning_april_dunford.md
- pricing_van_westendorp.md

---

## DATE-STAMPING — MANDATORY (FIX G)

**At the start of EVERY market research session, run this shell command:**
```bash
CURRENT_DATE=$(date "+%B %Y")
CURRENT_YEAR=$(date "+%Y")
```

**Rules:**
1. Use `$CURRENT_DATE` (e.g., "July 2026") in ALL web search queries:
   - BAD: "pharmacy adherence platforms market size"
   - GOOD: "pharmacy adherence platforms market size $CURRENT_DATE"
2. Tag every data point with its source and retrieval date:
   - Format: `[Source: <URL or publication> | Retrieved: $CURRENT_DATE]`
3. Flag any figure that cannot be verified with a live web search:
   - `⚠️ TRAINING DATA — unverified as of $CURRENT_DATE. Verify before using in business decisions.`
4. **Flag derived/computed estimates** (FIX H-G): any figure produced by combining, overlapping, or computing across multiple sources — even if all inputs came from live web searches — must carry:
   - `⚠️ TRAINING DATA — derived estimate, unverified as of $CURRENT_DATE`
   - Plus a `Derived from: <source A> × <source B>` note explaining the computation
   - RULE: A derived figure is NOT the same as a sourced figure, even if both inputs are live-sourced. Investor decks, SAM slices, SOM projections, and CAGR extrapolations from overlapping market reports are ALL derived estimates.
4. **Never hardcode a year.** Always derive from shell. If shell is unavailable, state:
   - `[DATE: shell unavailable — using session context date: <date from context>]`
5. Competitor data older than 6 months = stale. Flag with:
   - `⚠️ STALE DATA — sourced from <period>, may not reflect current state.`

## Additional activity

- [source_freshness_assumptions.md](source_freshness_assumptions.md) — task-specific guidance; see the specialist catalog for when to load it.
