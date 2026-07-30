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
import { useRTL } from '@/hooks/useRTL';
import { useT } from '@/hooks/useTranslation';

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
  const { rowDir, arrowIcon } = useRTL();
  return (
    <Pressable
      style={{ flexDirection: rowDir, alignItems: 'center', paddingVertical: 14, paddingHorizontal: 16, gap: 14 }}
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
      {right ?? (onPress ? <Feather name={arrowIcon} size={16} color={colors.mutedForeground} /> : null)}
    </Pressable>
  );
}

export default function SettingsScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;
  const { t } = useT();
  const { rowDir } = useRTL();

  const {
    language, setLanguage,
    fontSize, setFontSize, fs,
    highContrast, setHighContrast,
    encounters, clearDeadlines, savedDeadlines,
  } = useApp();

  const FONT_SIZES: { labelKey: 'settings.font_small' | 'settings.font_medium' | 'settings.font_large'; value: FontSizeLevel; preview: number }[] = [
    { labelKey: 'settings.font_small',  value: 'small',  preview: 12 },
    { labelKey: 'settings.font_medium', value: 'medium', preview: 14 },
    { labelKey: 'settings.font_large',  value: 'large',  preview: 18 },
  ];

  const [showLangPicker, setShowLangPicker] = useState(false);

  const handleHighContrast = (v: boolean) => {
    setHighContrast(v);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
  };

  const handleClearData = () => {
    Alert.alert(
      t('settings.clear_title'),
      `${t('settings.clear_title')}: ${encounters.length} encounter log${encounters.length === 1 ? '' : 's'} + ${savedDeadlines.length} deadline${savedDeadlines.length === 1 ? '' : 's'}.`,
      [
        { text: t('settings.clear_cancel'), style: 'cancel' },
        {
          text: t('settings.clear_confirm'),
          style: 'destructive',
          onPress: () => {
            clearDeadlines();
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
            Alert.alert(t('settings.cleared_title'), t('settings.cleared_msg'));
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
      flexDirection: rowDir, alignItems: 'center', gap: 12,
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
    fontRow: { flexDirection: rowDir, gap: 8, paddingHorizontal: 16, paddingVertical: 14 },
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
    hcRow: { flexDirection: rowDir },
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
        <Text style={styles.headerTitle} accessibilityRole="header">{t('settings.title')}</Text>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent}>

        {/* ── Language ── */}
        <Text style={styles.sectionLabel} accessibilityRole="header">{t('settings.section_language')}</Text>
        <View style={styles.card}>
          <SettingsRow
            icon="globe"
            label={t('settings.app_language')}
            description={`${language.nativeName} — ${language.name}`}
            onPress={() => setShowLangPicker(true)}
          />
        </View>

        {/* ── Accessibility ── */}
        <Text style={styles.sectionLabel} accessibilityRole="header">{t('settings.section_accessibility')}</Text>
        <View style={styles.card}>
          {/* Font size chips */}
          <View style={{ paddingHorizontal: 16, paddingTop: 14, paddingBottom: 4 }}>
            <View style={{ flexDirection: rowDir, alignItems: 'center', gap: 14, marginBottom: 12 }}>
              <View style={{ width: 36, height: 36, borderRadius: 10, backgroundColor: colors.primary + '18', alignItems: 'center', justifyContent: 'center' }}>
                <Feather name="type" size={18} color={colors.primary} />
              </View>
              <View>
                <Text style={{ fontSize: fs(15), fontFamily: 'Inter_500Medium', color: colors.foreground }}>{t('settings.font_size')}</Text>
                <Text style={{ fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground }}>
                  {t('settings.font_size_desc')}
                </Text>
              </View>
            </View>
            <View style={styles.fontRow}>
              {FONT_SIZES.map((f) => (
                <Pressable
                  key={f.value}
                  style={[styles.fontChip, fontSize === f.value && styles.fontChipActive]}
                  onPress={() => { setFontSize(f.value); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); }}
                  accessibilityLabel={`Font size ${t(f.labelKey)}`}
                  accessibilityRole="radio"
                  accessibilityState={{ selected: fontSize === f.value }}
                >
                  <Text style={[{ fontSize: f.preview }, styles.fontPreview, fontSize === f.value && styles.fontPreviewActive]}>Aa</Text>
                  <Text style={[styles.fontChipLabel, fontSize === f.value && styles.fontChipLabelActive]}>{t(f.labelKey)}</Text>
                </Pressable>
              ))}
            </View>
          </View>

          <View style={styles.divider} />

          {/* High contrast toggle */}
          <SettingsRow
            icon="sun"
            label={t('settings.high_contrast')}
            description={highContrast ? t('settings.high_contrast_on') : t('settings.high_contrast_off')}
            right={
              <Switch
                value={highContrast}
                onValueChange={handleHighContrast}
                trackColor={{ false: colors.muted, true: colors.primary + '80' }}
                thumbColor={highContrast ? colors.primary : '#F4F4F4'}
                accessibilityLabel={t('settings.high_contrast')}
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
            label={t('settings.screen_reader')}
            description={t('settings.screen_reader_desc')}
          />
        </View>

        {/* ── Guided Tour & QR ── */}
        <Text style={styles.sectionLabel} accessibilityRole="header">{t('settings.section_tour')}</Text>
        <View style={styles.card}>
          <SettingsRow
            icon="compass"
            label={t('settings.guided_tour')}
            description={t('settings.guided_tour_desc')}
            onPress={() => { router.back(); setTimeout(() => router.push('/tour'), 300); }}
          />
          <View style={styles.divider} />
          <SettingsRow
            icon="grid"
            label={t('settings.expo_qr')}
            description={t('settings.expo_qr_desc')}
            onPress={() => { router.back(); setTimeout(() => router.push('/qrcode-screen'), 300); }}
          />
        </View>

        {/* ── Data ── */}
        <Text style={styles.sectionLabel} accessibilityRole="header">{t('settings.section_data')}</Text>
        <View style={styles.card}>
          <SettingsRow
            icon="database"
            label={t('settings.deadlines_label')}
            description={`${savedDeadlines.length} deadline${savedDeadlines.length === 1 ? '' : 's'} pinned`}
          />
          <View style={styles.divider} />
          <SettingsRow
            icon="clipboard"
            label={t('settings.log_label')}
            description={`${encounters.length} encounter${encounters.length === 1 ? '' : 's'} stored`}
          />
          <View style={styles.divider} />
          <SettingsRow
            icon="trash-2"
            label={t('settings.clear_deadlines')}
            description={t('settings.clear_deadlines_desc')}
            onPress={handleClearData}
          />
        </View>

        {/* ── About ── */}
        <Text style={styles.sectionLabel} accessibilityRole="header">{t('settings.section_about')}</Text>
        <View style={styles.card}>
          <SettingsRow icon="shield" label="CivicShield Pro" description={t('settings.app_desc')} />
          <View style={styles.divider} />
          <SettingsRow icon="lock" label={t('settings.privacy_row')} description={t('settings.privacy_desc')} />
          <View style={styles.divider} />
          <SettingsRow icon="heart" label={t('settings.built_for')} description={t('settings.built_for_desc')} />
        </View>

        {/* Disclaimer */}
        <View style={styles.disclaimer}>
          <Text style={styles.disclaimerText}>{t('settings.disclaimer')}</Text>
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
