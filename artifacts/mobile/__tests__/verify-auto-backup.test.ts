/**
 * Unit tests for the backup-verification helper.
 *
 * `verifyBackupContent` is pure — no Expo, no React, no AsyncStorage — so it
 * runs cleanly in the Node/Jest environment.
 *
 * Covers:
 *   - Corrupt / invalid JSON
 *   - Valid JSON but wrong app / version markers
 *   - Missing or invalid exportedAt timestamp
 *   - No recorded lastAutoBackupAt (cannot confirm currency)
 *   - Scheduled backup overdue (daily / weekly)
 *   - File timestamp drifts more than 60 s from recorded timestamp (stale file)
 *   - Happy path: current file, matching count
 *   - Happy path: count mismatch is still 'ok' (informational, not a failure)
 */

import { verifyBackupContent } from '../utils/verifyAutoBackup';

// ─── Helpers ──────────────────────────────────────────────────────────────────

const HOUR_MS = 60 * 60 * 1000;
const DAY_MS  = 24 * HOUR_MS;
const WEEK_MS = 7  * DAY_MS;

/** Epoch ms used as the "current time" throughout these tests. */
const NOW = new Date('2026-08-02T12:00:00.000Z').getTime();

/** ISO timestamp `delta` ms before NOW. */
function ago(delta: number): string {
  return new Date(NOW - delta).toISOString();
}

/**
 * Build a syntactically valid CivicShield backup JSON string.
 * Override individual fields via `overrides` to exercise failure paths.
 */
function makeBackupJson(overrides: Record<string, unknown> = {}): string {
  const base: Record<string, unknown> = {
    version:    1,
    app:        'CivicShield Pro',
    exportedAt: ago(30_000), // 30 s ago — within tolerance
    encounters: [{ id: '1' }, { id: '2' }],
  };
  return JSON.stringify({ ...base, ...overrides });
}

// ─── Corrupt / malformed input ────────────────────────────────────────────────

describe('verifyBackupContent – corrupt / malformed', () => {
  it('returns corrupt_json for empty string', () => {
    expect(verifyBackupContent('', ago(30_000), 'daily', 2, NOW)).toMatchObject({ status: 'corrupt_json' });
  });

  it('returns corrupt_json for plain text', () => {
    expect(verifyBackupContent('not json at all', ago(30_000), 'daily', 2, NOW)).toMatchObject({ status: 'corrupt_json' });
  });

  it('returns unrecognised when app field is wrong', () => {
    const content = makeBackupJson({ app: 'OtherApp' });
    expect(verifyBackupContent(content, ago(30_000), 'daily', 2, NOW)).toMatchObject({ status: 'unrecognised' });
  });

  it('returns unrecognised when version field is wrong', () => {
    const content = makeBackupJson({ version: 2 });
    expect(verifyBackupContent(content, ago(30_000), 'daily', 2, NOW)).toMatchObject({ status: 'unrecognised' });
  });

  it('returns missing_timestamp when exportedAt is absent', () => {
    const content = makeBackupJson({ exportedAt: undefined });
    expect(verifyBackupContent(content, ago(30_000), 'daily', 2, NOW)).toMatchObject({ status: 'missing_timestamp' });
  });

  it('returns missing_timestamp when exportedAt is null', () => {
    const content = makeBackupJson({ exportedAt: null });
    expect(verifyBackupContent(content, ago(30_000), 'daily', 2, NOW)).toMatchObject({ status: 'missing_timestamp' });
  });

  it('returns missing_timestamp when exportedAt is not a valid date string', () => {
    const content = makeBackupJson({ exportedAt: 'not-a-date' });
    expect(verifyBackupContent(content, ago(30_000), 'daily', 2, NOW)).toMatchObject({ status: 'missing_timestamp' });
  });
});

// ─── No recorded timestamp ────────────────────────────────────────────────────

describe('verifyBackupContent – no recorded lastAutoBackupAt', () => {
  it('returns no_record when lastAutoBackupAt is null (never backed up)', () => {
    const content = makeBackupJson({ exportedAt: ago(30_000) });
    expect(verifyBackupContent(content, null, 'daily', 2, NOW)).toMatchObject({ status: 'no_record' });
  });

  it('returns no_record even when the file looks perfectly valid', () => {
    const content = makeBackupJson({ exportedAt: ago(5_000) });
    expect(verifyBackupContent(content, null, 'each', 2, NOW)).toMatchObject({ status: 'no_record' });
  });
});

// ─── Schedule-level freshness (overdue) ───────────────────────────────────────

describe('verifyBackupContent – overdue (daily schedule)', () => {
  it('returns overdue when daily backup is more than 24 h old', () => {
    const lastAt  = ago(DAY_MS + 1);
    const content = makeBackupJson({ exportedAt: lastAt });
    expect(verifyBackupContent(content, lastAt, 'daily', 2, NOW)).toMatchObject({ status: 'overdue' });
  });

  it('returns overdue at exactly the 24-hour threshold', () => {
    const lastAt  = ago(DAY_MS);
    const content = makeBackupJson({ exportedAt: lastAt });
    expect(verifyBackupContent(content, lastAt, 'daily', 2, NOW)).toMatchObject({ status: 'overdue' });
  });

  it('does NOT return overdue when daily backup is 23 h 59 min old', () => {
    const lastAt  = ago(DAY_MS - HOUR_MS);
    const content = makeBackupJson({ exportedAt: lastAt });
    const result  = verifyBackupContent(content, lastAt, 'daily', 2, NOW);
    expect(result.status).toBe('ok');
  });
});

describe('verifyBackupContent – overdue (weekly schedule)', () => {
  it('returns overdue when weekly backup is more than 7 days old', () => {
    const lastAt  = ago(WEEK_MS + 1);
    const content = makeBackupJson({ exportedAt: lastAt });
    expect(verifyBackupContent(content, lastAt, 'weekly', 2, NOW)).toMatchObject({ status: 'overdue' });
  });

  it('does NOT return overdue when weekly backup is 6 days old', () => {
    const lastAt  = ago(6 * DAY_MS);
    const content = makeBackupJson({ exportedAt: lastAt });
    const result  = verifyBackupContent(content, lastAt, 'weekly', 2, NOW);
    expect(result.status).toBe('ok');
  });
});

describe('verifyBackupContent – each schedule never overdue via timer', () => {
  it('does not return overdue for "each" regardless of age', () => {
    const lastAt  = ago(30 * DAY_MS); // 30 days old
    const content = makeBackupJson({ exportedAt: lastAt });
    // isBackupDue returns false for 'each', so we fall through to file-level check;
    // the 60 s tolerance will fire here, but status is 'stale', not 'overdue'.
    const result = verifyBackupContent(content, lastAt, 'each', 2, NOW);
    expect(result.status).not.toBe('overdue');
  });
});

// ─── File-level freshness (stale) ─────────────────────────────────────────────

describe('verifyBackupContent – stale file', () => {
  it('returns stale when file exportedAt is > 60 s older than lastAutoBackupAt', () => {
    const fileExportedAt  = ago(5 * HOUR_MS);     // file written 5 h ago
    const lastAutoBackup  = ago(HOUR_MS);          // latest recorded success: 1 h ago
    const content = makeBackupJson({ exportedAt: fileExportedAt });
    const result  = verifyBackupContent(content, lastAutoBackup, 'daily', 2, NOW);
    expect(result).toMatchObject({ status: 'stale', fileTs: fileExportedAt, recordedTs: lastAutoBackup });
  });

  it('returns stale when file exportedAt is > 60 s NEWER than lastAutoBackupAt', () => {
    // Shouldn't happen in practice, but absolute-diff means we catch it both ways.
    const lastAutoBackup  = ago(5 * HOUR_MS);
    const fileExportedAt  = ago(HOUR_MS);
    const content = makeBackupJson({ exportedAt: fileExportedAt });
    const result  = verifyBackupContent(content, lastAutoBackup, 'daily', 2, NOW);
    expect(result).toMatchObject({ status: 'stale' });
  });

  it('does NOT return stale when difference is exactly 60 s', () => {
    const lastAutoBackup = ago(HOUR_MS);
    const fileExportedAt = ago(HOUR_MS + 60_000); // exactly at boundary
    const content = makeBackupJson({ exportedAt: fileExportedAt });
    // Math.abs(diff) === 60_000; condition is > 60_000 so this is NOT stale
    const result = verifyBackupContent(content, lastAutoBackup, 'daily', 2, NOW);
    expect(result.status).toBe('ok');
  });

  it('does NOT return stale when difference is 59 s', () => {
    const lastAutoBackup = ago(HOUR_MS);
    const fileExportedAt = ago(HOUR_MS + 59_000);
    const content = makeBackupJson({ exportedAt: fileExportedAt });
    const result  = verifyBackupContent(content, lastAutoBackup, 'daily', 2, NOW);
    expect(result.status).toBe('ok');
  });
});

// ─── Happy path ───────────────────────────────────────────────────────────────

describe('verifyBackupContent – ok', () => {
  it('returns ok with correct encounter count when everything matches', () => {
    const lastAutoBackup = ago(HOUR_MS);
    const fileExportedAt = ago(HOUR_MS + 5_000); // 5 s apart — well within tolerance
    const content = makeBackupJson({
      exportedAt: fileExportedAt,
      encounters: [{ id: '1' }, { id: '2' }, { id: '3' }],
    });
    const result = verifyBackupContent(content, lastAutoBackup, 'daily', 3, NOW);
    expect(result).toMatchObject({
      status:         'ok',
      encounterCount: 3,
      currentCount:   3,
    });
  });

  it('returns ok even when backup encounter count differs from current (informational)', () => {
    const lastAutoBackup = ago(30_000);
    const content = makeBackupJson({
      exportedAt: ago(30_000),
      encounters: [{ id: '1' }],
    });
    // Current app has 3 encounters but backup only recorded 1 — e.g. offline adds
    const result = verifyBackupContent(content, lastAutoBackup, 'daily', 3, NOW);
    expect(result).toMatchObject({ status: 'ok', encounterCount: 1, currentCount: 3 });
  });

  it('includes fileSizeKb in ok result', () => {
    const lastAutoBackup = ago(30_000);
    const content = makeBackupJson({ exportedAt: ago(30_000) });
    const result  = verifyBackupContent(content, lastAutoBackup, 'each', 2, NOW);
    expect(result.status).toBe('ok');
    if (result.status === 'ok') {
      expect(parseFloat(result.fileSizeKb)).toBeGreaterThan(0);
    }
  });

  it('works for "each" schedule with a very recent backup', () => {
    const lastAutoBackup = ago(5_000);
    const content = makeBackupJson({ exportedAt: ago(5_000) });
    expect(verifyBackupContent(content, lastAutoBackup, 'each', 2, NOW)).toMatchObject({ status: 'ok' });
  });

  it('works for "weekly" schedule with a backup from 3 days ago', () => {
    const lastAutoBackup = ago(3 * DAY_MS);
    const content = makeBackupJson({ exportedAt: ago(3 * DAY_MS + 2_000) }); // 2 s apart
    expect(verifyBackupContent(content, lastAutoBackup, 'weekly', 2, NOW)).toMatchObject({ status: 'ok' });
  });
});
