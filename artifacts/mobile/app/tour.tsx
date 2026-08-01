import React, { useState } from 'react';
import {
  Dimensions,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { router } from 'expo-router';
import { Feather } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useApp } from '@/context/AppContext';
import { useColors } from '@/hooks/useColors';
import { useRTL } from '@/hooks/useRTL';
import { useT } from '@/hooks/useTranslation';

const { width } = Dimensions.get('window');

interface TourStep {
  emoji: string;
  title: string;
  description: string;
  tip: string;
  color: string;
  icon: string;
  tab?: string;
}

export default function TourScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const { setTourCompleted, fs } = useApp();
  const { t } = useT();
  const { rowDir, arrowIcon } = useRTL();
  const [step, setStep] = useState(0);

  const STEPS: TourStep[] = [
    {
      emoji: '👋',
      title: t('tour.welcome_title'),
      description: t('tour.welcome_desc'),
      tip: t('tour.welcome_tip'),
      color: '#C97B8E',
      icon: 'shield',
    },
    {
      emoji: '📄',
      title: t('tour.docs_title'),
      description: t('tour.docs_desc'),
      tip: t('tour.docs_tip'),
      color: '#C9A050',
      icon: 'file-text',
      tab: '/(tabs)/docs',
    },
    {
      emoji: '🌐',
      title: t('tour.translate_title'),
      description: t('tour.translate_desc'),
      tip: t('tour.translate_tip'),
      color: '#C97B8E',
      icon: 'globe',
      tab: '/(tabs)/translate',
    },
    {
      emoji: '📚',
      title: t('tour.rights_title'),
      description: t('tour.rights_desc'),
      tip: t('tour.rights_tip'),
      color: '#A07888',
      icon: 'book-open',
      tab: '/(tabs)/rights',
    },
    {
      emoji: '📍',
      title: t('tour.resources_title'),
      description: t('tour.resources_desc'),
      tip: t('tour.resources_tip'),
      color: '#5A9E6F',
      icon: 'map-pin',
      tab: '/(tabs)/resources',
    },
    {
      emoji: '🗂️',
      title: t('tour.log_title'),
      description: t('tour.log_desc'),
      tip: t('tour.log_tip'),
      color: '#C97B8E',
      icon: 'clipboard',
      tab: '/log-list',
    },
    {
      emoji: '✅',
      title: t('tour.ready_title'),
      description: t('tour.ready_desc'),
      tip: t('tour.ready_tip'),
      color: '#5A9E6F',
      icon: 'check-circle',
    },
  ];

  const topPad = Platform.OS === 'web' ? 67 : insets.top;
  const bottomPad = Platform.OS === 'web' ? 34 : insets.bottom;
  const current = STEPS[step];
  const isLast = step === STEPS.length - 1;
  const isFirst = step === 0;

  const handleNext = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    if (isLast) {
      handleFinish();
    } else {
      setStep((s) => s + 1);
    }
  };

  const handleBack = () => {
    if (!isFirst) {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      setStep((s) => s - 1);
    }
  };

  const handleFinish = () => {
    setTourCompleted(true);
    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    router.back();
  };

  const goToFeature = () => {
    if (current.tab) {
      setTourCompleted(true);
      router.replace(current.tab as never);
    }
  };

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: colors.background,
    },
    header: {
      paddingTop: topPad + 12,
      paddingHorizontal: 20,
      paddingBottom: 12,
      flexDirection: rowDir,
      alignItems: 'center',
      justifyContent: 'space-between',
    },
    skipBtn: {
      paddingVertical: 6,
      paddingHorizontal: 12,
      borderRadius: 20,
      backgroundColor: colors.muted,
    },
    skipText: {
      fontSize: fs(13),
      fontFamily: 'Inter_500Medium',
      color: colors.mutedForeground,
    },
    stepIndicator: {
      flexDirection: rowDir,
      gap: 6,
      alignItems: 'center',
    },
    dot: {
      width: 7,
      height: 7,
      borderRadius: 4,
    },
    body: {
      flex: 1,
      paddingHorizontal: 24,
      justifyContent: 'center',
    },
    emojiCircle: {
      width: 100,
      height: 100,
      borderRadius: 50,
      alignItems: 'center',
      justifyContent: 'center',
      alignSelf: 'center',
      marginBottom: 28,
    },
    emoji: {
      fontSize: 46,
    },
    title: {
      fontSize: fs(26),
      fontFamily: 'Inter_700Bold',
      color: colors.foreground,
      textAlign: 'center',
      marginBottom: 16,
      lineHeight: 34,
    },
    description: {
      fontSize: fs(16),
      fontFamily: 'Inter_400Regular',
      color: colors.foreground,
      textAlign: 'center',
      lineHeight: 24,
      marginBottom: 24,
    },
    tipCard: {
      backgroundColor: current.color + '12',
      borderRadius: colors.radius,
      borderWidth: 1,
      borderColor: current.color + '30',
      padding: 14,
      flexDirection: rowDir,
      gap: 10,
      marginBottom: 24,
    },
    tipText: {
      flex: 1,
      fontSize: fs(13),
      fontFamily: 'Inter_400Regular',
      color: colors.foreground,
      lineHeight: 19,
    },
    tryBtn: {
      flexDirection: rowDir,
      alignItems: 'center',
      justifyContent: 'center',
      gap: 8,
      borderRadius: colors.radius,
      paddingVertical: 12,
      borderWidth: 1.5,
      borderColor: current.color,
      marginBottom: 12,
    },
    tryBtnText: {
      fontSize: fs(14),
      fontFamily: 'Inter_600SemiBold',
      color: current.color,
    },
    footer: {
      paddingHorizontal: 24,
      paddingBottom: bottomPad + 20,
      gap: 12,
    },
    nextBtn: {
      borderRadius: colors.radius,
      paddingVertical: 16,
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: rowDir,
      gap: 8,
    },
    nextBtnText: {
      fontSize: fs(16),
      fontFamily: 'Inter_600SemiBold',
      color: '#FFFFFF',
    },
    backBtn: {
      borderRadius: colors.radius,
      paddingVertical: 12,
      alignItems: 'center',
    },
    backBtnText: {
      fontSize: fs(14),
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
    },
  });

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable style={styles.skipBtn} onPress={handleFinish} accessibilityLabel="Skip tour" accessibilityRole="button">
          <Text style={styles.skipText}>{t('tour.skip')}</Text>
        </Pressable>
        <View style={styles.stepIndicator}>
          {STEPS.map((_, i) => (
            <View
              key={i}
              style={[
                styles.dot,
                {
                  backgroundColor: i === step ? current.color : colors.muted,
                  width: i === step ? 20 : 7,
                },
              ]}
            />
          ))}
        </View>
        <Text style={{ fontSize: fs(13), fontFamily: 'Inter_500Medium', color: colors.mutedForeground }}>
          {step + 1}/{STEPS.length}
        </Text>
      </View>

      {/* Main content */}
      <View style={styles.body}>
        {/* Emoji circle */}
        <View style={[styles.emojiCircle, { backgroundColor: current.color + '18' }]}>
          <Text style={styles.emoji}>{current.emoji}</Text>
        </View>

        <Text style={styles.title} accessibilityRole="header">{current.title}</Text>
        <Text style={styles.description}>{current.description}</Text>

        {/* Tip card */}
        <View style={styles.tipCard}>
          <Feather name="zap" size={16} color={current.color} style={{ marginTop: 1 }} />
          <Text style={styles.tipText}>{current.tip}</Text>
        </View>

        {/* "Try it now" button for feature steps */}
        {current.tab && (
          <Pressable style={styles.tryBtn} onPress={goToFeature} accessibilityLabel={`Go to ${current.title}`} accessibilityRole="button">
            <Feather name={current.icon as never} size={16} color={current.color} />
            <Text style={styles.tryBtnText}>{t('tour.try_now')}</Text>
          </Pressable>
        )}
      </View>

      {/* Footer nav */}
      <View style={styles.footer}>
        <Pressable
          style={[styles.nextBtn, { backgroundColor: current.color }]}
          onPress={handleNext}
          accessibilityLabel={isLast ? 'Finish tour' : 'Next step'}
          accessibilityRole="button"
        >
          <Text style={styles.nextBtnText}>
            {isLast ? t('tour.get_started') : t('tour.next')}
          </Text>
          {!isLast && <Feather name={arrowIcon} size={18} color="#FFFFFF" />}
        </Pressable>

        {!isFirst && (
          <Pressable style={styles.backBtn} onPress={handleBack} accessibilityLabel="Previous step" accessibilityRole="button">
            <Text style={styles.backBtnText}>{t('tour.back')}</Text>
          </Pressable>
        )}
      </View>
    </View>
  );
}
