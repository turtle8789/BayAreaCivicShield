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
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Encounter, useApp } from '@/context/AppContext';
import { useColors } from '@/hooks/useColors';
import { useT } from '@/hooks/useTranslation';

function EncounterCard({ encounter, onDelete }: { encounter: Encounter; onDelete: () => void }) {
  const colors = useColors();
  const { fs } = useApp();
  const { t } = useT();
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
    cardHeader:     { flexDirection: 'row', alignItems: 'center', padding: 14, gap: 10 },
    typeDot:        { width: 10, height: 10, borderRadius: 5, backgroundColor: colors.primary },
    typeLabel:      { fontSize: fs(15), fontFamily: 'Inter_600SemiBold', color: colors.foreground },
    dateText:       { fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground },
    expandedSection:{ borderTopWidth: 1, borderTopColor: colors.border, padding: 14, gap: 10 },
    fieldLabel:     { fontSize: fs(11), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase', letterSpacing: 0.6, marginBottom: 2 },
    fieldValue:     { fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.foreground, lineHeight: 20 },
    deleteBtn:      { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6, borderRadius: 10, paddingVertical: 9, backgroundColor: colors.destructive + '12', borderWidth: 1, borderColor: colors.destructive + '25' },
  });

  return (
    <View style={styles.card}>
      <Pressable style={styles.cardHeader} onPress={() => setExpanded(!expanded)}>
        <View style={styles.typeDot} />
        <View style={{ flex: 1 }}>
          <Text style={styles.typeLabel}>{t(typeKey)}</Text>
          <View style={{ flexDirection: 'row', gap: 6, marginTop: 2 }}>
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
          <View style={{ flexDirection: 'row', marginTop: 4 }}>
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

export default function LogListScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;
  const bottomPad = Platform.OS === 'web' ? 34 : insets.bottom;
  const { encounters, deleteEncounter, fs } = useApp();
  const { t } = useT();

  const navigateToNew = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    router.push('/new-log');
  };

  const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: colors.background },
    header: {
      paddingTop: topPad + 12, paddingHorizontal: 20, paddingBottom: 16,
      borderBottomWidth: 1, borderBottomColor: colors.border,
      flexDirection: 'row', alignItems: 'center', gap: 12,
    },
    headerLeft:   { flex: 1 },
    headerTitle:  { fontSize: fs(22), fontFamily: 'Inter_700Bold', color: colors.foreground },
    headerSub:    { fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 2 },
    addBtn:       { width: 40, height: 40, borderRadius: 20, backgroundColor: colors.primary, alignItems: 'center', justifyContent: 'center' },
    listContent:  { padding: 16, paddingBottom: bottomPad + 24 },
    countText:    { fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, paddingHorizontal: 16, paddingTop: 12, paddingBottom: 4 },
    emptyWrap:    { alignItems: 'center', justifyContent: 'center', paddingTop: 80, gap: 12 },
    emptyIcon:    { width: 72, height: 72, borderRadius: 36, backgroundColor: colors.muted, alignItems: 'center', justifyContent: 'center' },
    emptyTitle:   { fontSize: fs(17), fontFamily: 'Inter_600SemiBold', color: colors.foreground },
    emptyText:    { fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, textAlign: 'center', paddingHorizontal: 40, lineHeight: 20 },
    emptyBtn:     { backgroundColor: colors.primary, borderRadius: colors.radius, paddingVertical: 12, paddingHorizontal: 24, flexDirection: 'row', alignItems: 'center', gap: 8 },
    emptyBtnText: { fontSize: fs(15), fontFamily: 'Inter_600SemiBold', color: colors.primaryForeground },
    privacyNote:  { flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: colors.muted, borderRadius: 10, padding: 10, marginHorizontal: 16, marginTop: 8 },
    privacyText:  { flex: 1, fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground },
  });

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} hitSlop={12}>
          <Feather name="arrow-left" size={22} color={colors.foreground} />
        </Pressable>
        <View style={styles.headerLeft}>
          <Text style={styles.headerTitle}>{t('log.title')}</Text>
          <Text style={styles.headerSub}>{t('log.subtitle')}</Text>
        </View>
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
