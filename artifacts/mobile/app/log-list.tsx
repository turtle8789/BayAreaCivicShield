import React, { useState } from 'react';
import {
  Alert,
  FlatList,
  KeyboardAvoidingView,
  Modal,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { router } from 'expo-router';
import { Feather } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import * as ExpoCrypto from 'expo-crypto';
import * as FileSystem from 'expo-file-system/legacy';
import * as Print from 'expo-print';
import * as Sharing from 'expo-sharing';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import CryptoJS from 'crypto-js';
import { Encounter, ENCOUNTER_TYPE_LABELS, useApp } from '@/context/AppContext';
import { useColors } from '@/hooks/useColors';
import { useRTL } from '@/hooks/useRTL';
import { useT } from '@/hooks/useTranslation';

// ─── EncounterCard ─────────────────────────────────────────────────────────────

function EncounterCard({ encounter, onDelete }: { encounter: Encounter; onDelete: () => void }) {
  const colors = useColors();
  const { fs } = useApp();
  const { t } = useT();
  const { rowDir, textStyle } = useRTL();
  const [expanded, setExpanded] = useState(false);
  const [shareModalVisible, setShareModalVisible] = useState(false);
  const [isSharing, setIsSharing] = useState(false);

  const date = new Date(encounter.date);
  const formattedDate = date.toLocaleDateString(undefined, {
    month: 'short', day: 'numeric', year: 'numeric',
  });
  const formattedTime = date.toLocaleTimeString(undefined, {
    hour: '2-digit', minute: '2-digit',
  });

  const handleDelete = () => {
    Alert.alert(t('log.delete_title'), t('log.delete_msg'), [
      { text: t('log.delete_cancel'), style: 'cancel' },
      {
        text: t('log.delete_btn'),
        style: 'destructive',
        onPress: () => {
          Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
          onDelete();
        },
      },
    ]);
  };

  const handleShare = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    setShareModalVisible(true);
  };

  const doSingleExport = async (password: string | null) => {
    setShareModalVisible(false);
    setIsSharing(true);
    try {
      const html = buildEncounterHtml([encounter], t('log.export_title'));

      if (password) {
        const encryptedPayload = aesEncryptStrong(html, password);
        const wrapperHtml = buildProtectedHtml(encryptedPayload, t('log.export_title'));

        const canShare = await Sharing.isAvailableAsync();
        if (canShare) {
          const fileUri = (FileSystem.cacheDirectory ?? '') + `encounter-${encounter.id}-protected.html`;
          await FileSystem.writeAsStringAsync(fileUri, wrapperHtml, {
            encoding: FileSystem.EncodingType.UTF8,
          });
          await Sharing.shareAsync(fileUri, {
            mimeType: 'text/html',
            dialogTitle: t('log.export_title'),
            UTI: 'public.html',
          });
        } else {
          if (typeof window !== 'undefined') {
            const blob = new Blob([wrapperHtml], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            window.open(url, '_blank');
          }
        }
      } else {
        const { uri } = await Print.printToFileAsync({ html, base64: false });
        const canShare = await Sharing.isAvailableAsync();
        if (canShare) {
          await Sharing.shareAsync(uri, {
            mimeType: 'application/pdf',
            dialogTitle: t('log.export_title'),
            UTI: 'com.adobe.pdf',
          });
        } else {
          await Print.printAsync({ html });
        }
      }
    } catch {
      Alert.alert(t('log.export_btn'), t('log.export_error'));
    } finally {
      setIsSharing(false);
    }
  };

  const typeKey = `encounter.${encounter.type}` as any;

  const styles = StyleSheet.create({
    card: {
      backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1,
      borderColor: colors.border, marginBottom: 10, overflow: 'hidden',
    },
    cardHeader:     { flexDirection: rowDir, alignItems: 'center', padding: 14, gap: 10 },
    typeDot:        { width: 10, height: 10, borderRadius: 5, backgroundColor: colors.primary },
    typeLabel:      { fontSize: fs(15), fontFamily: 'Inter_600SemiBold', color: colors.foreground },
    dateText:       { fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground },
    expandedSection:{ borderTopWidth: 1, borderTopColor: colors.border, padding: 14, gap: 10 },
    fieldLabel:     { fontSize: fs(11), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase', letterSpacing: 0.6, marginBottom: 2 },
    fieldValue:     { fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.foreground, lineHeight: 20, ...textStyle },
    deleteBtn:      { flex: 1, flexDirection: rowDir, alignItems: 'center', justifyContent: 'center', gap: 6, borderRadius: 10, paddingVertical: 9, backgroundColor: colors.destructive + '12', borderWidth: 1, borderColor: colors.destructive + '25' },
    shareBtn:       { flex: 1, flexDirection: rowDir, alignItems: 'center', justifyContent: 'center', gap: 6, borderRadius: 10, paddingVertical: 9, backgroundColor: colors.primary + '12', borderWidth: 1, borderColor: colors.primary + '25' },
  });

  return (
    <View style={styles.card}>
      <Pressable style={styles.cardHeader} onPress={() => setExpanded(!expanded)}>
        <View style={styles.typeDot} />
        <View style={{ flex: 1 }}>
          <Text style={styles.typeLabel}>{t(typeKey)}</Text>
          <View style={{ flexDirection: rowDir, gap: 6, marginTop: 2 }}>
            <Text style={styles.dateText}>{formattedDate} {t('log.at')} {formattedTime}</Text>
            {encounter.location ? <Text style={styles.dateText}>· {encounter.location}</Text> : null}
          </View>
        </View>
        <Feather name={expanded ? 'chevron-up' : 'chevron-down'} size={18} color={colors.mutedForeground} />
      </Pressable>

      {expanded && (
        <View style={styles.expandedSection}>
          {encounter.officerInfo ? (
            <View>
              <Text style={styles.fieldLabel}>{t('log.officer_info')}</Text>
              <Text style={styles.fieldValue}>{encounter.officerInfo}</Text>
            </View>
          ) : null}
          {encounter.description ? (
            <View>
              <Text style={styles.fieldLabel}>{t('log.description_label')}</Text>
              <Text style={styles.fieldValue}>{encounter.description}</Text>
            </View>
          ) : null}
          {encounter.outcome ? (
            <View>
              <Text style={styles.fieldLabel}>{t('log.outcome_label')}</Text>
              <Text style={styles.fieldValue}>{encounter.outcome}</Text>
            </View>
          ) : null}
          <View style={{ flexDirection: rowDir, marginTop: 4, gap: 8 }}>
            <Pressable style={styles.shareBtn} onPress={handleShare} disabled={isSharing}>
              <Feather name="share" size={14} color={isSharing ? colors.mutedForeground : colors.primary} />
              <Text style={{ fontSize: fs(13), fontFamily: 'Inter_500Medium', color: isSharing ? colors.mutedForeground : colors.primary }}>
                {t('log.share_btn')}
              </Text>
            </Pressable>
            <Pressable style={styles.deleteBtn} onPress={handleDelete}>
              <Feather name="trash-2" size={14} color={colors.destructive} />
              <Text style={{ fontSize: fs(13), fontFamily: 'Inter_500Medium', color: colors.destructive }}>
                {t('log.delete_btn')}
              </Text>
            </Pressable>
          </View>
        </View>
      )}

      <PasswordModal
        visible={shareModalVisible}
        onCancel={() => setShareModalVisible(false)}
        onShare={doSingleExport}
      />
    </View>
  );
}

// ─── HTML builder ──────────────────────────────────────────────────────────────

function buildEncounterHtml(encounters: Encounter[], exportTitle: string): string {
  const now = new Date().toLocaleDateString(undefined, {
    month: 'long', day: 'numeric', year: 'numeric',
  });

  const rows = encounters.map((enc) => {
    const date = new Date(enc.date);
    const dateStr = date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    const timeStr = date.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
    const typeLabel = ENCOUNTER_TYPE_LABELS[enc.type] ?? enc.type;

    const fields: Array<{ label: string; value: string }> = [
      { label: 'Date & Time', value: `${dateStr} at ${timeStr}` },
      { label: 'Type', value: typeLabel },
    ];
    if (enc.location)    fields.push({ label: 'Location',     value: enc.location });
    if (enc.officerInfo) fields.push({ label: 'Officer Info', value: enc.officerInfo });
    if (enc.description) fields.push({ label: 'Description',  value: enc.description });
    if (enc.outcome)     fields.push({ label: 'Outcome',      value: enc.outcome });

    const fieldRows = fields.map(f => `
      <tr>
        <td class="label">${f.label}</td>
        <td class="value">${f.value.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</td>
      </tr>`).join('');

    return `
      <div class="entry">
        <table>${fieldRows}</table>
      </div>`;
  }).join('');

  return `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<style>
  body { font-family: -apple-system, Helvetica, Arial, sans-serif; margin: 0; padding: 32px; color: #111; }
  h1 { font-size: 22px; font-weight: 700; margin: 0 0 4px; color: #111; }
  .meta { font-size: 12px; color: #666; margin-bottom: 28px; }
  .entry { border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px; margin-bottom: 16px; break-inside: avoid; }
  table { width: 100%; border-collapse: collapse; }
  td { padding: 5px 8px; font-size: 13px; vertical-align: top; }
  td.label { color: #666; font-weight: 600; text-transform: uppercase; font-size: 10px; letter-spacing: 0.5px; width: 110px; padding-top: 7px; }
  td.value { color: #111; line-height: 1.5; }
  .footer { margin-top: 32px; font-size: 11px; color: #999; border-top: 1px solid #e0e0e0; padding-top: 12px; }
</style>
</head>
<body>
  <h1>${exportTitle}</h1>
  <div class="meta">Generated on ${now} · ${encounters.length} ${encounters.length === 1 ? 'entry' : 'entries'}</div>
  ${rows}
  <div class="footer">CivicShield Pro · Encounter Log · This document is for personal legal reference only.</div>
</body>
</html>`;
}

// ─── Encryption helpers ────────────────────────────────────────────────────────

/** Converts a Uint8Array to a lowercase hex string. */
function uint8ToHex(bytes: Uint8Array): string {
  return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Encrypts plaintext with AES-256-CBC using a PBKDF2-derived key.
 * Key derivation: PBKDF2-SHA256, 100 000 iterations, 16-byte random salt.
 * Random bytes are sourced from expo-crypto (native CSPRNG) to avoid
 * the crypto.getRandomValues dependency that CryptoJS.lib.WordArray.random
 * requires in React Native.
 * Returns a JSON payload string containing version, salt (hex), IV (hex), and
 * ciphertext (Base64) — safe to embed in an HTML template literal.
 */
function aesEncryptStrong(plaintext: string, password: string): string {
  // Use expo-crypto for cryptographically secure random bytes (16 bytes each)
  const saltHex = uint8ToHex(ExpoCrypto.getRandomBytes(16));
  const ivHex   = uint8ToHex(ExpoCrypto.getRandomBytes(16));

  const salt = CryptoJS.enc.Hex.parse(saltHex);
  const iv   = CryptoJS.enc.Hex.parse(ivHex);

  const key = CryptoJS.PBKDF2(password, salt, {
    keySize:    256 / 32, // 256-bit key
    iterations: 100_000,
    hasher:     CryptoJS.algo.SHA256,
  });
  const ciphertext = CryptoJS.AES.encrypt(plaintext, key, {
    iv,
    mode:    CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7,
  });
  return JSON.stringify({
    v: 1,
    s: saltHex,
    i: ivHex,
    c: ciphertext.toString(),  // Base64
  });
}

// ─── Self-decrypting HTML wrapper ──────────────────────────────────────────────

function buildProtectedHtml(encryptedPayload: string, exportTitle: string): string {
  // Safely embed the JSON payload as a JS string literal
  const safePayload = encryptedPayload.replace(/\\/g, '\\\\').replace(/`/g, '\\`');
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>🔒 ${exportTitle} – CivicShield Pro</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:-apple-system,Helvetica,Arial,sans-serif;background:#f5f5f7;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
  .card{background:#fff;border-radius:16px;padding:40px 32px;max-width:420px;width:100%;box-shadow:0 4px 24px rgba(0,0,0,0.08);text-align:center}
  .shield{width:72px;height:72px;background:#0a7ea4;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 20px;font-size:32px}
  h1{font-size:20px;font-weight:700;color:#111;margin-bottom:8px}
  p{font-size:14px;color:#666;line-height:1.5;margin-bottom:24px}
  input{width:100%;border:1.5px solid #ddd;border-radius:10px;padding:12px 16px;font-size:16px;outline:none;transition:border-color .2s;margin-bottom:12px}
  input:focus{border-color:#0a7ea4}
  button{width:100%;background:#0a7ea4;color:#fff;border:none;border-radius:10px;padding:14px;font-size:16px;font-weight:600;cursor:pointer;transition:opacity .2s}
  button:hover{opacity:0.88}
  button:disabled{opacity:0.5;cursor:not-allowed}
  .err{color:#d32f2f;font-size:13px;margin-top:8px;display:none}
  .note{font-size:11px;color:#aaa;margin-top:20px;line-height:1.5}
  #doc{display:none}
</style>
</head>
<body>
<div class="card" id="lock-card">
  <div class="shield">🔒</div>
  <h1>Password Protected</h1>
  <p>This encounter log is encrypted with AES-256 + PBKDF2. Enter the password to view its contents.</p>
  <input type="password" id="pwd" placeholder="Enter password" autocomplete="current-password"/>
  <button id="unlockBtn" onclick="unlock()">Unlock</button>
  <div class="err" id="err">Incorrect password. Please try again.</div>
  <div class="note">Encrypted by CivicShield Pro · AES-256-CBC / PBKDF2-SHA256 (100 000 iterations)<br/>An internet connection is required to load the decryption library.</div>
</div>
<div id="doc"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.2.0/crypto-js.min.js"
  integrity="sha512-a+SUDuwNzXDvz4XrIcXHuCFDqPxFPFN3IRlhS1yVHf+CYY5wDkU3yDe5pLYGbJ4K0XE7CyFRFn3KcbZLpXZQ=="
  crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<script>
var PAYLOAD=\`${safePayload}\`;
function unlock(){
  var btn=document.getElementById('unlockBtn');
  var pwd=document.getElementById('pwd').value;
  if(!pwd)return;
  btn.disabled=true;
  btn.textContent='Unlocking\u2026';
  // Run key derivation async so the UI can update first
  setTimeout(function(){
    try{
      var p=JSON.parse(PAYLOAD);
      if(p.v!==1)throw new Error('unsupported version');
      var salt=CryptoJS.enc.Hex.parse(p.s);
      var iv=CryptoJS.enc.Hex.parse(p.i);
      var key=CryptoJS.PBKDF2(pwd,salt,{keySize:8,iterations:100000,hasher:CryptoJS.algo.SHA256});
      var decrypted=CryptoJS.AES.decrypt(p.c,key,{iv:iv,mode:CryptoJS.mode.CBC,padding:CryptoJS.pad.Pkcs7});
      var html=decrypted.toString(CryptoJS.enc.Utf8);
      if(!html||html.length<50)throw new Error('bad decrypt');
      document.getElementById('lock-card').style.display='none';
      var doc=document.getElementById('doc');
      doc.style.display='block';
      doc.innerHTML=html;
    }catch(e){
      document.getElementById('err').style.display='block';
      btn.disabled=false;
      btn.textContent='Unlock';
      document.getElementById('pwd').value='';
      document.getElementById('pwd').focus();
    }
  },50);
}
document.getElementById('pwd').addEventListener('keydown',function(e){if(e.key==='Enter')unlock();});
</script>
</body>
</html>`;
}

// ─── Password Modal ────────────────────────────────────────────────────────────

interface PasswordModalProps {
  visible: boolean;
  onCancel: () => void;
  onShare: (password: string | null) => void;
}

function PasswordModal({ visible, onCancel, onShare }: PasswordModalProps) {
  const colors = useColors();
  const { fs } = useApp();
  const { t } = useT();
  const [password, setPassword] = useState('');

  const handleClose = () => {
    setPassword('');
    onCancel();
  };

  const handleSkip = () => {
    setPassword('');
    onShare(null);
  };

  const handleProtected = () => {
    const pwd = password.trim();
    setPassword('');
    onShare(pwd.length > 0 ? pwd : null);
  };

  const hasPassword = password.trim().length > 0;

  const s = StyleSheet.create({
    overlay:    { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
    sheet:      { backgroundColor: colors.background, borderTopLeftRadius: 20, borderTopRightRadius: 20, padding: 24, paddingBottom: 36 },
    handle:     { width: 36, height: 4, borderRadius: 2, backgroundColor: colors.border, alignSelf: 'center', marginBottom: 20 },
    iconWrap:   { width: 56, height: 56, borderRadius: 28, backgroundColor: colors.primary + '18', alignItems: 'center', justifyContent: 'center', alignSelf: 'center', marginBottom: 14 },
    title:      { fontSize: fs(18), fontFamily: 'Inter_700Bold', color: colors.foreground, textAlign: 'center', marginBottom: 8 },
    desc:       { fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, textAlign: 'center', lineHeight: 19, marginBottom: 20 },
    input:      { backgroundColor: colors.muted, borderRadius: 12, borderWidth: 1, borderColor: colors.border, paddingHorizontal: 16, paddingVertical: 12, fontSize: fs(15), fontFamily: 'Inter_400Regular', color: colors.foreground, marginBottom: 16 },
    btnPrimary: { backgroundColor: colors.primary, borderRadius: 12, paddingVertical: 14, alignItems: 'center', marginBottom: 10 },
    btnOutline: { backgroundColor: 'transparent', borderRadius: 12, paddingVertical: 14, alignItems: 'center', borderWidth: 1, borderColor: colors.border, marginBottom: 10 },
    btnCancel:  { paddingVertical: 10, alignItems: 'center' },
    btnTextPrimary: { fontSize: fs(15), fontFamily: 'Inter_600SemiBold', color: colors.primaryForeground },
    btnTextOutline: { fontSize: fs(15), fontFamily: 'Inter_600SemiBold', color: colors.foreground },
    btnTextCancel:  { fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.mutedForeground },
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
            returnKeyType="done"
            onSubmitEditing={handleProtected}
          />

          {hasPassword ? (
            <Pressable style={s.btnPrimary} onPress={handleProtected}>
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

// ─── LogListScreen ─────────────────────────────────────────────────────────────

export default function LogListScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const topPad = Platform.OS === 'web' ? 67 : insets.top;
  const bottomPad = Platform.OS === 'web' ? 34 : insets.bottom;
  const { encounters, deleteEncounter, fs } = useApp();
  const { t } = useT();
  const { rowDir, backIcon } = useRTL();
  const [isExporting, setIsExporting] = useState(false);
  const [passwordModalVisible, setPasswordModalVisible] = useState(false);

  const navigateToNew = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    router.push('/new-log');
  };

  const handleExport = () => {
    if (encounters.length === 0) {
      Alert.alert(t('log.export_btn'), t('log.export_empty'));
      return;
    }
    if (isExporting) return;
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    setPasswordModalVisible(true);
  };

  const doExport = async (password: string | null) => {
    setPasswordModalVisible(false);
    setIsExporting(true);
    try {
      const html = buildEncounterHtml(encounters, t('log.export_title'));

      if (password) {
        // ── Encrypted path: AES-256-CBC + PBKDF2-SHA256 → self-decrypting HTML ──
        const encryptedPayload = aesEncryptStrong(html, password);
        const wrapperHtml = buildProtectedHtml(encryptedPayload, t('log.export_title'));

        const canShare = await Sharing.isAvailableAsync();
        if (canShare) {
          const fileUri = (FileSystem.cacheDirectory ?? '') + 'encounter-log-protected.html';
          await FileSystem.writeAsStringAsync(fileUri, wrapperHtml, {
            encoding: FileSystem.EncodingType.UTF8,
          });
          await Sharing.shareAsync(fileUri, {
            mimeType: 'text/html',
            dialogTitle: t('log.export_title'),
            UTI: 'public.html',
          });
        } else {
          // Web fallback: open as data URI in a new tab
          if (typeof window !== 'undefined') {
            const blob = new Blob([wrapperHtml], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            window.open(url, '_blank');
          }
        }
      } else {
        // ── Plain PDF path (original behaviour) ────────────────────────────────
        const { uri } = await Print.printToFileAsync({ html, base64: false });
        const canShare = await Sharing.isAvailableAsync();
        if (canShare) {
          await Sharing.shareAsync(uri, {
            mimeType: 'application/pdf',
            dialogTitle: t('log.export_title'),
            UTI: 'com.adobe.pdf',
          });
        } else {
          await Print.printAsync({ html });
        }
      }
    } catch {
      Alert.alert(t('log.export_btn'), t('log.export_error'));
    } finally {
      setIsExporting(false);
    }
  };

  const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: colors.background },
    header: {
      paddingTop: topPad + 12, paddingHorizontal: 20, paddingBottom: 16,
      borderBottomWidth: 1, borderBottomColor: colors.border,
      flexDirection: rowDir, alignItems: 'center', gap: 12,
    },
    headerLeft:   { flex: 1 },
    headerTitle:  { fontSize: fs(22), fontFamily: 'Inter_700Bold', color: colors.foreground },
    headerSub:    { fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 2 },
    addBtn:       { width: 40, height: 40, borderRadius: 20, backgroundColor: colors.primary, alignItems: 'center', justifyContent: 'center' },
    exportBtn:    { width: 40, height: 40, borderRadius: 20, backgroundColor: colors.muted, alignItems: 'center', justifyContent: 'center' },
    listContent:  { padding: 16, paddingBottom: bottomPad + 24 },
    countText:    { fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, paddingHorizontal: 16, paddingTop: 12, paddingBottom: 4 },
    emptyWrap:    { alignItems: 'center', justifyContent: 'center', paddingTop: 80, gap: 12 },
    emptyIcon:    { width: 72, height: 72, borderRadius: 36, backgroundColor: colors.muted, alignItems: 'center', justifyContent: 'center' },
    emptyTitle:   { fontSize: fs(17), fontFamily: 'Inter_600SemiBold', color: colors.foreground },
    emptyText:    { fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, textAlign: 'center', paddingHorizontal: 40, lineHeight: 20 },
    emptyBtn:     { backgroundColor: colors.primary, borderRadius: colors.radius, paddingVertical: 12, paddingHorizontal: 24, flexDirection: rowDir, alignItems: 'center', gap: 8 },
    emptyBtnText: { fontSize: fs(15), fontFamily: 'Inter_600SemiBold', color: colors.primaryForeground },
    privacyNote:  { flexDirection: rowDir, alignItems: 'center', gap: 8, backgroundColor: colors.muted, borderRadius: 10, padding: 10, marginHorizontal: 16, marginTop: 8 },
    privacyText:  { flex: 1, fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground },
  });

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} hitSlop={12}>
          <Feather name={backIcon} size={22} color={colors.foreground} />
        </Pressable>
        <View style={styles.headerLeft}>
          <Text style={styles.headerTitle}>{t('log.title')}</Text>
          <Text style={styles.headerSub}>{t('log.subtitle')}</Text>
        </View>
        {encounters.length > 0 && (
          <Pressable style={styles.exportBtn} onPress={handleExport} disabled={isExporting}>
            <Feather name="share" size={18} color={isExporting ? colors.mutedForeground : colors.foreground} />
          </Pressable>
        )}
        <Pressable style={styles.addBtn} onPress={navigateToNew}>
          <Feather name="plus" size={22} color="#FFFFFF" />
        </Pressable>
      </View>

      {encounters.length === 0 ? (
        <View style={styles.emptyWrap}>
          <View style={styles.emptyIcon}>
            <Feather name="clipboard" size={30} color={colors.mutedForeground} />
          </View>
          <Text style={styles.emptyTitle}>{t('log.empty_title')}</Text>
          <Text style={styles.emptyText}>{t('log.empty_desc')}</Text>
          <Pressable style={styles.emptyBtn} onPress={navigateToNew}>
            <Feather name="plus" size={16} color={colors.primaryForeground} />
            <Text style={styles.emptyBtnText}>{t('log.first_btn')}</Text>
          </Pressable>
        </View>
      ) : (
        <>
          <View style={styles.privacyNote}>
            <Feather name="lock" size={13} color={colors.mutedForeground} />
            <Text style={styles.privacyText}>
              {encounters.length} {encounters.length === 1 ? t('log.entry') : t('log.entries')} · {t('log.stored_device')}
            </Text>
          </View>
          <FlatList
            data={encounters}
            keyExtractor={(item) => item.id}
            contentContainerStyle={styles.listContent}
            renderItem={({ item }) => (
              <EncounterCard encounter={item} onDelete={() => deleteEncounter(item.id)} />
            )}
            showsVerticalScrollIndicator={false}
          />
        </>
      )}

      <PasswordModal
        visible={passwordModalVisible}
        onCancel={() => setPasswordModalVisible(false)}
        onShare={doExport}
      />
    </View>
  );
}
