/**
 * Pure timing helpers for the PIN auto-lock feature.
 *
 * Extracted from AppShell so the threshold logic can be unit-tested without
 * React, AsyncStorage, or any Expo API.
 */

/**
 * Core threshold check: should the app lock given an elapsed background time?
 *
 * @param elapsedMs   - Milliseconds that have passed since the app was backgrounded
 * @param lockTimeout - Minutes until auto-lock; -1 = never lock, 0 = always lock
 * @returns true when the elapsed time meets or exceeds the configured threshold
 */
export function hasExceededLockTimeout(
  elapsedMs: number,
  lockTimeout: number,
): boolean {
  if (lockTimeout === -1) return false;
  const thresholdMs = lockTimeout * 60 * 1000;
  return elapsedMs >= thresholdMs;
}

/**
 * Parses a raw AsyncStorage string for the backgroundedAt timestamp and
 * decides whether the app should lock on resume.
 *
 * Safe-fallback contract: missing, empty, NaN, or non-finite values all
 * return false (stay unlocked) so a corrupt stored value can never
 * permanently lock a user out.
 *
 * @param stored      - Raw string from AsyncStorage (null when the key is absent)
 * @param lockTimeout - Minutes until auto-lock; -1 = never lock, 0 = always lock
 * @param now         - Current epoch ms — injected so tests don't need Date.now()
 * @returns true when the stored timestamp indicates the timeout has elapsed
 */
export function shouldLockOnStoredTimestamp(
  stored: string | null,
  lockTimeout: number,
  now: number,
): boolean {
  if (lockTimeout === -1) return false;
  if (!stored) return false; // absent or empty string → safe fallback
  const ts = Number(stored);
  if (!Number.isFinite(ts)) return false; // NaN / ±Infinity / corrupt → safe fallback
  return hasExceededLockTimeout(now - ts, lockTimeout);
}
