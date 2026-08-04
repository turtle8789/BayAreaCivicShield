/**
 * Unit tests for the silent auto-backup path.
 *
 * `writeSilentBackup` and `buildAutoBackupPayload` are pure utility functions
 * that accept an injectable filesystem adapter — no React, no Expo, no
 * AsyncStorage — so they run cleanly in the Node/Jest environment.
 *
 * Covers:
 *   - Written file is valid JSON parseable as CivicShield Pro backup
 *   - Payload has correct `app`, `version`, and `exportedAt` fields
 *   - `exportedAt` in the file matches the returned `exportedAt` value
 *     (so callers can store it as `lastAutoBackupAt` with confidence)
 *   - Encounters array is written verbatim
 *   - Empty encounters array produces a valid file (no crash, no null)
 *   - File is written to documentDirectory + filename, not cacheDirectory
 *   - `buildAutoBackupPayload` round-trips through JSON.parse correctly
 */

import { buildAutoBackupPayload, writeSilentBackup, AUTO_BACKUP_FILENAME } from '../utils/silentBackup';
import type { Encounter } from '../context/AppContext';
import type { BackupFileSystem } from '../utils/silentBackup';

// ─── Fixtures ─────────────────────────────────────────────────────────────────

const SAMPLE_ENCOUNTER: Encounter = {
  id:          'enc-001',
  date:        '2026-07-15T09:30:00.000Z',
  type:        'traffic_stop',
  location:    '5th Ave & Broadway',
  officerInfo: 'Badge #1234',
  description: 'Routine stop at intersection',
  outcome:     'No citation issued',
};

const ANOTHER_ENCOUNTER: Encounter = {
  id:          'enc-002',
  date:        '2026-07-20T14:00:00.000Z',
  type:        'questioning',
  location:    'City Park',
  officerInfo: 'Plain-clothes officer',
  description: 'Asked about activity in area',
  outcome:     'Released without incident',
};

const FIXED_NOW = '2026-08-02T12:00:00.000Z';

/** Build a minimal mock filesystem that captures what was written. */
function makeMockFs(documentDirectory = 'file:///docs/'): {
  fs: BackupFileSystem;
  written: Map<string, string>;
} {
  const written = new Map<string, string>();
  const fs: BackupFileSystem = {
    documentDirectory,
    writeAsStringAsync: async (uri: string, content: string) => {
      written.set(uri, content);
    },
  };
  return { fs, written };
}

// ─── buildAutoBackupPayload ───────────────────────────────────────────────────

describe('buildAutoBackupPayload', () => {
  it('returns valid JSON', () => {
    const raw = buildAutoBackupPayload([SAMPLE_ENCOUNTER], FIXED_NOW);
    expect(() => JSON.parse(raw)).not.toThrow();
  });

  it('includes app = "CivicShield Pro"', () => {
    const parsed = JSON.parse(buildAutoBackupPayload([], FIXED_NOW));
    expect(parsed.app).toBe('CivicShield Pro');
  });

  it('includes version = 1', () => {
    const parsed = JSON.parse(buildAutoBackupPayload([], FIXED_NOW));
    expect(parsed.version).toBe(1);
  });

  it('includes the supplied exportedAt timestamp verbatim', () => {
    const parsed = JSON.parse(buildAutoBackupPayload([], FIXED_NOW));
    expect(parsed.exportedAt).toBe(FIXED_NOW);
  });

  it('includes the encounters array verbatim', () => {
    const parsed = JSON.parse(buildAutoBackupPayload([SAMPLE_ENCOUNTER, ANOTHER_ENCOUNTER], FIXED_NOW));
    expect(parsed.encounters).toHaveLength(2);
    expect(parsed.encounters[0].id).toBe('enc-001');
    expect(parsed.encounters[1].id).toBe('enc-002');
  });

  it('produces a valid file for an empty encounters array (no crash)', () => {
    const raw = buildAutoBackupPayload([], FIXED_NOW);
    const parsed = JSON.parse(raw);
    expect(Array.isArray(parsed.encounters)).toBe(true);
    expect(parsed.encounters).toHaveLength(0);
  });
});

// ─── writeSilentBackup – happy path ──────────────────────────────────────────

describe('writeSilentBackup – written file content', () => {
  it('writes a file that parses as valid JSON', async () => {
    const { fs, written } = makeMockFs();
    await writeSilentBackup([SAMPLE_ENCOUNTER], fs, FIXED_NOW);

    expect(written.size).toBe(1);
    const [, content] = [...written.entries()][0];
    expect(() => JSON.parse(content)).not.toThrow();
  });

  it('written file has app = "CivicShield Pro"', async () => {
    const { fs, written } = makeMockFs();
    await writeSilentBackup([SAMPLE_ENCOUNTER], fs, FIXED_NOW);

    const parsed = JSON.parse([...written.values()][0]);
    expect(parsed.app).toBe('CivicShield Pro');
  });

  it('written file has version = 1', async () => {
    const { fs, written } = makeMockFs();
    await writeSilentBackup([SAMPLE_ENCOUNTER], fs, FIXED_NOW);

    const parsed = JSON.parse([...written.values()][0]);
    expect(parsed.version).toBe(1);
  });

  it('written file exportedAt matches the returned exportedAt (timestamp sync)', async () => {
    const { fs, written } = makeMockFs();
    const result = await writeSilentBackup([SAMPLE_ENCOUNTER], fs, FIXED_NOW);

    const parsed = JSON.parse([...written.values()][0]);
    // This is the key invariant: the timestamp in the file and the one
    // returned to the caller (to be stored as lastAutoBackupAt) must match.
    expect(parsed.exportedAt).toBe(result.exportedAt);
    expect(result.exportedAt).toBe(FIXED_NOW);
  });

  it('written file contains all encounter fields correctly', async () => {
    const { fs, written } = makeMockFs();
    await writeSilentBackup([SAMPLE_ENCOUNTER], fs, FIXED_NOW);

    const parsed = JSON.parse([...written.values()][0]);
    expect(parsed.encounters).toHaveLength(1);
    const enc = parsed.encounters[0];
    expect(enc.id).toBe(SAMPLE_ENCOUNTER.id);
    expect(enc.type).toBe(SAMPLE_ENCOUNTER.type);
    expect(enc.location).toBe(SAMPLE_ENCOUNTER.location);
    expect(enc.officerInfo).toBe(SAMPLE_ENCOUNTER.officerInfo);
    expect(enc.description).toBe(SAMPLE_ENCOUNTER.description);
    expect(enc.outcome).toBe(SAMPLE_ENCOUNTER.outcome);
  });
});

// ─── writeSilentBackup – file URI ─────────────────────────────────────────────

describe('writeSilentBackup – file location', () => {
  it('writes to documentDirectory + auto-backup filename', async () => {
    const { fs, written } = makeMockFs('file:///documents/');
    await writeSilentBackup([SAMPLE_ENCOUNTER], fs, FIXED_NOW);

    const [uri] = [...written.keys()];
    expect(uri).toBe(`file:///documents/${AUTO_BACKUP_FILENAME}`);
  });

  it('returned fileUri matches the written key', async () => {
    const { fs, written } = makeMockFs('file:///documents/');
    const result = await writeSilentBackup([SAMPLE_ENCOUNTER], fs, FIXED_NOW);

    const [uri] = [...written.keys()];
    expect(result.fileUri).toBe(uri);
  });

  it('falls back to empty-string prefix when documentDirectory is null', async () => {
    const written = new Map<string, string>();
    const fs: BackupFileSystem = {
      documentDirectory: null,
      writeAsStringAsync: async (uri, content) => { written.set(uri, content); },
    };
    await writeSilentBackup([], fs, FIXED_NOW);

    const [uri] = [...written.keys()];
    expect(uri).toBe(AUTO_BACKUP_FILENAME);
  });
});

// ─── writeSilentBackup – empty encounters (edge case) ────────────────────────

describe('writeSilentBackup – empty encounters array', () => {
  it('does not throw when encounters is empty', async () => {
    const { fs } = makeMockFs();
    await expect(writeSilentBackup([], fs, FIXED_NOW)).resolves.not.toThrow();
  });

  it('writes encounters: [] (not null or undefined)', async () => {
    const { fs, written } = makeMockFs();
    await writeSilentBackup([], fs, FIXED_NOW);

    const parsed = JSON.parse([...written.values()][0]);
    expect(parsed.encounters).toEqual([]);
  });

  it('returns a valid exportedAt even with no encounters', async () => {
    const { fs } = makeMockFs();
    const result = await writeSilentBackup([], fs, FIXED_NOW);

    expect(result.exportedAt).toBe(FIXED_NOW);
    expect(() => new Date(result.exportedAt)).not.toThrow();
    expect(isNaN(new Date(result.exportedAt).getTime())).toBe(false);
  });
});

// ─── lastAutoBackupAt / exportedAt synchronisation ───────────────────────────

describe('writeSilentBackup – lastAutoBackupAt ↔ exportedAt synchronisation', () => {
  it('exportedAt in the file equals the value callers should store as lastAutoBackupAt', async () => {
    // This is the core contract: AppContext calls writeSilentBackup, takes the
    // returned exportedAt, and stores it via setLastAutoBackupAt /
    // AsyncStorage.setItem.  The file's exportedAt must equal that stored value
    // so the "verify backup" screen can confirm the file is current.
    const { fs, written } = makeMockFs();
    const result = await writeSilentBackup([SAMPLE_ENCOUNTER, ANOTHER_ENCOUNTER], fs, FIXED_NOW);

    const filePayload = JSON.parse([...written.values()][0]);
    expect(filePayload.exportedAt).toBe(result.exportedAt);
  });

  it('multiple consecutive writes each return distinct exportedAt values', async () => {
    const { fs } = makeMockFs();

    const t1 = '2026-08-02T11:00:00.000Z';
    const t2 = '2026-08-02T12:00:00.000Z';

    const r1 = await writeSilentBackup([], fs, t1);
    const r2 = await writeSilentBackup([], fs, t2);

    expect(r1.exportedAt).toBe(t1);
    expect(r2.exportedAt).toBe(t2);
    expect(r1.exportedAt).not.toBe(r2.exportedAt);
  });
});
