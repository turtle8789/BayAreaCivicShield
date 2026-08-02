/**
 * Legal Aid Near Me — live Overpass API search for lawyers, legal aid offices,
 * and courthouses within a user-selected radius. Crisis hotlines + curated legal
 * services have moved to the Resource Hub tab.
 */
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
import { useColors } from '@/hooks/useColors';
import { useRTL } from '@/hooks/useRTL';
import { useT } from '@/hooks/useTranslation';

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

async function openGoogleMaps(lat: number, lon: number, name: string) {
  const query  = encodeURIComponent(name);
  const coords = `${lat},${lon}`;
  const googleUrl = `https://maps.google.com/?q=${query}&ll=${coords}`;
  if (Platform.OS === 'ios') {
    const appleUrl = `maps:?q=${query}&ll=${coords}`;
    if (await Linking.canOpenURL(appleUrl)) {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      await Linking.openURL(appleUrl);
      return;
    }
  }
  Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
  await Linking.openURL(googleUrl);
}

// ─── Overpass types & query ───────────────────────────────────────────────────

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
  typeKey: string;
  typeColor: string;
  address: string;
  phone: string;
  website: string;
}

const OVERPASS_MAX_MI = 50;
const OVERPASS_MAX_M  = OVERPASS_MAX_MI * 1609.344;

// Multiple public Overpass mirrors — tried in order; first success wins.
const OVERPASS_ENDPOINTS = [
  'https://overpass-api.de/api/interpreter',
  'https://overpass.kumi.systems/api/interpreter',
  'https://overpass.private.coffee/api/interpreter',
];

function buildOverpassQuery(lat: number, lon: number): string {
  const r = OVERPASS_MAX_M.toFixed(0);
  const c = `${lat},${lon}`;
  return `[out:json][timeout:25];
(
  node["office"~"^(lawyer|legal_services|legal_aid)$"](around:${r},${c});
  node["amenity"~"^(legal_advice|courthouse)$"](around:${r},${c});
  node["name"~"Legal Aid|Legal Services|Legal Help|Public Defender|Immigration Legal|Civil Rights|ACLU|NAACP|Law Center|Law Foundation|Legal Foundation",i](around:${r},${c});
  way["office"~"^(lawyer|legal_services|legal_aid)$"](around:${r},${c});
  way["amenity"~"^(legal_advice|courthouse)$"](around:${r},${c});
)->.all;
.all out center tags;`;
}

function liveTypeInfo(tags: Record<string, string>): { typeKey: string; color: string } {
  const o = tags.office, a = tags.amenity;
  if (o === 'lawyer')         return { typeKey: 'resources.nearby.type_lawyer',         color: '#9B7EC9' };
  if (o === 'legal_services') return { typeKey: 'resources.nearby.type_legal_services', color: '#5A9E6F' };
  if (o === 'legal_aid')      return { typeKey: 'resources.nearby.type_legal_aid',      color: '#4A90D9' };
  if (a === 'legal_advice')   return { typeKey: 'resources.nearby.type_legal_advice',   color: '#4A90D9' };
  if (a === 'courthouse')     return { typeKey: 'resources.nearby.type_courthouse',     color: '#C9A050' };
  return { typeKey: 'resources.nearby.type_legal_resource', color: '#888' };
}

function liveAddress(tags: Record<string, string>): string {
  const num    = tags['addr:housenumber'] || '';
  const street = tags['addr:street']      || '';
  const city   = tags['addr:city']        || '';
  const state  = tags['addr:state']       || '';
  return [num && street ? `${num} ${street}` : street, city, state].filter(Boolean).join(', ');
}

function parseOverpassResults(json: { elements: OverpassElement[] }, lat: number, lon: number): LiveResult[] {
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
      id: `${el.type}-${el.id}`, name,
      lat: elLat, lon: elLon, dist,
      typeKey: typeInfo.typeKey, typeColor: typeInfo.color,
      address: liveAddress(el.tags),
      phone:   el.tags.phone    || el.tags['contact:phone']   || '',
      website: el.tags.website  || el.tags['contact:website'] || el.tags.url || '',
    });
  }
  return results.sort((a, b) => a.dist - b.dist);
}

async function queryOverpass(lat: number, lon: number): Promise<LiveResult[]> {
  const body = `data=${encodeURIComponent(buildOverpassQuery(lat, lon))}`;
  let lastError: unknown;
  for (const endpoint of OVERPASS_ENDPOINTS) {
    const controller = new AbortController();
    const tid = setTimeout(() => controller.abort(), 22_000);
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body,
        signal: controller.signal,
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = (await res.json()) as { elements: OverpassElement[] };
      return parseOverpassResults(json, lat, lon);
    } catch (e) {
      lastError = e;
      // AbortError = our timeout; still try next mirror
    } finally {
      clearTimeout(tid);
    }
  }
  throw lastError;
}

// ─── LiveResultCard ───────────────────────────────────────────────────────────

function LiveResultCard({ item, rowDir }: { item: LiveResult; rowDir: 'row' | 'row-reverse' }) {
  const colors = useColors();
  const { t }  = useT();

  return (
    <View style={{ backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1,
      borderColor: colors.border, padding: 14, marginBottom: 10 }}>
      {/* Type badge + distance */}
      <View style={{ flexDirection: rowDir, alignItems: 'center', gap: 8, marginBottom: 6 }}>
        <View style={{ paddingHorizontal: 8, paddingVertical: 3, borderRadius: 20,
          backgroundColor: item.typeColor + '20' }}>
          <Text style={{ fontSize: 11, fontFamily: 'Inter_600SemiBold', color: item.typeColor }}>
            {t(item.typeKey as any)}
          </Text>
        </View>
        <Text style={{ fontSize: 11, fontFamily: 'Inter_500Medium', color: '#5A9E6F',
          backgroundColor: '#5A9E6F18', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 20 }}>
          {item.dist < 0.2
            ? `${Math.round(item.dist * 5280)} ${t('resources.nearby.ft_away')}`
            : `${item.dist < 10 ? item.dist.toFixed(1) : Math.round(item.dist)} ${t('resources.nearby.mi_away')}`}
        </Text>
      </View>
      <Text style={{ fontSize: 15, fontFamily: 'Inter_600SemiBold', color: colors.foreground, marginBottom: 4 }}>
        {item.name}
      </Text>
      {item.address ? (
        <Text style={{ fontSize: 12, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginBottom: 8 }}>
          📍 {item.address}
        </Text>
      ) : null}
      <View style={{ flexDirection: rowDir, gap: 8, flexWrap: 'wrap' }}>
        {item.phone ? (
          <Pressable
            style={{ flexDirection: rowDir, alignItems: 'center', gap: 5, backgroundColor: colors.primary + '14',
              borderRadius: 10, paddingVertical: 8, paddingHorizontal: 12 }}
            onPress={() => Linking.openURL(`tel:${item.phone.replace(/\D/g, '')}`)}
            accessibilityRole="button">
            <Feather name="phone" size={13} color={colors.primary} />
            <Text style={{ fontSize: 12, fontFamily: 'Inter_500Medium', color: colors.primary }}>{t('common.call')}</Text>
          </Pressable>
        ) : null}
        {item.website ? (
          <Pressable
            style={{ flexDirection: rowDir, alignItems: 'center', gap: 5, backgroundColor: colors.muted,
              borderRadius: 10, paddingVertical: 8, paddingHorizontal: 12 }}
            onPress={() => Linking.openURL(item.website.startsWith('http') ? item.website : `https://${item.website}`)}
            accessibilityRole="button">
            <Feather name="globe" size={13} color={colors.mutedForeground} />
            <Text style={{ fontSize: 12, fontFamily: 'Inter_500Medium', color: colors.mutedForeground }}>{t('common.website')}</Text>
          </Pressable>
        ) : null}
        <Pressable
          style={{ flexDirection: rowDir, alignItems: 'center', gap: 5, backgroundColor: '#5A9E6F14',
            borderRadius: 10, paddingVertical: 8, paddingHorizontal: 12 }}
          onPress={() => openGoogleMaps(item.lat, item.lon, item.name)}
          accessibilityRole="button">
          <Feather name="map-pin" size={13} color="#5A9E6F" />
          <Text style={{ fontSize: 12, fontFamily: 'Inter_500Medium', color: '#5A9E6F' }}>{t('resources.nearby.maps')}</Text>
        </Pressable>
      </View>
    </View>
  );
}

// ─── Main Screen ──────────────────────────────────────────────────────────────

const RADIUS_CHIPS = [1, 5, 10, 25, 50] as const;

export default function ResourcesScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const { t }  = useT();
  const { rowDir } = useRTL();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;

  const [loading, setLoading]           = useState(false);
  const [locationName, setLocationName] = useState('');
  const [manualInput, setManualInput]   = useState('');
  const [allResults, setAllResults]     = useState<LiveResult[]>([]);
  const [searched, setSearched]         = useState(false);
  const [radiusMiles, setRadiusMiles]   = useState<number>(25);
  const [overpassError, setOverpassError] = useState('');
  const [userLat, setUserLat]           = useState<number | null>(null);
  const [userLon, setUserLon]           = useState<number | null>(null);

  const runSearch = async (lat: number, lon: number, name: string) => {
    setLoading(true);
    setOverpassError('');
    setUserLat(lat); setUserLon(lon); setLocationName(name);
    try {
      const results = await queryOverpass(lat, lon);
      setAllResults(results);
      setSearched(true);
      if (results.length > 0) Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch (e: any) {
      const msg = e?.name === 'AbortError' ? t('resources.nearby.error') + ' (timeout)' : t('resources.nearby.error');
      setOverpassError(msg);
      setSearched(true);
    } finally {
      setLoading(false);
    }
  };

  const useMyLocation = async () => {
    try {
      setLoading(true);
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert(t('resources.perm_denied'), t('resources.perm_denied'));
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
    if (!q) return;
    setLoading(true);
    try {
      const controller = new AbortController();
      const tid = setTimeout(() => controller.abort(), 15_000);
      let data: Array<{ lat: string; lon: string; display_name: string }> = [];
      try {
        const res = await fetch(
          `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(q)}&format=json&limit=1`,
          { signal: controller.signal },
        );
        data = await res.json();
      } finally {
        clearTimeout(tid);
      }
      if (!data?.length) {
        Alert.alert(t('resources.not_found'), t('resources.nearby.geocode_not_found').replace('{query}', q));
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

  const callEmergency = async () => {
    const url = 'tel:911';
    const ok = await Linking.canOpenURL(url);
    if (ok) { Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning); await Linking.openURL(url); }
    else Alert.alert(t('resources.emergency_title'), t('resources.emergency_msg'));
  };

  const styles = StyleSheet.create({
    container:   { flex: 1, backgroundColor: colors.background },
    header:      { paddingTop: topPad + 12, paddingHorizontal: 20, paddingBottom: 14,
                   borderBottomWidth: 1, borderBottomColor: colors.border },
    headerTitle: { fontSize: 22, fontFamily: 'Inter_700Bold', color: colors.foreground },
    headerSub:   { fontSize: 13, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 2 },
    scroll:      { flex: 1 },
    scrollContent:{ padding: 16, paddingBottom: Platform.OS === 'web' ? 34 : 120, flexGrow: 1 },
    emergencyCard:{ backgroundColor: '#E05252', borderRadius: colors.radius, padding: 14, marginBottom: 14,
                    flexDirection: rowDir, alignItems: 'center', gap: 12 },
    locationCard: { backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1,
                    borderColor: colors.border, padding: 14, marginBottom: 12 },
  });

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle} accessibilityRole="header">{t('resources.near_me')}</Text>
        <Text style={styles.headerSub}>{t('resources.search_tip')}</Text>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false} keyboardShouldPersistTaps="handled">

        {/* 911 Emergency */}
        <Pressable style={styles.emergencyCard} onPress={callEmergency}
          accessibilityRole="button" accessibilityLabel="Call 911 — Emergency Services">
          <Feather name="alert-triangle" size={22} color="#FFFFFF" />
          <Text style={{ flex: 1, fontSize: 15, fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' }}>
            {t('resources.emergency')}
          </Text>
          <Text style={{ fontSize: 22, fontFamily: 'Inter_700Bold', color: '#FFFFFF' }}>911</Text>
        </Pressable>

        {/* Location input */}
        <View style={styles.locationCard}>
          <View style={{ flexDirection: rowDir, alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
            <Text style={{ fontSize: 14, fontFamily: 'Inter_600SemiBold', color: colors.foreground }}>
              📍 {t('resources.find_near_you')}
            </Text>
            <View style={{ flexDirection: rowDir, alignItems: 'center', gap: 4, backgroundColor: colors.muted,
              borderRadius: 12, paddingHorizontal: 8, paddingVertical: 4 }}>
              <Feather name="database" size={10} color={colors.mutedForeground} />
              <Text style={{ fontSize: 10, fontFamily: 'Inter_500Medium', color: colors.mutedForeground }}>
                {t('resources.nearby.live_source')}
              </Text>
            </View>
          </View>

          <Pressable
            style={{ flexDirection: rowDir, alignItems: 'center', justifyContent: 'center', gap: 8,
              backgroundColor: colors.primary, borderRadius: 10, paddingVertical: 12, marginBottom: 10,
              opacity: loading ? 0.6 : 1 }}
            onPress={useMyLocation} disabled={loading} accessibilityRole="button">
            {loading
              ? <ActivityIndicator size="small" color="#FFFFFF" />
              : <Feather name="navigation" size={16} color="#FFFFFF" />}
            <Text style={{ fontSize: 14, fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' }}>
              {loading ? t('resources.nearby.searching') : t('resources.use_my_location')}
            </Text>
          </Pressable>

          <Text style={{ fontSize: 12, fontFamily: 'Inter_400Regular', color: colors.mutedForeground,
            textAlign: 'center', marginBottom: 10 }}>
            {t('resources.enter_city_zip')}
          </Text>

          <View style={{ flexDirection: rowDir, gap: 8 }}>
            <TextInput
              style={{ flex: 1, backgroundColor: colors.muted, borderRadius: 10, paddingHorizontal: 12,
                paddingVertical: 10, fontSize: 14, fontFamily: 'Inter_400Regular', color: colors.foreground,
                borderWidth: 1, borderColor: colors.border }}
              value={manualInput}
              onChangeText={setManualInput}
              placeholder={t('resources.enter_location')}
              placeholderTextColor={colors.mutedForeground}
              returnKeyType="search"
              onSubmitEditing={searchByAddress}
              editable={!loading}
            />
            <Pressable
              style={{ backgroundColor: colors.primary, borderRadius: 10, paddingHorizontal: 16,
                paddingVertical: 10, alignItems: 'center', justifyContent: 'center', opacity: loading ? 0.6 : 1 }}
              onPress={searchByAddress} disabled={loading} accessibilityRole="button">
              {loading
                ? <ActivityIndicator size="small" color="#FFFFFF" />
                : <Feather name="search" size={16} color="#FFFFFF" />}
            </Pressable>
          </View>
        </View>

        {/* Error message */}
        {overpassError ? (
          <View style={{ backgroundColor: '#E0525218', borderRadius: colors.radius, padding: 12,
            borderWidth: 1, borderColor: '#E0525240', marginBottom: 12 }}>
            <Text style={{ fontSize: 13, fontFamily: 'Inter_500Medium', color: '#E05252' }}>
              {overpassError}
            </Text>
            <Text style={{ fontSize: 12, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 4 }}>
              The live search service is unavailable. Use the Google Maps button below to find legal aid near you.
            </Text>
          </View>
        ) : null}

        {/* Location name */}
        {searched && !overpassError && locationName ? (
          <Text style={{ fontSize: 12, fontFamily: 'Inter_400Regular', color: colors.mutedForeground,
            marginBottom: 10, flexDirection: rowDir }}>
            📍 {locationName}
          </Text>
        ) : null}

        {/* Radius chips */}
        {searched && !overpassError && allResults.length > 0 && (
          <View style={{ marginBottom: 12 }}>
            <Text style={{ fontSize: 11, fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground,
              textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 8 }}>
              {t('resources.nearby.show_within')}
            </Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              <View style={{ flexDirection: rowDir, gap: 6, paddingRight: 8 }}>
                {RADIUS_CHIPS.map((mi) => {
                  const active = radiusMiles === mi;
                  const count  = allResults.filter(r => r.dist <= mi).length;
                  return (
                    <Pressable key={mi}
                      onPress={() => { setRadiusMiles(mi); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); }}
                      style={{ paddingHorizontal: 14, paddingVertical: 7, borderRadius: 20, borderWidth: 1.5,
                        borderColor: active ? colors.primary : colors.border,
                        backgroundColor: active ? colors.primary + '14' : colors.muted,
                        flexDirection: rowDir, alignItems: 'center', gap: 5 }}
                      accessibilityRole="radio" accessibilityState={{ selected: active }}>
                      <Text style={{ fontSize: 13, fontFamily: active ? 'Inter_600SemiBold' : 'Inter_400Regular',
                        color: active ? colors.primary : colors.mutedForeground }}>
                        {mi} {t('resources.mi')}
                      </Text>
                      <Text style={{ fontSize: 11, fontFamily: 'Inter_500Medium',
                        color: active ? colors.primary : colors.mutedForeground, opacity: 0.75 }}>
                        ({count})
                      </Text>
                    </Pressable>
                  );
                })}
              </View>
            </ScrollView>
          </View>
        )}

        {/* Results count */}
        {searched && !overpassError && (
          <Text style={{ fontSize: 12, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginBottom: 10 }}>
            {filtered.length === 0
              ? t('resources.nearby.no_results_radius')
              : `${filtered.length} ${t(filtered.length === 1 ? 'resources.result' : 'resources.results')} ${t('resources.within')} ${radiusMiles} ${t('resources.mi')}`}
          </Text>
        )}

        {/* Results */}
        {searched && !overpassError && filtered.length === 0 && (
          <View style={{ backgroundColor: colors.muted, borderRadius: colors.radius, padding: 16,
            borderWidth: 1, borderColor: colors.border, alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <Feather name="search" size={20} color={colors.mutedForeground} />
            <Text style={{ fontSize: 14, fontFamily: 'Inter_500Medium', color: colors.mutedForeground, textAlign: 'center' }}>
              {t('resources.nearby.no_resources').replace('{radius}', String(radiusMiles))}
            </Text>
            <Text style={{ fontSize: 13, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, textAlign: 'center', lineHeight: 18 }}>
              OpenStreetMap data is sparse for legal offices in many areas. Try Google Maps below for the most complete results.
            </Text>
          </View>
        )}

        {searched && !overpassError && filtered.map(item => (
          <LiveResultCard key={item.id} item={item} rowDir={rowDir} />
        ))}

        {/* Google Maps fallback — always visible after any search so users can find results OSM doesn't have */}
        {searched && (userLat !== null && userLon !== null) && (
          <Pressable
            style={({ pressed }) => ({
              flexDirection: rowDir, alignItems: 'center', justifyContent: 'center', gap: 8,
              marginTop: 12, backgroundColor: '#4285F4',
              borderRadius: colors.radius, paddingVertical: 13, paddingHorizontal: 16,
              opacity: pressed ? 0.85 : 1,
            })}
            onPress={() => {
              const q = encodeURIComponent(`legal aid near ${locationName || 'me'}`);
              Linking.openURL(`https://www.google.com/maps/search/${q}/@${userLat},${userLon},13z`);
            }}
            accessibilityRole="button"
            accessibilityLabel="Search Google Maps for legal aid">
            <Feather name="map" size={16} color="#FFFFFF" />
            <Text style={{ fontSize: 14, fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' }}>
              Search Google Maps for More Results
            </Text>
          </Pressable>
        )}

        {/* Intro tip */}
        {!searched && !loading && (
          <View style={{ backgroundColor: colors.primary + '0F', borderRadius: colors.radius, padding: 14,
            borderWidth: 1, borderColor: colors.primary + '20', flexDirection: rowDir, gap: 10 }}>
            <Feather name="map" size={16} color={colors.primary} />
            <Text style={{ flex: 1, fontSize: 13, fontFamily: 'Inter_400Regular',
              color: colors.mutedForeground, lineHeight: 19 }}>
              {t('resources.search_tip')} {t('resources.nearby.osm_note')}
            </Text>
          </View>
        )}

      </ScrollView>
    </View>
  );
}
