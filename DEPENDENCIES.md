"""
CivicShield Pro - Dependency Reference Guide

Complete breakdown of all production dependencies with explanations,
use cases, and integration points in the application.
"""

# ============================================================================
# CORE FRAMEWORK DEPENDENCY
# ============================================================================

"""
📦 STREAMLIT (1.28.1)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT IT DOES:
  Converts Python scripts into interactive web applications without needing
  HTML/CSS/JavaScript knowledge. Streamlit handles all the UI rendering and
  manages the web server.

WHY WE NEED IT:
  CivicShield needs a user-friendly web interface that works on any browser.
  Streamlit provides this automatically.

KEY FEATURES WE USE:
  1. Session State Management
     - Stores user selections across page navigations
     - Remembers selected language throughout app use
     - Maintains encounter log between sessions
     
     Code Example:
     st.session_state.selected_language = "Spanish"
     st.session_state.encounter_log = load_encounters()

  2. Multi-Page Routing
     - Different pages for different features
     - Page names stored in session state
     - Users navigate via sidebar buttons
     
     Code Example:
     if st.session_state.page == "Home":
         page_home()
     elif st.session_state.page == "RightsEducation":
         page_rights_education()

  3. Interactive Widgets
     - Button clicks trigger functions
     - Text inputs capture user text
     - Selectboxes allow option selection
     - Microphone widgets for audio
     - Audio widgets for playback
     
     Code Examples:
     st.button("Emergency Help")
     st.selectbox("Choose language", language_list)
     st.text_area("Enter officer statement")
     st.audio(audio_bytes, format="audio/mp3")

  4. Real-Time Updates
     - App reruns when user interacts
     - Variables update immediately
     - No page refresh needed
     
     Behind the scenes: Streamlit detects widget changes
     and reruns the entire script from top to bottom.

  5. Built-In Components
     - Alerts (st.error, st.warning, st.info, st.success)
     - Metrics (st.metric for statistics)
     - Tabs (st.tabs for grouped content)
     - Columns (st.columns for layout)
     - Expandable sections (st.expander)

  6. Markdown Support
     - Write content using Markdown syntax
     - HTML support for custom styling
     - Code block syntax highlighting

PERFORMANCE:
  - Fast initial load (2-3 seconds)
  - Quick reruns for user interactions (<500ms typically)
  - Lightweight for production deployment

INTEGRATION POINTS IN CIVICSHIELD:
  - Lines 1-100: Configuration (st.set_page_config)
  - Lines 85-150: Custom CSS styling
  - Throughout: All UI elements use st. functions
  - Lines 1800+: Navigation using st.button and session state
  - Page functions: Every feature uses Streamlit components

DOCUMENTATION:
  https://docs.streamlit.io
  https://docs.streamlit.io/develop/concepts/architecture
"""

# ============================================================================
# TRANSLATION DEPENDENCY
# ============================================================================

"""
📦 DEEP-TRANSLATOR (1.11.4)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT IT DOES:
  Provides a simple Python interface to Google Translate API. Handles all
  the complexity of calling Google's translation service. Supports 100+
  languages out of the box.

WHY WE NEED IT:
  CivicShield must support 14 languages. deep-translator makes this easy
  without needing complex API setup or authentication keys.

HOW IT WORKS:
  1. You specify source language (typically "en" for English)
  2. Specify target language (e.g., "es" for Spanish)
  3. Pass text to translate
  4. Get translated text back

KEY FEATURES WE USE:
  1. Multi-Language Support (14 languages)
     - English (en)
     - Spanish (es)
     - Vietnamese (vi)
     - Mandarin (zh-CN)
     - Cantonese (zh-TW)
     - Tagalog (tl)
     - Hindi (hi)
     - Korean (ko)
     - Japanese (ja)
     - Portuguese (pt)
     - Arabic (ar)
     - Telugu (te)
     - Tamil (ta)
     - Punjabi (pa)

  2. Simple API
     Code Example:
     from deep_translator import GoogleTranslator
     
     translator = GoogleTranslator(source='en', target='es')
     spanish_text = translator.translate("Hello")  # Returns: "Hola"

  3. No API Key Required
     - Works with free Google Translate API
     - No authentication needed
     - No quota setup required
     
  4. Fast Performance
     - Cached for repeated translations
     - Each translation takes 0.5-2 seconds
     - Supports batch translation

CACHING STRATEGY (Performance Optimization):
  We cache translator objects to reuse them:
  
  @st.cache_resource
  def get_translator(source_lang, target_lang):
      return GoogleTranslator(source=source_lang, target=target_lang)
  
  This avoids creating new translator objects for every translation.

INTEGRATION POINTS IN CIVICSHIELD:
  - Line 247-260: Translator caching function
  - Line 300-350: Getting UI strings (uses translation)
  - Line 1400+: Translating officer statements
  - Line 1450+: Translating legal advice
  - Throughout: Language-aware content display

LIMITATIONS:
  - Requires internet connection
  - Google's API has rate limiting (acceptable for this use case)
  - Some languages may have lower accuracy

ERROR HANDLING:
  - App handles translation failures gracefully
  - Falls back to English if translation fails
  - Shows error message to user but doesn't crash

DOCUMENTATION:
  https://github.com/nidhaloff/deep_translator
  https://deep-translator.readthedocs.io
"""

# ============================================================================
# TEXT-TO-SPEECH DEPENDENCY
# ============================================================================

"""
📦 GTTS - GOOGLE TEXT-TO-SPEECH (2.4.0)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT IT DOES:
  Converts text into natural-sounding speech audio files. Uses Google's
  text-to-speech service to generate MP3 audio that sounds like a human
  speaking.

WHY WE NEED IT:
  CivicShield must provide audio guidance for users in 14 languages.
  gTTS lets us generate this audio automatically.

HOW IT WORKS:
  1. Pass text and language code to gTTS
  2. It connects to Google's API
  3. API synthesizes speech from the text
  4. Returns MP3 audio file
  5. We save or play the audio

KEY FEATURES WE USE:
  1. Multi-Language Support
     - All 14 target languages fully supported
     - Natural-sounding voices per language
     - No gender selection needed for basic use

  2. Simple Audio Generation
     Code Example:
     from gtts import gTTS
     
     tts = gTTS(text="Your rights", lang='es')
     tts.save("audio.mp3")

  3. Flexible Output
     - Save to file: tts.save("file.mp3")
     - Get bytes: audio_fp = tts.write_to_fp(BytesIO())
     - Play directly: st.audio(audio_bytes)

  4. Speed Control
     - slow=False (normal speed) - what we use
     - slow=True (slower for clarity)

  5. No API Key Required
     - Free to use
     - No authentication needed
     - Reasonable rate limits

AUDIO QUALITY:
  - MP3 format (standard, works everywhere)
  - Natural-sounding voices
  - Clear pronunciation
  - Professional quality suitable for app

PERFORMANCE:
  - Audio generation: 2-5 seconds per clip
  - Depends on text length (longer = slower)
  - Network latency included in timing

INTEGRATION POINTS IN CIVICSHIELD:
  - Line 680+: Emergency notification audio
  - Line 1500+: Legal advice audio in target language
  - Line 1550+: Response audio in English
  - Audio playback section: Streamlit displays audio

USE CASES IN APP:
  1. Emergency Mode
     - Audio: "Officer, I am using a translation app..."
     - Alerts officer to app functionality

  2. Legal Advice Audio
     - Generates advice in user's selected language
     - User listens while reading text
     - Helps non-readers and double-checks text

  3. Response Coaching
     - Plays suggested response audio
     - User can practice pronunciation
     - Officer hears response in clear English

MARKDOWN CLEANUP:
  Before generating audio, we remove markdown symbols:
  text = text.replace("**", "").replace("###", "")
  
  This ensures audio sounds natural without reading symbols aloud.

LIMITATIONS:
  - Requires internet connection
  - Google's API has rate limiting
  - Some unusual text might not sound perfect
  - Each new text requires separate API call

ERROR HANDLING:
  - Try/except blocks catch API failures
  - Falls back to text display if audio fails
  - Shows user-friendly error message

DOCUMENTATION:
  https://github.com/pndurette/gTTS
  https://gtts.readthedocs.io
"""

# ============================================================================
# SPEECH-TO-TEXT DEPENDENCY
# ============================================================================

"""
📦 SPEECHRECOGNITION (3.10.0)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT IT DOES:
  Converts audio (from microphone or file) into text using Google's speech
  recognition API. Handles all the complexity of audio processing and API
  calls behind the scenes.

WHY WE NEED IT:
  Users record officer statements via microphone. We must convert this
  audio to text for translation and advice generation.

HOW IT WORKS:
  1. User records audio via microphone
  2. SpeechRecognition processes audio file
  3. Sends to Google Speech-to-Text API
  4. API returns recognized text
  5. App uses text for translation

KEY FEATURES WE USE:
  1. Google Speech Recognition
     Code Example:
     import speech_recognition as sr
     import io
     
     recognizer = sr.Recognizer()
     with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
         audio_data = recognizer.record(source)
         text = recognizer.recognize_google(audio_data, language="en-US")

  2. Multiple Audio Format Support
     - WAV (what we use from mic_recorder)
     - FLAC
     - AIFF
     - MP3 (with ffmpeg)
     - Supports any format librosa can read

  3. Language Specification
     - Specify input language (we use "en-US" for English)
     - Improves recognition accuracy
     - Critical for proper transcription

  4. Error Handling
     - Catches unrecognized speech
     - Network errors
     - API request errors
     - User-friendly exception messages

ACCURACY & PERFORMANCE:
  - Accuracy: 85-95% for clear English speech
  - Processing: 1-3 seconds for 30-second audio clip
  - Depends on: Audio quality, speaker clarity, background noise
  - Works best: Quiet environments, clear speech

HOW ACCURACY IS ACHIEVED:
  1. Audio preprocessing (noise reduction, normalization)
  2. Google's trained AI models recognize patterns
  3. Language model helps predict probable words
  4. Context helps disambiguate similar-sounding words

INTEGRATION POINTS IN CIVICSHIELD:
  - Line 1300+: Microphone audio processing
  - Lines 1310-1325: Audio recognition block
  - Error handling: Lines 1325-1335

AUDIO INPUT SOURCE:
  Audio comes from streamlit-mic-recorder (see below)
  - Records in WAV format
  - Returns bytes (binary audio data)
  - We wrap in BytesIO for SpeechRecognition

ERROR HANDLING IN APP:
  try:
      # Process audio
  except sr.UnknownValueError:
      st.warning("Could not understand audio. Please speak clearly.")
  except sr.RequestError as e:
      st.error(f"Speech recognition error: {e}")

LIMITATIONS:
  - Requires internet connection
  - Google API has rate limiting
  - Works best with clear speech
  - Background noise reduces accuracy
  - Heavy accents may reduce accuracy
  - Not suitable for fast-talking

WAYS TO IMPROVE ACCURACY:
  1. Record in quiet environment
  2. Speak clearly and at normal pace
  3. Avoid background noise
  4. Use quality microphone
  5. Keep microphone at consistent distance
  6. Use manual text input as fallback

ALTERNATIVES PROVIDED:
  - Manual text input (user types officer statement)
  - Fallback when speech recognition fails
  - Better for users with accessibility needs

DOCUMENTATION:
  https://github.com/Uberi/speech_recognition
  https://speech-recognition.readthedocs.io
"""

# ============================================================================
# MICROPHONE RECORDING DEPENDENCY
# ============================================================================

"""
📦 STREAMLIT-MIC-RECORDER (0.0.8)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT IT DOES:
  Provides a microphone recording button in the Streamlit interface. Uses
  browser's Web Audio API (WebRTC) to capture audio without needing any
  desktop software.

WHY WE NEED IT:
  Users must be able to record officer statements directly in the browser.
  This component provides the recording UI and captures audio.

HOW IT WORKS:
  1. User clicks "Record" button in browser
  2. Browser requests microphone permission
  3. User allows access (one-time dialog)
  4. Microphone captures audio while button is active
  5. User clicks "Stop Recording" button
  6. Component returns audio bytes as WAV file
  7. App passes to SpeechRecognition for transcription

KEY FEATURES WE USE:
  1. Browser-Based Recording (No Desktop App)
     - Works in any modern browser
     - No installation required
     - Security: User controls permissions
     - Audio never leaves user's machine during recording

  2. Simple UI Component
     Code Example:
     from streamlit_mic_recorder import mic_recorder
     
     audio_record = mic_recorder(
         start_prompt="🎤 Record",
         stop_prompt="⏹️ Stop",
         format="wav",
         key='recorder'
     )
     
     if audio_record:
         audio_bytes = audio_record['bytes']
         # Process audio...

  3. WAV Format Output
     - WAV is uncompressed, perfect for processing
     - Lower latency than MP3
     - Best format for speech recognition
     - SpeechRecognition expects WAV

  4. Custom Button Labels
     - Prompts for recording: "Record Officer's Voice"
     - Prompts for stopping: "Stop Recording & Translate"
     - Makes UI intuitive

BROWSER SUPPORT:
  - Chrome 90+ (best support)
  - Firefox 88+ (good support)
  - Safari 14+ (good support)
  - Edge 90+ (best support)
  - Mobile browsers (iOS 15+, Android)

MICROPHONE PERMISSIONS:
  - Browser shows permission dialog on first use
  - User clicks "Allow" to grant access
  - Browsers remember choice
  - Users can revoke in browser settings

INTEGRATION POINTS IN CIVICSHIELD:
  - Line 1290-1310: Microphone recording interface
  - Connected to SpeechRecognition for transcription
  - Alternative to manual text input

AUDIO QUALITY FACTORS:
  - Microphone quality (built-in vs headset)
  - Distance from mouth (ideal: 6-8 inches)
  - Background noise level
  - Environmental acoustics

BROWSER AUDIO API LIMITATIONS:
  - Requires HTTPS for production (HTTP works for localhost)
  - Audio stays in browser during recording
  - Audio sent to Google for transcription (privacy note)
  - Some corporate firewalls may block WebRTC

INTEGRATION WITH OTHER COMPONENTS:
  mic_recorder (audio capture)
       ↓
  SpeechRecognition (transcription)
       ↓
  GoogleTranslator (translation)
       ↓
  gTTS (audio generation)
       ↓
  st.audio (playback)

FALLBACK OPTION:
  If microphone fails or user prefers:
  - Manual text input available
  - Users type officer statement
  - Skips audio processing
  - Same translation and advice generated

ERROR HANDLING:
  - Permission denial: Show info message
  - Microphone unavailable: Suggest text input
  - Browser incompatibility: Use text fallback
  - Audio capture failure: Graceful error message

PRODUCTION CONSIDERATIONS:
  - Ensure HTTPS in production (browsers enforce this)
  - Test on target browsers and devices
  - Provide text input alternative
  - Document microphone permission requirements

DOCUMENTATION:
  https://github.com/stefanrmmr/streamlit-mic-recorder
  https://github.com/streamlit/community-cloud/issues
"""

# ============================================================================
# ENVIRONMENT MANAGEMENT DEPENDENCY
# ============================================================================

"""
📦 PYTHON-DOTENV (1.0.0)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT IT DOES:
  Loads environment variables from a .env file. Lets you store configuration
  and secrets outside of code.

WHY WE NEED IT:
  Best practice for production apps. If we add API keys or sensitive config
  later, we don't want to hardcode them in the script.

HOW IT WORKS:
  1. Create .env file with variables
  2. python-dotenv reads this file
  3. Variables loaded as environment variables
  4. Access via os.environ

KEY FEATURES:
  1. Simple .env File Format
     Example .env file:
     OPENAI_API_KEY=sk-xxxxxxxxxxxx
     DATABASE_URL=postgresql://...
     DEBUG=true

  2. Load Variables
     Code Example:
     from dotenv import load_dotenv
     import os
     
     load_dotenv()
     api_key = os.environ.get('OPENAI_API_KEY')

  3. Security
     - .env files never committed to git
     - Secrets stay out of source code
     - Different values per environment (dev/prod)

CURRENT USE IN CIVICSHIELD:
  - Not currently used (all free APIs, no keys needed)
  - Listed for future extensibility

FUTURE USE CASES:
  - OpenAI API for advanced legal analysis
  - Database connection strings
  - Email service credentials
  - Custom API keys
  - Deployment environment settings

ADDING TO CIVICSHIELD:
  If you need to use it later:
  
  1. Create .env file
  2. Add to .gitignore (so it's not committed)
  3. In code:
     from dotenv import load_dotenv
     import os
     load_dotenv()
     secret = os.environ.get('SECRET_NAME')

SECURITY BEST PRACTICES:
  - Never commit .env to git
  - Never share .env file
  - Use different credentials per environment
  - Rotate credentials periodically
  - Use version control for .env.example (without values)

DOCUMENTATION:
  https://github.com/theskumar/python-dotenv
  https://python-dotenv.readthedocs.io
"""

# ============================================================================
# DEPENDENCY INTERACTION DIAGRAM
# ============================================================================

"""
HOW DEPENDENCIES WORK TOGETHER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

USER INTERFACE LAYER
┌─────────────────────────────────────────────────────────┐
│  STREAMLIT                                              │
│  ├─ Renders buttons, text inputs, sidebars             │
│  ├─ Manages session state (language, page, etc)        │
│  ├─ Displays alerts and metrics                        │
│  └─ Plays audio files                                  │
└─────────────────────────────────────────────────────────┘

AUDIO INPUT LAYER
┌─────────────────────────────────────────────────────────┐
│  STREAMLIT-MIC-RECORDER                                 │
│  └─ Captures audio from user's microphone              │
│                            ↓                            │
│  SPEECHRECOGNITION                                      │
│  └─ Transcribes audio to text (English)                │
└─────────────────────────────────────────────────────────┘

TRANSLATION LAYER
┌─────────────────────────────────────────────────────────┐
│  DEEP-TRANSLATOR                                        │
│  ├─ Translates officer statement to user's language    │
│  ├─ Translates legal advice to user's language         │
│  └─ Translates UI strings to user's language           │
└─────────────────────────────────────────────────────────┘

AUDIO OUTPUT LAYER
┌─────────────────────────────────────────────────────────┐
│  GTTS                                                   │
│  ├─ Generates speech audio from translated advice      │
│  ├─ Generates speech audio from responses              │
│  └─ Generates speech audio for emergency alerts        │
└─────────────────────────────────────────────────────────┘

CONFIGURATION LAYER
┌─────────────────────────────────────────────────────────┐
│  PYTHON-DOTENV (Optional, for future extensions)       │
│  └─ Manages environment variables and secrets          │
└─────────────────────────────────────────────────────────┘

COMPLETE WORKFLOW EXAMPLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. User selects "Spanish" → STREAMLIT stores in session_state

2. User records officer saying "step out of the car"
   → STREAMLIT-MIC-RECORDER captures audio

3. App processes audio
   → SPEECHRECOGNITION converts to English text

4. Text "step out of the car" needs translation and advice
   → DEEP-TRANSLATOR translates to Spanish
   → Gets legal advice about traffic stops
   → Translates advice to Spanish

5. App generates audio guidance
   → GTTS creates MP3 of advice in Spanish
   → GTTS creates MP3 of response in English

6. Display to user
   → STREAMLIT shows translated text
   → STREAMLIT plays audio files
   → Shows keyboard navigation options

7. User can log encounter
   → STREAMLIT stores in JSON
   → Data persists between sessions

All 6 dependencies work together seamlessly!
"""

# ============================================================================
# VERSION PINNING STRATEGY
# ============================================================================

"""
WHY WE PIN VERSIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Problem: If we don't specify versions, installing packages at different
times might install different versions. This causes:
- Breaking changes
- Features disappearing
- Tests failing
- Unpredictable behavior

Solution: Pin to specific versions we tested

VERSION SCHEME: X.Y.Z (semantic versioning)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

X = Major version (breaking changes)
Y = Minor version (new features, backward compatible)
Z = Patch version (bug fixes, backward compatible)

Example: 1.28.1
- Major: 1 (Streamlit 1.x branch)
- Minor: 28 (28th minor release)
- Patch: 1 (first patch for v1.28)

OUR PINNING STRATEGY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

streamlit==1.28.1          Fixed: Specific version
deep-translator==1.11.4    Fixed: Tested with this version
gTTS==2.4.0                Fixed: Stable version
SpeechRecognition==3.10.0  Fixed: Latest stable
streamlit-mic-recorder==0.0.8  Fixed: Only 0.0.8 works with current Streamlit
python-dotenv==1.0.0       Fixed: Stable version

WHEN TO UPDATE VERSIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Good reasons to update:
  - Security vulnerabilities found
  - Critical bug fixes available
  - New features needed for app
  - Old version no longer supported

❌ Don't update just because new version exists:
  - Test thoroughly after any update
  - Check for breaking changes
  - May introduce bugs or incompatibilities

HOW TO UPDATE SAFELY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Update one package at a time
2. Test app thoroughly after update
3. Check release notes for breaking changes
4. Update requirements.txt with new version
5. Commit changes with testing notes

CHECKING FOR UPDATES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

pip list --outdated     # Shows packages with updates available

pip check              # Shows dependency conflicts
"""

# ============================================================================
# INSTALLATION TROUBLESHOOTING
# ============================================================================

"""
COMMON INSTALLATION ISSUES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Issue: "ModuleNotFoundError: No module named 'streamlit'"

Cause: Packages not installed in active virtual environment

Solution:
  1. Verify virtual environment is active
  2. Reinstall requirements: pip install -r requirements.txt
  3. Check pip location: where pip (Windows) or which pip (Mac/Linux)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Issue: "Requirement already satisfied" but package still not working

Cause: Different Python version or wrong environment

Solution:
  1. Check Python version: python --version
  2. Verify pip matches Python: python -m pip --version
  3. Clear cache: pip install --no-cache-dir -r requirements.txt

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Issue: "ERROR: Could not find a version that satisfies"

Cause: Version incompatibility or package unavailable

Solution:
  1. Update pip: pip install --upgrade pip
  2. Update setuptools: pip install --upgrade setuptools
  3. Try installing without version pins: pip install streamlit
  4. Check internet connection

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Issue: Microphone not working in browser

Cause: Browser permission or WebRTC issue

Solution:
  1. Check browser console (F12) for errors
  2. Verify microphone in browser settings
  3. Try different browser
  4. Use manual text input as fallback

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Issue: Translation API errors

Cause: Internet connection or API rate limiting

Solution:
  1. Check internet connection
  2. Try translating again (may be temporary)
  3. Use manual translation as fallback
  4. Check deep-translator GitHub issues

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Issue: Speech recognition not working

Cause: Audio quality, privacy settings, or API issue

Solution:
  1. Test microphone with system audio settings
  2. Try speaking clearly near microphone
  3. Use manual text input instead
  4. Check internet connection
  5. Try different audio file format

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Getting Help:
  - Check requirements.txt comments for each package
  - Read SETUP_GUIDE.md for detailed installation steps
  - Check package documentation URLs
  - Search for error messages on Stack Overflow
  - Create GitHub issue with full error traceback
"""

# ============================================================================
# PRODUCTION DEPLOYMENT NOTES
# ============================================================================

"""
DEPLOYMENT CONSIDERATIONS FOR EACH DEPENDENCY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STREAMLIT:
  ✓ Built-in security with Streamlit Cloud
  ✓ Handles HTTPS automatically
  ✓ Can be deployed with just GitHub repo
  ✗ May have rate limiting on free tier
  ⚠ Use environment secrets for sensitive data

DEEP-TRANSLATOR:
  ✓ No auth needed (uses free Google API)
  ✓ Good for production without setup
  ✗ Has rate limits (~100 req/min typically)
  ✗ Requires internet connection always
  ⚠ Monitor API changes from Google

GTTS:
  ✓ Free and reliable for production
  ✓ No auth/setup required
  ✗ Has rate limiting
  ✗ Requires internet connection
  ⚠ Consider caching generated audio files

SPEECHRECOGNITION:
  ✓ Easy to implement
  ✗ Requires internet (uses Google API)
  ✗ Rate limited
  ✗ May timeout on poor connections
  ⚠ Provide text input fallback

STREAMLIT-MIC-RECORDER:
  ✓ Works in browser (no server changes)
  ✓ No authentication needed
  ✗ Requires HTTPS in production
  ✗ Some corporate firewalls block WebRTC
  ⚠ Test in target network environment

PYTHON-DOTENV:
  ✓ Essential for secure production
  ✓ Zero overhead
  ✗ Only for development (Streamlit Cloud uses secrets)
  ⚠ Use Streamlit Cloud "Secrets" for deployments

PRODUCTION CHECKLIST:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

☐ All dependencies pinned to tested versions
☐ requirements.txt committed to git
☐ Tested app on deployment platform
☐ Error handling for all API calls
☐ Fallback options for audio features
☐ Environment variables/secrets configured
☐ Rate limiting handled gracefully
☐ HTTPS enabled (for microphone)
☐ Tested on target browsers
☐ Performance optimized (caching)
☐ Incident monitoring in place
☐ Documentation up to date
"""
