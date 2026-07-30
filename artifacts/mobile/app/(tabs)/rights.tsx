import React, { useState } from 'react';
import {
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { Feather } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { QUIZ_QUESTIONS, RIGHTS_CATEGORIES, RightsCategory } from '@/constants/rights-data';
import { useColors } from '@/hooks/useColors';
import { useT } from '@/hooks/useTranslation';

// ─── Rights Category Card ─────────────────────────────────────────────────────

function CategoryCard({ category, onPress }: { category: RightsCategory; onPress: () => void }) {
  const colors = useColors();
  const { t } = useT();

  return (
    <Pressable
      style={({ pressed }) => ({
        backgroundColor: colors.card,
        borderRadius: colors.radius,
        padding: 16,
        marginBottom: 10,
        borderWidth: 1,
        borderColor: colors.border,
        flexDirection: 'row' as const,
        alignItems: 'center' as const,
        gap: 12,
        opacity: pressed ? 0.85 : 1,
      })}
      onPress={onPress}
      accessibilityRole="button"
      accessibilityLabel={`${category.title} — ${category.rights.length} ${t('rights.key_rights')}`}
    >
      <View style={{ width: 44, height: 44, borderRadius: 12, alignItems: 'center', justifyContent: 'center', backgroundColor: category.color + '18' }}>
        <Feather name={category.icon as never} size={22} color={category.color} />
      </View>
      <View style={{ flex: 1 }}>
        <Text style={{ flex: 1, fontSize: 16, fontFamily: 'Inter_600SemiBold', color: colors.foreground }}>
          {category.title}
        </Text>
        <Text style={{ fontSize: 12, fontFamily: 'Inter_400Regular', color: colors.mutedForeground }}>
          {category.rights.length} {t('rights.key_rights')}
        </Text>
      </View>
      <Feather name="chevron-right" size={18} color={colors.mutedForeground} />
    </Pressable>
  );
}

// ─── Rights Detail ────────────────────────────────────────────────────────────

function RightsDetail({ category, onBack }: { category: RightsCategory; onBack: () => void }) {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const { t } = useT();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <View style={{
        paddingTop: topPad + 12, paddingHorizontal: 20, paddingBottom: 16,
        borderBottomWidth: 1, borderBottomColor: colors.border,
        flexDirection: 'row', alignItems: 'center', gap: 12,
      }}>
        <Pressable onPress={onBack} hitSlop={12} accessibilityLabel={t('common.back')} accessibilityRole="button">
          <Feather name="arrow-left" size={22} color={colors.foreground} />
        </Pressable>
        <Text style={{ flex: 1, fontSize: 20, fontFamily: 'Inter_700Bold', color: colors.foreground }}>
          {category.title}
        </Text>
      </View>
      <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: 20, paddingBottom: Platform.OS === 'web' ? 34 : 24, flexGrow: 1 }}>
        {category.rights.map((right, i) => (
          <View key={i} style={{ flexDirection: 'row', gap: 12, marginBottom: 16 }}>
            <View style={{ width: 8, height: 8, borderRadius: 4, marginTop: 7, backgroundColor: category.color }} />
            <Text style={{ flex: 1, fontSize: 15, fontFamily: 'Inter_400Regular', color: colors.foreground, lineHeight: 22 }}>
              {right}
            </Text>
          </View>
        ))}
        <View style={{ backgroundColor: colors.muted, borderRadius: colors.radius, padding: 14, marginTop: 8 }}>
          <Text style={{ fontSize: 12, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 18 }}>
            {t('rights.general_info')}
          </Text>
        </View>
      </ScrollView>
    </View>
  );
}

// ─── Quiz ─────────────────────────────────────────────────────────────────────

function QuizScreen({ onBack }: { onBack: () => void }) {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const { t } = useT();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;

  const [currentIdx, setCurrentIdx]     = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [score, setScore]               = useState(0);
  const [finished, setFinished]         = useState(false);

  const question = QUIZ_QUESTIONS[currentIdx];
  const total    = QUIZ_QUESTIONS.length;
  const isCorrect = selectedAnswer !== null && selectedAnswer === question.correctIndex;

  const handleAnswer = (optionIdx: number) => {
    if (selectedAnswer !== null) return;
    setSelectedAnswer(optionIdx);
    if (optionIdx === question.correctIndex) {
      setScore((s) => s + 1);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } else {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    }
  };

  const handleNext = () => {
    if (currentIdx + 1 >= total) {
      setFinished(true);
    } else {
      setCurrentIdx((i) => i + 1);
      setSelectedAnswer(null);
    }
  };

  const handleRestart = () => {
    setCurrentIdx(0);
    setSelectedAnswer(null);
    setScore(0);
    setFinished(false);
  };

  const styles = StyleSheet.create({
    container:        { flex: 1, backgroundColor: colors.background },
    header:           { paddingTop: topPad + 12, paddingHorizontal: 20, paddingBottom: 16, borderBottomWidth: 1, borderBottomColor: colors.border, flexDirection: 'row', alignItems: 'center', gap: 12 },
    headerTitle:      { flex: 1, fontSize: 20, fontFamily: 'Inter_700Bold', color: colors.foreground },
    progressText:     { fontSize: 14, fontFamily: 'Inter_500Medium', color: colors.mutedForeground },
    scrollContent:    { padding: 20, paddingBottom: Platform.OS === 'web' ? 34 : 24, flexGrow: 1 },
    progressBar:      { height: 5, backgroundColor: colors.muted, borderRadius: 3, marginBottom: 24 },
    progressFill:     { height: 5, backgroundColor: colors.primary, borderRadius: 3 },
    question:         { fontSize: 18, fontFamily: 'Inter_600SemiBold', color: colors.foreground, lineHeight: 26, marginBottom: 20 },
    option:           { borderRadius: colors.radius, borderWidth: 1.5, borderColor: colors.border, backgroundColor: colors.card, padding: 14, marginBottom: 10 },
    optionCorrect:    { borderColor: '#5A9E6F', backgroundColor: '#5A9E6F' + '14' },
    optionWrong:      { borderColor: colors.destructive, backgroundColor: colors.destructive + '10' },
    optionText:       { fontSize: 15, fontFamily: 'Inter_400Regular', color: colors.foreground, lineHeight: 21 },
    // Feedback banner
    feedbackBanner:   { borderRadius: colors.radius, paddingVertical: 12, paddingHorizontal: 16, marginBottom: 12, flexDirection: 'row', alignItems: 'center', gap: 10 },
    feedbackText:     { fontSize: 16, fontFamily: 'Inter_700Bold' },
    feedbackSub:      { fontSize: 13, fontFamily: 'Inter_400Regular', marginTop: 1 },
    explanation:      { backgroundColor: colors.muted, borderRadius: colors.radius, padding: 14, marginBottom: 12 },
    explanationText:  { fontSize: 14, fontFamily: 'Inter_400Regular', color: colors.foreground, lineHeight: 20 },
    nextBtn:          { backgroundColor: colors.primary, borderRadius: colors.radius, paddingVertical: 14, alignItems: 'center', marginTop: 4 },
    nextBtnText:      { fontSize: 16, fontFamily: 'Inter_600SemiBold', color: colors.primaryForeground },
    finishContainer:  { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 32 },
    finishScore:      { fontSize: 64, fontFamily: 'Inter_700Bold', color: colors.primary },
    finishTotal:      { fontSize: 20, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginBottom: 8 },
    finishTitle:      { fontSize: 22, fontFamily: 'Inter_600SemiBold', color: colors.foreground, marginBottom: 8 },
    finishSub:        { fontSize: 15, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, textAlign: 'center', lineHeight: 22, marginBottom: 32 },
    restartBtn:       { backgroundColor: colors.primary, borderRadius: colors.radius, paddingVertical: 14, paddingHorizontal: 32 },
    restartBtnText:   { fontSize: 16, fontFamily: 'Inter_600SemiBold', color: colors.primaryForeground },
  });

  if (finished) {
    const pct = Math.round((score / total) * 100);
    const title   = pct >= 80 ? t('rights.score_great') : pct >= 60 ? t('rights.score_good') : t('rights.score_keep');
    const message = pct >= 80
      ? t('rights.score_great_msg')
      : pct >= 60
        ? t('rights.score_good_msg')
        : t('rights.score_keep_msg');
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <Pressable onPress={onBack} hitSlop={12} accessibilityRole="button" accessibilityLabel={t('common.back')}>
            <Feather name="arrow-left" size={22} color={colors.foreground} />
          </Pressable>
          <Text style={styles.headerTitle}>{t('rights.quiz_complete')}</Text>
        </View>
        <View style={styles.finishContainer}>
          <Text style={styles.finishScore}>{score}</Text>
          <Text style={styles.finishTotal}>{t('common.out_of')} {total} {t('rights.correct_label')}</Text>
          <Text style={styles.finishTitle}>{title}</Text>
          <Text style={styles.finishSub}>{message}</Text>
          <Pressable style={styles.restartBtn} onPress={handleRestart} accessibilityRole="button">
            <Text style={styles.restartBtnText}>{t('rights.try_again')}</Text>
          </Pressable>
        </View>
      </View>
    );
  }

  const progress = (currentIdx + 1) / total;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Pressable onPress={onBack} hitSlop={12} accessibilityRole="button" accessibilityLabel={t('common.back')}>
          <Feather name="arrow-left" size={22} color={colors.foreground} />
        </Pressable>
        <Text style={styles.headerTitle}>{t('rights.quiz_title')}</Text>
        <Text style={styles.progressText}>{currentIdx + 1}/{total}</Text>
      </View>

      <ScrollView style={{ flex: 1 }} contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Progress bar */}
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: `${progress * 100}%` as never }]} />
        </View>

        {/* Score running tally */}
        <View style={{ flexDirection: 'row', justifyContent: 'flex-end', marginBottom: 12 }}>
          <View style={{ backgroundColor: colors.primary + '14', borderRadius: 20, paddingHorizontal: 12, paddingVertical: 4, flexDirection: 'row', alignItems: 'center', gap: 5 }}>
            <Feather name="award" size={13} color={colors.primary} />
            <Text style={{ fontSize: 13, fontFamily: 'Inter_600SemiBold', color: colors.primary }}>
              {score} / {currentIdx + (selectedAnswer !== null ? 1 : 0)}
            </Text>
          </View>
        </View>

        {/* Question */}
        <Text style={styles.question}>{question.question}</Text>

        {/* Answer options */}
        {question.options.map((opt, i) => {
          let optStyle = styles.option;
          if (selectedAnswer !== null) {
            if (i === question.correctIndex) optStyle = { ...styles.option, ...styles.optionCorrect };
            else if (i === selectedAnswer && selectedAnswer !== question.correctIndex) {
              optStyle = { ...styles.option, ...styles.optionWrong };
            }
          }
          return (
            <Pressable
              key={i}
              style={optStyle}
              onPress={() => handleAnswer(i)}
              accessibilityRole="button"
              accessibilityLabel={`Option ${i + 1}: ${opt}`}
              disabled={selectedAnswer !== null}
            >
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: 10 }}>
                {selectedAnswer !== null && i === question.correctIndex && (
                  <Feather name="check-circle" size={17} color="#5A9E6F" />
                )}
                {selectedAnswer !== null && i === selectedAnswer && selectedAnswer !== question.correctIndex && (
                  <Feather name="x-circle" size={17} color={colors.destructive} />
                )}
                {(selectedAnswer === null || (i !== question.correctIndex && i !== selectedAnswer)) && (
                  <View style={{ width: 17, height: 17, borderRadius: 9, borderWidth: 1.5, borderColor: colors.border }} />
                )}
                <Text style={[styles.optionText, { flex: 1 }]}>{opt}</Text>
              </View>
            </Pressable>
          );
        })}

        {/* Feedback banner — shown immediately after answering */}
        {selectedAnswer !== null && (
          <>
            <View style={[
              styles.feedbackBanner,
              { backgroundColor: isCorrect ? '#5A9E6F18' : colors.destructive + '12',
                borderWidth: 1,
                borderColor: isCorrect ? '#5A9E6F40' : colors.destructive + '40' },
            ]}>
              <Feather
                name={isCorrect ? 'check-circle' : 'x-circle'}
                size={22}
                color={isCorrect ? '#5A9E6F' : colors.destructive}
              />
              <View style={{ flex: 1 }}>
                <Text style={[styles.feedbackText, { color: isCorrect ? '#5A9E6F' : colors.destructive }]}>
                  {isCorrect ? t('rights.correct') : t('rights.incorrect')}
                </Text>
                {!isCorrect && (
                  <Text style={[styles.feedbackSub, { color: colors.mutedForeground }]}>
                    {t('rights.correct_was')}
                  </Text>
                )}
              </View>
            </View>

            {/* Explanation */}
            <View style={styles.explanation}>
              <Text style={styles.explanationText}>{question.explanation}</Text>
            </View>

            <Pressable style={styles.nextBtn} onPress={handleNext} accessibilityRole="button">
              <Text style={styles.nextBtnText}>
                {currentIdx + 1 >= total ? t('rights.see_results') : t('rights.next_question')}
              </Text>
            </Pressable>
          </>
        )}
      </ScrollView>
    </View>
  );
}

// ─── Main Rights Screen ───────────────────────────────────────────────────────

type RightsView = 'list' | 'detail' | 'quiz';

export default function RightsScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const { t } = useT();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;

  const [view, setView] = useState<RightsView>('list');
  const [selectedCategory, setSelectedCategory] = useState<RightsCategory | null>(null);

  if (view === 'detail' && selectedCategory) {
    return <RightsDetail category={selectedCategory} onBack={() => setView('list')} />;
  }
  if (view === 'quiz') {
    return <QuizScreen onBack={() => setView('list')} />;
  }

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <View style={{
        paddingTop: topPad + 12, paddingHorizontal: 20, paddingBottom: 16,
        borderBottomWidth: 1, borderBottomColor: colors.border,
      }}>
        <Text style={{ fontSize: 22, fontFamily: 'Inter_700Bold', color: colors.foreground }} accessibilityRole="header">
          {t('rights.title')}
        </Text>
        <Text style={{ fontSize: 13, fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 2 }}>
          {t('rights.subtitle')}
        </Text>
      </View>

      <ScrollView
        style={{ flex: 1 }}
        contentContainerStyle={{ padding: 16, paddingBottom: Platform.OS === 'web' ? 34 : 24, flexGrow: 1 }}
        showsVerticalScrollIndicator={false}
      >
        {/* Quiz banner */}
        <Pressable
          style={({ pressed }) => ({
            backgroundColor: colors.primary,
            borderRadius: colors.radius,
            padding: 16,
            marginBottom: 20,
            flexDirection: 'row' as const,
            alignItems: 'center' as const,
            gap: 12,
            opacity: pressed ? 0.9 : 1,
          })}
          onPress={() => setView('quiz')}
          accessibilityRole="button"
          accessibilityLabel={t('rights.quiz_banner_title')}
        >
          <Feather name="award" size={28} color="#FFFFFF" />
          <View style={{ flex: 1 }}>
            <Text style={{ fontSize: 16, fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' }}>
              {t('rights.quiz_banner_title')}
            </Text>
            <Text style={{ fontSize: 13, fontFamily: 'Inter_400Regular', color: '#FFFFFFCC', marginTop: 2 }}>
              {t('rights.quiz_banner_sub')}
            </Text>
          </View>
          <Feather name="chevron-right" size={20} color="#FFFFFF" />
        </Pressable>

        <Text style={{ fontSize: 13, fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 12 }} accessibilityRole="header">
          {t('rights.rights_by_situation')}
        </Text>

        {RIGHTS_CATEGORIES.map((cat) => (
          <CategoryCard
            key={cat.id}
            category={cat}
            onPress={() => { setSelectedCategory(cat); setView('detail'); }}
          />
        ))}
      </ScrollView>
    </View>
  );
}
