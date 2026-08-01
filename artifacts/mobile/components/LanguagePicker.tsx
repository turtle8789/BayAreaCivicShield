import React, { useState } from 'react';
import {
  FlatList,
  Modal,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { Feather } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Language, LANGUAGES } from '@/constants/languages';
import { useColors } from '@/hooks/useColors';
import { useRTL } from '@/hooks/useRTL';
import { useT } from '@/hooks/useTranslation';

interface LanguagePickerProps {
  visible: boolean;
  selectedCode: string;
  onSelect: (language: Language) => void;
  onClose: () => void;
}

export function LanguagePicker({ visible, selectedCode, onSelect, onClose }: LanguagePickerProps) {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const { rowDir } = useRTL();
  const { t } = useT();
  const [query, setQuery] = useState('');

  const filtered = LANGUAGES.filter(
    (l) =>
      l.name.toLowerCase().includes(query.toLowerCase()) ||
      l.nativeName.toLowerCase().includes(query.toLowerCase()),
  );

  const styles = StyleSheet.create({
    overlay: {
      flex: 1,
      backgroundColor: 'rgba(0,0,0,0.45)',
      justifyContent: 'flex-end',
    },
    sheet: {
      backgroundColor: colors.card,
      borderTopLeftRadius: 24,
      borderTopRightRadius: 24,
      paddingTop: 12,
      paddingBottom: insets.bottom + 16,
      maxHeight: '80%',
    },
    handle: {
      width: 40,
      height: 4,
      borderRadius: 2,
      backgroundColor: colors.border,
      alignSelf: 'center',
      marginBottom: 16,
    },
    header: {
      flexDirection: rowDir,
      alignItems: 'center',
      paddingHorizontal: 20,
      marginBottom: 12,
    },
    headerTitle: {
      flex: 1,
      fontSize: 18,
      fontFamily: 'Inter_600SemiBold',
      color: colors.foreground,
    },
    searchWrap: {
      flexDirection: rowDir,
      alignItems: 'center',
      backgroundColor: colors.muted,
      borderRadius: 12,
      marginHorizontal: 20,
      marginBottom: 8,
      paddingHorizontal: 12,
      height: 44,
      gap: 8,
    },
    searchInput: {
      flex: 1,
      fontSize: 15,
      fontFamily: 'Inter_400Regular',
      color: colors.foreground,
    },
    item: {
      flexDirection: rowDir,
      alignItems: 'center',
      paddingHorizontal: 20,
      paddingVertical: 14,
      gap: 12,
    },
    itemSelected: {
      backgroundColor: colors.primary + '14',
    },
    langName: {
      flex: 1,
      fontSize: 15,
      fontFamily: 'Inter_500Medium',
      color: colors.foreground,
    },
    langNative: {
      fontSize: 14,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
    },
    separator: {
      height: 1,
      backgroundColor: colors.border,
      marginHorizontal: 20,
    },
  });

  return (
    <Modal visible={visible} transparent animationType="slide" onRequestClose={onClose}>
      <Pressable style={styles.overlay} onPress={onClose}>
        <Pressable style={styles.sheet} onPress={() => { /* absorb */ }}>
          <View style={styles.handle} />
          <View style={styles.header}>
            <Text style={styles.headerTitle}>{t('langpicker.title')}</Text>
            <Pressable onPress={onClose} hitSlop={12}>
              <Feather name="x" size={22} color={colors.mutedForeground} />
            </Pressable>
          </View>
          <View style={styles.searchWrap}>
            <Feather name="search" size={16} color={colors.mutedForeground} />
            <TextInput
              style={styles.searchInput}
              value={query}
              onChangeText={setQuery}
              placeholder={t('langpicker.search_ph')}
              placeholderTextColor={colors.mutedForeground}
              autoCorrect={false}
            />
            {query.length > 0 && (
              <Pressable onPress={() => setQuery('')} hitSlop={8}>
                <Feather name="x-circle" size={16} color={colors.mutedForeground} />
              </Pressable>
            )}
          </View>
          <FlatList
            data={filtered}
            keyExtractor={(item) => item.code}
            ItemSeparatorComponent={() => <View style={styles.separator} />}
            renderItem={({ item }) => {
              const isSelected = item.code === selectedCode;
              return (
                <Pressable
                  style={[styles.item, isSelected && styles.itemSelected]}
                  onPress={() => {
                    onSelect(item);
                    onClose();
                  }}
                >
                  <Text style={styles.langName}>{item.name}</Text>
                  <Text style={styles.langNative}>{item.nativeName}</Text>
                  {isSelected && (
                    <Feather name="check" size={18} color={colors.primary} />
                  )}
                </Pressable>
              );
            }}
          />
        </Pressable>
      </Pressable>
    </Modal>
  );
}
