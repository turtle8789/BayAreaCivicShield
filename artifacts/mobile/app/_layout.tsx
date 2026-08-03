import React, { useEffect, useRef, useState } from 'react';
import {
  AppState,
  AppStateStatus,
  Modal,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { KeyboardProvider } from 'react-native-keyboard-controller';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import {
  Inter_400Regular,
  Inter_500Medium,
  Inter_600SemiBold,
  Inter_700Bold,
  useFonts,
} from '@expo-google-fonts/inter';
import { router, Stack } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { AppProvider, useApp } from '@/context/AppContext';
import PinLockScreen from '@/components/PinLockScreen';
import { AutoBackupToast } from '@/components/AutoBackupToast';
import { useColors } from '@/hooks/useColors';
import {
  hasExceededLockTimeout,
  shouldLockOnStoredTimestamp,
} from '@/utils/pinLockTiming';

/** Persisted keys */
const STORAGE_BACKGROUNDED_AT          = 'civicshield_backgrounded_at';
const STORAGE_SECURITY_PROMPT_NEVER    = 'civicshield_security_prompt_never';

SplashScreen.preventAutoHideAsync();

const queryClient = new QueryClient();

function RootLayoutNav() {
  return (
    <Stack screenOptions={{ headerBackTitle: 'Back' }}>
      <Stack.Screen name="(tabs)"        options={{ headerShown: false }} />
      <Stack.Screen name="new-log"       options={{ headerShown: false, presentation: 'modal' }} />
      <Stack.Screen name="log-list"      options={{ headerShown: false }} />
      <Stack.Screen name="settings"      options={{ headerShown: false, presentation: 'modal' }} />
      <Stack.Screen name="security"      options={{ headerShown: false }} />
      <Stack.Screen name="tour"          options={{ headerShown: false, presentation: 'modal' }} />
      <Stack.Screen name="forum"         options={{ headerShown: false }} />
      <Stack.Screen name="resource-hub"  options={{ headerShown: false }} />
      <Stack.Screen name="qrcode-screen" options={{ headerShown: false }} />
    </Stack>
  );
}

// ── Security prompt shown on launch when no PIN is set up ─────────────────────

function SecurityPromptModal({
  visible,
  onSetUp,
  onDismiss,
  onDismissForever,
}: {
  visible: boolean;
  onSetUp: () => void;
  onDismiss: () => void;
  onDismissForever: () => void;
}) {
  const colors = useColors();

  const s = StyleSheet.create({
    backdrop: {
      flex: 1,
      backgroundColor: 'rgba(0,0,0,0.55)',
      justifyContent: 'center',
      alignItems: 'center',
      padding: 28,
    },
    card: {
      width: '100%',
      maxWidth: 360,
      backgroundColor: colors.card,
      borderRadius: 20,
      padding: 24,
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 8 },
      shadowOpacity: 0.18,
      shadowRadius: 20,
      elevation: 12,
    },
    icon: {
      fontSize: 44,
      textAlign: 'center',
      marginBottom: 12,
    },
    title: {
      fontSize: 19,
      fontFamily: 'Inter_700Bold',
      color: colors.foreground,
      textAlign: 'center',
      marginBottom: 10,
      lineHeight: 25,
    },
    body: {
      fontSize: 14,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
      textAlign: 'center',
      lineHeight: 21,
      marginBottom: 22,
    },
    setupBtn: {
      backgroundColor: colors.primary,
      borderRadius: 13,
      paddingVertical: 14,
      alignItems: 'center',
      marginBottom: 12,
    },
    setupBtnText: {
      fontSize: 15,
      fontFamily: 'Inter_600SemiBold',
      color: '#FFFFFF',
    },
    row: {
      flexDirection: 'row',
      gap: 8,
    },
    dismissBtn: {
      flex: 1,
      backgroundColor: colors.muted,
      borderRadius: 13,
      paddingVertical: 12,
      alignItems: 'center',
      borderWidth: 1,
      borderColor: colors.border,
    },
    dismissBtnText: {
      fontSize: 13,
      fontFamily: 'Inter_500Medium',
      color: colors.foreground,
      textAlign: 'center',
      lineHeight: 18,
    },
    neverText: {
      color: colors.mutedForeground,
    },
  });

  return (
    <Modal
      visible={visible}
      transparent
      animationType="fade"
      statusBarTranslucent
      onRequestClose={onDismiss}
    >
      <View style={s.backdrop}>
        <View style={s.card}>
          <Text style={s.icon}>🔒</Text>

          <Text style={s.title}>Protect Your Records</Text>

          <Text style={s.body}>
            For the safety of the app and your encounter records, it's
            recommended to set up a lock using your PIN, fingerprint, or Face ID.
            You can dismiss this if you'd prefer not to.
          </Text>

          {/* Primary action */}
          <Pressable
            style={({ pressed }) => [s.setupBtn, { opacity: pressed ? 0.85 : 1 }]}
            onPress={onSetUp}
            accessibilityRole="button"
            accessibilityLabel="Set up app lock"
          >
            <Text style={s.setupBtnText}>Set Up App Lock</Text>
          </Pressable>

          {/* Secondary actions */}
          <View style={s.row}>
            <Pressable
              style={({ pressed }) => [s.dismissBtn, { opacity: pressed ? 0.75 : 1 }]}
              onPress={onDismiss}
              accessibilityRole="button"
              accessibilityLabel="Dismiss"
            >
              <Text style={s.dismissBtnText}>Dismiss</Text>
            </Pressable>

            <Pressable
              style={({ pressed }) => [s.dismissBtn, { opacity: pressed ? 0.75 : 1 }]}
              onPress={onDismissForever}
              accessibilityRole="button"
              accessibilityLabel="Dismiss and don't show again"
            >
              <Text style={[s.dismissBtnText, s.neverText]}>
                Don't Show{'\n'}Again
              </Text>
            </Pressable>
          </View>
        </View>
      </View>
    </Modal>
  );
}

// ── App shell ─────────────────────────────────────────────────────────────────

/** Sits inside AppProvider so it can read lock state from context. */
function AppShell() {
  const { hydrated, appLockEnabled, appPin, lockTimeout } = useApp();
  const [unlocked, setUnlocked]                 = useState(false);
  const [showSecurityPrompt, setShowSecurityPrompt] = useState(false);

  // In-memory cache of the backgrounded timestamp; also mirrored to AsyncStorage
  // so it survives process suspension (e.g. screen lock without a background event).
  const backgroundedAt = useRef<number | null>(null);

  // On mount: restore any persisted backgroundedAt from a previous session so that
  // if the device screen locked and the OS suspended the process mid-session we can
  // still enforce the timeout when the user returns.
  useEffect(() => {
    if (!appLockEnabled || !appPin || lockTimeout === -1) return;

    AsyncStorage.getItem(STORAGE_BACKGROUNDED_AT).then((stored) => {
      if (shouldLockOnStoredTimestamp(stored, lockTimeout, Date.now())) {
        setUnlocked(false);
      }
      // Clear once consumed so it doesn't affect future launches
      if (stored) {
        AsyncStorage.removeItem(STORAGE_BACKGROUNDED_AT).catch(() => {});
      }
    }).catch(() => {});
  // Run once after hydration; values come from context state at mount time.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hydrated]);

  useEffect(() => {
    const handleAppStateChange = (nextState: AppStateStatus) => {
      if (nextState === 'background' || nextState === 'inactive') {
        const now = Date.now();
        backgroundedAt.current = now;
        AsyncStorage.setItem(STORAGE_BACKGROUNDED_AT, String(now)).catch(() => {});
      } else if (nextState === 'active') {
        if (appLockEnabled && appPin) {
          const ts = backgroundedAt.current;
          if (ts !== null && hasExceededLockTimeout(Date.now() - ts, lockTimeout)) {
            setUnlocked(false);
          }
        }
        backgroundedAt.current = null;
        AsyncStorage.removeItem(STORAGE_BACKGROUNDED_AT).catch(() => {});
      }
    };

    const subscription = AppState.addEventListener('change', handleAppStateChange);
    return () => subscription.remove();
  }, [appLockEnabled, appPin, lockTimeout]);

  // Show the security setup prompt once after hydration if no PIN is configured
  // and the user hasn't permanently dismissed it.
  useEffect(() => {
    if (!hydrated) return;
    if (appLockEnabled && appPin) return; // Lock already set up — never prompt

    AsyncStorage.getItem(STORAGE_SECURITY_PROMPT_NEVER).then((val) => {
      if (val !== 'true') {
        setShowSecurityPrompt(true);
      }
    }).catch(() => {});
  // Only run once after initial hydration
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hydrated]);

  const handleSecuritySetUp = () => {
    setShowSecurityPrompt(false);
    // Small delay so the modal animates out before the push
    setTimeout(() => router.push('/security'), 150);
  };

  const handleSecurityDismiss = () => {
    setShowSecurityPrompt(false);
  };

  const handleSecurityDismissForever = () => {
    setShowSecurityPrompt(false);
    AsyncStorage.setItem(STORAGE_SECURITY_PROMPT_NEVER, 'true').catch(() => {});
  };

  // While AsyncStorage is loading, render nothing (SplashScreen covers it)
  if (!hydrated) return null;

  if (appLockEnabled && appPin && !unlocked) {
    return <PinLockScreen pin={appPin} onUnlock={() => setUnlocked(true)} />;
  }

  return (
    <>
      <RootLayoutNav />
      <AutoBackupToast />
      <SecurityPromptModal
        visible={showSecurityPrompt}
        onSetUp={handleSecuritySetUp}
        onDismiss={handleSecurityDismiss}
        onDismissForever={handleSecurityDismissForever}
      />
    </>
  );
}

// ── Root ──────────────────────────────────────────────────────────────────────

export default function RootLayout() {
  const [fontsLoaded, fontError] = useFonts({
    Inter_400Regular,
    Inter_500Medium,
    Inter_600SemiBold,
    Inter_700Bold,
  });

  useEffect(() => {
    if (fontsLoaded || fontError) SplashScreen.hideAsync();
  }, [fontsLoaded, fontError]);

  if (!fontsLoaded && !fontError) return null;

  return (
    <SafeAreaProvider>
      <ErrorBoundary>
        <QueryClientProvider client={queryClient}>
          <GestureHandlerRootView>
            <KeyboardProvider>
              <AppProvider>
                <AppShell />
              </AppProvider>
            </KeyboardProvider>
          </GestureHandlerRootView>
        </QueryClientProvider>
      </ErrorBoundary>
    </SafeAreaProvider>
  );
}
