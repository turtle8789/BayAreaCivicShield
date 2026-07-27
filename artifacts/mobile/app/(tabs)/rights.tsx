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

// ─── Rights Category Card ────────────────────────────────────────────────────

function CategoryCard({ category, onPress }: { category: RightsCategory; onPress: () => void }) {
  const colors = useColors();

  const styles = StyleSheet.create({
    card: {
      backgroundColor: colors.card,
      borderRadius: colors.radius,
      padding: 16,
      marginBottom: 10,
      borderWidth: 1,
      borderColor: colors.border,
      flexDirection: 'row',
      alignItems: 'center',
      gap: 12,
    },
    iconWrap: {
      width: 44,
      height: 44,
      borderRadius: 12,
      alignItems: 'center',
      justifyContent: 'center',
    },
    title: {
      flex: 1,
      fontSize: 16,
      fontFamily: 'Inter_600SemiBold',
      color: colors.foreground,
    },
    count: {
      fontSize: 12,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
    },
  });

  return (
    <Pressable style={styles.card} onPress={onPress}>
      <View style={[styles.iconWrap, { backgroundColor: category.color + '18' }]}>
        <Feather name={category.icon as never} size={22} color={category.color} />
      </View>
      <View style={{ flex: 1 }}>
        <Text style={styles.title}>{category.title}</Text>
        <Text style={styles.count}>{category.rights.length} key rights</Text>
      </View>
      <Feather name="chevron-right" size={18} color={colors.mutedForeground} />
    </Pressable>
  );
}

// ─── Rights Detail Modal ─────────────────────────────────────────────────────

function RightsDetail({ category, onBack }: { category: RightsCategory; onBack: () => void }) {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;

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
      flexDirection: 'row',
      alignItems: 'center',
      gap: 12,
    },
    headerTitle: {
      flex: 1,
      fontSize: 20,
      fontFamily: 'Inter_700Bold',
      color: colors.foreground,
    },
    scroll: { flex: 1 },
    scrollContent: {
      padding: 20,
      paddingBottom: Platform.OS === 'web' ? 34 : 24,
    },
    rightItem: {
      flexDirection: 'row',
      gap: 12,
      marginBottom: 16,
    },
    dot: {
      width: 8,
      height: 8,
      borderRadius: 4,
      marginTop: 6,
    },
    rightText: {
      flex: 1,
      fontSize: 15,
      fontFamily: 'Inter_400Regular',
      color: colors.foreground,
      lineHeight: 22,
    },
    disclaimer: {
      backgroundColor: colors.muted,
      borderRadius: colors.radius,
      padding: 14,
      marginTop: 8,
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
        <Pressable onPress={onBack} hitSlop={12}>
          <Feather name="arrow-left" size={22} color={colors.foreground} />
        </Pressable>
        <Text style={styles.headerTitle}>{category.title}</Text>
      </View>
      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent}>
        {category.rights.map((right, i) => (
          <View key={i} style={styles.rightItem}>
            <View style={[styles.dot, { backgroundColor: category.color }]} />
            <Text style={styles.rightText}>{right}</Text>
          </View>
        ))}
        <View style={styles.disclaimer}>
          <Text style={styles.disclaimerText}>
            This is general educational information, not legal advice. Laws vary by state and situation. Always consult a licensed attorney for your specific circumstances.
          </Text>
        </View>
      </ScrollView>
    </View>
  );
}

// ─── Quiz ────────────────────────────────────────────────────────────────────

function QuizScreen({ onBack }: { onBack: () => void }) {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;

  const [currentIdx, setCurrentIdx] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [score, setScore] = useState(0);
  const [finished, setFinished] = useState(false);

  const question = QUIZ_QUESTIONS[currentIdx];
  const total = QUIZ_QUESTIONS.length;

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
      flexDirection: 'row',
      alignItems: 'center',
      gap: 12,
    },
    headerTitle: {
      flex: 1,
      fontSize: 20,
      fontFamily: 'Inter_700Bold',
      color: colors.foreground,
    },
    progressText: {
      fontSize: 14,
      fontFamily: 'Inter_500Medium',
      color: colors.mutedForeground,
    },
    scroll: { flex: 1 },
    scrollContent: {
      padding: 20,
      paddingBottom: Platform.OS === 'web' ? 34 : 24,
    },
    progressBar: {
      height: 4,
      backgroundColor: colors.muted,
      borderRadius: 2,
      marginBottom: 24,
    },
    progressFill: {
      height: 4,
      backgroundColor: colors.primary,
      borderRadius: 2,
    },
    question: {
      fontSize: 18,
      fontFamily: 'Inter_600SemiBold',
      color: colors.foreground,
      lineHeight: 26,
      marginBottom: 24,
    },
    option: {
      borderRadius: colors.radius,
      borderWidth: 1.5,
      borderColor: colors.border,
      backgroundColor: colors.card,
      padding: 14,
      marginBottom: 10,
    },
    optionCorrect: {
      borderColor: '#A7B8A0',
      backgroundColor: '#A7B8A0' + '14',
    },
    optionWrong: {
      borderColor: colors.destructive,
      backgroundColor: colors.destructive + '10',
    },
    optionSelected: {
      borderColor: colors.primary,
    },
    optionText: {
      fontSize: 15,
      fontFamily: 'Inter_400Regular',
      color: colors.foreground,
      lineHeight: 21,
    },
    explanation: {
      backgroundColor: '#A7B8A0' + '18',
      borderRadius: colors.radius,
      padding: 14,
      marginTop: 4,
      marginBottom: 12,
    },
    explanationText: {
      fontSize: 14,
      fontFamily: 'Inter_400Regular',
      color: colors.foreground,
      lineHeight: 20,
    },
    nextBtn: {
      backgroundColor: colors.primary,
      borderRadius: colors.radius,
      paddingVertical: 14,
      alignItems: 'center',
      marginTop: 8,
    },
    nextBtnText: {
      fontSize: 16,
      fontFamily: 'Inter_600SemiBold',
      color: colors.primaryForeground,
    },
    finishContainer: {
      flex: 1,
      alignItems: 'center',
      justifyContent: 'center',
      padding: 32,
    },
    finishScore: {
      fontSize: 60,
      fontFamily: 'Inter_700Bold',
      color: colors.primary,
    },
    finishTotal: {
      fontSize: 20,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
      marginBottom: 8,
    },
    finishTitle: {
      fontSize: 22,
      fontFamily: 'Inter_600SemiBold',
      color: colors.foreground,
      marginBottom: 8,
    },
    finishSub: {
      fontSize: 15,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
      textAlign: 'center',
      lineHeight: 22,
      marginBottom: 32,
    },
    restartBtn: {
      backgroundColor: colors.primary,
      borderRadius: colors.radius,
      paddingVertical: 14,
      paddingHorizontal: 32,
    },
    restartBtnText: {
      fontSize: 16,
      fontFamily: 'Inter_600SemiBold',
      color: colors.primaryForeground,
    },
  });

  if (finished) {
    const pct = Math.round((score / total) * 100);
    const message = pct >= 80 ? 'Excellent! You know your rights well.' : pct >= 60 ? 'Good job! Review the rights sections to learn more.' : 'Keep studying — knowing your rights matters.';
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <Pressable onPress={onBack} hitSlop={12}>
            <Feather name="arrow-left" size={22} color={colors.foreground} />
          </Pressable>
          <Text style={styles.headerTitle}>Quiz Complete</Text>
        </View>
        <View style={styles.finishContainer}>
          <Text style={styles.finishScore}>{score}</Text>
          <Text style={styles.finishTotal}>out of {total} correct</Text>
          <Text style={styles.finishTitle}>{pct >= 80 ? 'Great work!' : pct >= 60 ? 'Good effort!' : 'Keep learning'}</Text>
          <Text style={styles.finishSub}>{message}</Text>
          <Pressable style={styles.restartBtn} onPress={handleRestart}>
            <Text style={styles.restartBtnText}>Try Again</Text>
          </Pressable>
        </View>
      </View>
    );
  }

  const progress = (currentIdx + 1) / total;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Pressable onPress={onBack} hitSlop={12}>
          <Feather name="arrow-left" size={22} color={colors.foreground} />
        </Pressable>
        <Text style={styles.headerTitle}>Know Your Rights Quiz</Text>
        <Text style={styles.progressText}>{currentIdx + 1}/{total}</Text>
      </View>
      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent}>
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: `${progress * 100}%` }]} />
        </View>

        <Text style={styles.question}>{question.question}</Text>

        {question.options.map((opt, i) => {
          let optStyle = styles.option;
          if (selectedAnswer !== null) {
            if (i === question.correctIndex) optStyle = { ...styles.option, ...styles.optionCorrect };
            else if (i === selectedAnswer && selectedAnswer !== question.correctIndex) {
              optStyle = { ...styles.option, ...styles.optionWrong };
            }
          }

          return (
            <Pressable key={i} style={optStyle} onPress={() => handleAnswer(i)}>
              <Text style={styles.optionText}>{opt}</Text>
            </Pressable>
          );
        })}

        {selectedAnswer !== null && (
          <>
            <View style={styles.explanation}>
              <Text style={styles.explanationText}>{question.explanation}</Text>
            </View>
            <Pressable style={styles.nextBtn} onPress={handleNext}>
              <Text style={styles.nextBtnText}>
                {currentIdx + 1 >= total ? 'See Results' : 'Next Question'}
              </Text>
            </Pressable>
          </>
        )}
      </ScrollView>
    </View>
  );
}

// ─── Main Rights Screen ───────────────────────────────────────────────────────

type View = 'list' | 'detail' | 'quiz';

export default function RightsScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;

  const [view, setView] = useState<View>('list');
  const [selectedCategory, setSelectedCategory] = useState<RightsCategory | null>(null);

  if (view === 'detail' && selectedCategory) {
    return <RightsDetail category={selectedCategory} onBack={() => setView('list')} />;
  }

  if (view === 'quiz') {
    return <QuizScreen onBack={() => setView('list')} />;
  }

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
    },
    headerTitle: {
      fontSize: 22,
      fontFamily: 'Inter_700Bold',
      color: colors.foreground,
    },
    headerSub: {
      fontSize: 13,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
      marginTop: 2,
    },
    scroll: { flex: 1 },
    scrollContent: {
      padding: 16,
      paddingBottom: Platform.OS === 'web' ? 34 : 24,
    },
    sectionTitle: {
      fontSize: 13,
      fontFamily: 'Inter_600SemiBold',
      color: colors.mutedForeground,
      textTransform: 'uppercase',
      letterSpacing: 0.8,
      marginBottom: 12,
    },
    quizBanner: {
      backgroundColor: colors.primary,
      borderRadius: colors.radius,
      padding: 16,
      marginBottom: 20,
      flexDirection: 'row',
      alignItems: 'center',
      gap: 12,
    },
    quizTextWrap: {
      flex: 1,
    },
    quizTitle: {
      fontSize: 16,
      fontFamily: 'Inter_600SemiBold',
      color: '#FFFFFF',
    },
    quizSub: {
      fontSize: 13,
      fontFamily: 'Inter_400Regular',
      color: '#FFFFFF' + 'CC',
      marginTop: 2,
    },
  });

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Know Your Rights</Text>
        <Text style={styles.headerSub}>California civil rights education</Text>
      </View>
      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Quiz banner */}
        <Pressable style={styles.quizBanner} onPress={() => setView('quiz')}>
          <Feather name="award" size={28} color="#FFFFFF" />
          <View style={styles.quizTextWrap}>
            <Text style={styles.quizTitle}>Test Your Knowledge</Text>
            <Text style={styles.quizSub}>10 questions on your civil rights</Text>
          </View>
          <Feather name="chevron-right" size={20} color="#FFFFFF" />
        </Pressable>

        <Text style={styles.sectionTitle}>Rights by Situation</Text>

        {RIGHTS_CATEGORIES.map((cat) => (
          <CategoryCard
            key={cat.id}
            category={cat}
            onPress={() => {
              setSelectedCategory(cat);
              setView('detail');
            }}
          />
        ))}
      </ScrollView>
    </View>
  );
}
