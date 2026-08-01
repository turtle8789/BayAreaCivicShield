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
import * as Print from 'expo-print';
import * as Sharing from 'expo-sharing';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Encounter, ENCOUNTER_TYPE_LABELS, useApp } from '@/context/AppContext';
import { useColors } from '@/hooks/useColors';
import { useRTL } from '@/hooks/useRTL';
import { useT } from '@/hooks/useTranslation';

function EncounterCard({ encounter, onDelete }: { encounter: Encounter; onDelete: () => void }) {
  const colors = useColors();
  const { fs } = useApp();
  const { t } = useT();
  const { rowDir, textStyle } = useRTL();
  const [expanded, setExpanded] = useState(false);

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

  // Translate encounter type using i18n key
  const typeKey = `encounter.${encounter.type}` as any;

  const styles = StyleSheet.create({
    card: {
      backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1,
      borderColor: colors.border, marginBottom: 10, overflow: 'hidden',
    },
    cardHeader:     { flexDirection: rowDir, alignItems: 'center', padding: 14, gap: 10 },
    typeDot:        { width: 10, height: 10, borderRadius: 5, backgroundColor: colors.primary },
    typeLabel:      { fontSize: fs(15), fontFamily: 'Inter_600SemiBold', color: colors.foreground },
    dateText:       { fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground },
    expandedSection:{ borderTopWidth: 1, borderTopColor: colors.border, padding: 14, gap: 10 },
    fieldLabel:     { fontSize: fs(11), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase', letterSpacing: 0.6, marginBottom: 2 },
    fieldValue:     { fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.foreground, lineHeight: 20, ...textStyle },
    deleteBtn:      { flex: 1, flexDirection: rowDir, alignItems: 'center', justifyContent: 'center', gap: 6, borderRadius: 10, paddingVertical: 9, backgroundColor: colors.destructive + '12', borderWidth: 1, borderColor: colors.destructive + '25' },
  });

  return (
    <View style={styles.card}>
      <Pressable style={styles.cardHeader} onPress={() => setExpanded(!expanded)}>
        <View style={styles.typeDot} />
        <View style={{ flex: 1 }}>
          <Text style={styles.typeLabel}>{t(typeKey)}</Text>
          <View style={{ flexDirection: rowDir, gap: 6, marginTop: 2 }}>
            <Text style={styles.dateText}>{formattedDate} {t('log.at')} {formattedTime}</Text>
            {encounter.location ? <Text style={styles.dateText}>· {encounter.location}</Text> : null}
          </View>
        </View>
        <Feather name={expanded ? 'chevron-up' : 'chevron-down'} size={18} color={colors.mutedForeground} />
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
          <View style={{ flexDirection: rowDir, marginTop: 4 }}>
            <Pressable style={styles.deleteBtn} onPress={handleDelete}>
              <Feather name="trash-2" size={14} color={colors.destructive} />
              <Text style={{ fontSize: fs(13), fontFamily: 'Inter_500Medium', color: colors.destructive }}>
                {t('log.delete_btn')}
              </Text>
            </Pressable>
          </View>
        </View>
      )}
    </View>
  );
}

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

export default function LogListScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;
  const bottomPad = Platform.OS === 'web' ? 34 : insets.bottom;
  const { encounters, deleteEncounter, fs } = useApp();
  const { t } = useT();
  const { rowDir, backIcon } = useRTL();
  const [isExporting, setIsExporting] = useState(false);

  const navigateToNew = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    router.push('/new-log');
  };

  const handleExport = async () => {
    if (encounters.length === 0) {
      Alert.alert(t('log.export_btn'), t('log.export_empty'));
      return;
    }
    if (isExporting) return;

    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    setIsExporting(true);
    try {
      const html = buildEncounterHtml(encounters, t('log.export_title'));
      const { uri } = await Print.printToFileAsync({ html, base64: false });

      const canShare = await Sharing.isAvailableAsync();
      if (canShare) {
        await Sharing.shareAsync(uri, {
          mimeType: 'application/pdf',
          dialogTitle: t('log.export_title'),
          UTI: 'com.adobe.pdf',
        });
      } else {
        // Web fallback: open the print dialog
        await Print.printAsync({ html });
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
    listContent:  { padding: 16, paddingBottom: bottomPad + 24 },
    countText:    { fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, paddingHorizontal: 16, paddingTop: 12, paddingBottom: 4 },
    emptyWrap:    { alignItems: 'center', justifyContent: 'center', paddingTop: 80, gap: 12 },
    emptyIcon:    { width: 72, height: 72, borderRadius: 36, backgroundColor: colors.muted, alignItems: 'center', justifyContent: 'center' },
    emptyTitle:   { fontSize: fs(17), fontFamily: 'Inter_600SemiBold', color: colors.foreground },
    emptyText:    { fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, textAlign: 'center', paddingHorizontal: 40, lineHeight: 20 },
    emptyBtn:     { backgroundColor: colors.primary, borderRadius: colors.radius, paddingVertical: 12, paddingHorizontal: 24, flexDirection: rowDir, alignItems: 'center', gap: 8 },
    emptyBtnText: { fontSize: fs(15), fontFamily: 'Inter_600SemiBold', color: colors.primaryForeground },
    privacyNote:  { flexDirection: rowDir, alignItems: 'center', gap: 8, backgroundColor: colors.muted, borderRadius: 10, padding: 10, marginHorizontal: 16, marginTop: 8 },
    privacyText:  { flex: 1, fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground },
  });

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} hitSlop={12}>
          <Feather name={backIcon} size={22} color={colors.foreground} />
        </Pressable>
        <View style={styles.headerLeft}>
          <Text style={styles.headerTitle}>{t('log.title')}</Text>
          <Text style={styles.headerSub}>{t('log.subtitle')}</Text>
        </View>
        {encounters.length > 0 && (
          <Pressable style={styles.exportBtn} onPress={handleExport} disabled={isExporting}>
            <Feather name="share" size={18} color={isExporting ? colors.mutedForeground : colors.foreground} />
          </Pressable>
        )}
        <Pressable style={styles.addBtn} onPress={navigateToNew}>
          <Feather name="plus" size={22} color="#FFFFFF" />
        </Pressable>
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
          <View style={styles.privacyNote}>
            <Feather name="lock" size={13} color={colors.mutedForeground} />
            <Text style={styles.privacyText}>
              {encounters.length} {encounters.length === 1 ? t('log.entry') : t('log.entries')} · {t('log.stored_device')}
            </Text>
          </View>
          <FlatList
            data={encounters}
            keyExtractor={(item) => item.id}
            contentContainerStyle={styles.listContent}
            renderItem={({ item }) => (
              <EncounterCard encounter={item} onDelete={() => deleteEncounter(item.id)} />
            )}
            showsVerticalScrollIndicator={false}
          />
        </>
      )}
    </View>
  );
}
