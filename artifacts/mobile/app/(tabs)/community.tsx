/**
 * Community tab — peer forum for sharing experiences and asking questions.
 * The Resource Hub lives in its own dedicated Hub tab.
 */
import React, { useState } from 'react';
import {
  Alert,
  KeyboardAvoidingView,
  Modal,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { Feather } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import {
  FORUM_CATEGORIES,
  FORUM_DISCLAIMER,
  ForumCategory,
  ForumPost,
  SEED_POSTS,
} from '@/constants/forum-data';
import { I18nKey } from '@/constants/i18n';
import { useApp } from '@/context/AppContext';
import { useColors } from '@/hooks/useColors';
import { useRTL } from '@/hooks/useRTL';
import { useT } from '@/hooks/useTranslation';

// ── helpers ──────────────────────────────────────────────────────────────────

function timeAgo(iso: string, t: (key: I18nKey) => string): string {
  const diff = (Date.now() - new Date(iso).getTime()) / 1000;
  if (diff < 60)    return t('community.time_just_now');
  if (diff < 3600)  return t('community.time_m_ago').replace('{n}', String(Math.floor(diff / 60)));
  if (diff < 86400) return t('community.time_h_ago').replace('{n}', String(Math.floor(diff / 3600)));
  return t('community.time_d_ago').replace('{n}', String(Math.floor(diff / 86400)));
}

function catMeta(cat: ForumCategory) {
  return FORUM_CATEGORIES.find((c) => c.value === cat)!;
}

// ── Forum ─────────────────────────────────────────────────────────────────────

function ForumTab() {
  const colors   = useColors();
  const { t } = useT();
  const { rowDir, textStyle } = useRTL();
  const { fs, forumPosts, addForumPost, toggleForumHelpful, helpfulIds } = useApp() as any;
  const allPosts = [...forumPosts.filter((p: ForumPost) => p.isUserPost), ...SEED_POSTS];

  const [search, setSearch]           = useState('');
  const [catFilter, setCatFilter]     = useState<ForumCategory | 'all'>('all');
  const [detailPost, setDetailPost]   = useState<ForumPost | null>(null);
  const [showNew, setShowNew]         = useState(false);
  const [newTitle, setNewTitle]       = useState('');
  const [newBody, setNewBody]         = useState('');
  const [newCat, setNewCat]           = useState<ForumCategory>('general');
  const [submitting, setSubmitting]   = useState(false);

  const filtered = allPosts.filter((p: ForumPost) => {
    const matchCat = catFilter === 'all' || p.category === catFilter;
    const q = search.toLowerCase();
    const matchQ = !q || p.title.toLowerCase().includes(q) || p.content.toLowerCase().includes(q);
    return matchCat && matchQ;
  });

  const submitPost = async () => {
    if (!newTitle.trim() || !newBody.trim()) {
      Alert.alert(t('community.missing_fields_title'), t('community.missing_fields_msg'));
      return;
    }
    setSubmitting(true);
    await addForumPost({
      title: newTitle.trim(),
      body: newBody.trim(),
      category: newCat,
      author: 'Anonymous',
      timestamp: new Date().toISOString(),
      replies: [],
    });
    setNewTitle(''); setNewBody(''); setNewCat('general');
    setSubmitting(false);
    setShowNew(false);
    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
  };

  return (
    <>
      {/* Search */}
      <View style={{ flexDirection: rowDir, alignItems: 'center', backgroundColor: colors.muted, borderRadius: 12, marginBottom: 10, paddingHorizontal: 12, height: 42, gap: 8, borderWidth: 1, borderColor: colors.border }}>
        <Feather name="search" size={15} color={colors.mutedForeground} />
        <TextInput
          style={[{ flex: 1, fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.foreground }, textStyle]}
          value={search}
          onChangeText={setSearch}
          placeholder={t('community.search_forum')}
          placeholderTextColor={colors.mutedForeground}
        />
        {search.length > 0 && (
          <Pressable onPress={() => setSearch('')} hitSlop={8}>
            <Feather name="x" size={14} color={colors.mutedForeground} />
          </Pressable>
        )}
      </View>

      {/* Category chips */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 10 }}>
        <View style={{ flexDirection: rowDir, gap: 6, paddingRight: 8 }}>
          {[{ value: 'all' as const, label: t('hub.filter_all'), labelKey: '', emoji: '📋' }, ...FORUM_CATEGORIES].map((c) => {
            const active = catFilter === c.value;
            const displayLabel = c.labelKey ? t(c.labelKey as I18nKey) : c.label;
            return (
              <Pressable
                key={c.value}
                onPress={() => { setCatFilter(c.value as ForumCategory | 'all'); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); }}
                style={{ flexDirection: rowDir, alignItems: 'center', gap: 4, paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20, borderWidth: 1.5, borderColor: active ? colors.primary : colors.border, backgroundColor: active ? colors.primary + '14' : colors.muted }}
              >
                <Text style={{ fontSize: fs(11) }}>{c.emoji}</Text>
                <Text style={{ fontSize: fs(12), fontFamily: active ? 'Inter_600SemiBold' : 'Inter_400Regular', color: active ? colors.primary : colors.mutedForeground }}>
                  {displayLabel}
                </Text>
              </Pressable>
            );
          })}
        </View>
      </ScrollView>

      {/* Post cards */}
      {filtered.map((p: ForumPost) => {
        const meta    = catMeta(p.category);
        const helpful = helpfulIds?.has(p.id) ?? p.markedHelpful;
        return (
          <View key={p.id} style={{ backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1, borderColor: colors.border, marginBottom: 10, overflow: 'hidden' }}>
            <Pressable onPress={() => setDetailPost(p)} style={{ padding: 14 }}>
              <View style={{ flexDirection: rowDir, alignItems: 'center', gap: 8, marginBottom: 6 }}>
                <View style={{ backgroundColor: meta.color + '18', borderRadius: 20, paddingHorizontal: 8, paddingVertical: 3, flexDirection: rowDir, alignItems: 'center', gap: 4 }}>
                  <Text style={{ fontSize: 11 }}>{meta.emoji}</Text>
                  <Text style={{ fontSize: fs(11), fontFamily: 'Inter_600SemiBold', color: meta.color }}>{t(meta.labelKey as I18nKey)}</Text>
                </View>
                <Text style={{ fontSize: fs(11), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginLeft: 'auto' }}>{timeAgo(p.timestamp, t)}</Text>
              </View>
              <Text style={{ fontSize: fs(15), fontFamily: 'Inter_600SemiBold', color: colors.foreground, lineHeight: 21, marginBottom: 4 }}>{p.title}</Text>
              <Text style={{ fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 19 }} numberOfLines={2}>{p.content}</Text>
            </Pressable>
            <View style={{ flexDirection: rowDir, alignItems: 'center', paddingHorizontal: 14, paddingBottom: 12, gap: 16 }}>
              <Pressable
                onPress={() => { toggleForumHelpful?.(p.id); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); }}
                style={{ flexDirection: rowDir, alignItems: 'center', gap: 5 }}
              >
                <Feather name="thumbs-up" size={14} color={helpful ? colors.primary : colors.mutedForeground} />
                <Text style={{ fontSize: fs(12), fontFamily: 'Inter_500Medium', color: helpful ? colors.primary : colors.mutedForeground }}>
                  {p.helpfulCount + (helpful && !p.markedHelpful ? 1 : 0)} 👍
                </Text>
              </Pressable>
              <Pressable onPress={() => setDetailPost(p)} style={{ flexDirection: rowDir, alignItems: 'center', gap: 5 }}>
                <Feather name="message-circle" size={14} color={colors.mutedForeground} />
                <Text style={{ fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground }}>
                  {p.replies.length} {p.replies.length === 1 ? t('forum.reply') : t('forum.replies')}
                </Text>
              </Pressable>
              <Text style={{ fontSize: fs(11), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginLeft: 'auto' }}>{p.author}</Text>
            </View>
          </View>
        );
      })}

      {filtered.length === 0 && (
        <View style={{ padding: 24, alignItems: 'center' }}>
          <Text style={{ fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, textAlign: 'center' }}>{t('community.no_posts')}</Text>
        </View>
      )}

      <View style={{ backgroundColor: colors.muted, borderRadius: colors.radius, padding: 12, marginTop: 4 }}>
        <Text style={{ fontSize: fs(11), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 17 }}>{FORUM_DISCLAIMER}</Text>
      </View>

      {/* Post Detail Modal */}
      {detailPost && (
        <Modal visible animationType="slide" presentationStyle="pageSheet" onRequestClose={() => setDetailPost(null)}>
          <DetailView post={detailPost} onClose={() => setDetailPost(null)} />
        </Modal>
      )}

      {/* New Post Modal */}
      <Modal visible={showNew} animationType="slide" presentationStyle="pageSheet" onRequestClose={() => setShowNew(false)}>
        <NewPostView
          title={newTitle} setTitle={setNewTitle}
          body={newBody} setBody={setNewBody}
          cat={newCat} setCat={setNewCat}
          submitting={submitting}
          onSubmit={submitPost}
          onClose={() => setShowNew(false)}
        />
      </Modal>

      {/* FAB */}
      <Pressable
        onPress={() => setShowNew(true)}
        style={{ position: 'absolute', bottom: 16, right: 0, backgroundColor: colors.primary, borderRadius: 24, paddingHorizontal: 18, paddingVertical: 12, flexDirection: rowDir, alignItems: 'center', gap: 6, elevation: 4 }}
        accessibilityRole="button"
        accessibilityLabel="Create new post"
      >
        <Feather name="edit-2" size={15} color="#FFFFFF" />
        <Text style={{ fontSize: 14, fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' }}>{t('community.post_btn')}</Text>
      </Pressable>
    </>
  );
}

// ── Post Detail ───────────────────────────────────────────────────────────────

function DetailView({ post, onClose }: { post: ForumPost; onClose: () => void }) {
  const colors = useColors();
  const { fs } = useApp();
  const { t } = useT();
  const { rowDir, textStyle } = useRTL();
  const meta = catMeta(post.category);
  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <View style={{ flexDirection: rowDir, alignItems: 'center', padding: 16, borderBottomWidth: 1, borderBottomColor: colors.border, paddingTop: Platform.OS === 'ios' ? 50 : 20 }}>
        <Pressable onPress={onClose} hitSlop={12} style={{ marginRight: 12 }} accessibilityRole="button" accessibilityLabel="Close">
          <Feather name="x" size={22} color={colors.foreground} />
        </Pressable>
        <View style={{ backgroundColor: meta.color + '18', borderRadius: 20, paddingHorizontal: 10, paddingVertical: 4, flexDirection: rowDir, alignItems: 'center', gap: 4 }}>
          <Text>{meta.emoji}</Text>
          <Text style={{ fontSize: fs(12), fontFamily: 'Inter_600SemiBold', color: meta.color }}>{t(meta.labelKey as I18nKey)}</Text>
        </View>
      </View>
      <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: 16, paddingBottom: 60, flexGrow: 1 }}>
        <Text style={{ fontSize: fs(20), fontFamily: 'Inter_700Bold', color: colors.foreground, lineHeight: 27, marginBottom: 8 }}>{post.title}</Text>
        <Text style={{ fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginBottom: 16 }}>{post.author} · {timeAgo(post.timestamp, t)}</Text>
        <Text style={[{ fontSize: fs(15), fontFamily: 'Inter_400Regular', color: colors.foreground, lineHeight: 23, marginBottom: 20 }, textStyle]}>{post.content}</Text>
        {post.replies.map((r, i) => (
          <View key={i} style={{ backgroundColor: colors.muted, borderRadius: 10, padding: 12, marginBottom: 10, borderWidth: 1, borderColor: colors.border }}>
            <View style={{ flexDirection: rowDir, alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <Text style={{ fontSize: fs(13), fontFamily: 'Inter_600SemiBold', color: colors.foreground }}>{r.author}</Text>
              <Text style={{ fontSize: fs(11), fontFamily: 'Inter_400Regular', color: colors.mutedForeground }}>{timeAgo(r.timestamp, t)}</Text>
            </View>
            <Text style={{ fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.foreground, lineHeight: 20 }}>{r.content}</Text>
          </View>
        ))}
      </ScrollView>
    </View>
  );
}

// ── New Post ──────────────────────────────────────────────────────────────────

function NewPostView({ title, setTitle, body, setBody, cat, setCat, submitting, onSubmit, onClose }: any) {
  const colors = useColors();
  const { t } = useT();
  const { fs } = useApp();
  const { rowDir, textStyle } = useRTL();
  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <View style={{ flexDirection: rowDir, alignItems: 'center', padding: 16, borderBottomWidth: 1, borderBottomColor: colors.border, paddingTop: Platform.OS === 'ios' ? 50 : 20 }}>
        <Pressable onPress={onClose} hitSlop={12} style={{ marginRight: 12 }}><Feather name="x" size={22} color={colors.foreground} /></Pressable>
        <Text style={{ flex: 1, fontSize: fs(17), fontFamily: 'Inter_700Bold', color: colors.foreground }}>{t('community.new_post')}</Text>
        <Pressable onPress={onSubmit} disabled={submitting} style={{ backgroundColor: colors.primary, borderRadius: 20, paddingHorizontal: 16, paddingVertical: 7, opacity: submitting ? 0.6 : 1 }}>
          <Text style={{ fontSize: fs(14), fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' }}>{t('community.share')}</Text>
        </Pressable>
      </View>
      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: 16, gap: 12, flexGrow: 1 }} keyboardShouldPersistTaps="handled">
          <Text style={{ fontSize: fs(12), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase' }}>{t('forum.category_label')}</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            <View style={{ flexDirection: rowDir, gap: 6 }}>
              {FORUM_CATEGORIES.map((c) => (
                <Pressable key={c.value} onPress={() => setCat(c.value)} style={{ flexDirection: rowDir, alignItems: 'center', gap: 4, paddingHorizontal: 12, paddingVertical: 7, borderRadius: 20, borderWidth: 1.5, borderColor: cat === c.value ? colors.primary : colors.border, backgroundColor: cat === c.value ? colors.primary + '14' : colors.muted }}>
                  <Text style={{ fontSize: 12 }}>{c.emoji}</Text>
                  <Text style={{ fontSize: fs(12), fontFamily: cat === c.value ? 'Inter_600SemiBold' : 'Inter_400Regular', color: cat === c.value ? colors.primary : colors.mutedForeground }}>{t(c.labelKey as I18nKey)}</Text>
                </Pressable>
              ))}
            </View>
          </ScrollView>
          <Text style={{ fontSize: fs(12), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase' }}>{t('forum.title_label')} *</Text>
          <TextInput style={[{ backgroundColor: colors.muted, borderRadius: 10, padding: 12, fontSize: fs(15), fontFamily: 'Inter_400Regular', color: colors.foreground, borderWidth: 1, borderColor: colors.border }, textStyle]} value={title} onChangeText={setTitle} placeholder={t('forum.title_ph')} placeholderTextColor={colors.mutedForeground} />
          <Text style={{ fontSize: fs(12), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase' }}>{t('forum.details_label')} *</Text>
          <TextInput style={[{ backgroundColor: colors.muted, borderRadius: 10, padding: 12, fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.foreground, minHeight: 140, textAlignVertical: 'top', borderWidth: 1, borderColor: colors.border }, textStyle]} value={body} onChangeText={setBody} placeholder={t('forum.details_ph')} placeholderTextColor={colors.mutedForeground} multiline />
          <View style={{ backgroundColor: colors.primary + '10', borderRadius: 10, padding: 12, flexDirection: rowDir, gap: 8 }}>
            <Feather name="lock" size={14} color={colors.primary} />
            <Text style={{ flex: 1, fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 18 }}>{t('community.anon_note')}</Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </View>
  );
}

// ── Main Screen ───────────────────────────────────────────────────────────────

export default function CommunityScreen() {
  const colors  = useColors();
  const insets  = useSafeAreaInsets();
  const { t }   = useT();
  const { fs }  = useApp();
  const topPad  = Platform.OS === 'web' ? 67 : insets.top;

  const styles = StyleSheet.create({
    container:     { flex: 1, backgroundColor: colors.background },
    header:        { paddingTop: topPad + 12, paddingHorizontal: 20, paddingBottom: 14, borderBottomWidth: 1, borderBottomColor: colors.border },
    headerTitle:   { fontSize: fs(22), fontFamily: 'Inter_700Bold', color: colors.foreground },
    headerSub:     { fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginTop: 2 },
    scroll:        { flex: 1 },
    scrollContent: { padding: 16, paddingBottom: Platform.OS === 'web' ? 80 : 110, flexGrow: 1 },
  });

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle} accessibilityRole="header">{t('community.title')}</Text>
        <Text style={styles.headerSub}>{t('community.subtitle')}</Text>
      </View>

      {/* Forum */}
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        <ForumTab />
      </ScrollView>
    </View>
  );
}
