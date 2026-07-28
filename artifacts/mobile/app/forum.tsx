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
import { router } from 'expo-router';
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
import { useApp } from '@/context/AppContext';
import { useColors } from '@/hooks/useColors';

// ── Helpers ───────────────────────────────────────────────────────────────────

function timeAgo(iso: string): string {
  const diff = (Date.now() - new Date(iso).getTime()) / 1000;
  if (diff < 60)   return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400)return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

function categoryMeta(cat: ForumCategory) {
  return FORUM_CATEGORIES.find((c) => c.value === cat)!;
}

// ── Post Card ─────────────────────────────────────────────────────────────────

function PostCard({
  post,
  onPress,
  onHelpful,
}: {
  post: ForumPost;
  onPress: () => void;
  onHelpful: () => void;
}) {
  const colors = useColors();
  const { fs } = useApp();
  const meta = categoryMeta(post.category);

  // Avoid nesting <Pressable> inside <Pressable> (causes web hydration warning).
  // The card body is tappable via its own Pressable; the footer actions are
  // separate Pressables rendered as siblings outside the card body Pressable.
  return (
    <View
      style={{
        backgroundColor: colors.card,
        borderRadius: colors.radius,
        borderWidth: 1,
        borderColor: colors.border,
        marginBottom: 10,
        overflow: 'hidden',
      }}
      accessibilityLabel={`Post: ${post.title}`}
    >
      {/* Tappable body — opens detail modal */}
      <Pressable
        onPress={onPress}
        style={({ pressed }) => ({ padding: 14, opacity: pressed ? 0.85 : 1 })}
        accessibilityRole="button"
        accessibilityLabel={`Open post: ${post.title}`}
      >
        {/* Category tag + time */}
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 8 }}>
          <View style={{ backgroundColor: meta.color + '18', borderRadius: 20, paddingHorizontal: 9, paddingVertical: 3, flexDirection: 'row', alignItems: 'center', gap: 4 }}>
            <Text style={{ fontSize: fs(12) }}>{meta.emoji}</Text>
            <Text style={{ fontSize: fs(11), fontFamily: 'Inter_600SemiBold', color: meta.color }}>{meta.label}</Text>
          </View>
          <Text style={{ fontSize: fs(11), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, marginLeft: 'auto' }}>
            {timeAgo(post.timestamp)}
          </Text>
        </View>
        {/* Title */}
        <Text style={{ fontSize: fs(15), fontFamily: 'Inter_600SemiBold', color: colors.foreground, marginBottom: 6, lineHeight: 21 }}>
          {post.title}
        </Text>
        {/* Preview */}
        <Text style={{ fontSize: fs(13), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 18 }} numberOfLines={2}>
          {post.content}
        </Text>
      </Pressable>

      {/* Footer — separate from the body Pressable to avoid nested buttons */}
      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 14, paddingHorizontal: 14, paddingBottom: 12 }}>
        <Pressable
          onPress={onHelpful}
          style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}
          accessibilityLabel={`Mark helpful. ${post.helpfulCount} found helpful`}
          accessibilityRole="button"
          hitSlop={6}
        >
          <Feather name="thumbs-up" size={14} color={post.markedHelpful ? meta.color : colors.mutedForeground} />
          <Text style={{ fontSize: fs(12), fontFamily: 'Inter_500Medium', color: post.markedHelpful ? meta.color : colors.mutedForeground }}>
            {post.helpfulCount} helpful
          </Text>
        </Pressable>
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}>
          <Feather name="message-circle" size={14} color={colors.mutedForeground} />
          <Text style={{ fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground }}>
            {post.replies.length} {post.replies.length === 1 ? 'reply' : 'replies'}
          </Text>
        </View>
        <Text style={{ marginLeft: 'auto', fontSize: fs(11), fontFamily: 'Inter_400Regular', color: colors.mutedForeground }}>
          {post.author}
        </Text>
      </View>
    </View>
  );
}

// ── Post Detail ───────────────────────────────────────────────────────────────

function PostDetail({
  post,
  onClose,
  onHelpful,
}: {
  post: ForumPost;
  onClose: () => void;
  onHelpful: () => void;
}) {
  const colors = useColors();
  const { fs } = useApp();
  const [replyText, setReplyText] = useState('');
  const meta = categoryMeta(post.category);

  const handleReply = () => {
    if (!replyText.trim()) return;
    Alert.alert('Reply Submitted', 'Your reply has been posted. (Replies are stored locally on this device.)');
    setReplyText('');
    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
  };

  return (
    <Modal visible animationType="slide" presentationStyle="pageSheet" onRequestClose={onClose}>
      <View style={{ flex: 1, backgroundColor: colors.background }}>
        {/* Header */}
        <View style={{ flexDirection: 'row', alignItems: 'center', padding: 16, borderBottomWidth: 1, borderBottomColor: colors.border, paddingTop: Platform.OS === 'ios' ? 50 : 20 }}>
          <Pressable onPress={onClose} hitSlop={12} style={{ marginRight: 12 }} accessibilityLabel="Close" accessibilityRole="button">
            <Feather name="x" size={22} color={colors.foreground} />
          </Pressable>
          <View
            style={{ backgroundColor: meta.color + '18', borderRadius: 20, paddingHorizontal: 10, paddingVertical: 4, flexDirection: 'row', alignItems: 'center', gap: 4 }}
          >
            <Text>{meta.emoji}</Text>
            <Text style={{ fontSize: fs(12), fontFamily: 'Inter_600SemiBold', color: meta.color }}>{meta.label}</Text>
          </View>
        </View>

        <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
          <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: 16, paddingBottom: 100, flexGrow: 1 }} keyboardShouldPersistTaps="handled">
            <Text style={{ fontSize: fs(20), fontFamily: 'Inter_700Bold', color: colors.foreground, lineHeight: 27, marginBottom: 8 }}>
              {post.title}
            </Text>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 14 }}>
              <Text style={{ fontSize: fs(12), fontFamily: 'Inter_400Regular', color: colors.mutedForeground }}>
                {post.author} · {timeAgo(post.timestamp)}
              </Text>
              <Pressable
                onPress={onHelpful}
                style={{ flexDirection: 'row', alignItems: 'center', gap: 4, marginLeft: 'auto' }}
                accessibilityRole="button"
                accessibilityLabel="Mark helpful"
              >
                <Feather name="thumbs-up" size={14} color={post.markedHelpful ? meta.color : colors.mutedForeground} />
                <Text style={{ fontSize: fs(12), fontFamily: 'Inter_500Medium', color: post.markedHelpful ? meta.color : colors.mutedForeground }}>
                  {post.helpfulCount}
                </Text>
              </Pressable>
            </View>

            <Text style={{ fontSize: fs(15), fontFamily: 'Inter_400Regular', color: colors.foreground, lineHeight: 23, marginBottom: 20 }}>
              {post.content}
            </Text>

            {/* Replies */}
            {post.replies.length > 0 && (
              <>
                <Text style={{ fontSize: fs(13), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase', letterSpacing: 0.7, marginBottom: 10 }}>
                  {post.replies.length} {post.replies.length === 1 ? 'Reply' : 'Replies'}
                </Text>
                {post.replies.map((r) => (
                  <View key={r.id} style={{ backgroundColor: colors.muted, borderRadius: 12, padding: 12, marginBottom: 8 }}>
                    <View style={{ flexDirection: 'row', marginBottom: 6 }}>
                      <Text style={{ fontSize: fs(13), fontFamily: 'Inter_600SemiBold', color: colors.foreground, flex: 1 }}>{r.author}</Text>
                      <Text style={{ fontSize: fs(11), fontFamily: 'Inter_400Regular', color: colors.mutedForeground }}>{timeAgo(r.timestamp)}</Text>
                    </View>
                    <Text style={{ fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.foreground, lineHeight: 20 }}>{r.content}</Text>
                    <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 8 }}>
                      <Feather name="thumbs-up" size={12} color={colors.mutedForeground} />
                      <Text style={{ fontSize: fs(11), fontFamily: 'Inter_400Regular', color: colors.mutedForeground }}>{r.helpfulCount} helpful</Text>
                    </View>
                  </View>
                ))}
              </>
            )}

            {/* Reply input */}
            <Text style={{ fontSize: fs(13), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase', letterSpacing: 0.7, marginTop: 12, marginBottom: 8 }}>
              Add a Reply
            </Text>
            <View style={{ backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1, borderColor: colors.border, marginBottom: 10, overflow: 'hidden' }}>
              <TextInput
                style={{ fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.foreground, padding: 12, minHeight: 90, textAlignVertical: 'top' }}
                value={replyText}
                onChangeText={setReplyText}
                multiline
                placeholder="Share information, advice, or support…"
                placeholderTextColor={colors.mutedForeground}
                accessibilityLabel="Reply text"
              />
            </View>
            <Pressable
              onPress={handleReply}
              style={[{ backgroundColor: meta.color, borderRadius: colors.radius, paddingVertical: 13, alignItems: 'center', marginBottom: 16 }, !replyText.trim() && { opacity: 0.5 }]}
              disabled={!replyText.trim()}
              accessibilityRole="button"
              accessibilityLabel="Post reply"
            >
              <Text style={{ fontSize: fs(15), fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' }}>Post Reply</Text>
            </Pressable>

            {/* Disclaimer */}
            <View style={{ backgroundColor: colors.muted, borderRadius: colors.radius, padding: 12 }}>
              <Text style={{ fontSize: fs(11), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 16 }}>
                {FORUM_DISCLAIMER}
              </Text>
            </View>
          </ScrollView>
        </KeyboardAvoidingView>
      </View>
    </Modal>
  );
}

// ── New Post Modal ────────────────────────────────────────────────────────────

function NewPostModal({
  visible,
  onClose,
  onSubmit,
}: {
  visible: boolean;
  onClose: () => void;
  onSubmit: (post: Omit<ForumPost, 'id' | 'helpfulCount' | 'markedHelpful' | 'isUserPost' | 'replies'>) => void;
}) {
  const colors = useColors();
  const { fs } = useApp();
  const [title, setTitle]     = useState('');
  const [content, setContent] = useState('');
  const [author, setAuthor]   = useState('Anonymous');
  const [category, setCategory] = useState<ForumCategory>('general');

  const handleSubmit = () => {
    if (!title.trim() || !content.trim()) {
      Alert.alert('Required', 'Please enter a title and description.');
      return;
    }
    onSubmit({ title: title.trim(), content: content.trim(), author: author.trim() || 'Anonymous', category, timestamp: new Date().toISOString() });
    setTitle(''); setContent(''); setAuthor('Anonymous'); setCategory('general');
    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    onClose();
  };

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet" onRequestClose={onClose}>
      <View style={{ flex: 1, backgroundColor: colors.background }}>
        <View style={{ flexDirection: 'row', alignItems: 'center', padding: 16, borderBottomWidth: 1, borderBottomColor: colors.border, paddingTop: Platform.OS === 'ios' ? 50 : 20 }}>
          <Pressable onPress={onClose} hitSlop={12} style={{ marginRight: 12 }} accessibilityRole="button" accessibilityLabel="Cancel">
            <Text style={{ fontSize: fs(15), fontFamily: 'Inter_500Medium', color: colors.mutedForeground }}>Cancel</Text>
          </Pressable>
          <Text style={{ flex: 1, fontSize: fs(17), fontFamily: 'Inter_700Bold', color: colors.foreground }}>New Post</Text>
          <Pressable onPress={handleSubmit} accessibilityRole="button" accessibilityLabel="Post">
            <Text style={{ fontSize: fs(15), fontFamily: 'Inter_600SemiBold', color: colors.primary }}>Post</Text>
          </Pressable>
        </View>

        <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
          <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: 16, gap: 12, flexGrow: 1 }} keyboardShouldPersistTaps="handled">
            {/* Category */}
            <Text style={{ fontSize: fs(12), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase', letterSpacing: 0.7, marginBottom: 4 }}>Category</Text>
            <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 4 }}>
              {FORUM_CATEGORIES.map((cat) => (
                <Pressable
                  key={cat.value}
                  onPress={() => setCategory(cat.value)}
                  style={{ backgroundColor: category === cat.value ? cat.color + '20' : colors.muted, borderRadius: 20, paddingHorizontal: 11, paddingVertical: 6, borderWidth: 1.5, borderColor: category === cat.value ? cat.color : 'transparent' }}
                  accessibilityRole="radio"
                  accessibilityState={{ selected: category === cat.value }}
                >
                  <Text style={{ fontSize: fs(13), fontFamily: 'Inter_500Medium', color: category === cat.value ? cat.color : colors.mutedForeground }}>
                    {cat.emoji} {cat.label}
                  </Text>
                </Pressable>
              ))}
            </View>

            {/* Title */}
            <Text style={{ fontSize: fs(12), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase', letterSpacing: 0.7, marginTop: 4 }}>Title</Text>
            <View style={{ backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1, borderColor: colors.border }}>
              <TextInput
                style={{ fontSize: fs(15), fontFamily: 'Inter_400Regular', color: colors.foreground, padding: 12 }}
                value={title}
                onChangeText={setTitle}
                placeholder="What's your question or experience?"
                placeholderTextColor={colors.mutedForeground}
                maxLength={120}
                accessibilityLabel="Post title"
              />
            </View>

            {/* Content */}
            <Text style={{ fontSize: fs(12), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase', letterSpacing: 0.7 }}>Details</Text>
            <View style={{ backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1, borderColor: colors.border }}>
              <TextInput
                style={{ fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.foreground, padding: 12, minHeight: 120, textAlignVertical: 'top' }}
                value={content}
                onChangeText={setContent}
                multiline
                placeholder="Share your experience, question, or advice…"
                placeholderTextColor={colors.mutedForeground}
                accessibilityLabel="Post content"
              />
            </View>

            {/* Author */}
            <Text style={{ fontSize: fs(12), fontFamily: 'Inter_600SemiBold', color: colors.mutedForeground, textTransform: 'uppercase', letterSpacing: 0.7 }}>Display Name</Text>
            <View style={{ backgroundColor: colors.card, borderRadius: colors.radius, borderWidth: 1, borderColor: colors.border }}>
              <TextInput
                style={{ fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.foreground, padding: 12 }}
                value={author}
                onChangeText={setAuthor}
                placeholder="Anonymous"
                placeholderTextColor={colors.mutedForeground}
                maxLength={40}
                accessibilityLabel="Display name"
              />
            </View>

            <View style={{ backgroundColor: colors.muted, borderRadius: colors.radius, padding: 12 }}>
              <Text style={{ fontSize: fs(11), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 16 }}>
                {FORUM_DISCLAIMER}
              </Text>
            </View>
          </ScrollView>
        </KeyboardAvoidingView>
      </View>
    </Modal>
  );
}

// ── Main Screen ───────────────────────────────────────────────────────────────

export default function ForumScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const { forumPosts, addForumPost, toggleForumHelpful, fs } = useApp();
  const topPad = Platform.OS === 'web' ? 20 : insets.top;

  const [filter, setFilter] = useState<ForumCategory | 'all'>('all');
  const [selectedPost, setSelectedPost] = useState<ForumPost | null>(null);
  const [showNewPost, setShowNewPost] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const allPosts = [...SEED_POSTS, ...forumPosts];
  const filtered = allPosts.filter((p) => {
    const matchCat = filter === 'all' || p.category === filter;
    const q = searchQuery.toLowerCase();
    const matchSearch = !q || p.title.toLowerCase().includes(q) || p.content.toLowerCase().includes(q);
    return matchCat && matchSearch;
  });

  // Sort: user posts first, then by helpful count
  const sorted = [...filtered].sort((a, b) => {
    if (a.isUserPost && !b.isUserPost) return -1;
    if (!a.isUserPost && b.isUserPost) return 1;
    return b.helpfulCount - a.helpfulCount;
  });

  const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: colors.background },
    header: { paddingTop: topPad + 12, paddingHorizontal: 20, paddingBottom: 0, borderBottomWidth: 1, borderBottomColor: colors.border },
    headerRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
    headerTitle: { flex: 1, fontSize: fs(22), fontFamily: 'Inter_700Bold', color: colors.foreground },
    newPostBtn: { flexDirection: 'row', alignItems: 'center', gap: 5, backgroundColor: colors.primary, borderRadius: 20, paddingHorizontal: 13, paddingVertical: 8 },
    newPostText: { fontSize: fs(13), fontFamily: 'Inter_600SemiBold', color: '#FFFFFF' },
    searchBar: { backgroundColor: colors.muted, borderRadius: 10, flexDirection: 'row', alignItems: 'center', paddingHorizontal: 12, marginBottom: 12, gap: 8 },
    searchInput: { flex: 1, fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.foreground, paddingVertical: 9 },
    filterRow: { flexDirection: 'row', paddingBottom: 0 },
    filterBtn: { paddingHorizontal: 14, paddingVertical: 10, marginRight: 4, borderBottomWidth: 2, borderBottomColor: 'transparent' },
    filterBtnActive: { borderBottomColor: colors.primary },
    filterText: { fontSize: fs(13), fontFamily: 'Inter_500Medium', color: colors.mutedForeground },
    filterTextActive: { color: colors.primary, fontFamily: 'Inter_600SemiBold' },
    scroll: { flex: 1 },
    scrollContent: { padding: 16, paddingBottom: Platform.OS === 'web' ? 80 : 110, flexGrow: 1 },
    disclaimer: { backgroundColor: colors.muted, borderRadius: colors.radius, padding: 12, marginTop: 8 },
    disclaimerText: { fontSize: fs(11), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, lineHeight: 16 },
    emptyState: { alignItems: 'center', paddingVertical: 40, gap: 10 },
    emptyText: { fontSize: fs(14), fontFamily: 'Inter_400Regular', color: colors.mutedForeground, textAlign: 'center' },
  });

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.headerRow}>
          <Pressable onPress={() => router.back()} hitSlop={10} style={{ marginRight: 10 }} accessibilityLabel="Back" accessibilityRole="button">
            <Feather name="arrow-left" size={22} color={colors.foreground} />
          </Pressable>
          <Text style={styles.headerTitle} accessibilityRole="header">💬 Community</Text>
          <Pressable style={styles.newPostBtn} onPress={() => setShowNewPost(true)} accessibilityRole="button" accessibilityLabel="New post">
            <Feather name="edit-3" size={14} color="#FFFFFF" />
            <Text style={styles.newPostText}>Post</Text>
          </Pressable>
        </View>

        {/* Search */}
        <View style={styles.searchBar}>
          <Feather name="search" size={15} color={colors.mutedForeground} />
          <TextInput
            style={styles.searchInput}
            value={searchQuery}
            onChangeText={setSearchQuery}
            placeholder="Search discussions…"
            placeholderTextColor={colors.mutedForeground}
            accessibilityLabel="Search forum"
          />
          {searchQuery.length > 0 && (
            <Pressable onPress={() => setSearchQuery('')} hitSlop={8}>
              <Feather name="x" size={14} color={colors.mutedForeground} />
            </Pressable>
          )}
        </View>

        {/* Category filter */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterRow}>
          <Pressable style={[styles.filterBtn, filter === 'all' && styles.filterBtnActive]} onPress={() => setFilter('all')} accessibilityRole="tab" accessibilityState={{ selected: filter === 'all' }}>
            <Text style={[styles.filterText, filter === 'all' && styles.filterTextActive]}>All</Text>
          </Pressable>
          {FORUM_CATEGORIES.map((cat) => (
            <Pressable
              key={cat.value}
              style={[styles.filterBtn, filter === cat.value && styles.filterBtnActive]}
              onPress={() => setFilter(cat.value)}
              accessibilityRole="tab"
              accessibilityState={{ selected: filter === cat.value }}
            >
              <Text style={[styles.filterText, filter === cat.value && styles.filterTextActive]}>
                {cat.emoji} {cat.label}
              </Text>
            </Pressable>
          ))}
        </ScrollView>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {sorted.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={{ fontSize: 36 }}>💬</Text>
            <Text style={styles.emptyText}>No posts yet in this category.{'\n'}Be the first to share!</Text>
            <Pressable style={[styles.newPostBtn, { marginTop: 8 }]} onPress={() => setShowNewPost(true)} accessibilityRole="button">
              <Text style={styles.newPostText}>Start a Discussion</Text>
            </Pressable>
          </View>
        ) : (
          sorted.map((post) => (
            <PostCard
              key={post.id}
              post={post}
              onPress={() => setSelectedPost(post)}
              onHelpful={() => { toggleForumHelpful(post.id); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); }}
            />
          ))
        )}

        <View style={styles.disclaimer}>
          <Text style={styles.disclaimerText}>{FORUM_DISCLAIMER}</Text>
        </View>
      </ScrollView>

      {selectedPost && (
        <PostDetail
          post={selectedPost}
          onClose={() => setSelectedPost(null)}
          onHelpful={() => { toggleForumHelpful(selectedPost.id); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); }}
        />
      )}

      <NewPostModal
        visible={showNewPost}
        onClose={() => setShowNewPost(false)}
        onSubmit={(data) => addForumPost(data)}
      />
    </View>
  );
}
