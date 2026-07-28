---
name: CivicShield Pro architecture
description: Key design decisions for the CivicShield Pro Expo mobile app — context shape, OCR API, voice input, high-contrast wiring.
---

## Runtime decisions

- **No backend** — all state in AsyncStorage; five storage keys: encounters, deadlines, fontsize, tour_done, high_contrast.
- **OCR** — free OCR.space API (`https://api.ocr.space/parse/image`, key `helloworld`), base64 image upload from expo-image-picker. Auto-runs extraction after OCR.
- **Translation** — MyMemory free API, 450-char limit, `auto|<targetCode>` pair.
- **Voice input** — Web Speech API (`window.SpeechRecognition || webkitSpeechRecognition`) on `Platform.OS === 'web'` only; graceful alert fallback on native Expo Go.
- **High contrast** — `HIGH_CONTRAST_OVERRIDES` exported from AppContext.tsx; `useColors()` reads `highContrast` from `AppContext` (exported raw context object) and merges overrides. Avoids circular deps by importing raw context, not the hook.
- **Font scaling** — `fs(base)` helper in AppContext multiplies by `FONT_SCALE[fontSize]`; all screens use it for every fontSize style value.
- **Tour** — `/tour` modal route (Stack screen), 7 steps, dot progress, "Try it Now" per step, persisted completion flag.
- **Deadlines dashboard** — `savedDeadlines[]` in context → gold alert cards pinned at top of Home above 911 banner; per-item dismiss + clear-all.

**Why:** keeps the app fully offline-capable and avoids any API key management burden on the user.
