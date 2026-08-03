/**
 * Unit tests for the backup scheduling logic.
 *
 * `isBackupDue` is a pure function — no React, no AsyncStorage, no Expo APIs —
 * so it runs cleanly in the Node test environment.
 *
 * Covers:
 *   - Off/each schedules: never due via the timer path
 *   - Daily schedule: due after ≥24 h, not due within 24 h
 *   - Weekly schedule: due after ≥7 days, not due within 7 days
 *   - Null lastBackupAt (never backed up): always due when scheduled
 *   - Boundary conditions at exactly the threshold
 */

import { isBackupDue } from '../utils/backupSchedule';

// ─── Convenience constants ────────────────────────────────────────────────────

const HOUR_MS  = 60 * 60 * 1000;
const DAY_MS   = 24 * HOUR_MS;
const WEEK_MS  = 7 * DAY_MS;

const NOW = new Date('2026-08-02T12:00:00.000Z').getTime();

/** ISO timestamp that is `delta` milliseconds before NOW */
function ago(delta: number): string {
  return new Date(NOW - delta).toISOString();
}

// ─── Off / each ───────────────────────────────────────────────────────────────

describe('isBackupDue – off schedule', () => {
  it('returns false when schedule is off, no prior backup', () => {
    expect(isBackupDue('off', null, NOW)).toBe(false);
  });

  it('returns false when schedule is off, even if a week has passed', () => {
    expect(isBackupDue('off', ago(WEEK_MS * 2), NOW)).toBe(false);
  });
});

describe('isBackupDue – each schedule', () => {
  it('returns false when schedule is each (trigger is per-encounter, not timer)', () => {
    expect(isBackupDue('each', null, NOW)).toBe(false);
  });

  it('returns false when schedule is each and last backup was a month ago', () => {
    expect(isBackupDue('each', ago(30 * DAY_MS), NOW)).toBe(false);
  });
});

// ─── Daily schedule ───────────────────────────────────────────────────────────

describe('isBackupDue – daily schedule', () => {
  it('returns true when last backup was null (never backed up)', () => {
    expect(isBackupDue('daily', null, NOW)).toBe(true);
  });

  it('returns true when last backup was more than 24 h ago', () => {
    expect(isBackupDue('daily', ago(DAY_MS + 1), NOW)).toBe(true);
  });

  it('returns true at exactly the 24-hour threshold', () => {
    expect(isBackupDue('daily', ago(DAY_MS), NOW)).toBe(true);
  });

  it('returns false when last backup was 1 ms before the 24-hour threshold', () => {
    expect(isBackupDue('daily', ago(DAY_MS - 1), NOW)).toBe(false);
  });

  it('returns false when last backup was 23 h 59 min ago', () => {
    expect(isBackupDue('daily', ago(DAY_MS - HOUR_MS), NOW)).toBe(false);
  });

  it('returns false when last backup was less than 1 minute ago', () => {
    expect(isBackupDue('daily', ago(30_000), NOW)).toBe(false);
  });
});

// ─── Weekly schedule ──────────────────────────────────────────────────────────

describe('isBackupDue – weekly schedule', () => {
  it('returns true when last backup was null (never backed up)', () => {
    expect(isBackupDue('weekly', null, NOW)).toBe(true);
  });

  it('returns true when last backup was more than 7 days ago', () => {
    expect(isBackupDue('weekly', ago(WEEK_MS + 1), NOW)).toBe(true);
  });

  it('returns true at exactly the 7-day threshold', () => {
    expect(isBackupDue('weekly', ago(WEEK_MS), NOW)).toBe(true);
  });

  it('returns false when last backup was 1 ms before the 7-day threshold', () => {
    expect(isBackupDue('weekly', ago(WEEK_MS - 1), NOW)).toBe(false);
  });

  it('returns false when last backup was 6 days 23 h ago', () => {
    expect(isBackupDue('weekly', ago(WEEK_MS - HOUR_MS), NOW)).toBe(false);
  });

  it('returns false when last backup was 1 day ago', () => {
    expect(isBackupDue('weekly', ago(DAY_MS), NOW)).toBe(false);
  });
});

// ─── Cross-schedule comparisons ───────────────────────────────────────────────

describe('isBackupDue – daily vs weekly threshold difference', () => {
  it('daily is due at 24h but weekly is not', () => {
    const lastBackup = ago(DAY_MS + 1);
    expect(isBackupDue('daily',  lastBackup, NOW)).toBe(true);
    expect(isBackupDue('weekly', lastBackup, NOW)).toBe(false);
  });

  it('both are due when last backup was 8 days ago', () => {
    const lastBackup = ago(8 * DAY_MS);
    expect(isBackupDue('daily',  lastBackup, NOW)).toBe(true);
    expect(isBackupDue('weekly', lastBackup, NOW)).toBe(true);
  });
});
