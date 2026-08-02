import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  Animated,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Feather } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import * as LocalAuthentication from 'expo-local-authentication';
import { useColors } from '@/hooks/useColors';
import { useApp } from '@/context/AppContext';

interface Props {
  pin: string;
  onUnlock: () => void;
}

type Screen = 'biometric' | 'pin';

const MAX_ATTEMPTS     = 5;
const LOCKOUT_SECONDS  = 30;
const KEY_ATTEMPTS     = '@pin_attempts';
const KEY_LOCKED_UNTIL = '@pin_locked_until';

export default function PinLockScreen({ pin, onUnlock }: Props) {
  const colors = useColors();
  const { biometricUnlockEnabled } = useApp();

  const [screen, setScreen]           = useState<Screen>('biometric');
  const [bioAvailable, setBioAvailable] = useState(false);
  const [bioTypes, setBioTypes]       = useState<LocalAuthentication.AuthenticationType[]>([]);
  const [bioChecked, setBioChecked]   = useState(false);

  // PIN state
  const [entered, setEntered]   = useState('');
  const [pinError, setPinError] = useState(false);
  const shake = useRef(new Animated.Value(0)).current;

  // Brute-force lockout state
  const [hydrated, setHydrated]       = useState(false);  // true once AsyncStorage read completes
  const [attempts, setAttempts]       = useState(0);
  const [lockedUntil, setLockedUntil] = useState<number | null>(null);
  const [countdown, setCountdown]     = useState(0);
  const countdownRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // ── Load persisted lockout state on mount ─────────────────────────────────
  useEffect(() => {
    (async () => {
      try {
        const [storedAttempts, storedLocked] = await Promise.all([
          AsyncStorage.getItem(KEY_ATTEMPTS),
          AsyncStorage.getItem(KEY_LOCKED_UNTIL),
        ]);
        const parsedAttempts = storedAttempts ? parseInt(storedAttempts, 10) : 0;
        const parsedLocked   = storedLocked   ? parseInt(storedLocked,   10) : NaN;

        // Guard against corrupted/non-finite values
        const safeAttempts = Number.isFinite(parsedAttempts) ? parsedAttempts : 0;
        const safeExpiry   = Number.isFinite(parsedLocked)   ? parsedLocked   : null;

        setAttempts(safeAttempts);
        if (safeExpiry !== null && safeExpiry > Date.now()) {
          setLockedUntil(safeExpiry);
        } else if (safeExpiry !== null) {
          // Expired — clear it
          await AsyncStorage.multiRemove([KEY_ATTEMPTS, KEY_LOCKED_UNTIL]);
        }
      } catch {
        // ignore storage errors — fail open on read errors (not fail locked)
      } finally {
        setHydrated(true);
      }
    })();
  }, []);

  // ── Countdown ticker ──────────────────────────────────────────────────────
  useEffect(() => {
    if (lockedUntil === null) {
      if (countdownRef.current) {
        clearInterval(countdownRef.current);
        countdownRef.current = null;
      }
      setCountdown(0);
      return;
    }

    const tick = () => {
      const remaining = Math.ceil((lockedUntil - Date.now()) / 1000);
      if (remaining <= 0) {
        setLockedUntil(null);
        setAttempts(0);
        AsyncStorage.multiRemove([KEY_ATTEMPTS, KEY_LOCKED_UNTIL]).catch(() => {});
        if (countdownRef.current) {
          clearInterval(countdownRef.current);
          countdownRef.current = null;
        }
        setCountdown(0);
      } else {
        setCountdown(remaining);
      }
    };

    tick(); // run immediately
    countdownRef.current = setInterval(tick, 1000);
    return () => {
      if (countdownRef.current) clearInterval(countdownRef.current);
    };
  }, [lockedUntil]);

  // Treat as locked until storage is hydrated — prevents bypass during async read
  const isLocked = !hydrated || (lockedUntil !== null && lockedUntil > Date.now());

  // ── Biometric probe ────────────────────────────────────────────────────────
  const checkBio = useCallback(async () => {
    // Skip biometrics entirely if the user has opted out
    if (!biometricUnlockEnabled || Platform.OS === 'web') {
      setBioChecked(true);
      setScreen('pin');
      return;
    }
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
  }, [biometricUnlockEnabled]);

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
    if (isLocked) return;
    if (entered.length >= 4) return;
    if (Platform.OS !== 'web') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    const next = entered + d;
    setEntered(next);
    setPinError(false);

    if (next.length === 4) {
      if (next === pin) {
        // Success — clear lockout state
        AsyncStorage.multiRemove([KEY_ATTEMPTS, KEY_LOCKED_UNTIL]).catch(() => {});
        if (Platform.OS !== 'web') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        onUnlock();
      } else {
        if (Platform.OS !== 'web') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
        setPinError(true);
        triggerShake();

        const newAttempts = attempts + 1;
        setAttempts(newAttempts);

        if (newAttempts >= MAX_ATTEMPTS) {
          // Trigger lockout
          const expiry = Date.now() + LOCKOUT_SECONDS * 1000;
          setLockedUntil(expiry);
          AsyncStorage.multiSet([
            [KEY_ATTEMPTS,     String(newAttempts)],
            [KEY_LOCKED_UNTIL, String(expiry)],
          ]).catch(() => {});
          setEntered('');
          setPinError(false);
        } else {
          AsyncStorage.setItem(KEY_ATTEMPTS, String(newAttempts)).catch(() => {});
          setTimeout(() => { setEntered(''); setPinError(false); }, 700);
        }
      }
    }
  };

  const handleDelete = () => {
    if (isLocked) return;
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
  const dotColor = pinError ? '#E05252' : isLocked ? colors.mutedForeground : colors.primary;

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

        {/* Status messages */}
        {!hydrated ? (
          // Neutral loading state — don't reveal lockout info before storage is read
          <Text style={[s.errorText, { color: 'transparent' }]}> </Text>
        ) : lockedUntil !== null && lockedUntil > Date.now() ? (
          <View style={s.lockoutBox}>
            <Feather name="lock" size={15} color="#E05252" style={{ marginBottom: 4 }} />
            <Text style={s.lockoutTitle}>Too many wrong attempts</Text>
            <Text style={s.lockoutSub}>
              Try again in{' '}
              <Text style={s.lockoutCountdown}>{countdown}s</Text>
            </Text>
          </View>
        ) : (
          <>
            {pinError && (
              <Text style={s.errorText}>
                Incorrect PIN —{' '}
                {MAX_ATTEMPTS - attempts <= 1
                  ? '1 attempt remaining'
                  : `${MAX_ATTEMPTS - attempts} attempts remaining`}
              </Text>
            )}
          </>
        )}

        {/* Numpad */}
        <View style={[s.pad, isLocked && s.padDisabled]}>
          {ROWS.map((row, ri) => (
            <View key={ri} style={s.padRow}>
              {row.map((d, di) => {
                if (d === '') return <View key={di} style={s.padSpacer} />;
                if (d === '⌫') return (
                  <Pressable
                    key={di}
                    style={[s.padBtn, { backgroundColor: colors.muted, opacity: isLocked ? 0.35 : 1 }]}
                    onPress={handleDelete}
                    accessibilityRole="button"
                    accessibilityLabel="Delete"
                    disabled={isLocked}
                  >
                    <Feather name="delete" size={22} color={colors.foreground} />
                  </Pressable>
                );
                return (
                  <Pressable
                    key={di}
                    style={({ pressed }) => [
                      s.padBtn,
                      {
                        backgroundColor: colors.card,
                        borderWidth: 1,
                        borderColor: colors.border,
                        opacity: isLocked ? 0.35 : pressed ? 0.65 : 1,
                      },
                    ]}
                    onPress={() => handleDigit(d)}
                    accessibilityRole="button"
                    accessibilityLabel={d}
                    disabled={isLocked}
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

  // Lockout banner
  lockoutBox:      { alignItems: 'center', marginBottom: 10, paddingVertical: 10, paddingHorizontal: 16, borderRadius: 10, backgroundColor: '#E0525218' },
  lockoutTitle:    { fontSize: 13, fontFamily: 'Inter_600SemiBold', color: '#E05252', marginBottom: 2 },
  lockoutSub:      { fontSize: 13, fontFamily: 'Inter_400Regular', color: '#E05252' },
  lockoutCountdown:{ fontFamily: 'Inter_700Bold' },

  pad:         { marginTop: 26, gap: 14, width: '100%' },
  padDisabled: { opacity: 0.5 },
  padRow:      { flexDirection: 'row', justifyContent: 'center', gap: 14 },
  padBtn:      { width: 74, height: 74, borderRadius: 37, alignItems: 'center', justifyContent: 'center' },
  padSpacer:   { width: 74, height: 74 },
  padDigit:    { fontSize: 26, fontFamily: 'Inter_600SemiBold' },
});
