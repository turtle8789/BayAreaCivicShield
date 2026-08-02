/**
 * End-to-end tests for the protected-HTML export / decrypt flow.
 *
 * Each test:
 *   1. Encrypts a sample payload with `aesEncryptStrong` (the same function
 *      used in the app).
 *   2. Wraps it in a self-decrypting HTML file via `buildProtectedHtml`.
 *   3. Loads the resulting HTML's inline scripts in a Node vm context, using a
 *      minimal DOM stub — no network access, no jsdom ESM dependencies.
 *   4. Simulates a user entering the password and triggering `unlock()`.
 *   5. Asserts the expected state after decryption completes.
 *
 * These tests run entirely in Node — no network, no native modules required.
 */

import * as vm from 'vm';
import { aesEncryptStrong } from '../utils/encryption';
import { buildProtectedHtml } from '../utils/protectedHtml';

// PBKDF2-SHA256 with 100 000 iterations is intentionally slow; allow up to 30 s
// per test so the suite stays green on constrained CI machines.
jest.setTimeout(30_000);

// ─── minimal DOM stub ─────────────────────────────────────────────────────────

interface StubElement {
  value: string;
  disabled: boolean;
  textContent: string;
  innerHTML: string;
  style: { display: string };
  focus(): void;
  addEventListener(_event: string, _handler: unknown): void;
}

function makeElement(overrides: Partial<StubElement> = {}): StubElement {
  return {
    value: '',
    disabled: false,
    textContent: '',
    innerHTML: '',
    style: { display: '' },
    focus: () => {},
    addEventListener: () => {},
    ...overrides,
  };
}

interface MockDOM {
  getElementById(id: string): StubElement;
  elements: Record<string, StubElement>;
}

function createMockDOM(): MockDOM {
  const elements: Record<string, StubElement> = {
    'pwd':        makeElement({ style: { display: 'block' } }),
    'unlockBtn':  makeElement({ textContent: 'Unlock' }),
    'err':        makeElement({ style: { display: 'none' } }),
    'lock-card':  makeElement({ style: { display: 'block' } }),
    'doc':        makeElement({ style: { display: 'none' } }),
  };
  return {
    getElementById: (id: string) => elements[id] ?? makeElement(),
    elements,
  };
}

// ─── html script helpers ──────────────────────────────────────────────────────

/** Extract all inline <script> block contents from an HTML string. */
function extractInlineScripts(html: string): string[] {
  const scripts: string[] = [];
  const re = /<script>([\s\S]*?)<\/script>/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(html)) !== null) {
    scripts.push(m[1]);
  }
  return scripts;
}

/**
 * Load the HTML into a vm sandbox and trigger the unlock function with the
 * given password.  Returns the sandbox's mock DOM after unlock finishes.
 *
 * The unlock function internally calls setTimeout(..., 50).  We replace
 * setTimeout in the sandbox with a synchronous thunk so the test runs
 * immediately without real async delays.
 */
function simulateUnlock(html: string, password: string): MockDOM {
  const dom = createMockDOM();

  // Build the sandbox.  `this` at the top level of each script IS the sandbox,
  // so the CryptoJS UMD preamble (`t.CryptoJS = e()`) will set CryptoJS on it.
  const sandbox: Record<string, unknown> = {
    document: dom,
    // Run setTimeout callbacks synchronously so we don't need real async
    setTimeout: (fn: () => void, _ms: number) => fn(),
    // Guard against any stray globals the CryptoJS bundle may reference
    global: undefined,
  };

  vm.createContext(sandbox);

  // Execute all inline scripts in order (CryptoJS bundle first, then unlock)
  for (const src of extractInlineScripts(html)) {
    vm.runInContext(src, sandbox);
  }

  // Set the password and fire the unlock flow
  dom.elements['pwd'].value = password;
  vm.runInContext('unlock()', sandbox);

  return dom;
}

// ─── sample data ──────────────────────────────────────────────────────────────

const SAMPLE_HTML = `<!DOCTYPE html>
<html>
<head><meta charset="utf-8"/><title>Test</title></head>
<body>
  <h1>CivicShield Encounter Log</h1>
  <p>Traffic stop on 2026-08-01 at 10:30</p>
  <p>Officer: Badge #1234</p>
  <p>Outcome: Verbal warning issued</p>
</body>
</html>`;

const CORRECT_PASSWORD = 'correct-horse-battery-staple';
const WRONG_PASSWORD   = 'incorrect-password-xyz-99999';

// ─── tests ────────────────────────────────────────────────────────────────────

describe('Protected HTML export – structural checks', () => {
  let protectedHtml: string;

  beforeAll(() => {
    const payload = aesEncryptStrong(SAMPLE_HTML, CORRECT_PASSWORD);
    protectedHtml = buildProtectedHtml(payload, 'Encounter Log');
  });

  it('embeds the v:2 encrypted payload', () => {
    expect(protectedHtml).toContain('var PAYLOAD=`');
    expect(protectedHtml).toContain('"v":2');
    expect(protectedHtml).toContain('"s":');
    expect(protectedHtml).toContain('"c":');
    expect(protectedHtml).toContain('"h":');
  });

  it('bundles CryptoJS inline (no CDN call needed)', () => {
    expect(protectedHtml).toContain('CryptoJS');
    expect(protectedHtml).toContain('PBKDF2');
    expect(protectedHtml).toContain('AES');
    // Should not reference any external script src
    expect(protectedHtml).not.toMatch(/<script\s+src=/i);
  });

  it('includes at least 50 KB of content (bundle not truncated)', () => {
    // The CryptoJS bundle alone is ~68 KB; anything under 50 KB means it was
    // accidentally stripped or truncated.
    expect(protectedHtml.length).toBeGreaterThan(50_000);
  });

  it('safely escapes backticks in the PAYLOAD variable', () => {
    // If backticks are not escaped the template literal would be terminated
    // early, breaking the PAYLOAD assignment.
    const payloadMatch = protectedHtml.match(/var PAYLOAD=`([\s\S]*?(?:\\`[\s\S]*?)*)`;/);
    expect(payloadMatch).not.toBeNull();
  });
});

describe('Protected HTML export – decrypt flow (vm sandbox)', () => {
  let protectedHtml: string;

  beforeAll(() => {
    const payload = aesEncryptStrong(SAMPLE_HTML, CORRECT_PASSWORD);
    protectedHtml = buildProtectedHtml(payload, 'Encounter Log');
  });

  it('decrypts and renders the plaintext for the correct password', () => {
    const dom = simulateUnlock(protectedHtml, CORRECT_PASSWORD);
    const e = dom.elements;

    // Lock screen hidden, decrypted content shown
    expect(e['lock-card'].style.display).toBe('none');
    expect(e['doc'].style.display).toBe('block');
    expect(e['err'].style.display).not.toBe('block');

    // The rendered doc must contain the original plaintext content
    expect(e['doc'].innerHTML).toContain('CivicShield Encounter Log');
    expect(e['doc'].innerHTML).toContain('Traffic stop');
    expect(e['doc'].innerHTML).toContain('Badge #1234');
    expect(e['doc'].innerHTML).toContain('Verbal warning issued');
  });

  it('shows an error and does NOT reveal content for a wrong password', () => {
    const dom = simulateUnlock(protectedHtml, WRONG_PASSWORD);
    const e = dom.elements;

    // Lock screen must still be visible
    expect(e['lock-card'].style.display).not.toBe('none');
    // Error message must be shown
    expect(e['err'].style.display).toBe('block');
    // Decrypted content must not be shown
    expect(e['doc'].style.display).not.toBe('block');
    // Button must be re-enabled so the user can retry
    expect(e['unlockBtn'].disabled).toBe(false);
    expect(e['unlockBtn'].textContent).toBe('Unlock');
    // The content div must remain empty
    expect(e['doc'].innerHTML).toBe('');
  });
});

describe('aesEncryptStrong – pure Node round-trip checks', () => {
  it('produces a v:2 JSON envelope', () => {
    const payload = aesEncryptStrong('hello world', 'password');
    const parsed  = JSON.parse(payload) as Record<string, unknown>;
    expect(parsed.v).toBe(2);
    expect(typeof parsed.s).toBe('string');
    expect(typeof parsed.i).toBe('string');
    expect(typeof parsed.c).toBe('string');
    expect(typeof parsed.h).toBe('string');
  });

  it('produces unique ciphertext for each call (random salt + IV)', () => {
    const a = aesEncryptStrong('same message', 'same-pass');
    const b = aesEncryptStrong('same message', 'same-pass');
    const pA = JSON.parse(a) as { s: string; i: string; c: string };
    const pB = JSON.parse(b) as { s: string; i: string; c: string };
    // Salt, IV, and ciphertext must all differ
    expect(pA.s).not.toBe(pB.s);
    expect(pA.i).not.toBe(pB.i);
    expect(pA.c).not.toBe(pB.c);
  });
});
