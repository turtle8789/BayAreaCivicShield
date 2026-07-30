export interface Language {
  code: string;
  name: string;
  nativeName: string;
  /** True for languages written right-to-left (Arabic, Urdu, Hebrew, etc.) */
  isRTL?: boolean;
}

export const LANGUAGES: Language[] = [
  { code: 'en',    name: 'English',              nativeName: 'English' },
  { code: 'es',    name: 'Spanish',              nativeName: 'Español' },
  { code: 'zh-CN', name: 'Chinese (Simplified)', nativeName: '中文(简体)' },
  { code: 'zh-TW', name: 'Chinese (Traditional)',nativeName: '中文(繁體)' },
  { code: 'vi',    name: 'Vietnamese',            nativeName: 'Tiếng Việt' },
  { code: 'tl',    name: 'Tagalog',              nativeName: 'Tagalog' },
  { code: 'hi',    name: 'Hindi',                nativeName: 'हिन्दी' },
  { code: 'ko',    name: 'Korean',               nativeName: '한국어' },
  { code: 'ar',    name: 'Arabic',               nativeName: 'العربية', isRTL: true },
  { code: 'fr',    name: 'French',               nativeName: 'Français' },
  { code: 'pt',    name: 'Portuguese',           nativeName: 'Português' },
  { code: 'ru',    name: 'Russian',              nativeName: 'Русский' },
  { code: 'ja',    name: 'Japanese',             nativeName: '日本語' },
  { code: 'am',    name: 'Amharic',              nativeName: 'አማርኛ' },
  // Newly added
  { code: 'te',    name: 'Telugu',               nativeName: 'తెలుగు' },
  { code: 'pa',    name: 'Punjabi',              nativeName: 'ਪੰਜਾਬੀ' },
  { code: 'ta',    name: 'Tamil',                nativeName: 'தமிழ்' },
  { code: 'bn',    name: 'Bengali',              nativeName: 'বাংলা' },
  { code: 'id',    name: 'Indonesian',           nativeName: 'Bahasa Indonesia' },
  { code: 'ur',    name: 'Urdu',                 nativeName: 'اردو', isRTL: true },
  { code: 'tr',    name: 'Turkish',              nativeName: 'Türkçe' },
  { code: 'sw',    name: 'Swahili',              nativeName: 'Kiswahili' },
  { code: 'it',    name: 'Italian',              nativeName: 'Italiano' },
  { code: 'th',    name: 'Thai',                 nativeName: 'ภาษาไทย' },
  { code: 'ms',    name: 'Malay',                nativeName: 'Bahasa Melayu' },
  { code: 'ne',    name: 'Nepali',               nativeName: 'नेपाली' },
  { code: 'so',    name: 'Somali',               nativeName: 'Soomaali' },
  { code: 'ht',    name: 'Haitian Creole',       nativeName: 'Kreyòl ayisyen' },
];

export const DEFAULT_LANGUAGE = LANGUAGES[0];

export function getLanguageByCode(code: string): Language {
  return LANGUAGES.find((l) => l.code === code) ?? DEFAULT_LANGUAGE;
}
