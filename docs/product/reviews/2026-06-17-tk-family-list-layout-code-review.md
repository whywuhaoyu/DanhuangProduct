# Tk Family List Layout Code Review

Date: 2026-06-17

Scope:

- `src-prototype/legacy-monolith/run-danhuang-desktop-pet.py`
- `CHANGELOG.md`
- `src-prototype/legacy-monolith/CHANGELOG.md`
- `docs/product/CURRENT_TK_UI_OPTIMIZATION_BACKLOG.md`
- `docs/product/UI_REDESIGN_SPEC.md`
- `docs/product/wpf-tech-spike/WPF_TECH_SPIKE_SPEC.md`
- `docs/product/IMPLEMENTATION_TRACKER.md`

## Findings

No blocking issues found after the layout fix.

## Review Notes

- The previous family list used a narrow right-side action column and 10px-wide canvas buttons. At normal panel widths, this compressed Chinese button labels into vertical text.
- The fix removes the narrow action column and moves actions into each card's content area. Buttons now have stable pixel widths, and the long category/photo/action metadata is truncated before it can crowd the row.
- Product UI rules were updated so future page changes must explicitly check button labels, chips, long titles, and descriptions for overlap, vertical text, and horizontal overflow.
- A legacy local image path in the default pet configuration was removed before rebuilding the public Windows package.

## Validation

- `python -m py_compile src-prototype/legacy-monolith/run-danhuang-desktop-pet.py`
- Source and E-drive runtime main script SHA256 matched after sync.
- Screenshot checks:
  - `qa/tk-family-list-actions-inline-900-20260617.png`
  - `qa/tk-family-list-actions-inline-900-scrolled-20260617.png`
- Windows package rebuilt and smoke-tested after the privacy scrub.

## Residual Risk

- Other pages may still contain older fixed-width rows. They should be included in the next screenshot baseline pass using the same no-overlap/no-vertical-text rule.
