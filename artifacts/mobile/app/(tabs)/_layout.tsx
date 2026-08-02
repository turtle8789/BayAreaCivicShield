import React from 'react';
import { Platform, StyleSheet, Text, useColorScheme, View } from 'react-native';
import { useColors } from '@/hooks/useColors';
import { useT } from '@/hooks/useTranslation';
import { Feather } from '@expo/vector-icons';
import { BlurView } from 'expo-blur';
import { isLiquidGlassAvailable } from 'expo-glass-effect';
import { Tabs } from 'expo-router';
import { Icon, NativeTabs } from 'expo-router/unstable-native-tabs';
import { SymbolView } from 'expo-symbols';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

// NativeTabLayout uses plain Text for labels so we can translate them
function NativeTabLayout() {
  const { t } = useT();
  return (
    <NativeTabs>
      <NativeTabs.Trigger name="index">
        <Icon sf={{ default: 'house', selected: 'house.fill' }} />
        <Text>{t('nav.home')}</Text>
      </NativeTabs.Trigger>
      <NativeTabs.Trigger name="rights">
        <Icon sf={{ default: 'book', selected: 'book.fill' }} />
        <Text>{t('nav.rights')}</Text>
      </NativeTabs.Trigger>
      <NativeTabs.Trigger name="resources">
        <Icon sf={{ default: 'location', selected: 'location.fill' }} />
        <Text>{t('nav.resources')}</Text>
      </NativeTabs.Trigger>
      <NativeTabs.Trigger name="hub">
        <Icon sf={{ default: 'square.grid.2x2', selected: 'square.grid.2x2.fill' }} />
        <Text>{t('nav.hub')}</Text>
      </NativeTabs.Trigger>
      <NativeTabs.Trigger name="log">
        <Icon sf={{ default: 'list.clipboard', selected: 'list.clipboard.fill' }} />
        <Text>{t('nav.log')}</Text>
      </NativeTabs.Trigger>
      <NativeTabs.Trigger name="translate">
        <Icon sf={{ default: 'globe', selected: 'globe.fill' }} />
        <Text>{t('nav.translate')}</Text>
      </NativeTabs.Trigger>
      <NativeTabs.Trigger name="docs">
        <Icon sf={{ default: 'doc.text', selected: 'doc.text.fill' }} />
        <Text>{t('nav.docs')}</Text>
      </NativeTabs.Trigger>
      <NativeTabs.Trigger name="community">
        <Icon sf={{ default: 'bubble.left.and.bubble.right', selected: 'bubble.left.and.bubble.right.fill' }} />
        <Text>{t('nav.community')}</Text>
      </NativeTabs.Trigger>
    </NativeTabs>
  );
}

function ClassicTabLayout() {
  const colors = useColors();
  const { t } = useT();
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';
  const isIOS = Platform.OS === 'ios';
  const isWeb = Platform.OS === 'web';
  const safeAreaInsets = useSafeAreaInsets();

  return (
    <Tabs
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

export default function TabLayout() {
  if (isLiquidGlassAvailable()) {
    return <NativeTabLayout />;
  }
  return <ClassicTabLayout />;
}
