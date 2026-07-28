import React, { useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Image,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import * as Clipboard from 'expo-clipboard';
import { Feather } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useColors } from '@/hooks/useColors';

// ─── Deadline / Date Extraction ───────────────────────────────────────────────

interface ExtractionResult {
  dates: string[];
  deadlines: string[];
  penalties: string[];
  actions: string[];
}

const MONTHS =
  'January|February|March|April|May|June|July|August|September|October|November|December';

function extractFromText(raw: string): ExtractionResult {
  const text = raw;
  const lines = text.split(/\r?\n/);

  // ── Date patterns ────────────────────────────────────────────────────────
  const datePatterns: RegExp[] = [
    /\b\d{1,2}\/\d{1,2}\/\d{4}\b/g,
    new RegExp(`\\b(?:${MONTHS})\\s+\\d{1,2},?\\s+\\d{4}\\b`, 'gi'),
    new RegExp(`\\b\\d{1,2}\\s+(?:${MONTHS})\\s+\\d{4}\\b`, 'gi'),
    /\bwithin\s+\d+\s+days?\b/gi,
    new RegExp(`\\bby\\s+(?:${MONTHS})\\s+\\d{1,2},?\\s+\\d{4}\\b`, 'gi'),
    /\b(?:on|before|after)\s+\d{1,2}\/\d{1,2}\/\d{4}\b/gi,
  ];

  const dates: string[] = [];
  for (const pattern of datePatterns) {
    for (const m of text.matchAll(pattern)) {
      const val = m[0].trim();
      if (!dates.includes(val)) dates.push(val);
    }
  }

  // ── Deadline lines ───────────────────────────────────────────────────────
  const deadlineRx =
    /\b(must|required|deadline|due|respond|file|appear|hearing|court\s+date|action\s+required|notice|warning|comply|submit|failure\s+to)\b/i;
  const deadlines: string[] = [];
  for (const line of lines) {
    const t = line.trim();
    if (t.length > 10 && deadlineRx.test(t)) {
      const val = t.slice(0, 220);
      if (!deadlines.includes(val)) deadlines.push(val);
    }
  }

  // ── Penalty lines ────────────────────────────────────────────────────────
  const penaltyRx =
    /\b(penalty|fine|arrest|warrant|failure\s+to|consequences|charged|prosecution|imprisonment|revoked)\b/i;
  const penalties: string[] = [];
  for (const line of lines) {
    const t = line.trim();
    if (t.length > 5 && penaltyRx.test(t)) {
      const val = t.slice(0, 220);
      if (!penalties.includes(val)) penalties.push(val);
    }
  }

  // ── Required action lines ────────────────────────────────────────────────
  const actionRx = /^\s*\d+[.)]\s|^\s*[-•]\s|bring|provide|submit|pay\b|appear\b|complete|sign\b/i;
  const actions: string[] = [];
  for (const line of lines) {
    const t = line.trim();
    if (t.length > 5 && actionRx.test(t)) {
      const val = t.slice(0, 220);
      if (!actions.includes(val)) actions.push(val);
    }
  }

  return {
    dates: dates.slice(0, 10),
    deadlines: deadlines.slice(0, 6),
    penalties: penalties.slice(0, 5),
    actions: actions.slice(0, 8),
  };
}

// ─── Sample legal document ────────────────────────────────────────────────────

const SAMPLE_TEXT = `NOTICE TO APPEAR IN COURT

You are required to appear in court on March 15, 2025 at 9:00 AM.
Location: San Francisco Superior Court, 400 McAllister St.

REQUIRED ACTIONS:
1. Bring valid photo ID
2. Bring proof of residence
3. Pay the citation fee of $250 by March 10, 2025

WARNING: Failure to appear may result in a warrant for your arrest and additional fines up to $1,000.

DEADLINE: You must file your response within 30 days of receiving this notice.

HEARING DATE: April 2, 2025 — Department 302

PENALTIES: Failure to comply will result in automatic default judgment against you.

Case Number: 2024-CV-123456`;

// ─── Sub-components ──────────────────────────────────────────────────────────

function ResultSection({
  label,
  icon,
  color,
  items,
  emptyMsg,
}: {
  label: string;
  icon: string;
  color: string;
  items: string[];
  emptyMsg: string;
}) {
  const colors = useColors();
  return (
    <View style={{ marginBottom: 16 }}>
      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 8 }}>
        <Feather name={icon as never} size={15} color={color} />
        <Text
          style={{
            fontSize: 13,
            fontFamily: 'Inter_600SemiBold',
            color: colors.mutedForeground,
            textTransform: 'uppercase',
            letterSpacing: 0.7,
          }}
        >
          {label}
        </Text>
        {items.length > 0 && (
          <View
            style={{
              backgroundColor: color + '22',
              borderRadius: 10,
              paddingHorizontal: 7,
              paddingVertical: 2,
            }}
          >
            <Text style={{ fontSize: 11, fontFamily: 'Inter_600SemiBold', color }}>
              {items.length}
            </Text>
          </View>
        )}
      </View>
      {items.length === 0 ? (
        <Text
          style={{ fontSize: 13, fontFamily: 'Inter_400Regular', color: colors.mutedForeground }}
        >
          {emptyMsg}
        </Text>
      ) : (
        items.map((item, i) => (
          <View
            key={i}
            style={{
              backgroundColor: color + '10',
              borderLeftWidth: 3,
              borderLeftColor: color,
              borderRadius: 6,
              padding: 10,
              marginBottom: 6,
            }}
          >
            <Text
              style={{
                fontSize: 13,
                fontFamily: 'Inter_400Regular',
                color: colors.foreground,
                lineHeight: 19,
              }}
            >
              {item}
            </Text>
          </View>
        ))
      )}
    </View>
  );
}

// ─── Main Screen ─────────────────────────────────────────────────────────────

export default function DocsScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;

  const [inputText, setInputText] = useState('');
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [showQR, setShowQR] = useState(false);
  const [activeSubTab, setActiveSubTab] = useState<'analyze' | 'guide'>('analyze');

  const handleAnalyze = () => {
    if (!inputText.trim()) {
      Alert.alert('No Text', 'Please paste legal text or tap "Load Sample" to try it out.');
      return;
    }
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    setAnalyzing(true);
    setShowQR(false);
    // Small timeout to show spinner
    setTimeout(() => {
      setResult(extractFromText(inputText));
      setAnalyzing(false);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    }, 500);
  };

  const handleLoadSample = () => {
    setInputText(SAMPLE_TEXT);
    setResult(null);
    setShowQR(false);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
  };

  const handleClear = () => {
    setInputText('');
    setResult(null);
    setShowQR(false);
  };

  const handleCopy = async () => {
    if (!result) return;
    const summary = [
      result.dates.length > 0 ? `DATES:\n${result.dates.map((d) => `• ${d}`).join('\n')}` : '',
      result.deadlines.length > 0
        ? `\nDEADLINES:\n${result.deadlines.map((d) => `• ${d}`).join('\n')}`
        : '',
      result.penalties.length > 0
        ? `\nPENALTIES:\n${result.penalties.map((d) => `• ${d}`).join('\n')}`
        : '',
      result.actions.length > 0
        ? `\nREQUIRED ACTIONS:\n${result.actions.map((d) => `• ${d}`).join('\n')}`
        : '',
    ]
      .filter(Boolean)
      .join('');
    await Clipboard.setStringAsync(summary || 'No items found.');
    Alert.alert('Copied', 'Summary copied to clipboard.');
    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
  };

  const handleQR = () => {
    if (!result) return;
    setShowQR((prev) => !prev);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
  };

  // Build QR content from top extracted items
  const qrContent = result
    ? [
        result.dates.length > 0 ? `Dates: ${result.dates.slice(0, 3).join(', ')}` : '',
        result.deadlines.length > 0 ? `Deadlines: ${result.deadlines[0].slice(0, 80)}` : '',
        result.penalties.length > 0 ? `Penalty: ${result.penalties[0].slice(0, 60)}` : '',
      ]
        .filter(Boolean)
        .join(' | ')
    : '';

  const qrImageUrl = qrContent
    ? `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(qrContent)}`
    : '';

  const totalFound = result
    ? result.dates.length + result.deadlines.length + result.penalties.length + result.actions.length
    : 0;

  const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: colors.background },
    header: {
      paddingTop: topPad + 12,
      paddingHorizontal: 20,
      paddingBottom: 0,
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    headerTitle: { fontSize: 22, fontFamily: 'Inter_700Bold', color: colors.foreground },
    headerSub: {
      fontSize: 13,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
      marginTop: 2,
      marginBottom: 12,
    },
    subTabRow: { flexDirection: 'row' },
    subTab: {
      flex: 1,
      paddingVertical: 10,
      alignItems: 'center',
      borderBottomWidth: 2,
      borderBottomColor: 'transparent',
    },
    subTabActive: { borderBottomColor: colors.primary },
    subTabText: {
      fontSize: 14,
      fontFamily: 'Inter_500Medium',
      color: colors.mutedForeground,
    },
    subTabTextActive: { color: colors.primary, fontFamily: 'Inter_600SemiBold' },
    scroll: { flex: 1 },
    scrollContent: {
      padding: 16,
      paddingBottom: Platform.OS === 'web' ? 34 : 100,
    },
    card: {
      backgroundColor: colors.card,
      borderRadius: colors.radius,
      borderWidth: 1,
      borderColor: colors.border,
      marginBottom: 12,
      overflow: 'hidden',
    },
    cardHeader: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingHorizontal: 14,
      paddingTop: 12,
      marginBottom: 4,
      gap: 6,
    },
    cardLabel: {
      flex: 1,
      fontSize: 12,
      fontFamily: 'Inter_600SemiBold',
      color: colors.mutedForeground,
      textTransform: 'uppercase',
      letterSpacing: 0.6,
    },
    charCount: { fontSize: 12, fontFamily: 'Inter_400Regular', color: colors.mutedForeground },
    textInput: {
      fontSize: 14,
      fontFamily: 'Inter_400Regular',
      color: colors.foreground,
      paddingHorizontal: 14,
      paddingBottom: 14,
      minHeight: 140,
      textAlignVertical: 'top',
    },
    btnRow: { flexDirection: 'row', gap: 8, marginBottom: 12 },
    sampleBtn: {
      flex: 1,
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 6,
      borderRadius: colors.radius,
      paddingVertical: 12,
      borderWidth: 1,
      borderColor: colors.border,
      backgroundColor: colors.card,
    },
    sampleBtnText: {
      fontSize: 14,
      fontFamily: 'Inter_500Medium',
      color: colors.foreground,
    },
    clearBtn: {
      width: 46,
      alignItems: 'center',
      justifyContent: 'center',
      borderRadius: colors.radius,
      borderWidth: 1,
      borderColor: colors.border,
      backgroundColor: colors.card,
    },
    analyzeBtn: {
      backgroundColor: colors.primary,
      borderRadius: colors.radius,
      paddingVertical: 15,
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: 'row',
      gap: 8,
      marginBottom: 16,
    },
    analyzeBtnDisabled: { opacity: 0.5 },
    analyzeBtnText: {
      fontSize: 16,
      fontFamily: 'Inter_600SemiBold',
      color: colors.primaryForeground,
    },
    resultHeader: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: 14,
    },
    resultTitle: { fontSize: 16, fontFamily: 'Inter_700Bold', color: colors.foreground },
    resultActions: { flexDirection: 'row', gap: 8 },
    iconBtn: {
      width: 36,
      height: 36,
      borderRadius: 18,
      backgroundColor: colors.muted,
      alignItems: 'center',
      justifyContent: 'center',
    },
    qrContainer: {
      alignItems: 'center',
      backgroundColor: colors.card,
      borderRadius: colors.radius,
      borderWidth: 1,
      borderColor: colors.border,
      padding: 20,
      marginBottom: 16,
    },
    qrLabel: {
      fontSize: 12,
      fontFamily: 'Inter_500Medium',
      color: colors.mutedForeground,
      marginTop: 10,
      textAlign: 'center',
    },
    summaryBadge: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 6,
      backgroundColor: colors.primary + '14',
      borderRadius: 20,
      paddingHorizontal: 12,
      paddingVertical: 6,
      alignSelf: 'flex-start',
      marginBottom: 16,
    },
    summaryBadgeText: {
      fontSize: 13,
      fontFamily: 'Inter_600SemiBold',
      color: colors.primary,
    },
    guideSection: {
      backgroundColor: colors.card,
      borderRadius: colors.radius,
      borderWidth: 1,
      borderColor: colors.border,
      padding: 16,
      marginBottom: 12,
    },
    guideSectionTitle: {
      fontSize: 15,
      fontFamily: 'Inter_600SemiBold',
      color: colors.foreground,
      marginBottom: 8,
    },
    guideText: {
      fontSize: 13,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
      lineHeight: 20,
    },
    tipCard: {
      backgroundColor: colors.primary + '0F',
      borderRadius: colors.radius,
      padding: 14,
      borderWidth: 1,
      borderColor: colors.primary + '20',
      flexDirection: 'row',
      gap: 10,
      marginBottom: 12,
    },
    tipText: {
      flex: 1,
      fontSize: 13,
      fontFamily: 'Inter_400Regular',
      color: colors.mutedForeground,
      lineHeight: 19,
    },
  });

  const renderAnalyzeTab = () => (
    <>
      {/* Input card */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Text style={styles.cardLabel}>Legal Text</Text>
          <Text style={styles.charCount}>{inputText.length} chars</Text>
        </View>
        <TextInput
          style={styles.textInput}
          value={inputText}
          onChangeText={setInputText}
          multiline
          placeholder="Paste or type legal document text here...&#10;&#10;(Court notices, eviction letters, citations, contracts, etc.)"
          placeholderTextColor={colors.mutedForeground}
        />
      </View>

      {/* Action buttons */}
      <View style={styles.btnRow}>
        <Pressable style={styles.sampleBtn} onPress={handleLoadSample}>
          <Feather name="file-text" size={15} color={colors.foreground} />
          <Text style={styles.sampleBtnText}>Load Sample</Text>
        </Pressable>
        {inputText.length > 0 && (
          <Pressable style={styles.clearBtn} onPress={handleClear}>
            <Feather name="x" size={18} color={colors.mutedForeground} />
          </Pressable>
        )}
      </View>

      {/* Analyze button */}
      <Pressable
        style={[styles.analyzeBtn, !inputText.trim() && styles.analyzeBtnDisabled]}
        onPress={handleAnalyze}
        disabled={!inputText.trim() || analyzing}
      >
        {analyzing ? (
          <ActivityIndicator size="small" color="#FFFFFF" />
        ) : (
          <Feather name="search" size={18} color="#FFFFFF" />
        )}
        <Text style={styles.analyzeBtnText}>
          {analyzing ? 'Analyzing...' : '🔍 Extract Deadlines & Dates'}
        </Text>
      </Pressable>

      {/* Results */}
      {result && (
        <>
          <View style={styles.resultHeader}>
            <Text style={styles.resultTitle}>Results</Text>
            <View style={styles.resultActions}>
              <Pressable style={styles.iconBtn} onPress={handleQR}>
                <Feather name="grid" size={16} color={colors.foreground} />
              </Pressable>
              <Pressable style={styles.iconBtn} onPress={handleCopy}>
                <Feather name="copy" size={16} color={colors.foreground} />
              </Pressable>
            </View>
          </View>

          {totalFound > 0 && (
            <View style={styles.summaryBadge}>
              <Feather name="check-circle" size={14} color={colors.primary} />
              <Text style={styles.summaryBadgeText}>
                {totalFound} item{totalFound === 1 ? '' : 's'} found
              </Text>
            </View>
          )}

          {/* QR Code */}
          {showQR && qrContent && (
            <View style={styles.qrContainer}>
              <Image
                source={{ uri: qrImageUrl }}
                style={{ width: 220, height: 220 }}
                resizeMode="contain"
              />
              <Text style={styles.qrLabel}>
                Scan to share extracted deadlines and dates
              </Text>
            </View>
          )}

          <ResultSection
            label="Important Dates"
            icon="calendar"
            color="#C9A050"
            items={result.dates}
            emptyMsg="No specific dates found."
          />
          <ResultSection
            label="Deadlines & Actions Required"
            icon="alert-circle"
            color={colors.primary}
            items={result.deadlines}
            emptyMsg="No deadlines detected."
          />
          <ResultSection
            label="Penalties & Warnings"
            icon="alert-triangle"
            color="#E05252"
            items={result.penalties}
            emptyMsg="No penalties found."
          />
          <ResultSection
            label="Required Actions"
            icon="check-square"
            color="#5A9E6F"
            items={result.actions}
            emptyMsg="No required actions found."
          />

          {totalFound === 0 && (
            <View style={styles.tipCard}>
              <Feather name="info" size={16} color={colors.primary} />
              <Text style={styles.tipText}>
                No structured items were detected. Try loading the sample document to see how extraction works, or paste more complete legal text.
              </Text>
            </View>
          )}
        </>
      )}

      {/* Tip card */}
      {!result && (
        <View style={styles.tipCard}>
          <Feather name="info" size={16} color={colors.primary} />
          <Text style={styles.tipText}>
            Paste text from a court notice, eviction letter, citation, or any legal document. The analyzer will find dates, deadlines, penalties, and required actions. Tap "Load Sample" to see an example.
          </Text>
        </View>
      )}
    </>
  );

  const renderGuideTab = () => (
    <>
      <View style={styles.guideSection}>
        <Text style={styles.guideSectionTitle}>📋 What This Tool Detects</Text>
        <Text style={styles.guideText}>
          {'• Court appearance dates and hearing dates\n• Filing deadlines and response windows\n• "Within X days" notice periods\n• Penalty and fine amounts\n• Required action items (bring ID, pay fee, etc.)\n• Warrant and arrest warnings'}
        </Text>
      </View>
      <View style={styles.guideSection}>
        <Text style={styles.guideSectionTitle}>📄 Document Types Supported</Text>
        <Text style={styles.guideText}>
          {'• Court summons and notices to appear\n• Eviction notices (30/60/90-day)\n• Traffic citations\n• Immigration notices\n• Lease violation letters\n• Government benefit denial letters\n• Any document with dates and deadlines'}
        </Text>
      </View>
      <View style={styles.guideSection}>
        <Text style={styles.guideSectionTitle}>📱 QR Code Sharing</Text>
        <Text style={styles.guideText}>
          After extracting information, tap the grid icon (⊞) to generate a QR code. Share the QR code with a lawyer, advocate, or trusted person so they can instantly see your key deadlines.
        </Text>
      </View>
      <View style={[styles.tipCard, { marginTop: 4 }]}>
        <Feather name="shield" size={16} color={colors.primary} />
        <Text style={styles.tipText}>
          This tool provides general information only. For legal advice specific to your situation, always consult a licensed attorney. Check the Resources tab for free legal aid near you.
        </Text>
      </View>
    </>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>📄 Document Analyzer</Text>
        <Text style={styles.headerSub}>Extract deadlines, dates & penalties from legal text</Text>
        <View style={styles.subTabRow}>
          <Pressable
            style={[styles.subTab, activeSubTab === 'analyze' && styles.subTabActive]}
            onPress={() => setActiveSubTab('analyze')}
          >
            <Text
              style={[
                styles.subTabText,
                activeSubTab === 'analyze' && styles.subTabTextActive,
              ]}
            >
              Analyze
            </Text>
          </Pressable>
          <Pressable
            style={[styles.subTab, activeSubTab === 'guide' && styles.subTabActive]}
            onPress={() => setActiveSubTab('guide')}
          >
            <Text
              style={[styles.subTabText, activeSubTab === 'guide' && styles.subTabTextActive]}
            >
              Guide
            </Text>
          </Pressable>
        </View>
      </View>

      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
      >
        {activeSubTab === 'analyze' ? renderAnalyzeTab() : renderGuideTab()}
      </ScrollView>
    </View>
  );
}
