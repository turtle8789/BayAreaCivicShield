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
import { EncounterType, ENCOUNTER_TYPE_LABELS, useApp } from '@/context/AppContext';
import { useColors } from '@/hooks/useColors';

const ENCOUNTER_TYPES: EncounterType[] = [
  'traffic_stop',
  'arrest',
  'questioning',
  'citation',
  'search',
  'other',
];

export default function NewLogScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;
  const { addEncounter } = useApp();

  const [type, setType] = useState<EncounterType>('traffic_stop');
  const [location, setLocation] = useState('');
  const [officerInfo, setOfficerInfo] = useState('');
  const [description, setDescription] = useState('');
  const [outcome, setOutcome] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    if (!description.trim()) {
      Alert.alert('Required', 'Please add a description of the encounter.');
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
      Alert.alert('Error', 'Failed to save encounter. Please try again.');
      setSaving(false);
    }
  };

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: colors.background,
    },
    header: {
      paddingTop: topPad + 12,
      paddingHorizontal: 20,
      paddingBottom: 16,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
      flexDirection: 'row',
      alignItems: 'center',
      gap: 12,
    },
    headerTitle: {
      flex: 1,
      fontSize: 20,
      fontFamily: 'Inter_700Bold',
      color: colors.foreground,
    },
    saveBtn: {
      backgroundColor: colors.primary,
      borderRadius: 20,
      paddingVertical: 8,
      paddingHorizontal: 16,
      opacity: saving ? 0.6 : 1,
    },
    saveBtnText: {
      fontSize: 14,
      fontFamily: 'Inter_600SemiBold',
      color: colors.primaryForeground,
    },
    scroll: { flex: 1 },
    scrollContent: {
      padding: 20,
      paddingBottom: Platform.OS === 'web' ? 34 : 40,
    },
    sectionLabel: {
      fontSize: 13,
      fontFamily: 'Inter_600SemiBold',
      color: colors.mutedForeground,
      textTransform: 'uppercase',
      letterSpacing: 0.7,
      marginBottom: 8,
      marginTop: 20,
    },
    typeGrid: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      gap: 8,
    },
    typeChip: {
      borderRadius: 20,
      paddingVertical: 8,
      paddingHorizontal: 14,
      borderWidth: 1.5,
      borderColor: colors.border,
      backgroundColor: colors.card,
    },
    typeChipSelected: {
      borderColor: colors.primary,
      backgroundColor: colors.primary + '14',
    },
    typeChipText: {
      fontSize: 13,
      fontFamily: 'Inter_500Medium',
      color: colors.mutedForeground,
    },
    typeChipTextSelected: {
      color: colors.primary,
      fontFamily: 'Inter_600SemiBold',
    },
    inputWrap: {
      backgroundColor: colors.card,
      borderRadius: colors.radius,
      borderWidth: 1,
      borderColor: colors.border,
      marginTop: 4,
    },
    input: {
      fontSize: 15,
      fontFamily: 'Inter_400Regular',
      color: colors.foreground,
      padding: 14,
    },
    textArea: {
      minHeight: 100,
      textAlignVertical: 'top',
    },
    hint: {
      fontSize: 12,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
      marginTop: 4,
    },
    legalNote: {
      backgroundColor: colors.primary + '0F',
      borderRadius: colors.radius,
      padding: 14,
      marginTop: 24,
      borderWidth: 1,
      borderColor: colors.primary + '20',
      flexDirection: 'row',
      gap: 10,
    },
    legalNoteText: {
      flex: 1,
      fontSize: 13,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
      lineHeight: 19,
    },
  });

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} hitSlop={12}>
          <Feather name="x" size={22} color={colors.foreground} />
        </Pressable>
        <Text style={styles.headerTitle}>Log Encounter</Text>
        <Pressable style={styles.saveBtn} onPress={handleSave} disabled={saving}>
          <Text style={styles.saveBtnText}>Save</Text>
        </Pressable>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent} keyboardShouldPersistTaps="handled">
        {/* Type */}
        <Text style={[styles.sectionLabel, { marginTop: 0 }]}>Encounter Type</Text>
        <View style={styles.typeGrid}>
          {ENCOUNTER_TYPES.map((t) => (
            <Pressable
              key={t}
              style={[styles.typeChip, type === t && styles.typeChipSelected]}
              onPress={() => {
                setType(t);
                Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
              }}
            >
              <Text style={[styles.typeChipText, type === t && styles.typeChipTextSelected]}>
                {ENCOUNTER_TYPE_LABELS[t]}
              </Text>
            </Pressable>
          ))}
        </View>

        {/* Location */}
        <Text style={styles.sectionLabel}>Location</Text>
        <View style={styles.inputWrap}>
          <TextInput
            style={styles.input}
            value={location}
            onChangeText={setLocation}
            placeholder="Where did this occur?"
            placeholderTextColor={colors.mutedForeground}
          />
        </View>

        {/* Officer Info */}
        <Text style={styles.sectionLabel}>Officer Information</Text>
        <View style={styles.inputWrap}>
          <TextInput
            style={styles.input}
            value={officerInfo}
            onChangeText={setOfficerInfo}
            placeholder="Badge number, name, unit (if known)"
            placeholderTextColor={colors.mutedForeground}
          />
        </View>

        {/* Description */}
        <Text style={styles.sectionLabel}>Description *</Text>
        <View style={styles.inputWrap}>
          <TextInput
            style={[styles.input, styles.textArea]}
            value={description}
            onChangeText={setDescription}
            placeholder="Describe what happened in detail..."
            placeholderTextColor={colors.mutedForeground}
            multiline
          />
        </View>
        <Text style={styles.hint}>Include as many details as you remember — time, circumstances, what was said.</Text>

        {/* Outcome */}
        <Text style={styles.sectionLabel}>Outcome</Text>
        <View style={styles.inputWrap}>
          <TextInput
            style={[styles.input, styles.textArea]}
            value={outcome}
            onChangeText={setOutcome}
            placeholder="What was the result? Any citations, arrests, searches..."
            placeholderTextColor={colors.mutedForeground}
            multiline
          />
        </View>

        {/* Legal note */}
        <View style={styles.legalNote}>
          <Feather name="lock" size={16} color={colors.primary} />
          <Text style={styles.legalNoteText}>
            This record is stored only on your device and is never shared. It can be useful if you need to file a complaint or consult a lawyer.
          </Text>
        </View>
      </ScrollView>
    </View>
  );
}
