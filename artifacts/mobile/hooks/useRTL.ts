import { useApp } from '@/context/AppContext';

/**
 * Provides RTL-aware layout helpers derived from the currently selected
 * language.  Import this in any screen that has directional layouts.
 *
 * Usage:
 *   const { isRTL, rowDir, arrowIcon, backIcon, textAlign } = useRTL();
 *   <View style={{ flexDirection: rowDir }}>…</View>
 *   <Feather name={arrowIcon} />   // forward chevron, flips in RTL
 *   <Feather name={backIcon} />    // back arrow,    flips in RTL
 */
export function useRTL() {
  const { isRTL } = useApp();

  /** Use for `flexDirection` on horizontal rows that should mirror in RTL. */
  const rowDir: 'row' | 'row-reverse' = isRTL ? 'row-reverse' : 'row';

  /**
   * Forward chevron icon name — points right in LTR, left in RTL.
   * Use for "open detail" or "next" affordances.
   */
  const arrowIcon: 'chevron-right' | 'chevron-left' = isRTL
    ? 'chevron-left'
    : 'chevron-right';

  /**
   * Back / close arrow icon name — points left in LTR, right in RTL.
   * Use for "go back" navigation affordances.
   */
  const backIcon: 'arrow-left' | 'arrow-right' = isRTL
    ? 'arrow-right'
    : 'arrow-left';

  /**
   * Apply to Text nodes that carry paragraph-like content so the native
   * text engine renders Arabic/Urdu glyphs right-aligned.
   */
  const textStyle = {
    textAlign: isRTL ? ('right' as const) : ('left' as const),
    writingDirection: isRTL ? ('rtl' as const) : ('ltr' as const),
  };

  return { isRTL, rowDir, arrowIcon, backIcon, textStyle };
}
