import { useContext } from 'react';
import { useColorScheme } from 'react-native';
import colors from '@/constants/colors';
import { AppContext, HIGH_CONTRAST_OVERRIDES } from '@/context/AppContext';

/**
 * Returns the design tokens for the current color scheme.
 *
 * Layering order (lowest → highest priority):
 *  1. Dark / light palette from constants/colors.ts based on device scheme
 *  2. High-contrast overrides from AppContext when the user enables them
 */
export function useColors() {
  const scheme = useColorScheme();
  const ctx = useContext(AppContext);
  const highContrast = ctx?.highContrast ?? false;

  const palette = scheme === 'dark' ? colors.dark : colors.light;

  if (highContrast) {
    return { ...palette, ...HIGH_CONTRAST_OVERRIDES, radius: colors.radius };
  }

  return { ...palette, radius: colors.radius };
}
