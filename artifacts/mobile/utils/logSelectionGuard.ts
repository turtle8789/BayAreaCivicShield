/**
 * Module-level store that lets the tab layout intercept tab presses while
 * the log-list screen has an active encounter selection.
 *
 * We intentionally keep this outside React state so the tab layout can read
 * it synchronously in a tabPress handler (which must call e.preventDefault()
 * before returning – no async/await possible there).
 */

type ClearFn = () => void;

let _active = false;
let _clearFn: ClearFn | null = null;

export const logSelectionGuard = {
  /** Called by log-list whenever selection state changes. */
  sync(active: boolean, clearFn: ClearFn): void {
    _active = active;
    _clearFn = active ? clearFn : null;
  },

  /** Called by log-list on unmount to avoid a dangling reference. */
  reset(): void {
    _active = false;
    _clearFn = null;
  },

  get isActive(): boolean {
    return _active;
  },

  /** Clears the selection in the log-list screen. */
  clear(): void {
    _clearFn?.();
  },
};
