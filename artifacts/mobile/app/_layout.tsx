import React, { useEffect } from 'react';
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

SplashScreen.preventAutoHideAsync();

const queryClient = new QueryClient();

function RootLayoutNav() {
  return (
    <Stack screenOptions={{ headerBackTitle: 'Back' }}>
      <Stack.Screen name="(tabs)"        options={{ headerShown: false }} />
      <Stack.Screen name="new-log"       options={{ headerShown: false, presentation: 'modal' }} />
      <Stack.Screen name="log-list"      options={{ headerShown: false }} />
      <Stack.Screen name="settings"      options={{ headerShown: false, presentation: 'modal' }} />
      <Stack.Screen name="tour"          options={{ headerShown: false, presentation: 'modal' }} />
      <Stack.Screen name="forum"         options={{ headerShown: false }} />
      <Stack.Screen name="resource-hub"  options={{ headerShown: false }} />
      <Stack.Screen name="qrcode-screen" options={{ headerShown: false }} />
    </Stack>
  );
}

/** Sits inside AppProvider so it can read lock state from context. */
function AppShell() {
  const { hydrated, appLockEnabled, appPin } = useApp();
  const [unlocked, setUnlocked] = React.useState(false);

  // While AsyncStorage is loading, render nothing (SplashScreen covers it)
  if (!hydrated) return null;

  if (appLockEnabled && appPin && !unlocked) {
    return <PinLockScreen pin={appPin} onUnlock={() => setUnlocked(true)} />;
  }
  return <RootLayoutNav />;
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
