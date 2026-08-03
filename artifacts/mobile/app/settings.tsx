import React, { useState } from 'react';
import {
  Alert,
  KeyboardAvoidingView,
  Modal,
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
import { PasswordModal } from '@/components/PasswordModal';
import { LanguagePicker } from '@/components/LanguagePicker';
import { Encounter, FontSizeLevel, useApp } from '@/context/AppContext';
import { BackupSchedule, BACKUP_SCHEDULE_LABELS } from '@/utils/backupSchedule';
import { useColors } from '@/hooks/useColors';
import { useRTL } from '@/hooks/useRTL';
import { useT } from '@/hooks/useTranslation';
import { aesDecryptStrong, aesEncryptStrong } from '@/utils/encryption';


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

// ─── BackupDecryptModal ────────────────────────────────────────────────────────
// Simple single-password modal used when restoring an encrypted backup file.

interface BackupDecryptModalProps {
  visible: boolean;
  onCancel: () => void;
  /** Return true if decryption succeeded; false if the password was wrong. */
  onDecrypt: (password: string) => Promise<boolean>;
}

function BackupDecryptModal({ visible, onCancel, onDecrypt }: BackupDecryptModalProps) {
  const colors = useColors();
  const { fs } = useApp();
  const { t } = useT();
  const [password,     setPassword]     = useState('');
  const [error,        setError]        = useState('');
  const [isDecrypting, setIsDecrypting] = useState(false);

  const handleClose = () => {
    setPassword('');
    setError('');
    onCancel();
  };

  const handleUnlock = async () => {
    const pwd = password.trim();
    if (!pwd || isDecrypting) return;
    setIsDecrypting(true);
    setError('');
    const ok = await onDecrypt(pwd);
    setIsDecrypting(false);
    if (!ok) {
      setError(t('settings.restore_pw_wrong'));
    } else {
      setPassword('');
      setError('');
    }
  };

  const s = StyleSheet.create({
    overlay:  { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
    sheet:    { backgroundColor: colors.background, borderTopLeftRadius: 20, borderTopRightRadius: 20, padding: 24, paddingBottom: 36 },
    handle:   { width: 36, height: 4, borderRadius: 2, backgroundColor: colors.border, alignSelf: 'center', marginBottom: 20 },
    iconWrap: { width: 56, height: 56, borderRadius: 28, backgroundColor: colors.primary + '18', alignItems: 'center', justifyContent: 'center', alignSelf: 'center', marginBottom: 14 },
    title:    { fontSize: fs(18), fontFamily: 'Inter_700Bold',    color: colors.foreground,       textAlign: 'center', marginBottom: 8 },
    desc:     { fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground,  textAlign: 'center', lineHeight: 19, marginBottom: 20 },
    input:    { backgroundColor: colors.muted, borderRadius: 12, borderWidth: 1, borderColor: colors.border, paddingHorizontal: 16, paddingVertical: 12, fontSize: fs(15), fontFamily: 'Inter_400Regular', color: colors.foreground, marginBottom: error ? 8 : 16 },
    errorText: { fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.destructive, marginBottom: 12 },
    btnPrimary:         { backgroundColor: colors.primary,        borderRadius: 12, paddingVertical: 14, alignItems: 'center', marginBottom: 10 },
    btnPrimaryDisabled: { backgroundColor: colors.primary + '60', borderRadius: 12, paddingVertical: 14, alignItems: 'center', marginBottom: 10 },
    btnCancel: { paddingVertical: 10, alignItems: 'center' },
    btnTextPrimary: { fontSize: fs(15), fontFamily: 'Inter_600SemiBold', color: colors.primaryForeground },
    btnTextCancel:  { fontSize: fs(14), fontFamily: 'Inter_400Regular',  color: colors.mutedForeground },
  });

  const canUnlock = password.trim().length > 0 && !isDecrypting;

  return (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={handleClose}
    >
      <KeyboardAvoidingView
        style={s.overlay}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <Pressable style={{ flex: 1 }} onPress={handleClose} />
        <View style={s.sheet}>
          <View style={s.handle} />
          <View style={s.iconWrap}>
            <Feather name="unlock" size={24} color={colors.primary} />
          </View>
          <Text style={s.title}>{t('settings.restore_pw_title')}</Text>
          <Text style={s.desc}>{t('settings.restore_pw_desc')}</Text>

          <TextInput
            style={s.input}
            placeholder={t('settings.restore_pw_ph')}
            placeholderTextColor={colors.mutedForeground}
            secureTextEntry
            value={password}
            onChangeText={(v) => { setPassword(v); setError(''); }}
            autoCapitalize="none"
            autoCorrect={false}
            returnKeyType="done"
            onSubmitEditing={canUnlock ? handleUnlock : undefined}
            editable={!isDecrypting}
          />

          {error ? <Text style={s.errorText}>{error}</Text> : null}

          <Pressable
            style={canUnlock ? s.btnPrimary : s.btnPrimaryDisabled}
            onPress={canUnlock ? handleUnlock : undefined}
            disabled={!canUnlock}
          >
            <Text style={s.btnTextPrimary}>
              {isDecrypting ? '…' : t('settings.restore_pw_btn')}
            </Text>
          </Pressable>

          <Pressable style={s.btnCancel} onPress={handleClose} disabled={isDecrypting}>
            <Text style={s.btnTextCancel}>{t('settings.restore_pw_cancel')}</Text>
          </Pressable>
        </View>
      </KeyboardAvoidingView>
    </Modal>
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
    appLockEnabled,
    backupSchedule, setBackupSchedule, lastAutoBackupAt,
    importEncounters,
  } = useApp();

  // ── Backup ────────────────────────────────────────────────────────────────
  const [isBackingUp, setIsBackingUp]   = useState(false);
  const [isRestoring, setIsRestoring]   = useState(false);
  const [backupPwModalVisible,  setBackupPwModalVisible]  = useState(false);
  const [restorePwModalVisible, setRestorePwModalVisible] = useState(false);
  const [pendingEncryptedData, setPendingEncryptedData]   = useState<Record<string, unknown> | null>(null);

  /** Friendly label for the last auto-backup timestamp. */
  const formatLastBackup = (iso: string | null): string => {
    if (!iso) return 'Never backed up yet';
    const diff = Date.now() - new Date(iso).getTime();
    const mins  = Math.floor(diff / 60_000);
    if (mins < 1)  return 'Backed up just now';
    if (mins < 60) return `Backed up ${mins} min ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24)  return `Backed up ${hrs}h ago`;
    return `Backed up ${Math.floor(hrs / 24)}d ago`;
  };

  /** Show the optional-password modal before creating a backup file. */
  const handleBackup = () => {
    if (encounters.length === 0) {
      Alert.alert('Back up log', 'No encounters to back up yet.');
      return;
    }
    if (isBackingUp) return;
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    setBackupPwModalVisible(true);
  };

  /** Called by PasswordModal with the chosen password (or null = no password). */
  const doBackup = async (password: string | null) => {
    setBackupPwModalVisible(false);
    setIsBackingUp(true);
    try {
      let filePayload: string;
      let fileName: string;

      if (password) {
        // Encrypt the encounters with AES-256-CBC + PBKDF2
        const innerJson = JSON.stringify({
          version: 1,
          app: 'CivicShield Pro',
          exportedAt: new Date().toISOString(),
          encounters,
        });
        filePayload = JSON.stringify({
          version: 1,
          app: 'CivicShield Pro',
          exportedAt: new Date().toISOString(),
          encrypted: true,
          payload: aesEncryptStrong(innerJson, password),
        }, null, 2);
        fileName = 'civicshield-backup-protected.json';
      } else {
        filePayload = JSON.stringify({
          version: 1,
          app: 'CivicShield Pro',
          exportedAt: new Date().toISOString(),
          encounters,
        }, null, 2);
        fileName = 'civicshield-backup.json';
      }

      const fileUri = (FileSystem.cacheDirectory ?? '') + fileName;
      await FileSystem.writeAsStringAsync(fileUri, filePayload, {
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

  // ── Shared encounter validation + import (used by both plain and encrypted restore) ──
  const validateAndImportEncounters = async (raw: unknown[]) => {
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
        'Restore backup',
        `Found ${newEncs.length} encounter${newEncs.length === 1 ? '' : 's'} in this backup.\n\nMerge adds them alongside your current ${encounters.length} — duplicates are skipped.\n\nReplace permanently deletes your current log and cannot be undone.`,
        [
          { text: 'Cancel', style: 'cancel', onPress: () => setIsRestoring(false) },
          {
            text: 'Replace…',
            style: 'destructive',
            onPress: () => {
              Alert.alert(
                'Delete current log?',
                `This will permanently delete all ${encounters.length} encounter${encounters.length === 1 ? '' : 's'} in your current log and replace them with the ${newEncs.length} from the backup.\n\nThis cannot be undone.`,
                [
                  { text: 'Cancel', style: 'cancel', onPress: () => setIsRestoring(false) },
                  {
                    text: 'Delete & Replace',
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
            },
          },
          {
            text: 'Merge',
            onPress: async () => {
              await importEncounters(newEncs, false);
              Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
              Alert.alert('Restored', `${newEncs.length} encounter${newEncs.length === 1 ? '' : 's'} merged into your log.`);
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

      // ── Encrypted backup path ───────────────────────────────────────────────
      if ((parsed as Record<string, unknown>)['encrypted'] === true) {
        setPendingEncryptedData(parsed as Record<string, unknown>);
        setRestorePwModalVisible(true);
        // isRestoring stays true — modal drives the rest of the flow
        return;
      }

      // ── Plain backup path ───────────────────────────────────────────────────
      const raw = (parsed as Record<string, unknown>)['encounters'];
      if (!Array.isArray(raw) || raw.length === 0) {
        Alert.alert('Restore failed', 'No encounters found in this backup file.');
        setIsRestoring(false);
        return;
      }

      await validateAndImportEncounters(raw);
    } catch {
      Alert.alert('Restore failed', 'The file could not be read or is not a valid CivicShield backup.');
      setIsRestoring(false);
    }
  };

  /**
   * Called by BackupDecryptModal with the entered password.
   * Returns true if decryption succeeded (modal can close), false if wrong password.
   */
  const handleDecryptAndRestore = async (password: string): Promise<boolean> => {
    if (!pendingEncryptedData) return false;

    const encryptedPayload = pendingEncryptedData['payload'] as string | undefined;
    if (typeof encryptedPayload !== 'string') return false;

    const decrypted = aesDecryptStrong(encryptedPayload, password);
    if (!decrypted) return false; // wrong password

    let innerParsed: unknown;
    try { innerParsed = JSON.parse(decrypted); } catch { return false; }

    const raw = (innerParsed as Record<string, unknown>)?.['encounters'];
    if (!Array.isArray(raw)) return false;

    // Close the modal before running the import flow
    setRestorePwModalVisible(false);
    setPendingEncryptedData(null);

    if (raw.length === 0) {
      Alert.alert('Restore failed', 'No encounters found in this backup file.');
      setIsRestoring(false);
      return true;
    }

    await validateAndImportEncounters(raw);
    return true;
  };

  const handleDecryptCancel = () => {
    setRestorePwModalVisible(false);
    setPendingEncryptedData(null);
    setIsRestoring(false);
  };

  // PIN setup moved to dedicated security screen (/security)

  const FONT_SIZES: { labelKey: 'settings.font_small' | 'settings.font_medium' | 'settings.font_large'; value: FontSizeLevel; preview: number }[] = [
    { labelKey: 'settings.font_small',  value: 'small',  preview: 12 },
    { labelKey: 'settings.font_medium', value: 'medium', preview: 14 },
    { labelKey: 'settings.font_large',  value: 'large',  preview: 18 },
  ];

  const [showLangPicker, setShowLangPicker]           = useState(false);
  const [showSchedulePicker, setShowSchedulePicker]   = useState(false);

  const handleHighContrast = (v: boolean) => {
    setHighContrast(v);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
  };

  /** Share the latest auto-backup file so users can move it to email, Files, or cloud storage. */
  const [isSharingAutoBackup, setIsSharingAutoBackup] = useState(false);
  const handleShareAutoBackup = async () => {
    if (isSharingAutoBackup) return;
    setIsSharingAutoBackup(true);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    try {
      const fileUri =
        (FileSystem.documentDirectory ?? FileSystem.cacheDirectory ?? '') +
        'civicshield-auto-backup.json';

      // Verify the file actually exists before trying to share it
      const info = await FileSystem.getInfoAsync(fileUri);
      if (!info.exists) {
        Alert.alert('Auto-backup', 'No auto-backup file found. Wait for the next scheduled backup or record an encounter.');
        return;
      }

      const canShare = await Sharing.isAvailableAsync();
      if (!canShare) {
        Alert.alert('Auto-backup', 'Sharing is not available on this device.');
        return;
      }

      await Sharing.shareAsync(fileUri, {
        mimeType: 'application/json',
        dialogTitle: 'Share auto-backup',
        UTI: 'public.json',
      });
    } catch {
      Alert.alert('Auto-backup', 'Could not share the backup file. Please try again.');
    } finally {
      setIsSharingAutoBackup(false);
    }
  };

  const handleClearData = () => {
    Alert.alert(
      t('settings.clear_title'),
      `${t('settings.clear_title')}: ${encounters.length} encounter${encounters.length === 1 ? '' : 's'} + ${savedDeadlines.length} deadline${savedDeadlines.length === 1 ? '' : 's'}.`,
      [
        { text: t('settings.clear_cancel'), style: 'cancel' },
        {
          text: t('settings.clear_confirm'),
          style: 'destructive',
          onPress: () => {
            Alert.alert(
              t('settings.clear_confirm2_title'),
              `This will permanently delete all ${encounters.length} encounter${encounters.length === 1 ? '' : 's'} and ${savedDeadlines.length} deadline${savedDeadlines.length === 1 ? '' : 's'}.\n\nThis cannot be undone.`,
              [
                { text: t('settings.clear_cancel'), style: 'cancel' },
                {
                  text: t('settings.clear_confirm2_btn'),
                  style: 'destructive',
                  onPress: () => {
                    clearDeadlines();
                    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
                    Alert.alert(t('settings.cleared_title'), t('settings.cleared_msg'));
                  },
                },
              ],
            );
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
        <Text style={styles.sectionLabel} accessibilityRole="header">🔒 {t('security.title')}</Text>
        <View style={styles.card}>
          <SettingsRow
            icon="lock"
            label={t('security.title')}
            description={appLockEnabled ? t('security.app_lock_on') : t('security.app_lock_off')}
            onPress={() => router.push('/security' as any)}
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
            icon="refresh-cw"
            label="Backup schedule"
            description={
              backupSchedule === 'off'
                ? 'Auto-backup is off'
                : `${BACKUP_SCHEDULE_LABELS[backupSchedule]} · ${formatLastBackup(lastAutoBackupAt)}`
            }
            onPress={() => {
              Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
              setShowSchedulePicker(true);
            }}
          />
          {/* Share auto-backup — only shown when auto-backup is on and a backup exists */}
          {backupSchedule !== 'off' && lastAutoBackupAt ? (
            <>
              <View style={styles.divider} />
              <SettingsRow
                icon="share-2"
                label="Share auto-backup"
                description={
                  isSharingAutoBackup
                    ? 'Preparing…'
                    : `Latest: ${formatLastBackup(lastAutoBackupAt)} · Tap to share or restore`
                }
                onPress={handleShareAutoBackup}
              />
            </>
          ) : null}
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

      {/* Backup password modal — shown before creating the backup file */}
      <PasswordModal
        visible={backupPwModalVisible}
        onCancel={() => setBackupPwModalVisible(false)}
        onShare={doBackup}
      />

      {/* Restore decrypt modal — shown when the imported backup is encrypted */}
      <BackupDecryptModal
        visible={restorePwModalVisible}
        onCancel={handleDecryptCancel}
        onDecrypt={handleDecryptAndRestore}
      />

      {/* Backup schedule picker — bottom sheet */}
      <Modal
        visible={showSchedulePicker}
        transparent
        animationType="slide"
        onRequestClose={() => setShowSchedulePicker(false)}
      >
        <Pressable
          style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.45)' }}
          onPress={() => setShowSchedulePicker(false)}
        />
        <View style={{
          backgroundColor: colors.background,
          borderTopLeftRadius: 20, borderTopRightRadius: 20,
          padding: 24, paddingBottom: 40,
        }}>
          {/* Handle */}
          <View style={{ width: 36, height: 4, borderRadius: 2, backgroundColor: colors.border, alignSelf: 'center', marginBottom: 20 }} />

          {/* Title */}
          <View style={{ flexDirection: rowDir, alignItems: 'center', gap: 10, marginBottom: 6 }}>
            <View style={{ width: 36, height: 36, borderRadius: 10, backgroundColor: colors.primary + '18', alignItems: 'center', justifyContent: 'center' }}>
              <Feather name="refresh-cw" size={18} color={colors.primary} />
            </View>
            <Text style={{ fontSize: fs(17), fontFamily: 'Inter_700Bold', color: colors.foreground }}>
              Backup schedule
            </Text>
          </View>
          <Text style={{ fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginBottom: 20, marginLeft: 46 }}>
            A silent backup is saved locally on-device — no account needed.
          </Text>

          {/* Options */}
          {(['off', 'each', 'daily', 'weekly'] as BackupSchedule[]).map((opt, idx, arr) => {
            const selected = backupSchedule === opt;
            const subtitles: Record<BackupSchedule, string> = {
              off:    'No automatic backups',
              each:   'Backup runs whenever you log an encounter',
              daily:  'Backup runs once per day when you open the app',
              weekly: 'Backup runs once per week when you open the app',
            };
            return (
              <React.Fragment key={opt}>
                <Pressable
                  style={{
                    flexDirection: rowDir, alignItems: 'center', gap: 14,
                    paddingVertical: 13, paddingHorizontal: 4,
                  }}
                  onPress={() => {
                    setBackupSchedule(opt);
                    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
                    setShowSchedulePicker(false);
                  }}
                  accessibilityRole="radio"
                  accessibilityState={{ selected }}
                  accessibilityLabel={BACKUP_SCHEDULE_LABELS[opt]}
                >
                  <View style={{
                    width: 22, height: 22, borderRadius: 11,
                    borderWidth: 2,
                    borderColor: selected ? colors.primary : colors.border,
                    backgroundColor: selected ? colors.primary : 'transparent',
                    alignItems: 'center', justifyContent: 'center',
                  }}>
                    {selected && <View style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: colors.primaryForeground }} />}
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={{ fontSize: fs(15), fontFamily: selected ? 'Inter_600SemiBold' : 'Inter_500Medium', color: colors.foreground }}>
                      {BACKUP_SCHEDULE_LABELS[opt]}
                    </Text>
                    <Text style={{ fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 1 }}>
                      {subtitles[opt]}
                    </Text>
                  </View>
                </Pressable>
                {idx < arr.length - 1 && (
                  <View style={{ height: 1, backgroundColor: colors.border, marginLeft: 36 }} />
                )}
              </React.Fragment>
            );
          })}

          {/* Last backup note */}
          {backupSchedule !== 'off' && (
            <View style={{
              marginTop: 20, backgroundColor: colors.muted,
              borderRadius: 10, padding: 12, flexDirection: rowDir, gap: 8, alignItems: 'center',
            }}>
              <Feather name="clock" size={14} color={colors.mutedForeground} />
              <Text style={{ fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground }}>
                {formatLastBackup(lastAutoBackupAt)}
              </Text>
            </View>
          )}
        </View>
      </Modal>
    </View>
  );
}
