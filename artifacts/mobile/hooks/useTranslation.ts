import { useApp } from '@/context/AppContext';
import { I18nKey, TRANSLATIONS } from '@/constants/i18n';

/**
 * Returns a `t(key)` function that resolves the UI string for the
 * currently selected app language, falling back to English.
 *
 * Usage:
 *   const { t } = useT();
 *   <Text>{t('nav.home')}</Text>
 */
export function useT() {
  const { language } = useApp();
  const code = language.code;

  const t = (key: I18nKey): string => {
    const entry = TRANSLATIONS[key] as Record<string, string> | undefined;
    if (!entry) return key;
    return entry[code] ?? entry['en'] ?? key;
  };

  return { t };
}
