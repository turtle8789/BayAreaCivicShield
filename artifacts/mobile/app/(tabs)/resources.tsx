import React, { useState } from 'react';
import {
  Alert,
  Linking,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { Feather } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { CATEGORY_COLORS, CATEGORY_LABELS, CRISIS_HOTLINES, Hotline } from '@/constants/crisis-hotlines';
import { LEGAL_RESOURCES, TYPE_LABELS } from '@/constants/legal-resources';
import { useColors } from '@/hooks/useColors';

type Tab = 'hotlines' | 'resources';

// ─── Hotline Card ─────────────────────────────────────────────────────────────

function HotlineCard({ hotline }: { hotline: Hotline }) {
  const colors = useColors();
  const categoryColor = CATEGORY_COLORS[hotline.category];

  const callNumber = async () => {
    const url = `tel:${hotline.number.replace(/[^0-9+]/g, '')}`;
    const supported = await Linking.canOpenURL(url);
    if (supported) {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      await Linking.openURL(url);
    } else if (Platform.OS === 'web') {
      Alert.alert('Call', `Please dial: ${hotline.number}`);
    }
  };

  const styles = StyleSheet.create({
    card: {
      backgroundColor: colors.card,
      borderRadius: colors.radius,
      padding: 14,
      marginBottom: 10,
      borderWidth: 1,
      borderColor: colors.border,
    },
    topRow: {
      flexDirection: 'row',
      alignItems: 'flex-start',
      gap: 10,
      marginBottom: 8,
    },
    badge: {
      paddingHorizontal: 8,
      paddingVertical: 3,
      borderRadius: 20,
    },
    badgeText: {
      fontSize: 11,
      fontFamily: 'Inter_600SemiBold',
      color: '#FFFFFF',
    },
    name: {
      flex: 1,
      fontSize: 15,
      fontFamily: 'Inter_600SemiBold',
      color: colors.foreground,
    },
    available: {
      fontSize: 11,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
    },
    description: {
      fontSize: 13,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
      lineHeight: 18,
      marginBottom: 10,
    },
    callBtn: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 6,
      backgroundColor: categoryColor + '14',
      borderRadius: 10,
      paddingVertical: 10,
      paddingHorizontal: 14,
      alignSelf: 'flex-start',
    },
    callNumber: {
      fontSize: 15,
      fontFamily: 'Inter_700Bold',
      color: categoryColor,
    },
  });

  return (
    <View style={styles.card}>
      <View style={styles.topRow}>
        <View style={[styles.badge, { backgroundColor: categoryColor }]}>
          <Text style={styles.badgeText}>{CATEGORY_LABELS[hotline.category]}</Text>
        </View>
        <Text style={styles.available}>{hotline.available}</Text>
      </View>
      <Text style={styles.name}>{hotline.name}</Text>
      <Text style={styles.description}>{hotline.description}</Text>
      <Pressable style={styles.callBtn} onPress={callNumber}>
        <Feather name="phone" size={15} color={categoryColor} />
        <Text style={styles.callNumber}>{hotline.number}</Text>
      </Pressable>
    </View>
  );
}

// ─── Legal Resource Card ──────────────────────────────────────────────────────

function ResourceCard({ resource }: { resource: typeof LEGAL_RESOURCES[0] }) {
  const colors = useColors();

  const callPhone = async () => {
    const url = `tel:${resource.phone.replace(/[^0-9+]/g, '')}`;
    const supported = await Linking.canOpenURL(url);
    if (supported) {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      await Linking.openURL(url);
    } else {
      Alert.alert('Call', `Please dial: ${resource.phone}`);
    }
  };

  const openWebsite = async () => {
    const url = `https://${resource.website}`;
    const supported = await Linking.canOpenURL(url);
    if (supported) {
      await Linking.openURL(url);
    }
  };

  const styles = StyleSheet.create({
    card: {
      backgroundColor: colors.card,
      borderRadius: colors.radius,
      padding: 14,
      marginBottom: 10,
      borderWidth: 1,
      borderColor: colors.border,
    },
    topRow: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 8,
      marginBottom: 6,
    },
    typeBadge: {
      paddingHorizontal: 8,
      paddingVertical: 3,
      borderRadius: 20,
      backgroundColor: colors.primary + '18',
    },
    typeBadgeText: {
      fontSize: 11,
      fontFamily: 'Inter_500Medium',
      color: colors.primary,
    },
    region: {
      fontSize: 12,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
    },
    name: {
      fontSize: 16,
      fontFamily: 'Inter_600SemiBold',
      color: colors.foreground,
      marginBottom: 4,
    },
    description: {
      fontSize: 13,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
      lineHeight: 18,
      marginBottom: 8,
    },
    servesWrap: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      gap: 6,
      marginBottom: 10,
    },
    serveTag: {
      backgroundColor: colors.muted,
      borderRadius: 6,
      paddingHorizontal: 8,
      paddingVertical: 3,
    },
    serveTagText: {
      fontSize: 11,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
    },
    actionRow: {
      flexDirection: 'row',
      gap: 8,
    },
    actionBtn: {
      flex: 1,
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 6,
      borderRadius: 10,
      paddingVertical: 10,
      borderWidth: 1,
    },
    callBtn: {
      backgroundColor: colors.primary + '0F',
      borderColor: colors.primary + '30',
    },
    webBtn: {
      backgroundColor: colors.muted,
      borderColor: colors.border,
    },
    callBtnText: {
      fontSize: 13,
      fontFamily: 'Inter_500Medium',
      color: colors.primary,
    },
    webBtnText: {
      fontSize: 13,
      fontFamily: 'Inter_500Medium',
      color: colors.mutedForeground,
    },
  });

  return (
    <View style={styles.card}>
      <View style={styles.topRow}>
        <View style={styles.typeBadge}>
          <Text style={styles.typeBadgeText}>{TYPE_LABELS[resource.type]}</Text>
        </View>
        <Text style={styles.region}>{resource.region}</Text>
      </View>
      <Text style={styles.name}>{resource.name}</Text>
      <Text style={styles.description}>{resource.description}</Text>
      <View style={styles.servesWrap}>
        {resource.serves.map((s) => (
          <View key={s} style={styles.serveTag}>
            <Text style={styles.serveTagText}>{s}</Text>
          </View>
        ))}
      </View>
      <View style={styles.actionRow}>
        <Pressable style={[styles.actionBtn, styles.callBtn]} onPress={callPhone}>
          <Feather name="phone" size={14} color={colors.primary} />
          <Text style={styles.callBtnText}>Call</Text>
        </Pressable>
        <Pressable style={[styles.actionBtn, styles.webBtn]} onPress={openWebsite}>
          <Feather name="globe" size={14} color={colors.mutedForeground} />
          <Text style={styles.webBtnText}>Website</Text>
        </Pressable>
      </View>
    </View>
  );
}

// ─── Main Screen ──────────────────────────────────────────────────────────────

export default function ResourcesScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;
  const [activeTab, setActiveTab] = useState<Tab>('hotlines');

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: colors.background,
    },
    header: {
      paddingTop: topPad + 12,
      paddingHorizontal: 20,
      paddingBottom: 0,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
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
      marginBottom: 12,
    },
    tabRow: {
      flexDirection: 'row',
      gap: 0,
    },
    tabBtn: {
      flex: 1,
      paddingVertical: 10,
      alignItems: 'center',
      borderBottomWidth: 2,
      borderBottomColor: 'transparent',
    },
    tabBtnActive: {
      borderBottomColor: colors.primary,
    },
    tabBtnText: {
      fontSize: 14,
      fontFamily: 'Inter_500Medium',
      color: colors.mutedForeground,
    },
    tabBtnTextActive: {
      color: colors.primary,
      fontFamily: 'Inter_600SemiBold',
    },
    scroll: { flex: 1 },
    scrollContent: {
      padding: 16,
      paddingBottom: Platform.OS === 'web' ? 34 : 24,
    },
    emergencyCard: {
      backgroundColor: '#E05252',
      borderRadius: colors.radius,
      padding: 16,
      marginBottom: 16,
      flexDirection: 'row',
      alignItems: 'center',
      gap: 12,
    },
    emergencyText: {
      flex: 1,
      fontSize: 15,
      fontFamily: 'Inter_600SemiBold',
      color: '#FFFFFF',
    },
    emergencyNumber: {
      fontSize: 22,
      fontFamily: 'Inter_700Bold',
      color: '#FFFFFF',
    },
  });

  const callEmergency = async () => {
    const url = 'tel:911';
    const supported = await Linking.canOpenURL(url);
    if (supported) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
      await Linking.openURL(url);
    } else {
      Alert.alert('Emergency', 'Call 911 immediately.');
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Resources</Text>
        <Text style={styles.headerSub}>Hotlines, legal aid, and support</Text>
        <View style={styles.tabRow}>
          <Pressable
            style={[styles.tabBtn, activeTab === 'hotlines' && styles.tabBtnActive]}
            onPress={() => setActiveTab('hotlines')}
          >
            <Text style={[styles.tabBtnText, activeTab === 'hotlines' && styles.tabBtnTextActive]}>
              Crisis Hotlines
            </Text>
          </Pressable>
          <Pressable
            style={[styles.tabBtn, activeTab === 'resources' && styles.tabBtnActive]}
            onPress={() => setActiveTab('resources')}
          >
            <Text style={[styles.tabBtnText, activeTab === 'resources' && styles.tabBtnTextActive]}>
              Legal Aid
            </Text>
          </Pressable>
        </View>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Emergency 911 always visible */}
        <Pressable style={styles.emergencyCard} onPress={callEmergency}>
          <Feather name="alert-triangle" size={22} color="#FFFFFF" />
          <Text style={styles.emergencyText}>Emergency Services</Text>
          <Text style={styles.emergencyNumber}>911</Text>
        </Pressable>

        {activeTab === 'hotlines'
          ? CRISIS_HOTLINES.filter((h) => h.id !== '911').map((hotline) => (
              <HotlineCard key={hotline.id} hotline={hotline} />
            ))
          : LEGAL_RESOURCES.map((resource) => (
              <ResourceCard key={resource.id} resource={resource} />
            ))}
      </ScrollView>
    </View>
  );
}
