/**
 * Removes duplicate property names inside translation objects in i18n.ts.
 * When a language code (like zh-CN) appears both inline on the same line as
 * `en:` AND as a standalone line, the standalone line is removed.
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const I18N_PATH  = path.resolve(__dirname, '../constants/i18n.ts');

const src   = fs.readFileSync(I18N_PATH, 'utf8');
const lines = src.split('\n');
const out   = [];
let removed = 0;

let i = 0;
while (i < lines.length) {
  const openMatch = lines[i].match(/^  '([^']+)':\s*\{/);
  if (!openMatch) {
    out.push(lines[i]);
    i++;
    continue;
  }

  // Collect the full object body
  out.push(lines[i]); // opening line
  i++;

  // Track property names seen so far in this object
  const seen = new Set();

  while (i < lines.length) {
    const line = lines[i];
    // Detect the closing line of the object
    if (/^  \},?$/.test(line)) {
      out.push(line);
      i++;
      break;
    }

    // Check if this line contains property keys
    // Match: optional whitespace, then one or more key:value pairs like `key: 'val',`
    // We need to find ALL property names on this line
    const propMatches = [...line.matchAll(/(?:^|,)\s*(?:'([^']+)'|(\w+))\s*:/g)];
    let isDuplicate = false;
    for (const m of propMatches) {
      const propName = m[1] ?? m[2];
      if (seen.has(propName)) {
        isDuplicate = true;
        break;
      }
      seen.add(propName);
    }

    if (isDuplicate) {
      removed++;
      // skip this line
    } else {
      out.push(line);
    }
    i++;
  }
}

fs.writeFileSync(I18N_PATH, out.join('\n'), 'utf8');
console.log(`✅ Removed ${removed} duplicate property lines from i18n.ts`);
