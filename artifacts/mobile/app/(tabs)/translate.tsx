import React, { useEffect, useRef, useState } from 'react';
import {
  AccessibilityInfo,
  ActivityIndicator,
  Alert,
  NativeModules,
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
import { RIGHTS_CATEGORIES, RightsCategory } from '@/constants/rights-data';
import { useApp } from '@/context/AppContext';
import { useColors } from '@/hooks/useColors';
import { useRTL } from '@/hooks/useRTL';
import { useT } from '@/hooks/useTranslation';

// ── Pre-scripted officer-facing texts (always English) ────────────────────────
const SCRIPT_BEFORE =
  'Officer, before we begin, I am using a translation app to avoid any language barriers. I am recording with your knowledge for safety and accuracy.';

const SCRIPT_AFTER =
  'I understand, officer, and I will comply by providing identification documents, but I do not consent to any search of my vehicle or personal property. I am invoking my right to remain silent. I would like to speak with an attorney.';

// ── Keyword → rights category mapping ────────────────────────────────────────
function detectCategory(text: string): RightsCategory {
  const lower = text.toLowerCase();
  if (/license|registr|insurance|speeding|speed|traffic|pull.?over|driv|ticket/.test(lower)) {
    return RIGHTS_CATEGORIES.find((c) => c.id === 'traffic')!;
  }
  if (/search|trunk|vehicle|car|glove|bag|backpack|purse/.test(lower)) {
    return RIGHTS_CATEGORIES.find((c) => c.id === 'search')!;
  }
  if (/arrest|handcuff|custody|miranda|book|jail|detain/.test(lower)) {
    return RIGHTS_CATEGORIES.find((c) => c.id === 'arrest')!;
  }
  if (/immigr|ice|deport|visa|status|papers|citizen|country/.test(lower)) {
    return RIGHTS_CATEGORIES.find((c) => c.id === 'immigration')!;
  }
  if (/home|house|apart|door|warrant|knock|enter|inside/.test(lower)) {
    return RIGHTS_CATEGORIES.find((c) => c.id === 'home')!;
  }
  return RIGHTS_CATEGORIES.find((c) => c.id === 'police')!;
}

// ── Translation helpers ───────────────────────────────────────────────────────
async function translateText(text: string, to: string): Promise<string> {
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

  const results: string[] = [];
  for (const chunk of chunks) {
    const url = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(chunk)}&langpair=en|${encodeURIComponent(to)}`;
    const res = await fetch(url, { headers: { Accept: 'application/json' } });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json() as any;
    const translated = data?.responseData?.translatedText ?? '';
    if (!translated) throw new Error('Empty');
    results.push(translated);
  }
  return results.join(' ');
}

// ── TTS ───────────────────────────────────────────────────────────────────────
function ttsSpeak(text: string, langCode: string) {
  if (Platform.OS === 'web') {
    const win = window as any;
    if (!win.speechSynthesis) return;
    win.speechSynthesis.cancel();
    const utter = new win.SpeechSynthesisUtterance(text);
    utter.lang = langCode;
    win.speechSynthesis.speak(utter);
  } else {
    try {
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const Speech = require('expo-speech');
      Speech.stop();
      Speech.speak(text, { language: langCode });
    } catch {
      Alert.alert('TTS', 'Text-to-speech is not available in this environment.');
    }
  }
}

function ttsStop() {
  if (Platform.OS === 'web') {
    (window as any).speechSynthesis?.cancel();
  } else {
    try {
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      require('expo-speech').stop();
    } catch { /* ignore */ }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
export default function TranslateScreen() {
  const colors  = useColors();
  const insets  = useSafeAreaInsets();
  const { fs }  = useApp();
  const { t }   = useT();
  const { rowDir, textStyle } = useRTL();
  const topPad  = Platform.OS === 'web' ? 67 : insets.top;

  // Language selection
  const [targetLang, setTargetLang]       = useState<Language>(LANGUAGES[1]); // default: Spanish
  const [showPicker, setShowPicker]       = useState(false);

  // Clip 1 — pre-encounter script
  const [script1, setScript1]             = useState(SCRIPT_BEFORE);
  const [script1Trans, setScript1Trans]   = useState('');
  const [translating1, setTranslating1]   = useState(false);

  // Clip 2 — mic capture + advice
  const [officerText, setOfficerText]     = useState('');
  const [listening, setListening]         = useState(false);
  const [loadingAdvice, setLoadingAdvice] = useState(false);
  const [category, setCategory]           = useState<RightsCategory | null>(null);
  const [adviceText, setAdviceText]       = useState('');   // translated rights
  const [advisorySpeech, setAdvisorySpeech] = useState('');

  // Clip 3 — post-rights script
  const [script3, setScript3]             = useState(SCRIPT_AFTER);

  // Web speech recognition ref
  const webRecRef = useRef<any>(null);
  const nativeCleanupRef = useRef<(() => void) | null>(null);

  useEffect(() => () => { nativeCleanupRef.current?.(); ttsStop(); }, []);

  // ── Auto-translate script 1 when language changes ─────────────────────────
  useEffect(() => {
    if (targetLang.code === 'en') { setScript1Trans(script1); return; }
    setTranslating1(true);
    setScript1Trans('');
    translateText(script1, targetLang.code)
      .then(setScript1Trans)
      .catch(() => setScript1Trans('(translation unavailable)'))
      .finally(() => setTranslating1(false));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [targetLang]);

  // ── Get Advice ─────────────────────────────────────────────────────────────
  const handleGetAdvice = async () => {
    if (!officerText.trim()) return;
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    setLoadingAdvice(true);
    setAdviceText('');
    setAdvisorySpeech('');
    const cat = detectCategory(officerText);
    setCategory(cat);

    try {
      if (targetLang.code === 'en') {
        const combined = `${cat.title.toUpperCase()} RIGHTS:\n\n` + cat.rights.map((r) => `• ${r}`).join('\n');
        setAdviceText(combined);
        setAdvisorySpeech(combined);
      } else {
        // Translate the title and each right
        const titleTrans = await translateText(cat.title, targetLang.code);
        const rightsTrans = await Promise.allSettled(
          cat.rights.map((r) => translateText(r, targetLang.code))
        );
        const lines = rightsTrans.map((res, i) =>
          res.status === 'fulfilled' ? `• ${res.value}` : `• ${cat.rights[i]}`
        );
        const combined = `${titleTrans.toUpperCase()}:\n\n` + lines.join('\n');
        setAdviceText(combined);
        setAdvisorySpeech(combined);
        AccessibilityInfo.announceForAccessibility('Rights advice ready');
      }
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch {
      setAdviceText('(Could not translate advice — showing in English)\n\n' +
        cat.rights.map((r) => `• ${r}`).join('\n'));
    } finally {
      setLoadingAdvice(false);
    }
  };

  // ── Voice — web ────────────────────────────────────────────────────────────
  const startWebVoice = () => {
    const win = window as any;
    const SR = win.SpeechRecognition || win.webkitSpeechRecognition;
    if (!SR) { Alert.alert('Not Supported', 'Voice input requires Chrome or Safari.'); return; }
    const rec = new SR();
    webRecRef.current = rec;
    rec.lang = 'en-US';
    rec.continuous = false;
    rec.interimResults = false;
    rec.onstart  = () => { setListening(true); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium); };
    rec.onresult = (e: any) => {
      const captured: string = e.results[0][0].transcript;
      setOfficerText((p) => p ? `${p} ${captured}` : captured);
      setListening(false);
    };
    rec.onerror  = (e: any) => {
      setListening(false);
      if (e.error === 'not-allowed') Alert.alert('Blocked', 'Allow microphone access in browser settings.');
    };
    rec.onend = () => setListening(false);
    rec.start();
  };
  const stopWebVoice = () => { webRecRef.current?.stop(); setListening(false); };

  // ── Voice — native ─────────────────────────────────────────────────────────
  const startNativeVoice = async () => {
    // NativeModules.ExpoSpeechRecognition is undefined in Expo Go — guard before require()
    // to avoid a hard crash at the native bridge level (try/catch can't catch bridge errors).
    if (!NativeModules.ExpoSpeechRecognition) {
      Alert.alert(
        '🎤 Voice on Mobile',
        'Voice input requires a full app build and is not available in Expo Go.\n\nType what the officer said in the text box instead — or use the web version where voice works today.',
        [{ text: 'Got it' }],
      );
      return;
    }
    try {
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const { ExpoSpeechRecognitionModule } = require('expo-speech-recognition');
      const { granted } = await ExpoSpeechRecognitionModule.requestPermissionsAsync();
      if (!granted) { Alert.alert('Microphone Required', 'Please allow microphone access in Settings.'); return; }

      const resSub = ExpoSpeechRecognitionModule.addListener('result', (event: any) => {
        if (event.isFinal) {
          const transcript = (event.results?.[0]?.transcript ?? '').trim();
          if (transcript) setOfficerText((p) => p ? `${p} ${transcript}` : transcript);
          cleanup();
        }
      });
      const endSub = ExpoSpeechRecognitionModule.addListener('end', () => setListening(false));
      const errSub = ExpoSpeechRecognitionModule.addListener('error', (event: any) => {
        setListening(false);
        if (event.error !== 'no-speech') Alert.alert('Voice Error', event.message ?? event.error);
        cleanup();
      });
      const cleanup = () => {
        resSub.remove(); endSub.remove(); errSub.remove();
        nativeCleanupRef.current = null;
      };
      nativeCleanupRef.current = () => {
        cleanup();
        try { ExpoSpeechRecognitionModule.abort(); } catch { /* ignore */ }
      };
      setListening(true);
      ExpoSpeechRecognitionModule.start({ lang: 'en-US', interimResults: false, continuous: false });
    } catch {
      Alert.alert('Voice on Mobile', 'Voice input requires a full app build (EAS Build), not Expo Go.\n\nType what the officer said instead.');
    }
  };
  const stopNativeVoice = () => {
    try { require('expo-speech-recognition').ExpoSpeechRecognitionModule.stop(); } catch { /* ignore */ }
    setListening(false);
  };

  const handleMic = () => {
    if (listening) { Platform.OS === 'web' ? stopWebVoice() : stopNativeVoice(); return; }
    Platform.OS === 'web' ? startWebVoice() : startNativeVoice();
  };

  // ── Styles ─────────────────────────────────────────────────────────────────
  const S = StyleSheet.create({
    container:   { flex: 1, backgroundColor: colors.background },
    header:      { paddingTop: topPad + 12, paddingHorizontal: 20, paddingBottom: 14,
                   borderBottomWidth: 1, borderBottomColor: colors.border },
    headerTitle: { fontSize: fs(22), fontFamily: 'Inter_700Bold', color: colors.foreground },
    headerSub:   { fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 2 },

    langRow:     { flexDirection: rowDir, alignItems: 'center', marginTop: 12, gap: 10 },
    langLabel:   { fontSize: fs(13), fontFamily: 'Inter_500Medium', color: colors.mutedForeground },
    langBtn:     { flexDirection: rowDir, alignItems: 'center', gap: 6, backgroundColor: colors.card,
                   borderRadius: 20, borderWidth: 1, borderColor: colors.border,
                   paddingVertical: 7, paddingHorizontal: 14 },
    langBtnText: { fontSize: fs(14), fontFamily: 'Inter_600SemiBold', color: colors.foreground },

    scroll:      { flex: 1 },
    scrollBody:  { padding: 16, paddingBottom: Platform.OS === 'web' ? 80 : 120 },

    // Clip card
    card:        { backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1,
                   borderColor: colors.border, marginBottom: 16, overflow: 'hidden' },
    cardHead:    { flexDirection: rowDir, alignItems: 'center', gap: 10,
                   backgroundColor: colors.primary + '14', paddingHorizontal: 16, paddingVertical: 12,
                   borderBottomWidth: 1, borderBottomColor: colors.border },
    cardBadge:   { width: 28, height: 28, borderRadius: 14, backgroundColor: colors.primary,
                   alignItems: 'center', justifyContent: 'center' },
    cardBadgeTxt:{ fontSize: fs(13), fontFamily: 'Inter_700Bold', color: '#FFFFFF' },
    cardTitle:   { flex: 1, fontSize: fs(16), fontFamily: 'Inter_700Bold', color: colors.foreground },
    cardDesc:    { fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 1 },
    cardBody:    { padding: 16 },

    sectionLabel: { fontSize: fs(12), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground,
                    textTransform: 'uppercase', letterSpacing: 0.6, marginBottom: 6 },
    scriptInput:  { fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.foreground,
                    backgroundColor: colors.background, borderRadius: 8, borderWidth: 1,
                    borderColor: colors.border, padding: 12, minHeight: 90, textAlignVertical: 'top', ...textStyle },
    transBox:     { backgroundColor: colors.primary + '0F', borderRadius: 8, padding: 12,
                    marginTop: 10, borderWidth: 1, borderColor: colors.primary + '25' },
    transText:    { fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.foreground, lineHeight: 21, ...textStyle },
    transLabel:   { fontSize: fs(11), fontFamily: 'Inter_600SemiBold', color: colors.primary,
                    marginBottom: 4, textTransform: 'uppercase', letterSpacing: 0.5 },

    playBtn:      { flexDirection: rowDir, alignItems: 'center', justifyContent: 'center', gap: 8,
                    backgroundColor: colors.primary, borderRadius: colors.radius,
                    paddingVertical: 12, paddingHorizontal: 20, marginTop: 14 },
    playBtnText:  { fontSize: fs(14), fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' },
    playBtnSecondary: { backgroundColor: colors.accent ?? '#C9A050' },

    micRow:       { flexDirection: rowDir, gap: 10, marginBottom: 12 },
    micBtn:       { flexDirection: rowDir, alignItems: 'center', gap: 6, borderRadius: 20,
                    paddingVertical: 9, paddingHorizontal: 16, borderWidth: 1.5 },
    micActive:    { backgroundColor: '#E0525214', borderColor: '#E05252' },
    micIdle:      { backgroundColor: colors.muted, borderColor: colors.border },
    micText:      { fontSize: fs(13), fontFamily: 'Inter_600SemiBold' },

    officerInput: { fontSize: fs(15), fontFamily: 'Inter_400Regular', color: colors.foreground,
                    backgroundColor: colors.background, borderRadius: 8, borderWidth: 1,
                    borderColor: colors.border, padding: 12, minHeight: 80, textAlignVertical: 'top', ...textStyle },

    getAdviceBtn: { flexDirection: rowDir, alignItems: 'center', justifyContent: 'center', gap: 8,
                    backgroundColor: colors.foreground, borderRadius: colors.radius,
                    paddingVertical: 12, marginTop: 12 },
    getAdviceTxt: { fontSize: fs(14), fontFamily: 'Inter_600SemiBold', color: colors.background },

    adviceBox:    { backgroundColor: colors.background, borderRadius: 8, padding: 14,
                    marginTop: 12, borderWidth: 1, borderColor: colors.border },
    adviceCat:    { fontSize: fs(13), fontFamily: 'Inter_700Bold', color: colors.primary,
                    marginBottom: 10, textTransform: 'uppercase', letterSpacing: 0.5 },
    adviceLine:   { fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.foreground,
                    lineHeight: 22, marginBottom: 4, ...textStyle },

    capturedBox:  { flexDirection: rowDir, alignItems: 'flex-start', gap: 6,
                    backgroundColor: '#5A9E6F14', borderRadius: 8, padding: 10, marginBottom: 10,
                    borderWidth: 1, borderColor: '#5A9E6F40' },
    capturedTxt:  { flex: 1, fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.foreground },

    listeningBadge: { flexDirection: rowDir, alignItems: 'center', gap: 6,
                      backgroundColor: '#E0525214', borderRadius: 20, alignSelf: 'flex-start',
                      paddingHorizontal: 12, paddingVertical: 6, marginBottom: 10 },
    listeningDot:   { width: 8, height: 8, borderRadius: 4, backgroundColor: '#E05252' },
    listeningTxt:   { fontSize: fs(13), fontFamily: 'Inter_600SemiBold', color: '#E05252' },

    divider:      { height: 1, backgroundColor: colors.border, marginVertical: 12 },
  });

  const langCode = targetLang.code;

  return (
    <View style={S.container}>
      {/* ── Header ── */}
      <View style={S.header}>
        <Text style={S.headerTitle} accessibilityRole="header">🌐 Translate</Text>
        <Text style={S.headerSub}>{t('translate.subtitle')}</Text>

        {/* Language selector */}
        <View style={S.langRow}>
          <Text style={S.langLabel}>Your language:</Text>
          <Pressable style={S.langBtn} onPress={() => setShowPicker(true)} accessibilityRole="button">
            <Text style={S.langBtnText}>🌐 {targetLang.nativeName}</Text>
            <Feather name="chevron-down" size={15} color={colors.mutedForeground} />
          </Pressable>
        </View>
      </View>

      <ScrollView style={S.scroll} contentContainerStyle={S.scrollBody} keyboardShouldPersistTaps="handled">

        {/* ══ CLIP 1 — Play Before Interaction ══ */}
        <View style={S.card}>
          <View style={S.cardHead}>
            <View style={S.cardBadge}><Text style={S.cardBadgeTxt}>1</Text></View>
            <View style={{ flex: 1 }}>
              <Text style={S.cardTitle}>Play Before Interaction</Text>
              <Text style={S.cardDesc}>Play this to the officer before recording begins.</Text>
            </View>
          </View>
          <View style={S.cardBody}>
            <Text style={S.sectionLabel}>Officer-facing script (English):</Text>
            <TextInput
              style={S.scriptInput}
              value={script1}
              onChangeText={setScript1}
              multiline
              accessibilityLabel="Pre-encounter officer script"
            />

            {/* Translation of script 1 */}
            {langCode !== 'en' && (
              <View style={S.transBox}>
                <Text style={S.transLabel}>What this says in {targetLang.name}:</Text>
                {translating1
                  ? <ActivityIndicator size="small" color={colors.primary} />
                  : <Text style={S.transText}>{script1Trans || '—'}</Text>
                }
              </View>
            )}

            <Pressable style={S.playBtn} onPress={() => ttsSpeak(script1, 'en-US')} accessibilityRole="button">
              <Feather name="play-circle" size={18} color="#FFFFFF" />
              <Text style={S.playBtnText}>▶ Play to Officer (English)</Text>
            </Pressable>
          </View>
        </View>

        {/* ══ CLIP 2 — Play Advice ══ */}
        <View style={S.card}>
          <View style={S.cardHead}>
            <View style={[S.cardBadge, { backgroundColor: '#5A9E6F' }]}><Text style={S.cardBadgeTxt}>2</Text></View>
            <View style={{ flex: 1 }}>
              <Text style={S.cardTitle}>Play Advice</Text>
              <Text style={S.cardDesc}>Record or type what the officer says to get your rights.</Text>
            </View>
          </View>
          <View style={S.cardBody}>

            {/* Mic recorder section */}
            <View style={{ backgroundColor: colors.primary + '08', borderRadius: 10, padding: 12,
                           borderWidth: 1, borderColor: colors.primary + '20', marginBottom: 12 }}>
              <Text style={[S.sectionLabel, { marginBottom: 8 }]}>🎙 Microphone Recorder</Text>
              <Text style={{ fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginBottom: 10 }}>
                Use Start/Stop to capture what the officer says.
              </Text>

              {listening && (
                <View style={S.listeningBadge} accessibilityLiveRegion="polite">
                  <View style={S.listeningDot} />
                  <Text style={S.listeningTxt}>Listening… speak now</Text>
                </View>
              )}

              <View style={S.micRow}>
                <Pressable
                  style={[S.micBtn, listening ? S.micActive : S.micIdle]}
                  onPress={handleMic}
                  accessibilityRole="button"
                  accessibilityLabel={listening ? 'Stop recording' : 'Start recording'}
                >
                  <Feather name={listening ? 'square' : 'mic'} size={15}
                    color={listening ? '#E05252' : colors.mutedForeground} />
                  <Text style={[S.micText, { color: listening ? '#E05252' : colors.mutedForeground }]}>
                    {listening ? 'Stop' : 'Start Recording'}
                  </Text>
                </Pressable>
              </View>

              {officerText.length > 0 && (
                <View style={S.capturedBox}>
                  <Feather name="check-circle" size={14} color="#5A9E6F" style={{ marginTop: 2 }} />
                  <Text style={S.capturedTxt}>Speech captured and converted to text.</Text>
                </View>
              )}
            </View>

            {/* Text area */}
            <Text style={S.sectionLabel}>Enter text or record audio to translate:</Text>
            <TextInput
              style={S.officerInput}
              value={officerText}
              onChangeText={setOfficerText}
              multiline
              placeholder="Type or record what the officer said…"
              placeholderTextColor={colors.mutedForeground}
              accessibilityLabel="Officer statement input"
            />

            {/* Get Advice button */}
            <Pressable
              style={[S.getAdviceBtn, (!officerText.trim() || loadingAdvice) && { opacity: 0.45 }]}
              onPress={handleGetAdvice}
              disabled={!officerText.trim() || loadingAdvice}
              accessibilityRole="button"
            >
              {loadingAdvice
                ? <ActivityIndicator size="small" color={colors.background} />
                : <Feather name="shield" size={16} color={colors.background} />
              }
              <Text style={S.getAdviceTxt}>
                {loadingAdvice ? 'Getting advice…' : '🛡 Translate & Get Advice'}
              </Text>
            </Pressable>

            {/* Rights advice display */}
            {category && adviceText ? (
              <>
                <View style={S.divider} />
                <Text style={S.sectionLabel}>Your Rights &amp; Legal Advice:</Text>
                <View style={S.adviceBox}>
                  <Text style={S.adviceCat}>
                    {category.icon === 'navigation' ? '🚗' :
                     category.icon === 'shield'     ? '🛡' :
                     category.icon === 'alert-circle' ? '⚠️' :
                     category.icon === 'globe'      ? '🌍' :
                     category.icon === 'home'       ? '🏠' :
                     category.icon === 'search'     ? '🔍' : '📋'}
                    {'  '}{category.title.toUpperCase()} RIGHTS:
                  </Text>
                  {adviceText.split('\n').filter(Boolean).slice(1).map((line, i) => (
                    <Text key={i} style={S.adviceLine}>{line}</Text>
                  ))}
                </View>

                <Pressable
                  style={[S.playBtn, S.playBtnSecondary]}
                  onPress={() => ttsSpeak(advisorySpeech, langCode)}
                  accessibilityRole="button"
                >
                  <Feather name="play-circle" size={18} color="#FFFFFF" />
                  <Text style={S.playBtnText}>▶ Play Advice ({targetLang.name})</Text>
                </Pressable>
              </>
            ) : null}
          </View>
        </View>

        {/* ══ CLIP 3 — Play After Understanding Rights ══ */}
        <View style={S.card}>
          <View style={S.cardHead}>
            <View style={[S.cardBadge, { backgroundColor: '#C9A050' }]}><Text style={S.cardBadgeTxt}>3</Text></View>
            <View style={{ flex: 1 }}>
              <Text style={S.cardTitle}>Play After Understanding Rights</Text>
              <Text style={S.cardDesc}>Play this to the officer after you hear your rights.</Text>
            </View>
          </View>
          <View style={S.cardBody}>
            <Text style={S.sectionLabel}>Officer-facing script (English):</Text>
            <TextInput
              style={S.scriptInput}
              value={script3}
              onChangeText={setScript3}
              multiline
              accessibilityLabel="Post-rights officer script"
            />

            <Pressable style={S.playBtn} onPress={() => ttsSpeak(script3, 'en-US')} accessibilityRole="button">
              <Feather name="play-circle" size={18} color="#FFFFFF" />
              <Text style={S.playBtnText}>▶ Play to Officer (English)</Text>
            </Pressable>
          </View>
        </View>

      </ScrollView>

      <LanguagePicker
        visible={showPicker}
        selectedCode={langCode}
        onSelect={(l) => { setTargetLang(l); setShowPicker(false); }}
        onClose={() => setShowPicker(false)}
      />
    </View>
  );
}
