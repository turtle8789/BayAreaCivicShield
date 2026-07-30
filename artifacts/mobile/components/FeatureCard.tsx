import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import Animated, { useAnimatedStyle, useSharedValue, withSpring } from 'react-native-reanimated';
import { Feather, Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import { useColors } from '@/hooks/useColors';
import { useRTL } from '@/hooks/useRTL';

type IconSet = 'feather' | 'ionicons' | 'material';

interface FeatureCardProps {
  title: string;
  description: string;
  iconName: string;
  iconSet?: IconSet;
  accentColor: string;
  onPress: () => void;
}

const AnimatedPressable = Animated.createAnimatedComponent(Pressable);

export function FeatureCard({ title, description, iconName, iconSet = 'feather', accentColor, onPress }: FeatureCardProps) {
  const colors = useColors();
  const { rowDir, arrowIcon } = useRTL();
  const scale = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  const handlePressIn = () => {
    scale.value = withSpring(0.96, { damping: 12 });
  };

  const handlePressOut = () => {
    scale.value = withSpring(1, { damping: 12 });
  };

  const renderIcon = () => {
    const size = 26;
    const color = accentColor;
    if (iconSet === 'ionicons') {
      return <Ionicons name={iconName as never} size={size} color={color} />;
    }
    if (iconSet === 'material') {
      return <MaterialCommunityIcons name={iconName as never} size={size} color={color} />;
    }
    return <Feather name={iconName as never} size={size} color={color} />;
  };

  const styles = StyleSheet.create({
    card: {
      backgroundColor: colors.card,
      borderRadius: colors.radius,
      padding: 18,
      marginBottom: 12,
      borderWidth: 1,
      borderColor: colors.border,
      flexDirection: rowDir,
      alignItems: 'center',
      gap: 14,
    },
    iconWrap: {
      width: 50,
      height: 50,
      borderRadius: 14,
      alignItems: 'center',
      justifyContent: 'center',
    },
    textWrap: {
      flex: 1,
    },
    title: {
      fontSize: 16,
      fontFamily: 'Inter_600SemiBold',
      color: colors.foreground,
      marginBottom: 3,
    },
    description: {
      fontSize: 13,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
      lineHeight: 18,
    },
    arrow: {
      marginLeft: 4,
    },
  });

  return (
    <AnimatedPressable
      onPress={onPress}
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      style={animatedStyle}
    >
      <View style={styles.card}>
        <View style={[styles.iconWrap, { backgroundColor: accentColor + '18' }]}>
          {renderIcon()}
        </View>
        <View style={styles.textWrap}>
          <Text style={styles.title}>{title}</Text>
          <Text style={styles.description} numberOfLines={2}>{description}</Text>
        </View>
        <Feather name={arrowIcon} size={18} color={colors.mutedForeground} style={styles.arrow} />
      </View>
    </AnimatedPressable>
  );
}
