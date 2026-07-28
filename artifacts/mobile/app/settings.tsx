import React, { useState } from 'react';
import {
  Alert,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  View,
} from 'react-native';
import { router } from 'expo-router';
import { Feather } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { LanguagePicker } from '@/components/LanguagePicker';
import { useApp } from '@/context/AppContext';
import { useColors } from '@/hooks/useColors';

type FontSize = 'small' | 'medium' | 'large';

const FONT_SIZES: { label: string; value: FontSize }[] = [
  { label: 'Small', value: 'small' },
  { label: 'Medium', value: 'medium' },
  { label: 'Large', value: 'large' },
];

function SettingsRow({
  icon,
  label,
  description,
  right,
  onPress,
}: {
  icon: string;
  label: string;
  description?: string;
  right?: React.ReactNode;
  onPress?: () => void;
}) {
  const colors = useColors();
  return (
    <Pressable
      style={{
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 14,
        paddingHorizontal: 16,
        gap: 14,
      }}
      onPress={onPress}
    >
      <View
        style={{
          width: 36,
          height: 36,
          borderRadius: 10,
          backgroundColor: colors.primary + '18',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Feather name={icon as never} size={18} color={colors.primary} />
      </View>
      <View style={{ flex: 1 }}>
        <Text style={{ fontSize: 15, fontFamily: 'Inter_500Medium', color: colors.foreground }}>
          {label}
        </Text>
        {description && (
          <Text
            style={{
              fontSize: 12,
              fontFamily: 'Inter_400Regular',
              color: colors.mutedForeground,
              marginTop: 1,
            }}
          >
            {description}
          </Text>
        )}
      </View>
      {right ?? (onPress ? (
        <Feather name="chevron-right" size={16} color={colors.mutedForeground} />
      ) : null)}
    </Pressable>
  );
}

export default function SettingsScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;
  const { language, setLanguage } = useApp();

  const [fontSize, setFontSize] = useState<FontSize>('medium');
  const [highContrast, setHighContrast] = useState(false);
  const [screenReader, setScreenReader] = useState(false);
  const [showLangPicker, setShowLangPicker] = useState(false);

  const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: colors.background },
    header: {
      paddingTop: topPad + 12,
      paddingHorizontal: 20,
      paddingBottom: 16,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
      flexDirection: 'row',
      alignItems: 'center',
      gap: 12,
    },
    headerTitle: { flex: 1, fontSize: 20, fontFamily: 'Inter_700Bold', color: colors.foreground },
    scroll: { flex: 1 },
    scrollContent: { paddingBottom: Platform.OS === 'web' ? 34 : 40 },
    sectionLabel: {
      fontSize: 11,
      fontFamily: 'Inter_600SemiBold',
      color: colors.mutedForeground,
      textTransform: 'uppercase',
      letterSpacing: 0.8,
      paddingHorizontal: 16,
      paddingTop: 20,
      paddingBottom: 6,
    },
    card: {
      backgroundColor: colors.card,
      borderRadius: colors.radius,
      borderWidth: 1,
      borderColor: colors.border,
      marginHorizontal: 16,
      overflow: 'hidden',
    },
    divider: {
      height: 1,
      backgroundColor: colors.border,
      marginLeft: 66,
    },
    fontRow: {
      flexDirection: 'row',
      gap: 8,
      paddingHorizontal: 16,
      paddingVertical: 14,
    },
    fontChip: {
      flex: 1,
      alignItems: 'center',
      paddingVertical: 8,
      borderRadius: 10,
      borderWidth: 1.5,
      borderColor: colors.border,
      backgroundColor: colors.muted,
    },
    fontChipActive: {
      borderColor: colors.primary,
      backgroundColor: colors.primary + '14',
    },
    fontChipText: { fontSize: 13, fontFamily: 'Inter_500Medium', color: colors.mutedForeground },
    fontChipTextActive: { color: colors.primary, fontFamily: 'Inter_600SemiBold' },
    versionText: {
      fontSize: 12,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
      textAlign: 'center',
      paddingVertical: 20,
    },
    disclaimer: {
      backgroundColor: colors.muted,
      borderRadius: colors.radius,
      padding: 14,
      marginHorizontal: 16,
      marginTop: 16,
    },
    disclaimerText: {
      fontSize: 12,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
      lineHeight: 18,
    },
  });

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} hitSlop={12}>
          <Feather name="x" size={22} color={colors.foreground} />
        </Pressable>
        <Text style={styles.headerTitle}>Settings</Text>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent}>

        {/* Language */}
        <Text style={styles.sectionLabel}>Language</Text>
        <View style={styles.card}>
          <SettingsRow
            icon="globe"
            label="App Language"
            description={language.nativeName}
            onPress={() => setShowLangPicker(true)}
          />
        </View>

        {/* Accessibility */}
        <Text style={styles.sectionLabel}>Accessibility</Text>
        <View style={styles.card}>
          {/* Font size */}
          <View style={{ paddingHorizontal: 16, paddingTop: 14, paddingBottom: 4 }}>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: 14, marginBottom: 12 }}>
              <View
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: 10,
                  backgroundColor: colors.primary + '18',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Feather name="type" size={18} color={colors.primary} />
              </View>
              <View>
                <Text style={{ fontSize: 15, fontFamily: 'Inter_500Medium', color: colors.foreground }}>
                  Font Size
                </Text>
                <Text style={{ fontSize: 12, fontFamily: 'Inter_400Regular', color: colors.mutedForeground }}>
                  Adjust text size throughout the app
                </Text>
              </View>
            </View>
            <View style={styles.fontRow}>
              {FONT_SIZES.map((f) => (
                <Pressable
                  key={f.value}
                  style={[styles.fontChip, fontSize === f.value && styles.fontChipActive]}
                  onPress={() => {
                    setFontSize(f.value);
                    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                  }}
                >
                  <Text style={[styles.fontChipText, fontSize === f.value && styles.fontChipTextActive]}>
                    {f.label}
                  </Text>
                </Pressable>
              ))}
            </View>
          </View>

          <View style={styles.divider} />

          <SettingsRow
            icon="sun"
            label="High Contrast Mode"
            description="Increases color contrast for readability"
            right={
              <Switch
                value={highContrast}
                onValueChange={(v) => {
                  setHighContrast(v);
                  Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                  if (v) Alert.alert('High Contrast', 'High contrast mode is on. This setting will apply in a future update.');
                }}
                trackColor={{ false: colors.muted, true: colors.primary + '80' }}
                thumbColor={highContrast ? colors.primary : '#FFFFFF'}
              />
            }
          />

          <View style={styles.divider} />

          <SettingsRow
            icon="volume-2"
            label={`🔇 Screen Reader ${screenReader ? 'ON' : 'OFF'}`}
            description="Enhanced accessibility labels for screen readers"
            right={
              <Switch
                value={screenReader}
                onValueChange={(v) => {
                  setScreenReader(v);
                  Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                }}
                trackColor={{ false: colors.muted, true: colors.primary + '80' }}
                thumbColor={screenReader ? colors.primary : '#FFFFFF'}
              />
            }
          />
        </View>

        {/* About */}
        <Text style={styles.sectionLabel}>About</Text>
        <View style={styles.card}>
          <SettingsRow
            icon="shield"
            label="CivicShield Pro"
            description="v1.0.0 — Multilingual legal assistance"
          />
          <View style={styles.divider} />
          <SettingsRow
            icon="info"
            label="Privacy"
            description="All data stays on your device. Nothing is shared."
          />
          <View style={styles.divider} />
          <SettingsRow
            icon="heart"
            label="Built for the Community"
            description="Free legal education and assistance tools"
          />
        </View>

        {/* Disclaimer */}
        <View style={styles.disclaimer}>
          <Text style={styles.disclaimerText}>
            ⚠️ Disclaimer: CivicShield Pro provides general legal information, not legal advice. Laws vary by state and situation. Always consult a licensed attorney for guidance specific to your circumstances.
          </Text>
        </View>

        <Text style={styles.versionText}>CivicShield Pro · v1.0.0</Text>
      </ScrollView>

      <LanguagePicker
        visible={showLangPicker}
        selectedCode={language.code}
        onSelect={(lang) => {
          setLanguage(lang);
          setShowLangPicker(false);
        }}
        onClose={() => setShowLangPicker(false)}
      />
    </View>
  );
}
