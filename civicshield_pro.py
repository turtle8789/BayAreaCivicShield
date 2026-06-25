"""
CivicShield Pro - Fully Localized Rights Translation & Civil Rights App
Production-Ready Implementation with Complete UI Localization

CORE FEATURES:
- Full application localization in 14 languages
- Dashboard-style home page with feature cards
- Real-time speech-to-text translation (14 languages)
- Rights education center with California legal information
- Legal Document Assistant with OCR and translation
- Encounter logging with persistent storage
- Community resources directory
- Emergency assistance guide
- Know Your Rights Near Me (location-based legal aid finder)
- Professional sidebar navigation
- Streamlit session state management
- Audio playback for users and officers
- Clean, accessible professional UI

AUTHOR: Community Justice Initiative
VERSION: 3.0.0
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
import re
import copy
from PIL import Image
import qrcode

# Optional imports with graceful fallback
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    from pdf2image import convert_from_bytes
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ============================================================================
# PAGE CONFIGURATION & THEMING
# ============================================================================
st.set_page_config(
    page_title="CivicShield Pro",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit menu and footer for custom design
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Modern Pinterest-Inspired CSS Design
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Lato:wght@300;400;700&display=swap');

* {
    font-family: 'Lato', sans-serif;
}

/* ============= COLOR PALETTE ============= */
:root {
    --cream-bg: #F8F5F2;
    --card-bg: #FFFDFB;
    --accent-terracotta: #C97C5D;
    --accent-rose: #D89CA4;
    --text-dark: #4B403A;
    --text-light: #6B5F55;
    --sage: #A7B8A0;
    --shadow-soft: 0 8px 24px rgba(75, 64, 58, 0.08);
    --shadow-hover: 0 16px 40px rgba(75, 64, 58, 0.15);
}

/* ============= MAIN LAYOUT ============= */
body {
    background-color: var(--cream-bg);
}

.main {
    background: linear-gradient(135deg, var(--cream-bg) 0%, #F5F0EB 100%);
    padding: 2rem 0;
}

/* ============= SIDEBAR STYLING ============= */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #F8F5F2 0%, #F5F0EB 100%);
    border-right: 1px solid #E8DFD7;
}

[data-testid="stSidebar"] > div > div > div > div > h1 {
    color: var(--text-dark);
    font-family: 'Poppins', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    letter-spacing: -0.5px;
}

/* ============= TYPOGRAPHY ============= */
h1 {
    font-family: 'Poppins', sans-serif;
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--text-dark);
    margin-bottom: 1.5rem;
    letter-spacing: -0.5px;
}

h2 {
    font-family: 'Poppins', sans-serif;
    font-size: 1.75rem;
    font-weight: 600;
    color: var(--text-dark);
    margin-bottom: 1.25rem;
}

h3 {
    font-family: 'Poppins', sans-serif;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-dark);
}

p {
    font-size: 1rem;
    line-height: 1.6;
    color: var(--text-light);
}

/* ============= MODERN CARDS ============= */
.dashboard-card {
    background: linear-gradient(135deg, var(--card-bg) 0%, #FFFAF7 100%);
    border-radius: 24px;
    padding: 2.5rem 2rem;
    margin: 1.5rem 0;
    border: 1px solid rgba(201, 124, 93, 0.1);
    box-shadow: var(--shadow-soft);
    transition: all 0.4s cubic-bezier(0.23, 1, 0.320, 1);
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.dashboard-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 0;
    background: linear-gradient(180deg, var(--accent-terracotta) 0%, var(--accent-rose) 100%);
    transition: height 0.4s ease;
}

.dashboard-card:hover {
    box-shadow: var(--shadow-hover);
    transform: translateY(-8px) scale(1.02);
    border-color: rgba(201, 124, 93, 0.2);
}

.dashboard-card:hover::before {
    height: 100%;
}

.card-icon {
    font-size: 3.5rem;
    margin-bottom: 1.25rem;
    display: inline-block;
    animation: fadeIn 0.6s ease-out;
}

.card-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-dark);
    margin-bottom: 0.75rem;
    font-family: 'Poppins', sans-serif;
}

.card-description {
    color: var(--text-light);
    font-size: 0.95rem;
    line-height: 1.6;
    font-weight: 400;
}

/* ============= BUTTONS ============= */
.stButton > button {
    border-radius: 50px !important;
    font-weight: 600 !important;
    font-family: 'Poppins', sans-serif !important;
    padding: 0.75rem 2rem !important;
    transition: all 0.3s cubic-bezier(0.23, 1, 0.320, 1) !important;
    border: none !important;
    background: linear-gradient(135deg, var(--accent-terracotta) 0%, var(--accent-rose) 100%) !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(201, 124, 93, 0.25) !important;
    cursor: pointer !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(201, 124, 93, 0.35) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* ============= ALERTS ============= */
.stAlert {
    border-radius: 16px !important;
    padding: 1.5rem !important;
    border: none !important;
    box-shadow: var(--shadow-soft) !important;
    margin: 1rem 0 !important;
}

/* Success alerts */
.stAlert[kind=success] {
    background-color: rgba(167, 184, 160, 0.1) !important;
    color: var(--sage) !important;
}

/* Error alerts */
.stAlert[kind=error] {
    background-color: rgba(217, 156, 164, 0.1) !important;
    color: var(--accent-rose) !important;
}

/* Warning alerts */
.stAlert[kind=warning] {
    background-color: rgba(201, 124, 93, 0.1) !important;
    color: var(--accent-terracotta) !important;
}

/* Info alerts */
.stAlert[kind=info] {
    background-color: rgba(201, 124, 93, 0.05) !important;
    color: var(--text-dark) !important;
}

/* ============= TEXT INPUTS & SELECTORS ============= */
.stTextInput > div > div > input,
.stSelectbox > div > div > select,
.stTextArea > div > div > textarea {
    border-radius: 12px !important;
    border: 1px solid #E8DFD7 !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
    background-color: var(--card-bg) !important;
    transition: all 0.3s ease !important;
}

.stTextInput > div > div > input:focus,
.stSelectbox > div > div > select:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent-terracotta) !important;
    box-shadow: 0 0 0 2px rgba(201, 124, 93, 0.1) !important;
}

/* ============= ANIMATIONS ============= */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideInLeft {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

.fadeIn-animation {
    animation: fadeIn 0.6s ease-out;
}

.slideIn-animation {
    animation: slideInLeft 0.6s ease-out;
}

.pulse-animation {
    animation: pulse 2s ease-in-out infinite;
}

/* ============= ACCESSIBILITY MODES ============= */
/* Large Text Mode */
.large-text {
    font-size: 1.1rem !important;
}

.large-text h1 {
    font-size: 3rem !important;
}

.large-text h2 {
    font-size: 2rem !important;
}

.large-text .stButton > button {
    padding: 1rem 2.5rem !important;
    font-size: 1.1rem !important;
}

/* High Contrast Mode */
.high-contrast {
    background: white !important;
}

.high-contrast .dashboard-card {
    background: white !important;
    border: 2px solid var(--text-dark) !important;
}

.high-contrast h1,
.high-contrast h2,
.high-contrast h3 {
    color: #000 !important;
    font-weight: 800 !important;
}

.high-contrast p {
    color: #000 !important;
    font-weight: 600 !important;
}

/* ============= RESPONSIVE DESIGN ============= */
@media (max-width: 1200px) {
    h1 { font-size: 2rem; }
    h2 { font-size: 1.5rem; }
    .dashboard-card { padding: 1.75rem; }
}

@media (max-width: 768px) {
    .main { padding: 1rem 0; }
    h1 { font-size: 1.75rem; }
    h2 { font-size: 1.25rem; }
    .dashboard-card { padding: 1.5rem 1rem; }
    .stButton > button { padding: 0.65rem 1.5rem !important; }
}

@media (max-width: 480px) {
    [data-testid="stSidebar"] { width: 250px !important; }
    h1 { font-size: 1.5rem; }
    .dashboard-card { padding: 1rem; }
}

/* ============= LOADING INDICATOR ============= */
.loading-spinner {
    display: inline-block;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* ============= DIVIDER ============= */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, #D89CA4 50%, transparent 100%);
    margin: 2rem 0;
}

/* ============= MOBILE OPTIMIZATION ============= */
@media (max-width: 768px) {
    h1 {
        font-size: 1.75rem !important;
    }
    
    h2 {
        font-size: 1.25rem !important;
    }
    
    .dashboard-card {
        padding: 1.5rem 1rem !important;
        margin: 1rem 0 !important;
    }
    
    .card-icon {
        font-size: 2.5rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    .stButton > button {
        padding: 0.5rem 1.5rem !important;
        font-size: 0.9rem !important;
    }
    
    .main {
        padding: 1rem 0 !important;
    }
    
    [data-testid="stSidebar"] {
        width: 280px !important;
    }
}

@media (max-width: 480px) {
    h1 {
        font-size: 1.5rem !important;
    }
    
    h2 {
        font-size: 1.1rem !important;
    }
    
    .dashboard-card {
        padding: 1rem 0.75rem !important;
        margin: 0.75rem 0 !important;
    }
    
    .card-icon {
        font-size: 2rem !important;
    }
    
    .card-title {
        font-size: 1.1rem !important;
    }
    
    .card-description {
        font-size: 0.85rem !important;
    }
    
    .stButton > button {
        padding: 0.4rem 1rem !important;
        font-size: 0.8rem !important;
    }
    
    p {
        font-size: 0.95rem !important;
    }
    
    [data-testid="stSidebar"] {
        width: 100% !important;
        position: fixed !important;
        height: 100vh !important;
    }
}

/* ============= LANDING PAGE STYLES ============= */
.landing-hero {
    text-align: center;
    padding: 3rem 2rem;
    background: linear-gradient(135deg, var(--cream-bg) 0%, #F0E5DC 100%);
    border-radius: 24px;
    margin: 2rem 0;
}

.landing-hero h1 {
    font-size: 3.5rem;
    color: var(--text-dark);
    margin-bottom: 1rem;
    line-height: 1.2;
}

.landing-hero p {
    font-size: 1.3rem;
    color: var(--text-light);
    max-width: 800px;
    margin: 0 auto 2rem;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
    margin: 3rem 0;
}

.qr-container {
    text-align: center;
    padding: 2rem;
    background: white;
    border-radius: 16px;
    border: 2px solid rgba(201, 124, 93, 0.2);
}

/* ============= TUTORIAL STYLES ============= */
.tutorial-container {
    max-width: 800px;
    margin: 2rem auto;
    text-align: center;
}

.tutorial-step {
    background: linear-gradient(135deg, var(--card-bg) 0%, #FFFAF7 100%);
    padding: 3rem 2rem;
    border-radius: 24px;
    border: 2px solid rgba(201, 124, 93, 0.1);
    margin: 2rem 0;
}

.step-number {
    display: inline-block;
    background: linear-gradient(135deg, var(--accent-terracotta) 0%, var(--accent-rose) 100%);
    color: white;
    border-radius: 50%;
    width: 60px;
    height: 60px;
    line-height: 60px;
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 1rem;
}

.step-description {
    font-size: 1.2rem;
    color: var(--text-light);
    margin: 1rem 0;
}

/* ============= LOADING SCREEN ============= */
.loading-overlay {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 300px;
}

.spinner {
    animation: spin 1s linear infinite;
    font-size: 3rem;
}

.welcome-message {
    text-align: center;
    padding: 2rem;
    background: linear-gradient(135deg, rgba(201, 124, 93, 0.1) 0%, rgba(216, 156, 164, 0.1) 100%);
    border-radius: 16px;
    border-left: 4px solid var(--accent-terracotta);
    margin: 2rem 0;
}

@media (max-width: 768px) {
    .landing-hero {
        padding: 2rem 1rem;
    }
    
    .landing-hero h1 {
        font-size: 2rem;
    }
    
    .landing-hero p {
        font-size: 1rem;
    }
    
    .feature-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .tutorial-step {
        padding: 2rem 1rem;
    }
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
# COMPREHENSIVE UI TRANSLATION DICTIONARY
# ============================================================================
UI_STRINGS = {
    "English": {
        # Sidebar
        "sidebar_title": "CivicShield",
        "sidebar_tagline": "Know Your Rights",
        "select_language": "📍 Select Language:",
        "nav_home": "🏠 Home",
        "nav_translation": "🗣️ Real-Time Translation",
        "nav_documents": "📄 Legal Documents",
        "nav_rights": "📚 Rights Center",
        "nav_quiz": "❓ Rights Quiz",
        "nav_resources": "🏥 Community Resources",
        "nav_nearby": "📍 Rights Near Me",
        "nav_logging": "📝 Encounter Log",
        "nav_emergency": "🚨 Emergency Help",
        "nav_about": "About CivicShield",
        "sidebar_version": "Version 3.0.0",
        "sidebar_purpose": "Professional civil rights protection and legal translation",
        "sidebar_languages": "Supported Languages: 14",
        "sidebar_disclaimer": "⚠️ Legal Disclaimer",
        "sidebar_disclaimer_text": "This app provides educational information, not legal advice. Always consult a qualified attorney for your specific situation.",
        
        # Home/Dashboard
        "home_title": "Welcome to CivicShield",
        "home_subtitle": "Know Your Rights. Protect Yourself. Get Help.",
        "dashboard_intro": "Select a feature below to get started:",
        
        # Feature Cards
        "card_translation_title": "Real-Time Translation",
        "card_translation_desc": "Translate officer statements and get legal advice in your language",
        "card_documents_title": "Legal Document Assistant",
        "card_documents_desc": "Upload documents, extract key information, and translate to your language",
        "card_rights_title": "Rights Education Center",
        "card_rights_desc": "Learn about your constitutional rights and legal protections",
        "card_quiz_title": "Rights Quiz",
        "card_quiz_desc": "Test your knowledge about your rights and civil liberties",
        "card_resources_title": "Community Resources",
        "card_resources_desc": "Find legal aid, emergency services, and support organizations",
        "card_nearby_title": "Rights Near Me",
        "card_nearby_desc": "Find nearby legal aid, courthouses, and community services",
        "card_logging_title": "Encounter Log",
        "card_logging_desc": "Document and track police encounters and incidents",
        "card_emergency_title": "Emergency Assistance",
        "card_emergency_desc": "Access crisis hotlines and emergency procedures",
        
        # Common Buttons
        "btn_open": "Open Feature",
        "btn_delete": "❌",
        "btn_record": "🎤 Record",
        "btn_stop": "⏹️ Stop",
        "btn_translate": "🌐 Translate",
        "btn_listen": "🔊 Listen",
        "btn_download": "📥 Download",
        "btn_search": "🔍 Search",
        "btn_log": "📝 Log",
        "btn_back": "← Back",
        "btn_submit": "✓ Submit",
        "btn_cancel": "✗ Cancel",
        
        # Real-Time Translation Page
        "translation_title": "Real-Time Translation",
        "translation_subtitle": "Translate officer statements and get legal advice",
        "officer_statement": "Officer's Statement (English):",
        "your_rights": "Your Rights & Legal Advice:",
        "record_officer": "🎤 Record Officer's Voice",
        "stop_recording": "⏹️ Stop Recording & Translate",
        "listen_to_advice": "🔊 Listen to Advice",
        "translation_hint": "Enter text or record audio to translate",
        "generating_audio": "Generating audio...",
        "audio_ready": "✅ Audio ready to play",
        "audio_failed": "❌ Audio generation failed",
        "speech_recognized": "Speech captured and converted to text.",
        "mic_unclear": "Could not understand the recorded speech. Please speak clearly and try again.",
        "stt_unavailable": "Speech-to-text service is currently unavailable. Please try again in a moment.",
        "unable_process_audio": "Unable to process recorded audio. Please record again.",
        "mic_recorder_title": "Microphone Recorder",
        "mic_recorder_desc": "Use Start Recording and Stop Recording to capture officer speech.",
        "mic_help": "If your browser blocks microphone access, allow microphone permission and record again.",
        "mic_access_failed": "Microphone access failed. Please allow browser microphone permission and try again.",
        "mic_no_audio": "No audio was captured. Microphone permission may be denied. Allow access and try recording again.",
        "btn_clear_filter": "Clear Filter",
        "currently_filtering": "Currently filtering by",
        "quiz_correct": "✅ Correct!",
        "quiz_incorrect": "❌ Incorrect.",
        "language_selector_error": "❌ Language selector error",
        "demo_section_title": "Demo & Testing",
        "demo_on": "🎬 Demo ON",
        "demo_off": "🎬 Demo OFF",
        "tour_button": "🎓 Tour",
        "tour_complete": "✅ ¡Tour completado! Estás listo para usar CivicShield.",
        "btn_go_home": "🏠 Ir al Inicio",
        "btn_skip_tour": "⏭️ Omitir Tour",
        "btn_next": "Siguiente ➡️",
        "btn_start_using": "🎉 ¡Comenzar!",
        "tour_complete": "✅ Tour Complete! You're ready to use CivicShield.",
        "btn_go_home": "🏠 Go to Home",
        "btn_skip_tour": "⏭️ Skip Tour",
        "btn_next": "Next ➡️",
        "btn_start_using": "🎉 Start Using!",
        
        # Document Assistant Page
        "documents_title": "Legal Document Assistant",
        "documents_subtitle": "Upload documents and extract key information",
        "upload_document": "📤 Upload Document",
        "take_photo": "📸 Take Photo",
        "extract_text": "Extract Text",
        "simplify_text": "Simplify Legal Language",
        "translate_document": "🌐 Translate Document",
        "extract_dates": "📅 Dates Found",
        "extract_deadlines": "⏰ Deadlines",
        "extract_agencies": "🏛️ Government Agencies",
        "extract_actions": "✅ Required Actions",
        "download_report": "📥 Download Report",
        "report_generated": "Report Generated",
        
        # Rights Education
        "rights_title": "Rights Education Center",
        "rights_subtitle": "Learn about your constitutional rights",
        "right_fourth": "Fourth Amendment: Search & Seizure",
        "right_fifth": "Fifth Amendment: Right to Silence",
        "right_sixth": "Sixth Amendment: Right to Attorney",
        "right_traffic": "Traffic Stop Rights",
        "right_arrest": "If You Are Arrested",
        "right_fourth_content": "**Your Right:** You have the right to be free from unreasonable searches and seizures.\n\n**Key Points:**\n- Police generally need a warrant to search your home, car, or personal belongings\n- You can refuse a search by saying: \"I do not consent to a search\"\n- Do NOT physically resist - it could result in additional charges\n- Even if you refuse, police may continue if they have a warrant or probable cause\n\n**What You CAN Do:**\n- Remain silent and ask \"Am I free to go?\"\n- Ask \"Do you have a warrant?\"\n- Keep your hands visible\n- Do not physically obstruct police",
        "right_fifth_content": "**Your Right:** You have the right to remain silent and not incriminate yourself.\n\n**Key Points:**\n- You do NOT have to answer police questions\n- Say clearly: \"I am exercising my right to remain silent\"\n- This right applies even if you haven't been arrested\n- Staying silent cannot be used against you in court\n\n**Important:**\n- You must tell police you are invoking this right - silence alone may not be enough\n- If arrested, ask for a lawyer immediately\n- Do not try to explain yourself or negotiate",
        "right_sixth_content": "**Your Right:** You have the right to an attorney.\n\n**Key Points:**\n- If you cannot afford an attorney, one will be provided\n- You can request an attorney at ANY time during questioning\n- Once you ask for a lawyer, police should stop questioning you\n- You have the right to have your attorney present during questioning\n\n**What to Say:**\n- \"I want to speak to an attorney\"\n- \"I am invoking my right to an attorney\"\n- Then remain silent until your attorney arrives",
        "right_traffic_content": "**During a Traffic Stop:**\n- You must provide your license, registration, and proof of insurance\n- You can ask: \"Am I being detained or am I free to go?\"\n- You do NOT have to consent to a search of your vehicle\n- Say clearly: \"I do not consent to a search\"\n\n**Vehicle Search:**\n- Police can look through windows without permission\n- Police can search your car if they find probable cause\n- They can search without consent if you're arrested\n- You CAN refuse the search, but they may proceed if they have probable cause\n\n**Your Rights:**\n- Keep hands visible\n- Speak calmly and politely\n- Do not physically resist\n- You can film the stop (but don't interfere)",
        "right_arrest_content": "**Important Steps:**\n1. Remain silent - do not answer questions\n2. Say \"I want a lawyer\" clearly\n3. Do not sign anything without your attorney\n4. Do not discuss the case with cellmates or other inmates\n\n**Your Rights Upon Arrest:**\n- You have the right to be informed of charges against you\n- You have the right to a phone call\n- You have the right to remain silent\n- You have the right to an attorney\n\n**What NOT to Do:**\n- Do not resist arrest (even if you believe it's illegal)\n- Do not sign any statements\n- Do not consent to searches\n- Do not make deals with police without a lawyer",
        
        # Community Resources
        "resources_title": "Community Resources",
        "resources_subtitle": "Find legal aid and support services",
        "legal_aid": "Legal Aid Organizations",
        "emergency_services": "Emergency Services",
        "immigration": "Immigration Legal Services",
        "phone": "Phone: ",
        "services": "Services: ",
        "website": "Website: ",
        "hours": "Hours: ",
        
        # Rights Near Me
        "nearby_title": "Rights Near Me",
        "nearby_subtitle": "Find legal aid and services in your area",
        "enter_address": "Enter Your Address:",
        "search_radius": "Search Radius (miles):",
        "nearest_legal_aid": "📋 Nearest Legal Aid Office",
        "nearest_courthouse": "⚖️ Nearest Courthouse",
        "nearest_police": "👮 Nearest Police Station",
        "nearest_translator": "🗣️ Translator Services",
        "nearest_community": "🏢 Community Centers",
        "address": "Address: ",
        "phone_number": "Phone: ",
        "hours_open": "Hours: ",
        "get_directions": "🗺️ Get Directions",
        "not_found": "No results found nearby",
        
        # Encounter Logging
        "logging_title": "Encounter Log",
        "logging_subtitle": "Document police encounters and incidents",
        "encounter_type": "Encounter Type:",
        "encounter_location": "Location:",
        "encounter_details": "Details:",
        "encounter_date": "Date & Time:",
        "officer_info": "Officer Information:",
        "officer_badge": "Badge Number:",
        "officer_agency": "Agency:",
        "encounter_saved": "✅ Encounter logged successfully",
        "view_history": "📋 View Encounter History",
        "total_encounters": "Total Encounters: ",
        "search_encounters": "🔍 Search Encounters",
        
        # Emergency Page
        "emergency_title": "Emergency Assistance",
        "emergency_subtitle": "Crisis Resources & Hotlines",
        "emergency_911": "Emergency (Police, Fire, Medical)",
        "emergency_suicide": "National Suicide Prevention",
        "emergency_domestic": "Domestic Violence Hotline",
        "emergency_assault": "Sexual Assault Support (RAINN)",
        "emergency_poison": "Poison Control",
        "emergency_text": "Crisis Text Line",
        "emergency_procedures": "Emergency Procedures:",
        "procedure_safe": "Stay Safe",
        "procedure_document": "Document Everything",
        "procedure_record": "Record Interactions (where legal)",
        "procedure_call": "Call for Help",
        "procedure_contact": "Contact Your Lawyer",
        
        # Status Messages
        "loading": "Loading...",
        "success": "Success!",
        "error": "Error",
        "warning": "Warning",
        "info": "Information",
        "processing": "Processing...",
        "please_wait": "Please wait...",
        "no_data": "No data available",
        "try_again": "Please try again",
        
        # Accessibility Settings
        "accessibility_title": "♿ Accessibility Settings",
        "text_size": "Text Size:",
        "text_size_normal": "Normal",
        "text_size_large": "Large",
        "text_size_extra_large": "Extra Large",
        "high_contrast": "🎨 High Contrast Mode",
        "high_contrast_on": "High Contrast ON",
        "high_contrast_off": "High Contrast OFF",
        "screen_reader": "Screen Reader Labels Enabled",
        "accessibility_saved": "✅ Accessibility settings saved",
        
        # Document Extraction Enhancements
        "extract_deadlines": "📋 Important Deadlines Found",
        "extract_penalties": "⚠️ Penalties & Warnings",
        "extract_requirements": "✓ Requirements & Actions",
        "deadline_found": "Deadline:",
        "penalty_found": "Penalty:",
        "requirement_found": "Required Action:",
        "document_summary": "📋 Document Summary",
        "summary_generated": "Summary generated successfully",
        
        # Location-Based Resource Finder
        "location_title": "📍 Find Resources Near You",
        "enter_address": "Enter your address or ZIP code:",
        "search_radius_miles": "Search radius (miles):",
        "find_resources": "🔍 Find Nearby Resources",
        "resource_type": "Type of Resource:",
        "all_resources": "All Resources",
        "legal_aid_offices": "Legal Aid Offices",
        "community_centers": "Community Centers",
        "language_services": "Language Services",
        "emergency_shelters": "Emergency Shelters",
        "distance_away": "miles away",
        "get_directions": "🗺️ Get Directions",
        "no_resources_found": "No resources found in this area",
        "resource_hours": "Hours: ",
        "resource_phone": "Phone: ",
        "resource_address": "Address: ",
        "resource_website": "Website: ",
        "loading_resources": "Finding resources near you...",
        
        # Dashboard & Document Assistant
        "saved_deadlines": "⏰ Your Saved Deadlines",
        "upload_legal_doc": "Upload a Legal Document",
        "important_dates": "📅 Important Dates",
        "required_actions": "✓ Required Actions",
        "critical_deadlines": "⏰ Critical Deadlines",
        "penalties_warnings": "⚠️ Penalties & Warnings",
        "extraction_guide": "Document Extraction Guide",
        "demo_mode_active": "📺 **DEMO MODE ACTIVE** - This is sample data for demonstration purposes",
        "have_deadlines": "📋 You have important deadlines to manage!",
        "view_all_deadlines": "📋 View All Deadlines →",
        "from_document": "From:",
        "file_type": "File Type",
        "file_size": "File Size",
        "status_ready": "Ready for extraction",
        "extract_information": "🔍 Extract Information",
        "extracting_info": "Extracting information from document...",
        "no_dates_found": "No dates found",
        "no_deadlines_found": "No deadlines found",
        "no_penalties_found": "No penalties found",
        "download_summary": "📥 Download Summary",
        "download_as_txt": "Download as TXT",
        "save_deadlines_to_dashboard": "💾 Save Deadlines to Dashboard",
        
        # Rights & Quiz
        "know_your_rights_long": "⚖️ Know Your Rights",
        "education_quizzes": "Education, Quizzes & Learning Modules",
        "learn_tab": "📚 Learn",
        "quiz_tab": "🧪 Quiz",
        "rights_education": "Rights Education",
        "select_topic": "Select a topic:",
        "test_knowledge": "Test your knowledge about your civil rights and legal protections.",
        "rights_quiz": "Rights Quiz",
        "can_police_search": "Can police search your car without consent?",
        "only_with_warrant": "Only with a warrant",
        "only_prob_cause": "Only if they have probable cause",
        "both_a_and_b": "Both A and B",
        "never_without": "No, never",
        "police_can_search": "Police can search with a warrant OR if they have probable cause to believe evidence is in the car.",
        "answer_police_q": "Do you have to answer police questions?",
        "yes_always": "Yes, always",
        "right_remain_silent": "No, you have the right to remain silent",
        "only_your_name": "Only your name",
        "only_if_arrested": "Only if arrested",
        "fifth_amendment": "You have the Fifth Amendment right to remain silent and not incriminate yourself.",
        "what_say_arrested": "What should you say if arrested?",
        "explain_what_happened": "Explain what happened",
        "ask_for_lawyer": "Ask for a lawyer",
        "refuse_give_name": "Refuse to give your name",
        "try_negotiate": "Try to negotiate",
        "always_ask_lawyer": "Always ask for a lawyer immediately and remain silent.",
        "check_answer": "✓ Check Answer {number}",
        "question_number": "Question {number}: {question}",
        "select_answer": "Select your answer:",
        "your_score": "Score",
        
        # Community
        "talk_community": "💬 Talk to Your Community",
        "community_intro": "Share experiences, ask questions, give advice - together we are stronger",
        "share_exp_tab": "💭 Share Experiences",
        "ask_q_tab": "❓ Ask Questions",
        "give_advice_tab": "💡 Give Advice",
        "share_your_exp": "💭 Share Your Experience",
        "share_story": "Share your story to help others. All posts are moderated for safety.",
        "title_label": "Title:",
        "exp_placeholder": "e.g., Tips for dealing with traffic stops",
        "your_story": "Your story:",
        "story_placeholder": "Share your experience...",
        "post_anonymously": "Post anonymously",
        "share_exp_btn": "📤 Share Experience",
        "fill_title_content": "⚠️ Please fill in both title and content",
        "exp_shared": "✅ Your experience has been shared! Thank you for helping the community.",
        "ask_community": "❓ Ask the Community",
        "question_help": "Have a question? The community is here to help.",
        "your_question": "Your question:",
        "question_placeholder": "e.g., What are my rights during a traffic stop?",
        "details_label": "Details:",
        "details_placeholder": "Provide more context...",
        "ask_anon": "Ask anonymously",
        "ask_q_btn": "❓ Ask Question",
        "enter_question": "⚠️ Please enter your question",
        "question_posted": "✅ Your question has been posted!",
        "give_advice": "💡 Give Advice",
        "help_others": "Help others with your knowledge and experience.",
        "topic_label": "Topic:",
        "topic_placeholder": "e.g., How to prepare for court",
        "your_advice": "Your advice:",
        "advice_placeholder": "Share what you know...",
        "share_anon": "Share anonymously",
        "share_advice_btn": "💡 Share Advice",
        "share_wisdom": "✅ Thank you for sharing your wisdom!",
        "fill_topic_advice": "⚠️ Please fill in both topic and advice",
        "recent_posts": "📋 Recent Community Posts",
        "no_posts_yet": "💭 No community posts yet. Be the first to share!",
        "posted_recently": "Posted {timestamp}",
        
        # Crisis
        "crisis_hotlines": "🚨 Crisis Resources & Hotlines",
        "crisis_support_24": "24/7 Support When You Need It Most",
        "emergency_hotlines_header": "🆘 Emergency Hotlines",
        "in_immediate_danger": "If you are in immediate danger, call 911",
        "emergency_number": "Emergency",
        "suicide_prevention": "National Suicide Prevention Lifeline",
        "domestic_violence": "National Domestic Violence Hotline",
        "sexual_assault": "RAINN - Sexual Assault Support",
        "poison_control": "Poison Control Center",
        "crisis_text": "Crisis Text Line",
        "safety_procedures": "📋 Safety Procedures",
        "stay_safe": "🛡️ Stay Safe",
        "stay_safe_desc": "Keep yourself safe - do not physically resist. Your safety is the priority.",
        "document_details": "📝 Document Details",
        "document_details_desc": "Remember: officer names, badge numbers, locations, times, what they said and did.",
        "record_safely": "🎥 Record Safely",
        "record_safely_desc": "If safe and legal in your area, record the interaction. Keep the camera visible.",
        "call_for_help": "📞 Call for Help",
        "call_help_desc": "Call 911 if in immediate danger. Stay calm and clear when explaining.",
        "get_legal_help": "⚖️ Get Legal Help",
        "legal_help_desc": "Contact an attorney immediately. Many public defenders offer emergency services.",
        "medical_attention": "🏥 Medical Attention",
        "medical_attention_desc": "If injured, seek medical care and document injuries with photos.",
        "mental_health_support": "🧠 Mental Health & Support",
        "legal_troubles_trauma": "Experiencing legal troubles, police encounters, or discrimination can be traumatic.",
        "mental_health_resources": "Mental health resources:",
        "samhsa_helpline": "SAMHSA National Helpline: 1-800-662-4357 (free, confidential, 24/7)",
        "psychology_directory": "Local therapists: Search Psychology Today's directory",
        "support_groups": "Support groups: NAACP, community centers, legal aid organizations often host support groups",

        # Community, landing, tutorial, and navigation additions
        "author_anonymous": "Anonymous",
        "author_community_member": "Community Member",
        "posted_recently": "Posted",
        "recently": "recently",
        "contact_emergency": "🆘 Emergency / Emergencia",
        "contact_suicide": "🧠 National Suicide Prevention Lifeline",
        "contact_domestic": "💔 National Domestic Violence Hotline",
        "contact_rainn": "🤝 RAINN - Sexual Assault Support",
        "contact_poison": "☠️ Poison Control Center",
        "contact_crisis_text": "📱 Crisis Text Line",
        "contact_crisis_text_number": "Text HOME to 741741",
        "enc_type_traffic_stop": "Traffic Stop",
        "enc_type_street_encounter": "Street Encounter",
        "enc_type_arrest": "Arrest",
        "enc_type_search": "Search",
        "enc_type_other": "Other",
        "encounter_label": "Encounter",
        "unknown": "Unknown",
        "na": "N/A",
        "error_generating_qr": "Error generating QR code",
        "btn_launch_app": "🚀 Launch App",
        "btn_start_demo": "📺 Start Demo",
        "btn_quick_tour": "❓ Quick Tour",
        "share_with_others": "📱 Share with Others",
        "qr_generation_in_progress": "QR code generation in progress...",
        "key_features_label": "Key Features:",
        "btn_previous": "⬅️ Previous",
        "language_change_error": "Language change error",
        "demo_mode_active_sidebar": "✅ Demo Mode Active - Sample data is displayed",
        "screen_reader_off": "🔇 Screen Reader OFF",
        "navigation_title": "Navigation",
        "nav_rights_full": "⚖️ Know Your Rights",
        "nav_resources_near_you": "📍 Resources Near You",
        "nav_logging_full": "📝 Encounter Log",
        "nav_crisis_resources": "🚨 Crisis Resources",
        "nav_community": "💬 Talk to Your Community",
        "sidebar_built_for": "Built for civil rights protection worldwide.",
        "show_landing_page": "🏠 Show Landing Page",
        "landing_hero_html": "<div class=\"landing-hero\"><h1>⚖️ CivicShield Pro</h1><h2>Know Your Rights. Protect Yourself. Get Help.</h2><p>A professional, multi-language platform empowering people to understand and assert their civil rights in real-time encounters.</p></div>",
        "landing_purpose_md": "### 🎯 Purpose\nCivicShield Pro provides judges, advocates, and community members with:\n\n- **Real-time legal translation** in 14 languages\n- **Instant rights information** tailored to your situation\n- **Document analysis** with deadline extraction\n- **Community support** and shared experiences\n- **Crisis resources** available 24/7",
        "landing_features_md": "### ⭐ Key Features\n\n- 🗣️ **Real-Time Translation** - Translate officer statements instantly\n- 📄 **Legal Documents** - Extract key info from court documents\n- ⚖️ **Know Your Rights** - Learn civil rights with interactive quiz\n- 📍 **Resources Near You** - Find legal aid & services by location\n- 📝 **Encounter Log** - Document police interactions\n- 🚨 **Crisis Hotlines** - 24/7 emergency support\n- 💬 **Community Forum** - Share and learn from others",
        "landing_share_md": "**Share CivicShield with judges, advocates, and community members:**\n\n1. Scan the QR code to access the app\n2. No installation needed - works in any browser\n3. Available in 14 languages\n4. Works on desktop, tablet, and mobile",
        "landing_who_should_use_md": "### 👥 Who Should Use CivicShield?\n\n**For Judges & Legal Professionals:**\n- Understand community perspective on civil rights protection\n- Assess whether defendants understand their rights\n- Reference real-time translation capabilities in decisions\n\n**For Advocates & Legal Aid:**\n- Provide clients with multi-language legal information\n- Help clients document encounters\n- Connect community members with resources\n\n**For Educators:**\n- Teach students about civil rights\n- Demonstrate real-world legal scenarios\n- Interactive learning with quizzes\n\n**For Community Members:**\n- Know what to do in a police encounter\n- Access emergency resources instantly\n- Connect with and learn from community experiences",
        "landing_disclaimer_md": "**⚠️ Legal Disclaimer:**\n\nCivicShield Pro provides educational information about civil rights, not legal advice.\nWhile we strive for accuracy, laws vary by jurisdiction and change frequently.\nAlways consult with a qualified attorney for your specific situation.",
        "tutorial_intro_html": "<div class=\"tutorial-container\"><h1>👋 Welcome to CivicShield Pro!</h1><p>Let's take a quick tour to help you get started.</p></div>",
        "tutorial_step1_title": "🏠 Home Dashboard",
        "tutorial_step1_desc": "Your central hub to access all CivicShield features. Each card represents a powerful tool for understanding and protecting your rights.",
        "tutorial_step1_feat1": "Navigate to any feature",
        "tutorial_step1_feat2": "View saved deadlines",
        "tutorial_step1_feat3": "Access crisis resources",
        "tutorial_step2_title": "🗣️ Real-Time Translation",
        "tutorial_step2_desc": "Instantly translate officer statements into 14 languages. Record conversations and get immediate translations to ensure you understand your rights.",
        "tutorial_step2_feat1": "Speech-to-text in any language",
        "tutorial_step2_feat2": "Real-time translation",
        "tutorial_step2_feat3": "Audio playback in your language",
        "tutorial_step3_title": "📄 Legal Documents",
        "tutorial_step3_desc": "Upload court documents, legal notices, or contracts. CivicShield extracts key information and identifies important deadlines.",
        "tutorial_step3_feat1": "Extract deadlines automatically",
        "tutorial_step3_feat2": "Identify penalties",
        "tutorial_step3_feat3": "Get translations",
        "tutorial_step4_title": "⚖️ Know Your Rights",
        "tutorial_step4_desc": "Learn about civil rights with educational content and test your knowledge with interactive quizzes. Available in multiple languages.",
        "tutorial_step4_feat1": "Learn civil rights",
        "tutorial_step4_feat2": "Take interactive quizzes",
        "tutorial_step4_feat3": "Track progress",
        "tutorial_step5_title": "📍 Resources Near You",
        "tutorial_step5_desc": "Find legal aid organizations, community centers, and emergency services near your location. Get directions with one click.",
        "tutorial_step5_feat1": "Search by location",
        "tutorial_step5_feat2": "Browse by category",
        "tutorial_step5_feat3": "Get directions instantly",
        "tutorial_step6_title": "💬 Community Forum",
        "tutorial_step6_desc": "Connect with others, share experiences, ask questions, and get advice from community members. Fully anonymous if you choose.",
        "tutorial_step6_feat1": "Share experiences anonymously",
        "tutorial_step6_feat2": "Ask legal questions",
        "tutorial_step6_feat3": "Give advice",
        "documents_intro_md": "Upload a legal document (image or PDF) to extract key information:\n- Important dates and deadlines\n- Required actions\n- Penalties and warnings\n- Government agencies",
        "document_extraction_tab": "📋 Document Extraction",
        "choose_document": "Choose a document (PDF, JPG, PNG)",
        "file_uploaded": "✅ File uploaded",
        "saved_deadlines_count": "✅ Saved {count} deadline(s) to your dashboard!",
        "no_deadlines_to_save": "⚠️ No deadlines to save",
        "extraction_guide_md": "**This tool can extract:**\n- **Dates**: Court dates, deadlines, filing dates\n- **Deadlines**: \"Must respond by...\", \"Appear on...\"\n- **Actions**: What you need to do\n- **Penalties**: Fines, consequences for non-compliance\n- **Agencies**: Court, government offices mentioned\n\n**Works best with:**\n- ✅ Clear, printed documents\n- ✅ Good lighting and contrast\n- ✅ English language text\n- ✅ High resolution images\n\n**May have issues with:**\n- ❌ Handwritten documents\n- ❌ Very old or damaged documents\n- ❌ Multiple languages mixed\n- ❌ Low quality images",
        "topic_progress": "📖 Topic {current} of {total}",
        "enter_address_placeholder": "Enter address, city, or ZIP code",
        "screen_reader_address_search": "Enter address for resource search",
        "miles_unit": "miles",
        "open_in_google_maps": "Open in Google Maps",
        "opening_maps_to": "Opening maps to",
        
        # Additional UI Labels
        "home_icon": "🏠",
        "translation_icon": "🗣️",
        "document_icon": "📄",
        "rights_icon": "📚",
        "quiz_icon": "❓",
        "resources_icon": "🏥",
        "location_icon": "📍",
        "log_icon": "📝",
        "emergency_icon": "🚨",
        "mic_icon": "🎤",
        "play_icon": "▶️",
        "download_icon": "📥",
        "search_icon": "🔍",
        "close_icon": "✕",
        "check_icon": "✓",
        "alert_icon": "⚠️",
        "info_icon": "ℹ️",
        "success_icon": "✅",
        "error_icon": "❌",
    },
    
    "Spanish / Español": {
        # Sidebar
        "sidebar_title": "CivicShield",
        "sidebar_tagline": "Conoce Tus Derechos",
        "select_language": "📍 Selecciona Idioma:",
        "nav_home": "🏠 Inicio",
        "nav_translation": "🗣️ Traducción en Tiempo Real",
        "nav_documents": "📄 Documentos Legales",
        "nav_rights": "📚 Centro de Derechos",
        "nav_quiz": "❓ Quiz de Derechos",
        "nav_resources": "🏥 Recursos Comunitarios",
        "nav_nearby": "📍 Derechos Cerca de Mí",
        "nav_logging": "📝 Registro de Encuentros",
        "nav_emergency": "🚨 Ayuda de Emergencia",
        "nav_about": "Acerca de CivicShield",
        "sidebar_version": "Versión 3.0.0",
        "sidebar_purpose": "Protección de derechos civiles y traducción legal profesional",
        "sidebar_languages": "Idiomas Soportados: 14",
        "sidebar_disclaimer": "⚠️ Aviso Legal",
        "sidebar_disclaimer_text": "Esta aplicación proporciona información educativa, no asesoramiento legal. Siempre consulte con un abogado calificado para su situación específica.",
        
        # Home/Dashboard
        "home_title": "Bienvenido a CivicShield",
        "home_subtitle": "Conoce Tus Derechos. Protégete. Obtén Ayuda.",
        "dashboard_intro": "Selecciona una característica a continuación para comenzar:",
        
        # Feature Cards
        "card_translation_title": "Traducción en Tiempo Real",
        "card_translation_desc": "Traduce declaraciones de oficiales y obtén asesoramiento legal en tu idioma",
        "card_documents_title": "Asistente de Documentos Legales",
        "card_documents_desc": "Carga documentos, extrae información clave y traduce a tu idioma",
        "card_rights_title": "Centro de Educación de Derechos",
        "card_rights_desc": "Aprende sobre tus derechos constitucionales y protecciones legales",
        "card_quiz_title": "Quiz de Derechos",
        "card_quiz_desc": "Prueba tu conocimiento sobre tus derechos y libertades civiles",
        "card_resources_title": "Recursos Comunitarios",
        "card_resources_desc": "Encuentra ayuda legal, servicios de emergencia y organizaciones de apoyo",
        "card_nearby_title": "Derechos Cerca de Mí",
        "card_nearby_desc": "Encuentra ayuda legal cercana, juzgados y servicios comunitarios",
        "card_logging_title": "Registro de Encuentros",
        "card_logging_desc": "Documenta y registra encuentros policiales e incidentes",
        "card_emergency_title": "Asistencia de Emergencia",
        "card_emergency_desc": "Accede a líneas de crisis y procedimientos de emergencia",
        
        # Common Buttons
        "btn_open": "Abrir Característica",
        "btn_delete": "❌",
        "btn_record": "🎤 Grabar",
        "btn_stop": "⏹️ Detener",
        "btn_translate": "🌐 Traducir",
        "btn_listen": "🔊 Escuchar",
        "btn_download": "📥 Descargar",
        "btn_search": "🔍 Buscar",
        "btn_log": "📝 Registrar",
        "btn_back": "← Atrás",
        "btn_submit": "✓ Enviar",
        "btn_cancel": "✗ Cancelar",
        
        # Real-Time Translation Page
        "translation_title": "Traducción en Tiempo Real",
        "translation_subtitle": "Traduce declaraciones de oficiales y obtén asesoramiento legal",
        "officer_statement": "Declaración del Oficial (Inglés):",
        "your_rights": "Tus Derechos y Asesoramiento Legal:",
        "record_officer": "🎤 Grabar Voz del Oficial",
        "stop_recording": "⏹️ Detener Grabación y Traducir",
        "listen_to_advice": "🔊 Escuchar Consejo",
        "translation_hint": "Ingresa texto o graba audio para traducir",
        "generating_audio": "Generando audio...",
        "audio_ready": "✅ Audio listo para reproducir",
        "audio_failed": "❌ Generación de audio fallida",
        "mic_recorder_title": "Grabadora de Micrófono",
        "mic_recorder_desc": "Use 'Iniciar Grabación' y 'Detener Grabación' para capturar el habla del oficial.",
        "mic_help": "Si tu navegador bloquea el acceso al micrófono, permite el permiso de micrófono y graba de nuevo.",
        "mic_access_failed": "Acceso al micrófono falló. Por favor permite el permiso del micrófono en el navegador e inténtalo de nuevo.",
        "mic_no_audio": "No se capturó audio. Es posible que el permiso del micrófono esté denegado. Permite el acceso e inténtalo de nuevo.",
        "btn_clear_filter": "Borrar Filtro",
        "currently_filtering": "Actualmente filtrando por",
        "quiz_correct": "✅ ¡Correcto!",
        "quiz_incorrect": "❌ Incorrecto.",
        "language_selector_error": "❌ Error del selector de idioma",
        "demo_section_title": "Demo y Pruebas",
        "demo_on": "🎬 Demo ACTIVADA",
        "demo_off": "🎬 Demo DESACTIVADA",
        "tour_button": "🎓 Tour",
        "speech_recognized": "Discurso capturado y convertido a texto.",
        "mic_unclear": "No se pudo entender el discurso grabado. Por favor, hable claramente e inténtelo de nuevo.",
        "stt_unavailable": "El servicio de reconocimiento de voz no está disponible actualmente. Por favor, inténtelo de nuevo en un momento.",
        "unable_process_audio": "No se puede procesar el audio grabado. Por favor, grabe de nuevo.",
        
        # Document Assistant Page
        "documents_title": "Asistente de Documentos Legales",
        "documents_subtitle": "Carga documentos y extrae información clave",
        "upload_document": "📤 Cargar Documento",
        "take_photo": "📸 Tomar Foto",
        "extract_text": "Extraer Texto",
        "simplify_text": "Simplificar Lenguaje Legal",
        "translate_document": "🌐 Traducir Documento",
        "extract_dates": "📅 Fechas Encontradas",
        "extract_deadlines": "⏰ Plazos",
        "extract_agencies": "🏛️ Agencias Gubernamentales",
        "extract_actions": "✅ Acciones Requeridas",
        "download_report": "📥 Descargar Reporte",
        "report_generated": "Reporte Generado",
        
        # Rights Education
        "rights_title": "Centro de Educación de Derechos",
        "rights_subtitle": "Aprende sobre tus derechos constitucionales",
        "right_fourth": "Cuarta Enmienda: Búsqueda e Incautación",
        "right_fifth": "Quinta Enmienda: Derecho al Silencio",
        "right_sixth": "Sexta Enmienda: Derecho a un Abogado",
        "right_traffic": "Derechos en Paradas de Tráfico",
        "right_arrest": "Si Eres Arrestado",
        "right_fourth_content": "**Tu derecho:** Tienes derecho a estar libre de registros e incautaciones irrazonables.\n\n**Puntos clave:**\n- La policía generalmente necesita una orden para registrar tu casa, auto o pertenencias\n- Puedes rechazar un registro diciendo: \"No doy mi consentimiento para un registro\"\n- NO te resistas físicamente: puede generar cargos adicionales\n- Incluso si te niegas, la policía puede continuar si tiene orden o causa probable\n\n**Lo que SÍ puedes hacer:**\n- Guardar silencio y preguntar \"¿Soy libre de irme?\"\n- Preguntar \"¿Tiene una orden?\"\n- Mantener las manos visibles\n- No obstruir físicamente a la policía",
        "right_fifth_content": "**Tu derecho:** Tienes derecho a guardar silencio y no incriminarte.\n\n**Puntos clave:**\n- NO tienes que responder preguntas de la policía\n- Di claramente: \"Estoy ejerciendo mi derecho a guardar silencio\"\n- Este derecho aplica incluso si no has sido arrestado\n- Guardar silencio no puede usarse en tu contra en la corte\n\n**Importante:**\n- Debes informar a la policía que invocas este derecho\n- Si te arrestan, pide un abogado inmediatamente\n- No intentes explicarte ni negociar",
        "right_sixth_content": "**Tu derecho:** Tienes derecho a un abogado.\n\n**Puntos clave:**\n- Si no puedes pagar un abogado, te asignarán uno\n- Puedes solicitar un abogado en CUALQUIER momento durante el interrogatorio\n- Una vez que pidas un abogado, la policía debe detener el interrogatorio\n- Tienes derecho a que tu abogado esté presente durante el interrogatorio\n\n**Qué decir:**\n- \"Quiero hablar con un abogado\"\n- \"Estoy invocando mi derecho a un abogado\"\n- Luego guarda silencio hasta que llegue tu abogado",
        "right_traffic_content": "**Durante una parada de tráfico:**\n- Debes presentar licencia, registro y seguro\n- Puedes preguntar: \"¿Estoy detenido o soy libre de irme?\"\n- NO tienes que consentir el registro de tu vehículo\n- Di claramente: \"No doy mi consentimiento para un registro\"\n\n**Registro del vehículo:**\n- La policía puede mirar por las ventanas sin permiso\n- Puede registrar tu auto si tiene causa probable\n- Puede registrar sin consentimiento si estás arrestado\n- Puedes negarte, pero podrían continuar con causa probable\n\n**Tus derechos:**\n- Mantén las manos visibles\n- Habla con calma y cortesía\n- No te resistas físicamente\n- Puedes grabar la parada (sin interferir)",
        "right_arrest_content": "**Pasos importantes:**\n1. Guarda silencio: no respondas preguntas\n2. Di \"Quiero un abogado\" claramente\n3. No firmes nada sin tu abogado\n4. No hables del caso con otras personas detenidas\n\n**Tus derechos al ser arrestado:**\n- Derecho a ser informado de los cargos\n- Derecho a una llamada telefónica\n- Derecho a guardar silencio\n- Derecho a un abogado\n\n**Qué NO hacer:**\n- No te resistas al arresto\n- No firmes declaraciones\n- No consientas registros\n- No hagas acuerdos con la policía sin abogado",
        
        # Community Resources
        "resources_title": "Recursos Comunitarios",
        "resources_subtitle": "Encuentra ayuda legal y servicios de apoyo",
        "legal_aid": "Organizaciones de Ayuda Legal",
        "emergency_services": "Servicios de Emergencia",
        "immigration": "Servicios Legales de Inmigración",
        "phone": "Teléfono: ",
        "services": "Servicios: ",
        "website": "Sitio Web: ",
        "hours": "Horarios: ",
        
        # Rights Near Me
        "nearby_title": "Derechos Cerca de Mí",
        "nearby_subtitle": "Encuentra ayuda legal y servicios en tu área",
        "enter_address": "Ingresa Tu Dirección:",
        "search_radius": "Radio de Búsqueda (millas):",
        "nearest_legal_aid": "📋 Oficina de Ayuda Legal Más Cercana",
        "nearest_courthouse": "⚖️ Juzgado Más Cercano",
        "nearest_police": "👮 Estación de Policía Más Cercana",
        "nearest_translator": "🗣️ Servicios de Traducción",
        "nearest_community": "🏢 Centros Comunitarios",
        "address": "Dirección: ",
        "phone_number": "Teléfono: ",
        "hours_open": "Horarios: ",
        "get_directions": "🗺️ Obtener Direcciones",
        "not_found": "No se encontraron resultados cercanos",
        
        # Encounter Logging
        "logging_title": "Registro de Encuentros",
        "logging_subtitle": "Documenta encuentros policiales e incidentes",
        "encounter_type": "Tipo de Encuentro:",
        "encounter_location": "Ubicación:",
        "encounter_details": "Detalles:",
        "encounter_date": "Fecha y Hora:",
        "officer_info": "Información del Oficial:",
        "officer_badge": "Número de Insignia:",
        "officer_agency": "Agencia:",
        "encounter_saved": "✅ Encuentro registrado exitosamente",
        "view_history": "📋 Ver Historial de Encuentros",
        "total_encounters": "Encuentros Totales: ",
        "search_encounters": "🔍 Buscar Encuentros",
        
        # Emergency Page
        "emergency_title": "Asistencia de Emergencia",
        "emergency_subtitle": "Recursos de Crisis y Líneas Directas",
        "emergency_911": "Emergencia (Policía, Bomberos, Médico)",
        "emergency_suicide": "Prevención Nacional del Suicidio",
        "emergency_domestic": "Línea Directa de Violencia Doméstica",
        "emergency_assault": "Apoyo para Agresión Sexual (RAINN)",
        "emergency_poison": "Control de Envenenamiento",
        "emergency_text": "Línea de Crisis por Texto",
        "emergency_procedures": "Procedimientos de Emergencia:",
        "procedure_safe": "Mantente Seguro",
        "procedure_document": "Documenta Todo",
        "procedure_record": "Grabar Interacciones (donde sea legal)",
        "procedure_call": "Llamar Pidiendo Ayuda",
        "procedure_contact": "Contacta a Tu Abogado",
        
        # Status Messages
        "loading": "Cargando...",
        "success": "¡Éxito!",
        "error": "Error",
        "warning": "Advertencia",
        "info": "Información",
        "processing": "Procesando...",
        "please_wait": "Por favor espera...",
        "no_data": "Sin datos disponibles",
        "try_again": "Por favor intenta de nuevo",
        
        # Accessibility Settings
        "accessibility_title": "♿ Configuración de Accesibilidad",
        "text_size": "Tamaño de Texto:",
        "text_size_normal": "Normal",
        "text_size_large": "Grande",
        "text_size_extra_large": "Muy Grande",
        "high_contrast": "🎨 Modo de Alto Contraste",
        "high_contrast_on": "Alto Contraste ACTIVADO",
        "high_contrast_off": "Alto Contraste DESACTIVADO",
        "screen_reader": "Etiquetas de Lector de Pantalla Habilitadas",
        "accessibility_saved": "✅ Configuración de accesibilidad guardada",
        
        # Document Extraction Enhancements
        "extract_deadlines": "📋 Plazos Importantes Encontrados",
        "extract_penalties": "⚠️ Multas y Advertencias",
        "extract_requirements": "✓ Requisitos y Acciones",
        "deadline_found": "Plazo:",
        "penalty_found": "Multa:",
        "requirement_found": "Acción Requerida:",
        "document_summary": "📋 Resumen del Documento",
        "summary_generated": "Resumen generado exitosamente",
        
        # Location-Based Resource Finder
        "location_title": "📍 Encontrar Recursos Cerca de Ti",
        "enter_address": "Ingresa tu dirección o código postal:",
        "search_radius_miles": "Radio de búsqueda (millas):",
        "find_resources": "🔍 Encontrar Recursos Cercanos",
        "resource_type": "Tipo de Recurso:",
        "all_resources": "Todos los Recursos",
        "legal_aid_offices": "Oficinas de Ayuda Legal",
        "community_centers": "Centros Comunitarios",
        "language_services": "Servicios de Idiomas",
        "emergency_shelters": "Albergues de Emergencia",
        "distance_away": "a millas de distancia",
        "get_directions": "🗺️ Obtener Direcciones",
        "no_resources_found": "No se encontraron recursos en esta área",
        "resource_hours": "Horarios: ",
        "resource_phone": "Teléfono: ",
        "resource_address": "Dirección: ",
        "resource_website": "Sitio Web: ",
        "loading_resources": "Encontrando recursos cerca de ti...",
        
        # Dashboard & Document Assistant
        "saved_deadlines": "⏰ Tus Plazos Guardados",
        "upload_legal_doc": "Cargar un Documento Legal",
        "important_dates": "📅 Fechas Importantes",
        "required_actions": "✓ Acciones Requeridas",
        "critical_deadlines": "⏰ Plazos Críticos",
        "penalties_warnings": "⚠️ Multas y Advertencias",
        "extraction_guide": "Guía de Extracción de Documentos",
        "demo_mode_active": "📺 **MODO DE DEMOSTRACIÓN ACTIVO** - Estos son datos de muestra para propósitos de demostración",
        "have_deadlines": "📋 ¡Tienes plazos importantes que administrar!",
        "view_all_deadlines": "📋 Ver Todos los Plazos →",
        "from_document": "De:",
        "file_type": "Tipo de Archivo",
        "file_size": "Tamaño del Archivo",
        "status_ready": "Listo para extracción",
        "extract_information": "🔍 Extraer Información",
        "extracting_info": "Extrayendo información del documento...",
        "no_dates_found": "No se encontraron fechas",
        "no_deadlines_found": "No se encontraron plazos",
        "no_penalties_found": "No se encontraron multas",
        "download_summary": "📥 Descargar Resumen",
        "download_as_txt": "Descargar como TXT",
        "save_deadlines_to_dashboard": "💾 Guardar Plazos en el Panel",
        
        # Rights & Quiz
        "know_your_rights_long": "⚖️ Conoce Tus Derechos",
        "education_quizzes": "Educación, Quizzes y Módulos de Aprendizaje",
        "learn_tab": "📚 Aprender",
        "quiz_tab": "🧪 Quiz",
        "rights_education": "Educación de Derechos",
        "select_topic": "Selecciona un tema:",
        "test_knowledge": "Prueba tu conocimiento sobre tus derechos civiles y protecciones legales.",
        "rights_quiz": "Quiz de Derechos",
        "can_police_search": "¿Pueden los policías buscar tu carro sin consentimiento?",
        "only_with_warrant": "Solo con una orden",
        "only_prob_cause": "Solo si tienen causa probable",
        "both_a_and_b": "Ambos A y B",
        "never_without": "No, nunca",
        "police_can_search": "La policía puede hacer una búsqueda con una orden O si tienen causa probable para creer que hay pruebas en el carro.",
        "answer_police_q": "¿Tienes que responder preguntas de la policía?",
        "yes_always": "Sí, siempre",
        "right_remain_silent": "No, tienes derecho a permanecer en silencio",
        "only_your_name": "Solo tu nombre",
        "only_if_arrested": "Solo si eres arrestado",
        "fifth_amendment": "Tienes derecho de la Quinta Enmienda a permanecer en silencio y no auto-incriminarte.",
        "what_say_arrested": "¿Qué deberías decir si eres arrestado?",
        "explain_what_happened": "Explicar lo que sucedió",
        "ask_for_lawyer": "Pedir un abogado",
        "refuse_give_name": "Negarse a dar tu nombre",
        "try_negotiate": "Intentar negociar",
        "always_ask_lawyer": "Siempre pide un abogado inmediatamente y permanece en silencio.",
        "check_answer": "✓ Verificar Respuesta {number}",
        "question_number": "Pregunta {number}: {question}",
        "select_answer": "Selecciona tu respuesta:",
        "your_score": "Tu Puntuación",
        
        # Community
        "talk_community": "💬 Habla con Tu Comunidad",
        "community_intro": "Comparte experiencias, haz preguntas, da consejos - juntos somos más fuertes",
        "share_exp_tab": "💭 Compartir Experiencias",
        "ask_q_tab": "❓ Hacer Preguntas",
        "give_advice_tab": "💡 Dar Consejos",
        "share_your_exp": "💭 Comparte Tu Experiencia",
        "share_story": "Comparte tu historia para ayudar a otros. Todos los posts son moderados por seguridad.",
        "title_label": "Título:",
        "exp_placeholder": "p.ej., Consejos para lidiar con paradas de tráfico",
        "your_story": "Tu historia:",
        "story_placeholder": "Comparte tu experiencia...",
        "post_anonymously": "Publicar anónimamente",
        "share_exp_btn": "📤 Compartir Experiencia",
        "fill_title_content": "⚠️ Por favor completa el título y el contenido",
        "exp_shared": "✅ ¡Tu experiencia ha sido compartida! Gracias por ayudar a la comunidad.",
        "ask_community": "❓ Pregunta a la Comunidad",
        "question_help": "¿Tienes una pregunta? La comunidad está aquí para ayudar.",
        "your_question": "Tu pregunta:",
        "question_placeholder": "p.ej., ¿Cuáles son mis derechos durante una parada de tráfico?",
        "details_label": "Detalles:",
        "details_placeholder": "Proporciona más contexto...",
        "ask_anon": "Preguntar anónimamente",
        "ask_q_btn": "❓ Hacer Pregunta",
        "enter_question": "⚠️ Por favor ingresa tu pregunta",
        "question_posted": "✅ ¡Tu pregunta ha sido publicada!",
        "give_advice": "💡 Dar Consejos",
        "help_others": "Ayuda a otros con tu conocimiento y experiencia.",
        "topic_label": "Tema:",
        "topic_placeholder": "p.ej., Cómo prepararse para la corte",
        "your_advice": "Tu consejo:",
        "advice_placeholder": "Comparte lo que sabes...",
        "share_anon": "Compartir anónimamente",
        "share_advice_btn": "💡 Compartir Consejo",
        "share_wisdom": "✅ ¡Gracias por compartir tu sabiduría!",
        "fill_topic_advice": "⚠️ Por favor completa el tema y el consejo",
        "recent_posts": "📋 Posts Recientes de la Comunidad",
        "no_posts_yet": "💭 Aún no hay posts de la comunidad. ¡Sé el primero en compartir!",
        "posted_recently": "Publicado {timestamp}",
        
        # Crisis
        "crisis_hotlines": "🚨 Recursos de Crisis y Líneas Directas",
        "crisis_support_24": "Apoyo 24/7 Cuando Lo Necesites",
        "emergency_hotlines_header": "🆘 Líneas Directas de Emergencia",
        "in_immediate_danger": "Si estás en peligro inmediato, llama al 911",
        "emergency_number": "Emergencia",
        "suicide_prevention": "Línea Nacional de Prevención del Suicidio",
        "domestic_violence": "Línea Directa de Violencia Doméstica Nacional",
        "sexual_assault": "RAINN - Apoyo para Agresión Sexual",
        "poison_control": "Centro de Control de Envenenamiento",
        "crisis_text": "Línea de Crisis por Texto",
        "safety_procedures": "📋 Procedimientos de Seguridad",
        "stay_safe": "🛡️ Mantente Seguro",
        "stay_safe_desc": "Mantente seguro - no resistas físicamente. Tu seguridad es la prioridad.",
        "document_details": "📝 Documentar Detalles",
        "document_details_desc": "Recuerda: nombres de oficiales, números de insignia, ubicaciones, horas, qué dijeron e hicieron.",
        "record_safely": "🎥 Grabar de Forma Segura",
        "record_safely_desc": "Si es seguro y legal en tu área, graba la interacción. Mantén la cámara visible.",
        "call_for_help": "📞 Llamar Pidiendo Ayuda",
        "call_help_desc": "Llama al 911 si estás en peligro inmediato. Mantente tranquilo y claro al explicar.",
        "get_legal_help": "⚖️ Obtener Ayuda Legal",
        "legal_help_desc": "Contacta a un abogado inmediatamente. Muchos defensores públicos ofrecen servicios de emergencia.",
        "medical_attention": "🏥 Atención Médica",
        "medical_attention_desc": "Si estás lesionado, busca atención médica y documenta las lesiones con fotos.",
        "mental_health_support": "🧠 Apoyo de Salud Mental",
        "legal_troubles_trauma": "Experimentar problemas legales, encuentros policiales o discriminación puede ser traumático.",
        "mental_health_resources": "Recursos de salud mental:",
        "samhsa_helpline": "Línea de Ayuda Nacional SAMHSA: 1-800-662-4357 (gratis, confidencial, 24/7)",
        "psychology_directory": "Terapeutas locales: Busca en el directorio de Psychology Today",
        "support_groups": "Grupos de apoyo: NAACP, centros comunitarios, organizaciones de ayuda legal a menudo ofrecen grupos de apoyo",
        "author_anonymous": "Anónimo",
        "author_community_member": "Miembro de la comunidad",
        "posted_recently": "Publicado",
        "recently": "recientemente",
        "contact_emergency": "🆘 Emergencia / Emergency",
        "contact_suicide": "🧠 Línea Nacional de Prevención del Suicidio",
        "contact_domestic": "💔 Línea Nacional de Violencia Doméstica",
        "contact_rainn": "🤝 RAINN - Apoyo para Agresión Sexual",
        "contact_poison": "☠️ Centro de Control de Envenenamiento",
        "contact_crisis_text": "📱 Línea de Crisis por Texto",
        "contact_crisis_text_number": "Envía HOME al 741741",
        "enc_type_traffic_stop": "Parada de tráfico",
        "enc_type_street_encounter": "Encuentro en la calle",
        "enc_type_arrest": "Arresto",
        "enc_type_search": "Registro",
        "enc_type_other": "Otro",
        "encounter_label": "Encuentro",
        "unknown": "Desconocido",
        "na": "N/D",
        "error_generating_qr": "Error al generar código QR",
        "btn_launch_app": "🚀 Iniciar App",
        "btn_start_demo": "📺 Iniciar Demo",
        "btn_quick_tour": "❓ Tour Rápido",
        "share_with_others": "📱 Compartir con otros",
        "qr_generation_in_progress": "Generación de código QR en progreso...",
        "key_features_label": "Funciones clave:",
        "btn_previous": "⬅️ Anterior",
        "language_change_error": "Error al cambiar idioma",
        "demo_mode_active_sidebar": "✅ Modo demo activo - se muestran datos de ejemplo",
        "screen_reader_off": "🔇 Lector de pantalla DESACTIVADO",
        "navigation_title": "Navegación",
        "nav_rights_full": "⚖️ Conoce Tus Derechos",
        "nav_resources_near_you": "📍 Recursos Cerca de Ti",
        "nav_logging_full": "📝 Registro de Encuentros",
        "nav_crisis_resources": "🚨 Recursos de Crisis",
        "nav_community": "💬 Habla con tu comunidad",
        "sidebar_built_for": "Creado para la protección de derechos civiles en todo el mundo.",
        "show_landing_page": "🏠 Mostrar página de inicio",
        "landing_hero_html": "<div class=\"landing-hero\"><h1>⚖️ CivicShield Pro</h1><h2>Conoce tus derechos. Protégete. Obtén ayuda.</h2><p>Una plataforma profesional y multilingüe para ayudar a las personas a comprender y hacer valer sus derechos civiles en encuentros en tiempo real.</p></div>",
        "landing_purpose_md": "### 🎯 Propósito\nCivicShield Pro ofrece a jueces, defensores y miembros de la comunidad:\n\n- **Traducción legal en tiempo real** en 14 idiomas\n- **Información inmediata de derechos** según tu situación\n- **Análisis de documentos** con extracción de plazos\n- **Apoyo comunitario** y experiencias compartidas\n- **Recursos de crisis** disponibles 24/7",
        "landing_features_md": "### ⭐ Funciones clave\n\n- 🗣️ **Traducción en tiempo real** - Traduce declaraciones de oficiales al instante\n- 📄 **Documentos legales** - Extrae información clave de documentos judiciales\n- ⚖️ **Conoce tus derechos** - Aprende derechos civiles con quiz interactivo\n- 📍 **Recursos cerca de ti** - Encuentra ayuda legal y servicios por ubicación\n- 📝 **Registro de encuentros** - Documenta interacciones policiales\n- 🚨 **Líneas de crisis** - Soporte de emergencia 24/7\n- 💬 **Foro comunitario** - Comparte y aprende de otros",
        "landing_share_md": "**Comparte CivicShield con jueces, defensores y miembros de la comunidad:**\n\n1. Escanea el código QR para acceder a la app\n2. No requiere instalación - funciona en cualquier navegador\n3. Disponible en 14 idiomas\n4. Funciona en escritorio, tablet y móvil",
        "landing_who_should_use_md": "### 👥 ¿Quién debería usar CivicShield?\n\n**Para jueces y profesionales legales:**\n- Comprender la perspectiva comunitaria sobre protección de derechos civiles\n- Evaluar si los acusados entienden sus derechos\n- Referenciar capacidades de traducción en tiempo real en decisiones\n\n**Para defensores y ayuda legal:**\n- Brindar información legal multilingüe a clientes\n- Ayudar a documentar encuentros\n- Conectar miembros de la comunidad con recursos\n\n**Para educadores:**\n- Enseñar derechos civiles\n- Demostrar escenarios legales del mundo real\n- Aprendizaje interactivo con quizzes\n\n**Para miembros de la comunidad:**\n- Saber qué hacer en un encuentro policial\n- Acceder a recursos de emergencia al instante\n- Conectarse y aprender de experiencias comunitarias",
        "landing_disclaimer_md": "**⚠️ Aviso legal:**\n\nCivicShield Pro proporciona información educativa sobre derechos civiles, no asesoría legal.\nAunque buscamos precisión, las leyes varían por jurisdicción y cambian con frecuencia.\nConsulta siempre con un abogado calificado para tu situación específica.",
        "tutorial_intro_html": "<div class=\"tutorial-container\"><h1>👋 ¡Bienvenido a CivicShield Pro!</h1><p>Hagamos un tour rápido para ayudarte a comenzar.</p></div>",
        "tutorial_step1_title": "🏠 Panel principal",
        "tutorial_step1_desc": "Tu centro principal para acceder a todas las funciones de CivicShield. Cada tarjeta representa una herramienta para comprender y proteger tus derechos.",
        "tutorial_step1_feat1": "Navegar a cualquier función",
        "tutorial_step1_feat2": "Ver plazos guardados",
        "tutorial_step1_feat3": "Acceder a recursos de crisis",
        "tutorial_step2_title": "🗣️ Traducción en tiempo real",
        "tutorial_step2_desc": "Traduce instantáneamente declaraciones de oficiales en 14 idiomas. Graba conversaciones y obtén traducciones inmediatas para entender tus derechos.",
        "tutorial_step2_feat1": "Voz a texto en cualquier idioma",
        "tutorial_step2_feat2": "Traducción en tiempo real",
        "tutorial_step2_feat3": "Audio en tu idioma",
        "tutorial_step3_title": "📄 Documentos legales",
        "tutorial_step3_desc": "Sube documentos judiciales, avisos legales o contratos. CivicShield extrae información clave e identifica plazos importantes.",
        "tutorial_step3_feat1": "Extraer plazos automáticamente",
        "tutorial_step3_feat2": "Identificar penalizaciones",
        "tutorial_step3_feat3": "Obtener traducciones",
        "tutorial_step4_title": "⚖️ Conoce tus derechos",
        "tutorial_step4_desc": "Aprende sobre derechos civiles con contenido educativo y prueba tus conocimientos con quizzes interactivos.",
        "tutorial_step4_feat1": "Aprender derechos civiles",
        "tutorial_step4_feat2": "Tomar quizzes interactivos",
        "tutorial_step4_feat3": "Seguir progreso",
        "tutorial_step5_title": "📍 Recursos cerca de ti",
        "tutorial_step5_desc": "Encuentra organizaciones de ayuda legal, centros comunitarios y servicios de emergencia cerca de tu ubicación.",
        "tutorial_step5_feat1": "Buscar por ubicación",
        "tutorial_step5_feat2": "Explorar por categoría",
        "tutorial_step5_feat3": "Obtener direcciones al instante",
        "tutorial_step6_title": "💬 Foro comunitario",
        "tutorial_step6_desc": "Conéctate con otras personas, comparte experiencias, haz preguntas y recibe consejos de la comunidad.",
        "tutorial_step6_feat1": "Compartir experiencias anónimas",
        "tutorial_step6_feat2": "Hacer preguntas legales",
        "tutorial_step6_feat3": "Dar consejos",
        "documents_intro_md": "Sube un documento legal (imagen o PDF) para extraer información clave:\n- Fechas y plazos importantes\n- Acciones requeridas\n- Penalizaciones y advertencias\n- Agencias gubernamentales",
        "document_extraction_tab": "📋 Extracción de Documento",
        "choose_document": "Elige un documento (PDF, JPG, PNG)",
        "file_uploaded": "✅ Archivo subido",
        "saved_deadlines_count": "✅ ¡Guardados {count} plazo(s) en tu panel!",
        "no_deadlines_to_save": "⚠️ No hay plazos para guardar",
        "extraction_guide_md": "**Esta herramienta puede extraer:**\n- **Fechas**: fechas de corte, plazos, fechas de presentación\n- **Plazos**: \"Debe responder antes de...\", \"Comparecer el...\"\n- **Acciones**: lo que debes hacer\n- **Penalizaciones**: multas, consecuencias por incumplimiento\n- **Agencias**: tribunales, oficinas gubernamentales mencionadas\n\n**Funciona mejor con:**\n- ✅ Documentos impresos y claros\n- ✅ Buena iluminación y contraste\n- ✅ Texto en inglés\n- ✅ Imágenes de alta resolución\n\n**Puede tener problemas con:**\n- ❌ Documentos manuscritos\n- ❌ Documentos muy antiguos o dañados\n- ❌ Múltiples idiomas mezclados\n- ❌ Imágenes de baja calidad",
        "topic_progress": "📖 Tema {current} de {total}",
        "enter_address_placeholder": "Ingresa dirección, ciudad o código postal",
        "screen_reader_address_search": "Ingresa dirección para buscar recursos",
        "miles_unit": "millas",
        "open_in_google_maps": "Abrir en Google Maps",
        "opening_maps_to": "Abriendo mapas a",
        
        # Additional UI Labels
        "home_icon": "🏠",
        "translation_icon": "🗣️",
        "document_icon": "📄",
        "rights_icon": "📚",
        "quiz_icon": "❓",
        "resources_icon": "🏥",
        "location_icon": "📍",
        "log_icon": "📝",
        "emergency_icon": "🚨",
        "mic_icon": "🎤",
        "play_icon": "▶️",
        "download_icon": "📥",
        "search_icon": "🔍",
        "close_icon": "✕",
        "check_icon": "✓",
        "alert_icon": "⚠️",
        "info_icon": "ℹ️",
        "success_icon": "✅",
        "error_icon": "❌",
    },

    "Cantonese / 粵語": {
        # Sidebar
        "sidebar_title": "CivicShield",
        "sidebar_tagline": "了解您的權利",
        "select_language": "📍 選擇語言：",
        "nav_home": "🏠 主頁",
        "nav_translation": "🗣️ 實時翻譯",
        "nav_documents": "📄 法律文件",
        "nav_rights": "📚 權利中心",
        "nav_quiz": "❓ 權利測驗",
        "nav_resources": "🏥 社區資源",
        "nav_nearby": "📍 附近的權利",
        "nav_logging": "📝 遭遇記錄",
        "nav_emergency": "🚨 緊急協助",
        "nav_about": "關於 CivicShield",
        "sidebar_version": "版本 3.0.0",
        "sidebar_purpose": "專業民權保護及法律翻譯",
        "sidebar_languages": "支援語言：14",
        "sidebar_disclaimer": "⚠️ 法律免責聲明",
        "sidebar_disclaimer_text": "此應用程式提供教育性資訊，並非法律建議。請就您的具體情況諮詢合格律師。",

        # Home/Dashboard
        "home_title": "歡迎使用 CivicShield",
        "home_subtitle": "了解您的權利。保護自己。獲得幫助。",
        "dashboard_intro": "選擇以下功能以開始：",

        # Feature Cards
        "card_translation_title": "實時翻譯",
        "card_translation_desc": "翻譯警察陳述並以您的語言獲取法律建議",
        "card_documents_title": "法律文件助理",
        "card_documents_desc": "上傳文件、提取關鍵資訊並翻譯成您的語言",
        "card_rights_title": "權利教育中心",
        "card_rights_desc": "了解您的憲法權利和法律保護",
        "card_quiz_title": "權利測驗",
        "card_quiz_desc": "測試您對自身權利和公民自由的認識",
        "card_resources_title": "社區資源",
        "card_resources_desc": "尋找法律援助、緊急服務和支持機構",
        "card_nearby_title": "附近的權利",
        "card_nearby_desc": "尋找附近的法律援助、法院和社區服務",
        "card_logging_title": "遭遇記錄",
        "card_logging_desc": "記錄和追蹤警察遭遇及事件",
        "card_emergency_title": "緊急協助",
        "card_emergency_desc": "獲取危機熱線和緊急程序",

        # Common Buttons
        "btn_open": "開啟功能",
        "btn_delete": "❌",
        "btn_record": "🎤 錄音",
        "btn_stop": "⏹️ 停止",
        "btn_translate": "🌐 翻譯",
        "btn_listen": "🔊 聆聽",
        "btn_download": "📥 下載",
        "btn_search": "🔍 搜索",
        "btn_log": "📝 記錄",
        "btn_back": "← 返回",
        "btn_submit": "✓ 提交",
        "btn_cancel": "✗ 取消",

        # Real-Time Translation Page (keys 50–100)
        "translation_title":    "實時翻譯",
        "translation_subtitle": "翻譯警察陳述並獲取法律建議",
        "officer_statement":    "警察陳述（英語）：",
        "your_rights":          "您的權利及法律建議：",
        "record_officer":       "🎤 錄製警察聲音",
        "stop_recording":       "⏹️ 停止錄音並翻譯",
        "listen_to_advice":     "🔊 聆聽建議",
        "translation_hint":     "輸入文字或錄製音頻以翻譯",
        "generating_audio":     "正在生成音頻...",
        "audio_ready":          "✅ 音頻已準備好播放",
        "audio_failed":         "❌ 音頻生成失敗",
        "speech_recognized":    "已捕獲語音並轉換為文字。",
        "mic_unclear":          "無法理解錄製的語音。請清晰說話並再試。",
        "stt_unavailable":      "語音轉文字服務目前不可用。請稍後再試。",
        "unable_process_audio": "無法處理錄製的音頻。請重新錄製。",
        "mic_recorder_title":   "麥克風錄音機",
        "mic_recorder_desc":    "使用「開始錄音」和「停止錄音」來捕捉警察的語音。",
        "mic_help":             "如果您的瀏覽器阻止了麥克風訪問，請允許麥克風權限後重新錄音。",
        "mic_access_failed":    "麥克風訪問失敗。請允許瀏覽器麥克風權限後再試。",
        "mic_no_audio":         "未捕獲到音頻。麥克風權限可能被拒絕。請允許訪問並重新嘗試錄音。",
        "btn_clear_filter":     "清除過濾器",
        "currently_filtering":  "目前按以下條件過濾",
        "quiz_correct":         "✅ 正確！",
        "quiz_incorrect":       "❌ 錯誤。",
        "language_selector_error": "❌ 語言選擇器錯誤",
        "demo_section_title":   "演示和測試",
        "demo_on":              "🎬 演示開啟",
        "demo_off":             "🎬 演示關閉",
        "tour_button":          "🎓 導覽",
        "tour_complete":        "✅ 導覽完成！您可以開始使用 CivicShield。",
        "btn_go_home":          "🏠 返回主頁",
        "btn_skip_tour":        "⏭️ 跳過導覽",
        "btn_next":             "下一步 ➡️",
        "btn_start_using":      "🎉 開始使用！",

        # Document Assistant Page (keys 84–96)
        "documents_title":      "法律文件助理",
        "documents_subtitle":   "上傳文件並提取關鍵資訊",
        "upload_document":      "📤 上傳文件",
        "take_photo":           "📸 拍照",
        "extract_text":         "提取文字",
        "simplify_text":        "簡化法律語言",
        "translate_document":   "🌐 翻譯文件",
        "extract_dates":        "📅 找到的日期",
        "extract_deadlines":    "⏰ 截止日期",
        "extract_agencies":     "🏛️ 政府機構",
        "extract_actions":      "✅ 所需行動",
        "download_report":      "📥 下載報告",
        "report_generated":     "報告已生成",

        # Rights Education (keys 97–100)
        "rights_title":    "權利教育中心",
        "rights_subtitle": "了解您的憲法權利",
        "right_fourth":    "第四修正案：搜查與扣押",
        "right_fifth":     "第五修正案：緘默權",
    },
}

# Ensure all 14 languages exist and include all keys.
for lang_name in LANGUAGE_MAP.keys():
    if lang_name not in UI_STRINGS:
        UI_STRINGS[lang_name] = copy.deepcopy(UI_STRINGS["English"])
    for key, value in UI_STRINGS["English"].items():
        UI_STRINGS[lang_name].setdefault(key, value)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
def init_session_state():
    """Initialize all session state variables on first run."""
    if "page" not in st.session_state:
        st.session_state.page = "Landing"  # Show landing page first
    if "language" not in st.session_state:
        st.session_state.language = st.session_state.get("selected_language", "English")
    if "encounter_log" not in st.session_state:
        st.session_state.encounter_log = load_encounters()
    if "emergency_activated" not in st.session_state:
        st.session_state.emergency_activated = False
    if "translation_history" not in st.session_state:
        st.session_state.translation_history = []
    
    # Accessibility settings
    if "text_size" not in st.session_state:
        st.session_state.text_size = "normal"
    if "high_contrast" not in st.session_state:
        st.session_state.high_contrast = False
    if "screen_reader_enabled" not in st.session_state:
        st.session_state.screen_reader_enabled = True
    
    # New features: saved deadlines and community discussion
    if "saved_deadlines" not in st.session_state:
        st.session_state.saved_deadlines = load_saved_deadlines()
    if "community_posts" not in st.session_state:
        st.session_state.community_posts = load_community_posts()
    if "resource_category_filter" not in st.session_state:
        st.session_state.resource_category_filter = None
    
    # Public deployment features
    if "first_time_user" not in st.session_state:
        st.session_state.first_time_user = True
    if "demo_mode" not in st.session_state:
        st.session_state.demo_mode = False
    if "tutorial_step" not in st.session_state:
        st.session_state.tutorial_step = 0
    if "skip_landing" not in st.session_state:
        st.session_state.skip_landing = False

# ============================================================================
# UTILITY FUNCTION - GET TRANSLATED STRING
# ============================================================================
def t(key: str) -> str:
    """
    Get translated text in selected language.
    Example: st.markdown(t('translation_title'))
    Safe fallback to English if language not available or session not initialized.
    """
    try:
        lang = st.session_state.get("language", st.session_state.get("selected_language", "English"))
    except:
        lang = "English"
    
    # Ensure language is valid
    if lang not in UI_STRINGS:
        lang = "English"
    
    # Get translation from UI_STRINGS
    translation = UI_STRINGS.get(lang, {}).get(key)
    
    # Fallback to English if translation not found
    if translation is None:
        translation = UI_STRINGS.get("English", {}).get(key, key)
    
    return translation

# ============================================================================
# ACCESSIBILITY FUNCTIONS
# ============================================================================
def apply_accessibility_css():
    """Apply accessibility CSS based on user settings."""
    css_classes = ""
    if st.session_state.text_size == "large":
        css_classes += "large-text "
    elif st.session_state.text_size == "extra_large":
        css_classes += "large-text "  # Can extend for extra size
    
    if st.session_state.high_contrast:
        css_classes += "high-contrast"
    
    if css_classes:
        st.markdown(f'<div class="{css_classes}">', unsafe_allow_html=True)
        return True
    return False

def close_accessibility_div():
    """Close the accessibility CSS div."""
    st.markdown('</div>', unsafe_allow_html=True)

def add_screen_reader_label(label: str):
    """Add screen reader accessible label (hidden for sighted users)."""
    if st.session_state.screen_reader_enabled:
        st.markdown(f'<span style="display:none;" role="status" aria-label="{label}"></span>', unsafe_allow_html=True)

# ============================================================================
# LOCATION-BASED RESOURCE FINDER
# ============================================================================
def find_resources_by_location(address: str, search_radius_miles: int = 5) -> list:
    """
    Find nearby resources based on address.
    
    This is a simplified mock implementation using hardcoded coordinates.
    For production, integrate with Google Maps API or geolocation service.
    """
    # Mock locations (in production, use Geocoding API)
    RESOURCES_DB = [
        {
            "name": "California Rural Legal Assistance (CRLA)",
            "category": "Legal Aid",
            "address": "123 Main St, San Francisco, CA 94102",
            "phone": "1-833-435-2752",
            "website": "crla.org",
            "hours": "9AM - 5PM Mon-Fri",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "distance": 2.5
        },
        {
            "name": "Community Legal Services Center",
            "category": "Legal Aid",
            "address": "456 Oak Ave, San Francisco, CA 94103",
            "phone": "(415) 701-1000",
            "website": "legalaid.org",
            "hours": "8AM - 6PM Mon-Sat",
            "latitude": 37.7750,
            "longitude": -122.4185,
            "distance": 2.8
        },
        {
            "name": "Immigrant Rights Center",
            "category": "Immigration Support",
            "address": "789 Pine St, San Francisco, CA 94104",
            "phone": "1-888-624-4747",
            "website": "immigrationrights.org",
            "hours": "10AM - 4PM Daily",
            "latitude": 37.7951,
            "longitude": -122.3975,
            "distance": 3.2
        },
        {
            "name": "Community Health & Resources",
            "category": "Community Center",
            "address": "321 Elm Way, San Francisco, CA 94105",
            "phone": "(415) 555-0123",
            "website": "communitycenter.org",
            "hours": "9AM - 9PM Daily",
            "latitude": 37.7849,
            "longitude": -122.2864,
            "distance": 4.1
        },
        {
            "name": "Multi-Language Translation Services",
            "category": "Language Services",
            "address": "654 Maple Rd, San Francisco, CA 94106",
            "phone": "1-800-827-7223",
            "website": "translationservices.org",
            "hours": "8AM - 8PM Daily",
            "latitude": 37.7749,
            "longitude": -122.3967,
            "distance": 1.8
        }
    ]
    
    # Mock: filter resources within search radius
    nearby_resources = [r for r in RESOURCES_DB if r["distance"] <= search_radius_miles]
    return sorted(nearby_resources, key=lambda x: x["distance"])

def extract_deadline_and_dates(text: str) -> dict:
    """
    Extract deadlines and important dates from legal text.
    Uses pattern matching for common legal date formats.
    """
    import re
    from datetime import datetime
    
    results = {
        "dates": [],
        "deadlines": [],
        "penalties": []
    }
    
    # Date patterns: MM/DD/YYYY, DD/MM/YYYY, Month DD, YYYY
    date_patterns = [
        r'\d{1,2}/\d{1,2}/\d{4}',
        r'\d{1,2}-\d{1,2}-\d{4}',
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        results["dates"].extend(matches)
    
    # Deadline keywords
    deadline_keywords = [
        r'must\s+(?:respond|reply|appear|pay|submit)(?:\s+(?:by|before|on|within))?.*?(?::\s*)([^.;,]*)',
        r'(?:deadline|due\s+date)(?:\s+is)?(?:\s+)?([^.;,]*)',
        r'respond\s+(?:by|within|before).*?(?::\s*)([^.;,]*)'
    ]
    
    for pattern in deadline_keywords:
        matches = re.findall(pattern, text, re.IGNORECASE)
        results["deadlines"].extend(matches)
    
    # Penalty keywords
    penalty_keywords = [
        r'(?:penalty|fine|multa|penalidad)(?:\s+of)?(?:\s+\$)?([^.;,]*)',
        r'(?:if\s+(?:you|not|fail))[^.]*?(?:penalty|fine|consequence).*?([^.;,]*)',
    ]
    
    for pattern in penalty_keywords:
        matches = re.findall(pattern, text, re.IGNORECASE)
        results["penalties"].extend(matches)
    
    # Remove duplicates and clean up
    results["dates"] = list(set(results["dates"]))
    results["deadlines"] = list(set([d.strip() for d in results["deadlines"] if d.strip()]))
    results["penalties"] = list(set([p.strip() for p in results["penalties"] if p.strip()]))
    
    return results

# ============================================================================
# PERSISTENT STORAGE FUNCTIONS
# ============================================================================
ENCOUNTER_FILE = "encounters.json"
DEADLINES_FILE = "saved_deadlines.json"
COMMUNITY_POSTS_FILE = "community_posts.json"

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

def load_saved_deadlines():
    """Load all saved deadlines from persistent storage."""
    if os.path.exists(DEADLINES_FILE):
        try:
            with open(DEADLINES_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_deadline(deadline_data):
    """Save new deadline to persistent storage."""
    deadlines = load_saved_deadlines()
    deadline_data["saved_timestamp"] = datetime.now().isoformat()
    deadline_data["id"] = len(deadlines) + 1
    deadlines.append(deadline_data)
    with open(DEADLINES_FILE, "w") as f:
        json.dump(deadlines, f, indent=2)
    st.session_state.saved_deadlines = deadlines
    return deadline_data

def delete_deadline(deadline_id):
    """Delete a saved deadline."""
    deadlines = load_saved_deadlines()
    deadlines = [d for d in deadlines if d.get("id") != deadline_id]
    with open(DEADLINES_FILE, "w") as f:
        json.dump(deadlines, f, indent=2)
    st.session_state.saved_deadlines = deadlines

def load_community_posts():
    """Load all community discussion posts from persistent storage."""
    if os.path.exists(COMMUNITY_POSTS_FILE):
        try:
            with open(COMMUNITY_POSTS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_community_post(post_data):
    """Save new community post to persistent storage."""
    posts = load_community_posts()
    post_data["timestamp"] = datetime.now().isoformat()
    post_data["id"] = len(posts) + 1
    posts.append(post_data)
    with open(COMMUNITY_POSTS_FILE, "w") as f:
        json.dump(posts, f, indent=2)
    st.session_state.community_posts = posts
    return post_data

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
    try:
        return GoogleTranslator(source=source_lang, target=target_lang)
    except:
        return None

# ============================================================================
# RIGHTS EDUCATION CONTENT (ENGLISH VERSION)
# ============================================================================
RIGHTS_EDUCATION = {
    "Fourth Amendment": {
        "title_key": "right_fourth",
        "content_key": "right_fourth_content"
    },
    "Fifth Amendment": {
        "title_key": "right_fifth",
        "content_key": "right_fifth_content"
    },
    "Sixth Amendment": {
        "title_key": "right_sixth",
        "content_key": "right_sixth_content"
    },
    "Traffic Stops": {
        "title_key": "right_traffic",
        "content_key": "right_traffic_content"
    },
    "Arrest": {
        "title_key": "right_arrest",
        "content_key": "right_arrest_content"
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
# PAGE FUNCTIONS
# ============================================================================

def page_home():
    """Dashboard home page with feature cards and saved deadlines."""
    
    # Load demo data if demo mode is active
    if st.session_state.demo_mode:
        demo_data = get_demo_data()
        st.session_state.saved_deadlines = demo_data["saved_deadlines"]
        st.session_state.community_posts = demo_data["community_posts"]
        st.session_state.encounter_log = demo_data["encounter_log"]
        
        # Show demo mode indicator
        st.info(t('demo_mode_active'))
    
    st.markdown(f"# 🏠 {t('home_title')}")
    st.markdown(f"## {t('home_subtitle')}")
    st.markdown("---")
    
    # Show saved deadlines section (NEW)
    if st.session_state.saved_deadlines:
        st.markdown(f"## {t('saved_deadlines')}")
        st.warning(f"📋 {t('have_deadlines')}")
        
        for deadline in st.session_state.saved_deadlines[-3:]:  # Show last 3
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"""
                <div class="dashboard-card">
                    <p><strong>📅 {deadline['deadline']}</strong></p>
                    <p>{t('from_document')}: {deadline.get('document', 'Unknown document')}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button(t('btn_delete'), key=f"del_deadline_{deadline.get('id')}"):
                    if not st.session_state.demo_mode:  # Don't delete in demo mode
                        delete_deadline(deadline.get('id'))
                        st.rerun()
        
        if st.button(t('view_all_deadlines'), use_container_width=True):
            st.session_state.page = "DocumentAssistant"
            st.rerun()
        st.divider()
    
    st.markdown(f"### {t('dashboard_intro')}")
    
    # Create feature cards in a 2-column grid layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Real-Time Translation Card
        with st.container():
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-icon">🗣️</div>
                <div class="card-title">{t('card_translation_title')}</div>
                <div class="card-description">{t('card_translation_desc')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"📖 {t('btn_open')}", use_container_width=True, key="open_translation"):
                st.session_state.page = "Translation"
                st.rerun()
        
        st.divider()
        
        # Legal Documents Card
        with st.container():
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-icon">📄</div>
                <div class="card-title">{t('card_documents_title')}</div>
                <div class="card-description">{t('card_documents_desc')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"📖 {t('btn_open')}", use_container_width=True, key="open_documents"):
                st.session_state.page = "DocumentAssistant"
                st.rerun()
        
        st.divider()
        
        # Know Your Rights Card
        with st.container():
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-icon">⚖️</div>
                <div class="card-title">{t('card_rights_title')}</div>
                <div class="card-description">{t('card_rights_desc')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"📖 {t('btn_open')}", use_container_width=True, key="open_rights"):
                st.session_state.page = "KnowYourRights"
                st.rerun()
        
        st.divider()
        
        # Resources Near You Card
        with st.container():
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-icon">📍</div>
                <div class="card-title">{t('card_nearby_title')}</div>
                <div class="card-description">{t('card_nearby_desc')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"📖 {t('btn_open')}", use_container_width=True, key="open_nearby"):
                st.session_state.page = "ResourcesNearYou"
                st.rerun()
    
    with col2:
        # Encounter Log Card
        with st.container():
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-icon">📝</div>
                <div class="card-title">{t('card_logging_title')}</div>
                <div class="card-description">{t('card_logging_desc')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"📖 {t('btn_open')}", use_container_width=True, key="open_logging"):
                st.session_state.page = "EncounterLogging"
                st.rerun()
        
        st.divider()
        
        # Crisis Resources Card
        with st.container():
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-icon">🚨</div>
                <div class="card-title">{t('card_emergency_title')}</div>
                <div class="card-description">{t('card_emergency_desc')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"📖 {t('btn_open')}", use_container_width=True, key="open_crisis"):
                st.session_state.page = "CrisisResources"
                st.rerun()
        
        st.divider()
        
        # Community Discussion Card
        with st.container():
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-icon">💬</div>
                <div class="card-title">{t('card_resources_title')}</div>
                <div class="card-description">{t('card_resources_desc')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"📖 {t('btn_open')}", use_container_width=True, key="open_community"):
                st.session_state.page = "CommunityDiscussion"
                st.rerun()


# ============================================================================
# LEGAL ADVICE GENERATOR
# ============================================================================
def get_legal_advice_for_statement(officer_statement: str) -> str:
    """Generate relevant legal advice based on officer statement keywords."""
    statement_lower = officer_statement.lower()
    
    # Keywords that trigger specific rights
    if any(word in statement_lower for word in ['search', 'car', 'vehicle', 'bag', 'pockets']):
        return (
            "🛡️ FOURTH AMENDMENT - Search & Seizure Rights:\n\n"
            "• You have the right to refuse a search of your vehicle, home, or belongings\n"
            "• Police need a warrant (signed by a judge) or your consent to search\n"
            "• Consent to a search must be clear and voluntary\n"
            "• If you refuse, clearly say: 'I do not consent to a search'\n"
            "• Keep your hands visible and do not interfere\n\n"
            "⚖️ Your actions:\n• Say NO clearly and calmly\n• Do not physically resist\n• Ask: 'Am I free to go?'\n• Ask for an attorney immediately"
        )
    elif any(word in statement_lower for word in ['arrest', 'custody', 'going downtown', 'taking you in']):
        return (
            "⚖️ SIXTH AMENDMENT - Right to Attorney:\n\n"
            "• You have an absolute right to an attorney\n"
            "• If you cannot afford one, one will be provided\n"
            "• Tell police: 'I want to speak to a lawyer'\n"
            "• Once you ask for a lawyer, police must stop questioning\n\n"
            "🛡️ During arrest:\n• Do not answer questions\n• Do not sign anything without your lawyer\n• Let your lawyer speak for you\n• Document everything"
        )
    elif any(word in statement_lower for word in ['question', 'answer', 'say', 'talk', 'speak', 'tell me']):
        return (
            "🤐 FIFTH AMENDMENT - Right to Remain Silent:\n\n"
            "• You do NOT have to answer police questions\n"
            "• Anything you say can be used against you in court\n"
            "• You can refuse to answer without getting in trouble\n"
            "• Say politely: 'I prefer not to answer questions'\n\n"
            "⚖️ What to do:\n• Stay calm and respectful\n• Clearly state your refusal\n• Ask: 'Am I free to go?'\n• Ask for an attorney\n• Do not run away"
        )
    elif any(word in statement_lower for word in ['stop', 'pulled', 'traffic', 'driving', 'license', 'registration']):
        return (
            "🚗 TRAFFIC STOP RIGHTS:\n\n"
            "• Keep your hands visible\n• Turn off engine, turn on lights\n• Stay in vehicle unless told to exit\n• Give license, registration, insurance ONLY\n• Refuse consent to search\n• Right to remain silent\n• Can refuse breathalyzer or sobriety test\n\n"
            "⚖️ Things to say:\n• 'I do not consent to a search'\n• 'I want an attorney'\n• 'Am I free to go?'\n• Stay calm and polite"
        )
    else:
        return (
            "📚 GENERAL RIGHTS IN POLICE ENCOUNTERS:\n\n"
            "✓ Right to remain silent\n"
            "✓ Right to an attorney\n"
            "✓ Can refuse searches\n"
            "✓ Can refuse to answer questions\n"
            "✓ Right to know why you're detained\n\n"
            "⚖️ What to do:\n"
            "1. Stay calm and respectful\n"
            "2. Keep hands visible\n"
            "3. Say: 'I want to speak to a lawyer'\n"
            "4. Refuse searches politely\n"
            "5. Document names, badge numbers, times"
        )

def page_translation():
    """Real-time translation page."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap');

        .translation-shell {
            background: linear-gradient(140deg, #f2f7ff 0%, #e6fff8 45%, #fff9ef 100%);
            border: 1px solid #d6e3ff;
            border-radius: 18px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            box-shadow: 0 8px 24px rgba(24, 73, 104, 0.1);
            font-family: 'Manrope', sans-serif;
        }

        .translation-shell h3 {
            margin: 0;
            color: #123a57;
            font-weight: 800;
            letter-spacing: 0.2px;
        }

        .translation-shell p {
            margin: 0.35rem 0 0 0;
            color: #35556e;
            font-size: 0.95rem;
        }

        .mic-help {
            margin-top: 0.6rem;
            padding: 0.75rem;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.75);
            border: 1px dashed #8bb3d9;
            color: #24485f;
            font-size: 0.9rem;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"# {t('translation_title')}")
    st.markdown(f"_{t('translation_subtitle')}_")
    st.divider()

    # Recorder state for reliable UX across reruns.
    if "translation_audio_bytes" not in st.session_state:
        st.session_state.translation_audio_bytes = None
    if "translation_transcript" not in st.session_state:
        st.session_state.translation_transcript = ""
    if "translation_mic_error" not in st.session_state:
        st.session_state.translation_mic_error = ""
    
    # Input section
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"## {t('officer_statement')}")
        st.markdown(f"""
        <div class="translation-shell">
            <h3>{t('mic_recorder_title')}</h3>
            <p>{t('mic_recorder_desc')}</p>
            <div class="mic-help">{t('mic_help')}</div>
        </div>
        """, unsafe_allow_html=True)

        recorder_output = None
        try:
            recorder_output = mic_recorder(
                start_prompt=t('btn_record'),
                stop_prompt=t('btn_stop'),
                format="wav",
                key="officer_mic_recorder"
            )
        except Exception:
            st.session_state.translation_mic_error = t('mic_access_failed')

        if recorder_output and isinstance(recorder_output, dict):
            audio_bytes = recorder_output.get("bytes")
            if audio_bytes:
                st.session_state.translation_audio_bytes = audio_bytes
                st.session_state.translation_mic_error = ""

                st.audio(audio_bytes, format="audio/wav")

                try:
                    recognizer = sr.Recognizer()
                    with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
                        audio_data = recognizer.record(source)
                    transcript = recognizer.recognize_google(audio_data, language="en-US")
                    st.session_state.translation_transcript = transcript
                    st.success(t('speech_recognized'))
                except sr.UnknownValueError:
                    st.session_state.translation_transcript = ""
                    st.session_state.translation_mic_error = t('mic_unclear')
                except sr.RequestError:
                    st.session_state.translation_transcript = ""
                    st.session_state.translation_mic_error = t('stt_unavailable')
                except Exception:
                    st.session_state.translation_transcript = ""
                    st.session_state.translation_mic_error = t('unable_process_audio')
            else:
                st.session_state.translation_mic_error = t('mic_no_audio')

        if st.session_state.translation_mic_error:
            st.error(st.session_state.translation_mic_error)

        if st.session_state.translation_transcript:
            st.session_state.english_input = st.session_state.translation_transcript

        english_text = st.text_area(
            t('translation_hint'),
            height=200,
            key="english_input"
        )
    
    with col2:
        st.markdown(f"## {t('your_rights')}")
        
        if english_text:
            target_lang = LANGUAGE_MAP[st.session_state.language]["code"]
            
            # Generate legal advice based on officer statement
            legal_advice = get_legal_advice_for_statement(english_text)
            
            if st.session_state.language != "English":
                try:
                    translator = get_translator("en", target_lang)
                    if translator:
                        # Translate the legal advice
                        translated_advice = translator.translate(legal_advice)
                        st.text_area(
                            f"{t('your_rights')}:",
                            value=translated_advice,
                            height=250,
                            disabled=True,
                            key="translated_output"
                        )

                        try:
                            tts = gTTS(text=translated_advice, lang=target_lang)
                            audio_buffer = io.BytesIO()
                            tts.write_to_fp(audio_buffer)
                            audio_buffer.seek(0)
                            st.audio(audio_buffer.read(), format="audio/mp3")
                        except Exception:
                            st.warning(t('audio_failed'))
                except:
                    st.error(t('error'))
            else:
                st.text_area(
                    f"{t('your_rights')}:",
                    value=legal_advice,
                    height=250,
                    disabled=True,
                    key="legal_advice_english"
                )
                
                try:
                    tts = gTTS(text=legal_advice, lang="en")
                    audio_buffer = io.BytesIO()
                    tts.write_to_fp(audio_buffer)
                    audio_buffer.seek(0)
                    st.audio(audio_buffer.read(), format="audio/mp3")
                except Exception:
                    st.warning(t('audio_failed'))

def page_documents():
    """Legal document assistant page with OCR and extraction."""
    st.markdown(f"# 📄 {t('documents_title')}")
    st.markdown(f"_{t('documents_subtitle')}_")
    st.divider()
    
    st.markdown(t('documents_intro_md'))
    
    # Document upload interface
    tab1, tab2 = st.tabs([t('upload_document'), t('document_extraction_tab')])
    
    with tab1:
        st.markdown(f"### {t('upload_legal_doc')}")
        uploaded_file = st.file_uploader(
            t('choose_document'),
            type=["pdf", "jpg", "jpeg", "png"],
            key="doc_uploader"
        )
        
        if uploaded_file:
            st.success(f"{t('file_uploaded')}: {uploaded_file.name}")
            
            # Show file info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(t('file_type'), uploaded_file.type)
            with col2:
                st.metric(t('file_size'), f"{uploaded_file.size / 1024:.1f} KB")
            with col3:
                st.metric(t('status_ready'), t('status_ready'))
            
            # Mock document extraction (in production, use Tesseract OCR)
            if st.button(t('extract_information'), use_container_width=True, key="extract_doc"):
                with st.spinner(t('extracting_info')):
                    # Mock extraction - sample legal text
                    sample_text = """
                    NOTICE TO APPEAR IN COURT
                    
                    You are required to appear in court on March 15, 2025 at 9:00 AM.
                    Location: San Francisco Superior Court, 400 McAllister St.
                    
                    REQUIRED ACTIONS:
                    1. Bring valid photo ID
                    2. Bring proof of residence
                    3. Pay the citation fee of $250 by March 10, 2025
                    
                    PENALTIES: Failure to appear may result in a warrant for your arrest.
                    
                    Case Number: 2024-CV-123456
                    Court Clerk: Department of Superior Court
                    """
                    
                    # Extract information
                    extracted = extract_deadline_and_dates(sample_text)
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"### {t('important_dates')}")
                        if extracted["dates"]:
                            for date in extracted["dates"]:
                                st.markdown(f"• **{date}**")
                        else:
                            st.info(t('no_dates_found'))
                        
                        st.markdown(f"### {t('required_actions')}")
                        if extracted["deadlines"]:
                            for deadline in extracted["deadlines"]:
                                st.markdown(f"• {deadline}")
                        else:
                            st.info(t('no_deadlines_found'))
                    
                    with col2:
                        st.markdown(f"### {t('critical_deadlines')}")
                        if extracted["deadlines"]:
                            for deadline in extracted["deadlines"]:
                                st.warning(f"⚠️ {deadline}")
                        else:
                            st.info(t('no_deadlines_found'))
                        
                        st.markdown(f"### {t('penalties_warnings')}")
                        if extracted["penalties"]:
                            for penalty in extracted["penalties"]:
                                st.error(f"❌ {penalty}")
                        else:
                            st.info(t('no_penalties_found'))
                    
                    # Download summary
                    st.divider()
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button(t('download_summary'), use_container_width=True):
                            summary_text = f"""
DOCUMENT EXTRACTION SUMMARY
==========================

DATES FOUND:
{chr(10).join(extracted['dates']) if extracted['dates'] else 'None'}

DEADLINES:
{chr(10).join(extracted['deadlines']) if extracted['deadlines'] else 'None'}

PENALTIES:
{chr(10).join(extracted['penalties']) if extracted['penalties'] else 'None'}
                            """
                            st.download_button(
                                label=t('download_as_txt'),
                                data=summary_text,
                                file_name="document_summary.txt",
                                mime="text/plain"
                            )
                    
                    # Save deadlines feature
                    with col2:
                        if st.button(t('save_deadlines_to_dashboard'), use_container_width=True, key="save_deadlines_btn"):
                            if extracted["deadlines"]:
                                for deadline in extracted["deadlines"]:
                                    deadline_data = {
                                        "deadline": deadline,
                                        "document": uploaded_file.name,
                                        "extracted_dates": extracted["dates"],
                                        "status": "Active",
                                        "language": st.session_state.language
                                    }
                                    save_deadline(deadline_data)
                                st.success(f"{t('saved_deadlines_count').format(count=len(extracted['deadlines']))}")
                            else:
                                st.warning(t('no_deadlines_to_save'))
    
    with tab2:
        st.markdown(f"### {t('extraction_guide')}")
        st.markdown(t('extraction_guide_md'))

def page_resources_near_you():
    """Unified Resources Near You - location-based legal aid and community services finder."""
    st.markdown(f"# 📍 {t('location_title')}")
    st.markdown(f"_{t('nearby_subtitle')}_")
    st.divider()
    
    # Resource search interface
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        address = st.text_input(
            t('enter_address'),
            placeholder=t('enter_address_placeholder'),
            key="resource_address"
        )
        add_screen_reader_label(f"{t('screen_reader_address_search')}: {address}")
    
    with col2:
        radius = st.slider(
            t('search_radius_miles'),
            min_value=1,
            max_value=50,
            value=5,
            key="search_radius_slider"
        )
    
    with col3:
        search_button = st.button(f"🔍 {t('btn_search')}", use_container_width=True, key="find_resources_btn")
    
    if search_button and address:
        # Show loading indicator
        with st.spinner(t('loading_resources')):
            resources = find_resources_by_location(address, radius)
            
            # Apply category filter if selected
            if st.session_state.resource_category_filter:
                resources = [r for r in resources if r['category'] == st.session_state.resource_category_filter]
        
        if resources:
            st.success(f"✅ {t('found_resources')}: {len(resources)} {t('resources_found')} {t('within_miles')} {radius}")
            
            # Display resources in modern cards
            for idx, resource in enumerate(resources):
                with st.container():
                    st.markdown(f"""
                    <div class="dashboard-card">
                        <div class="card-icon">📍</div>
                        <div class="card-title">{resource['name']}</div>
                        <div class="card-description">
                            <p><strong>{t('distance_away')}:</strong> {resource['distance']} {t('miles_unit')}</p>
                            <p><strong>{t('resource_address')}:</strong> {resource['address']}</p>
                            <p><strong>{t('resource_phone')}:</strong> {resource['phone']}</p>
                            <p><strong>{t('resource_hours')}:</strong> {resource['hours']}</p>
                            <p><strong>{t('resource_website')}:</strong> {resource['website']}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Get Directions button - opens Google Maps
                    if st.button(f"🗺️ {t('get_directions')} - {resource['name']}", use_container_width=True, key=f"directions_{idx}"):
                        # Build Google Maps URL
                        address_encoded = resource['address'].replace(' ', '+')
                        maps_url = f"https://www.google.com/maps/search/{address_encoded}/"
                        st.markdown(f"""
                        <a href="{maps_url}" target="_blank">
                        <button style="width: 100%; padding: 8px; background-color: #4285F4; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        🗺️ {t('open_in_google_maps')}
                        </button>
                        </a>
                        """, unsafe_allow_html=True)
                        st.success(f"📍 {t('opening_maps_to')}: {resource['name']}")
        else:
            st.warning(f"⚠️ {t('no_resources_found')}")
    
    # Browse by Resource Type
    st.divider()
    st.markdown(f"### 📋 {t('browse_resources')}")
    
    resource_categories = [
        ("⚖️ Legal Aid", "Legal Aid"),
        ("🏢 Community Centers", "Community Center"),
        ("🗣️ Language Services", "Language Services"),
        ("👥 Immigration Support", "Immigration Support"),
        ("🏥 Emergency Shelters", "Emergency Shelter")
    ]
    
    cols = st.columns(len(resource_categories))
    for idx, (label, category) in enumerate(resource_categories):
        with cols[idx]:
            if st.button(label, use_container_width=True, key=f"category_{category}"):
                st.session_state.resource_category_filter = category
                st.rerun()
    
    # Show active filter
    if st.session_state.resource_category_filter:
        st.info(f"📁 {t('currently_filtering')}: **{st.session_state.resource_category_filter}**")
        if st.button(f"❌ {t('btn_clear_filter')}", use_container_width=True):
            st.session_state.resource_category_filter = None
            st.rerun()

def page_rights_near_me():
    """Know Your Rights Near Me - location-based legal aid finder (legacy function - calls new unified page)."""
    page_resources_near_you()

def page_know_your_rights():
    """Combined Rights Education and Interactive Quizzes - Unified Learning Center."""
    st.markdown(f"# {t('know_your_rights_long')}")
    st.markdown(f"_{t('education_quizzes')}_")
    st.divider()
    
    # Tab-based interface
    tab1, tab2 = st.tabs([t('learn_tab'), t('quiz_tab')])
    
    with tab1:
        st.markdown(f"## {t('rights_education')}")
        
        rights_options = list(RIGHTS_EDUCATION.keys())
        selected_right = st.selectbox(
            t('select_topic'),
            rights_options,
            key="rights_select",
            format_func=lambda k: t(RIGHTS_EDUCATION[k]['title_key'])
        )
        
        if selected_right:
            right = RIGHTS_EDUCATION[selected_right]
            st.markdown(f"### {t(right['title_key'])}")
            st.markdown(t(right['content_key']))
            
            # Progress indicator
            progress_pct = (list(RIGHTS_EDUCATION.keys()).index(selected_right) + 1) / len(RIGHTS_EDUCATION) * 100
            st.progress(progress_pct / 100)
            st.caption(t('topic_progress').format(current=list(RIGHTS_EDUCATION.keys()).index(selected_right) + 1, total=len(RIGHTS_EDUCATION)))
    
    with tab2:
        st.markdown(f"## {t('rights_quiz')}")
        st.markdown(t('test_knowledge'))
        st.divider()
        
        quiz_questions = [
            {
                "question": t('can_police_search'),
                "options": [t('only_with_warrant'), t('only_prob_cause'), t('both_a_and_b'), t('never_without')],
                "correct": 2,
                "explanation": t('police_can_search')
            },
            {
                "question": t('answer_police_q'),
                "options": [t('yes_always'), t('right_remain_silent'), t('only_your_name'), t('only_if_arrested')],
                "correct": 1,
                "explanation": t('fifth_amendment')
            },
            {
                "question": t('what_say_arrested'),
                "options": [t('explain_what_happened'), t('ask_for_lawyer'), t('refuse_give_name'), t('try_negotiate')],
                "correct": 1,
                "explanation": t('always_ask_lawyer')
            }
        ]
        
        score = 0
        answered = 0
        
        for i, q in enumerate(quiz_questions):
            st.markdown(f"### {t('question_number').format(number=i+1, question=q['question'])}")
            answer = st.radio(
                t('select_answer'),
                q['options'],
                key=f"quiz_q{i}"
            )
            
            if st.button(t('check_answer').format(number=i+1), key=f"check_q{i}"):
                answered += 1
                if answer == q['options'][q['correct']]:
                    st.success(t('quiz_correct'))
                    score += 1
                else:
                    st.error(f"{t('quiz_incorrect')} {q['explanation']}")
            st.divider()
        
            if quiz_pct:
                quiz_pct = (score / len(quiz_questions)) * 100
                st.progress(quiz_pct / 100)
                st.metric(t('your_score'), f"{score}/{len(quiz_questions)}", f"{quiz_pct:.0f}%")

def page_community_discussion():
    """Talk to Your Community - Safe community discussion space."""
    st.markdown(f"# 💬 {t('talk_community')}")
    st.markdown(f"_{t('community_intro')}_")
    st.divider()
    
    # Tabs for different community features
    tab1, tab2, tab3 = st.tabs([t('share_exp_tab'), t('ask_q_tab'), t('give_advice_tab')])
    
    with tab1:
        st.markdown(f"### {t('share_your_exp')}")
        st.markdown(t('share_story'))
        
        post_title = st.text_input(t('title_label'), placeholder=t('exp_placeholder'), key="exp_title")
        post_content = st.text_area(t('your_story'), placeholder=t('story_placeholder'), height=200, key="exp_content")
        anonymous = st.checkbox(t('post_anonymously'), value=True, key="exp_anon")
        
        if st.button(t('share_exp_btn'), use_container_width=True, key="submit_exp"):
            if post_title and post_content:
                post = {
                    "type": "experience",
                    "title": post_title,
                    "content": post_content,
                    "anonymous": anonymous,
                    "author": t('author_anonymous') if anonymous else t('author_community_member')
                }
                save_community_post(post)
                st.success(t('exp_shared'))
            else:
                st.warning(t('fill_title_content'))
    
    with tab2:
        st.markdown(f"### {t('ask_community')}")
        st.markdown(t('question_help'))
        
        q_title = st.text_input(t('your_question'), placeholder=t('question_placeholder'), key="q_title")
        q_content = st.text_area(t('details_label'), placeholder=t('details_placeholder'), height=150, key="q_content")
        anonymous = st.checkbox(t('ask_anon'), value=True, key="q_anon")
        
        if st.button(t('ask_q_btn'), use_container_width=True, key="submit_q"):
            if q_title:
                post = {
                    "type": "question",
                    "title": q_title,
                    "content": q_content,
                    "anonymous": anonymous,
                    "author": t('author_anonymous') if anonymous else t('author_community_member'),
                    "responses": []
                }
                save_community_post(post)
                st.success(t('question_posted'))
            else:
                st.warning(t('enter_question'))
    
    with tab3:
        st.markdown(f"### {t('give_advice')}")
        st.markdown(t('help_others'))
        
        advice_title = st.text_input(t('topic_label'), placeholder=t('topic_placeholder'), key="adv_title")
        advice_content = st.text_area(t('your_advice'), placeholder=t('advice_placeholder'), height=200, key="adv_content")
        anonymous = st.checkbox(t('share_anon'), value=True, key="adv_anon")
        
        if st.button(t('share_advice_btn'), use_container_width=True, key="submit_adv"):
            if advice_title and advice_content:
                post = {
                    "type": "advice",
                    "title": advice_title,
                    "content": advice_content,
                    "anonymous": anonymous,
                    "author": t('author_anonymous') if anonymous else t('author_community_member')
                }
                save_community_post(post)
                st.success(t('share_wisdom'))
            else:
                st.warning(t('fill_topic_advice'))
    
    # Display recent community posts
    st.divider()
    st.markdown(f"## {t('recent_posts')}")
    
    if st.session_state.community_posts:
        # Sort by newest first
        sorted_posts = sorted(st.session_state.community_posts, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]
        
        for post in sorted_posts:
            with st.expander(f"{post.get('type', '').title()} - {post['title']} - {post['author']}"):
                st.markdown(post.get("content", ""))
                st.caption(f"{t('posted_recently')} {post.get('timestamp', t('recently'))}")
    else:
            st.info(t('no_posts_yet'))

def page_crisis_resources():
    """Crisis Resources & Hotlines - Emergency assistance and mental health support."""
    st.markdown(f"# {t('crisis_hotlines')}")
    st.markdown(f"_{t('crisis_support_24')}_")
    st.divider()
    
    # Critical hotlines section
    st.markdown(f"## {t('emergency_hotlines_header')}")
    st.markdown(f"**{t('in_immediate_danger')}**")
    
    crisis_contacts = {
        t('contact_emergency'): "911",
        t('contact_suicide'): "988",
        t('contact_domestic'): "1-800-799-7233",
        t('contact_rainn'): "1-800-656-4673",
        t('contact_poison'): "1-800-222-1222",
        t('contact_crisis_text'): t('contact_crisis_text_number')
    }
    
    cols = st.columns(3)
    col_idx = 0
    for service, number in crisis_contacts.items():
        with cols[col_idx % 3]:
            st.markdown(f"""
            <div class="dashboard-card" style="text-align: center;">
                <h3 style="margin-bottom: 1rem;">{service}</h3>
                <h2 style="color: var(--accent-terracotta); font-weight: 800; margin: 0.5rem 0;">{number}</h2>
            </div>
            """, unsafe_allow_html=True)
        col_idx += 1
    
    st.divider()
    
    # Emergency procedures
    st.markdown(f"## {t('safety_procedures')}")
    
    procedures = [
        (t('stay_safe'), t('stay_safe_desc')),
        (t('document_details'), t('document_details_desc')),
        (t('record_safely'), t('record_safely_desc')),
        (t('call_for_help'), t('call_help_desc')),
        (t('get_legal_help'), t('legal_help_desc')),
        (t('medical_attention'), t('medical_attention_desc'))
    ]
    
    for title, desc in procedures:
        with st.container():
            st.markdown(f"### {title}")
            st.write(desc)
    
    st.divider()
    
    # Mental health and support
    st.markdown(f"## {t('mental_health_support')}")
    st.markdown(f"""
    {t('legal_troubles_trauma')}
    
    **{t('mental_health_resources')}**
    - **{t('samhsa_helpline')}**
    - **{t('crisis_text')}**: {t('contact_crisis_text_number')}
    - **{t('psychology_directory')}**
    - **{t('support_groups')}**
    """)

def page_emergency():
    """Legacy Emergency page - redirects to Crisis Resources."""
    page_crisis_resources()



def page_encounter_logging():
    """Encounter logging page."""
    st.markdown(f"# {t('logging_title')}")
    st.markdown(f"_{t('logging_subtitle')}_")
    st.divider()
    
    tab1, tab2 = st.tabs([t('btn_log'), t('view_history')])
    
    with tab1:
        st.markdown(f"## {t('logging_title')}")
        
        encounter_type = st.selectbox(
            t('encounter_type'),
            [t('enc_type_traffic_stop'), t('enc_type_street_encounter'), t('enc_type_arrest'), t('enc_type_search'), t('enc_type_other')],
            key="enc_type"
        )
        
        location = st.text_input(t('encounter_location'), key="enc_location")
        details = st.text_area(t('encounter_details'), key="enc_details", height=200)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            badge_number = st.text_input(t('officer_badge'), key="officer_badge")
        with col2:
            agency = st.text_input(t('officer_agency'), key="officer_agency")
        
        if st.button(f"✅ {t('btn_submit')}", use_container_width=True):
            encounter = {
                "timestamp": datetime.now().isoformat(),
                "type": encounter_type,
                "location": location,
                "details": details,
                "officer_badge": badge_number,
                "officer_agency": agency,
                "language": st.session_state.language
            }
            save_encounter(encounter)
            st.success(t('encounter_saved'))
    
    with tab2:
        st.markdown(f"## {t('view_history')}")
        encounters = st.session_state.encounter_log
        
        if encounters:
            st.write(f"{t('total_encounters')}{len(encounters)}")
            for i, enc in enumerate(reversed(encounters)):
                with st.expander(f"{t('encounter_label')} {len(encounters)-i}: {enc.get('type', t('unknown'))} - {enc.get('timestamp', t('na'))}"):
                    st.json(enc)
        else:
            st.info(t('no_data'))



# ============================================================================
# PUBLIC DEPLOYMENT FEATURES
# ============================================================================

def generate_qr_code(url: str, size: int = 10):
    """Generate QR code from URL for sharing."""
    try:
        qr = qrcode.QRCode(version=1, box_size=size, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        return img
    except Exception as e:
        st.error(f"{t('error_generating_qr')}: {e}")
        return None

def get_demo_data():
    """Get demo data for demo mode."""
    return {
        "saved_deadlines": [
            {
                "id": 1,
                "deadline": "2026-08-15",
                "document": "Court Order - Civil Rights Case",
                "timestamp": "2026-06-24T10:30:00"
            },
            {
                "id": 2,
                "deadline": "2026-07-30",
                "document": "Legal Notice - Appeal Filing",
                "timestamp": "2026-06-20T14:00:00"
            },
            {
                "id": 3,
                "deadline": "2026-09-01",
                "document": "Settlement Agreement",
                "timestamp": "2026-06-19T09:15:00"
            }
        ],
        "community_posts": [
            {
                "id": 1,
                "title": "My First Traffic Stop Experience",
                "type": "experience",
                "content": "I learned to stay calm and ask for a lawyer immediately.",
                "author": "Anonymous",
                "timestamp": "2026-06-23T16:45:00"
            },
            {
                "id": 2,
                "title": "How to Request Body Camera Footage?",
                "type": "question",
                "content": "What's the best way to request police body camera footage for my case?",
                "author": "Anonymous",
                "timestamp": "2026-06-22T11:20:00"
            },
            {
                "id": 3,
                "title": "Always Know Your Rights",
                "type": "advice",
                "content": "Document everything, record if legal, and never sign anything without reading it first.",
                "author": "Anonymous",
                "timestamp": "2026-06-21T13:30:00"
            }
        ],
        "encounter_log": [
            {
                "timestamp": "2026-06-20T15:00:00",
                "type": "Traffic Stop",
                "location": "Downtown Area",
                "details": "Stopped for speeding, polite interaction",
                "officer_badge": "12345",
                "officer_agency": "Local Police"
            }
        ]
    }

def page_landing():
    """Landing page for first-time visitors - judges see this first."""
    # Hide sidebar for landing page
    st.set_page_config(page_title="CivicShield Pro - Know Your Rights", layout="wide")
    
    st.markdown(t('landing_hero_html'), unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(t('landing_purpose_md'))
    
    with col2:
        st.markdown(t('landing_features_md'))
    
    st.divider()
    
    # Demo and Tutorial buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(t('btn_launch_app'), use_container_width=True):
            st.session_state.skip_landing = True
            st.session_state.first_time_user = True
            st.session_state.page = "Tutorial"
            st.rerun()
    
    with col2:
        if st.button(t('btn_start_demo'), use_container_width=True):
            st.session_state.demo_mode = True
            st.session_state.skip_landing = True
            st.session_state.page = "Home"
            st.rerun()
    
    with col3:
        if st.button(t('btn_quick_tour'), use_container_width=True):
            st.session_state.skip_landing = True
            st.session_state.tutorial_step = 0
            st.session_state.page = "Tutorial"
            st.rerun()
    
    st.divider()
    
    # QR Code for easy sharing
    st.markdown(f"### {t('share_with_others')}")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(t('landing_share_md'))
    
    with col2:
        # Generate QR code for app URL (in production, use actual deployment URL)
        try:
            app_url = "https://civicshield-pro.streamlit.app"  # Update with actual deployment URL
            qr_img = generate_qr_code(app_url)
            if qr_img:
                st.image(qr_img, use_column_width=True)
        except:
            st.info(t('qr_generation_in_progress'))
    
    st.divider()
    
    # Target users
    st.markdown(t('landing_who_should_use_md'))
    
    st.divider()
    
    # Footer with disclaimer
    st.warning(t('landing_disclaimer_md'))

def page_tutorial():
    """First-time user tutorial with interactive walkthrough."""
    st.markdown(t('tutorial_intro_html'), unsafe_allow_html=True)
    
    # Tutorial steps
    steps = [
        {
            "title": t('tutorial_step1_title'),
            "description": t('tutorial_step1_desc'),
            "features": [t('tutorial_step1_feat1'), t('tutorial_step1_feat2'), t('tutorial_step1_feat3')]
        },
        {
            "title": t('tutorial_step2_title'),
            "description": t('tutorial_step2_desc'),
            "features": [t('tutorial_step2_feat1'), t('tutorial_step2_feat2'), t('tutorial_step2_feat3')]
        },
        {
            "title": t('tutorial_step3_title'),
            "description": t('tutorial_step3_desc'),
            "features": [t('tutorial_step3_feat1'), t('tutorial_step3_feat2'), t('tutorial_step3_feat3')]
        },
        {
            "title": t('tutorial_step4_title'),
            "description": t('tutorial_step4_desc'),
            "features": [t('tutorial_step4_feat1'), t('tutorial_step4_feat2'), t('tutorial_step4_feat3')]
        },
        {
            "title": t('tutorial_step5_title'),
            "description": t('tutorial_step5_desc'),
            "features": [t('tutorial_step5_feat1'), t('tutorial_step5_feat2'), t('tutorial_step5_feat3')]
        },
        {
            "title": t('tutorial_step6_title'),
            "description": t('tutorial_step6_desc'),
            "features": [t('tutorial_step6_feat1'), t('tutorial_step6_feat2'), t('tutorial_step6_feat3')]
        }
    ]
    
    # Display current step
    step_idx = st.session_state.tutorial_step
    if step_idx < len(steps):
        step = steps[step_idx]
        
        st.markdown(f"""
        <div class="tutorial-step">
            <div class="step-number">{step_idx + 1}</div>
            <h2>{step['title']}</h2>
            <div class="step-description">{step['description']}</div>
            <h4>✨ {t('key_features_label')}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        for feature in step["features"]:
            st.markdown(f"- {feature}")
        
        st.divider()
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if step_idx > 0:
                if st.button(t('btn_previous'), use_container_width=True):
                    st.session_state.tutorial_step -= 1
                    st.rerun()
        
        with col2:
            if st.button(t('btn_skip_tour'), use_container_width=True):
                st.session_state.tutorial_step = 0
                st.session_state.page = "Home"
                st.rerun()
        
        with col3:
                if step_idx < len(steps) - 1:
                    if st.button(t('btn_next'), use_container_width=True):
                        st.session_state.tutorial_step += 1
                        st.rerun()
                else:
                    if st.button(t('btn_start_using'), use_container_width=True):
                        st.session_state.tutorial_step = 0
                        st.session_state.first_time_user = False
                        st.session_state.page = "Home"
                        st.rerun()
    else:
        st.success(t('tour_complete'))
        if st.button(t('btn_go_home'), use_container_width=True):
            st.session_state.page = "Home"
            st.rerun()

# ============================================================================
# MAIN APP WITH SIDEBAR NAVIGATION
# ============================================================================
def main():
    """Main app with fully localized sidebar navigation."""
    
    # Initialize session state
    init_session_state()
    
    # Show landing page for first-time users or when landing page is requested
    if (st.session_state.first_time_user and not st.session_state.skip_landing) or st.session_state.page == "Landing":
        page_landing()
        return
    
    # Show tutorial page if requested
    if st.session_state.page == "Tutorial":
        page_tutorial()
        return
    
    # Apply accessibility CSS for main app
    apply_accessibility_css()
    
    # Sidebar header
    st.sidebar.markdown(f"# ⚖️ {t('sidebar_title')}")
    st.sidebar.markdown(f"*{t('sidebar_tagline')}*")
    st.sidebar.markdown("---")
    
    # Language selector in sidebar - with safe error handling
    def on_language_change():
        """Trigger rerun when language is changed."""
        try:
            new_lang = st.session_state.language_selector
            if new_lang in LANGUAGE_MAP:
                st.session_state.language = new_lang
                st.rerun()
        except Exception as e:
            st.error(f"{t('language_change_error')}: {e}")
    
    try:
        lang_list = list(LANGUAGE_MAP.keys())
        current_lang = st.session_state.language
        
        # Ensure current language is in the list
        if current_lang not in lang_list:
            current_lang = "English"
            st.session_state.language = "English"
        
        current_index = lang_list.index(current_lang)
        
        st.sidebar.selectbox(
            t('select_language'),
            lang_list,
            index=current_index,
            key="language_selector",
            on_change=on_language_change
        )
    except Exception as e:
        st.sidebar.error(f"{t('language_selector_error')}: {e}")
        st.session_state.language = "English"
    
    st.sidebar.divider()
    
    # Demo Mode toggle
    st.sidebar.markdown(f"### 📺 {t('demo_section_title')}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            t('demo_on') if st.session_state.demo_mode else t('demo_off'),
            use_container_width=True,
            key="demo_toggle"
        ):
            st.session_state.demo_mode = not st.session_state.demo_mode
            st.rerun()
    with col2:
        if st.button(t('tour_button'), use_container_width=True, key="tour_button"):
            st.session_state.tutorial_step = 0
            st.session_state.page = "Tutorial"
            st.rerun()
    
    if st.session_state.demo_mode:
        st.sidebar.success(t('demo_mode_active_sidebar'))
    
    st.sidebar.divider()
    
    # Accessibility Settings
    with st.sidebar.expander(t('accessibility_title'), expanded=False):
        # Text size selector
        text_size_option = st.radio(
            t('text_size'),
            [t('text_size_normal'), t('text_size_large'), t('text_size_extra_large')],
            index=0 if st.session_state.text_size == "normal" else 1,
            key="text_size_radio"
        )
        if t('text_size_normal') in text_size_option:
            st.session_state.text_size = "normal"
        elif t('text_size_large') in text_size_option:
            st.session_state.text_size = "large"
        else:
            st.session_state.text_size = "extra_large"
        
        # High contrast toggle
        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                f"⚪ {t('high_contrast_off')}" if st.session_state.high_contrast else f"◯ {t('high_contrast_on')}",
                use_container_width=True,
                key="contrast_toggle"
            ):
                st.session_state.high_contrast = not st.session_state.high_contrast
                st.rerun()
        
        # Screen reader toggle
        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                f"📢 {t('screen_reader')}" if st.session_state.screen_reader_enabled else t('screen_reader_off'),
                use_container_width=True,
                key="screen_reader_toggle"
            ):
                st.session_state.screen_reader_enabled = not st.session_state.screen_reader_enabled
                st.rerun()
        
        st.success(t('accessibility_saved'))
    
    st.sidebar.divider()
    
    # Navigation menu
    st.sidebar.markdown(f"### 🧭 {t('navigation_title')}")
    
    nav_options = {
        t('nav_home'): "Home",
        t('nav_translation'): "Translation",
        t('nav_documents'): "DocumentAssistant",
        t('nav_rights_full'): "KnowYourRights",
        t('nav_resources_near_you'): "ResourcesNearYou",
        t('nav_logging_full'): "EncounterLogging",
        t('nav_crisis_resources'): "CrisisResources",
        t('nav_community'): "CommunityDiscussion",
    }
    
    for label, page_name in nav_options.items():
        if st.sidebar.button(label, use_container_width=True, key=f"nav_{page_name}"):
            st.session_state.page = page_name
            st.rerun()
    
    st.sidebar.divider()
    
    # About section
    st.sidebar.markdown(f"### {t('nav_about')}")
    st.sidebar.markdown(f"""
    **{t('sidebar_version')}**
    
    {t('sidebar_purpose')}
    
    **{t('sidebar_languages')}**
    
    {t('sidebar_built_for')}
    """)
    
    st.sidebar.divider()
    
    # Disclaimer
    st.sidebar.warning(f"""
    **{t('sidebar_disclaimer')}**
    
    {t('sidebar_disclaimer_text')}
    """)
    
    st.sidebar.divider()
    
    # Landing page quick link
    if st.sidebar.button(t('show_landing_page'), use_container_width=True):
        st.session_state.page = "Landing"
        st.session_state.skip_landing = False
        st.rerun()
    
    # Page routing
    if st.session_state.page == "Home":
        page_home()
    elif st.session_state.page == "Translation":
        page_translation()
    elif st.session_state.page == "DocumentAssistant":
        page_documents()
    elif st.session_state.page == "KnowYourRights":
        page_know_your_rights()
    elif st.session_state.page == "ResourcesNearYou":
        page_resources_near_you()
    elif st.session_state.page == "EncounterLogging":
        page_encounter_logging()
    elif st.session_state.page == "CrisisResources":
        page_crisis_resources()
    elif st.session_state.page == "CommunityDiscussion":
        page_community_discussion()
    else:
        page_home()

# ============================================================================
# APP ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    main()

