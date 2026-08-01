import React, { useEffect, useRef, useState } from 'react';
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
import { useColors } from '@/hooks/useColors';

interface Props {
  pin: string;
  onUnlock: () => void;
}

export default function PinLockScreen({ pin, onUnlock }: Props) {
  const colors = useColors();
  const [entered, setEntered] = useState('');
  const [error, setError] = useState(false);
  const shake = useRef(new Animated.Value(0)).current;

  const triggerShake = () => {
    shake.setValue(0);
    Animated.sequence([
      Animated.timing(shake, { toValue: 8, duration: 60, useNativeDriver: true }),
      Animated.timing(shake, { toValue: -8, duration: 60, useNativeDriver: true }),
      Animated.timing(shake, { toValue: 8, duration: 60, useNativeDriver: true }),
      Animated.timing(shake, { toValue: 0, duration: 60, useNativeDriver: true }),
    ]).start();
  };

  const handleDigit = (d: string) => {
    if (entered.length >= 4) return;
    if (Platform.OS !== 'web') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    const next = entered + d;
    setEntered(next);
    setError(false);

    if (next.length === 4) {
      if (next === pin) {
        if (Platform.OS !== 'web') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        onUnlock();
      } else {
        if (Platform.OS !== 'web') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
        setError(true);
        triggerShake();
        setTimeout(() => { setEntered(''); setError(false); }, 700);
      }
    }
  };

  const handleDelete = () => {
    setEntered(prev => prev.slice(0, -1));
    setError(false);
  };

  const ROWS = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['', '0', '⌫'],
  ];

  const dotColor = error ? '#E05252' : colors.primary;

  return (
    <View style={[s.container, { backgroundColor: colors.background }]}>
      <View style={s.inner}>
        {/* Icon + Title */}
        <View style={[s.iconWrap, { backgroundColor: colors.primary + '18' }]}>
          <Feather name="shield" size={32} color={colors.primary} />
        </View>
        <Text style={[s.title, { color: colors.foreground }]}>CivicShield Pro</Text>
        <Text style={[s.subtitle, { color: colors.mutedForeground }]}>
          Enter your PIN to access the app
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

        {error && (
          <Text style={s.errorText}>Incorrect PIN — try again</Text>
        )}

        {/* Numpad */}
        <View style={s.pad}>
          {ROWS.map((row, ri) => (
            <View key={ri} style={s.padRow}>
              {row.map((d, di) => {
                if (d === '') return <View key={di} style={s.padBtnSpacer} />;
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
      </View>
    </View>
  );
}

const s = StyleSheet.create({
  container:    { flex: 1, alignItems: 'center', justifyContent: 'center' },
  inner:        { width: '80%', maxWidth: 300, alignItems: 'center' },
  iconWrap:     { width: 72, height: 72, borderRadius: 36, alignItems: 'center', justifyContent: 'center', marginBottom: 16 },
  title:        { fontSize: 22, fontFamily: 'Inter_700Bold', marginBottom: 4 },
  subtitle:     { fontSize: 13, fontFamily: 'Inter_400Regular', marginBottom: 36, textAlign: 'center', lineHeight: 19 },
  dotsRow:      { flexDirection: 'row', gap: 18, marginBottom: 10 },
  dot:          { width: 16, height: 16, borderRadius: 8, borderWidth: 2 },
  errorText:    { fontSize: 13, fontFamily: 'Inter_500Medium', color: '#E05252', marginBottom: 8 },
  pad:          { marginTop: 28, gap: 14, width: '100%' },
  padRow:       { flexDirection: 'row', justifyContent: 'center', gap: 14 },
  padBtn:       { width: 74, height: 74, borderRadius: 37, alignItems: 'center', justifyContent: 'center' },
  padBtnSpacer: { width: 74, height: 74 },
  padDigit:     { fontSize: 26, fontFamily: 'Inter_600SemiBold' },
});
