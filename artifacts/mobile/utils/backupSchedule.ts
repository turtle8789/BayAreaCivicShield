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
 * Returns true when a timed backup is overdue.
 * 'off' and 'each' never trigger via the timer path.
 *
 * @param schedule    - current user preference
 * @param lastBackupAt - ISO timestamp of the last successful backup, or null
 * @param now          - current epoch ms (injectable for testing; defaults to Date.now())
 */
export function isBackupDue(
  schedule: BackupSchedule,
  lastBackupAt: string | null,
  now: number = Date.now(),
): boolean {
  if (schedule === 'off' || schedule === 'each') return false;
  const lastMs    = lastBackupAt ? new Date(lastBackupAt).getTime() : 0;
  const elapsed   = now - lastMs;
  const threshold = schedule === 'daily'
    ? 24 * 60 * 60 * 1000         // 24 hours
    : 7 * 24 * 60 * 60 * 1000;   // 7 days
  return elapsed >= threshold;
}
