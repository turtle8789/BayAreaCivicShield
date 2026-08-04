/**
 * Pure backup-verification logic — no React, no Expo, no AsyncStorage.
 * Extracted so it can be unit-tested without mocking native modules.
 *
 * `verifyBackupContent` takes the raw file string plus context from the app
 * state and returns a typed outcome.  All IO (file-exists, read) lives in the
 * caller (`handleVerifyBackup` in settings.tsx).
 */

import { BackupSchedule, isBackupDue } from './backupSchedule';

// ─── Result types ────────────────────────────────────────────────────────────

export type VerifyBackupOutcome =
  | {
      status: 'ok';
      encounterCount: number;
      /** Encounter count currently held in the app — for comparison display. */
      currentCount: number;
      fileSizeKb: string;
      exportedAt: string; // ISO string from the file
    }
  | { status: 'corrupt_json' }
  | { status: 'unrecognised' }
  | { status: 'missing_timestamp' }
  /**
   * No successful backup has ever been recorded in AsyncStorage.
   * A file on disk (possibly from a previous install) cannot be confirmed current.
   */
  | { status: 'no_record' }
  /**
   * The recorded last-successful-backup time is old enough that the schedule
   * would already have triggered a new write — meaning the latest scheduled run
   * either hasn't fired yet or silently failed.
   */
  | { status: 'overdue' }
  /**
   * The file's `exportedAt` and the recorded `lastAutoBackupAt` differ by more
   * than the write-time tolerance, so the file is not from the latest successful run.
   */
  | { status: 'stale'; fileTs: string; recordedTs: string };

// ─── Pure verifier ────────────────────────────────────────────────────────────

/**
 * Verify that a backup file's content is current and matches app state.
 *
 * @param content               - raw UTF-8 content of the backup file
 * @param lastAutoBackupAt      - ISO timestamp stored in AsyncStorage after the last
 *                                successful write, or null if no backup has ever completed
 * @param backupSchedule        - the user's current schedule preference
 * @param currentEncounterCount - how many encounters the app currently holds
 * @param now                   - current epoch ms (injectable for testing)
 */
export function verifyBackupContent(
  content: string,
  lastAutoBackupAt: string | null,
  backupSchedule: BackupSchedule,
  currentEncounterCount: number,
  now: number = Date.now(),
): VerifyBackupOutcome {
  // ── 1. JSON parse ──────────────────────────────────────────────────────────
  let parsed: unknown;
  try { parsed = JSON.parse(content); } catch {
    return { status: 'corrupt_json' };
  }

  // ── 2. App / version markers ───────────────────────────────────────────────
  const obj = parsed as Record<string, unknown>;
  if (obj['app'] !== 'CivicShield Pro' || obj['version'] !== 1) {
    return { status: 'unrecognised' };
  }

  // ── 3. Require a parseable exportedAt ─────────────────────────────────────
  //    A missing or invalid timestamp is treated as corruption — any genuine
  //    CivicShield backup always includes this field.
  const exportedAtStr = obj['exportedAt'];
  if (typeof exportedAtStr !== 'string' || isNaN(Date.parse(exportedAtStr))) {
    return { status: 'missing_timestamp' };
  }

  // ── 4. Require a recorded successful-backup timestamp ─────────────────────
  //    Without it we cannot confirm the file is current (it may be from a prior
  //    install, a manual copy, or an older app version).
  if (!lastAutoBackupAt) {
    return { status: 'no_record' };
  }

  // ── 5. Schedule-level freshness ────────────────────────────────────────────
  //    `lastAutoBackupAt` is only written after a *successful* write.  If the
  //    schedule says a new backup is now due, the last write is old enough that
  //    we cannot claim the file is "current".
  if (isBackupDue(backupSchedule, lastAutoBackupAt, now)) {
    return { status: 'overdue' };
  }

  // ── 6. File-level freshness ────────────────────────────────────────────────
  //    `exportedAt` (in the file payload) and `lastAutoBackupAt` (persisted to
  //    AsyncStorage) are written milliseconds apart inside `performSilentBackup`.
  //    A mismatch larger than 60 s means the file is from a *different* (older)
  //    backup run — the latest scheduled write did not update the file.
  const fileTs     = new Date(exportedAtStr).getTime();
  const recordedTs = new Date(lastAutoBackupAt).getTime();
  if (Math.abs(fileTs - recordedTs) > 60_000) {
    return { status: 'stale', fileTs: exportedAtStr, recordedTs: lastAutoBackupAt };
  }

  // ── 7. All checks passed ───────────────────────────────────────────────────
  const encs           = obj['encounters'];
  const encounterCount = Array.isArray(encs) ? encs.length : 0;
  const fileSizeKb     = (content.length / 1024).toFixed(1);

  return {
    status: 'ok',
    encounterCount,
    currentCount: currentEncounterCount,
    fileSizeKb,
    exportedAt: exportedAtStr,
  };
}
