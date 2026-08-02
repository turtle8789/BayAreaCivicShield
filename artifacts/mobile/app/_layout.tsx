import React, { useEffect, useRef } from 'react';
import { AppState, AppStateStatus } from 'react-native';
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
import { Stack } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { AppProvider, useApp } from '@/context/AppContext';
import PinLockScreen from '@/components/PinLockScreen';
import { AutoBackupToast } from '@/components/AutoBackupToast';

/** AsyncStorage key used to persist the backgrounded timestamp across process suspensions. */
const STORAGE_BACKGROUNDED_AT = 'civicshield_backgrounded_at';

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

/** Sits inside AppProvider so it can read lock state from context. */
function AppShell() {
  const { hydrated, appLockEnabled, appPin, lockTimeout } = useApp();
  const [unlocked, setUnlocked] = React.useState(false);

  // In-memory cache of the backgrounded timestamp; also mirrored to AsyncStorage
  // so it survives process suspension (e.g. screen lock without a background event).
  const backgroundedAt = useRef<number | null>(null);

  // On mount: restore any persisted backgroundedAt from a previous session so that
  // if the device screen locked and the OS suspended the process mid-session we can
  // still enforce the timeout when the user returns.
  useEffect(() => {
    if (!appLockEnabled || !appPin || lockTimeout === -1) return;

    AsyncStorage.getItem(STORAGE_BACKGROUNDED_AT).then((stored) => {
      if (stored) {
        const ts = Number(stored);
        if (!Number.isNaN(ts)) {
          const elapsedMs = Date.now() - ts;
          const thresholdMs = lockTimeout * 60 * 1000;
          if (elapsedMs >= thresholdMs) {
            setUnlocked(false);
          }
        }
        // Clear once consumed so it doesn't affect future launches
        AsyncStorage.removeItem(STORAGE_BACKGROUNDED_AT).catch(() => {});
      }
    }).catch(() => {});
  // Run once after hydration; values come from context state at mount time.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hydrated]);

  useEffect(() => {
    const handleAppStateChange = (nextState: AppStateStatus) => {
      if (nextState === 'background' || nextState === 'inactive') {
        // Record the moment we left foreground — both in memory and in storage
        // so the timestamp survives process suspension (e.g. screen-off events
        // that don't reliably fire before the OS freezes the process).
        const now = Date.now();
        backgroundedAt.current = now;
        AsyncStorage.setItem(STORAGE_BACKGROUNDED_AT, String(now)).catch(() => {});
      } else if (nextState === 'active') {
        // Came back — check elapsed time against the threshold.
        // Use in-memory ref first; fall back to nothing (the mount-time effect
        // already handled the persisted value when we resumed after a cold start).
        if (appLockEnabled && appPin) {
          const ts = backgroundedAt.current;
          if (ts !== null && lockTimeout !== -1) {
            const elapsedMs = Date.now() - ts;
            const thresholdMs = lockTimeout * 60 * 1000;
            if (elapsedMs >= thresholdMs) {
              setUnlocked(false);
            }
          }
        }
        // Clear both the ref and the persisted value now that we're active again
        backgroundedAt.current = null;
        AsyncStorage.removeItem(STORAGE_BACKGROUNDED_AT).catch(() => {});
      }
    };

    const subscription = AppState.addEventListener('change', handleAppStateChange);
    return () => subscription.remove();
  }, [appLockEnabled, appPin, lockTimeout]);

  // While AsyncStorage is loading, render nothing (SplashScreen covers it)
  if (!hydrated) return null;

  if (appLockEnabled && appPin && !unlocked) {
    return <PinLockScreen pin={appPin} onUnlock={() => setUnlocked(true)} />;
  }
  return (
    <>
      <RootLayoutNav />
      <AutoBackupToast />
    </>
  );
}

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
