/**
 * Pure backup-schedule helpers — no React, no Expo, no AsyncStorage.
 * Extracted here so they can be unit-tested in the Node/Jest environment.
 */

export type BackupSchedule = 'off' | 'each' | 'daily' | 'weekly';

export const BACKUP_SCHEDULE_LABELS: Record<BackupSchedule, string> = {
  off:    'Off',
  each:   'After each encounter',
  daily:  'Daily',
  weekly: 'Weekly',
};

/**
 * Preferred time-of-day window for scheduled (daily/weekly) backups.
 *
 * | Value       | Hours (local)  |
 * |-------------|----------------|
 * | any         | always         |
 * | morning     | 05:00 – 11:59  |
 * | afternoon   | 12:00 – 16:59  |
 * | evening     | 17:00 – 21:59  |
 */
export type BackupTimeWindow = 'any' | 'morning' | 'afternoon' | 'evening';

export const BACKUP_TIME_WINDOW_LABELS: Record<BackupTimeWindow, string> = {
  any:       'Any time',
  morning:   'Morning  (5 AM – noon)',
  afternoon: 'Afternoon  (noon – 5 PM)',
  evening:   'Evening  (5 PM – 10 PM)',
};

// ─── Hydration helpers ────────────────────────────────────────────────────────

/**
 * Result of resolving the backup schedule from raw storage values at app startup.
 * Extracted as a pure function so it can be unit-tested without mocking React or
 * native modules.
 */
export interface ScheduleHydrationResult {
  /** The effective schedule to apply in-memory. */
  schedule: BackupSchedule;
  /**
   * True when storage was wiped while a backup schedule was previously active.
   * The app should prompt the user to re-confirm their schedule.
   */
  scheduleLost: boolean;
}

/**
 * Resolves the effective backup schedule after hydration from AsyncStorage,
 * handling three distinct cases:
 *
 * 1. **Normal**: `STORAGE_BACKUP_SCHEDULE` is present → use it directly.
 * 2. **Legacy migration**: schedule key is absent but the old boolean
 *    `STORAGE_AUTO_BACKUP` key is `'true'` → silently migrate to `'each'`.
 * 3. **Storage wipe**: both keys are absent but a backup file exists on disk
 *    → the schedule was lost; default to `'off'` and flag `scheduleLost`.
 * 4. **First install**: no keys, no file → default to `'off'` silently.
 *
 * @param schedFromStorage    - raw value of STORAGE_BACKUP_SCHEDULE (null = absent)
 * @param legacyAutoBackup    - raw value of STORAGE_AUTO_BACKUP (null = absent)
 * @param backupFileExists    - whether the auto-backup file exists in documentDirectory
 */
export function resolveScheduleOnHydration(
  schedFromStorage: string | null,
  legacyAutoBackup: string | null,
  backupFileExists: boolean,
): ScheduleHydrationResult {
  // Case 1: new schedule key is present — use it as-is (covers all values incl. 'off')
  if (schedFromStorage !== null) {
    return { schedule: schedFromStorage as BackupSchedule, scheduleLost: false };
  }

  // Case 2: legacy key indicates auto-backup was on — silently migrate
  if (legacyAutoBackup === 'true') {
    return { schedule: 'each', scheduleLost: false };
  }

  // Case 3: no storage keys at all but a backup file survives → storage was wiped
  if (backupFileExists) {
    return { schedule: 'off', scheduleLost: true };
  }

  // Case 4: first install or clean state — no loss, default off
  return { schedule: 'off', scheduleLost: false };
}

/**
 * @deprecated Use resolveScheduleOnHydration instead.
 *
 * Returns true when the backup schedule key is absent from storage but an
 * auto-backup file already exists on disk AND the legacy auto-backup key
 * does not indicate a valid migration path.
 *
 * Kept for backward compatibility with existing unit tests. New callers should
 * use resolveScheduleOnHydration which handles all hydration cases in one place.
 */
export function detectScheduleLoss(
  scheduleFromStorage: string | null,
  backupFileExists: boolean,
): boolean {
  // The key being null (absent) is different from it being the string 'off'.
  // If it was explicitly set to 'off' by the user, that is not a loss.
  return scheduleFromStorage === null && backupFileExists;
}

/**
 * Returns true when the given hour-of-day falls inside the requested window.
 * @param window     - user's preferred window
 * @param hourOfDay  - 0-23 local hour
 */
export function isInTimeWindow(window: BackupTimeWindow, hourOfDay: number): boolean {
  switch (window) {
    case 'morning':   return hourOfDay >= 5  && hourOfDay < 12;
    case 'afternoon': return hourOfDay >= 12 && hourOfDay < 17;
    case 'evening':   return hourOfDay >= 17 && hourOfDay < 22;
    default:          return true; // 'any'
  }
}

/**
 * Returns true when a timed backup is overdue AND the current time falls
 * within the user's preferred time window.
 * 'off' and 'each' never trigger via the timer path.
 *
 * @param schedule    - current user preference
 * @param lastBackupAt - ISO timestamp of the last successful backup, or null
 * @param now          - current epoch ms (injectable for testing; defaults to Date.now())
 * @param timeWindow   - preferred time-of-day window (defaults to 'any')
 */
export function isBackupDue(
  schedule: BackupSchedule,
  lastBackupAt: string | null,
  now: number = Date.now(),
  timeWindow: BackupTimeWindow = 'any',
): boolean {
  if (schedule === 'off' || schedule === 'each') return false;
  const lastMs    = lastBackupAt ? new Date(lastBackupAt).getTime() : 0;
  const elapsed   = now - lastMs;
  const threshold = schedule === 'daily'
    ? 24 * 60 * 60 * 1000         // 24 hours
    : 7 * 24 * 60 * 60 * 1000;   // 7 days
  if (elapsed < threshold) return false;
  // Threshold has passed — also check the preferred time window
  const hourOfDay = new Date(now).getHours();
  return isInTimeWindow(timeWindow, hourOfDay);
}
