import React from 'react';
import { Alert, Platform, StyleSheet, useColorScheme, View } from 'react-native';
import { useColors } from '@/hooks/useColors';
import { useT } from '@/hooks/useTranslation';
import { logSelectionGuard } from '@/utils/logSelectionGuard';
import { Feather } from '@expo/vector-icons';
import { BlurView } from 'expo-blur';
import { Tabs } from 'expo-router';
import { SymbolView } from 'expo-symbols';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

// Note: NativeTabs (expo-router/unstable-native-tabs) does not expose a
// pre-navigation tabPress interceptor (screenListeners is not in its API), so
// ClassicTabLayout is used unconditionally to guarantee the discard-selection
// confirmation can always preventDefault() on any tab switch.

export default function TabLayout() {
  return <ClassicTabLayout />;
}

function ClassicTabLayout() {
  const colors = useColors();
  const { t } = useT();
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';
  const isIOS = Platform.OS === 'ios';
  const isWeb = Platform.OS === 'web';
  const safeAreaInsets = useSafeAreaInsets();

  // screenListeners intercepts tabPress on each screen's own tab before navigation.
  // route.name is the tab being pressed; when the log tab is currently active and
  // the guard is armed, we call e.preventDefault() and show the confirmation dialog.
  const screenListeners = ({ navigation, route }: { navigation: any; route: any }) => ({
    tabPress: (e: any) => {
      const state = navigation.getState();
      const activeTab = state?.routes?.[state?.index]?.name;
      if (activeTab === 'log' && route.name !== 'log' && logSelectionGuard.isActive) {
        e.preventDefault();
        Alert.alert(t('log.discard_title'), t('log.discard_msg'), [
          { text: t('log.discard_stay'), style: 'cancel' },
          {
            text: t('log.discard_exit'),
            style: 'destructive',
            onPress: () => {
              logSelectionGuard.clear();      // clears selection in log-list.tsx
              navigation.navigate(route.name); // proceed to intended tab
            },
          },
        ]);
      }
    },
  });

  return (
    <Tabs
      screenListeners={screenListeners}
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.tabIconDefault,
        tabBarStyle: {
          position: 'absolute',
          backgroundColor: isIOS ? 'transparent' : colors.background,
          borderTopWidth: isWeb ? 1 : 0,
          borderTopColor: colors.border,
          elevation: 0,
          paddingBottom: safeAreaInsets.bottom,
          ...(isWeb ? { height: 84 } : {}),
        },
        tabBarBackground: () =>
          isIOS ? (
            <BlurView
              intensity={100}
              tint={isDark ? 'dark' : 'light'}
              style={StyleSheet.absoluteFill}
            />
          ) : isWeb ? (
            <View
              style={[StyleSheet.absoluteFill, { backgroundColor: colors.background }]}
            />
          ) : null,
        tabBarLabelStyle: {
          fontFamily: 'Inter_500Medium',
          fontSize: 10,
        },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: t('nav.home'),
          tabBarIcon: ({ color }) =>
            isIOS ? <SymbolView name="house" tintColor={color} size={22} /> : <Feather name="home" size={22} color={color} />,
        }}
      />
      <Tabs.Screen
        name="rights"
        options={{
          title: t('nav.rights'),
          tabBarIcon: ({ color }) =>
            isIOS ? <SymbolView name="book" tintColor={color} size={22} /> : <Feather name="book-open" size={22} color={color} />,
        }}
      />
      <Tabs.Screen
        name="resources"
        options={{
          title: t('nav.resources'),
          tabBarIcon: ({ color }) =>
            isIOS ? <SymbolView name="location" tintColor={color} size={22} /> : <Feather name="map-pin" size={22} color={color} />,
        }}
      />
      <Tabs.Screen
        name="hub"
        options={{
          title: t('nav.hub'),
          tabBarIcon: ({ color }) =>
            isIOS ? <SymbolView name="square.grid.2x2" tintColor={color} size={22} /> : <Feather name="grid" size={22} color={color} />,
        }}
      />
      <Tabs.Screen
        name="log"
        options={{
          title: t('nav.log'),
          tabBarIcon: ({ color }) =>
            isIOS ? <SymbolView name="list.clipboard" tintColor={color} size={22} /> : <Feather name="clipboard" size={22} color={color} />,
        }}
      />
      <Tabs.Screen
        name="translate"
        options={{
          title: t('nav.translate'),
          tabBarIcon: ({ color }) =>
            isIOS ? <SymbolView name="globe" tintColor={color} size={22} /> : <Feather name="globe" size={22} color={color} />,
        }}
      />
      <Tabs.Screen
        name="docs"
        options={{
          title: t('nav.docs'),
          tabBarIcon: ({ color }) =>
            isIOS ? <SymbolView name="doc.text" tintColor={color} size={22} /> : <Feather name="file-text" size={22} color={color} />,
        }}
      />
      <Tabs.Screen
        name="community"
        options={{
          title: t('nav.community'),
          tabBarIcon: ({ color }) =>
            isIOS ? <SymbolView name="bubble.left.and.bubble.right" tintColor={color} size={22} /> : <Feather name="message-circle" size={22} color={color} />,
        }}
      />
    </Tabs>
  );
}

