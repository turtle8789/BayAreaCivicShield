/**
 * Pure helpers for the PIN brute-force lockout state machine.
 *
 * Keeping the logic here (away from React) lets us unit-test every branch
 * without mounting a component or mocking the Expo/AsyncStorage layer.
 */

export const MAX_ATTEMPTS    = 5;
export const LOCKOUT_SECONDS = 30;

export const KEY_ATTEMPTS     = '@pin_attempts';
export const KEY_LOCKED_UNTIL = '@pin_locked_until';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface HydratedLockoutState {
  /** Number of failed attempts to restore into React state. */
  attempts: number;
  /**
   * Unix-ms expiry to restore — null if not currently locked.
   * When null AND shouldClearStorage is true the caller must wipe AsyncStorage.
   */
  lockedUntil: number | null;
  /**
   * True when storage holds stale data that should be removed.
   * Covers two cases:
   *   1. The lockout has expired since the app was last open.
   *   2. The stored values were corrupted / non-finite.
   */
  shouldClearStorage: boolean;
}

export interface AttemptResult {
  /** Updated attempt count after this wrong-PIN press. */
  newAttempts: number;
  /**
   * Non-null when the new count meets or exceeds MAX_ATTEMPTS —
   * this is the Unix-ms timestamp the lockout should expire at.
   */
  lockedUntilExpiry: number | null;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

/**
 * Parse raw AsyncStorage strings into a validated lockout state.
 *
 * Rules:
 * - Non-finite / missing values are treated as 0 / null (fail-open).
 * - If a valid expiry exists but has already passed at `now`, the lockout is
 *   considered over — attempts reset to 0 and storage is flagged for clearing.
 * - If no expiry was stored (only an attempt count), that count is preserved
 *   so the counter carries across sessions even without a lockout.
 *
 * @param storedAttempts  Raw string from AsyncStorage.getItem(KEY_ATTEMPTS)
 * @param storedLocked    Raw string from AsyncStorage.getItem(KEY_LOCKED_UNTIL)
 * @param now             Current epoch ms (injectable for testing)
 */
export function parseLockoutState(
  storedAttempts: string | null,
  storedLocked: string | null,
  now: number,
): HydratedLockoutState {
  const parsedAttempts = storedAttempts ? parseInt(storedAttempts, 10) : 0;
  const parsedLocked   = storedLocked   ? parseInt(storedLocked,   10) : NaN;

  const safeAttempts = Number.isFinite(parsedAttempts) ? parsedAttempts : 0;
  const safeExpiry   = Number.isFinite(parsedLocked)   ? parsedLocked   : null;

  if (safeExpiry !== null) {
    if (safeExpiry > now) {
      // Active lockout — restore it
      return { attempts: safeAttempts, lockedUntil: safeExpiry, shouldClearStorage: false };
    } else {
      // Lockout has expired since last open — reset everything
      return { attempts: 0, lockedUntil: null, shouldClearStorage: true };
    }
  }

  // No lockout stored — just restore the attempt count (may be 0)
  return { attempts: safeAttempts, lockedUntil: null, shouldClearStorage: false };
}

/**
 * Compute the new lockout state after one wrong-PIN attempt.
 *
 * @param currentAttempts  The attempt count *before* this failure.
 * @param now              Current epoch ms (injectable for testing)
 */
export function computeAttemptResult(
  currentAttempts: number,
  now: number,
): AttemptResult {
  const newAttempts = currentAttempts + 1;
  if (newAttempts >= MAX_ATTEMPTS) {
    return { newAttempts, lockedUntilExpiry: now + LOCKOUT_SECONDS * 1000 };
  }
  return { newAttempts, lockedUntilExpiry: null };
}
