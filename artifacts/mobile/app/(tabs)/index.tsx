import React, { useState } from 'react';
import {
  Image,
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
  const { language, setLanguage, encounters } = useApp();
  const [showLangPicker, setShowLangPicker] = useState(false);

  const topPad = Platform.OS === 'web' ? 67 : insets.top;

  const features = [
    {
      title: '📄 Document Analyzer',
      description: 'Paste legal text to extract deadlines, penalties, required actions, and generate a QR code.',
      iconName: 'file-text',
      accentColor: '#C9A050',
      route: '/(tabs)/docs',
    },
    {
      title: '🌐 Real-Time Translation',
      description: 'Instantly translate text into 14 languages during encounters or for legal documents.',
      iconName: 'globe',
      accentColor: '#C97B8E',
      route: '/(tabs)/translate',
    },
    {
      title: '📚 Know Your Rights',
      description: 'Learn civil rights for traffic stops, police encounters, arrests, immigration, and more.',
      iconName: 'book-open',
      accentColor: '#A07888',
      route: '/(tabs)/rights',
    },
    {
      title: '📍 Find Legal Resources',
      description: 'Locate nearby legal aid, hotlines, and support organizations. Find resources near you.',
      iconName: 'map-pin',
      accentColor: '#C9A050',
      route: '/(tabs)/resources',
    },
    {
      title: '📞 Crisis Hotlines',
      description: '24/7 emergency, legal, immigration, domestic violence, and LGBTQ+ lines.',
      iconName: 'phone-call',
      accentColor: '#E05252',
      route: '/(tabs)/resources',
    },
    {
      title: '🗂️ Encounter Log',
      description: 'Privately document police interactions with details, location, and outcomes.',
      iconName: 'clipboard',
      accentColor: '#C97B8E',
      route: '/log-list',
    },
  ];

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: colors.background,
    },
    header: {
      paddingTop: topPad + 8,
      paddingHorizontal: 20,
      paddingBottom: 14,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
      backgroundColor: colors.background,
    },
    headerRow: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
    },
    logoRow: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 10,
    },
    logoImage: {
      width: 40,
      height: 40,
      borderRadius: 8,
    },
    appName: {
      fontSize: 22,
      fontFamily: 'Inter_700Bold',
      color: colors.primary,
      letterSpacing: -0.4,
    },
    tagline: {
      fontSize: 12,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
      marginTop: 1,
    },
    headerActions: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 8,
    },
    langBtn: {
      flexDirection: 'row',
      alignItems: 'center',
      backgroundColor: colors.muted,
      borderRadius: 20,
      paddingHorizontal: 11,
      paddingVertical: 6,
      gap: 5,
    },
    langBtnText: {
      fontSize: 12,
      fontFamily: 'Inter_500Medium',
      color: colors.foreground,
    },
    settingsBtn: {
      width: 34,
      height: 34,
      borderRadius: 17,
      backgroundColor: colors.muted,
      alignItems: 'center',
      justifyContent: 'center',
    },
    scroll: {
      flex: 1,
    },
    scrollContent: {
      padding: 16,
      paddingBottom: Platform.OS === 'web' ? 34 : 100,
    },
    emergencyBanner: {
      backgroundColor: '#E05252',
      borderRadius: colors.radius,
      flexDirection: 'row',
      alignItems: 'center',
      padding: 14,
      marginBottom: 16,
      gap: 10,
    },
    emergencyText: {
      flex: 1,
      fontSize: 14,
      fontFamily: 'Inter_600SemiBold',
      color: '#FFFFFF',
    },
    emergencyNumber: {
      fontSize: 20,
      fontFamily: 'Inter_700Bold',
      color: '#FFFFFF',
    },
    logBanner: {
      backgroundColor: colors.primary + '12',
      borderRadius: colors.radius,
      borderWidth: 1,
      borderColor: colors.primary + '30',
      flexDirection: 'row',
      alignItems: 'center',
      padding: 14,
      marginBottom: 16,
      gap: 10,
    },
    logBannerText: {
      flex: 1,
    },
    logBannerTitle: {
      fontSize: 14,
      fontFamily: 'Inter_600SemiBold',
      color: colors.primary,
    },
    logBannerSub: {
      fontSize: 12,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
      marginTop: 1,
    },
    sectionTitle: {
      fontSize: 12,
      fontFamily: 'Inter_600SemiBold',
      color: colors.mutedForeground,
      textTransform: 'uppercase',
      letterSpacing: 0.8,
      marginBottom: 12,
    },
  });

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerRow}>
          <View style={styles.logoRow}>
            <Image
              source={require('@/assets/images/icon.png')}
              style={styles.logoImage}
              resizeMode="contain"
            />
            <View>
              <Text style={styles.appName}>CivicShield Pro</Text>
              <Text style={styles.tagline}>Know your rights. Stay protected.</Text>
            </View>
          </View>
          <View style={styles.headerActions}>
            <Pressable style={styles.langBtn} onPress={() => setShowLangPicker(true)}>
              <Feather name="globe" size={13} color={colors.primary} />
              <Text style={styles.langBtnText}>{language.nativeName}</Text>
              <Feather name="chevron-down" size={11} color={colors.mutedForeground} />
            </Pressable>
            <Pressable style={styles.settingsBtn} onPress={() => router.push('/settings')}>
              <Feather name="settings" size={16} color={colors.mutedForeground} />
            </Pressable>
          </View>
        </View>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Emergency banner */}
        <Pressable style={styles.emergencyBanner} onPress={() => router.push('/(tabs)/resources')}>
          <Feather name="alert-triangle" size={20} color="#FFFFFF" />
          <Text style={styles.emergencyText}>In an emergency or crisis?</Text>
          <Text style={styles.emergencyNumber}>911</Text>
        </Pressable>

        {/* Encounter log shortcut */}
        <Pressable style={styles.logBanner} onPress={() => router.push('/log-list')}>
          <Feather name="clipboard" size={20} color={colors.primary} />
          <View style={styles.logBannerText}>
            <Text style={styles.logBannerTitle}>Encounter Log</Text>
            <Text style={styles.logBannerSub}>
              {encounters.length === 0
                ? 'No encounters logged yet — tap to add one'
                : `${encounters.length} encounter${encounters.length === 1 ? '' : 's'} logged`}
            </Text>
          </View>
          <Feather name="chevron-right" size={16} color={colors.mutedForeground} />
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
