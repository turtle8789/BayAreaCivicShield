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
