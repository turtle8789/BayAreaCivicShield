import React, { useState } from 'react';
import {
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { router } from 'expo-router';
import { Feather } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { FeatureCard } from '@/components/FeatureCard';
import { LanguagePicker } from '@/components/LanguagePicker';
import { useApp } from '@/context/AppContext';
import { useColors } from '@/hooks/useColors';

export default function HomeScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const { language, setLanguage } = useApp();
  const [showLangPicker, setShowLangPicker] = useState(false);

  const topPad = Platform.OS === 'web' ? 67 : insets.top;

  const features = [
    {
      title: 'Real-Time Translation',
      description: 'Instantly translate speech or text into 14 languages to communicate clearly.',
      iconName: 'globe',
      accentColor: '#C97C5D',
      route: '/(tabs)/translate',
    },
    {
      title: 'Know Your Rights',
      description: 'Learn civil rights for traffic stops, police encounters, arrests, and more.',
      iconName: 'book-open',
      accentColor: '#A7B8A0',
      route: '/(tabs)/rights',
    },
    {
      title: 'Legal Resources',
      description: 'Find nearby legal aid organizations, public defenders, and nonprofits.',
      iconName: 'map-pin',
      accentColor: '#9B6B8E',
      route: '/(tabs)/resources',
    },
    {
      title: 'Encounter Log',
      description: 'Document police interactions with details, location, and outcomes.',
      iconName: 'clipboard',
      accentColor: '#C97C5D',
      route: '/(tabs)/log',
    },
    {
      title: 'Crisis Hotlines',
      description: '24/7 emergency, legal, immigration, domestic violence, and LGBTQ+ lines.',
      iconName: 'phone-call',
      accentColor: '#E05252',
      route: '/(tabs)/resources',
    },
  ];

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: colors.background,
    },
    header: {
      paddingTop: topPad + 12,
      paddingHorizontal: 20,
      paddingBottom: 16,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
      backgroundColor: colors.background,
    },
    headerRow: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
    },
    appName: {
      fontSize: 22,
      fontFamily: 'Inter_700Bold',
      color: colors.primary,
      letterSpacing: -0.4,
    },
    tagline: {
      fontSize: 13,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
      marginTop: 2,
    },
    langBtn: {
      flexDirection: 'row',
      alignItems: 'center',
      backgroundColor: colors.muted,
      borderRadius: 20,
      paddingHorizontal: 12,
      paddingVertical: 7,
      gap: 6,
    },
    langBtnText: {
      fontSize: 13,
      fontFamily: 'Inter_500Medium',
      color: colors.foreground,
    },
    scroll: {
      flex: 1,
    },
    scrollContent: {
      padding: 20,
      paddingBottom: Platform.OS === 'web' ? 34 : 24,
    },
    sectionTitle: {
      fontSize: 13,
      fontFamily: 'Inter_600SemiBold',
      color: colors.mutedForeground,
      textTransform: 'uppercase',
      letterSpacing: 0.8,
      marginBottom: 14,
    },
    emergencyBanner: {
      backgroundColor: '#E05252' + '14',
      borderWidth: 1,
      borderColor: '#E05252' + '30',
      borderRadius: colors.radius,
      flexDirection: 'row',
      alignItems: 'center',
      padding: 14,
      marginBottom: 20,
      gap: 10,
    },
    emergencyText: {
      flex: 1,
      fontSize: 13,
      fontFamily: 'Inter_500Medium',
      color: '#E05252',
    },
    emergencyNumber: {
      fontSize: 16,
      fontFamily: 'Inter_700Bold',
      color: '#E05252',
    },
  });

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerRow}>
          <View>
            <Text style={styles.appName}>CivicShield Pro</Text>
            <Text style={styles.tagline}>Know your rights. Stay protected.</Text>
          </View>
          <Pressable style={styles.langBtn} onPress={() => setShowLangPicker(true)}>
            <Feather name="globe" size={14} color={colors.primary} />
            <Text style={styles.langBtnText}>{language.nativeName}</Text>
            <Feather name="chevron-down" size={12} color={colors.mutedForeground} />
          </Pressable>
        </View>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Emergency banner */}
        <Pressable style={styles.emergencyBanner} onPress={() => router.push('/(tabs)/resources')}>
          <Feather name="alert-circle" size={20} color="#E05252" />
          <Text style={styles.emergencyText}>In an emergency or crisis?</Text>
          <Text style={styles.emergencyNumber}>911</Text>
        </Pressable>

        <Text style={styles.sectionTitle}>Tools & Resources</Text>

        {features.map((f) => (
          <FeatureCard
            key={f.title}
            title={f.title}
            description={f.description}
            iconName={f.iconName}
            accentColor={f.accentColor}
            onPress={() => router.push(f.route as never)}
          />
        ))}
      </ScrollView>

      <LanguagePicker
        visible={showLangPicker}
        selectedCode={language.code}
        onSelect={setLanguage}
        onClose={() => setShowLangPicker(false)}
      />
    </View>
  );
}
