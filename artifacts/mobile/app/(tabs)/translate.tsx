import React, { useRef, useState } from 'react';
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

const CHAR_LIMIT = 450;

async function translateText(
  text: string,
  sourceLang: string,
  targetLang: string,
): Promise<string> {
  const from = sourceLang === 'auto' ? 'auto' : sourceLang;
  const url = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=${from}|${targetLang}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Network error: ${res.status}`);
  const data = (await res.json()) as {
    responseData?: { translatedText?: string };
    responseStatus?: number;
  };
  if (data.responseStatus !== 200) throw new Error('Translation service error');
  return data.responseData?.translatedText ?? text;
}

export default function TranslateScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const { fs } = useApp();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;

  const [sourceText, setSourceText] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [sourceLang, setSourceLang] = useState<Language | 'auto'>('auto');
  const [targetLang, setTargetLang] = useState<Language>(LANGUAGES[1]);
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const [showSourcePicker, setShowSourcePicker] = useState(false);
  const [showTargetPicker, setShowTargetPicker] = useState(false);

  // Ref to hold the SpeechRecognition instance (web only)
  const recognitionRef = useRef<any>(null);

  const sourceCode = sourceLang === 'auto' ? 'auto' : sourceLang.code;
  const sourceName = sourceLang === 'auto' ? 'Auto-detect' : sourceLang.nativeName;

  const handleTranslate = async () => {
    if (!sourceText.trim()) return;
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setLoading(true);
    setTranslatedText('');
    try {
      const result = await translateText(sourceText, sourceCode, targetLang.code);
      setTranslatedText(result);
      AccessibilityInfo.announceForAccessibility(`Translation complete: ${result.slice(0, 100)}`);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch {
      Alert.alert('Translation Failed', 'Could not connect to translation service. Please try again.');
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
    setTranslatedText(sourceText);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
  };

  const handleClear = () => {
    setSourceText('');
    setTranslatedText('');
  };

  // ── Voice input ───────────────────────────────────────────────────────────
  const handleVoice = () => {
    if (Platform.OS !== 'web') {
      Alert.alert(
        '🎤 Voice Input',
        'Voice recording is fully supported on the web version of CivicShield Pro. Open the app in a browser to use voice-to-text translation.',
        [{ text: 'Got it' }],
      );
      return;
    }

    const win = window as any;
    const SpeechRecognition =
      win.SpeechRecognition || win.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      Alert.alert(
        'Not Supported',
        'Voice input is not supported in this browser. Try Chrome or Safari.',
      );
      return;
    }

    if (listening) {
      // Stop current session
      recognitionRef.current?.stop();
      setListening(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;

    // Use source language for recognition (fall back to English)
    recognition.lang = sourceCode !== 'auto' ? sourceCode : 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setListening(true);
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      AccessibilityInfo.announceForAccessibility('Listening. Speak now.');
    };

    recognition.onresult = (event: any) => {
      const transcript: string = event.results[0][0].transcript;
      setSourceText((prev) => (prev ? `${prev} ${transcript}` : transcript));
      setListening(false);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      AccessibilityInfo.announceForAccessibility(`Voice captured: ${transcript}`);
    };

    recognition.onerror = (event: any) => {
      setListening(false);
      if (event.error === 'no-speech') {
        Alert.alert('No Speech Detected', 'No voice was captured. Please speak clearly and try again.');
      } else if (event.error === 'not-allowed') {
        Alert.alert('Microphone Blocked', 'Please allow microphone access in your browser settings.');
      } else {
        Alert.alert('Voice Error', 'Could not capture voice. Please try again.');
      }
    };

    recognition.onend = () => setListening(false);

    try {
      recognition.start();
    } catch {
      setListening(false);
      Alert.alert('Error', 'Could not start voice recognition. Please try again.');
    }
  };

  const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: colors.background },
    header: {
      paddingTop: topPad + 12, paddingHorizontal: 20, paddingBottom: 16,
      borderBottomWidth: 1, borderBottomColor: colors.border,
    },
    headerTitle: { fontSize: fs(22), fontFamily: 'Inter_700Bold', color: colors.foreground },
    headerSub: { fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 2 },
    scroll: { flex: 1 },
    scrollContent: { padding: 16, paddingBottom: Platform.OS === 'web' ? 34 : 100 },
    langBar: { flexDirection: 'row', alignItems: 'center', marginBottom: 12, gap: 8 },
    langBtn: {
      flex: 1, backgroundColor: colors.card, borderRadius: 12, borderWidth: 1,
      borderColor: colors.border, paddingVertical: 10, paddingHorizontal: 14,
      flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    },
    langBtnText: { fontSize: fs(14), fontFamily: 'Inter_500Medium', color: colors.foreground },
    swapBtn: {
      width: 36, height: 36, borderRadius: 18, backgroundColor: colors.muted,
      alignItems: 'center', justifyContent: 'center',
    },
    card: {
      backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1,
      borderColor: colors.border, marginBottom: 12, overflow: 'hidden',
    },
    cardHeader: {
      flexDirection: 'row', alignItems: 'center', paddingHorizontal: 14,
      paddingTop: 12, marginBottom: 4, gap: 6,
    },
    cardLabel: {
      flex: 1, fontSize: fs(12), fontFamily: 'Inter_600SemiBold',
      color: colors.mutedForeground, textTransform: 'uppercase', letterSpacing: 0.6,
    },
    charCount: { fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground },
    charCountWarn: { color: colors.destructive },
    textInput: {
      fontSize: fs(16), fontFamily: 'Inter_400Regular', color: colors.foreground,
      paddingHorizontal: 14, paddingBottom: 14, minHeight: 120, textAlignVertical: 'top',
    },
    voiceRow: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 14, paddingBottom: 12, gap: 8 },
    voiceBtn: {
      flexDirection: 'row', alignItems: 'center', gap: 6,
      borderRadius: 20, paddingVertical: 8, paddingHorizontal: 14,
      borderWidth: 1.5,
    },
    voiceBtnActive: { backgroundColor: '#E05252' + '14', borderColor: '#E05252' },
    voiceBtnIdle: { backgroundColor: colors.muted, borderColor: colors.border },
    voiceBtnText: { fontSize: fs(13), fontFamily: 'Inter_500Medium' },
    translatedText: {
      fontSize: fs(16), fontFamily: 'Inter_400Regular', color: colors.foreground,
      paddingHorizontal: 14, paddingBottom: 14, minHeight: 80,
    },
    translatingWrap: { padding: 14, alignItems: 'center', flexDirection: 'row', gap: 8 },
    translatingText: { fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.mutedForeground },
    placeholderText: { fontSize: fs(15), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, padding: 14 },
    translateBtn: {
      backgroundColor: colors.primary, borderRadius: colors.radius, paddingVertical: 15,
      alignItems: 'center', justifyContent: 'center', flexDirection: 'row', gap: 8,
    },
    translateBtnDisabled: { opacity: 0.5 },
    translateBtnText: { fontSize: fs(16), fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' },
    tipCard: {
      backgroundColor: colors.primary + '0F', borderRadius: colors.radius, padding: 14,
      borderWidth: 1, borderColor: colors.primary + '20', marginTop: 12,
    },
    tipText: { fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 19 },
    listeningBadge: {
      flexDirection: 'row', alignItems: 'center', gap: 6,
      backgroundColor: '#E0525214', borderRadius: 20, paddingHorizontal: 12, paddingVertical: 6,
      alignSelf: 'center', marginBottom: 12,
    },
    listeningDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: '#E05252' },
  });

  const isOverLimit = sourceText.length >= CHAR_LIMIT;

  return (
    <View style={styles.container} accessibilityLabel="Translation screen">
      <View style={styles.header}>
        <Text style={styles.headerTitle} accessibilityRole="header">🌐 Translate</Text>
        <Text style={styles.headerSub}>Text or voice — 14 languages</Text>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent} keyboardShouldPersistTaps="handled">

        {/* Listening indicator */}
        {listening && (
          <View style={styles.listeningBadge} accessibilityLiveRegion="polite" accessibilityLabel="Listening for voice input">
            <View style={styles.listeningDot} />
            <Text style={{ fontSize: fs(13), fontFamily: 'Inter_600SemiBold', color: '#E05252' }}>
              Listening… speak now
            </Text>
          </View>
        )}

        {/* Language pair bar */}
        <View style={styles.langBar}>
          <Pressable
            style={styles.langBtn}
            onPress={() => setShowSourcePicker(true)}
            accessibilityLabel={`Source language: ${sourceName}`}
            accessibilityRole="button"
          >
            <Text style={styles.langBtnText}>{sourceName}</Text>
            <Feather name="chevron-down" size={16} color={colors.mutedForeground} />
          </Pressable>

          <Pressable
            style={[styles.swapBtn, sourceLang === 'auto' && { opacity: 0.4 }]}
            onPress={handleSwap}
            disabled={sourceLang === 'auto'}
            accessibilityLabel="Swap languages"
            accessibilityRole="button"
          >
            <Feather name="repeat" size={16} color={colors.foreground} />
          </Pressable>

          <Pressable
            style={styles.langBtn}
            onPress={() => setShowTargetPicker(true)}
            accessibilityLabel={`Target language: ${targetLang.nativeName}`}
            accessibilityRole="button"
          >
            <Text style={styles.langBtnText}>{targetLang.nativeName}</Text>
            <Feather name="chevron-down" size={16} color={colors.mutedForeground} />
          </Pressable>
        </View>

        {/* Source text card */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardLabel} accessibilityRole="header">Original</Text>
            <Text style={[styles.charCount, isOverLimit && styles.charCountWarn]}>
              {sourceText.length}/{CHAR_LIMIT}
            </Text>
            {sourceText.length > 0 && (
              <Pressable onPress={handleClear} hitSlop={8} accessibilityLabel="Clear text" accessibilityRole="button">
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
            accessibilityHint="Type or use voice button to add text"
          />
          {/* Voice button row */}
          <View style={styles.voiceRow}>
            <Pressable
              style={[styles.voiceBtn, listening ? styles.voiceBtnActive : styles.voiceBtnIdle]}
              onPress={handleVoice}
              accessibilityLabel={listening ? 'Stop voice recording' : 'Start voice recording'}
              accessibilityRole="button"
              accessibilityState={{ selected: listening }}
            >
              <Feather
                name={listening ? 'mic-off' : 'mic'}
                size={15}
                color={listening ? '#E05252' : colors.mutedForeground}
              />
              <Text style={[styles.voiceBtnText, { color: listening ? '#E05252' : colors.mutedForeground }]}>
                {listening ? 'Stop' : '🎤 Voice'}
              </Text>
            </Pressable>
            {Platform.OS !== 'web' && (
              <Text style={{ fontSize: fs(11), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, flex: 1 }}>
                Voice available on web version
              </Text>
            )}
          </View>
        </View>

        {/* Translated output card */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardLabel} accessibilityRole="header">{targetLang.name}</Text>
          </View>
          {loading ? (
            <View style={styles.translatingWrap}>
              <ActivityIndicator size="small" color={colors.primary} />
              <Text style={styles.translatingText}>Translating…</Text>
            </View>
          ) : translatedText ? (
            <Text style={styles.translatedText} selectable accessibilityLabel={`Translation: ${translatedText}`}>
              {translatedText}
            </Text>
          ) : (
            <Text style={styles.placeholderText}>Translation will appear here</Text>
          )}
        </View>

        {/* Translate button */}
        <Pressable
          style={[styles.translateBtn, (!sourceText.trim() || loading) && styles.translateBtnDisabled]}
          onPress={handleTranslate}
          disabled={!sourceText.trim() || loading}
          accessibilityLabel="Translate"
          accessibilityRole="button"
          accessibilityState={{ disabled: !sourceText.trim() || loading }}
        >
          <Feather name="globe" size={18} color="#FFFFFF" />
          <Text style={styles.translateBtnText}>Translate</Text>
        </Pressable>

        {/* Tips */}
        <View style={styles.tipCard}>
          <Text style={styles.tipText}>
            💡 <Text style={{ fontFamily: 'Inter_600SemiBold' }}>During an encounter:</Text> Show this screen to an officer or tap the mic 🎤 to capture what is being said and translate it instantly.{'\n\n'}
            🎤 <Text style={{ fontFamily: 'Inter_600SemiBold' }}>Voice note:</Text> Voice-to-text works in the web (browser) version. On mobile via Expo Go, type or paste your text.
          </Text>
        </View>
      </ScrollView>

      <LanguagePicker
        visible={showSourcePicker}
        selectedCode={sourceCode}
        onSelect={(lang) => setSourceLang(lang)}
        onClose={() => setShowSourcePicker(false)}
      />
      <LanguagePicker
        visible={showTargetPicker}
        selectedCode={targetLang.code}
        onSelect={(lang) => setTargetLang(lang)}
        onClose={() => setShowTargetPicker(false)}
      />
    </View>
  );
}
