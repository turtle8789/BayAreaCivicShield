import React, { useState } from 'react';
import {
  Platform,
  Pressable,
  ScrollView,
  Share,
  Text,
  View,
} from 'react-native';
import { router } from 'expo-router';
import { Feather } from '@expo/vector-icons';
import Constants from 'expo-constants';
import * as Clipboard from 'expo-clipboard';
import * as Haptics from 'expo-haptics';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import QRCode from 'react-native-qrcode-svg';
import { useColors } from '@/hooks/useColors';
import { useRTL } from '@/hooks/useRTL';
import { useT } from '@/hooks/useTranslation';

// ─── Derive the Expo Go connection URL ───────────────────────────────────────

function getExpoGoUrl(): string {
  // expo-constants exposes the dev server host during development
  const hostUri: string | undefined =
    (Constants.expoConfig as { hostUri?: string } | null)?.hostUri ??
    (Constants as { manifest?: { debuggerHost?: string } }).manifest?.debuggerHost;

  if (hostUri) {
    // hostUri is "hostname:port" — Expo Go needs exp:// scheme
    return `exp://${hostUri}`;
  }

  // On web preview, use the current window host
  if (Platform.OS === 'web' && typeof window !== 'undefined') {
    return `exp://${window.location.hostname}`;
  }

  // Fallback: instructions URL
  return 'https://expo.dev/go';
}

export default function QRCodeScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const { t } = useT();
  const { rowDir, backIcon } = useRTL();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;

  const expoUrl = getExpoGoUrl();
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await Clipboard.setStringAsync(expoUrl);
    setCopied(true);
    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleShare = async () => {
    await Share.share({ message: expoUrl, url: expoUrl });
  };

  const isRealUrl = expoUrl.startsWith('exp://') && expoUrl !== 'exp://expo.dev/go';

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      {/* Header */}
      <View style={{
        paddingTop: topPad + 12, paddingHorizontal: 20, paddingBottom: 16,
        borderBottomWidth: 1, borderBottomColor: colors.border,
        flexDirection: rowDir, alignItems: 'center', gap: 12,
      }}>
        <Pressable onPress={() => router.back()} hitSlop={12} accessibilityRole="button" accessibilityLabel={t('common.back')}>
          <Feather name={backIcon} size={22} color={colors.foreground} />
        </Pressable>
        <Text style={{ flex: 1, fontSize: 20, fontFamily: 'Inter_700Bold', color: colors.foreground }}>
          {t('qr.title')}
        </Text>
      </View>

      <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: 24, alignItems: 'center', flexGrow: 1 }}>

        {/* Subtitle */}
        <Text style={{ fontSize: 14, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, textAlign: 'center', lineHeight: 21, marginBottom: 28 }}>
          {t('qr.subtitle')}
        </Text>

        {/* QR code card */}
        <View style={{
          backgroundColor: '#FFFFFF',
          borderRadius: 20,
          padding: 24,
          marginBottom: 24,
          shadowColor: '#000',
          shadowOffset: { width: 0, height: 4 },
          shadowOpacity: 0.08,
          shadowRadius: 16,
          elevation: 4,
          alignItems: 'center',
        }}>
          <QRCode
            value={expoUrl}
            size={220}
            color="#1A1A2E"
            backgroundColor="#FFFFFF"
            logo={require('@/assets/images/icon.png')}
            logoSize={44}
            logoBackgroundColor="#FFFFFF"
            logoBorderRadius={8}
          />
        </View>

        {/* Status indicator */}
        <View style={{ flexDirection: rowDir, alignItems: 'center', gap: 8, marginBottom: 20 }}>
          <View style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: isRealUrl ? '#5A9E6F' : '#C9A050' }} />
          <Text style={{ fontSize: 13, fontFamily: 'Inter_500Medium', color: isRealUrl ? '#5A9E6F' : '#C9A050' }}>
            {isRealUrl ? 'Live dev server detected' : 'Connect to a dev server first'}
          </Text>
        </View>

        {/* URL box */}
        <View style={{ width: '100%', backgroundColor: colors.muted, borderRadius: colors.radius, borderWidth: 1, borderColor: colors.border, padding: 14, marginBottom: 12 }}>
          <Text style={{ fontSize: 11, fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase', letterSpacing: 0.7, marginBottom: 6 }}>
            {t('qr.url_label')}
          </Text>
          <Text style={{ fontSize: 13, fontFamily: 'Inter_500Medium', color: colors.foreground, lineHeight: 18 }} selectable>
            {expoUrl}
          </Text>
        </View>

        {/* Action buttons */}
        <View style={{ flexDirection: rowDir, gap: 10, width: '100%', marginBottom: 24 }}>
          <Pressable
            style={({ pressed }) => ({
              flex: 1, flexDirection: rowDir, alignItems: 'center', justifyContent: 'center', gap: 7,
              backgroundColor: copied ? '#5A9E6F' : colors.primary,
              borderRadius: colors.radius, paddingVertical: 13,
              opacity: pressed ? 0.88 : 1,
            })}
            onPress={handleCopy}
            accessibilityRole="button"
            accessibilityLabel={t('qr.copy_url')}
          >
            <Feather name={copied ? 'check' : 'copy'} size={16} color="#FFFFFF" />
            <Text style={{ fontSize: 14, fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' }}>
              {copied ? t('qr.copied') : t('qr.copy_url')}
            </Text>
          </Pressable>
          {Platform.OS !== 'web' && (
            <Pressable
              style={({ pressed }) => ({
                flex: 1, flexDirection: rowDir, alignItems: 'center', justifyContent: 'center', gap: 7,
                backgroundColor: colors.muted, borderRadius: colors.radius, paddingVertical: 13,
                borderWidth: 1, borderColor: colors.border,
                opacity: pressed ? 0.85 : 1,
              })}
              onPress={handleShare}
              accessibilityRole="button"
              accessibilityLabel="Share URL"
            >
              <Feather name="share-2" size={16} color={colors.foreground} />
              <Text style={{ fontSize: 14, fontFamily: 'Inter_600SemiBold', color: colors.foreground }}>Share</Text>
            </Pressable>
          )}
        </View>

        {/* How-to steps */}
        <View style={{ width: '100%', backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1, borderColor: colors.border, padding: 16 }}>
          <Text style={{ fontSize: 14, fontFamily: 'Inter_600SemiBold', color: colors.foreground, marginBottom: 12 }}>
            How to connect with Expo Go
          </Text>
          {[
            'Download the free Expo Go app from the App Store or Google Play.',
            'Make sure your phone and this computer are on the same Wi-Fi network.',
            'Open Expo Go → tap "Scan QR Code" → scan the code above.',
            'The app will load live on your phone with hot-reload.',
          ].map((step, i) => (
            <View key={i} style={{ flexDirection: rowDir, gap: 12, marginBottom: i < 3 ? 10 : 0 }}>
              <View style={{ width: 24, height: 24, borderRadius: 12, backgroundColor: colors.primary + '20', alignItems: 'center', justifyContent: 'center', marginTop: 1 }}>
                <Text style={{ fontSize: 12, fontFamily: 'Inter_700Bold', color: colors.primary }}>{i + 1}</Text>
              </View>
              <Text style={{ flex: 1, fontSize: 13, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 19 }}>
                {step}
              </Text>
            </View>
          ))}
        </View>

        {/* Note about Replit tunnel */}
        <View style={{ width: '100%', backgroundColor: '#C9A05014', borderRadius: colors.radius, borderWidth: 1, borderColor: '#C9A05030', padding: 14, marginTop: 12 }}>
          <Text style={{ fontSize: 12, fontFamily: 'Inter_500Medium', color: '#C9A050', marginBottom: 4 }}>
            📡 Replit Tunnel Note
          </Text>
          <Text style={{ fontSize: 12, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 18 }}>
            Since this app runs on Replit, you may need to use the Expo Go "Enter URL manually" option and paste the URL above — the QR code scan requires the phone to reach the Replit tunnel address.
          </Text>
        </View>

      </ScrollView>
    </View>
  );
}
