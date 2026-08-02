/**
 * Resource Hub tab — combines the curated HUB_RESOURCES with crisis hotlines
 * and local legal services, all in one searchable/filterable screen.
 */
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
import { Feather } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import * as WebBrowser from 'expo-web-browser';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { CATEGORY_COLORS, CATEGORY_LABELS, CRISIS_HOTLINES } from '@/constants/crisis-hotlines';
import { LEGAL_RESOURCES } from '@/constants/legal-resources';
import {
  HUB_CATEGORIES,
  HUB_DISCLAIMER,
  HUB_RESOURCES,
  HubCategory,
} from '@/constants/resource-hub-data';
import { I18nKey } from '@/constants/i18n';
import { useApp } from '@/context/AppContext';
import { useColors } from '@/hooks/useColors';
import { useRTL } from '@/hooks/useRTL';
import { useT } from '@/hooks/useTranslation';

type FilterType = HubCategory | 'all' | 'crisis' | 'legal_services';

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

export default function HubScreen() {
  const colors  = useColors();
  const insets  = useSafeAreaInsets();
  const { fs }  = useApp();
  const { t }   = useT();
  const { rowDir } = useRTL();
  const topPad  = Platform.OS === 'web' ? 20 : insets.top;

  const [filter, setFilter]           = useState<FilterType>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const q = searchQuery.toLowerCase();

  const filteredHub = HUB_RESOURCES.filter((r) => {
    const matchCat    = filter === 'all' || filter === r.category;
    const matchSearch = !q || r.name.toLowerCase().includes(q) || r.description.toLowerCase().includes(q) || r.tags.some(t => t.toLowerCase().includes(q));
    return matchCat && matchSearch;
  });

  const filteredHotlines = CRISIS_HOTLINES.filter(h =>
    h.id !== '911' &&
    (!q || h.name.toLowerCase().includes(q) || h.description.toLowerCase().includes(q))
  );

  const filteredLegal = LEGAL_RESOURCES.filter(r =>
    !q || r.name.toLowerCase().includes(q) || (r.description || '').toLowerCase().includes(q)
  );

  const styles = StyleSheet.create({
    container:   { flex: 1, backgroundColor: colors.background },
    header:      { paddingTop: topPad + 12, paddingHorizontal: 20, paddingBottom: 0, borderBottomWidth: 1, borderBottomColor: colors.border },
    headerTitle: { fontSize: fs(22), fontFamily: 'Inter_700Bold', color: colors.foreground, marginBottom: 4 },
    headerSub:   { fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginBottom: 10 },
    searchBar:   { backgroundColor: colors.muted, borderRadius: 10, flexDirection: rowDir, alignItems: 'center', paddingHorizontal: 12, marginBottom: 10, gap: 8 },
    searchInput: { flex: 1, fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.foreground, paddingVertical: 9 },
    filterRow:   { flexDirection: rowDir, paddingBottom: 0 },
    filterBtn:   { paddingHorizontal: 12, paddingVertical: 10, marginRight: 4, borderBottomWidth: 2, borderBottomColor: 'transparent' },
    filterActive:{ borderBottomColor: colors.primary },
    filterText:  { fontSize: fs(12), fontFamily: 'Inter_500Medium', color: colors.mutedForeground },
    filterTextActive: { color: colors.primary, fontFamily: 'Inter_600SemiBold' },
    scroll:      { flex: 1 },
    scrollContent: { padding: 16, paddingBottom: Platform.OS === 'web' ? 80 : 120, flexGrow: 1 },
    card:        { backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1, borderColor: colors.border, marginBottom: 10, padding: 14 },
    cardTop:     { flexDirection: rowDir, alignItems: 'flex-start', gap: 10, marginBottom: 8 },
    cardName:    { flex: 1, fontSize: fs(15), fontFamily: 'Inter_600SemiBold', color: colors.foreground, lineHeight: 21 },
    freeBadge:   { backgroundColor: '#5A9E6F18', borderRadius: 20, paddingHorizontal: 8, paddingVertical: 3 },
    freeTxt:     { fontSize: fs(10), fontFamily: 'Inter_600SemiBold', color: '#5A9E6F' },
    paidBadge:   { backgroundColor: colors.muted, borderRadius: 20, paddingHorizontal: 8, paddingVertical: 3 },
    paidTxt:     { fontSize: fs(10), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground },
    desc:        { fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 18, marginBottom: 10 },
    tags:        { flexDirection: rowDir, flexWrap: 'wrap', gap: 6, marginBottom: 10 },
    tag:         { backgroundColor: colors.muted, borderRadius: 20, paddingHorizontal: 8, paddingVertical: 3 },
    tagText:     { fontSize: fs(11), fontFamily: 'Inter_400Regular', color: colors.mutedForeground },
    btnRow:      { flexDirection: rowDir, gap: 8 },
    openBtn:     { flex: 1, backgroundColor: colors.primary, borderRadius: 10, paddingVertical: 10, alignItems: 'center', flexDirection: rowDir, justifyContent: 'center', gap: 6 },
    openBtnTxt:  { fontSize: fs(13), fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' },
    callBtn:     { backgroundColor: '#5A9E6F', borderRadius: 10, paddingVertical: 10, paddingHorizontal: 14, flexDirection: rowDir, alignItems: 'center', gap: 5 },
    callBtnTxt:  { fontSize: fs(13), fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' },
    sectionHdr:  { flexDirection: rowDir, alignItems: 'center', gap: 6, marginBottom: 8, marginTop: 4 },
    sectionTitle:{ fontSize: fs(12), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase', letterSpacing: 0.7 },
    sectionLine: { height: 1, flex: 1, backgroundColor: colors.border, marginLeft: 6 },
    disclaimer:  { backgroundColor: colors.muted, borderRadius: colors.radius, padding: 12, marginTop: 8 },
    disclaimerTxt:{ fontSize: fs(11), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 16 },
    emptyState:  { alignItems: 'center', paddingVertical: 40, gap: 8 },
    emptyTxt:    { fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, textAlign: 'center' },
  });

  const renderContent = () => {
    if (filter === 'crisis') {
      if (filteredHotlines.length === 0) return <View style={styles.emptyState}><Text style={styles.emptyTxt}>{t('hub.not_found')}</Text></View>;
      return filteredHotlines.map(h => (
        <HotlineCard key={h.id} hotline={h} styles={styles} colors={colors} fs={fs} rowDir={rowDir} />
      ));
    }
    if (filter === 'legal_services') {
      if (filteredLegal.length === 0) return <View style={styles.emptyState}><Text style={styles.emptyTxt}>{t('hub.not_found')}</Text></View>;
      return filteredLegal.map(r => (
        <LegalCard key={r.id} resource={r} styles={styles} colors={colors} fs={fs} rowDir={rowDir} t={t} />
      ));
    }
    if (filter !== 'all' || searchQuery) {
      if (filteredHub.length === 0) return <View style={styles.emptyState}><Text style={styles.emptyTxt}>{t('hub.not_found')}</Text></View>;
      return filteredHub.map(r => <HubCard key={r.id} resource={r} styles={styles} colors={colors} fs={fs} t={t} />);
    }

    // "All" view — grouped sections
    return (
      <>
        {/* Curated hub resources by category */}
        {HUB_CATEGORIES.map((cat) => {
          const items = HUB_RESOURCES.filter(r => r.category === cat.value);
          if (items.length === 0) return null;
          return (
            <View key={cat.value} style={{ marginBottom: 6 }}>
              <View style={styles.sectionHdr}>
                <Text style={{ fontSize: fs(16) }}>{cat.emoji}</Text>
                <Text style={[styles.sectionTitle, { color: cat.color }]}>{t(cat.labelKey as I18nKey)}</Text>
                <View style={styles.sectionLine} />
              </View>
              {items.map(r => <HubCard key={r.id} resource={r} styles={styles} colors={colors} fs={fs} t={t} />)}
            </View>
          );
        })}

        {/* Crisis Hotlines */}
        <View style={{ marginBottom: 6 }}>
          <View style={styles.sectionHdr}>
            <Text style={{ fontSize: fs(16) }}>📞</Text>
            <Text style={[styles.sectionTitle, { color: '#E05252' }]}>Crisis Hotlines</Text>
            <View style={styles.sectionLine} />
          </View>
          {filteredHotlines.map(h => (
            <HotlineCard key={h.id} hotline={h} styles={styles} colors={colors} fs={fs} rowDir={rowDir} />
          ))}
        </View>

        {/* Legal Services */}
        <View style={{ marginBottom: 6 }}>
          <View style={styles.sectionHdr}>
            <Text style={{ fontSize: fs(16) }}>⚖️</Text>
            <Text style={[styles.sectionTitle, { color: '#C97C5D' }]}>Legal Services</Text>
            <View style={styles.sectionLine} />
          </View>
          {filteredLegal.map(r => (
            <LegalCard key={r.id} resource={r} styles={styles} colors={colors} fs={fs} rowDir={rowDir} t={t} />
          ))}
        </View>

        <View style={styles.disclaimer}><Text style={styles.disclaimerTxt}>{HUB_DISCLAIMER}</Text></View>
      </>
    );
  };

  const totalCount = HUB_RESOURCES.length + filteredHotlines.length + filteredLegal.length;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle} accessibilityRole="header">{t('hub.title')}</Text>
        <Text style={styles.headerSub}>{totalCount} {t('hub.curated_count')}</Text>

        <View style={styles.searchBar}>
          <Feather name="search" size={15} color={colors.mutedForeground} />
          <TextInput
            style={styles.searchInput}
            value={searchQuery}
            onChangeText={setSearchQuery}
            placeholder={t('hub.search_ph')}
            placeholderTextColor={colors.mutedForeground}
            accessibilityLabel="Search resources"
          />
          {searchQuery.length > 0 && (
            <Pressable onPress={() => setSearchQuery('')} hitSlop={8}>
              <Feather name="x" size={14} color={colors.mutedForeground} />
            </Pressable>
          )}
        </View>

        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterRow}>
          {/* All */}
          <Pressable style={[styles.filterBtn, filter === 'all' && styles.filterActive]} onPress={() => setFilter('all')} accessibilityRole="tab">
            <Text style={[styles.filterText, filter === 'all' && styles.filterTextActive]}>{t('hub.filter_all')}</Text>
          </Pressable>
          {/* Hub categories */}
          {HUB_CATEGORIES.map((cat) => (
            <Pressable key={cat.value} style={[styles.filterBtn, filter === cat.value && styles.filterActive]} onPress={() => setFilter(cat.value)} accessibilityRole="tab">
              <Text style={[styles.filterText, filter === cat.value && styles.filterTextActive]}>{cat.emoji} {t(cat.labelKey as I18nKey)}</Text>
            </Pressable>
          ))}
          {/* Crisis + Legal */}
          <Pressable style={[styles.filterBtn, filter === 'crisis' && styles.filterActive]} onPress={() => setFilter('crisis')} accessibilityRole="tab">
            <Text style={[styles.filterText, filter === 'crisis' && styles.filterTextActive]}>📞 Crisis Lines</Text>
          </Pressable>
          <Pressable style={[styles.filterBtn, filter === 'legal_services' && styles.filterActive]} onPress={() => setFilter('legal_services')} accessibilityRole="tab">
            <Text style={[styles.filterText, filter === 'legal_services' && styles.filterTextActive]}>⚖️ Legal Services</Text>
          </Pressable>
        </ScrollView>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {renderContent()}
      </ScrollView>
    </View>
  );
}

// ─── Hub resource card (curated links) ───────────────────────────────────────
function HubCard({ resource: r, styles, colors, fs, t }: any) {
  const cat = HUB_CATEGORIES.find((c) => c.value === r.category);
  return (
    <View style={styles.card}>
      <View style={styles.cardTop}>
        <Text style={styles.cardName}>{r.name}</Text>
        <View style={r.free ? styles.freeBadge : styles.paidBadge}>
          <Text style={r.free ? styles.freeTxt : styles.paidTxt}>{r.free ? t('hub.free') : t('hub.paid')}</Text>
        </View>
      </View>
      <Text style={styles.desc}>{r.description}</Text>
      <View style={styles.tags}>
        {r.tags.slice(0, 3).map((tag: string) => (
          <View key={tag} style={styles.tag}><Text style={styles.tagText}>{tag}</Text></View>
        ))}
      </View>
      <View style={styles.btnRow}>
        <Pressable
          style={({ pressed }: any) => [styles.openBtn, pressed && { opacity: 0.85 }]}
          onPress={() => { openUrl(r.url); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); }}
          accessibilityRole="button">
          <Feather name="external-link" size={14} color="#FFFFFF" />
          <Text style={styles.openBtnTxt}>{t('hub.open_website')}</Text>
        </Pressable>
        {r.phone && (
          <Pressable
            style={({ pressed }: any) => [styles.callBtn, pressed && { opacity: 0.85 }]}
            onPress={() => { Linking.openURL(`tel:${r.phone.replace(/\D/g, '')}`); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); }}
            accessibilityRole="button">
            <Feather name="phone" size={14} color="#FFFFFF" />
            <Text style={styles.callBtnTxt}>{t('hub.call')}</Text>
          </Pressable>
        )}
      </View>
    </View>
  );
}

// ─── Crisis hotline card ──────────────────────────────────────────────────────
function HotlineCard({ hotline: h, styles, colors, fs, rowDir }: any) {
  const categoryColor = CATEGORY_COLORS[h.category as keyof typeof CATEGORY_COLORS];
  const categoryLabel = CATEGORY_LABELS[h.category as keyof typeof CATEGORY_LABELS];
  const callNumber = async () => {
    const url = `tel:${h.number.replace(/[^0-9+]/g, '')}`;
    const ok = await Linking.canOpenURL(url);
    if (ok) { Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium); await Linking.openURL(url); }
    else Alert.alert('Call', `Please dial: ${h.number}`);
  };
  return (
    <View style={styles.card}>
      <View style={{ flexDirection: rowDir, alignItems: 'center', gap: 8, marginBottom: 6 }}>
        <View style={{ paddingHorizontal: 8, paddingVertical: 3, borderRadius: 20, backgroundColor: categoryColor }}>
          <Text style={{ fontSize: 11, fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' }}>{categoryLabel}</Text>
        </View>
        <Text style={{ fontSize: 11, fontFamily: 'Inter_400Regular', color: colors.mutedForeground }}>{h.available}</Text>
      </View>
      <Text style={styles.cardName}>{h.name}</Text>
      <Text style={[styles.desc, { marginTop: 4 }]}>{h.description}</Text>
      <Pressable
        style={{ flexDirection: rowDir, alignItems: 'center', gap: 6, backgroundColor: categoryColor + '18',
          borderRadius: 10, paddingVertical: 10, paddingHorizontal: 14, alignSelf: 'flex-start' }}
        onPress={callNumber} accessibilityRole="button">
        <Feather name="phone" size={14} color={categoryColor} />
        <Text style={{ fontSize: 14, fontFamily: 'Inter_600SemiBold', color: categoryColor }}>{h.number}</Text>
      </Pressable>
    </View>
  );
}

// ─── Legal resource card (Bay Area orgs) ─────────────────────────────────────
function LegalCard({ resource: r, styles, colors, fs, rowDir, t }: any) {
  const callNumber = async () => {
    if (!r.phone) return;
    const url = `tel:${r.phone.replace(/[^0-9+]/g, '')}`;
    const ok = await Linking.canOpenURL(url);
    if (ok) { Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium); await Linking.openURL(url); }
    else Alert.alert('Call', `Please dial: ${r.phone}`);
  };
  return (
    <View style={styles.card}>
      <Text style={styles.cardName}>{r.name}</Text>
      {r.description ? <Text style={styles.desc}>{r.description}</Text> : null}
      {r.address ? (
        <View style={{ flexDirection: rowDir, alignItems: 'center', gap: 6, marginBottom: 8 }}>
          <Feather name="map-pin" size={12} color={colors.mutedForeground} />
          <Text style={{ fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, flex: 1 }}>{r.address}</Text>
        </View>
      ) : null}
      <View style={styles.btnRow}>
        {r.website && (
          <Pressable style={styles.openBtn} onPress={() => openUrl(r.website)} accessibilityRole="button">
            <Feather name="external-link" size={14} color="#FFFFFF" />
            <Text style={styles.openBtnTxt}>{t('hub.open_website')}</Text>
          </Pressable>
        )}
        {r.phone && (
          <Pressable style={styles.callBtn} onPress={callNumber} accessibilityRole="button">
            <Feather name="phone" size={14} color="#FFFFFF" />
            <Text style={styles.callBtnTxt}>{t('hub.call')}</Text>
          </Pressable>
        )}
      </View>
    </View>
  );
}
