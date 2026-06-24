"""
CivicShield - Professional Rights Translation & Emergency Response App
Production-Ready Implementation with Multi-Language Support

CORE FEATURES:
- Real-time speech-to-text translation (14 languages)
- Rights education center with California legal information
- Encounter logging with persistent storage
- Community resources directory
- Emergency assistance guide
- Professional sidebar navigation
- Streamlit session state management
- Audio playback for users and officers
- Clean, accessible professional UI

AUTHOR: Community Justice Initiative
VERSION: 2.0.0
"""

import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
import json
import os
from datetime import datetime
import io

# ============================================================================
# DEPENDENCY DOCUMENTATION
# ============================================================================
"""
PRODUCTION DEPENDENCIES:
1. streamlit==1.28.0+
   - Web app framework for Python
   - Session state management
   - Multi-page app routing
   - UI components (buttons, text inputs, etc.)

2. deep_translator==1.11.0+
   - Google Translate API wrapper
   - 14+ language translation support
   - Lightweight, no API key required for basic use

3. gtts==2.4.0+
   - Google Text-to-Speech synthesis
   - Generates natural-sounding audio
   - Supports all 14 target languages

4. streamlit-mic-recorder==0.0.8+
   - Browser-based microphone recording
   - WAV format audio capture
   - Real-time recording UI

5. SpeechRecognition==3.10.0+
   - Google Speech-to-Text recognition
   - Audio processing and transcription
   - Works with WAV/MP3 files

INSTALLATION:
pip install streamlit==1.28.0 deep_translator==1.11.0 gtts==2.4.0 streamlit-mic-recorder==0.0.8 SpeechRecognition==3.10.0
"""

# ============================================================================
# PAGE CONFIGURATION & THEMING
# ============================================================================
st.set_page_config(
    page_title="CivicShield Pro",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional appearance
st.markdown("""
<style>
    /* Main content styling */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1e3a5f;
    }
    
    [data-testid="stSidebar"] > div > div > div > div > h1 {
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    
    /* Alert styling */
    .stAlert {
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Metric cards */
    .metric-card {
        background-color: white;
        border-radius: 8px;
        padding: 1.5rem;
        border-left: 4px solid #d62828;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* Headers */
    h1 {
        color: #1e3a5f;
        border-bottom: 3px solid #d62828;
        padding-bottom: 0.5rem;
    }
    
    h2 {
        color: #1e3a5f;
        margin-top: 1.5rem;
    }
    
    /* Right container styling */
    .right-container {
        background-color: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LANGUAGE CONFIGURATION
# ============================================================================
LANGUAGE_MAP = {
    "English": {"code": "en", "native": "English"},
    "Spanish / Español": {"code": "es", "native": "Spanish"},
    "Cantonese / 粵語": {"code": "zh-TW", "native": "Cantonese"},
    "Vietnamese / Tiếng Việt": {"code": "vi", "native": "Vietnamese"},
    "Mandarin / 普通話": {"code": "zh-CN", "native": "Mandarin"},
    "Tagalog": {"code": "tl", "native": "Tagalog"},
    "Hindi / हिन्दी": {"code": "hi", "native": "Hindi"},
    "Korean / 한국어": {"code": "ko", "native": "Korean"},
    "Japanese / 日本語": {"code": "ja", "native": "Japanese"},
    "Portuguese / Português": {"code": "pt", "native": "Portuguese"},
    "Arabic / العربية": {"code": "ar", "native": "Arabic"},
    "Telugu / తెలుగు": {"code": "te", "native": "Telugu"},
    "Tamil / தமிழ்": {"code": "ta", "native": "Tamil"},
    "Punjabi / ਪੰਜਾਬੀ": {"code": "pa", "native": "Punjabi"}
}

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
def init_session_state():
    """Initialize all session state variables on first run."""
    if "page" not in st.session_state:
        st.session_state.page = "Home"
    if "selected_language" not in st.session_state:
        st.session_state.selected_language = "English"
    if "encounter_log" not in st.session_state:
        st.session_state.encounter_log = load_encounters()
    if "emergency_activated" not in st.session_state:
        st.session_state.emergency_activated = False
    if "translation_history" not in st.session_state:
        st.session_state.translation_history = []

init_session_state()

# ============================================================================
# PERSISTENT STORAGE FUNCTIONS
# ============================================================================
ENCOUNTER_FILE = "encounters.json"
RESOURCES_FILE = "resources.json"

def load_encounters():
    """Load all logged encounters from persistent storage."""
    if os.path.exists(ENCOUNTER_FILE):
        try:
            with open(ENCOUNTER_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_encounter(encounter_data):
    """Save new encounter to persistent storage."""
    encounters = load_encounters()
    encounters.append(encounter_data)
    with open(ENCOUNTER_FILE, "w") as f:
        json.dump(encounters, f, indent=2)
    st.session_state.encounter_log = encounters

def log_encounter(encounter_type, language, notes=""):
    """Create structured encounter log entry."""
    encounter = {
        "timestamp": datetime.now().isoformat(),
        "type": encounter_type,
        "language": language,
        "notes": notes,
        "status": "Completed"
    }
    save_encounter(encounter)
    return encounter

def get_encounter_stats():
    """Generate statistics from encounter log."""
    encounters = st.session_state.encounter_log
    if not encounters:
        return {"total": 0, "languages": {}, "types": {}}
    
    stats = {
        "total": len(encounters),
        "languages": {},
        "types": {}
    }
    
    for enc in encounters:
        lang = enc.get("language", "Unknown")
        enc_type = enc.get("type", "Unknown")
        stats["languages"][lang] = stats["languages"].get(lang, 0) + 1
        stats["types"][enc_type] = stats["types"].get(enc_type, 0) + 1
    
    return stats

# ============================================================================
# TRANSLATION & CACHING
# ============================================================================
@st.cache_resource(show_spinner=False)
def get_translator(source_lang, target_lang):
    """Cache translator objects for performance."""
    return GoogleTranslator(source=source_lang, target=target_lang)

@st.cache_data(show_spinner=False)
def get_ui_strings(language_name, language_code):
    """Cache UI strings with language-specific optimizations."""
    default_strings = {
        "home_title": "CivicShield: Know Your Rights",
        "home_subtitle": "Real-time legal translation and civil rights protection",
        "emergency_alert": "EMERGENCY: HELP ME RIGHT NOW",
        "translation_label": "Officer's Statement (English):",
        "advice_label": "Your Rights & Advice:",
        "language_label": "Select Your Language:",
        "record_button": "🎤 Record Officer's Voice",
        "stop_button": "⏹️ Stop Recording & Translate",
        "listen_button": "🔊 Listen to Advice",
        "respond_button": "📢 Speak Your Response",
        "log_encounter": "📝 Log Encounter",
        "view_encounters": "📋 View Encounter History",
        "rights_center": "📚 Rights Education Center",
        "resources": "🏥 Community Resources",
        "emergency": "🚨 Emergency Assistance",
        "settings": "⚙️ Settings",
    }
    
    # Fast path for English (no translation needed)
    if language_name == "English":
        return default_strings
    
    # Fast path for Spanish (pre-translated)
    if language_name == "Spanish":
        return {
            "home_title": "CivicShield: Conoce Tus Derechos",
            "home_subtitle": "Traducción legal en tiempo real y protección de derechos civiles",
            "emergency_alert": "EMERGENCIA: ¡AYÚDEME AHORA MISMO!",
            "translation_label": "Declaración del Oficial (Inglés):",
            "advice_label": "Tus Derechos y Consejo:",
            "language_label": "Selecciona Tu Idioma:",
            "record_button": "🎤 Grabar Voz del Oficial",
            "stop_button": "⏹️ Detener y Traducir",
            "listen_button": "🔊 Escuchar Consejo",
            "respond_button": "📢 Habla Tu Respuesta",
            "log_encounter": "📝 Registrar Encuentro",
            "view_encounters": "📋 Ver Historial de Encuentros",
            "rights_center": "📚 Centro de Educación de Derechos",
            "resources": "🏥 Recursos Comunitarios",
            "emergency": "🚨 Asistencia de Emergencia",
            "settings": "⚙️ Configuración",
        }
    
    # Dynamic translation for other languages
    try:
        translator = get_translator("en", language_code)
        translated = {}
        for key, value in default_strings.items():
            translated[key] = translator.translate(value)
        return translated
    except:
        return default_strings

# ============================================================================
# RIGHTS EDUCATION CONTENT
# ============================================================================
RIGHTS_EDUCATION = {
    "Fourth Amendment": {
        "title": "Fourth Amendment: Protection from Searches",
        "content": """
**Your Right:** You have the right to be free from unreasonable searches and seizures.

**Key Points:**
- Police generally need a warrant to search your home, car, or personal belongings
- You can refuse a search by saying: "I do not consent to a search"
- Do NOT physically resist - it could result in additional charges
- Even if you refuse, police may continue if they have a warrant or probable cause

**What You CAN Do:**
- Remain silent and ask "Am I free to go?"
- Ask "Do you have a warrant?"
- Keep your hands visible
- Do not physically obstruct police
        """
    },
    "Fifth Amendment": {
        "title": "Fifth Amendment: Right to Remain Silent",
        "content": """
**Your Right:** You have the right to remain silent and not incriminate yourself.

**Key Points:**
- You do NOT have to answer police questions
- Say clearly: "I am exercising my right to remain silent"
- This right applies even if you haven't been arrested
- Staying silent cannot be used against you in court

**Important:**
- You must tell police you are invoking this right - silence alone may not be enough
- If arrested, ask for a lawyer immediately
- Do not try to explain yourself or negotiate
        """
    },
    "Sixth Amendment": {
        "title": "Sixth Amendment: Right to an Attorney",
        "content": """
**Your Right:** You have the right to an attorney.

**Key Points:**
- If you cannot afford an attorney, one will be provided
- You can request an attorney at ANY time during questioning
- Once you ask for a lawyer, police should stop questioning you
- You have the right to have your attorney present during questioning

**What to Say:**
- "I want to speak to an attorney"
- "I am invoking my right to an attorney"
- Then remain silent until your attorney arrives
        """
    },
    "Traffic Stops": {
        "title": "Traffic Stop Rights (California)",
        "content": """
**During a Traffic Stop:**
- You must provide your license, registration, and proof of insurance
- You can ask: "Am I being detained or am I free to go?"
- You do NOT have to consent to a search of your vehicle
- Say clearly: "I do not consent to a search"

**Vehicle Search:**
- Police can look through windows without permission
- Police can search your car if they find probable cause (drugs smell, weapons visible)
- They can search without consent if you're arrested
- You CAN refuse the search, but they may proceed if they have probable cause

**Your Rights:**
- Keep hands visible
- Speak calmly and politely
- Do not physically resist
- You can film the stop (but don't interfere)
        """
    },
    "Arrest": {
        "title": "If You Are Arrested",
        "content": """
**Important Steps:**
1. Remain silent - do not answer questions
2. Say "I want a lawyer" clearly
3. Do not sign anything without your attorney
4. Do not discuss the case with cellmates or other inmates

**Your Rights Upon Arrest:**
- You have the right to be informed of charges against you
- You have the right to a phone call
- You have the right to remain silent
- You have the right to an attorney

**What NOT to Do:**
- Do not resist arrest (even if you believe it's illegal)
- Do not sign any statements
- Do not consent to searches
- Do not make deals with police without a lawyer
        """
    }
}

# ============================================================================
# COMMUNITY RESOURCES
# ============================================================================
COMMUNITY_RESOURCES = {
    "Legal Aid Organizations": [
        {
            "name": "California Rural Legal Assistance (CRLA)",
            "phone": "1-833-435-2752",
            "services": "Free legal services for low-income individuals",
            "website": "crla.org"
        },
        {
            "name": "Legal Aid Society of San Francisco",
            "phone": "(415) 701-1000",
            "services": "Criminal defense, immigration, housing",
            "website": "sflas.org"
        },
        {
            "name": "Public Defender's Office (San Jose)",
            "phone": "(408) 287-1010",
            "services": "Free legal defense for criminal cases",
            "website": "sccgov.org/sites/pdo"
        }
    ],
    "Emergency Services": [
        {
            "name": "National Suicide Prevention Lifeline",
            "phone": "988",
            "services": "24/7 mental health crisis support",
            "website": "988lifeline.org"
        },
        {
            "name": "RAINN - Sexual Assault Hotline",
            "phone": "1-800-656-4673",
            "services": "Confidential sexual assault support",
            "website": "rainn.org"
        },
        {
            "name": "National Domestic Violence Hotline",
            "phone": "1-800-799-7233",
            "services": "Domestic violence resources and support",
            "website": "thehotline.org"
        }
    ],
    "Immigration Legal Services": [
        {
            "name": "American Civil Liberties Union (ACLU)",
            "phone": "1-212-549-2500",
            "services": "Immigration rights and legal advocacy",
            "website": "aclu.org/immigrants-rights"
        },
        {
            "name": "USCIS - Official Immigration Services",
            "phone": "1-800-375-5283",
            "services": "Government immigration information",
            "website": "uscis.gov"
        }
    ]
}

# ============================================================================
# EMERGENCY ASSISTANCE PAGE
# ============================================================================
def page_emergency():
    """Emergency assistance and crisis resources."""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("# 🚨 Emergency Assistance")
        st.markdown("### Immediate Resources & Crisis Support")
    
    with col2:
        st.metric("Emergency", "911", delta="Always Available")
    
    st.divider()
    
    # Emergency contacts
    st.markdown("## Critical Phone Numbers")
    emergency_numbers = {
        "Emergency (Police, Fire, Medical)": "911",
        "National Suicide Prevention": "988",
        "Domestic Violence Hotline": "1-800-799-7233",
        "Sexual Assault Support (RAINN)": "1-800-656-4673",
        "Poison Control": "1-800-222-1222",
        "Crisis Text Line": "Text HOME to 741741"
    }
    
    for service, number in emergency_numbers.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{service}**")
        with col2:
            st.code(number, language="")
    
    st.divider()
    
    # Emergency procedures
    st.markdown("## What to Do in an Emergency")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Medical Emergency
        1. **Call 911 immediately**
        2. State your location clearly
        3. Describe the emergency
        4. Follow dispatcher instructions
        5. Unlock doors for paramedics
        
        ### Active Threat/Violence
        1. **RUN** - Leave area immediately
        2. **HIDE** - Lock doors, silence phones
        3. **FIGHT** - Only as last resort
        4. **Call 911** when safe to do so
        """)
    
    with col2:
        st.markdown("""
        ### Police Encounter Emergency
        1. **Stay calm** - Comply with lawful orders
        2. **Remain silent** - Say "I want a lawyer"
        3. **Keep hands visible** - Show non-compliance
        4. **Record the encounter** - If safe to do so
        5. **Note officer details** - Badge number, name
        
        ### Mental Health Crisis
        1. **Call 988** - Crisis support line
        2. **Tell someone you trust**
        3. **Go to hospital** if having thoughts of harm
        4. **Remove access** to means of self-harm
        5. **Stay with someone** - Don't be alone
        """)
    
    st.divider()
    
    # Crisis support resources
    st.markdown("## 24/7 Crisis Support Resources")
    
    crisis_resources = {
        "Crisis Text Line": {
            "how": "Text HOME to 741741",
            "available": "24/7",
            "focus": "Any crisis - mental health, abuse, substance use"
        },
        "National Suicide Prevention": {
            "how": "Call or text 988",
            "available": "24/7",
            "focus": "Suicide prevention and mental health crisis"
        },
        "SAMHSA National Helpline": {
            "how": "1-800-662-4357",
            "available": "24/7, Free, Confidential",
            "focus": "Substance abuse and mental health treatment"
        }
    }
    
    for resource, info in crisis_resources.items():
        st.markdown(f"""
        **{resource}**
        - **Contact:** {info['how']}
        - **Available:** {info['available']}
        - **Focus:** {info['focus']}
        """)

# ============================================================================
# RIGHTS EDUCATION PAGE
# ============================================================================
def page_rights_education():
    """Educational content about legal rights."""
    st.markdown("# 📚 Rights Education Center")
    st.markdown("### Know Your Constitutional Rights")
    
    st.divider()
    
    # Topic selector
    selected_right = st.selectbox(
        "Select a topic to learn about:",
        list(RIGHTS_EDUCATION.keys()),
        key="rights_selector"
    )
    
    # Display selected topic
    topic = RIGHTS_EDUCATION[selected_right]
    st.markdown(f"## {topic['title']}")
    st.markdown(topic['content'])
    
    st.divider()
    
    # General guidelines
    st.markdown("## General Guidelines for Any Police Encounter")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### ✅ DO
        - Stay calm and polite
        - Keep hands visible
        - Answer basic ID questions
        - Remember details
        - Ask for a lawyer
        - Say "I don't consent"
        """)
    
    with col2:
        st.markdown("""
        ### ❌ DON'T
        - Run or resist
        - Reach suddenly
        - Lie or make up stories
        - Touch the officer
        - Consent to searches
        - Sign anything
        """)
    
    with col3:
        st.markdown("""
        ### 🗣️ SAY
        - "Am I being detained?"
        - "I want a lawyer"
        - "I don't consent"
        - Keep responses brief
        - Speak clearly
        - Stay silent otherwise
        """)
    
    st.divider()
    
    st.info("""
    **⚠️ Disclaimer:** This educational content is for informational purposes only. 
    It is not legal advice. Always consult with a qualified attorney for specific legal situations.
    """)

# ============================================================================
# COMMUNITY RESOURCES PAGE
# ============================================================================
def page_community_resources():
    """Display community resources and support services."""
    st.markdown("# 🏥 Community Resources")
    st.markdown("### Local & National Support Services")
    
    st.divider()
    
    # Resource category selector
    category = st.selectbox(
        "Select resource category:",
        list(COMMUNITY_RESOURCES.keys()),
        key="resources_selector"
    )
    
    st.markdown(f"## {category}")
    
    # Display resources
    for resource in COMMUNITY_RESOURCES[category]:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
            ### {resource['name']}
            **Services:** {resource['services']}
            **Phone:** {resource['phone']}
            **Website:** {resource['website']}
            """)
        
        with col2:
            if st.button(f"📞 Call {resource['name']}", key=resource['name']):
                st.info(f"Call: {resource['phone']}")
    
    st.divider()
    
    # Bay Area specific information
    st.markdown("""
    ## Bay Area Specific Resources
    
    ### San Jose
    - **Public Defender:** (408) 287-1010
    - **Legal Aid:** (408) 288-6713
    
    ### San Francisco
    - **Public Defender:** (628) 652-4000
    - **Legal Aid:** (415) 701-1000
    
    ### Oakland
    - **Public Defender:** (510) 267-8500
    - **Legal Aid:** (510) 663-4060
    """)

# ============================================================================
# ENCOUNTER LOGGING PAGE
# ============================================================================
def page_encounter_logging():
    """Log and view police encounters."""
    st.markdown("# 📝 Encounter Logging & Tracking")
    st.markdown("### Document Your Interactions for Legal Protection")
    
    st.divider()
    
    # Tabs for logging vs. viewing
    tab1, tab2 = st.tabs(["📝 Log New Encounter", "📋 View History"])
    
    with tab1:
        st.markdown("## Log a New Encounter")
        
        col1, col2 = st.columns(2)
        
        with col1:
            encounter_type = st.selectbox(
                "Encounter Type:",
                ["Traffic Stop", "Police Questioning", "Search/Seizure", 
                 "Arrest", "Other"],
                key="encounter_type"
            )
            
            selected_lang = st.selectbox(
                "Language Used:",
                list(LANGUAGE_MAP.keys()),
                key="encounter_lang"
            )
        
        with col2:
            location = st.text_input("Location (optional):")
            officer_badge = st.text_input("Officer Badge Number (if known):")
        
        # Detailed notes
        notes = st.text_area(
            "Encounter Details:",
            placeholder="Describe what happened, what was said, etc.",
            height=200,
            key="encounter_notes"
        )
        
        # Outcome
        outcome = st.selectbox(
            "Outcome:",
            ["Released with warning", "Ticketed", "Arrested", "Other", "Unresolved"],
            key="encounter_outcome"
        )
        
        st.divider()
        
        # Save button
        if st.button("💾 Save Encounter Log", type="primary", use_container_width=True):
            encounter = log_encounter(
                encounter_type=encounter_type,
                language=LANGUAGE_MAP[selected_lang]["native"],
                notes=f"Location: {location}\nBadge: {officer_badge}\nDetails: {notes}\nOutcome: {outcome}"
            )
            st.success("✅ Encounter logged successfully!")
            st.balloons()
    
    with tab2:
        st.markdown("## Encounter History")
        
        # Statistics
        stats = get_encounter_stats()
        
        if stats["total"] > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Encounters Logged", stats["total"])
            
            with col2:
                most_lang = max(stats["languages"], key=stats["languages"].get) if stats["languages"] else "N/A"
                st.metric("Most Used Language", most_lang)
            
            with col3:
                most_type = max(stats["types"], key=stats["types"].get) if stats["types"] else "N/A"
                st.metric("Most Common Type", most_type)
            
            st.divider()
            
            # Display encounters
            st.markdown("### Logged Encounters")
            for i, enc in enumerate(reversed(st.session_state.encounter_log), 1):
                with st.expander(f"Encounter {len(st.session_state.encounter_log) - i + 1}: {enc.get('type', 'Unknown')} - {enc.get('timestamp', 'Unknown')[:10]}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Type:** {enc.get('type', 'Unknown')}")
                        st.markdown(f"**Language:** {enc.get('language', 'Unknown')}")
                    with col2:
                        st.markdown(f"**Date:** {enc.get('timestamp', 'Unknown')[:10]}")
                        st.markdown(f"**Status:** {enc.get('status', 'Unknown')}")
                    st.divider()
                    st.markdown(f"**Details:**\n{enc.get('notes', 'No details provided')}")
        else:
            st.info("📭 No encounters logged yet. Your encounters will appear here.")

# ============================================================================
# HOME PAGE - MAIN TRANSLATION INTERFACE
# ============================================================================
def page_home():
    """Main home page with translation and audio features."""
    
    # Get selected language
    target_language = st.session_state.selected_language
    target_code = LANGUAGE_MAP[target_language]["code"]
    lang_name = LANGUAGE_MAP[target_language]["native"]
    
    # Get UI strings
    ui = get_ui_strings(lang_name, target_code)
    
    st.markdown(f"# {ui['home_title']}")
    st.markdown(f"### {ui['home_subtitle']}")
    
    st.divider()
    
    # Emergency button (prominent placement)
    if st.button(ui['emergency_alert'], type="primary", use_container_width=True, key="emergency_home"):
        st.session_state.emergency_activated = True
        
        # Generate and play emergency audio
        audio_text_en = "Officer, I am using a translation app to protect my rights. Please speak into the device."
        try:
            tts = gTTS(text=audio_text_en, lang='en', slow=False)
            tts.save("emergency_notification.mp3")
            
            st.error("⚠️ EMERGENCY MODE ACTIVATED")
            st.write("Playing audio to officer...")
            
            with open("emergency_notification.mp3", "rb") as f:
                st.audio(f.read(), format="audio/mp3")
            
            log_encounter("Emergency Activation", lang_name, "Emergency assistance activated")
        except Exception as e:
            st.error(f"Audio generation failed: {e}")
    
    st.divider()
    
    st.markdown("## 🎤 Real-Time Translation Interface")
    st.markdown("### Step 1: Record Officer's Statement")
    
    # Audio recording section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Record officer's voice:**")
        audio_record = mic_recorder(
            start_prompt=ui['record_button'],
            stop_prompt=ui['stop_button'],
            format="wav",
            key='officer_voice_recorder'
        )
    
    with col2:
        st.markdown("**Or type manually:**")
        manual_input = st.text_area(
            ui['translation_label'],
            placeholder="Type what the officer said...",
            height=100,
            key="manual_officer_input"
        )
    
    # Process recorded audio
    officer_text = ""
    if audio_record:
        try:
            audio_bytes = audio_record['bytes']
            recognizer = sr.Recognizer()
            
            with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
                audio_data = recognizer.record(source)
                officer_text = recognizer.recognize_google(audio_data, language="en-US")
                st.success(f"✅ Speech recognized: \"{officer_text}\"")
        except sr.UnknownValueError:
            st.warning("Could not understand audio. Please speak clearly or type below.")
        except sr.RequestError as e:
            st.error(f"Speech recognition error: {e}")
    
    # Use manual input if no speech recognition
    final_input = manual_input if manual_input else officer_text
    
    st.divider()
    
    # Translation and advice section
    if final_input:
        st.markdown("## 📖 Step 2: Your Rights & Advice")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Original (English):**")
            st.text(final_input)
        
        with col2:
            # Translate to target language
            if lang_name != "English":
                try:
                    translator = get_translator("en", target_code)
                    translated = translator.translate(final_input)
                    st.markdown(f"**Translated ({lang_name}):**")
                    st.text(translated)
                except Exception as e:
                    st.error(f"Translation error: {e}")
        
        st.divider()
        
        # Legal advice based on keywords
        st.markdown("### ⚖️ Legal Safeguards")
        
        lower_input = final_input.lower()
        advice_en = ""
        advice_translated = ""
        alert_level = "info"
        
        # Keyword-based advice
        if "search" in lower_input or "look inside" in lower_input:
            advice_en = """
            **FOURTH AMENDMENT ALERT: Right Against Unreasonable Searches**
            
            You have the legal right to refuse warrantless searches. 
            Do NOT physically resist, but say clearly: 
            
            **"I do not consent to a search."**
            
            Even if they search anyway, your refusal is legally important.
            """
            alert_level = "error"
        
        elif "step out" in lower_input or "get out" in lower_input:
            advice_en = """
            **TRAFFIC STOP RULE: Pennsylvania v. Mimms**
            
            Under this law, you MUST exit the vehicle if ordered during a traffic stop.
            However, you do NOT have to answer their questions.
            
            Ask clearly: **"Am I free to go, or am I being detained?"**
            """
            alert_level = "warning"
        
        elif "handcuff" in lower_input or "arrest" in lower_input:
            advice_en = """
            **FIFTH AMENDMENT ALERT: Right to Remain Silent**
            
            You have the right to remain silent. Do not resist physically.
            State clearly and calmly:
            
            **"I am exercising my right to remain silent and I want an attorney."**
            
            Then remain completely silent until an attorney arrives.
            """
            alert_level = "error"
        
        elif "question" in lower_input or "ask" in lower_input:
            advice_en = """
            **GENERAL QUESTIONING RIGHTS**
            
            You have the right to remain silent and refuse to answer questions.
            You can say: 
            
            **"I would like to speak to an attorney before answering any questions."**
            """
            alert_level = "info"
        
        else:
            advice_en = """
            **STANDARD ENCOUNTER RIGHTS**
            
            - Keep hands visible and non-threatening
            - Remain calm and polite
            - You have the right to remain silent
            - You have the right to refuse searches ("I don't consent")
            - You have the right to an attorney
            """
            alert_level = "info"
        
        # Translate advice
        if lang_name != "English" and advice_en:
            try:
                translator = get_translator("en", target_code)
                # Translate key phrases only for better quality
                advice_translated = translator.translate(advice_en)
            except:
                advice_translated = advice_en
        
        # Display advice
        if alert_level == "error":
            st.error(advice_en)
            if advice_translated and lang_name != "English":
                st.error(f"**{lang_name}:**\n{advice_translated}")
        elif alert_level == "warning":
            st.warning(advice_en)
            if advice_translated and lang_name != "English":
                st.warning(f"**{lang_name}:**\n{advice_translated}")
        else:
            st.info(advice_en)
            if advice_translated and lang_name != "English":
                st.info(f"**{lang_name}:**\n{advice_translated}")
        
        st.divider()
        
        # Audio playback section
        st.markdown("## 🔊 Step 3: Audio Coaching")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Listen to Advice ({lang_name}):**")
            
            # Determine which text to use for audio
            audio_text = advice_en if lang_name == "English" else advice_translated
            
            # Clean up markdown for TTS
            audio_text_clean = audio_text.replace("**", "").replace("###", "").replace("##", "").replace("#", "").replace("\n\n", ". ")
            
            try:
                tts_advice = gTTS(text=audio_text_clean[:500], lang=target_code, slow=False)
                tts_advice.save("advice_audio.mp3")
                
                with open("advice_audio.mp3", "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
            except Exception as e:
                st.warning(f"Could not generate audio: {e}")
        
        with col2:
            st.markdown("**Your Response to Officer (English):**")
            
            # Generate suggested response
            if "search" in lower_input:
                response_en = "Officer, I do not consent to a search of my property."
            elif "arrest" in lower_input:
                response_en = "Officer, I am exercising my right to remain silent and I want an attorney."
            else:
                response_en = "I would like to speak to an attorney before answering any questions."
            
            st.info(response_en)
            
            # Play response audio
            try:
                tts_response = gTTS(text=response_en, lang='en', slow=False)
                tts_response.save("response_audio.mp3")
                
                with open("response_audio.mp3", "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
            except Exception as e:
                st.warning(f"Could not generate response audio: {e}")
        
        st.divider()
        
        # Log encounter option
        if st.button(ui['log_encounter'], key="log_from_home"):
            log_encounter("Translation Session", lang_name, f"Officer said: {final_input}")
            st.success("✅ Encounter logged!")

# ============================================================================
# MAIN APP NAVIGATION & LAYOUT
# ============================================================================
def main():
    """Main app with sidebar navigation."""
    
    # Sidebar header
    st.sidebar.markdown("# ⚖️ CivicShield")
    st.sidebar.markdown("---")
    
    # Language selector in sidebar
    st.session_state.selected_language = st.sidebar.selectbox(
        "📍 Select Language:",
        list(LANGUAGE_MAP.keys()),
        index=list(LANGUAGE_MAP.keys()).index(st.session_state.selected_language),
        key="language_selector"
    )
    
    st.sidebar.divider()
    
    # Navigation menu
    st.sidebar.markdown("### Navigation")
    
    nav_options = {
        "🏠 Home": "Home",
        "📚 Rights Education": "RightsEducation",
        "🏥 Community Resources": "Resources",
        "📝 Encounter Logging": "EncounterLogging",
        "🚨 Emergency Help": "Emergency",
    }
    
    for label, page_name in nav_options.items():
        if st.sidebar.button(label, use_container_width=True, key=f"nav_{page_name}"):
            st.session_state.page = page_name
    
    st.sidebar.divider()
    
    # About section
    st.sidebar.markdown("### About CivicShield")
    st.sidebar.markdown("""
    **Version:** 2.0.0  
    **Purpose:** Real-time legal translation and civil rights protection
    
    **Supported Languages:** 14  
    **Features:** Translation, audio, rights education, encounter logging
    
    Built for the San Francisco Bay Area and beyond.
    """)
    
    st.sidebar.divider()
    
    # Disclaimer
    st.sidebar.warning("""
    **⚠️ Legal Disclaimer**
    
    This app provides educational information, not legal advice. 
    Always consult a qualified attorney for your specific situation.
    """)
    
    # Page routing
    if st.session_state.page == "Home":
        page_home()
    elif st.session_state.page == "RightsEducation":
        page_rights_education()
    elif st.session_state.page == "Resources":
        page_community_resources()
    elif st.session_state.page == "EncounterLogging":
        page_encounter_logging()
    elif st.session_state.page == "Emergency":
        page_emergency()

# ============================================================================
# APP ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    main()
