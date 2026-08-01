import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  Animated,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { Feather } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import * as LocalAuthentication from 'expo-local-authentication';
import { useColors } from '@/hooks/useColors';

interface Props {
  pin: string;
  onUnlock: () => void;
}

type Screen = 'biometric' | 'pin';

export default function PinLockScreen({ pin, onUnlock }: Props) {
  const colors = useColors();

  const [screen, setScreen]           = useState<Screen>('biometric');
  const [bioAvailable, setBioAvailable] = useState(false);
  const [bioTypes, setBioTypes]       = useState<LocalAuthentication.AuthenticationType[]>([]);
  const [bioChecked, setBioChecked]   = useState(false);

  // PIN state
  const [entered, setEntered]   = useState('');
  const [pinError, setPinError] = useState(false);
  const shake = useRef(new Animated.Value(0)).current;

  // ── Biometric probe ────────────────────────────────────────────────────────
  const checkBio = useCallback(async () => {
    if (Platform.OS === 'web') { setBioChecked(true); setScreen('pin'); return; }
    try {
      const hasHw      = await LocalAuthentication.hasHardwareAsync();
      const enrolled   = await LocalAuthentication.isEnrolledAsync();
      const types      = await LocalAuthentication.supportedAuthenticationTypesAsync();
      const available  = hasHw && enrolled;
      setBioAvailable(available);
      setBioTypes(types);
      setBioChecked(true);
      if (!available) setScreen('pin');
    } catch {
      setBioChecked(true);
      setScreen('pin');
    }
  }, []);

  // ── Trigger biometric prompt ───────────────────────────────────────────────
  const promptBio = useCallback(async () => {
    try {
      const result = await LocalAuthentication.authenticateAsync({
        promptMessage:  'Unlock CivicShield Pro',
        fallbackLabel:  'Use PIN',
        cancelLabel:    'Use PIN',
        disableDeviceFallback: false,
      });
      if (result.success) {
        if (Platform.OS !== 'web') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        onUnlock();
      }
      // If the user tapped "Use PIN" (fallback), switch to PIN screen
      if (!result.success && (result as any).error === 'user_fallback') {
        setScreen('pin');
      }
    } catch {
      setScreen('pin');
    }
  }, [onUnlock]);

  // Check biometric availability on mount, then auto-prompt
  useEffect(() => {
    checkBio();
  }, [checkBio]);

  // Auto-trigger biometric prompt once we know it's available
  useEffect(() => {
    if (bioChecked && bioAvailable && screen === 'biometric') {
      promptBio();
    }
  }, [bioChecked, bioAvailable, screen, promptBio]);

  // ── PIN handlers ───────────────────────────────────────────────────────────
  const triggerShake = () => {
    shake.setValue(0);
    Animated.sequence([
      Animated.timing(shake, { toValue: 9, duration: 55, useNativeDriver: true }),
      Animated.timing(shake, { toValue: -9, duration: 55, useNativeDriver: true }),
      Animated.timing(shake, { toValue: 9, duration: 55, useNativeDriver: true }),
      Animated.timing(shake, { toValue: 0, duration: 55, useNativeDriver: true }),
    ]).start();
  };

  const handleDigit = (d: string) => {
    if (entered.length >= 4) return;
    if (Platform.OS !== 'web') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    const next = entered + d;
    setEntered(next);
    setPinError(false);

    if (next.length === 4) {
      if (next === pin) {
        if (Platform.OS !== 'web') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        onUnlock();
      } else {
        if (Platform.OS !== 'web') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
        setPinError(true);
        triggerShake();
        setTimeout(() => { setEntered(''); setPinError(false); }, 700);
      }
    }
  };

  const handleDelete = () => {
    setEntered(p => p.slice(0, -1));
    setPinError(false);
  };

  // ── Derive biometric icon name ─────────────────────────────────────────────
  const isFaceId = bioTypes.includes(LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION);
  const bioIconName = isFaceId ? 'smile' : 'disc'; // smile ≈ face, disc ≈ fingerprint ring

  const ROWS = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['',  '0', '⌫'],
  ];

  // ── Shared header ──────────────────────────────────────────────────────────
  const Header = () => (
    <View style={s.headerWrap}>
      <View style={[s.iconWrap, { backgroundColor: colors.primary + '18' }]}>
        <Feather name="shield" size={30} color={colors.primary} />
      </View>
      <Text style={[s.title, { color: colors.foreground }]}>CivicShield Pro</Text>
    </View>
  );

  // ── Biometric screen ───────────────────────────────────────────────────────
  if (screen === 'biometric' && bioAvailable) {
    return (
      <View style={[s.container, { backgroundColor: colors.background }]}>
        <View style={s.inner}>
          <Header />

          <Pressable
            onPress={promptBio}
            style={({ pressed }) => [s.bioButton, { borderColor: colors.primary, opacity: pressed ? 0.65 : 1 }]}
            accessibilityRole="button"
            accessibilityLabel={isFaceId ? 'Unlock with Face ID' : 'Unlock with fingerprint'}
          >
            <Feather name={bioIconName} size={52} color={colors.primary} />
          </Pressable>

          <Text style={[s.bioLabel, { color: colors.foreground }]}>
            {isFaceId ? 'Tap to unlock with Face ID' : 'Tap to unlock with fingerprint'}
          </Text>
          <Text style={[s.bioSub, { color: colors.mutedForeground }]}>
            Touch the button above or wait for the prompt
          </Text>

          <Pressable
            onPress={() => setScreen('pin')}
            style={({ pressed }) => [s.altBtn, { opacity: pressed ? 0.6 : 1 }]}
            accessibilityRole="button"
            accessibilityLabel="Use PIN instead"
          >
            <Feather name="grid" size={14} color={colors.mutedForeground} />
            <Text style={[s.altBtnText, { color: colors.mutedForeground }]}>Try another way · Use PIN</Text>
          </Pressable>
        </View>
      </View>
    );
  }

  // ── PIN screen ─────────────────────────────────────────────────────────────
  const dotColor = pinError ? '#E05252' : colors.primary;

  return (
    <View style={[s.container, { backgroundColor: colors.background }]}>
      <View style={s.inner}>
        <Header />

        <Text style={[s.pinSubtitle, { color: colors.mutedForeground }]}>
          Enter your PIN to continue
        </Text>

        {/* Dots */}
        <Animated.View style={[s.dotsRow, { transform: [{ translateX: shake }] }]}>
          {[0, 1, 2, 3].map(i => (
            <View
              key={i}
              style={[
                s.dot,
                { borderColor: dotColor },
                i < entered.length && { backgroundColor: dotColor },
              ]}
            />
          ))}
        </Animated.View>

        {pinError && (
          <Text style={s.errorText}>Incorrect PIN — try again</Text>
        )}

        {/* Numpad */}
        <View style={s.pad}>
          {ROWS.map((row, ri) => (
            <View key={ri} style={s.padRow}>
              {row.map((d, di) => {
                if (d === '') return <View key={di} style={s.padSpacer} />;
                if (d === '⌫') return (
                  <Pressable
                    key={di}
                    style={({ pressed }) => [s.padBtn, { backgroundColor: colors.muted, opacity: pressed ? 0.6 : 1 }]}
                    onPress={handleDelete}
                    accessibilityRole="button"
                    accessibilityLabel="Delete"
                  >
                    <Feather name="delete" size={22} color={colors.foreground} />
                  </Pressable>
                );
                return (
                  <Pressable
                    key={di}
                    style={({ pressed }) => [
                      s.padBtn,
                      { backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, opacity: pressed ? 0.65 : 1 },
                    ]}
                    onPress={() => handleDigit(d)}
                    accessibilityRole="button"
                    accessibilityLabel={d}
                  >
                    <Text style={[s.padDigit, { color: colors.foreground }]}>{d}</Text>
                  </Pressable>
                );
              })}
            </View>
          ))}
        </View>

        {/* Switch back to biometrics if available */}
        {bioAvailable && (
          <Pressable
            onPress={() => { setScreen('biometric'); promptBio(); }}
            style={({ pressed }) => [s.altBtn, { marginTop: 20, opacity: pressed ? 0.6 : 1 }]}
            accessibilityRole="button"
            accessibilityLabel={isFaceId ? 'Use Face ID' : 'Use fingerprint'}
          >
            <Feather name={bioIconName} size={14} color={colors.mutedForeground} />
            <Text style={[s.altBtnText, { color: colors.mutedForeground }]}>
              {isFaceId ? 'Use Face ID instead' : 'Use fingerprint instead'}
            </Text>
          </Pressable>
        )}
      </View>
    </View>
  );
}

const s = StyleSheet.create({
  container:   { flex: 1, alignItems: 'center', justifyContent: 'center' },
  inner:       { width: '80%', maxWidth: 300, alignItems: 'center' },
  headerWrap:  { alignItems: 'center', marginBottom: 32 },
  iconWrap:    { width: 68, height: 68, borderRadius: 34, alignItems: 'center', justifyContent: 'center', marginBottom: 14 },
  title:       { fontSize: 22, fontFamily: 'Inter_700Bold' },

  // Biometric screen
  bioButton:   { width: 100, height: 100, borderRadius: 50, borderWidth: 2, alignItems: 'center', justifyContent: 'center', marginBottom: 20 },
  bioLabel:    { fontSize: 16, fontFamily: 'Inter_600SemiBold', marginBottom: 6, textAlign: 'center' },
  bioSub:      { fontSize: 13, fontFamily: 'Inter_400Regular', textAlign: 'center', lineHeight: 19, marginBottom: 36 },

  // Shared "switch" link
  altBtn:      { flexDirection: 'row', alignItems: 'center', gap: 7, paddingVertical: 10, paddingHorizontal: 14 },
  altBtnText:  { fontSize: 13, fontFamily: 'Inter_500Medium' },

  // PIN screen
  pinSubtitle: { fontSize: 14, fontFamily: 'Inter_400Regular', marginBottom: 28, textAlign: 'center' },
  dotsRow:     { flexDirection: 'row', gap: 18, marginBottom: 10 },
  dot:         { width: 16, height: 16, borderRadius: 8, borderWidth: 2 },
  errorText:   { fontSize: 13, fontFamily: 'Inter_500Medium', color: '#E05252', marginBottom: 8 },
  pad:         { marginTop: 26, gap: 14, width: '100%' },
  padRow:      { flexDirection: 'row', justifyContent: 'center', gap: 14 },
  padBtn:      { width: 74, height: 74, borderRadius: 37, alignItems: 'center', justifyContent: 'center' },
  padSpacer:   { width: 74, height: 74 },
  padDigit:    { fontSize: 26, fontFamily: 'Inter_600SemiBold' },
});
