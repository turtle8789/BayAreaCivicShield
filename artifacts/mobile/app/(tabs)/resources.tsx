import React, { useState } from 'react';
import {
  ActivityIndicator,
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
import * as Location from 'expo-location';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { CATEGORY_COLORS, CATEGORY_LABELS, CRISIS_HOTLINES, Hotline } from '@/constants/crisis-hotlines';
import { LEGAL_RESOURCES, LegalResource, ResourceType, TYPE_LABELS } from '@/constants/legal-resources';
import { useColors } from '@/hooks/useColors';
import { useRTL } from '@/hooks/useRTL';
import { useT } from '@/hooks/useTranslation';

type Tab = 'hotlines' | 'resources' | 'nearby';

// ─── Haversine distance (miles) ───────────────────────────────────────────────

function haversine(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 3958.8;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

// ─── Open Google Maps with exact lat/lon ─────────────────────────────────────

async function openGoogleMaps(lat: number, lon: number, name: string) {
  // Use lat,lon for pin accuracy — faster and more precise than address search
  const query = encodeURIComponent(name);
  const coords = `${lat},${lon}`;
  const googleUrl = `https://maps.google.com/?q=${query}&ll=${coords}`;

  // iOS: try Apple Maps first (native), fall back to Google
  if (Platform.OS === 'ios') {
    const appleUrl = `maps:?q=${query}&ll=${coords}`;
    const supported = await Linking.canOpenURL(appleUrl);
    if (supported) {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      await Linking.openURL(appleUrl);
      return;
    }
  }
  Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
  await Linking.openURL(googleUrl);
}

// ─── Hotline Card ─────────────────────────────────────────────────────────────

function HotlineCard({ hotline }: { hotline: Hotline }) {
  const colors = useColors();
  const { t } = useT();
  const { rowDir } = useRTL();
  const categoryColor = CATEGORY_COLORS[hotline.category];

  const callNumber = async () => {
    const url = `tel:${hotline.number.replace(/[^0-9+]/g, '')}`;
    const supported = await Linking.canOpenURL(url);
    if (supported) {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      await Linking.openURL(url);
    } else {
      Alert.alert(t('common.call'), `Please dial: ${hotline.number}`);
    }
  };

  return (
    <View style={{ backgroundColor: colors.card, borderRadius: colors.radius, padding: 14, marginBottom: 10, borderWidth: 1, borderColor: colors.border }}>
      <View style={{ flexDirection: rowDir, alignItems: 'flex-start', gap: 10, marginBottom: 6 }}>
        <View style={{ paddingHorizontal: 8, paddingVertical: 3, borderRadius: 20, backgroundColor: categoryColor }}>
          <Text style={{ fontSize: 11, fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' }}>
            {CATEGORY_LABELS[hotline.category]}
          </Text>
        </View>
        <Text style={{ fontSize: 11, fontFamily: 'Inter_400Regular', color: colors.mutedForeground }}>
          {hotline.available}
        </Text>
      </View>
      <Text style={{ fontSize: 15, fontFamily: 'Inter_600SemiBold', color: colors.foreground, marginBottom: 4 }}>
        {hotline.name}
      </Text>
      <Text style={{ fontSize: 13, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 18, marginBottom: 10 }}>
        {hotline.description}
      </Text>
      <Pressable
        style={{ flexDirection: rowDir, alignItems: 'center', gap: 6, backgroundColor: categoryColor + '14', borderRadius: 10, paddingVertical: 10, paddingHorizontal: 14, alignSelf: 'flex-start' }}
        onPress={callNumber}
        accessibilityLabel={`${t('common.call')} ${hotline.number}`}
        accessibilityRole="button"
      >
        <Feather name="phone" size={15} color={categoryColor} />
        <Text style={{ fontSize: 15, fontFamily: 'Inter_700Bold', color: categoryColor }}>
          {hotline.number}
        </Text>
      </Pressable>
    </View>
  );
}

// ─── Legal Resource Card ──────────────────────────────────────────────────────

function ResourceCard({
  resource,
  distanceMiles,
}: {
  resource: LegalResource;
  distanceMiles?: number;
}) {
  const colors = useColors();
  const { t } = useT();
  const { rowDir } = useRTL();

  const callPhone = async () => {
    const url = `tel:${resource.phone.replace(/[^0-9+]/g, '')}`;
    const supported = await Linking.canOpenURL(url);
    if (supported) {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      await Linking.openURL(url);
    } else {
      Alert.alert(t('common.call'), `Please dial: ${resource.phone}`);
    }
  };

  const openWebsite = async () => {
    const url = resource.website.startsWith('http') ? resource.website : `https://${resource.website}`;
    const supported = await Linking.canOpenURL(url);
    if (supported) await Linking.openURL(url);
  };

  return (
    <View style={{ backgroundColor: colors.card, borderRadius: colors.radius, padding: 14, marginBottom: 10, borderWidth: 1, borderColor: colors.border }}>
      <View style={{ flexDirection: rowDir, alignItems: 'center', gap: 8, marginBottom: 6 }}>
        <View style={{ paddingHorizontal: 8, paddingVertical: 3, borderRadius: 20, backgroundColor: colors.primary + '18' }}>
          <Text style={{ fontSize: 11, fontFamily: 'Inter_500Medium', color: colors.primary }}>
            {TYPE_LABELS[resource.type]}
          </Text>
        </View>
        <Text style={{ fontSize: 12, fontFamily: 'Inter_400Regular', color: colors.mutedForeground }}>
          {resource.region}
        </Text>
        {distanceMiles !== undefined && (
          <View style={{ marginLeft: 'auto', backgroundColor: '#5A9E6F22', borderRadius: 20, paddingHorizontal: 8, paddingVertical: 3 }}>
            <Text style={{ fontSize: 11, fontFamily: 'Inter_600SemiBold', color: '#5A9E6F' }}>
              {distanceMiles < 10 ? distanceMiles.toFixed(1) : Math.round(distanceMiles)} mi
            </Text>
          </View>
        )}
      </View>
      <Text style={{ fontSize: 16, fontFamily: 'Inter_600SemiBold', color: colors.foreground, marginBottom: 4 }}>
        {resource.name}
      </Text>
      <Text style={{ fontSize: 13, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 18, marginBottom: 6 }}>
        {resource.description}
      </Text>
      {resource.address ? (
        <Text style={{ fontSize: 12, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginBottom: 8 }}>
          📍 {resource.address}
        </Text>
      ) : null}
      <View style={{ flexDirection: rowDir, flexWrap: 'wrap', gap: 6, marginBottom: 10 }}>
        {resource.serves.map((s) => (
          <View key={s} style={{ backgroundColor: colors.muted, borderRadius: 6, paddingHorizontal: 8, paddingVertical: 3 }}>
            <Text style={{ fontSize: 11, fontFamily: 'Inter_400Regular', color: colors.mutedForeground }}>{s}</Text>
          </View>
        ))}
      </View>
      <View style={{ flexDirection: rowDir, gap: 8 }}>
        <Pressable
          style={{ flex: 1, flexDirection: rowDir, alignItems: 'center', justifyContent: 'center', gap: 6, borderRadius: 10, paddingVertical: 10, backgroundColor: colors.primary + '0F', borderWidth: 1, borderColor: colors.primary + '30' }}
          onPress={callPhone}
          accessibilityRole="button"
          accessibilityLabel={t('common.call')}
        >
          <Feather name="phone" size={14} color={colors.primary} />
          <Text style={{ fontSize: 13, fontFamily: 'Inter_500Medium', color: colors.primary }}>{t('common.call')}</Text>
        </Pressable>
        <Pressable
          style={{ flex: 1, flexDirection: rowDir, alignItems: 'center', justifyContent: 'center', gap: 6, borderRadius: 10, paddingVertical: 10, backgroundColor: colors.muted, borderWidth: 1, borderColor: colors.border }}
          onPress={openWebsite}
          accessibilityRole="button"
          accessibilityLabel={t('common.website')}
        >
          <Feather name="globe" size={14} color={colors.mutedForeground} />
          <Text style={{ fontSize: 13, fontFamily: 'Inter_500Medium', color: colors.mutedForeground }}>{t('common.website')}</Text>
        </Pressable>
        <Pressable
          style={{ flex: 1, flexDirection: rowDir, alignItems: 'center', justifyContent: 'center', gap: 6, borderRadius: 10, paddingVertical: 10, backgroundColor: '#5A9E6F14', borderWidth: 1, borderColor: '#5A9E6F30' }}
          onPress={() => openGoogleMaps(resource.lat, resource.lon, resource.name)}
          accessibilityRole="button"
          accessibilityLabel={t('common.open_maps')}
        >
          <Feather name="map-pin" size={14} color="#5A9E6F" />
          <Text style={{ fontSize: 13, fontFamily: 'Inter_500Medium', color: '#5A9E6F' }}>{t('common.directions')}</Text>
        </Pressable>
      </View>
    </View>
  );
}

// ─── Category Filter Chips ────────────────────────────────────────────────────

const TYPE_FILTER_OPTIONS: Array<{ value: ResourceType | 'all'; labelKey: string }> = [
  { value: 'all',             labelKey: 'resources.filter_all' },
  { value: 'legal_aid',       labelKey: 'resources.filter_legal_aid' },
  { value: 'public_defender', labelKey: 'resources.filter_defender' },
  { value: 'nonprofit',       labelKey: 'resources.filter_nonprofit' },
  { value: 'clinic',          labelKey: 'resources.filter_clinic' },
  { value: 'bar_referral',    labelKey: 'resources.filter_bar' },
];

function TypeFilterChips({
  selected,
  onChange,
}: {
  selected: ResourceType | 'all';
  onChange: (v: ResourceType | 'all') => void;
}) {
  const colors = useColors();
  const { t } = useT();
  const { rowDir } = useRTL();
  return (
    <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 12 }}>
      <View style={{ flexDirection: rowDir, gap: 8, paddingRight: 8 }}>
        {TYPE_FILTER_OPTIONS.map((opt) => {
          const active = selected === opt.value;
          const label = t(opt.labelKey as any);
          return (
            <Pressable
              key={opt.value}
              onPress={() => { onChange(opt.value); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); }}
              style={{
                paddingHorizontal: 14,
                paddingVertical: 7,
                borderRadius: 20,
                borderWidth: 1.5,
                borderColor: active ? colors.primary : colors.border,
                backgroundColor: active ? colors.primary + '18' : colors.muted,
              }}
              accessibilityRole="radio"
              accessibilityState={{ selected: active }}
              accessibilityLabel={`Filter: ${label}`}
            >
              <Text style={{ fontSize: 13, fontFamily: active ? 'Inter_600SemiBold' : 'Inter_400Regular', color: active ? colors.primary : colors.mutedForeground }}>
                {label}
              </Text>
            </Pressable>
          );
        })}
      </View>
    </ScrollView>
  );
}

// ─── Find Near You Tab ────────────────────────────────────────────────────────

function FindNearbyTab() {
  const colors = useColors();
  const { t } = useT();
  const { rowDir } = useRTL();

  const [loading, setLoading]         = useState(false);
  const [userLat, setUserLat]         = useState<number | null>(null);
  const [userLon, setUserLon]         = useState<number | null>(null);
  const [locationName, setLocationName] = useState('');
  const [manualZip, setManualZip]     = useState('');
  const [sorted, setSorted]           = useState<Array<{ resource: LegalResource; dist: number }>>([]);
  const [searched, setSearched]       = useState(false);
  const [typeFilter, setTypeFilter]   = useState<ResourceType | 'all'>('all');
  const [radiusMiles, setRadiusMiles] = useState<number | null>(25); // null = no limit

  const useMyLocation = async () => {
    try {
      setLoading(true);
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Denied', t('resources.perm_denied'));
        setLoading(false);
        return;
      }
      const loc = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced });
      computeResults(loc.coords.latitude, loc.coords.longitude, t('resources.your_location'));
    } catch {
      Alert.alert('Error', t('resources.location_error'));
      setLoading(false);
    }
  };

  // Free Nominatim geocoding — no key needed
  const searchByAddress = async () => {
    if (!manualZip.trim()) {
      Alert.alert(t('resources.enter_location'), t('resources.enter_location'));
      return;
    }
    setLoading(true);
    try {
      const q = encodeURIComponent(manualZip.trim());
      const res = await fetch(
        `https://nominatim.openstreetmap.org/search?q=${q}&format=json&limit=1&addressdetails=1`,
        { headers: { 'User-Agent': 'CivicShieldPro/2.0 (civic-legal-aid-app)' } },
      );
      const data = (await res.json()) as Array<{ lat: string; lon: string; display_name: string }>;
      if (!data || data.length === 0) {
        Alert.alert(t('resources.not_found'), `"${manualZip.trim()}" could not be found. Try a full city name (e.g. "Los Angeles"), a ZIP code (e.g. "90001"), or an address.`);
        setLoading(false);
        return;
      }
      const lat = parseFloat(data[0].lat);
      const lon = parseFloat(data[0].lon);
      computeResults(lat, lon, data[0].display_name.split(',').slice(0, 2).join(','));
    } catch {
      Alert.alert('Error', t('resources.geocode_error'));
      setLoading(false);
    }
  };

  const computeResults = (lat: number, lon: number, name: string) => {
    setUserLat(lat);
    setUserLon(lon);
    setLocationName(name);
    const withDist = LEGAL_RESOURCES.map((r) => ({
      resource: r,
      dist: haversine(lat, lon, r.lat, r.lon),
    })).sort((a, b) => a.dist - b.dist);
    setSorted(withDist);
    setSearched(true);
    setLoading(false);
    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
  };

  // Apply type + radius filters
  const RADIUS_OPTIONS: Array<{ label: string; value: number | null }> = [
    { label: '5 mi',              value: 5    },
    { label: '10 mi',             value: 10   },
    { label: '25 mi',             value: 25   },
    { label: '50 mi',             value: 50   },
    { label: t('resources.radius_any'), value: null },
  ];

  const filtered = sorted.filter(({ resource, dist }) => {
    const matchType   = typeFilter === 'all' || resource.type === typeFilter;
    const matchRadius = radiusMiles === null || dist <= radiusMiles;
    return matchType && matchRadius;
  });

  return (
    <>
      {/* Location input card */}
      <View style={{ backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1, borderColor: colors.border, padding: 14, marginBottom: 12 }}>
        <Text style={{ fontSize: 14, fontFamily: 'Inter_600SemiBold', color: colors.foreground, marginBottom: 10 }}>
          📍 {t('resources.find_near_you')}
        </Text>
        <Pressable
          style={{ flexDirection: rowDir, alignItems: 'center', justifyContent: 'center', gap: 8, backgroundColor: colors.primary, borderRadius: 10, paddingVertical: 12, marginBottom: 10, opacity: loading ? 0.6 : 1 }}
          onPress={useMyLocation}
          disabled={loading}
          accessibilityRole="button"
          accessibilityLabel={t('resources.use_my_location')}
        >
          {loading ? <ActivityIndicator size="small" color="#FFFFFF" /> : <Feather name="navigation" size={16} color="#FFFFFF" />}
          <Text style={{ fontSize: 14, fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' }}>
            {t('resources.use_my_location')}
          </Text>
        </Pressable>
        <Text style={{ fontSize: 12, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, textAlign: 'center', marginBottom: 10 }}>
          {t('resources.enter_city_zip')}
        </Text>
        <View style={{ flexDirection: rowDir, gap: 8 }}>
          <TextInput
            style={{ flex: 1, backgroundColor: colors.muted, borderRadius: 10, paddingHorizontal: 12, paddingVertical: 10, fontSize: 14, fontFamily: 'Inter_400Regular', color: colors.foreground, borderWidth: 1, borderColor: colors.border }}
            value={manualZip}
            onChangeText={setManualZip}
            placeholder={t('resources.location_ph')}
            placeholderTextColor={colors.mutedForeground}
            returnKeyType="search"
            onSubmitEditing={searchByAddress}
          />
          <Pressable
            style={{ backgroundColor: colors.secondary, borderRadius: 10, paddingHorizontal: 14, alignItems: 'center', justifyContent: 'center', opacity: loading ? 0.6 : 1 }}
            onPress={searchByAddress}
            disabled={loading}
            accessibilityRole="button"
            accessibilityLabel={t('common.search')}
          >
            <Feather name="search" size={18} color="#FFFFFF" />
          </Pressable>
        </View>
      </View>

      {/* Results */}
      {searched && (
        <>
          {/* Location label */}
          {locationName ? (
            <View style={{ flexDirection: rowDir, alignItems: 'center', gap: 6, marginBottom: 10 }}>
              <Feather name="map-pin" size={13} color={colors.primary} />
              <Text style={{ fontSize: 13, fontFamily: 'Inter_500Medium', color: colors.mutedForeground, flex: 1 }}>
                {t('resources.showing_near')} {locationName}
              </Text>
              {/* Open full map in Google Maps centered on user location */}
              {userLat !== null && userLon !== null && (
                <Pressable
                  onPress={() => openGoogleMaps(userLat!, userLon!, 'Legal Aid Near Me')}
                  style={{ flexDirection: rowDir, alignItems: 'center', gap: 4, backgroundColor: '#5A9E6F14', borderRadius: 20, paddingHorizontal: 10, paddingVertical: 5 }}
                  accessibilityRole="button"
                  accessibilityLabel={t('common.open_maps')}
                >
                  <Feather name="external-link" size={12} color="#5A9E6F" />
                  <Text style={{ fontSize: 12, fontFamily: 'Inter_500Medium', color: '#5A9E6F' }}>
                    {t('common.open_maps')}
                  </Text>
                </Pressable>
              )}
            </View>
          ) : null}

          {/* Radius filter */}
          <View style={{ marginBottom: 12 }}>
            <Text style={{ fontSize: 12, fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase', letterSpacing: 0.7, marginBottom: 8 }}>
              📍 {t('resources.search_radius')}
            </Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              <View style={{ flexDirection: rowDir, gap: 6, paddingRight: 8 }}>
                {RADIUS_OPTIONS.map((opt) => {
                  const active = radiusMiles === opt.value;
                  return (
                    <Pressable
                      key={String(opt.value)}
                      onPress={() => { setRadiusMiles(opt.value); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); }}
                      style={{ paddingHorizontal: 14, paddingVertical: 7, borderRadius: 20, borderWidth: 1.5, borderColor: active ? colors.primary : colors.border, backgroundColor: active ? colors.primary + '14' : colors.muted }}
                      accessibilityRole="radio"
                      accessibilityState={{ selected: active }}
                    >
                      <Text style={{ fontSize: 13, fontFamily: active ? 'Inter_600SemiBold' : 'Inter_400Regular', color: active ? colors.primary : colors.mutedForeground }}>{opt.label}</Text>
                    </Pressable>
                  );
                })}
              </View>
            </ScrollView>
          </View>

          {/* Type filter chips */}
          <View style={{ marginBottom: 4 }}>
            <Text style={{ fontSize: 12, fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase', letterSpacing: 0.7, marginBottom: 8 }}>
              {t('resources.filter_type')}
            </Text>
            <TypeFilterChips selected={typeFilter} onChange={setTypeFilter} />
          </View>

          {/* Result count */}
          <Text style={{ fontSize: 12, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginBottom: 10 }}>
            {filtered.length} {filtered.length === 1 ? t('resources.result') : t('resources.results')}
            {radiusMiles !== null ? ` ${t('resources.within')} ${radiusMiles} ${t('resources.mi')}` : ''}
            {typeFilter !== 'all' ? ` · ${TYPE_LABELS[typeFilter as ResourceType]}` : ''}
          </Text>

          {filtered.length === 0 ? (
            <View style={{ backgroundColor: colors.muted, borderRadius: colors.radius, padding: 14, borderWidth: 1, borderColor: colors.border }}>
              <Text style={{ fontSize: 14, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, textAlign: 'center' }}>
                {t('resources.no_results')}
              </Text>
            </View>
          ) : (
            filtered.map(({ resource, dist }) => (
              <ResourceCard key={resource.id} resource={resource} distanceMiles={dist} />
            ))
          )}
        </>
      )}

      {!searched && !loading && (
        <View style={{ backgroundColor: colors.primary + '0F', borderRadius: colors.radius, padding: 14, borderWidth: 1, borderColor: colors.primary + '20', flexDirection: rowDir, gap: 10 }}>
          <Feather name="map" size={16} color={colors.primary} />
          <Text style={{ flex: 1, fontSize: 13, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 19 }}>
            {t('resources.search_tip')}
          </Text>
        </View>
      )}
    </>
  );
}

// ─── Main Screen ──────────────────────────────────────────────────────────────

export default function ResourcesScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const { t } = useT();
  const { rowDir } = useRTL();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;
  const [activeTab, setActiveTab] = useState<Tab>('hotlines');

  const callEmergency = async () => {
    const url = 'tel:911';
    const supported = await Linking.canOpenURL(url);
    if (supported) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
      await Linking.openURL(url);
    } else {
      Alert.alert(t('resources.emergency_title'), t('resources.emergency_msg'));
    }
  };

  const styles = StyleSheet.create({
    container:         { flex: 1, backgroundColor: colors.background },
    header:            { paddingTop: topPad + 12, paddingHorizontal: 20, paddingBottom: 0, borderBottomWidth: 1, borderBottomColor: colors.border },
    headerTitle:       { fontSize: 22, fontFamily: 'Inter_700Bold', color: colors.foreground },
    headerSub:         { fontSize: 13, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 2, marginBottom: 12 },
    tabRow:            { flexDirection: rowDir },
    tabBtn:            { flex: 1, paddingVertical: 10, alignItems: 'center', borderBottomWidth: 2, borderBottomColor: 'transparent' },
    tabBtnActive:      { borderBottomColor: colors.primary },
    tabBtnText:        { fontSize: 13, fontFamily: 'Inter_500Medium', color: colors.mutedForeground },
    tabBtnTextActive:  { color: colors.primary, fontFamily: 'Inter_600SemiBold' },
    scroll:            { flex: 1 },
    scrollContent:     { padding: 16, paddingBottom: Platform.OS === 'web' ? 34 : 100, flexGrow: 1 },
    emergencyCard:     { backgroundColor: '#E05252', borderRadius: colors.radius, padding: 16, marginBottom: 16, flexDirection: rowDir, alignItems: 'center', gap: 12 },
  });

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle} accessibilityRole="header">{t('resources.title')}</Text>
        <Text style={styles.headerSub}>{t('resources.subtitle')}</Text>
        <View style={styles.tabRow}>
          {(['hotlines', 'resources', 'nearby'] as Tab[]).map((tab) => (
            <Pressable
              key={tab}
              style={[styles.tabBtn, activeTab === tab && styles.tabBtnActive]}
              onPress={() => setActiveTab(tab)}
              accessibilityRole="tab"
              accessibilityState={{ selected: activeTab === tab }}
            >
              <Text style={[styles.tabBtnText, activeTab === tab && styles.tabBtnTextActive]}>
                {tab === 'hotlines'
                  ? t('resources.hotlines')
                  : tab === 'resources'
                    ? t('resources.legal_aid')
                    : t('resources.near_me')}
              </Text>
            </Pressable>
          ))}
        </View>
      </View>

      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        {/* Emergency 911 always visible */}
        <Pressable style={styles.emergencyCard} onPress={callEmergency} accessibilityRole="button" accessibilityLabel="Call 911 — Emergency Services">
          <Feather name="alert-triangle" size={22} color="#FFFFFF" />
          <Text style={{ flex: 1, fontSize: 15, fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' }}>
            {t('resources.emergency')}
          </Text>
          <Text style={{ fontSize: 22, fontFamily: 'Inter_700Bold', color: '#FFFFFF' }}>911</Text>
        </Pressable>

        {activeTab === 'hotlines' &&
          CRISIS_HOTLINES.filter((h) => h.id !== '911').map((hotline) => (
            <HotlineCard key={hotline.id} hotline={hotline} />
          ))}

        {activeTab === 'resources' &&
          LEGAL_RESOURCES.map((resource) => (
            <ResourceCard key={resource.id} resource={resource} />
          ))}

        {activeTab === 'nearby' && <FindNearbyTab />}
      </ScrollView>
    </View>
  );
}
