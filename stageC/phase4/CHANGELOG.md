# Phase 4 changelog

## Phase4-v0.1.2 — 2026-11-03

- Keeps the six full-text caffeine PK records in a proposed, `IN_PROGRESS` evidence layer.
- Tightens the Phase 3 context selector so measured or derived numeric PK records are never exposed through the context-only interface, even if incorrectly marked accepted for contextual display.
- Adds a regression test for this quantitative-record exclusion. Phase3 may view only future accepted qualitative context records after identity, applicability, and independent-review gates.
- Preserves the participant-count discrepancy, name-only identity, context-limited applicability, and pending second review.

## Phase4-v0.1.1 — 2026-11-03

- First full-text extraction continuation: five separate Cmax table rows and one qualitative statistical comparison.
- Preserves source conditions, units, SD/range, and unresolved denominator discrepancy.

## Phase4-v0.1.0 — 2026-11-03

- Initial abstract-level workflow demonstration. This package remains immutable.
