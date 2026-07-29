import React, { useState } from 'react';
import {
  AccessibilityInfo,
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
import * as ImagePicker from 'expo-image-picker';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useApp } from '@/context/AppContext';
import { useColors } from '@/hooks/useColors';

// ─── OCR via OCR.space free API ───────────────────────────────────────────────

async function ocrImageBase64(base64: string): Promise<string> {
  const formData = new FormData();
  formData.append('apikey', 'helloworld'); // OCR.space free public key
  formData.append('language', 'eng');
  formData.append('isOverlayRequired', 'false');
  formData.append('detectOrientation', 'true');
  formData.append('base64Image', `data:image/jpeg;base64,${base64}`);

  const res = await fetch('https://api.ocr.space/parse/image', {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error(`OCR service error ${res.status}`);
  const data = (await res.json()) as {
    ParsedResults?: Array<{ ParsedText?: string }>;
    IsErroredOnProcessing?: boolean;
    ErrorMessage?: string;
  };
  if (data.IsErroredOnProcessing) throw new Error(data.ErrorMessage ?? 'OCR failed');
  return data.ParsedResults?.[0]?.ParsedText?.trim() ?? '';
}

// ─── Deadline / Date Extraction ───────────────────────────────────────────────

export interface ExtractionResult {
  dates: string[];
  deadlines: string[];
  penalties: string[];
  actions: string[];
}

const MONTHS =
  'January|February|March|April|May|June|July|August|September|October|November|December';

export function extractFromText(raw: string): ExtractionResult {
  const lines = raw.split(/\r?\n/);

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
    for (const m of raw.matchAll(pattern)) {
      const val = m[0].trim();
      if (!dates.includes(val)) dates.push(val);
    }
  }

  const deadlineRx =
    /\b(must|required|deadline|due|respond|file|appear|hearing|court\s*date|action\s*required|notice|warning|comply|submit|failure\s+to)\b/i;
  const deadlines: string[] = [];
  for (const line of lines) {
    const t = line.trim();
    if (t.length > 10 && deadlineRx.test(t)) {
      const val = t.slice(0, 240);
      if (!deadlines.includes(val)) deadlines.push(val);
    }
  }

  const penaltyRx =
    /\b(penalty|fine|arrest|warrant|failure\s+to|consequences|charged|prosecution|imprisonment|revoked)\b/i;
  const penalties: string[] = [];
  for (const line of lines) {
    const t = line.trim();
    if (t.length > 5 && penaltyRx.test(t)) {
      const val = t.slice(0, 240);
      if (!penalties.includes(val)) penalties.push(val);
    }
  }

  const actionRx = /^\s*\d+[.)]\s|^\s*[-•]\s|bring|provide|submit|pay\b|appear\b|complete|sign\b/i;
  const actions: string[] = [];
  for (const line of lines) {
    const t = line.trim();
    if (t.length > 5 && actionRx.test(t)) {
      const val = t.slice(0, 240);
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

// ─── Result Section ───────────────────────────────────────────────────────────

function ResultSection({
  label, icon, color, items, emptyMsg,
}: {
  label: string; icon: string; color: string; items: string[]; emptyMsg: string;
}) {
  const colors = useColors();
  const { fs } = useApp();
  return (
    <View style={{ marginBottom: 16 }}>
      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 8 }}>
        <Feather name={icon as never} size={15} color={color} />
        <Text
          style={{ fontSize: fs(12), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase', letterSpacing: 0.7 }}
          accessibilityRole="header"
        >
          {label}
        </Text>
        {items.length > 0 && (
          <View style={{ backgroundColor: color + '22', borderRadius: 10, paddingHorizontal: 7, paddingVertical: 2 }}>
            <Text style={{ fontSize: fs(11), fontFamily: 'Inter_600SemiBold', color }}>{items.length}</Text>
          </View>
        )}
      </View>
      {items.length === 0 ? (
        <Text style={{ fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground }}>{emptyMsg}</Text>
      ) : (
        items.map((item, i) => (
          <View key={i} style={{ backgroundColor: color + '10', borderLeftWidth: 3, borderLeftColor: color, borderRadius: 6, padding: 10, marginBottom: 6 }}>
            <Text style={{ fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.foreground, lineHeight: 19 }} selectable>
              {item}
            </Text>
          </View>
        ))
      )}
    </View>
  );
}

// ─── Main Screen ──────────────────────────────────────────────────────────────

export default function DocsScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const { addDeadline, pendingDocText, setPendingDocText, fs } = useApp();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;

  const [inputText, setInputText] = useState('');
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [ocrLoading, setOcrLoading] = useState(false);
  const [showQR, setShowQR] = useState(false);
  const [activeSubTab, setActiveSubTab] = useState<'analyze' | 'guide'>('analyze');
  const [savedIds, setSavedIds] = useState<Set<string>>(new Set());

  // If navigated here from a saved deadline's "View Case Details", pre-populate the text
  React.useEffect(() => {
    if (pendingDocText) {
      setInputText(pendingDocText);
      setResult(null);
      setShowQR(false);
      setSavedIds(new Set());
      setPendingDocText(null);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleAnalyze = () => {
    if (!inputText.trim()) {
      Alert.alert('No Text', 'Please paste legal text, load a sample, or scan a document image.');
      return;
    }
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    setAnalyzing(true);
    setShowQR(false);
    setTimeout(() => {
      const r = extractFromText(inputText);
      setResult(r);
      setAnalyzing(false);
      const totalFound = r.dates.length + r.deadlines.length + r.penalties.length + r.actions.length;
      AccessibilityInfo.announceForAccessibility(
        totalFound > 0 ? `Analysis complete. Found ${totalFound} items.` : 'Analysis complete. No structured items found.',
      );
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    }, 500);
  };

  // ── Image / Camera picker → OCR ──────────────────────────────────────────
  const pickImage = async (useCamera: boolean) => {
    const permResult = useCamera
      ? await ImagePicker.requestCameraPermissionsAsync()
      : await ImagePicker.requestMediaLibraryPermissionsAsync();

    if (permResult.status !== 'granted') {
      Alert.alert('Permission Required', useCamera
        ? 'Camera permission is needed to scan documents.'
        : 'Photo library permission is needed to select images.');
      return;
    }

    const pickerResult = useCamera
      ? await ImagePicker.launchCameraAsync({ base64: true, quality: 0.85, allowsEditing: true })
      : await ImagePicker.launchImageLibraryAsync({ base64: true, quality: 0.85, mediaTypes: 'images', allowsEditing: false });

    if (pickerResult.canceled || !pickerResult.assets?.[0]) return;

    const asset = pickerResult.assets[0];
    if (!asset.base64) {
      Alert.alert('Error', 'Could not read image data. Please try another image.');
      return;
    }

    setOcrLoading(true);
    setResult(null);
    setShowQR(false);
    try {
      const text = await ocrImageBase64(asset.base64);
      if (!text) {
        Alert.alert(
          'No Text Found',
          'Could not extract text from this image. Try a clearer, well-lit photo, or type/paste the text manually.',
        );
      } else {
        setInputText(text);
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        // Auto-analyze after OCR
        setTimeout(() => {
          setResult(extractFromText(text));
        }, 100);
      }
    } catch {
      Alert.alert('OCR Failed', 'Could not read text from the image. Please try again or paste the text manually.');
    } finally {
      setOcrLoading(false);
    }
  };

  const showImageOptions = () => {
    Alert.alert('Scan Document', 'Choose how to provide the document:', [
      { text: '📷 Take Photo', onPress: () => pickImage(true) },
      { text: '🖼️ Choose from Library', onPress: () => pickImage(false) },
      { text: 'Cancel', style: 'cancel' },
    ]);
  };

  // ── Save deadlines to dashboard ───────────────────────────────────────────
  const handleSaveDeadline = async (text: string, key: string) => {
    await addDeadline(text, 'Document Analyzer', inputText);
    setSavedIds((prev) => new Set(prev).add(key));
    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    Alert.alert('✅ Saved to Dashboard', 'This important date is now pinned at the top of your Home screen. Tap it to return to this document.');
  };

  const handleSaveAll = async () => {
    if (!result) return;
    const all = [
      ...result.deadlines,
      ...result.dates.map((d) => `Date: ${d}`),
      ...result.penalties.map((p) => `Penalty: ${p}`),
    ];
    if (all.length === 0) {
      Alert.alert('Nothing to Save', 'No deadlines or dates were found to save.');
      return;
    }
    for (const item of all.slice(0, 5)) {
      await addDeadline(item, 'Document Analyzer', inputText);
    }
    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    Alert.alert(
      `✅ Saved ${Math.min(all.length, 5)} Important Date${Math.min(all.length, 5) === 1 ? '' : 's'}`,
      'These are pinned at the top of your Home screen. Tap any one to return to this document.',
    );
  };

  const handleCopy = async () => {
    if (!result) return;
    const parts = [
      result.dates.length > 0 ? `DATES:\n${result.dates.map((d) => `• ${d}`).join('\n')}` : '',
      result.deadlines.length > 0 ? `\nDEADLINES:\n${result.deadlines.map((d) => `• ${d}`).join('\n')}` : '',
      result.penalties.length > 0 ? `\nPENALTIES:\n${result.penalties.map((d) => `• ${d}`).join('\n')}` : '',
      result.actions.length > 0 ? `\nREQUIRED ACTIONS:\n${result.actions.map((d) => `• ${d}`).join('\n')}` : '',
    ].filter(Boolean).join('');
    await Clipboard.setStringAsync(parts || 'No items found.');
    Alert.alert('Copied', 'Summary copied to clipboard.');
  };

  const qrContent = result
    ? [
        result.dates.length > 0 ? `Dates: ${result.dates.slice(0, 3).join(', ')}` : '',
        result.deadlines.length > 0 ? `Deadlines: ${result.deadlines[0].slice(0, 80)}` : '',
        result.penalties.length > 0 ? `Penalty: ${result.penalties[0].slice(0, 60)}` : '',
      ].filter(Boolean).join(' | ')
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
      paddingTop: topPad + 12, paddingHorizontal: 20, paddingBottom: 0,
      borderBottomWidth: 1, borderBottomColor: colors.border,
    },
    headerTitle: { fontSize: fs(22), fontFamily: 'Inter_700Bold', color: colors.foreground },
    headerSub: { fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 2, marginBottom: 12 },
    subTabRow: { flexDirection: 'row' },
    subTab: { flex: 1, paddingVertical: 10, alignItems: 'center', borderBottomWidth: 2, borderBottomColor: 'transparent' },
    subTabActive: { borderBottomColor: colors.primary },
    subTabText: { fontSize: fs(14), fontFamily: 'Inter_500Medium', color: colors.mutedForeground },
    subTabTextActive: { color: colors.primary, fontFamily: 'Inter_600SemiBold' },
    scroll: { flex: 1 },
    scrollContent: { padding: 16, paddingBottom: Platform.OS === 'web' ? 34 : 100, flexGrow: 1 },
    card: { backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1, borderColor: colors.border, marginBottom: 12, overflow: 'hidden' },
    cardHeader: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 14, paddingTop: 12, marginBottom: 4, gap: 6 },
    cardLabel: { flex: 1, fontSize: fs(12), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase', letterSpacing: 0.6 },
    charCount: { fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground },
    textInput: { fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.foreground, paddingHorizontal: 14, paddingBottom: 14, minHeight: 130, textAlignVertical: 'top' },
    actionRow: { flexDirection: 'row', gap: 8, marginBottom: 12 },
    actionBtn: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6, borderRadius: colors.radius, paddingVertical: 11, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.card },
    actionBtnText: { fontSize: fs(13), fontFamily: 'Inter_500Medium', color: colors.foreground },
    analyzeBtn: { backgroundColor: colors.primary, borderRadius: colors.radius, paddingVertical: 15, alignItems: 'center', justifyContent: 'center', flexDirection: 'row', gap: 8, marginBottom: 16 },
    analyzeBtnDisabled: { opacity: 0.5 },
    analyzeBtnText: { fontSize: fs(16), fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' },
    resultHeader: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 },
    resultTitle: { fontSize: fs(16), fontFamily: 'Inter_700Bold', color: colors.foreground },
    iconBtn: { width: 36, height: 36, borderRadius: 18, backgroundColor: colors.muted, alignItems: 'center', justifyContent: 'center' },
    saveDashBtn: { flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: '#C9A050', borderRadius: colors.radius, paddingVertical: 13, paddingHorizontal: 16, justifyContent: 'center', marginBottom: 16 },
    saveDashText: { fontSize: fs(14), fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' },
    qrContainer: { alignItems: 'center', backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1, borderColor: colors.border, padding: 20, marginBottom: 16 },
    tipCard: { backgroundColor: colors.primary + '0F', borderRadius: colors.radius, padding: 14, borderWidth: 1, borderColor: colors.primary + '20', flexDirection: 'row', gap: 10, marginBottom: 12 },
    tipText: { flex: 1, fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 20 },
    ocrOverlay: { backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1, borderColor: colors.border, padding: 20, alignItems: 'center', gap: 10, marginBottom: 12 },
  });

  const renderAnalyzeTab = () => (
    <>
      {/* Input card */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Text style={styles.cardLabel} accessibilityRole="header">Legal Text</Text>
          <Text style={styles.charCount}>{inputText.length} chars</Text>
        </View>
        <TextInput
          style={styles.textInput}
          value={inputText}
          onChangeText={setInputText}
          multiline
          placeholder="Paste or type legal document text here…"
          placeholderTextColor={colors.mutedForeground}
          accessibilityLabel="Legal document text input"
          accessibilityHint="Paste text from a court notice, eviction letter, or any legal document"
        />
      </View>

      {/* Action buttons row */}
      <View style={styles.actionRow}>
        <Pressable
          style={styles.actionBtn}
          onPress={showImageOptions}
          disabled={ocrLoading}
          accessibilityLabel="Scan document image"
          accessibilityRole="button"
        >
          {ocrLoading
            ? <ActivityIndicator size="small" color={colors.primary} />
            : <Feather name="camera" size={15} color={colors.primary} />}
          <Text style={[styles.actionBtnText, { color: colors.primary }]}>
            {ocrLoading ? 'Scanning…' : 'Scan Image'}
          </Text>
        </Pressable>
        <Pressable
          style={styles.actionBtn}
          onPress={() => { setInputText(SAMPLE_TEXT); setResult(null); setShowQR(false); }}
          accessibilityLabel="Load sample document"
          accessibilityRole="button"
        >
          <Feather name="file-text" size={15} color={colors.foreground} />
          <Text style={styles.actionBtnText}>Sample</Text>
        </Pressable>
        {inputText.length > 0 && (
          <Pressable
            style={[styles.actionBtn, { flex: 0, paddingHorizontal: 14 }]}
            onPress={() => { setInputText(''); setResult(null); setShowQR(false); }}
            accessibilityLabel="Clear text"
            accessibilityRole="button"
          >
            <Feather name="x" size={17} color={colors.mutedForeground} />
          </Pressable>
        )}
      </View>

      {/* OCR loading overlay */}
      {ocrLoading && (
        <View style={styles.ocrOverlay}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={{ fontSize: fs(14), fontFamily: 'Inter_500Medium', color: colors.foreground }}>
            Reading document…
          </Text>
          <Text style={{ fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground }}>
            OCR is extracting text from your image
          </Text>
        </View>
      )}

      {/* Analyze button */}
      <Pressable
        style={[styles.analyzeBtn, (!inputText.trim() || analyzing || ocrLoading) && styles.analyzeBtnDisabled]}
        onPress={handleAnalyze}
        disabled={!inputText.trim() || analyzing || ocrLoading}
        accessibilityLabel="Extract deadlines and dates"
        accessibilityRole="button"
      >
        {analyzing
          ? <ActivityIndicator size="small" color="#FFFFFF" />
          : <Feather name="search" size={18} color="#FFFFFF" />}
        <Text style={styles.analyzeBtnText}>
          {analyzing ? 'Analyzing…' : '🔍 Extract Deadlines & Dates'}
        </Text>
      </Pressable>

      {/* Results */}
      {result && (
        <>
          <View style={styles.resultHeader}>
            <Text style={styles.resultTitle} accessibilityRole="header">
              Results {totalFound > 0 ? `(${totalFound} found)` : ''}
            </Text>
            <View style={{ flexDirection: 'row', gap: 8 }}>
              <Pressable style={styles.iconBtn} onPress={() => setShowQR((p) => !p)} accessibilityLabel="Toggle QR code" accessibilityRole="button">
                <Feather name="grid" size={16} color={colors.foreground} />
              </Pressable>
              <Pressable style={styles.iconBtn} onPress={handleCopy} accessibilityLabel="Copy summary" accessibilityRole="button">
                <Feather name="copy" size={16} color={colors.foreground} />
              </Pressable>
            </View>
          </View>

          {/* Save to Dashboard — primary CTA */}
          {totalFound > 0 && (
            <Pressable
              style={styles.saveDashBtn}
              onPress={handleSaveAll}
              accessibilityLabel="Save deadlines to dashboard"
              accessibilityRole="button"
            >
              <Feather name="bookmark" size={16} color="#FFFFFF" />
              <Text style={styles.saveDashText}>💾 Save Deadlines to Dashboard</Text>
            </Pressable>
          )}

          {/* QR code */}
          {showQR && qrContent && (
            <View style={styles.qrContainer}>
              <Image source={{ uri: qrImageUrl }} style={{ width: 220, height: 220 }} resizeMode="contain" accessibilityLabel="QR code of extracted deadlines" />
              <Text style={{ fontSize: fs(12), fontFamily: 'Inter_500Medium', color: colors.mutedForeground, marginTop: 10, textAlign: 'center' }}>
                Scan to share extracted deadlines
              </Text>
            </View>
          )}

          <ResultSection label="Important Dates" icon="calendar" color="#C9A050" items={result.dates} emptyMsg="No specific dates found." />
          <ResultSection label="Deadlines & Actions Required" icon="alert-circle" color={colors.primary} items={result.deadlines} emptyMsg="No deadlines detected." />
          <ResultSection label="Penalties & Warnings" icon="alert-triangle" color="#E05252" items={result.penalties} emptyMsg="No penalties found." />
          <ResultSection label="Required Actions" icon="check-square" color="#5A9E6F" items={result.actions} emptyMsg="No required actions found." />

          {totalFound === 0 && (
            <View style={styles.tipCard}>
              <Feather name="info" size={16} color={colors.primary} />
              <Text style={styles.tipText}>No structured items detected. Try the sample document or paste more complete legal text.</Text>
            </View>
          )}
        </>
      )}

      {!result && !ocrLoading && (
        <View style={styles.tipCard}>
          <Feather name="info" size={16} color={colors.primary} />
          <Text style={styles.tipText}>
            Paste text from a court notice or tap <Text style={{ fontFamily: 'Inter_600SemiBold' }}>Scan Image</Text> to photograph a document. The analyzer finds dates, deadlines, penalties, and required actions.
          </Text>
        </View>
      )}
    </>
  );

  const renderGuideTab = () => (
    <>
      {[
        { title: '📋 What This Tool Detects', body: '• Court appearance dates and hearing dates\n• Filing deadlines and response windows\n• "Within X days" notice periods\n• Penalty and fine amounts\n• Required action items (bring ID, pay fee, etc.)\n• Warrant and arrest warnings' },
        { title: '📄 Supported Document Types', body: '• Court summons and notices to appear\n• Eviction notices (30/60/90-day)\n• Traffic citations\n• Immigration notices\n• Lease violation letters\n• Government benefit denial letters' },
        { title: '📷 Scanning a Document', body: 'Tap "Scan Image" to photograph a document or choose one from your library. The OCR engine will extract the text automatically. For best results, use good lighting and hold the camera steady.' },
        { title: '📱 QR Code Sharing', body: 'After extracting, tap the grid icon (⊞) to generate a QR code. Share it with a lawyer or advocate so they can instantly see your key deadlines.' },
        { title: '💾 Saving to Dashboard', body: 'Tap "Save Deadlines to Dashboard" and your key deadlines will appear pinned at the top of your Home screen as reminders.' },
      ].map((s) => (
        <View key={s.title} style={{ backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1, borderColor: colors.border, padding: 16, marginBottom: 12 }}>
          <Text style={{ fontSize: fs(15), fontFamily: 'Inter_600SemiBold', color: colors.foreground, marginBottom: 8 }} accessibilityRole="header">{s.title}</Text>
          <Text style={{ fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 20 }}>{s.body}</Text>
        </View>
      ))}
      <View style={styles.tipCard}>
        <Feather name="shield" size={16} color={colors.primary} />
        <Text style={styles.tipText}>General information only — not legal advice. Check the Resources tab for free legal aid near you.</Text>
      </View>
    </>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle} accessibilityRole="header">📄 Document Analyzer</Text>
        <Text style={styles.headerSub}>Text or image — extract deadlines, dates & penalties</Text>
        <View style={styles.subTabRow}>
          {(['analyze', 'guide'] as const).map((tab) => (
            <Pressable key={tab} style={[styles.subTab, activeSubTab === tab && styles.subTabActive]} onPress={() => setActiveSubTab(tab)} accessibilityRole="tab" accessibilityState={{ selected: activeSubTab === tab }}>
              <Text style={[styles.subTabText, activeSubTab === tab && styles.subTabTextActive]}>
                {tab === 'analyze' ? 'Analyze' : 'Guide'}
              </Text>
            </Pressable>
          ))}
        </View>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent} keyboardShouldPersistTaps="handled">
        {activeSubTab === 'analyze' ? renderAnalyzeTab() : renderGuideTab()}
      </ScrollView>
    </View>
  );
}
