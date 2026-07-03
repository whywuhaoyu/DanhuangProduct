# Tk Chat Role Skill and Pet Category Code Review

Date: 2026-06-17

Scope:

- `src-prototype/legacy-monolith/run-danhuang-desktop-pet.py`
- `CHANGELOG.md`
- `src-prototype/legacy-monolith/CHANGELOG.md`
- `docs/product/PRODUCT_REQUIREMENTS.md`
- `docs/product/UI_REDESIGN_SPEC.md`
- `docs/product/wpf-tech-spike/WPF_TECH_SPIKE_SPEC.md`
- `docs/product/CURRENT_TK_UI_OPTIMIZATION_BACKLOG.md`
- `docs/product/IMPLEMENTATION_TRACKER.md`

## Findings

No blocking issues found in the reviewed change set.

## Review Notes

- Chat role Skill is stored in local settings and injected into both normal AI chat and fast reply prompts. Presets describe capability/style only and explicitly avoid impersonating real people.
- Pet categories are normalized through `infer_pet_category(...)`, persisted on pet records, shown in the pet profile UI, and injected into AI context plus image/action prompt generation.
- Basic action slots remain compatible with the existing atlas contract, while UI labels and generation prompts reinterpret the slots by category. This keeps old assets usable while allowing people, birds, aquatic creatures, robots, fantasy creatures, and object-like pets to use different motion semantics.
- The WPF spec and product docs now carry the same role Skill and pet category requirements, so the later WPF rewrite has a stable parity target.

## Validation

- `python -m py_compile src-prototype/legacy-monolith/run-danhuang-desktop-pet.py`
- Function-level checks:
  - knowledge questions trigger research while companion phrases do not
  - role Skill prompt includes the selected style and the no-impersonation constraint
  - species/category inference resolves dog, human, bird, fantasy, and large mammal examples
  - image/action prompts include category labels and category-specific action semantics

## Residual Risk

- The current role Skill list is intentionally local and generic. Future “达人风格” expansion should remain opt-in and avoid naming or imitating living people without explicit, compliant constraints.
- Existing pet records without `category` rely on inference from `species`; ambiguous species continue to fall back to `other`.
