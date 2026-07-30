---
name: RTL support pattern
description: How RTL (right-to-left) layout is implemented in CivicShield Pro
---

# RTL Support Pattern

## The rule
RTL languages (Arabic `ar`, Urdu `ur`) are flagged via `isRTL: true` on the `Language` type in `constants/languages.ts`. The app context derives `isRTL: boolean` from the selected language and exposes it from `useApp()`. Screens consume it via the `useRTL()` hook (`hooks/useRTL.ts`).

**Why:** Do NOT use `I18nManager.forceRTL` — it conflicts with manual row-reverse mirroring. After a bundle reload with `forceRTL(true)`, native RTL is active and React Native's `row` already follows RTL start/end, so the manual reversal double-flips everything. Decision: rely solely on manual mirroring for immediate runtime switching with no restart required.

## How to apply
Import `useRTL` in any screen that has directional layouts:
```ts
const { isRTL, rowDir, arrowIcon, backIcon, textStyle } = useRTL();
```
- `rowDir` → use as `flexDirection` on horizontal rows (`'row' | 'row-reverse'`)
- `arrowIcon` → forward chevron (`'chevron-right' | 'chevron-left'`)
- `backIcon` → navigation back arrow (`'arrow-left' | 'arrow-right'`)
- `textStyle` → apply to paragraph Text nodes (`textAlign` + `writingDirection`)

This applies to ALL components including LanguagePicker and any shared components.

## Adding more RTL languages
Add `isRTL: true` to the `Language` entry in `constants/languages.ts`. No other code changes needed.
