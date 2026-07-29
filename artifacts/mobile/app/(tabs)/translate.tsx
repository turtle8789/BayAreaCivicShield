import React, { useEffect, useRef, useState } from 'react';
import {
  AccessibilityInfo,
  ActivityIndicator,
  Alert,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { Feather } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { LanguagePicker } from '@/components/LanguagePicker';
import { LANGUAGES, Language } from '@/constants/languages';
import { useApp } from '@/context/AppContext';
import { useColors } from '@/hooks/useColors';

// expo-speech-recognition requires a native dev/production build.
// We lazy-require it only when the user taps the mic button so the
// app doesn't crash in Expo Go (where the native module is absent).
// Web falls back to the browser Web Speech API instead.

const CHAR_LIMIT = 450;

async function doTranslate(text: string, from: string, to: string): Promise<string> {
  // Chunk long text into ≤450-char pieces (MyMemory free limit per request)
  const chunks: string[] = [];
  const words = text.split(' ');
  let current = '';
  for (const word of words) {
    if ((current + ' ' + word).length > 440) {
      if (current) chunks.push(current.trim());
      current = word;
    } else {
      current = current ? current + ' ' + word : word;
    }
  }
  if (current) chunks.push(current.trim());

  const translated: string[] = [];
  for (const chunk of chunks) {
    const langPair = `${from === 'auto' ? 'autodetect' : from}|${to}`;
    const url = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(chunk)}&langpair=${encodeURIComponent(langPair)}`;
    const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = (await res.json()) as {
      responseData?: { translatedText?: string };
      responseStatus?: number;
      responseDetails?: string;
    };
    // status 429 = rate limit; status 403 = quota exceeded
    if (data.responseStatus === 429 || data.responseStatus === 403) {
      throw new Error('RATE_LIMIT');
    }
    const result = data.responseData?.translatedText ?? '';
    // MyMemory sometimes returns "PLEASE SELECT TWO DISTINCT LANGUAGES" on same-lang pairs
    if (result.includes('PLEASE SELECT TWO DISTINCT LANGUAGES')) {
      throw new Error('SAME_LANG');
    }
    if (!result) throw new Error('Empty translation response');
    translated.push(result);
  }
  return translated.join(' ');
}

export default function TranslateScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const { fs } = useApp();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;

  const [sourceText, setSourceText]       = useState('');
  const [translatedText, setTranslated]   = useState('');
  const [sourceLang, setSourceLang]       = useState<Language | 'auto'>('auto');
  const [targetLang, setTargetLang]       = useState<Language>(LANGUAGES[1]);
  const [loading, setLoading]             = useState(false);
  const [listening, setListening]         = useState(false);
  const [showSourcePicker, setShowSrc]    = useState(false);
  const [showTargetPicker, setShowTgt]    = useState(false);

  // Holds cleanup for the current native recognition session
  const nativeCleanupRef = useRef<(() => void) | null>(null);
  // Holds the web SpeechRecognition instance
  const webRecRef = useRef<any>(null);

  const sourceCode = sourceLang === 'auto' ? 'auto' : sourceLang.code;
  const sourceName = sourceLang === 'auto' ? 'Auto-detect' : sourceLang.nativeName;

  // Clean up native listeners on unmount
  useEffect(() => {
    return () => { nativeCleanupRef.current?.(); };
  }, []);

  // ── Translate ──────────────────────────────────────────────────────────────
  const handleTranslate = async () => {
    if (!sourceText.trim()) return;
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setLoading(true);
    setTranslated('');
    try {
      const result = await doTranslate(sourceText, sourceCode, targetLang.code);
      setTranslated(result);
      AccessibilityInfo.announceForAccessibility(`Translation: ${result.slice(0, 80)}`);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch (err: any) {
      const msg = err?.message ?? '';
      if (msg === 'RATE_LIMIT') {
        Alert.alert('Rate Limit Reached', 'The free translation service has a daily limit. Please try again in a few minutes, or use shorter text.');
      } else if (msg === 'SAME_LANG') {
        Alert.alert('Same Language', 'Source and target language appear to be the same. Please select a different target language.');
      } else {
        Alert.alert('Translation Failed', 'Could not connect to the translation service. Check your internet connection and try again.');
      }
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    } finally {
      setLoading(false);
    }
  };

  const handleSwap = () => {
    if (sourceLang === 'auto') return;
    const tmp = sourceLang;
    setSourceLang(targetLang);
    setTargetLang(tmp);
    setSourceText(translatedText);
    setTranslated(sourceText);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
  };

  // ── Voice — web ────────────────────────────────────────────────────────────
  const startWebVoice = () => {
    const win = window as any;
    const SR = win.SpeechRecognition || win.webkitSpeechRecognition;
    if (!SR) {
      Alert.alert('Not Supported', 'Voice input is not supported in this browser. Try Chrome or Safari.');
      return;
    }
    const rec = new SR();
    webRecRef.current = rec;
    rec.lang = sourceCode !== 'auto' ? sourceCode : 'en-US';
    rec.continuous = false;
    rec.interimResults = false;
    rec.onstart  = () => { setListening(true); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium); };
    rec.onresult = (e: any) => {
      const t: string = e.results[0][0].transcript;
      setSourceText((p) => p ? `${p} ${t}` : t);
      setListening(false);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      AccessibilityInfo.announceForAccessibility(`Captured: ${t}`);
    };
    rec.onerror  = (e: any) => {
      setListening(false);
      if (e.error === 'not-allowed') Alert.alert('Blocked', 'Allow microphone in browser settings.');
      else if (e.error !== 'no-speech') Alert.alert('Voice Error', 'Could not capture voice. Try again.');
    };
    rec.onend = () => setListening(false);
    rec.start();
  };

  const stopWebVoice = () => { webRecRef.current?.stop(); setListening(false); };

  // ── Voice — native (expo-speech-recognition, lazy-loaded) ─────────────────
  const startNativeVoice = async () => {
    try {
      // Lazy require so the app doesn't crash in Expo Go when the
      // native module hasn't been linked (requires a dev/prod build).
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const { ExpoSpeechRecognitionModule } = require('expo-speech-recognition');

      const { granted } = await ExpoSpeechRecognitionModule.requestPermissionsAsync();
      if (!granted) {
        Alert.alert('Microphone Required', 'Please allow microphone access in Settings to use voice input.');
        return;
      }

      const lang = sourceCode !== 'auto' ? sourceCode : 'en-US';

      // Subscribe to events before starting
      const resSub = ExpoSpeechRecognitionModule.addListener(
        'result',
        (event: any) => {
          if (event.isFinal) {
            const transcript = (event.results?.[0]?.transcript ?? '').trim();
            if (transcript) {
              setSourceText((p) => p ? `${p} ${transcript}` : transcript);
              Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
              AccessibilityInfo.announceForAccessibility(`Captured: ${transcript}`);
            }
            cleanup();
          }
        },
      );
      const endSub = ExpoSpeechRecognitionModule.addListener('end', () => {
        setListening(false);
      });
      const errSub = ExpoSpeechRecognitionModule.addListener('error', (event: any) => {
        setListening(false);
        const msg = event.error === 'no-speech'
          ? 'No speech detected. Please try again.'
          : event.error === 'not-allowed'
          ? 'Microphone permission denied. Allow it in Settings.'
          : `Voice error: ${event.message ?? event.error}`;
        Alert.alert('Voice Error', msg);
        cleanup();
      });

      const cleanup = () => {
        resSub.remove();
        endSub.remove();
        errSub.remove();
        nativeCleanupRef.current = null;
      };

      nativeCleanupRef.current = () => {
        cleanup();
        try { ExpoSpeechRecognitionModule.abort(); } catch { /* ignore */ }
      };

      setListening(true);
      ExpoSpeechRecognitionModule.start({ lang, interimResults: false, continuous: false });

    } catch {
      // Module not available in this environment (Expo Go)
      Alert.alert(
        '🎤 Voice on Mobile',
        'Voice recognition requires a full app build and is not available in Expo Go.\n\nTo use voice on your device:\n• Build with EAS Build (expo build)\n• Or use the web version of the app where voice works today.',
        [{ text: 'Got it' }],
      );
    }
  };

  const stopNativeVoice = () => {
    try {
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const { ExpoSpeechRecognitionModule } = require('expo-speech-recognition');
      ExpoSpeechRecognitionModule.stop();
    } catch { /* ignore */ }
    setListening(false);
  };

  // ── Unified voice handler ──────────────────────────────────────────────────
  const handleVoice = () => {
    if (listening) {
      if (Platform.OS === 'web') stopWebVoice();
      else stopNativeVoice();
      return;
    }
    if (Platform.OS === 'web') startWebVoice();
    else startNativeVoice();
  };

  // ── Styles ─────────────────────────────────────────────────────────────────
  const styles = StyleSheet.create({
    container:      { flex: 1, backgroundColor: colors.background },
    header:         { paddingTop: topPad + 12, paddingHorizontal: 20, paddingBottom: 16, borderBottomWidth: 1, borderBottomColor: colors.border },
    headerTitle:    { fontSize: fs(22), fontFamily: 'Inter_700Bold', color: colors.foreground },
    headerSub:      { fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 2 },
    scroll:         { flex: 1 },
    scrollContent:  { padding: 16, paddingBottom: Platform.OS === 'web' ? 80 : 120, flexGrow: 1 },

    langBar:  { flexDirection: 'row', alignItems: 'center', marginBottom: 12, gap: 8 },
    langBtn:  { flex: 1, backgroundColor: colors.card, borderRadius: 12, borderWidth: 1, borderColor: colors.border, paddingVertical: 10, paddingHorizontal: 14, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
    langText: { fontSize: fs(14), fontFamily: 'Inter_500Medium', color: colors.foreground },
    swapBtn:  { width: 36, height: 36, borderRadius: 18, backgroundColor: colors.muted, alignItems: 'center', justifyContent: 'center' },

    card:       { backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1, borderColor: colors.border, marginBottom: 12, overflow: 'hidden' },
    cardHeader: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 14, paddingTop: 12, marginBottom: 4, gap: 6 },
    cardLabel:  { flex: 1, fontSize: fs(12), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase', letterSpacing: 0.6 },
    charCount:  { fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground },
    charWarn:   { color: colors.destructive },

    textInput:  { fontSize: fs(16), fontFamily: 'Inter_400Regular', color: colors.foreground, paddingHorizontal: 14, paddingBottom: 14, minHeight: 120, textAlignVertical: 'top' },

    voiceRow:        { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 14, paddingBottom: 12, gap: 8 },
    voiceBtn:        { flexDirection: 'row', alignItems: 'center', gap: 6, borderRadius: 20, paddingVertical: 8, paddingHorizontal: 14, borderWidth: 1.5 },
    voiceBtnActive:  { backgroundColor: '#E0525214', borderColor: '#E05252' },
    voiceBtnIdle:    { backgroundColor: colors.muted, borderColor: colors.border },
    voiceBtnText:    { fontSize: fs(13), fontFamily: 'Inter_500Medium' },
    voiceHint:       { flex: 1, fontSize: fs(11), fontFamily: 'Inter_400Regular', color: colors.mutedForeground },

    outputText:    { fontSize: fs(16), fontFamily: 'Inter_400Regular', color: colors.foreground, paddingHorizontal: 14, paddingBottom: 14, minHeight: 80 },
    translatingRow:{ padding: 14, alignItems: 'center', flexDirection: 'row', gap: 8 },
    translatingTxt:{ fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.mutedForeground },
    placeholder:   { fontSize: fs(15), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, padding: 14 },

    translateBtn:         { backgroundColor: colors.primary, borderRadius: colors.radius, paddingVertical: 15, alignItems: 'center', justifyContent: 'center', flexDirection: 'row', gap: 8 },
    translateBtnDisabled: { opacity: 0.5 },
    translateBtnText:     { fontSize: fs(16), fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' },

    listeningBadge: { flexDirection: 'row', alignItems: 'center', gap: 6, backgroundColor: '#E0525214', borderRadius: 20, paddingHorizontal: 12, paddingVertical: 6, alignSelf: 'center', marginBottom: 12 },
    listeningDot:   { width: 8, height: 8, borderRadius: 4, backgroundColor: '#E05252' },

    tipCard: { backgroundColor: colors.primary + '0F', borderRadius: colors.radius, padding: 14, borderWidth: 1, borderColor: colors.primary + '20', marginTop: 12 },
    tipText: { fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 19 },
  });

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle} accessibilityRole="header">🌐 Translate</Text>
        <Text style={styles.headerSub}>Text or voice — 14 languages</Text>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent} keyboardShouldPersistTaps="handled">

        {/* Listening indicator */}
        {listening && (
          <View style={styles.listeningBadge} accessibilityLiveRegion="polite">
            <View style={styles.listeningDot} />
            <Text style={{ fontSize: fs(13), fontFamily: 'Inter_600SemiBold', color: '#E05252' }}>
              Listening… speak now
            </Text>
          </View>
        )}

        {/* Language pair bar */}
        <View style={styles.langBar}>
          <Pressable style={styles.langBtn} onPress={() => setShowSrc(true)} accessibilityLabel={`Source: ${sourceName}`} accessibilityRole="button">
            <Text style={styles.langText}>{sourceName}</Text>
            <Feather name="chevron-down" size={16} color={colors.mutedForeground} />
          </Pressable>
          <Pressable style={[styles.swapBtn, sourceLang === 'auto' && { opacity: 0.4 }]} onPress={handleSwap} disabled={sourceLang === 'auto'} accessibilityLabel="Swap languages" accessibilityRole="button">
            <Feather name="repeat" size={16} color={colors.foreground} />
          </Pressable>
          <Pressable style={styles.langBtn} onPress={() => setShowTgt(true)} accessibilityLabel={`Target: ${targetLang.nativeName}`} accessibilityRole="button">
            <Text style={styles.langText}>{targetLang.nativeName}</Text>
            <Feather name="chevron-down" size={16} color={colors.mutedForeground} />
          </Pressable>
        </View>

        {/* Source card */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardLabel} accessibilityRole="header">Original</Text>
            <Text style={[styles.charCount, sourceText.length >= CHAR_LIMIT && styles.charWarn]}>
              {sourceText.length}/{CHAR_LIMIT}
            </Text>
            {sourceText.length > 0 && (
              <Pressable onPress={() => { setSourceText(''); setTranslated(''); }} hitSlop={8} accessibilityLabel="Clear" accessibilityRole="button">
                <Feather name="x" size={16} color={colors.mutedForeground} />
              </Pressable>
            )}
          </View>
          <TextInput
            style={styles.textInput}
            value={sourceText}
            onChangeText={(t) => setSourceText(t.slice(0, CHAR_LIMIT))}
            multiline
            placeholder="Enter text to translate…"
            placeholderTextColor={colors.mutedForeground}
            accessibilityLabel="Text to translate"
          />
          {/* Voice button */}
          <View style={styles.voiceRow}>
            {Platform.OS !== 'web' ? (
              // On native, voice requires a full dev/production build — not available in Expo Go.
              // Show a clearly disabled button so users know upfront instead of hitting an error.
              <View style={[styles.voiceBtn, styles.voiceBtnIdle, { opacity: 0.45 }]}>
                <Feather name="mic-off" size={15} color={colors.mutedForeground} />
                <Text style={[styles.voiceBtnText, { color: colors.mutedForeground }]}>🎤 Voice</Text>
              </View>
            ) : (
              <Pressable
                style={[styles.voiceBtn, listening ? styles.voiceBtnActive : styles.voiceBtnIdle]}
                onPress={handleVoice}
                accessibilityLabel={listening ? 'Stop listening' : 'Start voice input'}
                accessibilityRole="button"
              >
                <Feather name={listening ? 'mic-off' : 'mic'} size={15} color={listening ? '#E05252' : colors.mutedForeground} />
                <Text style={[styles.voiceBtnText, { color: listening ? '#E05252' : colors.mutedForeground }]}>
                  {listening ? 'Stop' : '🎤 Voice'}
                </Text>
              </Pressable>
            )}
            <Text style={styles.voiceHint}>
              {Platform.OS !== 'web'
                ? 'Voice needs a full app build — type text above'
                : listening ? 'Speak clearly…' : 'Tap mic to speak'}
            </Text>
          </View>
        </View>

        {/* Output card */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardLabel} accessibilityRole="header">{targetLang.name}</Text>
          </View>
          {loading
            ? <View style={styles.translatingRow}><ActivityIndicator size="small" color={colors.primary} /><Text style={styles.translatingTxt}>Translating…</Text></View>
            : translatedText
              ? <Text style={styles.outputText} selectable>{translatedText}</Text>
              : <Text style={styles.placeholder}>Translation will appear here</Text>
          }
        </View>

        {/* Translate button */}
        <Pressable
          style={[styles.translateBtn, (!sourceText.trim() || loading) && styles.translateBtnDisabled]}
          onPress={handleTranslate}
          disabled={!sourceText.trim() || loading}
          accessibilityLabel="Translate"
          accessibilityRole="button"
        >
          <Feather name="globe" size={18} color="#FFFFFF" />
          <Text style={styles.translateBtnText}>Translate</Text>
        </Pressable>

        {/* Tips */}
        <View style={styles.tipCard}>
          <Text style={styles.tipText}>
            💡 <Text style={{ fontFamily: 'Inter_600SemiBold' }}>During an encounter:</Text> Show this screen to an officer or tap 🎤 to capture and translate what is said.{'\n\n'}
            🎤 <Text style={{ fontFamily: 'Inter_600SemiBold' }}>Voice works on:</Text> Web (browser), iOS, and Android when running a full app build. Expo Go shows a setup guide instead.
          </Text>
        </View>
      </ScrollView>

      <LanguagePicker visible={showSourcePicker} selectedCode={sourceCode} onSelect={(l) => setSourceLang(l)} onClose={() => setShowSrc(false)} />
      <LanguagePicker visible={showTargetPicker} selectedCode={targetLang.code} onSelect={(l) => setTargetLang(l)} onClose={() => setShowTgt(false)} />
    </View>
  );
}
