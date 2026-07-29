import React, { useState } from 'react';
import {
  Image,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { router } from 'expo-router';
import { Feather } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { FeatureCard } from '@/components/FeatureCard';
import { LanguagePicker } from '@/components/LanguagePicker';
import { useApp } from '@/context/AppContext';
import { useColors } from '@/hooks/useColors';
import { useT } from '@/hooks/useTranslation';

export default function HomeScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const {
    language, setLanguage,
    encounters,
    savedDeadlines, removeDeadline, clearDeadlines,
    setPendingDocText,
    forumPosts,
    fs,
  } = useApp();
  const { t } = useT();
  const [showLangPicker, setShowLangPicker] = useState(false);

  const topPad    = Platform.OS === 'web' ? 67 : insets.top;
  const bottomPad = Platform.OS === 'web' ? 80 : insets.bottom + 80;

  // ── Feature cards — every capability in the app ───────────────────────────
  const features = [
    {
      title: t('home.feature_docs'),
      description: 'Scan or paste legal text. Extract deadlines, dates & penalties. Save to dashboard.',
      iconName: 'file-text',
      accentColor: '#C9A050',
      route: '/(tabs)/docs',
    },
    {
      title: t('home.feature_translate'),
      description: 'Translate text or voice into 28 languages. Tap 🎤 to speak — iOS, Android & web.',
      iconName: 'globe',
      accentColor: '#C97B8E',
      route: '/(tabs)/translate',
    },
    {
      title: t('home.feature_rights'),
      description: 'Civil rights for traffic stops, arrests, immigration, home searches & more.',
      iconName: 'book-open',
      accentColor: '#A07888',
      route: '/(tabs)/rights',
    },
    {
      title: t('home.feature_resources'),
      description: 'Legal aid, hotlines & support organizations sorted by distance from you.',
      iconName: 'map-pin',
      accentColor: '#C9A050',
      route: '/(tabs)/resources',
    },
    {
      title: t('home.feature_hotlines'),
      description: '24/7 emergency, legal, immigration, domestic violence & LGBTQ+ lines.',
      iconName: 'phone-call',
      accentColor: '#E05252',
      route: '/(tabs)/resources',
    },
    {
      title: t('home.feature_forum'),
      description: `${forumPosts.length > 0 ? `${forumPosts.length} posts by you + ` : ''}7 community discussions — share experiences, ask questions, get advice.`,
      iconName: 'message-circle',
      accentColor: '#9B7EC9',
      route: '/forum',
    },
    {
      title: t('home.feature_hub'),
      description: '25+ curated free legal aid links, civil rights orgs, housing, immigration & employment.',
      iconName: 'book',
      accentColor: '#5A9E6F',
      route: '/resource-hub',
    },
    {
      title: t('home.feature_log'),
      description: encounters.length === 0
        ? 'Privately document police interactions — stored only on your device.'
        : `${encounters.length} encounter${encounters.length === 1 ? '' : 's'} logged — tap to view or add.`,
      iconName: 'clipboard',
      accentColor: '#C97B8E',
      route: '/log-list',
    },
  ];

  const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: colors.background },
    header: {
      paddingTop: topPad + 8, paddingHorizontal: 20, paddingBottom: 12,
      borderBottomWidth: 1, borderBottomColor: colors.border,
      backgroundColor: colors.background,
    },
    headerRow:    { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
    logoRow:      { flexDirection: 'row', alignItems: 'center', gap: 10 },
    logoImage:    { width: 40, height: 40, borderRadius: 8 },
    appName:      { fontSize: fs(22), fontFamily: 'Inter_700Bold', color: colors.primary, letterSpacing: -0.4 },
    tagline:      { fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 1 },
    headerActions:{ flexDirection: 'row', alignItems: 'center', gap: 8 },
    langBtn:      { flexDirection: 'row', alignItems: 'center', backgroundColor: colors.muted, borderRadius: 20, paddingHorizontal: 11, paddingVertical: 6, gap: 5 },
    langBtnText:  { fontSize: fs(12), fontFamily: 'Inter_500Medium', color: colors.foreground },
    iconBtn:      { width: 34, height: 34, borderRadius: 17, backgroundColor: colors.muted, alignItems: 'center', justifyContent: 'center' },
    // Settings row below the logo — more prominent
    settingsRow:  { flexDirection: 'row', gap: 8, marginTop: 10 },
    settingsChip: { flexDirection: 'row', alignItems: 'center', gap: 5, backgroundColor: colors.muted, borderRadius: 20, paddingHorizontal: 11, paddingVertical: 6 },
    settingsChipText: { fontSize: fs(12), fontFamily: 'Inter_500Medium', color: colors.mutedForeground },

    scroll:        { flex: 1 },
    scrollContent: { padding: 16, paddingBottom: bottomPad, flexGrow: 1 },

    // Deadlines
    deadlineSectionHeader: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 },
    deadlineSectionTitle:  { fontSize: fs(12), fontFamily: 'Inter_600SemiBold', color: '#C9A050', textTransform: 'uppercase', letterSpacing: 0.8 },
    clearAllBtn:  { flexDirection: 'row', alignItems: 'center', gap: 4 },
    clearAllText: { fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground },
    deadlineCard: { backgroundColor: '#C9A050' + '12', borderRadius: colors.radius, borderWidth: 1, borderColor: '#C9A050' + '40', padding: 12, marginBottom: 8 },
    deadlineText: { fontSize: fs(13), fontFamily: 'Inter_500Medium', color: colors.foreground, lineHeight: 18 },
    deadlineSource:{ fontSize: fs(11), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 2 },

    // Emergency
    emergencyBanner: { backgroundColor: '#E05252', borderRadius: colors.radius, flexDirection: 'row', alignItems: 'center', padding: 14, marginBottom: 14, gap: 10 },
    emergencyText:   { flex: 1, fontSize: fs(14), fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' },
    emergencyNumber: { fontSize: fs(20), fontFamily: 'Inter_700Bold', color: '#FFFFFF' },

    // Tour
    tourBtn:     { flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: '#C9A050' + '18', borderRadius: colors.radius, borderWidth: 1, borderColor: '#C9A050' + '40', padding: 12, marginBottom: 14 },
    tourBtnText: { flex: 1, fontSize: fs(13), fontFamily: 'Inter_500Medium', color: '#C9A050' },

    sectionTitle: { fontSize: fs(12), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 12 },

    // Legal disclaimer
    disclaimer:    { backgroundColor: colors.muted, borderRadius: colors.radius, padding: 14, marginTop: 8 },
    disclaimerText:{ fontSize: fs(11), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 17 },
  });

  return (
    <View style={styles.container}>
      {/* ── Header ── */}
      <View style={styles.header}>
        <View style={styles.headerRow}>
          <View style={styles.logoRow}>
            <Image
              source={require('@/assets/images/icon.png')}
              style={styles.logoImage}
              resizeMode="contain"
              accessibilityLabel="CivicShield Pro logo"
            />
            <View>
              <Text style={styles.appName} accessibilityRole="header">CivicShield Pro</Text>
              <Text style={styles.tagline}>{t('home.tagline')}</Text>
            </View>
          </View>
          <Pressable
            style={styles.langBtn}
            onPress={() => setShowLangPicker(true)}
            accessibilityLabel={`Language: ${language.nativeName}`}
            accessibilityRole="button"
          >
            <Feather name="globe" size={13} color={colors.primary} />
            <Text style={styles.langBtnText}>{language.nativeName}</Text>
            <Feather name="chevron-down" size={11} color={colors.mutedForeground} />
          </Pressable>
        </View>

        {/* Quick-access row — Settings + Accessibility prominent */}
        <View style={styles.settingsRow}>
          <Pressable
            style={styles.settingsChip}
            onPress={() => router.push('/settings')}
            accessibilityLabel="Settings"
            accessibilityRole="button"
          >
            <Feather name="settings" size={13} color={colors.mutedForeground} />
            <Text style={styles.settingsChipText}>{t('common.settings')}</Text>
          </Pressable>
          <Pressable
            style={styles.settingsChip}
            onPress={() => router.push('/settings')}
            accessibilityLabel="Accessibility settings"
            accessibilityRole="button"
          >
            <Feather name="eye" size={13} color={colors.mutedForeground} />
            <Text style={styles.settingsChipText}>{t('common.accessibility')}</Text>
          </Pressable>
          <Pressable
            style={styles.settingsChip}
            onPress={() => router.push('/tour')}
            accessibilityLabel="Guided tour"
            accessibilityRole="button"
          >
            <Feather name="compass" size={13} color="#C9A050" />
            <Text style={[styles.settingsChipText, { color: '#C9A050' }]}>{t('common.tour')}</Text>
          </Pressable>
        </View>
      </View>

      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        alwaysBounceVertical
      >
        {/* ── Important Dates Dashboard ── */}
        {savedDeadlines.length > 0 && (
          <View style={{ marginBottom: 14 }}>
            <View style={styles.deadlineSectionHeader}>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
                <Feather name="calendar" size={14} color="#C9A050" />
                <Text style={styles.deadlineSectionTitle} accessibilityRole="header">
                  {t('home.saved_deadlines')} ({savedDeadlines.length})
                </Text>
              </View>
              <Pressable
                style={styles.clearAllBtn}
                onPress={() => { clearDeadlines(); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); }}
                accessibilityLabel="Clear all important dates"
                accessibilityRole="button"
              >
                <Feather name="trash-2" size={12} color={colors.mutedForeground} />
                <Text style={styles.clearAllText}>{t('home.clear_all')}</Text>
              </Pressable>
            </View>
            {savedDeadlines.map((d) => (
              <View key={d.id} style={styles.deadlineCard}>
                {/* Header row: ⚠️ label + dismiss button */}
                <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                  <View style={{ flexDirection: 'row', alignItems: 'center', gap: 5 }}>
                    <Text style={{ fontSize: fs(11), fontFamily: 'Inter_700Bold', color: '#C9A050', letterSpacing: 0.6 }}>
                      ⚠️ IMPORTANT DATE
                    </Text>
                  </View>
                  <Pressable
                    onPress={() => { removeDeadline(d.id); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); }}
                    accessibilityLabel="Dismiss"
                    accessibilityRole="button"
                    hitSlop={10}
                  >
                    <Feather name="x" size={15} color={colors.mutedForeground} />
                  </Pressable>
                </View>

                {/* Deadline text */}
                <Text style={styles.deadlineText}>{d.text}</Text>

                {/* Footer row: source · date  +  View Case Details → */}
                <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginTop: 8 }}>
                  <Text style={styles.deadlineSource}>
                    {d.source} · {new Date(d.savedAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  </Text>
                  {d.docText ? (
                    <Pressable
                      onPress={() => {
                        setPendingDocText(d.docText!);
                        router.push('/(tabs)/docs');
                        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                      }}
                      style={{ flexDirection: 'row', alignItems: 'center', gap: 3 }}
                      accessibilityRole="button"
                      accessibilityLabel="View case details"
                    >
                      <Text style={{ fontSize: fs(11), fontFamily: 'Inter_600SemiBold', color: colors.primary }}>
                        {t('home.view_case')}
                      </Text>
                      <Feather name="chevron-right" size={12} color={colors.primary} />
                    </Pressable>
                  ) : null}
                </View>
              </View>
            ))}
          </View>
        )}

        {/* ── Emergency banner ── */}
        <Pressable
          style={styles.emergencyBanner}
          onPress={() => router.push('/(tabs)/resources')}
          accessibilityLabel="Emergency — call 911"
          accessibilityRole="button"
        >
          <Feather name="alert-triangle" size={20} color="#FFFFFF" />
          <Text style={styles.emergencyText}>{t('home.emergency')}</Text>
          <Text style={styles.emergencyNumber}>911</Text>
        </Pressable>

        {/* ── Tools & Resources — all features ── */}
        <Text style={styles.sectionTitle} accessibilityRole="header">{t('home.tools_section')}</Text>

        {features.map((f) => (
          <FeatureCard
            key={f.title}
            title={f.title}
            description={f.description}
            iconName={f.iconName}
            accentColor={f.accentColor}
            onPress={() => router.push(f.route as never)}
          />
        ))}

        {/* ── Legal disclaimer ── */}
        <View style={styles.disclaimer} accessibilityLabel="Legal disclaimer">
          <Text style={styles.disclaimerText}>{t('home.disclaimer')}</Text>
        </View>
      </ScrollView>

      <LanguagePicker
        visible={showLangPicker}
        selectedCode={language.code}
        onSelect={setLanguage}
        onClose={() => setShowLangPicker(false)}
      />
    </View>
  );
}
