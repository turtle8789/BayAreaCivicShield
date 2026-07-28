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

export default function HomeScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const { language, setLanguage, encounters, savedDeadlines, removeDeadline, fs } = useApp();
  const [showLangPicker, setShowLangPicker] = useState(false);

  const topPad = Platform.OS === 'web' ? 67 : insets.top;

  const features = [
    {
      title: '📄 Document Analyzer',
      description: 'Scan or paste legal text to extract deadlines, dates & penalties. Save to dashboard.',
      iconName: 'file-text',
      accentColor: '#C9A050',
      route: '/(tabs)/docs',
    },
    {
      title: '🌐 Real-Time Translation',
      description: 'Translate text or voice recordings into 14 languages instantly.',
      iconName: 'globe',
      accentColor: '#C97B8E',
      route: '/(tabs)/translate',
    },
    {
      title: '📚 Know Your Rights',
      description: 'Civil rights for traffic stops, police encounters, arrests, immigration & more.',
      iconName: 'book-open',
      accentColor: '#A07888',
      route: '/(tabs)/rights',
    },
    {
      title: '📍 Find Legal Resources',
      description: 'Locate nearby legal aid, hotlines & support organizations sorted by distance.',
      iconName: 'map-pin',
      accentColor: '#C9A050',
      route: '/(tabs)/resources',
    },
    {
      title: '📞 Crisis Hotlines',
      description: '24/7 emergency, legal, immigration, domestic violence & LGBTQ+ lines.',
      iconName: 'phone-call',
      accentColor: '#E05252',
      route: '/(tabs)/resources',
    },
    {
      title: '🗂️ Encounter Log',
      description: 'Privately document police interactions — stored only on your device.',
      iconName: 'clipboard',
      accentColor: '#C97B8E',
      route: '/log-list',
    },
  ];

  const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: colors.background },
    header: {
      paddingTop: topPad + 8,
      paddingHorizontal: 20,
      paddingBottom: 12,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
      backgroundColor: colors.background,
    },
    headerRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
    logoRow: { flexDirection: 'row', alignItems: 'center', gap: 10 },
    logoImage: { width: 40, height: 40, borderRadius: 8 },
    appName: { fontSize: fs(22), fontFamily: 'Inter_700Bold', color: colors.primary, letterSpacing: -0.4 },
    tagline: { fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 1 },
    headerActions: { flexDirection: 'row', alignItems: 'center', gap: 8 },
    langBtn: {
      flexDirection: 'row', alignItems: 'center', backgroundColor: colors.muted,
      borderRadius: 20, paddingHorizontal: 11, paddingVertical: 6, gap: 5,
    },
    langBtnText: { fontSize: fs(12), fontFamily: 'Inter_500Medium', color: colors.foreground },
    iconBtn: {
      width: 34, height: 34, borderRadius: 17, backgroundColor: colors.muted,
      alignItems: 'center', justifyContent: 'center',
    },
    scroll: { flex: 1 },
    scrollContent: { padding: 16, paddingBottom: Platform.OS === 'web' ? 34 : 100 },

    // Deadline dashboard cards
    deadlineCard: {
      backgroundColor: '#C9A050' + '12',
      borderRadius: colors.radius,
      borderWidth: 1,
      borderColor: '#C9A050' + '40',
      padding: 12,
      marginBottom: 8,
      flexDirection: 'row',
      alignItems: 'flex-start',
      gap: 10,
    },
    deadlineText: { flex: 1, fontSize: fs(13), fontFamily: 'Inter_500Medium', color: colors.foreground, lineHeight: 18 },
    deadlineSource: { fontSize: fs(11), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 2 },
    deadlineDismiss: { padding: 2 },
    deadlineSectionHeader: {
      flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8,
    },
    deadlineSectionTitle: {
      fontSize: fs(12), fontFamily: 'Inter_600SemiBold', color: '#C9A050',
      textTransform: 'uppercase', letterSpacing: 0.8,
    },
    clearAllBtn: { flexDirection: 'row', alignItems: 'center', gap: 4 },
    clearAllText: { fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground },

    // Emergency banner
    emergencyBanner: {
      backgroundColor: '#E05252', borderRadius: colors.radius, flexDirection: 'row',
      alignItems: 'center', padding: 14, marginBottom: 14, gap: 10,
    },
    emergencyText: { flex: 1, fontSize: fs(14), fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' },
    emergencyNumber: { fontSize: fs(20), fontFamily: 'Inter_700Bold', color: '#FFFFFF' },

    // Encounter log shortcut
    logBanner: {
      backgroundColor: colors.primary + '12', borderRadius: colors.radius, borderWidth: 1,
      borderColor: colors.primary + '30', flexDirection: 'row', alignItems: 'center',
      padding: 14, marginBottom: 14, gap: 10,
    },
    logBannerTitle: { fontSize: fs(14), fontFamily: 'Inter_600SemiBold', color: colors.primary },
    logBannerSub: { fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 1 },

    // Tour button
    tourBtn: {
      flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: colors.secondary + '18',
      borderRadius: colors.radius, borderWidth: 1, borderColor: colors.secondary + '40',
      padding: 12, marginBottom: 14,
    },
    tourBtnText: { flex: 1, fontSize: fs(13), fontFamily: 'Inter_500Medium', color: colors.secondary ?? '#C9A050' },

    sectionTitle: {
      fontSize: fs(12), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground,
      textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 12,
    },
  });

  const { clearDeadlines } = useApp();

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerRow}>
          <View style={styles.logoRow}>
            <Image source={require('@/assets/images/icon.png')} style={styles.logoImage} resizeMode="contain" accessibilityLabel="CivicShield Pro logo" />
            <View>
              <Text style={styles.appName} accessibilityRole="header">CivicShield Pro</Text>
              <Text style={styles.tagline}>Know your rights. Stay protected.</Text>
            </View>
          </View>
          <View style={styles.headerActions}>
            <Pressable style={styles.langBtn} onPress={() => setShowLangPicker(true)} accessibilityLabel={`Language: ${language.nativeName}`} accessibilityRole="button">
              <Feather name="globe" size={13} color={colors.primary} />
              <Text style={styles.langBtnText}>{language.nativeName}</Text>
              <Feather name="chevron-down" size={11} color={colors.mutedForeground} />
            </Pressable>
            <Pressable style={styles.iconBtn} onPress={() => router.push('/settings')} accessibilityLabel="Settings" accessibilityRole="button">
              <Feather name="settings" size={16} color={colors.mutedForeground} />
            </Pressable>
          </View>
        </View>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>

        {/* ── Saved Deadlines Dashboard ── */}
        {savedDeadlines.length > 0 && (
          <View style={{ marginBottom: 14 }}>
            <View style={styles.deadlineSectionHeader}>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
                <Feather name="bookmark" size={14} color="#C9A050" />
                <Text style={styles.deadlineSectionTitle} accessibilityRole="header">
                  Saved Deadlines ({savedDeadlines.length})
                </Text>
              </View>
              <Pressable
                style={styles.clearAllBtn}
                onPress={() => { clearDeadlines(); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); }}
                accessibilityLabel="Clear all saved deadlines"
                accessibilityRole="button"
              >
                <Feather name="trash-2" size={12} color={colors.mutedForeground} />
                <Text style={styles.clearAllText}>Clear all</Text>
              </Pressable>
            </View>
            {savedDeadlines.map((d) => (
              <View key={d.id} style={styles.deadlineCard} accessibilityLabel={`Saved deadline: ${d.text}`}>
                <Feather name="alert-circle" size={16} color="#C9A050" style={{ marginTop: 1 }} />
                <View style={{ flex: 1 }}>
                  <Text style={styles.deadlineText}>{d.text}</Text>
                  <Text style={styles.deadlineSource}>
                    {d.source} · {new Date(d.savedAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  </Text>
                </View>
                <Pressable
                  style={styles.deadlineDismiss}
                  onPress={() => { removeDeadline(d.id); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); }}
                  accessibilityLabel="Dismiss this deadline"
                  accessibilityRole="button"
                  hitSlop={8}
                >
                  <Feather name="x" size={15} color={colors.mutedForeground} />
                </Pressable>
              </View>
            ))}
          </View>
        )}

        {/* ── Emergency banner ── */}
        <Pressable style={styles.emergencyBanner} onPress={() => router.push('/(tabs)/resources')} accessibilityLabel="Emergency services — call 911" accessibilityRole="button">
          <Feather name="alert-triangle" size={20} color="#FFFFFF" />
          <Text style={styles.emergencyText}>In an emergency or crisis?</Text>
          <Text style={styles.emergencyNumber}>911</Text>
        </Pressable>

        {/* ── Tour button (shows if not yet completed) ── */}
        <Pressable
          style={styles.tourBtn}
          onPress={() => router.push('/tour')}
          accessibilityLabel="Start guided tour"
          accessibilityRole="button"
        >
          <Feather name="compass" size={18} color="#C9A050" />
          <Text style={styles.tourBtnText}>🎓 Guided Tour — learn how to use CivicShield Pro</Text>
          <Feather name="chevron-right" size={16} color="#C9A050" />
        </Pressable>

        {/* ── Encounter log shortcut ── */}
        <Pressable style={styles.logBanner} onPress={() => router.push('/log-list')} accessibilityLabel={`Encounter log — ${encounters.length} entries`} accessibilityRole="button">
          <Feather name="clipboard" size={20} color={colors.primary} />
          <View style={{ flex: 1 }}>
            <Text style={styles.logBannerTitle}>🗂️ Encounter Log</Text>
            <Text style={styles.logBannerSub}>
              {encounters.length === 0 ? 'No encounters logged yet — tap to add one' : `${encounters.length} encounter${encounters.length === 1 ? '' : 's'} logged`}
            </Text>
          </View>
          <Feather name="chevron-right" size={16} color={colors.mutedForeground} />
        </Pressable>

        <Text style={styles.sectionTitle} accessibilityRole="header">Tools & Resources</Text>

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
