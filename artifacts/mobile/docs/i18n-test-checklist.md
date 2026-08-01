# CivicShield Pro — Language Switching Test Checklist

Use this checklist to verify that switching languages in Settings correctly updates every screen.  
Test at minimum: **Spanish (es)**, **Chinese Simplified (zh-CN)**, and **Vietnamese (vi)**.

---

## How to switch language

1. Open the app → tap **⚙️** on the Home screen
2. Tap **App Language** → pick a language from the picker
3. Confirm the picker title itself appears in the current language before switching

---

## Screen-by-screen verification

### Home tab
- [ ] Tab bar label shows translated name (e.g. "Inicio" / "主页" / "Trang chủ")
- [ ] Tagline: "Know your rights. Stay protected." → translated
- [ ] "Tools & Resources" section heading → translated
- [ ] Feature card titles/descriptions → translated
- [ ] Emergency button label → translated
- [ ] Legal disclaimer → translated

### Docs tab (`/(tabs)/docs`)
- [ ] Tab bar label → translated
- [ ] Screen title: "Document Analyzer" → translated
- [ ] "Analyze" / "Guide" sub-tabs → translated
- [ ] Placeholder text in the input → translated
- [ ] "Scan Image" and "Sample" buttons → translated
- [ ] "Extract Deadlines & Dates" button → translated

### Translate tab (`/(tabs)/translate`)
- [ ] Tab bar label → translated
- [ ] Subtitle → translated
- [ ] Input placeholder → translated
- [ ] "Translate" button → translated
- [ ] "Clear" and "Auto-detect" controls → translated

### Rights tab (`/(tabs)/rights`)
- [ ] Tab bar label → translated
- [ ] Title: "Know Your Rights" → translated
- [ ] Quiz banner title/subtitle → translated
- [ ] "Next Question" / "See Results" / "Try Again" buttons → translated

### Resources tab (`/(tabs)/resources`)
- [ ] Tab bar label → translated
- [ ] "Crisis Hotlines" / "Legal Aid" / "📍 Near Me" sub-tabs → translated
- [ ] Search placeholder → translated
- [ ] "Use My Location" button → translated

### Community tab (`/(tabs)/community`)
- [ ] Tab bar label → translated
- [ ] Header "💬 Community" → translated
- [ ] "💬 Forum" / "📦 Resource Hub" sub-tabs → translated
- [ ] Search placeholder → translated
- [ ] New post form: "Category", "Title", "Details" labels → translated
- [ ] New post "Share" submit button → translated
- [ ] Anonymous note → translated
- [ ] "Call" button on resources → translated
- [ ] FREE / PAID badges → translated

### Settings screen
- [ ] All section headers → translated
- [ ] Language row description shows native name + English name
- [ ] "Small" / "Medium" / "Large" font size chips → translated
- [ ] High contrast toggle label → translated
- [ ] Clear data confirmation alert → translated

### Language Picker (modal)
- [ ] Title "Select Language" → translated
- [ ] Search placeholder "Search languages…" → translated

### Encounter Log (`/log-list`)
- [ ] Screen title → translated
- [ ] Subtitle → translated
- [ ] Empty state title + description → translated
- [ ] "Log First Encounter" button → translated
- [ ] Delete confirmation alert → translated
- [ ] Encounter type labels (Traffic Stop, Arrest, etc.) → translated

### New Encounter form (`/new-log`)
- [ ] Screen title → translated
- [ ] Type chips (Traffic Stop, Arrest, Questioning, etc.) → translated
- [ ] Section labels (Location, Officer Info, Description, Outcome) → translated
- [ ] "Save" button → translated
- [ ] Validation alert title "Required" → translated
- [ ] Legal note → translated

### Guided Tour (`/tour`)
- [ ] Step titles and descriptions → translated for all 7 steps
- [ ] Tip cards → translated
- [ ] "Skip" / "Next" / "Back" / "Get Started!" buttons → translated
- [ ] "Try It Now" button → translated

---

## Pass criteria

A language switch **passes** when:
- At least one key visible string on each tab is in the target language (not English)
- No screen shows a mix of translated and untranslated **UI labels** (user-entered content is allowed to stay in its original language)
- Switching back to English restores all original strings

## Known untranslated content (not UI labels — acceptable)

- Seed forum post titles and content (community data)
- Forum category labels (`FORUM_CATEGORIES` data)
- Resource names and descriptions (external data)
- Relative timestamps ("just now", "2h ago") in the forum
- QR screen developer notes
