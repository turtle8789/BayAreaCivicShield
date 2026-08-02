import React, { useState } from 'react';
import {
  Alert,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  View,
} from 'react-native';
import { router } from 'expo-router';
import { Feather } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system/legacy';
import * as Sharing from 'expo-sharing';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { LanguagePicker } from '@/components/LanguagePicker';
import { Encounter, FontSizeLevel, useApp } from '@/context/AppContext';
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
    appLockEnabled, appPin, setAppLock,
    importEncounters,
  } = useApp();

  // ── Backup ────────────────────────────────────────────────────────────────
  const [isBackingUp, setIsBackingUp]   = useState(false);
  const [isRestoring, setIsRestoring]   = useState(false);

  const handleBackup = async () => {
    if (encounters.length === 0) {
      Alert.alert('Back up log', 'No encounters to back up yet.');
      return;
    }
    if (isBackingUp) return;
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    setIsBackingUp(true);
    try {
      const payload = JSON.stringify({
        version: 1,
        app: 'CivicShield Pro',
        exportedAt: new Date().toISOString(),
        encounters,
      }, null, 2);
      const fileUri = (FileSystem.cacheDirectory ?? '') + 'civicshield-backup.json';
      await FileSystem.writeAsStringAsync(fileUri, payload, {
        encoding: FileSystem.EncodingType.UTF8,
      });
      const canShare = await Sharing.isAvailableAsync();
      if (canShare) {
        await Sharing.shareAsync(fileUri, {
          mimeType: 'application/json',
          dialogTitle: 'Back up encounter log',
          UTI: 'public.json',
        });
      } else {
        Alert.alert('Back up log', 'Sharing is not available on this device.');
      }
    } catch {
      Alert.alert('Back up log', 'Could not create backup. Please try again.');
    } finally {
      setIsBackingUp(false);
    }
  };

  const handleRestore = async () => {
    if (isRestoring) return;
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    setIsRestoring(true);
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['application/json', 'text/plain', '*/*'],
        copyToCacheDirectory: true,
      });
      if (result.canceled || !result.assets?.[0]) { setIsRestoring(false); return; }

      const asset = result.assets[0];
      const content = await FileSystem.readAsStringAsync(asset.uri, {
        encoding: FileSystem.EncodingType.UTF8,
      });

      // ── Runtime validation ─────────────────────────────────────────────────
      let parsed: unknown;
      try { parsed = JSON.parse(content); } catch {
        Alert.alert('Restore failed', 'The file is not valid JSON.');
        setIsRestoring(false);
        return;
      }

      if (
        typeof parsed !== 'object' || parsed === null ||
        (parsed as Record<string, unknown>)['app'] !== 'CivicShield Pro' ||
        (parsed as Record<string, unknown>)['version'] !== 1
      ) {
        Alert.alert('Restore failed', 'This file is not a CivicShield Pro backup.');
        setIsRestoring(false);
        return;
      }

      const raw = (parsed as Record<string, unknown>)['encounters'];
      if (!Array.isArray(raw) || raw.length === 0) {
        Alert.alert('Restore failed', 'No encounters found in this backup file.');
        setIsRestoring(false);
        return;
      }

      const VALID_TYPES = new Set<string>([
        'traffic_stop', 'arrest', 'questioning', 'citation', 'search', 'other',
      ]);

      const validationErrors: string[] = [];
      const newEncs: Encounter[] = raw.map((item: unknown, idx: number) => {
        if (typeof item !== 'object' || item === null) {
          validationErrors.push(`Entry ${idx + 1}: not an object`);
          return null as unknown as Encounter;
        }
        const e = item as Record<string, unknown>;

        if (typeof e['id'] !== 'string' || e['id'].trim() === '') {
          validationErrors.push(`Entry ${idx + 1}: missing or empty id`);
        }
        if (typeof e['date'] !== 'string' || isNaN(Date.parse(e['date'] as string))) {
          validationErrors.push(`Entry ${idx + 1}: invalid date`);
        }
        if (typeof e['type'] !== 'string' || !VALID_TYPES.has(e['type'] as string)) {
          validationErrors.push(`Entry ${idx + 1}: unknown type "${e['type']}"`);
        }
        for (const field of ['location', 'officerInfo', 'description', 'outcome'] as const) {
          if (typeof e[field] !== 'string') {
            validationErrors.push(`Entry ${idx + 1}: field "${field}" must be a string`);
          }
        }

        return {
          id:          String(e['id'] ?? ''),
          date:        String(e['date'] ?? ''),
          type:        (e['type'] as Encounter['type']) ?? 'other',
          location:    String(e['location'] ?? ''),
          officerInfo: String(e['officerInfo'] ?? ''),
          description: String(e['description'] ?? ''),
          outcome:     String(e['outcome'] ?? ''),
        } satisfies Encounter;
      });

      if (validationErrors.length > 0) {
        Alert.alert(
          'Restore failed',
          `The backup contains ${validationErrors.length} invalid record${validationErrors.length === 1 ? '' : 's'}. No data was changed.\n\n${validationErrors.slice(0, 3).join('\n')}${validationErrors.length > 3 ? `\n…and ${validationErrors.length - 3} more` : ''}`,
        );
        setIsRestoring(false);
        return;
      }

      if (encounters.length > 0) {
        Alert.alert(
          'Merge or replace?',
          `Found ${newEncs.length} encounter${newEncs.length === 1 ? '' : 's'} in this backup.\n\nMerge adds them alongside your current ${encounters.length} — duplicates are skipped. Replace deletes your current log and uses the backup only.`,
          [
            { text: 'Cancel', style: 'cancel', onPress: () => setIsRestoring(false) },
            {
              text: 'Merge',
              onPress: async () => {
                await importEncounters(newEncs, false);
                Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
                Alert.alert('Restored', `${newEncs.length} encounter${newEncs.length === 1 ? '' : 's'} merged into your log.`);
                setIsRestoring(false);
              },
            },
            {
              text: 'Replace',
              style: 'destructive',
              onPress: async () => {
                await importEncounters(newEncs, true);
                Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
                Alert.alert('Restored', `Log replaced with ${newEncs.length} encounter${newEncs.length === 1 ? '' : 's'} from backup.`);
                setIsRestoring(false);
              },
            },
          ],
        );
      } else {
        await importEncounters(newEncs, true);
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        Alert.alert('Restored', `${newEncs.length} encounter${newEncs.length === 1 ? '' : 's'} restored from backup.`);
        setIsRestoring(false);
      }
    } catch {
      Alert.alert('Restore failed', 'The file could not be read or is not a valid CivicShield backup.');
      setIsRestoring(false);
    }
  };

  // ── App Lock PIN setup state ──────────────────────────────────────────────
  const [showPinSetup, setShowPinSetup] = useState(false);
  const [pinStep, setPinStep]           = useState<'enter' | 'confirm'>('enter');
  const [pinInput, setPinInput]         = useState('');
  const [pinConfirm, setPinConfirm]     = useState('');
  const [pinError, setPinError]         = useState('');

  const startPinSetup = () => {
    setPinInput(''); setPinConfirm(''); setPinStep('enter'); setPinError('');
    setShowPinSetup(true);
  };

  const handlePinChange = (v: string) => {
    const digits = v.replace(/\D/g, '').slice(0, 4);
    setPinError('');
    if (pinStep === 'enter') {
      setPinInput(digits);
      if (digits.length === 4) { setPinStep('confirm'); setPinConfirm(''); }
    } else {
      setPinConfirm(digits);
      if (digits.length === 4) {
        if (digits === pinInput) {
          setAppLock(true, digits);
          setShowPinSetup(false);
          Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        } else {
          setPinError('PINs don\'t match — try again');
          setPinInput(''); setPinConfirm(''); setPinStep('enter');
        }
      }
    }
  };

  const disableLock = () => {
    Alert.alert('Disable App Lock', 'Remove the PIN and allow anyone to open this app?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Disable', style: 'destructive', onPress: () => { setAppLock(false, ''); setShowPinSetup(false); } },
    ]);
  };

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

        {/* ── Privacy & Security ── */}
        <Text style={styles.sectionLabel} accessibilityRole="header">🔒 Privacy &amp; Security</Text>
        <View style={styles.card}>
          <SettingsRow
            icon="lock"
            label="App Lock"
            description={appLockEnabled ? 'PIN required to open the app' : 'Anyone can open the app'}
            right={
              <Switch
                value={appLockEnabled}
                onValueChange={(v) => { if (v) startPinSetup(); else disableLock(); }}
                trackColor={{ false: colors.muted, true: colors.primary + '80' }}
                thumbColor={appLockEnabled ? colors.primary : '#F4F4F4'}
                accessibilityLabel="App Lock"
              />
            }
          />
          {appLockEnabled && (
            <>
              <View style={styles.divider} />
              <SettingsRow icon="edit-2" label="Change PIN" description="Update your 4-digit PIN" onPress={startPinSetup} />
            </>
          )}

          {/* Inline PIN setup card */}
          {showPinSetup && (
            <View style={{ padding: 16, borderTopWidth: 1, borderTopColor: colors.border }}>
              <Text style={{ fontSize: fs(13), fontFamily: 'Inter_600SemiBold', color: colors.foreground, marginBottom: 4 }}>
                {pinStep === 'enter' ? '🔐 Set a 4-digit PIN' : '✅ Confirm your PIN'}
              </Text>
              <Text style={{ fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginBottom: 12 }}>
                {pinStep === 'enter' ? 'Enter 4 digits — it will auto-advance when done.' : 'Re-enter the same PIN to confirm.'}
              </Text>
              {/* Dot display */}
              <View style={{ flexDirection: 'row', gap: 14, marginBottom: 12 }}>
                {[0, 1, 2, 3].map(i => {
                  const filled = pinStep === 'enter' ? i < pinInput.length : i < pinConfirm.length;
                  return (
                    <View key={i} style={{ width: 14, height: 14, borderRadius: 7, borderWidth: 2,
                      borderColor: pinError ? '#E05252' : colors.primary,
                      backgroundColor: filled ? (pinError ? '#E05252' : colors.primary) : 'transparent' }} />
                  );
                })}
              </View>
              {pinError ? <Text style={{ color: '#E05252', fontSize: fs(12), fontFamily: 'Inter_500Medium', marginBottom: 8 }}>{pinError}</Text> : null}
              <TextInput
                style={{ backgroundColor: colors.background, borderWidth: 1, borderColor: colors.border,
                  borderRadius: 10, paddingHorizontal: 14, paddingVertical: 11, fontSize: fs(16),
                  fontFamily: 'Inter_400Regular', color: colors.foreground, letterSpacing: 8 }}
                value={pinStep === 'enter' ? pinInput : pinConfirm}
                onChangeText={handlePinChange}
                keyboardType="number-pad"
                secureTextEntry
                maxLength={4}
                autoFocus
                placeholder="••••"
                placeholderTextColor={colors.mutedForeground}
                accessibilityLabel={pinStep === 'enter' ? 'Enter PIN' : 'Confirm PIN'}
              />
              <Pressable onPress={() => setShowPinSetup(false)}
                style={{ marginTop: 12, alignItems: 'center', paddingVertical: 10 }}>
                <Text style={{ fontSize: fs(13), fontFamily: 'Inter_500Medium', color: colors.mutedForeground }}>Cancel</Text>
              </Pressable>
            </View>
          )}
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
            icon="upload-cloud"
            label={t('settings.backup_label')}
            description={isBackingUp ? 'Preparing…' : t('settings.backup_desc')}
            onPress={handleBackup}
          />
          <View style={styles.divider} />
          <SettingsRow
            icon="download-cloud"
            label={t('settings.restore_label')}
            description={isRestoring ? 'Importing…' : t('settings.restore_desc')}
            onPress={handleRestore}
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
