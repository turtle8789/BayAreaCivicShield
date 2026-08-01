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

// ─── Overpass API — live legal resource search ────────────────────────────────

interface OverpassElement {
  id: number;
  type: 'node' | 'way' | 'relation';
  lat?: number;
  lon?: number;
  center?: { lat: number; lon: number };
  tags: Record<string, string>;
}

interface LiveResult {
  id: string;
  name: string;
  lat: number;
  lon: number;
  dist: number;
  typeLabel: string;
  typeColor: string;
  address: string;
  phone: string;
  website: string;
}

const OVERPASS_MAX_MI   = 50;
const OVERPASS_MAX_M    = OVERPASS_MAX_MI * 1609.344;

function buildOverpassQuery(lat: number, lon: number): string {
  const r = OVERPASS_MAX_M.toFixed(0);
  const c = `${lat},${lon}`;
  return `[out:json][timeout:30];
(
  node["office"~"^(lawyer|legal_services|legal_aid)$"](around:${r},${c});
  node["amenity"~"^(legal_advice|courthouse)$"](around:${r},${c});
  node["name"~"Legal Aid|Legal Services|Legal Help|Public Defender|Immigration Legal|Civil Rights|ACLU|NAACP|Law Center|Law Foundation|Legal Foundation",i](around:${r},${c});
  way["office"~"^(lawyer|legal_services|legal_aid)$"](around:${r},${c});
  way["amenity"~"^(legal_advice|courthouse)$"](around:${r},${c});
)->.all;
.all out center tags;`;
}

function liveTypeInfo(tags: Record<string, string>): { label: string; color: string } {
  const o = tags.office;
  const a = tags.amenity;
  if (o === 'lawyer')         return { label: 'Lawyer / Attorney',  color: '#9B7EC9' };
  if (o === 'legal_services') return { label: 'Legal Services',     color: '#5A9E6F' };
  if (o === 'legal_aid')      return { label: 'Legal Aid',          color: '#4A90D9' };
  if (a === 'legal_advice')   return { label: 'Legal Advice',       color: '#4A90D9' };
  if (a === 'courthouse')     return { label: 'Courthouse',         color: '#C9A050' };
  return { label: 'Legal Resource', color: '#888' };
}

function liveAddress(tags: Record<string, string>): string {
  const num    = tags['addr:housenumber'] || '';
  const street = tags['addr:street']      || '';
  const city   = tags['addr:city']        || '';
  const state  = tags['addr:state']       || '';
  const full   = [num && street ? `${num} ${street}` : street, city, state].filter(Boolean);
  return full.join(', ');
}

async function queryOverpass(lat: number, lon: number): Promise<LiveResult[]> {
  const body = `data=${encodeURIComponent(buildOverpassQuery(lat, lon))}`;
  const res  = await fetch('https://overpass-api.de/api/interpreter', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  });
  if (!res.ok) throw new Error(`Overpass HTTP ${res.status}`);
  const json = (await res.json()) as { elements: OverpassElement[] };

  const seen = new Set<string>();
  const results: LiveResult[] = [];

  for (const el of json.elements) {
    const name = el.tags?.name;
    if (!name) continue;
    const elLat = el.lat  ?? el.center?.lat ?? 0;
    const elLon = el.lon  ?? el.center?.lon ?? 0;
    if (!elLat && !elLon) continue;
    const key = `${name}|${elLat.toFixed(4)}|${elLon.toFixed(4)}`;
    if (seen.has(key)) continue;
    seen.add(key);
    const dist = haversine(lat, lon, elLat, elLon);
    if (dist > OVERPASS_MAX_MI) continue;
    const typeInfo = liveTypeInfo(el.tags);
    results.push({
      id: `${el.type}-${el.id}`,
      name,
      lat: elLat, lon: elLon, dist,
      typeLabel: typeInfo.label, typeColor: typeInfo.color,
      address: liveAddress(el.tags),
      phone:   el.tags.phone    || el.tags['contact:phone'] || '',
      website: el.tags.website  || el.tags['contact:website'] || el.tags.url || '',
    });
  }
  return results.sort((a, b) => a.dist - b.dist);
}

// ─── LiveResultCard ────────────────────────────────────────────────────────────

function LiveResultCard({ item, rowDir }: { item: LiveResult; rowDir: 'row' | 'row-reverse' }) {
  const colors = useColors();
  const { t }  = useT();

  const openMaps = () => {
    const url = Platform.select({
      ios:     `maps://maps.apple.com/?q=${encodeURIComponent(item.name)}&ll=${item.lat},${item.lon}`,
      android: `geo:${item.lat},${item.lon}?q=${encodeURIComponent(item.name)}`,
      default: `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(item.name + ' ' + item.address)}`,
    });
    Linking.openURL(url!).catch(() =>
      Linking.openURL(`https://www.google.com/maps/search/?api=1&query=${item.lat},${item.lon}`)
    );
  };

  const openPhone = () => Linking.openURL(`tel:${item.phone.replace(/\s/g, '')}`);
  const openWeb   = () => Linking.openURL(item.website.startsWith('http') ? item.website : `https://${item.website}`);

  return (
    <View style={{ backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1, borderColor: colors.border, marginBottom: 10, overflow: 'hidden' }}>
      {/* Header row */}
      <View style={{ padding: 14, paddingBottom: 10 }}>
        <View style={{ flexDirection: rowDir, alignItems: 'flex-start', gap: 10, marginBottom: 6 }}>
          <View style={{ flex: 1 }}>
            <Text style={{ fontSize: 14, fontFamily: 'Inter_600SemiBold', color: colors.foreground, lineHeight: 20 }}>{item.name}</Text>
            {item.address ? (
              <Text style={{ fontSize: 12, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 3 }}>{item.address}</Text>
            ) : null}
          </View>
          <Text style={{ fontSize: 11, fontFamily: 'Inter_600SemiBold', color: '#fff', backgroundColor: item.typeColor, paddingHorizontal: 8, paddingVertical: 3, borderRadius: 20, overflow: 'hidden', alignSelf: 'flex-start' }}>
            {item.typeLabel}
          </Text>
        </View>
        {/* Distance badge */}
        <View style={{ flexDirection: rowDir, alignItems: 'center', gap: 4 }}>
          <Feather name="navigation" size={11} color={colors.primary} />
          <Text style={{ fontSize: 12, fontFamily: 'Inter_500Medium', color: colors.primary }}>
            {item.dist < 1 ? `${(item.dist * 5280).toFixed(0)} ft away` : `${item.dist.toFixed(1)} mi away`}
          </Text>
        </View>
      </View>

      {/* Action buttons */}
      {(item.phone || item.website || true) && (
        <View style={{ flexDirection: rowDir, borderTopWidth: 1, borderTopColor: colors.border }}>
          {item.phone ? (
            <Pressable
              onPress={openPhone}
              style={({ pressed }) => [{ flex: 1, flexDirection: rowDir, alignItems: 'center', justifyContent: 'center', gap: 5, paddingVertical: 10, opacity: pressed ? 0.6 : 1, borderRightWidth: item.website ? 1 : 0, borderRightColor: colors.border }]}
              accessibilityRole="button" accessibilityLabel="Call"
            >
              <Feather name="phone" size={14} color="#5A9E6F" />
              <Text style={{ fontSize: 12, fontFamily: 'Inter_500Medium', color: '#5A9E6F' }}>Call</Text>
            </Pressable>
          ) : null}
          {item.website ? (
            <Pressable
              onPress={openWeb}
              style={({ pressed }) => [{ flex: 1, flexDirection: rowDir, alignItems: 'center', justifyContent: 'center', gap: 5, paddingVertical: 10, opacity: pressed ? 0.6 : 1, borderRightWidth: 1, borderRightColor: colors.border }]}
              accessibilityRole="button" accessibilityLabel="Website"
            >
              <Feather name="globe" size={14} color="#4A90D9" />
              <Text style={{ fontSize: 12, fontFamily: 'Inter_500Medium', color: '#4A90D9' }}>Website</Text>
            </Pressable>
          ) : null}
          <Pressable
            onPress={openMaps}
            style={({ pressed }) => [{ flex: 1, flexDirection: rowDir, alignItems: 'center', justifyContent: 'center', gap: 5, paddingVertical: 10, opacity: pressed ? 0.6 : 1 }]}
            accessibilityRole="button" accessibilityLabel={t('common.open_maps')}
          >
            <Feather name="map-pin" size={14} color={colors.primary} />
            <Text style={{ fontSize: 12, fontFamily: 'Inter_500Medium', color: colors.primary }}>Maps</Text>
          </Pressable>
        </View>
      )}
    </View>
  );
}

// ─── FindNearbyTab ─────────────────────────────────────────────────────────────

const RADIUS_CHIPS = [1, 5, 10, 25, 50] as const;

function FindNearbyTab() {
  const colors = useColors();
  const { t } = useT();
  const { rowDir } = useRTL();

  const [loading, setLoading]           = useState(false);
  const [userLat, setUserLat]           = useState<number | null>(null);
  const [userLon, setUserLon]           = useState<number | null>(null);
  const [locationName, setLocationName] = useState('');
  const [manualInput, setManualInput]   = useState('');
  const [allResults, setAllResults]     = useState<LiveResult[]>([]);
  const [searched, setSearched]         = useState(false);
  const [radiusMiles, setRadiusMiles]   = useState<number>(25);
  const [overpassError, setOverpassError] = useState('');

  const runSearch = async (lat: number, lon: number, name: string) => {
    setLoading(true);
    setOverpassError('');
    setUserLat(lat); setUserLon(lon); setLocationName(name);
    try {
      const results = await queryOverpass(lat, lon);
      setAllResults(results);
      setSearched(true);
      if (results.length > 0) Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch (e) {
      setOverpassError('Could not reach the search service. Check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

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
      await runSearch(loc.coords.latitude, loc.coords.longitude, t('resources.your_location'));
    } catch {
      Alert.alert('Error', t('resources.location_error'));
      setLoading(false);
    }
  };

  const searchByAddress = async () => {
    const q = manualInput.trim();
    if (!q) { Alert.alert(t('resources.enter_location'), t('resources.enter_location')); return; }
    setLoading(true);
    try {
      const res  = await fetch(
        `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(q)}&format=json&limit=1`,
        { headers: { 'User-Agent': 'CivicShieldPro/2.0 (civic-legal-aid-app)' } },
      );
      const data = (await res.json()) as Array<{ lat: string; lon: string; display_name: string }>;
      if (!data?.length) {
        Alert.alert(t('resources.not_found'), `"${q}" could not be found. Try a full city name, ZIP code, or address.`);
        setLoading(false);
        return;
      }
      const lat  = parseFloat(data[0].lat);
      const lon  = parseFloat(data[0].lon);
      const name = data[0].display_name.split(',').slice(0, 2).join(',');
      await runSearch(lat, lon, name);
    } catch {
      Alert.alert('Error', t('resources.geocode_error'));
      setLoading(false);
    }
  };

  const filtered = allResults.filter(r => r.dist <= radiusMiles);

  return (
    <>
      {/* Location input card */}
      <View style={{ backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1, borderColor: colors.border, padding: 14, marginBottom: 12 }}>
        <View style={{ flexDirection: rowDir, alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
          <Text style={{ fontSize: 14, fontFamily: 'Inter_600SemiBold', color: colors.foreground }}>
            📍 {t('resources.find_near_you')}
          </Text>
          <View style={{ flexDirection: rowDir, alignItems: 'center', gap: 4, backgroundColor: colors.muted, borderRadius: 12, paddingHorizontal: 8, paddingVertical: 4 }}>
            <Feather name="database" size={10} color={colors.mutedForeground} />
            <Text style={{ fontSize: 10, fontFamily: 'Inter_500Medium', color: colors.mutedForeground }}>Live · OpenStreetMap</Text>
          </View>
        </View>
        <Pressable
          style={{ flexDirection: rowDir, alignItems: 'center', justifyContent: 'center', gap: 8, backgroundColor: colors.primary, borderRadius: 10, paddingVertical: 12, marginBottom: 10, opacity: loading ? 0.6 : 1 }}
          onPress={useMyLocation}
          disabled={loading}
          accessibilityRole="button"
          accessibilityLabel={t('resources.use_my_location')}
        >
          {loading ? <ActivityIndicator size="small" color="#FFFFFF" /> : <Feather name="navigation" size={16} color="#FFFFFF" />}
          <Text style={{ fontSize: 14, fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' }}>
            {loading ? 'Searching…' : t('resources.use_my_location')}
          </Text>
        </Pressable>
        <Text style={{ fontSize: 12, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, textAlign: 'center', marginBottom: 10 }}>
          {t('resources.enter_city_zip')}
        </Text>
        <View style={{ flexDirection: rowDir, gap: 8 }}>
          <TextInput
            style={{ flex: 1, backgroundColor: colors.muted, borderRadius: 10, paddingHorizontal: 12, paddingVertical: 10, fontSize: 14, fontFamily: 'Inter_400Regular', color: colors.foreground, borderWidth: 1, borderColor: colors.border }}
            value={manualInput}
            onChangeText={setManualInput}
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

      {/* Error banner */}
      {overpassError ? (
        <View style={{ backgroundColor: '#E0525214', borderRadius: colors.radius, borderWidth: 1, borderColor: '#E0525230', padding: 12, marginBottom: 12, flexDirection: rowDir, gap: 8 }}>
          <Feather name="alert-circle" size={14} color="#E05252" />
          <Text style={{ flex: 1, fontSize: 13, fontFamily: 'Inter_400Regular', color: '#E05252', lineHeight: 18 }}>{overpassError}</Text>
        </View>
      ) : null}

      {/* Results section */}
      {searched && (
        <>
          {/* Location header row */}
          <View style={{ flexDirection: rowDir, alignItems: 'center', gap: 6, marginBottom: 12 }}>
            <Feather name="map-pin" size={13} color={colors.primary} />
            <Text style={{ fontSize: 13, fontFamily: 'Inter_500Medium', color: colors.mutedForeground, flex: 1 }} numberOfLines={1}>
              {t('resources.showing_near')} {locationName}
            </Text>
            {userLat !== null && userLon !== null && (
              <Pressable
                onPress={() => openGoogleMaps(userLat!, userLon!, 'Legal Aid Near Me')}
                style={{ flexDirection: rowDir, alignItems: 'center', gap: 4, backgroundColor: '#5A9E6F14', borderRadius: 20, paddingHorizontal: 10, paddingVertical: 5 }}
                accessibilityRole="button"
              >
                <Feather name="external-link" size={12} color="#5A9E6F" />
                <Text style={{ fontSize: 12, fontFamily: 'Inter_500Medium', color: '#5A9E6F' }}>{t('common.open_maps')}</Text>
              </Pressable>
            )}
          </View>

          {/* Radius chips */}
          <View style={{ marginBottom: 14 }}>
            <Text style={{ fontSize: 11, fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 8 }}>
              Show within
            </Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              <View style={{ flexDirection: rowDir, gap: 6, paddingRight: 8 }}>
                {RADIUS_CHIPS.map((mi) => {
                  const active = radiusMiles === mi;
                  const count  = allResults.filter(r => r.dist <= mi).length;
                  return (
                    <Pressable
                      key={mi}
                      onPress={() => { setRadiusMiles(mi); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); }}
                      style={{ paddingHorizontal: 14, paddingVertical: 7, borderRadius: 20, borderWidth: 1.5, borderColor: active ? colors.primary : colors.border, backgroundColor: active ? colors.primary + '14' : colors.muted, flexDirection: rowDir, alignItems: 'center', gap: 5 }}
                      accessibilityRole="radio"
                      accessibilityState={{ selected: active }}
                    >
                      <Text style={{ fontSize: 13, fontFamily: active ? 'Inter_600SemiBold' : 'Inter_400Regular', color: active ? colors.primary : colors.mutedForeground }}>
                        {mi} mi
                      </Text>
                      <Text style={{ fontSize: 11, fontFamily: 'Inter_500Medium', color: active ? colors.primary : colors.mutedForeground, opacity: 0.75 }}>
                        ({count})
                      </Text>
                    </Pressable>
                  );
                })}
              </View>
            </ScrollView>
          </View>

          {/* Count */}
          <Text style={{ fontSize: 12, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginBottom: 10 }}>
            {filtered.length === 0
              ? 'No results within this radius'
              : `${filtered.length} result${filtered.length === 1 ? '' : 's'} within ${radiusMiles} mi`}
          </Text>

          {filtered.length === 0 ? (
            <View style={{ backgroundColor: colors.muted, borderRadius: colors.radius, padding: 16, borderWidth: 1, borderColor: colors.border, alignItems: 'center', gap: 8 }}>
              <Feather name="search" size={20} color={colors.mutedForeground} />
              <Text style={{ fontSize: 14, fontFamily: 'Inter_500Medium', color: colors.mutedForeground, textAlign: 'center' }}>
                No legal resources found within {radiusMiles} miles.
              </Text>
              <Text style={{ fontSize: 13, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, textAlign: 'center', lineHeight: 18 }}>
                Try expanding your radius, or check the Legal Aid tab for organizations that serve your area remotely.
              </Text>
            </View>
          ) : (
            filtered.map(item => <LiveResultCard key={item.id} item={item} rowDir={rowDir} />)
          )}
        </>
      )}

      {!searched && !loading && (
        <View style={{ backgroundColor: colors.primary + '0F', borderRadius: colors.radius, padding: 14, borderWidth: 1, borderColor: colors.primary + '20', flexDirection: rowDir, gap: 10 }}>
          <Feather name="map" size={16} color={colors.primary} />
          <Text style={{ flex: 1, fontSize: 13, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 19 }}>
            {t('resources.search_tip')} Results come directly from OpenStreetMap — no API key needed.
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
