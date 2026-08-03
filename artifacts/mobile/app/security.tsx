import React, { useEffect, useState } from 'react';
import {
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  View,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { router } from 'expo-router';
import { Feather } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import * as LocalAuthentication from 'expo-local-authentication';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useApp } from '@/context/AppContext';
import { useColors } from '@/hooks/useColors';
import { useRTL } from '@/hooks/useRTL';
import { useT } from '@/hooks/useTranslation';

const LOCK_TIMEOUT_OPTIONS = [
  { label: 'Immediately', value: 0 },
  { label: '30 sec',      value: 0.5 },
  { label: '1 min',       value: 1 },
  { label: '5 min',       value: 5 },
  { label: '15 min',      value: 15 },
  { label: 'Never',       value: -1 },
];

const DISMISS_KEY = 'civicshield_lock_prompt_dismissed';

export default function SecurityScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const { t } = useT();
  const { rowDir, backIcon } = useRTL();
  const { fs, appLockEnabled, appPin, setAppLock, lockTimeout, setLockTimeout,
          biometricUnlockEnabled, setBiometricUnlockEnabled } = useApp();

  const [bioAvailable, setBioAvailable] = useState(false);
  useEffect(() => {
    if (Platform.OS === 'web') return;
    (async () => {
      try {
        const hasHw    = await LocalAuthentication.hasHardwareAsync();
        const enrolled = await LocalAuthentication.isEnrolledAsync();
        setBioAvailable(hasHw && enrolled);
      } catch {
        setBioAvailable(false);
      }
    })();
  }, []);
  const topPad = Platform.OS === 'web' ? 67 : insets.top;

  const [dismissed, setDismissed]   = useState(false);
  const [showSetup, setShowSetup]   = useState(false);
  const [pinStep, setPinStep]       = useState<'enter' | 'confirm'>('enter');
  const [pinInput, setPinInput]     = useState('');
  const [pinConfirm, setPinConfirm] = useState('');
  const [pinError, setPinError]     = useState('');

  useEffect(() => {
    AsyncStorage.getItem(DISMISS_KEY).then(v => { if (v === '1') setDismissed(true); });
  }, []);

  const dismissForever = () => {
    AsyncStorage.setItem(DISMISS_KEY, '1');
    setDismissed(true);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
  };
  const dismissSession = () => {
    setDismissed(true);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
  };

  const handlePinChange = (val: string) => {
    const digits = val.replace(/\D/g, '').slice(0, 4);
    setPinError('');
    if (pinStep === 'enter') {
      setPinInput(digits);
      if (digits.length === 4) setTimeout(() => setPinStep('confirm'), 80);
    } else {
      setPinConfirm(digits);
      if (digits.length === 4) {
        setTimeout(() => {
          if (digits === pinInput) {
            setAppLock(true, pinInput);
            setShowSetup(false);
            setPinInput(''); setPinConfirm(''); setPinStep('enter');
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
          } else {
            setPinError('PINs do not match — try again');
            setPinConfirm('');
            setPinStep('enter');
            setPinInput('');
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
          }
        }, 80);
      }
    }
  };

  const disableLock = () => {
    setAppLock(false, '');
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
  };

  const startPinSetup = () => {
    setPinInput(''); setPinConfirm(''); setPinStep('enter'); setPinError('');
    setShowSetup(true);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
  };

  const showRecommendation = !appLockEnabled && !dismissed;

  return (
    <KeyboardAvoidingView style={{ flex: 1, backgroundColor: colors.background }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      {/* Header */}
      <View style={{ paddingTop: topPad + 12, paddingHorizontal: 20, paddingBottom: 14,
        borderBottomWidth: 1, borderBottomColor: colors.border,
        flexDirection: rowDir, alignItems: 'center', gap: 12 }}>
        <Pressable onPress={() => router.back()} hitSlop={12} accessibilityRole="button" accessibilityLabel="Back">
          <Feather name={backIcon} size={22} color={colors.foreground} />
        </Pressable>
        <Text style={{ flex: 1, fontSize: fs(20), fontFamily: 'Inter_700Bold', color: colors.foreground }}>
          🔒 {t('security.title')}
        </Text>
      </View>

      <ScrollView contentContainerStyle={{ padding: 16, paddingBottom: 80 }} showsVerticalScrollIndicator={false}>

        {/* ── Recommendation banner (only when no lock set and not dismissed) ── */}
        {showRecommendation && (
          <View style={{ backgroundColor: colors.primary + '12', borderRadius: colors.radius,
            borderWidth: 1, borderColor: colors.primary + '30', padding: 16, marginBottom: 16 }}>
            <View style={{ flexDirection: rowDir, alignItems: 'flex-start', gap: 12, marginBottom: 14 }}>
              <View style={{ width: 40, height: 40, borderRadius: 20, backgroundColor: colors.primary + '20',
                alignItems: 'center', justifyContent: 'center' }}>
                <Feather name="shield" size={20} color={colors.primary} />
              </View>
              <Text style={{ flex: 1, fontSize: fs(14), fontFamily: 'Inter_400Regular',
                color: colors.foreground, lineHeight: 21 }}>
                {t('security.recommend')}
              </Text>
            </View>
            {/* Set up button */}
            <Pressable
              style={{ backgroundColor: colors.primary, borderRadius: 10, paddingVertical: 12,
                alignItems: 'center', marginBottom: 10 }}
              onPress={startPinSetup}
              accessibilityRole="button">
              <Text style={{ fontSize: fs(14), fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' }}>
                {t('security.setup_lock')}
              </Text>
            </Pressable>
            {/* Dismiss row */}
            <View style={{ flexDirection: rowDir, gap: 8 }}>
              <Pressable
                style={{ flex: 1, borderWidth: 1, borderColor: colors.border, borderRadius: 10,
                  paddingVertical: 10, alignItems: 'center' }}
                onPress={dismissSession}
                accessibilityRole="button">
                <Text style={{ fontSize: fs(13), fontFamily: 'Inter_500Medium', color: colors.mutedForeground }}>
                  {t('security.dismiss')}
                </Text>
              </Pressable>
              <Pressable
                style={{ flex: 1, borderWidth: 1, borderColor: colors.border, borderRadius: 10,
                  paddingVertical: 10, alignItems: 'center' }}
                onPress={dismissForever}
                accessibilityRole="button">
                <Text style={{ fontSize: fs(13), fontFamily: 'Inter_500Medium', color: colors.mutedForeground }}>
                  {t('security.dont_show')}
                </Text>
              </Pressable>
            </View>
          </View>
        )}

        {/* ── Lock enabled status ── */}
        {appLockEnabled && (
          <View style={{ backgroundColor: '#5A9E6F14', borderRadius: colors.radius,
            borderWidth: 1, borderColor: '#5A9E6F40', padding: 14,
            flexDirection: rowDir, alignItems: 'center', gap: 12, marginBottom: 16 }}>
            <Feather name="check-circle" size={20} color="#5A9E6F" />
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: fs(14), fontFamily: 'Inter_600SemiBold', color: '#5A9E6F' }}>
                {t('security.lock_enabled')}
              </Text>
              <Text style={{ fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground }}>
                {t('security.lock_enabled_desc')}
              </Text>
            </View>
          </View>
        )}

        {/* ── App Lock toggle ── */}
        <View style={{ backgroundColor: colors.card, borderRadius: colors.radius,
          borderWidth: 1, borderColor: colors.border, marginBottom: 12 }}>
          {/* Toggle row */}
          <View style={{ flexDirection: rowDir, alignItems: 'center', padding: 14, gap: 12 }}>
            <View style={{ width: 36, height: 36, borderRadius: 10, backgroundColor: colors.primary + '18',
              alignItems: 'center', justifyContent: 'center' }}>
              <Feather name="lock" size={18} color={colors.primary} />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: fs(15), fontFamily: 'Inter_500Medium', color: colors.foreground }}>
                {t('security.app_lock')}
              </Text>
              <Text style={{ fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 1 }}>
                {appLockEnabled ? t('security.app_lock_on') : t('security.app_lock_off')}
              </Text>
            </View>
            <Switch
              value={appLockEnabled}
              onValueChange={(v) => { if (v) startPinSetup(); else disableLock(); }}
              trackColor={{ false: colors.muted, true: colors.primary + '80' }}
              thumbColor={appLockEnabled ? colors.primary : '#F4F4F4'}
            />
          </View>

          {/* PIN setup inline */}
          {showSetup && (
            <View style={{ padding: 14, borderTopWidth: 1, borderTopColor: colors.border }}>
              <Text style={{ fontSize: fs(13), fontFamily: 'Inter_600SemiBold', color: colors.foreground, marginBottom: 4 }}>
                {pinStep === 'enter' ? '🔐 Set a 4-digit PIN' : '✅ Confirm your PIN'}
              </Text>
              <Text style={{ fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginBottom: 12 }}>
                {pinStep === 'enter' ? 'Enter 4 digits — it will auto-advance when done.' : 'Re-enter the same PIN to confirm.'}
              </Text>
              <View style={{ flexDirection: 'row', gap: 14, marginBottom: 12 }}>
                {[0, 1, 2, 3].map(i => {
                  const filled = pinStep === 'enter' ? i < pinInput.length : i < pinConfirm.length;
                  return (
                    <View key={i} style={{ width: 14, height: 14, borderRadius: 7, borderWidth: 2,
                      borderColor: pinError ? '#E05252' : colors.primary,
                      backgroundColor: filled ? (pinError ? '#E05252' : colors.primary) : 'transparent' }} />
                  );
                })}
              </View>
              {pinError ? <Text style={{ color: '#E05252', fontSize: fs(12), fontFamily: 'Inter_500Medium', marginBottom: 8 }}>{pinError}</Text> : null}
              <TextInput
                style={{ backgroundColor: colors.background, borderWidth: 1, borderColor: colors.border,
                  borderRadius: 10, paddingHorizontal: 14, paddingVertical: 11, fontSize: fs(16),
                  fontFamily: 'Inter_400Regular', color: colors.foreground, letterSpacing: 8 }}
                value={pinStep === 'enter' ? pinInput : pinConfirm}
                onChangeText={handlePinChange}
                keyboardType="number-pad"
                secureTextEntry
                maxLength={4}
                autoFocus
                placeholder="••••"
                placeholderTextColor={colors.mutedForeground}
              />
              <Pressable onPress={() => setShowSetup(false)} style={{ marginTop: 12, alignItems: 'center', paddingVertical: 10 }}>
                <Text style={{ fontSize: fs(13), fontFamily: 'Inter_500Medium', color: colors.mutedForeground }}>Cancel</Text>
              </Pressable>
            </View>
          )}

          {/* Change PIN (only when lock is on and no setup in progress) */}
          {appLockEnabled && !showSetup && (
            <>
              <View style={{ height: 1, backgroundColor: colors.border }} />
              <Pressable
                style={{ flexDirection: rowDir, alignItems: 'center', padding: 14, gap: 12 }}
                onPress={startPinSetup}
                accessibilityRole="button">
                <View style={{ width: 36, height: 36, borderRadius: 10, backgroundColor: colors.primary + '18',
                  alignItems: 'center', justifyContent: 'center' }}>
                  <Feather name="edit-2" size={18} color={colors.primary} />
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={{ fontSize: fs(15), fontFamily: 'Inter_500Medium', color: colors.foreground }}>
                    {t('security.change_pin')}
                  </Text>
                  <Text style={{ fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 1 }}>
                    {t('security.change_pin_desc')}
                  </Text>
                </View>
                <Feather name="chevron-right" size={16} color={colors.mutedForeground} />
              </Pressable>

              {/* Biometric toggle — only shown when hardware is available */}
              {bioAvailable && (
                <>
                  <View style={{ height: 1, backgroundColor: colors.border }} />
                  <View style={{ flexDirection: rowDir, alignItems: 'center', padding: 14, gap: 12 }}>
                    <View style={{ width: 36, height: 36, borderRadius: 10, backgroundColor: colors.primary + '18',
                      alignItems: 'center', justifyContent: 'center' }}>
                      <Feather name="aperture" size={18} color={colors.primary} />
                    </View>
                    <View style={{ flex: 1 }}>
                      <Text style={{ fontSize: fs(15), fontFamily: 'Inter_500Medium', color: colors.foreground }}>
                        Use biometrics to unlock
                      </Text>
                      <Text style={{ fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 1 }}>
                        {biometricUnlockEnabled ? 'Face ID / fingerprint offered first' : 'PIN only — biometrics skipped'}
                      </Text>
                    </View>
                    <Switch
                      value={biometricUnlockEnabled}
                      onValueChange={(v) => {
                        setBiometricUnlockEnabled(v);
                        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
                      }}
                      trackColor={{ false: colors.muted, true: colors.primary + '80' }}
                      thumbColor={biometricUnlockEnabled ? colors.primary : '#F4F4F4'}
                      accessibilityLabel="Use biometrics to unlock"
                    />
                  </View>
                </>
              )}
            </>
          )}
        </View>

        {/* ── Lock timeout (only when lock enabled) ── */}
        {appLockEnabled && (
          <View style={{ backgroundColor: colors.card, borderRadius: colors.radius,
            borderWidth: 1, borderColor: colors.border, padding: 14, marginBottom: 12 }}>
            <View style={{ flexDirection: rowDir, alignItems: 'center', gap: 12, marginBottom: 12 }}>
              <View style={{ width: 36, height: 36, borderRadius: 10, backgroundColor: colors.primary + '18',
                alignItems: 'center', justifyContent: 'center' }}>
                <Feather name="clock" size={18} color={colors.primary} />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={{ fontSize: fs(15), fontFamily: 'Inter_500Medium', color: colors.foreground }}>
                  {t('security.lock_after')}
                </Text>
                <Text style={{ fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 1 }}>
                  {t('security.lock_after_desc')}
                </Text>
              </View>
            </View>
            <View style={{ flexDirection: rowDir, flexWrap: 'wrap', gap: 8 }}>
              {LOCK_TIMEOUT_OPTIONS.map((opt) => {
                const active = lockTimeout === opt.value;
                return (
                  <Pressable
                    key={opt.value}
                    onPress={() => { setLockTimeout(opt.value); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); }}
                    style={{ paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20,
                      borderWidth: 1.5,
                      borderColor: active ? colors.primary : colors.border,
                      backgroundColor: active ? colors.primary + '14' : colors.muted }}
                    accessibilityRole="radio"
                    accessibilityState={{ selected: active }}>
                    <Text style={{ fontSize: fs(13), fontFamily: active ? 'Inter_600SemiBold' : 'Inter_400Regular',
                      color: active ? colors.primary : colors.mutedForeground }}>
                      {opt.label}
                    </Text>
                  </Pressable>
                );
              })}
            </View>
          </View>
        )}

      </ScrollView>
    </KeyboardAvoidingView>
  );
}
