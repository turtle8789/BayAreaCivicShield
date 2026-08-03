/**
 * Unit tests for the PIN auto-lock timing logic.
 *
 * Both helpers are pure functions — no React, no AsyncStorage, no Expo APIs —
 * so they run cleanly in the Node test environment.
 *
 * Coverage matrix:
 *   hasExceededLockTimeout
 *     - elapsed < threshold          → false (stay unlocked)
 *     - elapsed === threshold        → true  (lock; boundary is inclusive)
 *     - elapsed > threshold          → true  (lock)
 *     - lockTimeout === -1           → false (never-lock mode)
 *     - lockTimeout === 0            → true  (always-lock; threshold is 0 ms)
 *
 *   shouldLockOnStoredTimestamp
 *     - elapsed < threshold          → false
 *     - elapsed >= threshold         → true
 *     - lockTimeout === -1           → false regardless of timestamp
 *     - lockTimeout === 0            → true regardless of elapsed time
 *     - stored === null              → false (safe fallback)
 *     - stored === ""                → false (safe fallback)
 *     - stored is non-numeric        → false (safe fallback)
 *     - stored === "NaN"             → false (safe fallback)
 *     - stored === "Infinity"        → false (safe fallback)
 *     - stored === "-Infinity"       → false (safe fallback)
 */

import {
  hasExceededLockTimeout,
  shouldLockOnStoredTimestamp,
} from '../utils/pinLockTiming';

// ─── Fixtures ─────────────────────────────────────────────────────────────────

const NOW = new Date('2026-08-02T12:00:00.000Z').getTime();

const MIN_MS = 60 * 1000; // one minute in ms

// ─── hasExceededLockTimeout ───────────────────────────────────────────────────

describe('hasExceededLockTimeout – below threshold (stay unlocked)', () => {
  it('returns false when elapsed is 0 ms and timeout is 1 minute', () => {
    expect(hasExceededLockTimeout(0, 1)).toBe(false);
  });

  it('returns false when elapsed is 1 ms short of the threshold', () => {
    expect(hasExceededLockTimeout(5 * MIN_MS - 1, 5)).toBe(false);
  });

  it('returns false when elapsed is zero and timeout is 5 minutes', () => {
    expect(hasExceededLockTimeout(0, 5)).toBe(false);
  });

  it('returns false when elapsed is well within a 30-minute timeout', () => {
    // 10 minutes elapsed, 30-minute timeout
    expect(hasExceededLockTimeout(10 * MIN_MS, 30)).toBe(false);
  });
});

describe('hasExceededLockTimeout – at or above threshold (should lock)', () => {
  it('returns true at exactly the threshold (boundary is inclusive)', () => {
    expect(hasExceededLockTimeout(5 * MIN_MS, 5)).toBe(true);
  });

  it('returns true when elapsed exceeds the threshold by 1 ms', () => {
    expect(hasExceededLockTimeout(5 * MIN_MS + 1, 5)).toBe(true);
  });

  it('returns true when elapsed far exceeds the threshold', () => {
    // Returned after 2 hours with a 1-minute timeout
    expect(hasExceededLockTimeout(120 * MIN_MS, 1)).toBe(true);
  });

  it('returns true at exactly the 1-minute threshold', () => {
    expect(hasExceededLockTimeout(MIN_MS, 1)).toBe(true);
  });
});

describe('hasExceededLockTimeout – lockTimeout === -1 (never lock)', () => {
  it('returns false regardless of elapsed time', () => {
    expect(hasExceededLockTimeout(0, -1)).toBe(false);
  });

  it('returns false even after a very long elapsed time', () => {
    expect(hasExceededLockTimeout(999_999_999, -1)).toBe(false);
  });
});

describe('hasExceededLockTimeout – lockTimeout === 0 (always lock)', () => {
  it('returns true when elapsed is 0 ms (threshold is 0 ms — always exceeded)', () => {
    // 0 >= 0 → lock
    expect(hasExceededLockTimeout(0, 0)).toBe(true);
  });

  it('returns true when elapsed is any positive number', () => {
    expect(hasExceededLockTimeout(1, 0)).toBe(true);
    expect(hasExceededLockTimeout(MIN_MS, 0)).toBe(true);
  });
});

// ─── shouldLockOnStoredTimestamp ──────────────────────────────────────────────

describe('shouldLockOnStoredTimestamp – elapsed below threshold (stay unlocked)', () => {
  it('returns false when the app was backgrounded 1 ms ago and timeout is 1 min', () => {
    const backgroundedAt = NOW - 1;
    expect(shouldLockOnStoredTimestamp(String(backgroundedAt), 1, NOW)).toBe(false);
  });

  it('returns false when elapsed is just under the configured timeout', () => {
    const backgroundedAt = NOW - (5 * MIN_MS - 1);
    expect(shouldLockOnStoredTimestamp(String(backgroundedAt), 5, NOW)).toBe(false);
  });
});

describe('shouldLockOnStoredTimestamp – elapsed at or above threshold (should lock)', () => {
  it('returns true at exactly the threshold (boundary is inclusive)', () => {
    const backgroundedAt = NOW - 5 * MIN_MS;
    expect(shouldLockOnStoredTimestamp(String(backgroundedAt), 5, NOW)).toBe(true);
  });

  it('returns true when the app was backgrounded longer than the timeout', () => {
    const backgroundedAt = NOW - 10 * MIN_MS;
    expect(shouldLockOnStoredTimestamp(String(backgroundedAt), 5, NOW)).toBe(true);
  });

  it('returns true after a multi-hour absence with a short timeout', () => {
    // Closed app for 2 hours, 1-minute timeout
    const backgroundedAt = NOW - 120 * MIN_MS;
    expect(shouldLockOnStoredTimestamp(String(backgroundedAt), 1, NOW)).toBe(true);
  });
});

describe('shouldLockOnStoredTimestamp – lockTimeout === -1 (never lock)', () => {
  it('returns false regardless of stored timestamp', () => {
    // Timestamp shows the threshold would be exceeded for any finite timeout,
    // but -1 means never lock.
    const backgroundedAt = NOW - 999 * MIN_MS;
    expect(shouldLockOnStoredTimestamp(String(backgroundedAt), -1, NOW)).toBe(false);
  });

  it('returns false even when stored is null', () => {
    expect(shouldLockOnStoredTimestamp(null, -1, NOW)).toBe(false);
  });
});

describe('shouldLockOnStoredTimestamp – lockTimeout === 0 (always lock)', () => {
  it('returns true when timestamp is present regardless of elapsed time', () => {
    // Came back immediately (1 ms), but timeout is 0 → always lock
    const backgroundedAt = NOW - 1;
    expect(shouldLockOnStoredTimestamp(String(backgroundedAt), 0, NOW)).toBe(true);
  });

  it('returns true when backgroundedAt === now (0 ms elapsed)', () => {
    expect(shouldLockOnStoredTimestamp(String(NOW), 0, NOW)).toBe(true);
  });
});

describe('shouldLockOnStoredTimestamp – missing timestamp (safe fallback)', () => {
  it('returns false when stored is null (key was never written)', () => {
    expect(shouldLockOnStoredTimestamp(null, 5, NOW)).toBe(false);
  });

  it('returns false when stored is an empty string', () => {
    expect(shouldLockOnStoredTimestamp('', 5, NOW)).toBe(false);
  });
});

describe('shouldLockOnStoredTimestamp – corrupt timestamp (safe fallback)', () => {
  it('returns false for a non-numeric string', () => {
    expect(shouldLockOnStoredTimestamp('corrupted', 5, NOW)).toBe(false);
  });

  it('returns false for "NaN"', () => {
    expect(shouldLockOnStoredTimestamp('NaN', 5, NOW)).toBe(false);
  });

  it('returns false for "Infinity"', () => {
    expect(shouldLockOnStoredTimestamp('Infinity', 5, NOW)).toBe(false);
  });

  it('returns false for "-Infinity"', () => {
    expect(shouldLockOnStoredTimestamp('-Infinity', 5, NOW)).toBe(false);
  });

  it('returns false for an object-like string', () => {
    expect(shouldLockOnStoredTimestamp('[object Object]', 5, NOW)).toBe(false);
  });

  it('returns false for a partial number string', () => {
    expect(shouldLockOnStoredTimestamp('123abc', 5, NOW)).toBe(false);
  });
});

// ─── End-to-end: mount-time rehydration scenario ──────────────────────────────

describe('end-to-end: mount-time rehydration from AsyncStorage', () => {
  it('stays unlocked when the app resumes within the timeout window', () => {
    // User backgrounded 2 minutes ago; timeout is 5 minutes
    const stored = String(NOW - 2 * MIN_MS);
    expect(shouldLockOnStoredTimestamp(stored, 5, NOW)).toBe(false);
  });

  it('locks when the app resumes after the timeout has elapsed', () => {
    // User backgrounded 6 minutes ago; timeout is 5 minutes
    const stored = String(NOW - 6 * MIN_MS);
    expect(shouldLockOnStoredTimestamp(stored, 5, NOW)).toBe(true);
  });

  it('locks at exactly the timeout boundary', () => {
    const stored = String(NOW - 5 * MIN_MS);
    expect(shouldLockOnStoredTimestamp(stored, 5, NOW)).toBe(true);
  });

  it('stays unlocked when lock is disabled (lockTimeout -1) even after a long absence', () => {
    const stored = String(NOW - 999 * MIN_MS);
    expect(shouldLockOnStoredTimestamp(stored, -1, NOW)).toBe(false);
  });

  it('always locks on resume when timeout is 0', () => {
    const stored = String(NOW - 1); // just backgrounded
    expect(shouldLockOnStoredTimestamp(stored, 0, NOW)).toBe(true);
  });

  it('safe fallback: stays unlocked when storage was cleared or never written', () => {
    expect(shouldLockOnStoredTimestamp(null, 5, NOW)).toBe(false);
  });
});

// ─── End-to-end: AppState foreground handler scenario ─────────────────────────

describe('end-to-end: AppState foreground transition threshold check', () => {
  it('does not lock when the user switches apps briefly', () => {
    const backgroundedAt = NOW - 30_000; // 30 seconds
    const elapsedMs = NOW - backgroundedAt;
    // 1-minute timeout; 30 s < 60 s
    expect(hasExceededLockTimeout(elapsedMs, 1)).toBe(false);
  });

  it('locks when the user is away longer than the configured timeout', () => {
    const backgroundedAt = NOW - 2 * MIN_MS;
    const elapsedMs = NOW - backgroundedAt;
    // 1-minute timeout; 2 min > 1 min
    expect(hasExceededLockTimeout(elapsedMs, 1)).toBe(true);
  });

  it('never locks in never-lock mode regardless of elapsed time', () => {
    const backgroundedAt = NOW - 60 * MIN_MS;
    const elapsedMs = NOW - backgroundedAt;
    expect(hasExceededLockTimeout(elapsedMs, -1)).toBe(false);
  });

  it('always locks in always-lock mode even for a brief switch', () => {
    const backgroundedAt = NOW - 500; // half a second
    const elapsedMs = NOW - backgroundedAt;
    expect(hasExceededLockTimeout(elapsedMs, 0)).toBe(true);
  });
});
