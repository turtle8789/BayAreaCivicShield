import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { DEFAULT_LANGUAGE, Language } from '@/constants/languages';
import { ForumPost, SEED_POSTS } from '@/constants/forum-data';

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
  date: string;
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

// ─── Saved Deadlines (from Document Analyzer → Dashboard) ─────────────────────

export interface SavedDeadline {
  id: string;
  text: string;
  source: string;
  savedAt: string;
}

// ─── Accessibility / Settings ─────────────────────────────────────────────────

export type FontSizeLevel = 'small' | 'medium' | 'large';

export const FONT_SCALE: Record<FontSizeLevel, number> = {
  small: 0.9,
  medium: 1.0,
  large: 1.2,
};

export const HIGH_CONTRAST_OVERRIDES = {
  background: '#000000',
  foreground: '#FFFFFF',
  text: '#FFFFFF',
  card: '#111111',
  cardForeground: '#FFFFFF',
  border: '#555555',
  input: '#555555',
  muted: '#1A1A1A',
  mutedForeground: '#AAAAAA',
};

// ─── Context types ────────────────────────────────────────────────────────────

interface AppContextValue {
  // Language
  language: Language;
  setLanguage: (lang: Language) => void;

  // Encounters
  encounters: Encounter[];
  addEncounter: (encounter: Omit<Encounter, 'id'>) => Promise<void>;
  deleteEncounter: (id: string) => Promise<void>;

  // Translation
  translateText: (text: string, targetLang: string) => Promise<string>;
  isTranslating: boolean;

  // Saved deadlines (dashboard)
  savedDeadlines: SavedDeadline[];
  addDeadline: (text: string, source: string) => Promise<void>;
  removeDeadline: (id: string) => Promise<void>;
  clearDeadlines: () => Promise<void>;

  // Forum (community discussion board)
  forumPosts: ForumPost[];  // user-created posts only (seed posts come from constants)
  addForumPost: (data: Omit<ForumPost, 'id' | 'helpfulCount' | 'markedHelpful' | 'isUserPost' | 'replies'>) => Promise<void>;
  toggleForumHelpful: (postId: string) => void;

  // Accessibility
  fontSize: FontSizeLevel;
  setFontSize: (size: FontSizeLevel) => void;
  fs: (base: number) => number;
  highContrast: boolean;
  setHighContrast: (v: boolean) => void;

  // Tour
  tourCompleted: boolean;
  setTourCompleted: (v: boolean) => void;
}

// Exported so useColors can read highContrast without a circular-dep issue
export const AppContext = createContext<AppContextValue | null>(null);

const STORAGE_ENCOUNTERS    = 'civicshield_encounters';
const STORAGE_DEADLINES     = 'civicshield_deadlines';
const STORAGE_FONT_SIZE     = 'civicshield_fontsize';
const STORAGE_TOUR          = 'civicshield_tour_done';
const STORAGE_HIGH_CONTRAST = 'civicshield_high_contrast';
const STORAGE_FORUM_POSTS   = 'civicshield_forum_posts';
const STORAGE_FORUM_HELPFUL = 'civicshield_forum_helpful'; // set of ids marked helpful

// ─── Translation via free MyMemory API ───────────────────────────────────────

async function translateWithMyMemory(text: string, targetLang: string): Promise<string> {
  if (!text.trim()) return '';
  const truncated = text.slice(0, 450);
  const url = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(truncated)}&langpair=auto|${targetLang}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = (await res.json()) as {
    responseData?: { translatedText?: string };
    responseStatus?: number;
  };
  if (data.responseStatus !== 200) throw new Error('Translation failed');
  return data.responseData?.translatedText ?? text;
}

// ─── Provider ─────────────────────────────────────────────────────────────────

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState]         = useState<Language>(DEFAULT_LANGUAGE);
  const [encounters, setEncounters]           = useState<Encounter[]>([]);
  const [isTranslating, setIsTranslating]     = useState(false);
  const [savedDeadlines, setSavedDeadlines]   = useState<SavedDeadline[]>([]);
  const [forumPosts, setForumPosts]           = useState<ForumPost[]>([]);
  const [helpfulIds, setHelpfulIds]           = useState<Set<string>>(new Set());
  const [fontSize, setFontSizeState]          = useState<FontSizeLevel>('medium');
  const [highContrast, setHighContrastState]  = useState(false);
  const [tourCompleted, setTourCompletedState]= useState(false);

  // ── Hydrate from AsyncStorage ─────────────────────────────────────────────
  useEffect(() => {
    Promise.all([
      AsyncStorage.getItem(STORAGE_ENCOUNTERS),
      AsyncStorage.getItem(STORAGE_DEADLINES),
      AsyncStorage.getItem(STORAGE_FONT_SIZE),
      AsyncStorage.getItem(STORAGE_TOUR),
      AsyncStorage.getItem(STORAGE_HIGH_CONTRAST),
      AsyncStorage.getItem(STORAGE_FORUM_POSTS),
      AsyncStorage.getItem(STORAGE_FORUM_HELPFUL),
    ]).then(([enc, dead, font, tour, hc, forum, helpful]) => {
      if (enc)     setEncounters(JSON.parse(enc) as Encounter[]);
      if (dead)    setSavedDeadlines(JSON.parse(dead) as SavedDeadline[]);
      if (font)    setFontSizeState(font as FontSizeLevel);
      if (tour)    setTourCompletedState(tour === 'true');
      if (hc)      setHighContrastState(hc === 'true');
      if (forum)   setForumPosts(JSON.parse(forum) as ForumPost[]);
      if (helpful) setHelpfulIds(new Set(JSON.parse(helpful) as string[]));
    }).catch(() => {});
  }, []);

  const setLanguage = useCallback((lang: Language) => setLanguageState(lang), []);

  // ── Encounters ────────────────────────────────────────────────────────────
  const addEncounter = useCallback(async (data: Omit<Encounter, 'id'>) => {
    const enc: Encounter = {
      ...data,
      id: Date.now().toString() + Math.random().toString(36).slice(2, 8),
    };
    const updated = [enc, ...encounters];
    setEncounters(updated);
    await AsyncStorage.setItem(STORAGE_ENCOUNTERS, JSON.stringify(updated));
  }, [encounters]);

  const deleteEncounter = useCallback(async (id: string) => {
    const updated = encounters.filter((e) => e.id !== id);
    setEncounters(updated);
    await AsyncStorage.setItem(STORAGE_ENCOUNTERS, JSON.stringify(updated));
  }, [encounters]);

  // ── Translation ───────────────────────────────────────────────────────────
  const translateText = useCallback(async (text: string, targetLang: string): Promise<string> => {
    setIsTranslating(true);
    try {
      return await translateWithMyMemory(text, targetLang);
    } finally {
      setIsTranslating(false);
    }
  }, []);

  // ── Saved Deadlines ───────────────────────────────────────────────────────
  const addDeadline = useCallback(async (text: string, source: string) => {
    const item: SavedDeadline = {
      id: Date.now().toString() + Math.random().toString(36).slice(2, 6),
      text: text.slice(0, 300),
      source,
      savedAt: new Date().toISOString(),
    };
    const updated = [item, ...savedDeadlines];
    setSavedDeadlines(updated);
    await AsyncStorage.setItem(STORAGE_DEADLINES, JSON.stringify(updated));
  }, [savedDeadlines]);

  const removeDeadline = useCallback(async (id: string) => {
    const updated = savedDeadlines.filter((d) => d.id !== id);
    setSavedDeadlines(updated);
    await AsyncStorage.setItem(STORAGE_DEADLINES, JSON.stringify(updated));
  }, [savedDeadlines]);

  const clearDeadlines = useCallback(async () => {
    setSavedDeadlines([]);
    await AsyncStorage.removeItem(STORAGE_DEADLINES);
  }, []);

  // ── Forum posts ───────────────────────────────────────────────────────────
  const addForumPost = useCallback(async (
    data: Omit<ForumPost, 'id' | 'helpfulCount' | 'markedHelpful' | 'isUserPost' | 'replies'>,
  ) => {
    const post: ForumPost = {
      ...data,
      id: `user_${Date.now()}`,
      helpfulCount: 0,
      markedHelpful: false,
      isUserPost: true,
      replies: [],
    };
    const updated = [post, ...forumPosts];
    setForumPosts(updated);
    await AsyncStorage.setItem(STORAGE_FORUM_POSTS, JSON.stringify(updated));
  }, [forumPosts]);

  // Toggle "helpful" for both seed posts and user posts (tracked by ID set)
  const toggleForumHelpful = useCallback((postId: string) => {
    const newIds = new Set(helpfulIds);
    if (newIds.has(postId)) {
      newIds.delete(postId);
    } else {
      newIds.add(postId);
    }
    setHelpfulIds(newIds);
    AsyncStorage.setItem(STORAGE_FORUM_HELPFUL, JSON.stringify([...newIds])).catch(() => {});

    // Also update count in user posts
    setForumPosts((prev) => {
      const updated = prev.map((p) =>
        p.id === postId
          ? { ...p, markedHelpful: !p.markedHelpful, helpfulCount: p.helpfulCount + (p.markedHelpful ? -1 : 1) }
          : p,
      );
      AsyncStorage.setItem(STORAGE_FORUM_POSTS, JSON.stringify(updated)).catch(() => {});
      return updated;
    });
  }, [helpfulIds]);

  // ── Accessibility ─────────────────────────────────────────────────────────
  const setFontSize = useCallback((size: FontSizeLevel) => {
    setFontSizeState(size);
    AsyncStorage.setItem(STORAGE_FONT_SIZE, size).catch(() => {});
  }, []);

  const fs = useCallback((base: number) => Math.round(base * FONT_SCALE[fontSize]), [fontSize]);

  const setHighContrast = useCallback((v: boolean) => {
    setHighContrastState(v);
    AsyncStorage.setItem(STORAGE_HIGH_CONTRAST, v ? 'true' : 'false').catch(() => {});
  }, []);

  // ── Tour ──────────────────────────────────────────────────────────────────
  const setTourCompleted = useCallback((v: boolean) => {
    setTourCompletedState(v);
    AsyncStorage.setItem(STORAGE_TOUR, v ? 'true' : 'false').catch(() => {});
  }, []);

  // Merge helpfulIds into seed posts so markedHelpful reflects persisted state
  const allForumPosts = forumPosts.map((p) => ({
    ...p,
    markedHelpful: helpfulIds.has(p.id),
  }));

  return (
    <AppContext.Provider
      value={{
        language, setLanguage,
        encounters, addEncounter, deleteEncounter,
        translateText, isTranslating,
        savedDeadlines, addDeadline, removeDeadline, clearDeadlines,
        forumPosts: allForumPosts, addForumPost, toggleForumHelpful,
        fontSize, setFontSize, fs,
        highContrast, setHighContrast,
        tourCompleted, setTourCompleted,
      }}
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
