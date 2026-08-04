/**
 * Silent-backup utility.
 *
 * Extracted from AppContext so the file-writing logic can be unit-tested
 * independently of React, Expo, and AsyncStorage.
 */

import type { Encounter } from '@/context/AppContext';

// ─── Types ────────────────────────────────────────────────────────────────────

/** The shape of the JSON written to documentDirectory. */
export interface AutoBackupPayload {
  version: 1;
  app: 'CivicShield Pro';
  exportedAt: string; // ISO 8601
  encounters: Encounter[];
}

/** Minimal filesystem surface required by writeSilentBackup. */
export interface BackupFileSystem {
  /** Analogous to FileSystem.documentDirectory — may be null. */
  documentDirectory: string | null;
  /** Write `content` to `uri` as UTF-8. */
  writeAsStringAsync: (uri: string, content: string) => Promise<void>;
}

/** Result of a successful writeSilentBackup call. */
export interface SilentBackupResult {
  /** The exportedAt timestamp written into the file. */
  exportedAt: string;
  /** The full URI the file was written to. */
  fileUri: string;
}

// ─── File-name constant (shared with settings.tsx reader) ────────────────────

export const AUTO_BACKUP_FILENAME = 'civicshield-auto-backup.json';

// ─── Core logic ───────────────────────────────────────────────────────────────

/**
 * Build the JSON string for the auto-backup file.
 * Pure — no side effects.
 */
export function buildAutoBackupPayload(
  encounters: Encounter[],
  exportedAt: string,
): string {
  const payload: AutoBackupPayload = {
    version: 1,
    app: 'CivicShield Pro',
    exportedAt,
    encounters,
  };
  return JSON.stringify(payload);
}

/**
 * Write the auto-backup file to document storage and return metadata.
 *
 * @param encounters  Current encounter list (may be empty).
 * @param fs          Filesystem adapter (real or mock).
 * @param now         ISO timestamp to use as `exportedAt` (injectable for testing).
 */
export async function writeSilentBackup(
  encounters: Encounter[],
  fs: BackupFileSystem,
  now: string = new Date().toISOString(),
): Promise<SilentBackupResult> {
  const payload = buildAutoBackupPayload(encounters, now);
  const fileUri = (fs.documentDirectory ?? '') + AUTO_BACKUP_FILENAME;
  await fs.writeAsStringAsync(fileUri, payload);
  return { exportedAt: now, fileUri };
}
