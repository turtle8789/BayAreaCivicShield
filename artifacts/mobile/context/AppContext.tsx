import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { DEFAULT_LANGUAGE, Language } from '@/constants/languages';

// ─── Encounter types ─────────────────────────────────────────────────────────

export type EncounterType =
  | 'traffic_stop'
  | 'arrest'
  | 'questioning'
  | 'citation'
  | 'search'
  | 'other';

export interface Encounter {
  id: string;
  date: string; // ISO string
  type: EncounterType;
  location: string;
  officerInfo: string;
  description: string;
  outcome: string;
}

export const ENCOUNTER_TYPE_LABELS: Record<EncounterType, string> = {
  traffic_stop: 'Traffic Stop',
  arrest: 'Arrest',
  questioning: 'Questioning',
  citation: 'Citation / Ticket',
  search: 'Search',
  other: 'Other',
};

// ─── Context types ────────────────────────────────────────────────────────────

interface AppContextValue {
  language: Language;
  setLanguage: (lang: Language) => void;
  encounters: Encounter[];
  addEncounter: (encounter: Omit<Encounter, 'id'>) => Promise<void>;
  deleteEncounter: (id: string) => Promise<void>;
  translateText: (text: string, targetLang: string) => Promise<string>;
  isTranslating: boolean;
}

const AppContext = createContext<AppContextValue | null>(null);

const STORAGE_KEY = 'civicshield_encounters';

// ─── Translation via free MyMemory API ───────────────────────────────────────

async function translateWithMyMemory(text: string, targetLang: string): Promise<string> {
  if (!text.trim()) return '';
  const truncated = text.slice(0, 450); // MyMemory free limit ~500 chars
  const url = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(truncated)}&langpair=auto|${targetLang}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = (await res.json()) as { responseData?: { translatedText?: string }; responseStatus?: number };
  if (data.responseStatus !== 200) throw new Error('Translation failed');
  return data.responseData?.translatedText ?? text;
}

// ─── Provider ─────────────────────────────────────────────────────────────────

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<Language>(DEFAULT_LANGUAGE);
  const [encounters, setEncounters] = useState<Encounter[]>([]);
  const [isTranslating, setIsTranslating] = useState(false);

  // Load persisted encounters on mount
  useEffect(() => {
    AsyncStorage.getItem(STORAGE_KEY)
      .then((raw) => {
        if (raw) setEncounters(JSON.parse(raw) as Encounter[]);
      })
      .catch(() => {/* ignore */});
  }, []);

  const persistEncounters = useCallback(async (list: Encounter[]) => {
    await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(list));
  }, []);

  const setLanguage = useCallback((lang: Language) => {
    setLanguageState(lang);
  }, []);

  const addEncounter = useCallback(async (data: Omit<Encounter, 'id'>) => {
    const encounter: Encounter = {
      ...data,
      id: Date.now().toString() + Math.random().toString(36).substring(2, 8),
    };
    const updated = [encounter, ...encounters];
    setEncounters(updated);
    await persistEncounters(updated);
  }, [encounters, persistEncounters]);

  const deleteEncounter = useCallback(async (id: string) => {
    const updated = encounters.filter((e) => e.id !== id);
    setEncounters(updated);
    await persistEncounters(updated);
  }, [encounters, persistEncounters]);

  const translateText = useCallback(async (text: string, targetLang: string): Promise<string> => {
    setIsTranslating(true);
    try {
      return await translateWithMyMemory(text, targetLang);
    } finally {
      setIsTranslating(false);
    }
  }, []);

  return (
    <AppContext.Provider
      value={{ language, setLanguage, encounters, addEncounter, deleteEncounter, translateText, isTranslating }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}
