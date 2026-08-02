/**
 * PasswordModal — bottom-sheet modal that lets the user optionally set a
 * password before exporting / sharing an encounter log.
 *
 * Props:
 *   visible   — controls Modal visibility
 *   onCancel  — called when the user dismisses without sharing
 *   onShare   — called with the password string (or null for unprotected)
 */

import React, { useState } from 'react';
import {
  KeyboardAvoidingView,
  Modal,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { Feather } from '@expo/vector-icons';
import { useApp } from '@/context/AppContext';
import { useColors } from '@/hooks/useColors';
import { useT } from '@/hooks/useTranslation';

interface PasswordModalProps {
  visible: boolean;
  onCancel: () => void;
  onShare: (password: string | null) => void;
}

export function PasswordModal({ visible, onCancel, onShare }: PasswordModalProps) {
  const colors = useColors();
  const { fs } = useApp();
  const { t } = useT();
  const [password, setPassword] = useState('');
  const [confirm, setConfirm]   = useState('');

  const handleClose = () => {
    setPassword('');
    setConfirm('');
    onCancel();
  };

  const handleSkip = () => {
    setPassword('');
    setConfirm('');
    onShare(null);
  };

  const handleProtected = () => {
    const pwd = password.trim();
    setPassword('');
    setConfirm('');
    onShare(pwd.length > 0 ? pwd : null);
  };

  const hasPassword       = password.trim().length > 0;
  const passwordsMatch    = password === confirm;
  const canShareProtected = hasPassword && passwordsMatch;
  const showMismatch      = hasPassword && confirm.length > 0 && !passwordsMatch;

  const s = StyleSheet.create({
    overlay:    { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
    sheet:      { backgroundColor: colors.background, borderTopLeftRadius: 20, borderTopRightRadius: 20, padding: 24, paddingBottom: 36 },
    handle:     { width: 36, height: 4, borderRadius: 2, backgroundColor: colors.border, alignSelf: 'center', marginBottom: 20 },
    iconWrap:   { width: 56, height: 56, borderRadius: 28, backgroundColor: colors.primary + '18', alignItems: 'center', justifyContent: 'center', alignSelf: 'center', marginBottom: 14 },
    title:      { fontSize: fs(18), fontFamily: 'Inter_700Bold', color: colors.foreground, textAlign: 'center', marginBottom: 8 },
    desc:       { fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, textAlign: 'center', lineHeight: 19, marginBottom: 20 },
    input:      { backgroundColor: colors.muted, borderRadius: 12, borderWidth: 1, borderColor: colors.border, paddingHorizontal: 16, paddingVertical: 12, fontSize: fs(15), fontFamily: 'Inter_400Regular', color: colors.foreground, marginBottom: 16 },
    inputError: { backgroundColor: colors.muted, borderRadius: 12, borderWidth: 1, borderColor: colors.destructive, paddingHorizontal: 16, paddingVertical: 12, fontSize: fs(15), fontFamily: 'Inter_400Regular', color: colors.foreground, marginBottom: 6 },
    mismatch:   { fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.destructive, marginBottom: 12 },
    btnPrimary:         { backgroundColor: colors.primary, borderRadius: 12, paddingVertical: 14, alignItems: 'center', marginBottom: 10 },
    btnPrimaryDisabled: { backgroundColor: colors.primary + '60', borderRadius: 12, paddingVertical: 14, alignItems: 'center', marginBottom: 10 },
    btnOutline: { backgroundColor: 'transparent', borderRadius: 12, paddingVertical: 14, alignItems: 'center', borderWidth: 1, borderColor: colors.border, marginBottom: 10 },
    btnCancel:  { paddingVertical: 10, alignItems: 'center' },
    btnTextPrimary: { fontSize: fs(15), fontFamily: 'Inter_600SemiBold', color: colors.primaryForeground },
    btnTextOutline: { fontSize: fs(15), fontFamily: 'Inter_600SemiBold', color: colors.foreground },
    btnTextCancel:  { fontSize: fs(14), fontFamily: 'Inter_400Regular',  color: colors.mutedForeground },
  });

  return (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={handleClose}
    >
      <KeyboardAvoidingView
        style={s.overlay}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <Pressable style={{ flex: 1 }} onPress={handleClose} />
        <View style={s.sheet}>
          <View style={s.handle} />
          <View style={s.iconWrap}>
            <Feather name="lock" size={24} color={colors.primary} />
          </View>
          <Text style={s.title}>{t('log.protect_title')}</Text>
          <Text style={s.desc}>{t('log.protect_desc')}</Text>

          <TextInput
            style={s.input}
            placeholder={t('log.protect_ph')}
            placeholderTextColor={colors.mutedForeground}
            secureTextEntry
            value={password}
            onChangeText={setPassword}
            autoCapitalize="none"
            autoCorrect={false}
            returnKeyType="next"
          />

          {hasPassword && (
            <>
              <TextInput
                style={showMismatch ? s.inputError : s.input}
                placeholder={t('log.protect_confirm_ph')}
                placeholderTextColor={colors.mutedForeground}
                secureTextEntry
                value={confirm}
                onChangeText={setConfirm}
                autoCapitalize="none"
                autoCorrect={false}
                returnKeyType="done"
                onSubmitEditing={canShareProtected ? handleProtected : undefined}
              />
              {showMismatch && (
                <Text style={s.mismatch}>{t('log.protect_mismatch')}</Text>
              )}
            </>
          )}

          {hasPassword ? (
            <Pressable
              style={canShareProtected ? s.btnPrimary : s.btnPrimaryDisabled}
              onPress={canShareProtected ? handleProtected : undefined}
              disabled={!canShareProtected}
            >
              <Text style={s.btnTextPrimary}>{t('log.protect_btn')}</Text>
            </Pressable>
          ) : (
            <Pressable style={s.btnPrimary} onPress={handleSkip}>
              <Text style={s.btnTextPrimary}>{t('log.protect_skip')}</Text>
            </Pressable>
          )}

          {hasPassword && (
            <Pressable style={s.btnOutline} onPress={handleSkip}>
              <Text style={s.btnTextOutline}>{t('log.protect_skip')}</Text>
            </Pressable>
          )}

          <Pressable style={s.btnCancel} onPress={handleClose}>
            <Text style={s.btnTextCancel}>{t('log.protect_cancel')}</Text>
          </Pressable>
        </View>
      </KeyboardAvoidingView>
    </Modal>
  );
}
