import React, { useState } from 'react';
import {
  Alert,
  Linking,
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
import * as WebBrowser from 'expo-web-browser';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import {
  HUB_CATEGORIES,
  HUB_DISCLAIMER,
  HUB_RESOURCES,
  HubCategory,
} from '@/constants/resource-hub-data';
import { useApp } from '@/context/AppContext';
import { useColors } from '@/hooks/useColors';

async function openUrl(url: string) {
  try {
    if (Platform.OS === 'web') {
      window.open(url, '_blank', 'noopener');
    } else {
      await WebBrowser.openBrowserAsync(url, {
        presentationStyle: WebBrowser.WebBrowserPresentationStyle.FULL_SCREEN,
      });
    }
  } catch {
    Alert.alert('Could not open link', 'Copy and paste the URL in your browser:\n' + url);
  }
}

function callNumber(phone: string) {
  Linking.openURL(`tel:${phone.replace(/\D/g, '')}`).catch(() => {
    Alert.alert('Unable to call', `Dial manually: ${phone}`);
  });
}

export default function ResourceHubScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const { fs } = useApp();
  const topPad = Platform.OS === 'web' ? 20 : insets.top;

  const [filter, setFilter] = useState<HubCategory | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = HUB_RESOURCES.filter((r) => {
    const matchCat = filter === 'all' || r.category === filter;
    const q = searchQuery.toLowerCase();
    const matchSearch =
      !q ||
      r.name.toLowerCase().includes(q) ||
      r.description.toLowerCase().includes(q) ||
      r.tags.some((t) => t.includes(q));
    return matchCat && matchSearch;
  });

  const styles = StyleSheet.create({
    container:  { flex: 1, backgroundColor: colors.background },
    header:     { paddingTop: topPad + 12, paddingHorizontal: 20, paddingBottom: 0, borderBottomWidth: 1, borderBottomColor: colors.border },
    headerRow:  { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
    headerTitle:{ flex: 1, fontSize: fs(22), fontFamily: 'Inter_700Bold', color: colors.foreground },
    headerSub:  { fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginBottom: 12 },
    searchBar:  { backgroundColor: colors.muted, borderRadius: 10, flexDirection: 'row', alignItems: 'center', paddingHorizontal: 12, marginBottom: 12, gap: 8 },
    searchInput:{ flex: 1, fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.foreground, paddingVertical: 9 },
    filterRow:  { flexDirection: 'row', paddingBottom: 0 },
    filterBtn:  { paddingHorizontal: 12, paddingVertical: 10, marginRight: 4, borderBottomWidth: 2, borderBottomColor: 'transparent' },
    filterActive:{ borderBottomColor: colors.primary },
    filterText: { fontSize: fs(12), fontFamily: 'Inter_500Medium', color: colors.mutedForeground },
    filterTextActive: { color: colors.primary, fontFamily: 'Inter_600SemiBold' },
    scroll:     { flex: 1 },
    scrollContent: { padding: 16, paddingBottom: Platform.OS === 'web' ? 80 : 110, flexGrow: 1 },
    card:       { backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1, borderColor: colors.border, marginBottom: 10, padding: 14 },
    cardTop:    { flexDirection: 'row', alignItems: 'flex-start', gap: 10, marginBottom: 8 },
    cardName:   { flex: 1, fontSize: fs(15), fontFamily: 'Inter_600SemiBold', color: colors.foreground, lineHeight: 21 },
    freeBadge:  { backgroundColor: '#5A9E6F18', borderRadius: 20, paddingHorizontal: 8, paddingVertical: 3 },
    freeBadgeTxt:{ fontSize: fs(10), fontFamily: 'Inter_600SemiBold', color: '#5A9E6F' },
    paidBadge:  { backgroundColor: colors.muted, borderRadius: 20, paddingHorizontal: 8, paddingVertical: 3 },
    paidBadgeTxt:{ fontSize: fs(10), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground },
    desc:       { fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 18, marginBottom: 10 },
    tags:       { flexDirection: 'row', flexWrap: 'wrap', gap: 6, marginBottom: 10 },
    tag:        { backgroundColor: colors.muted, borderRadius: 20, paddingHorizontal: 8, paddingVertical: 3 },
    tagText:    { fontSize: fs(11), fontFamily: 'Inter_400Regular', color: colors.mutedForeground },
    btnRow:     { flexDirection: 'row', gap: 8 },
    openBtn:    { flex: 1, backgroundColor: colors.primary, borderRadius: 10, paddingVertical: 10, alignItems: 'center', flexDirection: 'row', justifyContent: 'center', gap: 6 },
    openBtnTxt: { fontSize: fs(13), fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' },
    callBtn:    { backgroundColor: '#5A9E6F', borderRadius: 10, paddingVertical: 10, paddingHorizontal: 14, flexDirection: 'row', alignItems: 'center', gap: 5 },
    callBtnTxt: { fontSize: fs(13), fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' },
    disclaimer: { backgroundColor: colors.muted, borderRadius: colors.radius, padding: 12, marginTop: 8 },
    disclaimerTxt: { fontSize: fs(11), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 16 },
    emptyState: { alignItems: 'center', paddingVertical: 40, gap: 8 },
    emptyTxt:   { fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, textAlign: 'center' },
    catSection: { marginBottom: 6, marginTop: 4 },
    catHeader:  { flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 8 },
    catTitle:   { fontSize: fs(12), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase', letterSpacing: 0.7 },
  });

  // Group by category when showing "all"
  const renderContent = () => {
    if (filter !== 'all' || searchQuery) {
      if (filtered.length === 0) {
        return (
          <View style={styles.emptyState}>
            <Text style={{ fontSize: 36 }}>🔍</Text>
            <Text style={styles.emptyTxt}>No resources found.{'\n'}Try a different search term or category.</Text>
          </View>
        );
      }
      return filtered.map((r) => <ResourceCard key={r.id} resource={r} styles={styles} colors={colors} fs={fs} />);
    }

    // Grouped view
    return HUB_CATEGORIES.map((cat) => {
      const items = HUB_RESOURCES.filter((r) => r.category === cat.value);
      if (items.length === 0) return null;
      return (
        <View key={cat.value} style={styles.catSection}>
          <View style={styles.catHeader}>
            <Text style={{ fontSize: fs(16) }}>{cat.emoji}</Text>
            <Text style={[styles.catTitle, { color: cat.color }]}>{cat.label}</Text>
            <View style={{ height: 1, flex: 1, backgroundColor: colors.border, marginLeft: 6 }} />
          </View>
          {items.map((r) => (
            <ResourceCard key={r.id} resource={r} styles={styles} colors={colors} fs={fs} />
          ))}
        </View>
      );
    });
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.headerRow}>
          <Pressable onPress={() => router.back()} hitSlop={10} style={{ marginRight: 10 }} accessibilityRole="button" accessibilityLabel="Back">
            <Feather name="arrow-left" size={22} color={colors.foreground} />
          </Pressable>
          <Text style={styles.headerTitle} accessibilityRole="header">📚 Resource Hub</Text>
        </View>
        <Text style={styles.headerSub}>{HUB_RESOURCES.length} curated free legal resources</Text>

        <View style={styles.searchBar}>
          <Feather name="search" size={15} color={colors.mutedForeground} />
          <TextInput
            style={styles.searchInput}
            value={searchQuery}
            onChangeText={setSearchQuery}
            placeholder="Search resources…"
            placeholderTextColor={colors.mutedForeground}
            accessibilityLabel="Search resources"
          />
          {searchQuery.length > 0 && (
            <Pressable onPress={() => setSearchQuery('')} hitSlop={8}><Feather name="x" size={14} color={colors.mutedForeground} /></Pressable>
          )}
        </View>

        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterRow}>
          <Pressable style={[styles.filterBtn, filter === 'all' && styles.filterActive]} onPress={() => setFilter('all')} accessibilityRole="tab" accessibilityState={{ selected: filter === 'all' }}>
            <Text style={[styles.filterText, filter === 'all' && styles.filterTextActive]}>All</Text>
          </Pressable>
          {HUB_CATEGORIES.map((cat) => (
            <Pressable key={cat.value} style={[styles.filterBtn, filter === cat.value && styles.filterActive]} onPress={() => setFilter(cat.value)} accessibilityRole="tab" accessibilityState={{ selected: filter === cat.value }}>
              <Text style={[styles.filterText, filter === cat.value && styles.filterTextActive]}>{cat.emoji} {cat.label}</Text>
            </Pressable>
          ))}
        </ScrollView>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {renderContent()}
        <View style={styles.disclaimer}>
          <Text style={styles.disclaimerTxt}>{HUB_DISCLAIMER}</Text>
        </View>
      </ScrollView>
    </View>
  );
}

function ResourceCard({ resource, styles, colors, fs }: { resource: (typeof HUB_RESOURCES)[0]; styles: any; colors: any; fs: (n: number) => number }) {
  const r = resource;
  const cat = HUB_CATEGORIES.find((c) => c.value === r.category)!;
  return (
    <View style={styles.card} accessibilityLabel={r.name}>
      <View style={styles.cardTop}>
        <Text style={styles.cardName}>{r.name}</Text>
        <View style={r.free ? styles.freeBadge : styles.paidBadge}>
          <Text style={r.free ? styles.freeBadgeTxt : styles.paidBadgeTxt}>{r.free ? 'FREE' : 'PAID'}</Text>
        </View>
      </View>
      <Text style={styles.desc}>{r.description}</Text>
      <View style={styles.tags}>
        {r.tags.slice(0, 3).map((t: string) => (
          <View key={t} style={styles.tag}><Text style={styles.tagText}>{t}</Text></View>
        ))}
      </View>
      <View style={styles.btnRow}>
        <Pressable
          style={({ pressed }) => [styles.openBtn, pressed && { opacity: 0.85 }]}
          onPress={() => { openUrl(r.url); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); }}
          accessibilityRole="button"
          accessibilityLabel={`Open ${r.name}`}
        >
          <Feather name="external-link" size={14} color="#FFFFFF" />
          <Text style={styles.openBtnTxt}>Open Website</Text>
        </Pressable>
        {r.phone && (
          <Pressable
            style={({ pressed }) => [styles.callBtn, pressed && { opacity: 0.85 }]}
            onPress={() => { callNumber(r.phone!); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); }}
            accessibilityRole="button"
            accessibilityLabel={`Call ${r.name}: ${r.phone}`}
          >
            <Feather name="phone" size={14} color="#FFFFFF" />
            <Text style={styles.callBtnTxt}>Call</Text>
          </Pressable>
        )}
      </View>
    </View>
  );
}
