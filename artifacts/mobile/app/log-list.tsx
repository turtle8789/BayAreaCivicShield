import React, { useState } from 'react';
import {
  Alert,
  FlatList,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { router } from 'expo-router';
import { Feather } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import * as FileSystem from 'expo-file-system/legacy';
import * as Print from 'expo-print';
import * as Sharing from 'expo-sharing';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { PasswordModal } from '@/components/PasswordModal';
import { Encounter, ENCOUNTER_TYPE_LABELS, useApp } from '@/context/AppContext';
import { useColors } from '@/hooks/useColors';
import { useRTL } from '@/hooks/useRTL';
import { useT } from '@/hooks/useTranslation';
import { aesEncryptStrong } from '@/utils/encryption';
import { buildProtectedHtml } from '@/utils/protectedHtml';

// ─── EncounterCard ─────────────────────────────────────────────────────────────

interface EncounterCardProps {
  encounter: Encounter;
  onDelete: () => void;
  selectionMode: boolean;
  selected: boolean;
  onLongPress: () => void;
  onToggleSelect: () => void;
}

function EncounterCard({ encounter, onDelete, selectionMode, selected, onLongPress, onToggleSelect }: EncounterCardProps) {
  const colors = useColors();
  const { fs } = useApp();
  const { t } = useT();
  const { rowDir, textStyle } = useRTL();
  const [expanded, setExpanded] = useState(false);
  const [shareModalVisible, setShareModalVisible] = useState(false);
  const [isSharing, setIsSharing] = useState(false);

  const date = new Date(encounter.date);
  const formattedDate = date.toLocaleDateString(undefined, {
    month: 'short', day: 'numeric', year: 'numeric',
  });
  const formattedTime = date.toLocaleTimeString(undefined, {
    hour: '2-digit', minute: '2-digit',
  });

  const handleDelete = () => {
    Alert.alert(t('log.delete_title'), t('log.delete_msg'), [
      { text: t('log.delete_cancel'), style: 'cancel' },
      {
        text: t('log.delete_btn'),
        style: 'destructive',
        onPress: () => {
          Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
          onDelete();
        },
      },
    ]);
  };

  const handleShare = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    setShareModalVisible(true);
  };

  const doSingleExport = async (password: string | null) => {
    setShareModalVisible(false);
    setIsSharing(true);
    try {
      const html = buildEncounterHtml([encounter], t('log.export_title'));

      // Build a human-readable filename: e.g. "traffic-stop-2026-08-02"
      const d = new Date(encounter.date);
      const dateSlug = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
      const typeSlug = encounter.type.replace(/_/g, '-').toLowerCase();
      const baseName = `${typeSlug}-${dateSlug}`;

      if (password) {
        const encryptedPayload = aesEncryptStrong(html, password);
        const wrapperHtml = buildProtectedHtml(encryptedPayload, t('log.export_title'));

        const canShare = await Sharing.isAvailableAsync();
        if (canShare) {
          const fileUri = (FileSystem.cacheDirectory ?? '') + `${baseName}-protected.html`;
          await FileSystem.writeAsStringAsync(fileUri, wrapperHtml, {
            encoding: FileSystem.EncodingType.UTF8,
          });
          await Sharing.shareAsync(fileUri, {
            mimeType: 'text/html',
            dialogTitle: t('log.export_title'),
            UTI: 'public.html',
          });
        } else {
          if (typeof window !== 'undefined') {
            const blob = new Blob([wrapperHtml], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            window.open(url, '_blank');
          }
        }
      } else {
        const { uri } = await Print.printToFileAsync({ html, base64: false });
        const canShare = await Sharing.isAvailableAsync();
        if (canShare) {
          // Copy to a named file so the share sheet shows a meaningful filename
          const namedUri = (FileSystem.cacheDirectory ?? '') + `${baseName}.pdf`;
          await FileSystem.copyAsync({ from: uri, to: namedUri });
          await Sharing.shareAsync(namedUri, {
            mimeType: 'application/pdf',
            dialogTitle: t('log.export_title'),
            UTI: 'com.adobe.pdf',
          });
        } else {
          await Print.printAsync({ html });
        }
      }
    } catch {
      Alert.alert(t('log.export_btn'), t('log.export_error'));
    } finally {
      setIsSharing(false);
    }
  };

  const typeKey = `encounter.${encounter.type}` as any;

  const styles = StyleSheet.create({
    card: {
      backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1,
      borderColor: selected ? colors.primary : colors.border, marginBottom: 10, overflow: 'hidden',
    },
    cardHeader:     { flexDirection: rowDir, alignItems: 'center', padding: 14, gap: 10 },
    typeDot:        { width: 10, height: 10, borderRadius: 5, backgroundColor: colors.primary },
    typeLabel:      { fontSize: fs(15), fontFamily: 'Inter_600SemiBold', color: colors.foreground },
    dateText:       { fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground },
    expandedSection:{ borderTopWidth: 1, borderTopColor: colors.border, padding: 14, gap: 10 },
    fieldLabel:     { fontSize: fs(11), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase', letterSpacing: 0.6, marginBottom: 2 },
    fieldValue:     { fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.foreground, lineHeight: 20, ...textStyle },
    deleteBtn:      { flex: 1, flexDirection: rowDir, alignItems: 'center', justifyContent: 'center', gap: 6, borderRadius: 10, paddingVertical: 9, backgroundColor: colors.destructive + '12', borderWidth: 1, borderColor: colors.destructive + '25' },
    shareBtn:       { flex: 1, flexDirection: rowDir, alignItems: 'center', justifyContent: 'center', gap: 6, borderRadius: 10, paddingVertical: 9, backgroundColor: colors.primary + '12', borderWidth: 1, borderColor: colors.primary + '25' },
    checkCircle:    { width: 22, height: 22, borderRadius: 11, borderWidth: 2, borderColor: colors.primary, alignItems: 'center', justifyContent: 'center', backgroundColor: selected ? colors.primary : 'transparent' },
  });

  const handleHeaderPress = () => {
    if (selectionMode) {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      onToggleSelect();
    } else {
      setExpanded(!expanded);
    }
  };

  return (
    <View style={styles.card}>
      <Pressable style={styles.cardHeader} onPress={handleHeaderPress} onLongPress={() => { Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium); onLongPress(); }}>
        {selectionMode ? (
          <View style={styles.checkCircle}>
            {selected && <Feather name="check" size={13} color="#FFFFFF" />}
          </View>
        ) : (
          <View style={styles.typeDot} />
        )}
        <View style={{ flex: 1 }}>
          <Text style={styles.typeLabel}>{t(typeKey)}</Text>
          <View style={{ flexDirection: rowDir, gap: 6, marginTop: 2 }}>
            <Text style={styles.dateText}>{formattedDate} {t('log.at')} {formattedTime}</Text>
            {encounter.location ? <Text style={styles.dateText}>· {encounter.location}</Text> : null}
          </View>
        </View>
        {!selectionMode && <Feather name={expanded ? 'chevron-up' : 'chevron-down'} size={18} color={colors.mutedForeground} />}
      </Pressable>

      {expanded && (
        <View style={styles.expandedSection}>
          {encounter.officerInfo ? (
            <View>
              <Text style={styles.fieldLabel}>{t('log.officer_info')}</Text>
              <Text style={styles.fieldValue}>{encounter.officerInfo}</Text>
            </View>
          ) : null}
          {encounter.description ? (
            <View>
              <Text style={styles.fieldLabel}>{t('log.description_label')}</Text>
              <Text style={styles.fieldValue}>{encounter.description}</Text>
            </View>
          ) : null}
          {encounter.outcome ? (
            <View>
              <Text style={styles.fieldLabel}>{t('log.outcome_label')}</Text>
              <Text style={styles.fieldValue}>{encounter.outcome}</Text>
            </View>
          ) : null}
          <View style={{ flexDirection: rowDir, marginTop: 4, gap: 8 }}>
            <Pressable style={styles.shareBtn} onPress={handleShare} disabled={isSharing}>
              <Feather name="share" size={14} color={isSharing ? colors.mutedForeground : colors.primary} />
              <Text style={{ fontSize: fs(13), fontFamily: 'Inter_500Medium', color: isSharing ? colors.mutedForeground : colors.primary }}>
                {t('log.share_btn')}
              </Text>
            </Pressable>
            <Pressable style={styles.deleteBtn} onPress={handleDelete}>
              <Feather name="trash-2" size={14} color={colors.destructive} />
              <Text style={{ fontSize: fs(13), fontFamily: 'Inter_500Medium', color: colors.destructive }}>
                {t('log.delete_btn')}
              </Text>
            </Pressable>
          </View>
        </View>
      )}

      <PasswordModal
        visible={shareModalVisible}
        onCancel={() => setShareModalVisible(false)}
        onShare={doSingleExport}
      />
    </View>
  );
}

// ─── HTML builder ──────────────────────────────────────────────────────────────

function buildEncounterHtml(encounters: Encounter[], exportTitle: string): string {
  const now = new Date().toLocaleDateString(undefined, {
    month: 'long', day: 'numeric', year: 'numeric',
  });

  const rows = encounters.map((enc) => {
    const date = new Date(enc.date);
    const dateStr = date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    const timeStr = date.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
    const typeLabel = ENCOUNTER_TYPE_LABELS[enc.type] ?? enc.type;

    const fields: Array<{ label: string; value: string }> = [
      { label: 'Date & Time', value: `${dateStr} at ${timeStr}` },
      { label: 'Type', value: typeLabel },
    ];
    if (enc.location)    fields.push({ label: 'Location',     value: enc.location });
    if (enc.officerInfo) fields.push({ label: 'Officer Info', value: enc.officerInfo });
    if (enc.description) fields.push({ label: 'Description',  value: enc.description });
    if (enc.outcome)     fields.push({ label: 'Outcome',      value: enc.outcome });

    const fieldRows = fields.map(f => `
      <tr>
        <td class="label">${f.label}</td>
        <td class="value">${f.value.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</td>
      </tr>`).join('');

    return `
      <div class="entry">
        <table>${fieldRows}</table>
      </div>`;
  }).join('');

  return `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<style>
  body { font-family: -apple-system, Helvetica, Arial, sans-serif; margin: 0; padding: 32px; color: #111; }
  h1 { font-size: 22px; font-weight: 700; margin: 0 0 4px; color: #111; }
  .meta { font-size: 12px; color: #666; margin-bottom: 28px; }
  .entry { border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px; margin-bottom: 16px; break-inside: avoid; }
  table { width: 100%; border-collapse: collapse; }
  td { padding: 5px 8px; font-size: 13px; vertical-align: top; }
  td.label { color: #666; font-weight: 600; text-transform: uppercase; font-size: 10px; letter-spacing: 0.5px; width: 110px; padding-top: 7px; }
  td.value { color: #111; line-height: 1.5; }
  .footer { margin-top: 32px; font-size: 11px; color: #999; border-top: 1px solid #e0e0e0; padding-top: 12px; }
</style>
</head>
<body>
  <h1>${exportTitle}</h1>
  <div class="meta">Generated on ${now} · ${encounters.length} ${encounters.length === 1 ? 'entry' : 'entries'}</div>
  ${rows}
  <div class="footer">CivicShield Pro · Encounter Log · This document is for personal legal reference only.</div>
</body>
</html>`;
}


// ─── LogListScreen ─────────────────────────────────────────────────────────────

export default function LogListScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;
  const bottomPad = Platform.OS === 'web' ? 34 : insets.bottom;
  const { encounters, deleteEncounter, fs } = useApp();
  const { t } = useT();
  const { rowDir, backIcon } = useRTL();
  const [isExporting, setIsExporting] = useState(false);
  const [passwordModalVisible, setPasswordModalVisible] = useState(false);
  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [multiPasswordModalVisible, setMultiPasswordModalVisible] = useState(false);

  const enterSelectionMode = (id: string) => {
    setSelectedIds(new Set([id]));
    setSelectionMode(true);
  };

  const toggleSelect = (id: string) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  };

  const cancelSelection = () => {
    setSelectionMode(false);
    setSelectedIds(new Set());
  };

  const handleMultiExportPress = () => {
    if (selectedIds.size === 0) return;
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    setMultiPasswordModalVisible(true);
  };

  const doMultiExport = async (password: string | null) => {
    setMultiPasswordModalVisible(false);
    setIsExporting(true);
    try {
      const selected = encounters.filter(e => selectedIds.has(e.id));
      const html = buildEncounterHtml(selected, t('log.export_title'));

      if (password) {
        const encryptedPayload = aesEncryptStrong(html, password);
        const wrapperHtml = buildProtectedHtml(encryptedPayload, t('log.export_title'));

        const canShare = await Sharing.isAvailableAsync();
        if (canShare) {
          const fileUri = (FileSystem.cacheDirectory ?? '') + 'encounter-selection-protected.html';
          await FileSystem.writeAsStringAsync(fileUri, wrapperHtml, {
            encoding: FileSystem.EncodingType.UTF8,
          });
          await Sharing.shareAsync(fileUri, {
            mimeType: 'text/html',
            dialogTitle: t('log.export_title'),
            UTI: 'public.html',
          });
        } else {
          if (typeof window !== 'undefined') {
            const blob = new Blob([wrapperHtml], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            window.open(url, '_blank');
          }
        }
      } else {
        const { uri } = await Print.printToFileAsync({ html, base64: false });
        const canShare = await Sharing.isAvailableAsync();
        if (canShare) {
          await Sharing.shareAsync(uri, {
            mimeType: 'application/pdf',
            dialogTitle: t('log.export_title'),
            UTI: 'com.adobe.pdf',
          });
        } else {
          await Print.printAsync({ html });
        }
      }
      cancelSelection();
    } catch {
      Alert.alert(t('log.export_btn'), t('log.export_error'));
    } finally {
      setIsExporting(false);
    }
  };

  const navigateToNew = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    router.push('/new-log');
  };

  const handleExport = () => {
    if (encounters.length === 0) {
      Alert.alert(t('log.export_btn'), t('log.export_empty'));
      return;
    }
    if (isExporting) return;
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    setPasswordModalVisible(true);
  };

  const doExport = async (password: string | null) => {
    setPasswordModalVisible(false);
    setIsExporting(true);
    try {
      const html = buildEncounterHtml(encounters, t('log.export_title'));

      if (password) {
        // ── Encrypted path: AES-256-CBC + PBKDF2-SHA256 → self-decrypting HTML ──
        const encryptedPayload = aesEncryptStrong(html, password);
        const wrapperHtml = buildProtectedHtml(encryptedPayload, t('log.export_title'));

        const canShare = await Sharing.isAvailableAsync();
        if (canShare) {
          const fileUri = (FileSystem.cacheDirectory ?? '') + 'encounter-log-protected.html';
          await FileSystem.writeAsStringAsync(fileUri, wrapperHtml, {
            encoding: FileSystem.EncodingType.UTF8,
          });
          await Sharing.shareAsync(fileUri, {
            mimeType: 'text/html',
            dialogTitle: t('log.export_title'),
            UTI: 'public.html',
          });
        } else {
          // Web fallback: open as data URI in a new tab
          if (typeof window !== 'undefined') {
            const blob = new Blob([wrapperHtml], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            window.open(url, '_blank');
          }
        }
      } else {
        // ── Plain PDF path (original behaviour) ────────────────────────────────
        const { uri } = await Print.printToFileAsync({ html, base64: false });
        const canShare = await Sharing.isAvailableAsync();
        if (canShare) {
          await Sharing.shareAsync(uri, {
            mimeType: 'application/pdf',
            dialogTitle: t('log.export_title'),
            UTI: 'com.adobe.pdf',
          });
        } else {
          await Print.printAsync({ html });
        }
      }
    } catch {
      Alert.alert(t('log.export_btn'), t('log.export_error'));
    } finally {
      setIsExporting(false);
    }
  };

  const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: colors.background },
    header: {
      paddingTop: topPad + 12, paddingHorizontal: 20, paddingBottom: 16,
      borderBottomWidth: 1, borderBottomColor: colors.border,
      flexDirection: rowDir, alignItems: 'center', gap: 12,
    },
    headerLeft:   { flex: 1 },
    headerTitle:  { fontSize: fs(22), fontFamily: 'Inter_700Bold', color: colors.foreground },
    headerSub:    { fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 2 },
    addBtn:       { width: 40, height: 40, borderRadius: 20, backgroundColor: colors.primary, alignItems: 'center', justifyContent: 'center' },
    exportBtn:    { width: 40, height: 40, borderRadius: 20, backgroundColor: colors.muted, alignItems: 'center', justifyContent: 'center' },
    listContent:  { padding: 16, paddingBottom: bottomPad + 80 },
    countText:    { fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, paddingHorizontal: 16, paddingTop: 12, paddingBottom: 4 },
    emptyWrap:    { alignItems: 'center', justifyContent: 'center', paddingTop: 80, gap: 12 },
    emptyIcon:    { width: 72, height: 72, borderRadius: 36, backgroundColor: colors.muted, alignItems: 'center', justifyContent: 'center' },
    emptyTitle:   { fontSize: fs(17), fontFamily: 'Inter_600SemiBold', color: colors.foreground },
    emptyText:    { fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, textAlign: 'center', paddingHorizontal: 40, lineHeight: 20 },
    emptyBtn:     { backgroundColor: colors.primary, borderRadius: colors.radius, paddingVertical: 12, paddingHorizontal: 24, flexDirection: rowDir, alignItems: 'center', gap: 8 },
    emptyBtnText: { fontSize: fs(15), fontFamily: 'Inter_600SemiBold', color: colors.primaryForeground },
    privacyNote:  { flexDirection: rowDir, alignItems: 'center', gap: 8, backgroundColor: colors.muted, borderRadius: 10, padding: 10, marginHorizontal: 16, marginTop: 8 },
    privacyText:  { flex: 1, fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground },
    selectionBar: {
      position: 'absolute', bottom: 0, left: 0, right: 0,
      paddingBottom: bottomPad + 12, paddingTop: 14, paddingHorizontal: 16,
      backgroundColor: colors.background,
      borderTopWidth: 1, borderTopColor: colors.border,
      flexDirection: rowDir, gap: 10, alignItems: 'center',
    },
    shareSelectedBtn: {
      flex: 1, flexDirection: rowDir, alignItems: 'center', justifyContent: 'center', gap: 8,
      backgroundColor: selectedIds.size > 0 ? colors.primary : colors.primary + '60',
      borderRadius: 12, paddingVertical: 14,
    },
    shareSelectedText: { fontSize: fs(15), fontFamily: 'Inter_600SemiBold', color: colors.primaryForeground },
    cancelSelectionBtn: {
      width: 48, height: 48, borderRadius: 12, backgroundColor: colors.muted,
      alignItems: 'center', justifyContent: 'center', borderWidth: 1, borderColor: colors.border,
    },
    selectHint: { fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, textAlign: 'center', paddingHorizontal: 16, paddingVertical: 6 },
  });

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        {selectionMode ? (
          <Pressable onPress={cancelSelection} hitSlop={12}>
            <Feather name="x" size={22} color={colors.foreground} />
          </Pressable>
        ) : (
          <Pressable onPress={() => router.back()} hitSlop={12}>
            <Feather name={backIcon} size={22} color={colors.foreground} />
          </Pressable>
        )}
        <View style={styles.headerLeft}>
          {selectionMode ? (
            <Text style={styles.headerTitle}>
              {selectedIds.size} {selectedIds.size === 1 ? t('log.entry') : t('log.entries')}
            </Text>
          ) : (
            <>
              <Text style={styles.headerTitle}>{t('log.title')}</Text>
              <Text style={styles.headerSub}>{t('log.subtitle')}</Text>
            </>
          )}
        </View>
        {!selectionMode && encounters.length > 0 && (
          <Pressable style={styles.exportBtn} onPress={handleExport} disabled={isExporting}>
            <Feather name="share" size={18} color={isExporting ? colors.mutedForeground : colors.foreground} />
          </Pressable>
        )}
        {!selectionMode && (
          <Pressable style={styles.addBtn} onPress={navigateToNew}>
            <Feather name="plus" size={22} color="#FFFFFF" />
          </Pressable>
        )}
      </View>

      {encounters.length === 0 ? (
        <View style={styles.emptyWrap}>
          <View style={styles.emptyIcon}>
            <Feather name="clipboard" size={30} color={colors.mutedForeground} />
          </View>
          <Text style={styles.emptyTitle}>{t('log.empty_title')}</Text>
          <Text style={styles.emptyText}>{t('log.empty_desc')}</Text>
          <Pressable style={styles.emptyBtn} onPress={navigateToNew}>
            <Feather name="plus" size={16} color={colors.primaryForeground} />
            <Text style={styles.emptyBtnText}>{t('log.first_btn')}</Text>
          </Pressable>
        </View>
      ) : (
        <>
          {selectionMode ? (
            <Text style={styles.selectHint}>{t('log.select_hint')}</Text>
          ) : (
            <View style={styles.privacyNote}>
              <Feather name="lock" size={13} color={colors.mutedForeground} />
              <Text style={styles.privacyText}>
                {encounters.length} {encounters.length === 1 ? t('log.entry') : t('log.entries')} · {t('log.stored_device')}
              </Text>
            </View>
          )}
          <FlatList
            data={encounters}
            keyExtractor={(item) => item.id}
            contentContainerStyle={styles.listContent}
            renderItem={({ item }) => (
              <EncounterCard
                encounter={item}
                onDelete={() => deleteEncounter(item.id)}
                selectionMode={selectionMode}
                selected={selectedIds.has(item.id)}
                onLongPress={() => enterSelectionMode(item.id)}
                onToggleSelect={() => toggleSelect(item.id)}
              />
            )}
            showsVerticalScrollIndicator={false}
          />
        </>
      )}

      {selectionMode && (
        <View style={styles.selectionBar}>
          <Pressable
            style={styles.shareSelectedBtn}
            onPress={handleMultiExportPress}
            disabled={selectedIds.size === 0 || isExporting}
          >
            <Feather name="share" size={16} color={colors.primaryForeground} />
            <Text style={styles.shareSelectedText}>
              {t('log.select_share')} ({selectedIds.size})
            </Text>
          </Pressable>
          <Pressable style={styles.cancelSelectionBtn} onPress={cancelSelection}>
            <Feather name="x" size={20} color={colors.foreground} />
          </Pressable>
        </View>
      )}

      <PasswordModal
        visible={passwordModalVisible}
        onCancel={() => setPasswordModalVisible(false)}
        onShare={doExport}
      />
      <PasswordModal
        visible={multiPasswordModalVisible}
        onCancel={() => setMultiPasswordModalVisible(false)}
        onShare={doMultiExport}
      />
    </View>
  );
}
