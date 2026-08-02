---
name: I18nKey derivation
description: I18nKey is auto-derived from the TRANSLATIONS object — do not maintain a manual union type.
---

# I18nKey derivation

**Rule:** `I18nKey` is defined at the bottom of `constants/i18n.ts` as:
```typescript
export type I18nKey = keyof typeof TRANSLATIONS;
```
The `TRANSLATIONS` object has no explicit type annotation (no `Translations = Record<I18nKey, ...>` wrapper).

**Why:** The original design had an explicit union type (`| 'nav.home' | 'nav.docs' | ...`) that required manual maintenance. When ~124 new keys were added by the `add_rights_keys.mjs` script, TypeScript rejected them because they weren't in the union. Switching to auto-derivation means new keys just work.

**How to apply:**
- When adding new i18n keys, just add them to `TRANSLATIONS` — they become valid `I18nKey` values automatically.
- Never reintroduce a manual union or `Translations = Record<I18nKey, ...>` type annotation.
- `useTranslation.ts` casts translation entries as `Record<string, string>` to allow dynamic language code indexing — keep this cast in place.
