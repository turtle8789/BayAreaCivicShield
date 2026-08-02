/**
 * Adds hub category label translation keys to i18n.ts,
 * translates them via OpenAI for all 28 languages, and patches the file.
 *
 * Run: node scripts/add_hub_category_keys.mjs
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const I18N_PATH = path.resolve(__dirname, '../constants/i18n.ts');

const OPENAI_KEY = process.env.AI_INTEGRATIONS_OPENAI_API_KEY;
const OPENAI_URL = process.env.AI_INTEGRATIONS_OPENAI_BASE_URL || 'https://api.openai.com/v1';

const ALL_LANGS = ['en','es','zh-CN','zh-TW','vi','tl','hi','ko','ar','fr','pt','ru','ja','am',
                   'te','pa','ta','bn','id','ur','tr','sw','it','th','ms','ne','so','ht'];

const CATEGORIES = [
  { key: 'hub.cat_legal_aid',    en: 'Free Legal Aid'     },
  { key: 'hub.cat_civil_rights', en: 'Civil Rights'        },
  { key: 'hub.cat_immigration',  en: 'Immigration'         },
  { key: 'hub.cat_housing',      en: 'Housing Rights'      },
  { key: 'hub.cat_employment',   en: 'Employment Rights'   },
  { key: 'hub.cat_lgbtq',        en: 'LGBTQ+ Legal'        },
  { key: 'hub.cat_forums',       en: 'Community Forums'    },
];

async function translateAll(texts, langs) {
  const prompt = `Translate each numbered phrase into all listed languages.
Languages: ${langs.filter(l => l !== 'en').join(', ')}
Keep "LGBTQ+" unchanged. Return ONLY a JSON object: { "langCode": ["trans1","trans2",...] }
No markdown, no extra text.

Phrases:
${texts.map((t, i) => `${i + 1}. ${t}`).join('\n')}`;

  const res = await fetch(`${OPENAI_URL}/chat/completions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${OPENAI_KEY}` },
    body: JSON.stringify({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.2,
      max_tokens: 3000,
    }),
  });
  const data = await res.json();
  const raw = data.choices[0].message.content.trim().replace(/^```(?:json)?\n?/, '').replace(/\n?```$/, '');
  return JSON.parse(raw);
}

async function main() {
  let src = fs.readFileSync(I18N_PATH, 'utf8');

  // Check if keys already exist
  if (src.includes("'hub.cat_legal_aid'")) {
    console.log('Hub category keys already exist in i18n.ts — skipping.');
    return;
  }

  const texts = CATEGORIES.map(c => c.en);
  const targetLangs = ALL_LANGS.filter(l => l !== 'en');

  console.log('Translating 7 hub category labels into 27 languages...');
  const result = await translateAll(texts, targetLangs);

  // Build entry strings
  const newEntries = CATEGORIES.map((cat, i) => {
    const parts = [`  '${cat.key}': {\n    en: '${cat.en}',`];
    for (const lang of targetLangs) {
      const vals = result[lang];
      if (vals && vals[i]) {
        const v = vals[i].replace(/\\/g, '\\\\').replace(/'/g, "\\'");
        const langKey = lang.includes('-') ? `'${lang}'` : lang;
        parts.push(`    ${langKey}: '${v}',`);
      }
    }
    parts.push('  },');
    return parts.join('\n');
  }).join('\n');

  // Inject before 'hub.not_found' (or after hub.filter_all)
  const insertMarker = "  'hub.not_found':";
  if (!src.includes(insertMarker)) {
    console.error("Could not find insertion point 'hub.not_found' in i18n.ts");
    process.exit(1);
  }
  src = src.replace(insertMarker, newEntries + '\n' + insertMarker);

  // Also add keys to I18nKey type union  
  const typeMarker = "| 'hub.open_website'";
  src = src.replace(typeMarker,
    "| 'hub.cat_legal_aid' | 'hub.cat_civil_rights' | 'hub.cat_immigration'\n" +
    "  | 'hub.cat_housing' | 'hub.cat_employment' | 'hub.cat_lgbtq' | 'hub.cat_forums'\n  " +
    typeMarker
  );

  fs.writeFileSync(I18N_PATH, src, 'utf8');
  console.log('✅ Hub category translation keys injected into i18n.ts');
}

main().catch(err => { console.error('Fatal:', err); process.exit(1); });
