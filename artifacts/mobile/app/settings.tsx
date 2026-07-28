import React, { useState } from 'react';
import {
  Alert,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  View,
} from 'react-native';
import { router } from 'expo-router';
import { Feather } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { LanguagePicker } from '@/components/LanguagePicker';
import { FontSizeLevel, useApp } from '@/context/AppContext';
import { useColors } from '@/hooks/useColors';

const FONT_SIZES: { label: string; value: FontSizeLevel; preview: number }[] = [
  { label: 'Small', value: 'small', preview: 12 },
  { label: 'Medium', value: 'medium', preview: 14 },
  { label: 'Large', value: 'large', preview: 18 },
];

function SettingsRow({
  icon,
  label,
  description,
  right,
  onPress,
}: {
  icon: string;
  label: string;
  description?: string;
  right?: React.ReactNode;
  onPress?: () => void;
}) {
  const colors = useColors();
  const { fs } = useApp();
  return (
    <Pressable
      style={{ flexDirection: 'row', alignItems: 'center', paddingVertical: 14, paddingHorizontal: 16, gap: 14 }}
      onPress={onPress}
      accessibilityRole={onPress ? 'button' : 'none'}
      accessibilityLabel={label}
      accessibilityHint={description}
    >
      <View style={{ width: 36, height: 36, borderRadius: 10, backgroundColor: colors.primary + '18', alignItems: 'center', justifyContent: 'center' }}>
        <Feather name={icon as never} size={18} color={colors.primary} />
      </View>
      <View style={{ flex: 1 }}>
        <Text style={{ fontSize: fs(15), fontFamily: 'Inter_500Medium', color: colors.foreground }}>{label}</Text>
        {description && (
          <Text style={{ fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 1 }}>
            {description}
          </Text>
        )}
      </View>
      {right ?? (onPress ? <Feather name="chevron-right" size={16} color={colors.mutedForeground} /> : null)}
    </Pressable>
  );
}

export default function SettingsScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;

  const {
    language, setLanguage,
    fontSize, setFontSize, fs,
    highContrast, setHighContrast,
    encounters, clearDeadlines, savedDeadlines,
  } = useApp();

  const [showLangPicker, setShowLangPicker] = useState(false);

  const handleHighContrast = (v: boolean) => {
    setHighContrast(v);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
  };

  const handleClearData = () => {
    Alert.alert(
      'Clear All Data',
      `This will permanently delete ${encounters.length} encounter log${encounters.length === 1 ? '' : 's'} and ${savedDeadlines.length} saved deadline${savedDeadlines.length === 1 ? '' : 's'}. This cannot be undone.`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete All',
          style: 'destructive',
          onPress: () => {
            clearDeadlines();
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
            Alert.alert('Cleared', 'All saved deadlines have been deleted.');
          },
        },
      ],
    );
  };

  const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: colors.background },
    header: {
      paddingTop: topPad + 12, paddingHorizontal: 20, paddingBottom: 16,
      borderBottomWidth: 1, borderBottomColor: colors.border,
      flexDirection: 'row', alignItems: 'center', gap: 12,
    },
    headerTitle: { flex: 1, fontSize: fs(20), fontFamily: 'Inter_700Bold', color: colors.foreground },
    scroll: { flex: 1 },
    scrollContent: { paddingBottom: Platform.OS === 'web' ? 34 : 60, flexGrow: 1 },
    sectionLabel: {
      fontSize: fs(11), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground,
      textTransform: 'uppercase', letterSpacing: 0.8,
      paddingHorizontal: 16, paddingTop: 20, paddingBottom: 6,
    },
    card: {
      backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1,
      borderColor: colors.border, marginHorizontal: 16, overflow: 'hidden',
    },
    divider: { height: 1, backgroundColor: colors.border, marginLeft: 66 },
    fontRow: { flexDirection: 'row', gap: 8, paddingHorizontal: 16, paddingVertical: 14 },
    fontChip: {
      flex: 1, alignItems: 'center', paddingVertical: 10, borderRadius: 10,
      borderWidth: 1.5, borderColor: colors.border, backgroundColor: colors.muted, gap: 4,
    },
    fontChipActive: { borderColor: colors.primary, backgroundColor: colors.primary + '14' },
    fontChipLabel: { fontSize: fs(12), fontFamily: 'Inter_500Medium', color: colors.mutedForeground },
    fontChipLabelActive: { color: colors.primary, fontFamily: 'Inter_600SemiBold' },
    fontPreview: { fontFamily: 'Inter_400Regular', color: colors.mutedForeground },
    fontPreviewActive: { color: colors.primary },
    hcPreview: {
      marginHorizontal: 16, marginBottom: 8, borderRadius: colors.radius, overflow: 'hidden',
      borderWidth: 1, borderColor: colors.border,
    },
    hcRow: { flexDirection: 'row' },
    hcSwatch: { flex: 1, height: 28 },
    versionText: {
      fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground,
      textAlign: 'center', paddingVertical: 20,
    },
    disclaimer: {
      backgroundColor: colors.muted, borderRadius: colors.radius, padding: 14,
      marginHorizontal: 16, marginTop: 16,
    },
    disclaimerText: {
      fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 18,
    },
  });

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} hitSlop={12} accessibilityLabel="Close settings" accessibilityRole="button">
          <Feather name="x" size={22} color={colors.foreground} />
        </Pressable>
        <Text style={styles.headerTitle} accessibilityRole="header">Settings</Text>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent}>

        {/* ── Language ── */}
        <Text style={styles.sectionLabel} accessibilityRole="header">Language</Text>
        <View style={styles.card}>
          <SettingsRow
            icon="globe"
            label="App Language"
            description={`${language.nativeName} — ${language.name}`}
            onPress={() => setShowLangPicker(true)}
          />
        </View>

        {/* ── Accessibility ── */}
        <Text style={styles.sectionLabel} accessibilityRole="header">Accessibility</Text>
        <View style={styles.card}>
          {/* Font size chips */}
          <View style={{ paddingHorizontal: 16, paddingTop: 14, paddingBottom: 4 }}>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: 14, marginBottom: 12 }}>
              <View style={{ width: 36, height: 36, borderRadius: 10, backgroundColor: colors.primary + '18', alignItems: 'center', justifyContent: 'center' }}>
                <Feather name="type" size={18} color={colors.primary} />
              </View>
              <View>
                <Text style={{ fontSize: fs(15), fontFamily: 'Inter_500Medium', color: colors.foreground }}>Font Size</Text>
                <Text style={{ fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground }}>
                  Changes text size throughout the app
                </Text>
              </View>
            </View>
            <View style={styles.fontRow}>
              {FONT_SIZES.map((f) => (
                <Pressable
                  key={f.value}
                  style={[styles.fontChip, fontSize === f.value && styles.fontChipActive]}
                  onPress={() => { setFontSize(f.value); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); }}
                  accessibilityLabel={`Font size ${f.label}`}
                  accessibilityRole="radio"
                  accessibilityState={{ selected: fontSize === f.value }}
                >
                  <Text style={[{ fontSize: f.preview }, styles.fontPreview, fontSize === f.value && styles.fontPreviewActive]}>Aa</Text>
                  <Text style={[styles.fontChipLabel, fontSize === f.value && styles.fontChipLabelActive]}>{f.label}</Text>
                </Pressable>
              ))}
            </View>
          </View>

          <View style={styles.divider} />

          {/* High contrast toggle */}
          <SettingsRow
            icon="sun"
            label="High Contrast Mode"
            description={highContrast ? 'On — dark background, white text' : 'Off — increases readability'}
            right={
              <Switch
                value={highContrast}
                onValueChange={handleHighContrast}
                trackColor={{ false: colors.muted, true: colors.primary + '80' }}
                thumbColor={highContrast ? colors.primary : '#F4F4F4'}
                accessibilityLabel="High contrast mode"
              />
            }
          />

          {/* Live high-contrast preview swatch */}
          {highContrast && (
            <View style={styles.hcPreview} accessibilityLabel="High contrast preview">
              <View style={styles.hcRow}>
                <View style={[styles.hcSwatch, { backgroundColor: '#000000' }]} />
                <View style={[styles.hcSwatch, { backgroundColor: '#FFFFFF' }]} />
                <View style={[styles.hcSwatch, { backgroundColor: colors.primary }]} />
                <View style={[styles.hcSwatch, { backgroundColor: '#C9A050' }]} />
              </View>
            </View>
          )}

          <View style={styles.divider} />

          {/* Screen reader note */}
          <SettingsRow
            icon="volume-2"
            label="Screen Reader Support"
            description="Accessibility labels are enabled throughout the app — compatible with VoiceOver (iOS) and TalkBack (Android)"
          />
        </View>

        {/* ── Guided Tour & QR ── */}
        <Text style={styles.sectionLabel} accessibilityRole="header">Tour & Help</Text>
        <View style={styles.card}>
          <SettingsRow
            icon="compass"
            label="Guided Tour"
            description="Step-by-step walkthrough of every feature"
            onPress={() => { router.back(); setTimeout(() => router.push('/tour'), 300); }}
          />
          <View style={styles.divider} />
          <SettingsRow
            icon="grid"
            label="Expo Go QR Code"
            description="Scan to preview this app on your phone"
            onPress={() => { router.back(); setTimeout(() => router.push('/qrcode-screen'), 300); }}
          />
        </View>

        {/* ── Data ── */}
        <Text style={styles.sectionLabel} accessibilityRole="header">Data & Privacy</Text>
        <View style={styles.card}>
          <SettingsRow
            icon="database"
            label="Saved Deadlines"
            description={`${savedDeadlines.length} deadline${savedDeadlines.length === 1 ? '' : 's'} pinned to Home`}
          />
          <View style={styles.divider} />
          <SettingsRow
            icon="clipboard"
            label="Encounter Log"
            description={`${encounters.length} encounter${encounters.length === 1 ? '' : 's'} stored on device`}
          />
          <View style={styles.divider} />
          <SettingsRow
            icon="trash-2"
            label="Clear Saved Deadlines"
            description="Remove all pinned deadlines from the dashboard"
            onPress={handleClearData}
          />
        </View>

        {/* ── About ── */}
        <Text style={styles.sectionLabel} accessibilityRole="header">About</Text>
        <View style={styles.card}>
          <SettingsRow icon="shield" label="CivicShield Pro" description="v1.0.0 — Multilingual legal assistance" />
          <View style={styles.divider} />
          <SettingsRow icon="lock" label="Privacy" description="All data stays on your device. Nothing is uploaded or shared." />
          <View style={styles.divider} />
          <SettingsRow icon="heart" label="Built for the Community" description="Free legal education and assistance tools" />
        </View>

        {/* Disclaimer */}
        <View style={styles.disclaimer}>
          <Text style={styles.disclaimerText}>
            ⚠️ Disclaimer: CivicShield Pro provides general legal information, not legal advice. Laws vary by state and situation. Always consult a licensed attorney for guidance specific to your circumstances.
          </Text>
        </View>

        <Text style={styles.versionText}>CivicShield Pro · v1.0.0</Text>
      </ScrollView>

      <LanguagePicker
        visible={showLangPicker}
        selectedCode={language.code}
        onSelect={(lang) => { setLanguage(lang); setShowLangPicker(false); }}
        onClose={() => setShowLangPicker(false)}
      />
    </View>
  );
}
