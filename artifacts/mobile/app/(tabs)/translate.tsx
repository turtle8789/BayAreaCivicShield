import React, { useState } from 'react';
import {
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
import { useColors } from '@/hooks/useColors';

const CHAR_LIMIT = 450;

async function translateText(text: string, sourceLang: string, targetLang: string): Promise<string> {
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
  const topPad = Platform.OS === 'web' ? 67 : insets.top;

  const [sourceText, setSourceText] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [sourceLang, setSourceLang] = useState<Language | 'auto'>('auto');
  const [targetLang, setTargetLang] = useState<Language>(LANGUAGES[1]); // Spanish default
  const [loading, setLoading] = useState(false);
  const [showSourcePicker, setShowSourcePicker] = useState(false);
  const [showTargetPicker, setShowTargetPicker] = useState(false);

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

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: colors.background,
    },
    header: {
      paddingTop: topPad + 12,
      paddingHorizontal: 20,
      paddingBottom: 16,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    headerTitle: {
      fontSize: 22,
      fontFamily: 'Inter_700Bold',
      color: colors.foreground,
    },
    headerSub: {
      fontSize: 13,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
      marginTop: 2,
    },
    scroll: {
      flex: 1,
    },
    scrollContent: {
      padding: 16,
      paddingBottom: Platform.OS === 'web' ? 34 : 24,
    },
    langBar: {
      flexDirection: 'row',
      alignItems: 'center',
      marginBottom: 12,
      gap: 8,
    },
    langBtn: {
      flex: 1,
      backgroundColor: colors.card,
      borderRadius: 12,
      borderWidth: 1,
      borderColor: colors.border,
      paddingVertical: 10,
      paddingHorizontal: 14,
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
    },
    langBtnText: {
      fontSize: 14,
      fontFamily: 'Inter_500Medium',
      color: colors.foreground,
    },
    swapBtn: {
      width: 36,
      height: 36,
      borderRadius: 18,
      backgroundColor: colors.muted,
      alignItems: 'center',
      justifyContent: 'center',
    },
    card: {
      backgroundColor: colors.card,
      borderRadius: colors.radius,
      borderWidth: 1,
      borderColor: colors.border,
      marginBottom: 12,
      overflow: 'hidden',
    },
    cardHeader: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingHorizontal: 14,
      paddingTop: 12,
      marginBottom: 4,
      gap: 6,
    },
    cardLabel: {
      flex: 1,
      fontSize: 12,
      fontFamily: 'Inter_600SemiBold',
      color: colors.mutedForeground,
      textTransform: 'uppercase',
      letterSpacing: 0.6,
    },
    charCount: {
      fontSize: 12,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
    },
    charCountWarn: {
      color: colors.destructive,
    },
    textInput: {
      fontSize: 16,
      fontFamily: 'Inter_400Regular',
      color: colors.foreground,
      paddingHorizontal: 14,
      paddingBottom: 14,
      minHeight: 120,
      textAlignVertical: 'top',
    },
    clearBtn: {
      padding: 4,
    },
    translatedText: {
      fontSize: 16,
      fontFamily: 'Inter_400Regular',
      color: colors.foreground,
      paddingHorizontal: 14,
      paddingBottom: 14,
      minHeight: 80,
    },
    translatingWrap: {
      padding: 14,
      alignItems: 'center',
      flexDirection: 'row',
      gap: 8,
    },
    translatingText: {
      fontSize: 14,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
    },
    placeholderText: {
      fontSize: 15,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
      padding: 14,
    },
    translateBtn: {
      backgroundColor: colors.primary,
      borderRadius: colors.radius,
      paddingVertical: 15,
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: 'row',
      gap: 8,
    },
    translateBtnDisabled: {
      opacity: 0.5,
    },
    translateBtnText: {
      fontSize: 16,
      fontFamily: 'Inter_600SemiBold',
      color: colors.primaryForeground,
    },
    tipCard: {
      backgroundColor: colors.primary + '0F',
      borderRadius: colors.radius,
      padding: 14,
      borderWidth: 1,
      borderColor: colors.primary + '20',
    },
    tipText: {
      fontSize: 13,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
      lineHeight: 19,
    },
  });

  const isOverLimit = sourceText.length >= CHAR_LIMIT;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Translate</Text>
        <Text style={styles.headerSub}>Translate to 14 languages</Text>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent} keyboardShouldPersistTaps="handled">
        {/* Language pair */}
        <View style={styles.langBar}>
          <Pressable style={styles.langBtn} onPress={() => setShowSourcePicker(true)}>
            <Text style={styles.langBtnText}>{sourceName}</Text>
            <Feather name="chevron-down" size={16} color={colors.mutedForeground} />
          </Pressable>

          <Pressable
            style={[styles.swapBtn, sourceLang === 'auto' && { opacity: 0.4 }]}
            onPress={handleSwap}
            disabled={sourceLang === 'auto'}
          >
            <Feather name="repeat" size={16} color={colors.foreground} />
          </Pressable>

          <Pressable style={styles.langBtn} onPress={() => setShowTargetPicker(true)}>
            <Text style={styles.langBtnText}>{targetLang.nativeName}</Text>
            <Feather name="chevron-down" size={16} color={colors.mutedForeground} />
          </Pressable>
        </View>

        {/* Source text */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardLabel}>Original</Text>
            <Text style={[styles.charCount, isOverLimit && styles.charCountWarn]}>
              {sourceText.length}/{CHAR_LIMIT}
            </Text>
            {sourceText.length > 0 && (
              <Pressable style={styles.clearBtn} onPress={handleClear}>
                <Feather name="x" size={16} color={colors.mutedForeground} />
              </Pressable>
            )}
          </View>
          <TextInput
            style={styles.textInput}
            value={sourceText}
            onChangeText={(t) => setSourceText(t.slice(0, CHAR_LIMIT))}
            multiline
            placeholder="Enter text to translate..."
            placeholderTextColor={colors.mutedForeground}
          />
        </View>

        {/* Translated text */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardLabel}>{targetLang.name}</Text>
          </View>
          {loading ? (
            <View style={styles.translatingWrap}>
              <ActivityIndicator size="small" color={colors.primary} />
              <Text style={styles.translatingText}>Translating...</Text>
            </View>
          ) : translatedText ? (
            <Text style={styles.translatedText} selectable>{translatedText}</Text>
          ) : (
            <Text style={styles.placeholderText}>Translation will appear here</Text>
          )}
        </View>

        {/* Translate button */}
        <Pressable
          style={[styles.translateBtn, (!sourceText.trim() || loading) && styles.translateBtnDisabled]}
          onPress={handleTranslate}
          disabled={!sourceText.trim() || loading}
        >
          <Feather name="globe" size={18} color={colors.primaryForeground} />
          <Text style={styles.translateBtnText}>Translate</Text>
        </Pressable>

        <View style={{ height: 16 }} />

        {/* Tip */}
        <View style={styles.tipCard}>
          <Text style={styles.tipText}>
            Tip: During an encounter, you can show this screen to an officer or use it to understand what is being said. Always stay calm and keep your hands visible.
          </Text>
        </View>
      </ScrollView>

      {/* Source language picker — includes "Auto-detect" option */}
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
