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
import { Encounter, ENCOUNTER_TYPE_LABELS, useApp } from '@/context/AppContext';
import { useColors } from '@/hooks/useColors';

function EncounterCard({ encounter, onDelete }: { encounter: Encounter; onDelete: () => void }) {
  const colors = useColors();
  const [expanded, setExpanded] = useState(false);

  const date = new Date(encounter.date);
  const formattedDate = date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
  const formattedTime = date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });

  const styles = StyleSheet.create({
    card: {
      backgroundColor: colors.card,
      borderRadius: colors.radius,
      borderWidth: 1,
      borderColor: colors.border,
      marginBottom: 10,
      overflow: 'hidden',
    },
    cardHeader: {
      flexDirection: 'row',
      alignItems: 'center',
      padding: 14,
      gap: 10,
    },
    typeDot: {
      width: 10,
      height: 10,
      borderRadius: 5,
      backgroundColor: colors.primary,
    },
    headerText: {
      flex: 1,
    },
    typeLabel: {
      fontSize: 15,
      fontFamily: 'Inter_600SemiBold',
      color: colors.foreground,
    },
    dateRow: {
      flexDirection: 'row',
      gap: 6,
      marginTop: 2,
    },
    dateText: {
      fontSize: 12,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
    },
    location: {
      fontSize: 12,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
    },
    expandedSection: {
      borderTopWidth: 1,
      borderTopColor: colors.border,
      padding: 14,
      gap: 10,
    },
    fieldLabel: {
      fontSize: 11,
      fontFamily: 'Inter_600SemiBold',
      color: colors.mutedForeground,
      textTransform: 'uppercase',
      letterSpacing: 0.6,
      marginBottom: 2,
    },
    fieldValue: {
      fontSize: 14,
      fontFamily: 'Inter_400Regular',
      color: colors.foreground,
      lineHeight: 20,
    },
    actionRow: {
      flexDirection: 'row',
      gap: 8,
      marginTop: 4,
    },
    deleteBtn: {
      flex: 1,
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 6,
      borderRadius: 10,
      paddingVertical: 9,
      backgroundColor: colors.destructive + '12',
      borderWidth: 1,
      borderColor: colors.destructive + '25',
    },
    deleteBtnText: {
      fontSize: 13,
      fontFamily: 'Inter_500Medium',
      color: colors.destructive,
    },
  });

  const handleDelete = () => {
    Alert.alert(
      'Delete Encounter',
      'Are you sure you want to delete this log entry?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: () => {
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
            onDelete();
          },
        },
      ],
    );
  };

  return (
    <View style={styles.card}>
      <Pressable style={styles.cardHeader} onPress={() => setExpanded(!expanded)}>
        <View style={styles.typeDot} />
        <View style={styles.headerText}>
          <Text style={styles.typeLabel}>{ENCOUNTER_TYPE_LABELS[encounter.type]}</Text>
          <View style={styles.dateRow}>
            <Text style={styles.dateText}>{formattedDate} at {formattedTime}</Text>
            {encounter.location ? <Text style={styles.dateText}>· {encounter.location}</Text> : null}
          </View>
        </View>
        <Feather name={expanded ? 'chevron-up' : 'chevron-down'} size={18} color={colors.mutedForeground} />
      </Pressable>

      {expanded && (
        <View style={styles.expandedSection}>
          {encounter.officerInfo ? (
            <View>
              <Text style={styles.fieldLabel}>Officer Info</Text>
              <Text style={styles.fieldValue}>{encounter.officerInfo}</Text>
            </View>
          ) : null}

          {encounter.description ? (
            <View>
              <Text style={styles.fieldLabel}>Description</Text>
              <Text style={styles.fieldValue}>{encounter.description}</Text>
            </View>
          ) : null}

          {encounter.outcome ? (
            <View>
              <Text style={styles.fieldLabel}>Outcome</Text>
              <Text style={styles.fieldValue}>{encounter.outcome}</Text>
            </View>
          ) : null}

          <View style={styles.actionRow}>
            <Pressable style={styles.deleteBtn} onPress={handleDelete}>
              <Feather name="trash-2" size={14} color={colors.destructive} />
              <Text style={styles.deleteBtnText}>Delete</Text>
            </Pressable>
          </View>
        </View>
      )}
    </View>
  );
}

export default function LogScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;
  const bottomPad = Platform.OS === 'web' ? 34 : insets.bottom;
  const { encounters, deleteEncounter } = useApp();

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
      alignItems: 'flex-end',
      justifyContent: 'space-between',
    },
    headerLeft: {
      flex: 1,
    },
    headerTitle: {
      fontSize: 22,
      fontFamily: 'Inter_700Bold',
      color: colors.foreground,
    },
    headerSub: {
      fontSize: 13,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
      marginTop: 2,
    },
    addBtn: {
      width: 40,
      height: 40,
      borderRadius: 20,
      backgroundColor: colors.primary,
      alignItems: 'center',
      justifyContent: 'center',
    },
    listContent: {
      padding: 16,
      paddingBottom: bottomPad + 16,
    },
    emptyWrap: {
      alignItems: 'center',
      justifyContent: 'center',
      paddingTop: 80,
      gap: 12,
    },
    emptyIcon: {
      width: 72,
      height: 72,
      borderRadius: 36,
      backgroundColor: colors.muted,
      alignItems: 'center',
      justifyContent: 'center',
    },
    emptyTitle: {
      fontSize: 17,
      fontFamily: 'Inter_600SemiBold',
      color: colors.foreground,
    },
    emptyText: {
      fontSize: 14,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
      textAlign: 'center',
      paddingHorizontal: 40,
      lineHeight: 20,
    },
    emptyBtn: {
      backgroundColor: colors.primary,
      borderRadius: colors.radius,
      paddingVertical: 12,
      paddingHorizontal: 24,
      flexDirection: 'row',
      alignItems: 'center',
      gap: 8,
    },
    emptyBtnText: {
      fontSize: 15,
      fontFamily: 'Inter_600SemiBold',
      color: colors.primaryForeground,
    },
    countText: {
      fontSize: 13,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
      paddingHorizontal: 16,
      paddingTop: 12,
      paddingBottom: 4,
    },
  });

  const navigateToNew = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    router.push('/new-log');
  };

  if (encounters.length === 0) {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <View style={styles.headerLeft}>
            <Text style={styles.headerTitle}>Encounter Log</Text>
            <Text style={styles.headerSub}>Document police interactions</Text>
          </View>
          <Pressable style={styles.addBtn} onPress={navigateToNew}>
            <Feather name="plus" size={22} color="#FFFFFF" />
          </Pressable>
        </View>
        <View style={styles.emptyWrap}>
          <View style={styles.emptyIcon}>
            <Feather name="clipboard" size={30} color={colors.mutedForeground} />
          </View>
          <Text style={styles.emptyTitle}>No encounters logged</Text>
          <Text style={styles.emptyText}>
            Document police interactions to protect yourself and your community. All records stay on your device.
          </Text>
          <Pressable style={styles.emptyBtn} onPress={navigateToNew}>
            <Feather name="plus" size={16} color={colors.primaryForeground} />
            <Text style={styles.emptyBtnText}>Log First Encounter</Text>
          </Pressable>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Text style={styles.headerTitle}>Encounter Log</Text>
          <Text style={styles.headerSub}>Document police interactions</Text>
        </View>
        <Pressable style={styles.addBtn} onPress={navigateToNew}>
          <Feather name="plus" size={22} color="#FFFFFF" />
        </Pressable>
      </View>

      <Text style={styles.countText}>{encounters.length} {encounters.length === 1 ? 'entry' : 'entries'}</Text>

      <FlatList
        data={encounters}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContent}
        renderItem={({ item }) => (
          <EncounterCard
            encounter={item}
            onDelete={() => deleteEncounter(item.id)}
          />
        )}
        scrollEnabled={encounters.length > 0}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
}
