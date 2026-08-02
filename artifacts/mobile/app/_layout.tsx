import React, { useEffect, useRef } from 'react';
import { AppState, AppStateStatus } from 'react-native';
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

  // Timestamp (ms) when the app moved to background
  const backgroundedAt = useRef<number | null>(null);

  useEffect(() => {
    const handleAppStateChange = (nextState: AppStateStatus) => {
      if (nextState === 'background' || nextState === 'inactive') {
        // Record the moment we left foreground
        backgroundedAt.current = Date.now();
      } else if (nextState === 'active') {
        // Came back — check elapsed time against the threshold
        if (appLockEnabled && appPin && backgroundedAt.current !== null) {
          if (lockTimeout === -1) {
            // Never re-lock
          } else {
            const elapsedMs = Date.now() - backgroundedAt.current;
            const thresholdMs = lockTimeout * 60 * 1000;
            if (elapsedMs >= thresholdMs) {
              setUnlocked(false);
            }
          }
        }
        backgroundedAt.current = null;
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
