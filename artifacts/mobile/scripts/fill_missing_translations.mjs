/**
 * Scans constants/i18n.ts, finds all keys missing any of the 14 newer
 * language codes, batch-translates them via OpenAI, and patches the file.
 *
 * Run: node scripts/fill_missing_translations.mjs
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const I18N_PATH = path.resolve(__dirname, '../constants/i18n.ts');

// All 27 non-English languages — so newly added English-only keys get fully translated
const NEW_LANGS = ['es','zh-CN','zh-TW','vi','tl','hi','ko','ar','fr','pt','ru','ja','am','te','pa','ta','bn','id','ur','tr','sw','it','th','ms','ne','so','ht'];

const LANG_NAMES = {
  te: 'Telugu', pa: 'Punjabi', ta: 'Tamil', bn: 'Bengali',
  id: 'Indonesian', ur: 'Urdu', tr: 'Turkish', sw: 'Swahili',
  it: 'Italian', th: 'Thai', ms: 'Malay', ne: 'Nepali',
  so: 'Somali', ht: 'Haitian Creole',
};

const OPENAI_KEY = process.env.AI_INTEGRATIONS_OPENAI_API_KEY;
const OPENAI_URL = process.env.AI_INTEGRATIONS_OPENAI_BASE_URL || 'https://api.openai.com/v1';

// ── Parse i18n.ts to find all entries + their lang coverage ──────────────────

function findMissingKeys(src) {
  // Match multi-line entries: '  \'key\': {' ... up to closing '},'
  const results = [];
  const lines = src.split('\n');
  let i = 0;
  while (i < lines.length) {
    const lineMatch = lines[i].match(/^  '([^']+)':\s*\{/);
    if (!lineMatch) { i++; continue; }

    const key = lineMatch[1];
    // Collect the body until we see a line that is just `  },`
    let body = '';
    let j = i + 1;
    while (j < lines.length && !lines[j].match(/^  \},?$/)) {
      body += lines[j] + '\n';
      j++;
    }

    // Extract English value (single-line or first occurrence of en:)
    const enMatch = body.match(/en:\s*'((?:[^'\\]|\\.)*)'/s) ||
                    body.match(/en:\s*"((?:[^"\\]|\\.)*)"/s);
    const enVal = enMatch ? enMatch[1].replace(/\\'/g, "'").replace(/\\n/g, '\n') : null;

    if (enVal) {
      const missing = NEW_LANGS.filter(l => {
        // Check if language code appears as a key in the body
        // Handle quoted keys (e.g. 'zh-CN':) and unquoted keys (e.g. es:)
        const escaped = l.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, '\\$&');
        return !new RegExp(`(?:'${escaped}'|\\b${escaped})\\s*:`).test(body);
      });
      if (missing.length > 0) {
        results.push({ key, en: enVal, missing, startLine: i, endLine: j });
      }
    }
    i = j + 1;
  }
  return results;
}

// ── OpenAI batch translation ───────────────────────────────────────────────────

async function translateBatch(texts, targetLangs) {
  // texts: string[]  targetLangs: string[]
  const langList = targetLangs.map(l => `${l} (${LANG_NAMES[l]})`).join(', ');
  const numbered = texts.map((t, i) => `${i + 1}. ${t}`).join('\n');

  const prompt = `You are a professional translator. Translate each numbered string into these ${targetLangs.length} languages: ${langList}.

RULES:
- Keep "CivicShield Pro" unchanged.
- Keep {n} placeholders unchanged.
- Return ONLY a JSON object where keys are language codes (${targetLangs.join(', ')}) and values are arrays of translated strings in the same order as input.
- No explanation, no markdown fences.

Strings to translate:
${numbered}`;

  const res = await fetch(`${OPENAI_URL}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${OPENAI_KEY}`,
    },
    body: JSON.stringify({
      model: 'gpt-5.4-mini',
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.2,
      max_tokens: 16000,
    }),
  });
  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`OpenAI error ${res.status}: ${errText.slice(0, 200)}`);
  }
  const data = await res.json();
  const raw = data.choices[0].message.content.trim();
  // Strip markdown fences if present
  const jsonStr = raw.replace(/^```(?:json)?\n?/, '').replace(/\n?```$/, '');
  return JSON.parse(jsonStr);
}

// ── Inject translations into source ──────────────────────────────────────────

function injectTranslations(src, key, newLangMap) {
  // Find the entry for this key and insert missing lang lines before the closing `  },`
  const keyPattern = new RegExp(`(  '${key.replace(/\./g, '\\.')}':.*?\\{[\\s\\S]*?)(  \\},?)`, 'm');
  const match = src.match(keyPattern);
  if (!match) {
    console.warn(`  ⚠️  Could not find key ${key} in source for injection`);
    return src;
  }

  // Build insertion lines (quote lang codes containing hyphens like zh-CN)
  const insertLines = Object.entries(newLangMap)
    .map(([lang, val]) => {
      const escaped = val.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/\n/g, '\\n');
      const langKey = lang.includes('-') ? `'${lang}'` : lang;
      return `    ${langKey}: '${escaped}',`;
    })
    .join('\n');

  const fullMatch = match[0];
  const closing = match[2];
  const withInsert = fullMatch.slice(0, fullMatch.length - closing.length) +
    insertLines + '\n' + closing;

  return src.replace(fullMatch, withInsert);
}

// ── Main ──────────────────────────────────────────────────────────────────────

async function main() {
  let src = fs.readFileSync(I18N_PATH, 'utf8');
  const missingEntries = findMissingKeys(src);
  console.log(`Found ${missingEntries.length} keys with missing translations.`);

  if (missingEntries.length === 0) {
    console.log('Nothing to do!');
    return;
  }

  const BATCH_SIZE = 4;
  let processed = 0;

  for (let bStart = 0; bStart < missingEntries.length; bStart += BATCH_SIZE) {
    const batch = missingEntries.slice(bStart, bStart + BATCH_SIZE);

    // Group by which languages are missing — try to do same-missing-set together
    // For simplicity, just use all NEW_LANGS for each batch
    const texts = batch.map(e => e.en);

    // Find union of missing langs in this batch
    const missingSet = new Set(batch.flatMap(e => e.missing));
    const targetLangs = NEW_LANGS.filter(l => missingSet.has(l));

    console.log(`Batch ${Math.floor(bStart / BATCH_SIZE) + 1}: translating ${batch.length} keys → ${targetLangs.join(', ')}`);

    let result;
    // Retry up to 3 times on JSON parse failure
    let attempts = 0;
    while (attempts < 3) {
      try {
        result = await translateBatch(texts, targetLangs);
        break;
      } catch (err) {
        attempts++;
        if (attempts >= 3) {
          console.error('  Translation error after 3 attempts:', err.message);
          result = null;
        } else {
          console.log(`  Retrying (attempt ${attempts + 1})...`);
          await new Promise(r => setTimeout(r, 1000));
        }
      }
    }
    if (!result) continue;

    // Inject each key's translations
    for (let i = 0; i < batch.length; i++) {
      const entry = batch[i];
      const newLangMap = {};
      for (const lang of entry.missing) {
        const vals = result[lang];
        if (vals && vals[i] !== undefined) {
          newLangMap[lang] = vals[i];
        }
      }
      if (Object.keys(newLangMap).length > 0) {
        src = injectTranslations(src, entry.key, newLangMap);
        processed++;
      }
    }

    // Write incrementally so progress is never lost on timeout
    fs.writeFileSync(I18N_PATH, src, 'utf8');
    console.log(`  ✓ Saved (${processed} keys so far)`);

    // Small delay to avoid rate limiting
    if (bStart + BATCH_SIZE < missingEntries.length) {
      await new Promise(r => setTimeout(r, 300));
    }
  }

  console.log(`\n✅ Done. Injected translations for ${processed} keys.`);
}

main().catch(err => { console.error('Fatal:', err); process.exit(1); });
