import React, { useState } from 'react';
import {
  Alert,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { router } from 'expo-router';
import { Feather } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { EncounterType, useApp } from '@/context/AppContext';
import { useColors } from '@/hooks/useColors';
import { useRTL } from '@/hooks/useRTL';
import { useT } from '@/hooks/useTranslation';

const ENCOUNTER_TYPES: EncounterType[] = [
  'traffic_stop', 'arrest', 'questioning', 'citation', 'search', 'other',
];

export default function NewLogScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;
  const { addEncounter, fs } = useApp();
  const { t } = useT();
  const { rowDir, textStyle } = useRTL();

  const [type, setType] = useState<EncounterType>('traffic_stop');
  const [location, setLocation] = useState('');
  const [officerInfo, setOfficerInfo] = useState('');
  const [description, setDescription] = useState('');
  const [outcome, setOutcome] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    if (!description.trim()) {
      Alert.alert('Required', t('newlog.required_msg'));
      return;
    }
    setSaving(true);
    try {
      await addEncounter({
        date: new Date().toISOString(),
        type,
        location: location.trim(),
        officerInfo: officerInfo.trim(),
        description: description.trim(),
        outcome: outcome.trim(),
      });
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      router.back();
    } catch {
      Alert.alert('Error', t('newlog.error_msg'));
      setSaving(false);
    }
  };

  const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: colors.background },
    header: {
      paddingTop: topPad + 12, paddingHorizontal: 20, paddingBottom: 16,
      borderBottomWidth: 1, borderBottomColor: colors.border,
      flexDirection: rowDir, alignItems: 'center', gap: 12,
    },
    headerTitle: { flex: 1, fontSize: fs(20), fontFamily: 'Inter_700Bold', color: colors.foreground },
    saveBtn: { backgroundColor: colors.primary, borderRadius: 20, paddingVertical: 8, paddingHorizontal: 16, opacity: saving ? 0.6 : 1 },
    saveBtnText: { fontSize: fs(14), fontFamily: 'Inter_600SemiBold', color: colors.primaryForeground },
    scroll: { flex: 1 },
    scrollContent: { padding: 20, paddingBottom: Platform.OS === 'web' ? 34 : 40, flexGrow: 1 },
    sectionLabel: {
      fontSize: fs(13), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground,
      textTransform: 'uppercase', letterSpacing: 0.7, marginBottom: 8, marginTop: 20,
    },
    typeGrid:             { flexDirection: rowDir, flexWrap: 'wrap', gap: 8 },
    typeChip:             { borderRadius: 20, paddingVertical: 8, paddingHorizontal: 14, borderWidth: 1.5, borderColor: colors.border, backgroundColor: colors.card },
    typeChipSelected:     { borderColor: colors.primary, backgroundColor: colors.primary + '14' },
    typeChipText:         { fontSize: fs(13), fontFamily: 'Inter_500Medium', color: colors.mutedForeground },
    typeChipTextSelected: { color: colors.primary, fontFamily: 'Inter_600SemiBold' },
    inputWrap:  { backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1, borderColor: colors.border, marginTop: 4 },
    input:      { fontSize: fs(15), fontFamily: 'Inter_400Regular', color: colors.foreground, padding: 14 },
    textArea:   { minHeight: 100, textAlignVertical: 'top' },
    hint:       { fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 4 },
    legalNote:  { backgroundColor: colors.primary + '0F', borderRadius: colors.radius, padding: 14, marginTop: 24, borderWidth: 1, borderColor: colors.primary + '20', flexDirection: rowDir, gap: 10 },
    legalNoteText: { flex: 1, fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 19 },
  });

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} hitSlop={12}>
          <Feather name="x" size={22} color={colors.foreground} />
        </Pressable>
        <Text style={styles.headerTitle}>{t('newlog.title')}</Text>
        <Pressable style={styles.saveBtn} onPress={handleSave} disabled={saving}>
          <Text style={styles.saveBtnText}>{t('newlog.save')}</Text>
        </Pressable>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent} keyboardShouldPersistTaps="handled">
        {/* Type */}
        <Text style={[styles.sectionLabel, { marginTop: 0 }]}>{t('newlog.type_label')}</Text>
        <View style={styles.typeGrid}>
          {ENCOUNTER_TYPES.map((enc) => (
            <Pressable
              key={enc}
              style={[styles.typeChip, type === enc && styles.typeChipSelected]}
              onPress={() => { setType(enc); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); }}
            >
              <Text style={[styles.typeChipText, type === enc && styles.typeChipTextSelected]}>
                {t(`encounter.${enc}` as any)}
              </Text>
            </Pressable>
          ))}
        </View>

        {/* Location */}
        <Text style={styles.sectionLabel}>{t('newlog.location')}</Text>
        <View style={styles.inputWrap}>
          <TextInput
            style={[styles.input, textStyle]}
            value={location}
            onChangeText={setLocation}
            placeholder={t('newlog.location_ph')}
            placeholderTextColor={colors.mutedForeground}
          />
        </View>

        {/* Officer Info */}
        <Text style={styles.sectionLabel}>{t('newlog.officer')}</Text>
        <View style={styles.inputWrap}>
          <TextInput
            style={[styles.input, textStyle]}
            value={officerInfo}
            onChangeText={setOfficerInfo}
            placeholder={t('newlog.officer_ph')}
            placeholderTextColor={colors.mutedForeground}
          />
        </View>

        {/* Description */}
        <Text style={styles.sectionLabel}>{t('newlog.description')}</Text>
        <View style={styles.inputWrap}>
          <TextInput
            style={[styles.input, styles.textArea, textStyle]}
            value={description}
            onChangeText={setDescription}
            placeholder={t('newlog.description_ph')}
            placeholderTextColor={colors.mutedForeground}
            multiline
          />
        </View>
        <Text style={styles.hint}>{t('newlog.description_hint')}</Text>

        {/* Outcome */}
        <Text style={styles.sectionLabel}>{t('newlog.outcome')}</Text>
        <View style={styles.inputWrap}>
          <TextInput
            style={[styles.input, styles.textArea, textStyle]}
            value={outcome}
            onChangeText={setOutcome}
            placeholder={t('newlog.outcome_ph')}
            placeholderTextColor={colors.mutedForeground}
            multiline
          />
        </View>

        {/* Legal note */}
        <View style={styles.legalNote}>
          <Feather name="lock" size={16} color={colors.primary} />
          <Text style={styles.legalNoteText}>{t('newlog.legal_note')}</Text>
        </View>
      </ScrollView>
    </View>
  );
}
