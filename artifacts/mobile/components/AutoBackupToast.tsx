/**
 * AutoBackupToast
 * A subtle green banner that slides in from the top for ~2.5 s
 * whenever a new auto-backup is written.
 */
import React, { useEffect, useRef } from 'react';
import { Animated, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Feather } from '@expo/vector-icons';
import { useApp } from '@/context/AppContext';

const VISIBLE_MS  = 2500;
const ANIMATE_MS  = 280;

export function AutoBackupToast() {
  const { lastAutoBackupAt } = useApp();
  const insets  = useSafeAreaInsets();
  const slideY  = useRef(new Animated.Value(-80)).current;
  const opacity = useRef(new Animated.Value(0)).current;

  // Track which timestamp we last showed so we don't re-show on re-renders
  const shownAt = useRef<string | null>(null);

  useEffect(() => {
    if (!lastAutoBackupAt || lastAutoBackupAt === shownAt.current) return;
    shownAt.current = lastAutoBackupAt;

    // Slide in
    Animated.parallel([
      Animated.timing(slideY,  { toValue: 0,   duration: ANIMATE_MS, useNativeDriver: true }),
      Animated.timing(opacity, { toValue: 1,   duration: ANIMATE_MS, useNativeDriver: true }),
    ]).start(() => {
      // Hold, then slide out
      setTimeout(() => {
        Animated.parallel([
          Animated.timing(slideY,  { toValue: -80, duration: ANIMATE_MS, useNativeDriver: true }),
          Animated.timing(opacity, { toValue: 0,   duration: ANIMATE_MS, useNativeDriver: true }),
        ]).start();
      }, VISIBLE_MS);
    });
  }, [lastAutoBackupAt, slideY, opacity]);

  return (
    <Animated.View
      pointerEvents="none"
      style={[
        styles.toast,
        { top: insets.top + 12, transform: [{ translateY: slideY }], opacity },
      ]}
      accessibilityLiveRegion="polite"
      accessibilityLabel="Auto-backup saved"
    >
      <View style={styles.iconWrap}>
        <Feather name="check-circle" size={16} color="#FFFFFF" />
      </View>
      <Text style={styles.text}>Auto-backup saved</Text>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  toast: {
    position: 'absolute',
    alignSelf: 'center',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: '#2D9B6F',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 24,
    shadowColor: '#000',
    shadowOpacity: 0.18,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 3 },
    elevation: 6,
    zIndex: 9999,
  },
  iconWrap: {
    width: 20,
    height: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    fontSize: 14,
    fontFamily: 'Inter_500Medium',
    color: '#FFFFFF',
  },
});
