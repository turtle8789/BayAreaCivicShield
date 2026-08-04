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

import { detectScheduleLoss, isBackupDue, resolveScheduleOnHydration } from '../utils/backupSchedule';

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

// ─── Hydration schedule resolution ───────────────────────────────────────────
//
// resolveScheduleOnHydration(schedFromStorage, legacyAutoBackup, backupFileExists)
// covers four distinct cases that must not drift out of sync in the provider:
//
//   Case 1 – Normal:          schedule key present → use it (any value incl. 'off')
//   Case 2 – Legacy migration: key absent, legacyAutoBackup='true' → silently migrate to 'each'
//   Case 3 – Storage wipe:    both keys absent, file exists → scheduleLost=true, default off
//   Case 4 – First install:   both keys absent, no file → scheduleLost=false, default off

describe('resolveScheduleOnHydration – case 1: schedule key present', () => {
  it('returns the stored schedule unchanged when key is present', () => {
    expect(resolveScheduleOnHydration('each', null, false))
      .toEqual({ schedule: 'each', scheduleLost: false });
  });

  it('returns "daily" with no loss when key is "daily"', () => {
    expect(resolveScheduleOnHydration('daily', 'true', true))
      .toEqual({ schedule: 'daily', scheduleLost: false });
  });

  it('returns "off" with no loss when user explicitly chose off', () => {
    // 'off' in storage means the user deliberately disabled — not a loss
    expect(resolveScheduleOnHydration('off', null, true))
      .toEqual({ schedule: 'off', scheduleLost: false });
  });

  it('returns "weekly" with no loss regardless of file state', () => {
    expect(resolveScheduleOnHydration('weekly', null, false))
      .toEqual({ schedule: 'weekly', scheduleLost: false });
  });
});

describe('resolveScheduleOnHydration – case 2: legacy migration', () => {
  it('migrates to "each" when new key absent but legacy key is "true"', () => {
    // This is the key false-positive case: a file exists AND legacy='true' — must NOT flag loss
    expect(resolveScheduleOnHydration(null, 'true', true))
      .toEqual({ schedule: 'each', scheduleLost: false });
  });

  it('migrates to "each" when legacy="true" even if no backup file exists yet', () => {
    expect(resolveScheduleOnHydration(null, 'true', false))
      .toEqual({ schedule: 'each', scheduleLost: false });
  });

  it('does NOT migrate when legacy key is "false"', () => {
    // legacyAutoBackup='false' is different from 'true' — no migration, and no file means no loss
    expect(resolveScheduleOnHydration(null, 'false', false))
      .toEqual({ schedule: 'off', scheduleLost: false });
  });

  it('does NOT migrate when legacy key is null — falls through to case 3 or 4', () => {
    expect(resolveScheduleOnHydration(null, null, true))
      .toEqual({ schedule: 'off', scheduleLost: true }); // case 3
  });
});

describe('resolveScheduleOnHydration – case 3: storage wipe detected', () => {
  it('flags scheduleLost when both keys absent and backup file exists', () => {
    // The canonical storage-wipe scenario: no schedule key, no legacy key, file survives
    expect(resolveScheduleOnHydration(null, null, true))
      .toEqual({ schedule: 'off', scheduleLost: true });
  });

  it('flags scheduleLost when legacy key is "false" and file exists', () => {
    // legacyAutoBackup='false' cannot rescue the schedule — file proves it was once on
    expect(resolveScheduleOnHydration(null, 'false', true))
      .toEqual({ schedule: 'off', scheduleLost: true });
  });
});

describe('resolveScheduleOnHydration – case 4: first install / clean state', () => {
  it('returns off with no loss on first install (no keys, no file)', () => {
    expect(resolveScheduleOnHydration(null, null, false))
      .toEqual({ schedule: 'off', scheduleLost: false });
  });

  it('returns off with no loss when legacy key is null and no file', () => {
    expect(resolveScheduleOnHydration(null, 'false', false))
      .toEqual({ schedule: 'off', scheduleLost: false });
  });
});

// ─── detectScheduleLoss (legacy helper — narrow backward-compat tests) ────────
//
// New code should use resolveScheduleOnHydration. These tests preserve the
// original helper's public contract.

describe('detectScheduleLoss', () => {
  it('returns true when schedule key is absent and backup file exists on disk', () => {
    expect(detectScheduleLoss(null, true)).toBe(true);
  });

  it('returns false when schedule key is absent and no backup file exists', () => {
    expect(detectScheduleLoss(null, false)).toBe(false);
  });

  it('returns false when schedule is "off" and file exists', () => {
    expect(detectScheduleLoss('off', true)).toBe(false);
  });

  it('returns false when schedule is "each" and file exists', () => {
    expect(detectScheduleLoss('each', true)).toBe(false);
  });

  it('returns false when schedule is "daily" and file exists', () => {
    expect(detectScheduleLoss('daily', true)).toBe(false);
  });

  it('returns false when schedule is "weekly" and file exists', () => {
    expect(detectScheduleLoss('weekly', true)).toBe(false);
  });

  it('returns false when schedule is "daily" and no file exists', () => {
    expect(detectScheduleLoss('daily', false)).toBe(false);
  });
});
