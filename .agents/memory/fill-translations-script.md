---
name: Fill translations script
description: How fill_missing_translations.mjs works and its current tuning.
---

# Fill translations script

**Location:** `artifacts/mobile/scripts/fill_missing_translations.mjs`

**How it works:**
- Scans `constants/i18n.ts` for keys that have only an `en:` value and are missing other languages.
- Groups missing keys into batches of 4, calls OpenAI `gpt-4o-mini` to translate into the missing languages.
- Writes results back to `i18n.ts` incrementally after each batch — safe to kill and restart.

**Current tuning (as of this session):**
- `BATCH_SIZE = 4` (was 8 — reduced to avoid truncated JSON responses)
- `max_tokens = 16000` (was 8192 — increased for 27-language responses)
- Retries 3 times on JSON parse failure before skipping a batch.

**Why batch_size=4:** With 27 target languages, each batch response can exceed 8192 tokens (rights/quiz strings are verbose). Reducing to 4 keys per batch keeps responses well under 16k tokens.

**Performance:** Each pass (one invocation) translates roughly 20–24 keys before hitting the 5-min shell timeout. With ~70 remaining keys, expect 3–4 runs to complete.

**How to run:**
```bash
cd artifacts/mobile
node scripts/fill_missing_translations.mjs
```
Run repeatedly until `English-only: 0`.
