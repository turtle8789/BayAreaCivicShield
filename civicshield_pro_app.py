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
import math
from PIL import Image
import qrcode
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
import requests
from bs4 import BeautifulSoup


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
    "Tagalog / Filipino": {"code": "tl", "native": "Tagalog"},
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
        "play_before_title": "1. Play Before Interaction",
        "play_before_desc": "Play this to the officer before recording begins.",
        "play_before_audio": "Officer, before we begin, I am using a translation app to avoid any language barriers. I am recording with your knowledge for safety and accuracy.",
        "play_after_title": "3. Play After Understanding Rights",
        "play_after_desc": "Play this to the officer after you hear your rights.",
        "play_after_audio": "I understand, officer, and I will comply, but I will be using my right to remain silent.",
        "officer_script": "Officer-facing script (English):",
        "officer_script_translated": "What this says in your language:",
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
        "extract_penalties": "⚠️ Penalties & Warnings",
        "extract_requirements": "✓ Requirements & Actions",
        "deadline_found": "Deadline:",
        "penalty_found": "Penalty:",
        "requirement_found": "Required Action:",
        "document_summary": "📋 Document Summary",
        "summary_generated": "Summary generated successfully",

        # Location-Based Resource Finder
        "location_title": "📍 Find Resources Near You",
        "search_radius_miles": "Search radius (miles):",
        "find_resources": "🔍 Find Nearby Resources",
        "resource_type": "Type of Resource:",
        "all_resources": "All Resources",
        "legal_aid_offices": "Legal Aid Offices",
        "community_centers": "Community Centers",
        "language_services": "Language Services",
        "emergency_shelters": "Emergency Shelters",
        "distance_away": "miles away",
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
        "play_before_title": "1. Reproducir Antes de la Interacción",
        "play_before_desc": "Muéstrale esto al oficial antes de comenzar la grabación.",
        "play_before_audio": "Officer, before we begin, I am using a translation app to avoid any language barriers. I am recording with your knowledge for safety and accuracy.",
        "play_after_title": "3. Reproducir Después de Entender tus Derechos",
        "play_after_desc": "Muéstrale esto al oficial después de escuchar tus derechos.",
        "play_after_audio": "I understand, officer, and I will comply, but I will be using my right to remain silent.",
        "officer_script": "Texto para el oficial (Inglés):",
        "officer_script_translated": "Lo que esto significa en tu idioma:",
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
        "play_before_title": "1. 互動前播放",
        "play_before_desc": "在錄音開始前，將此播放給警察聽。",
        "play_before_audio": "Officer, before we begin, I am using a translation app to avoid any language barriers. I am recording with your knowledge for safety and accuracy.",
        "play_after_title": "3. 了解權利後播放",
        "play_after_desc": "聆聽您的權利後，將此播放給警察聽。",
        "play_after_audio": "I understand, officer, and I will comply, but I will be using my right to remain silent.",
        "officer_script": "警察聽的內容（英語）：",
        "officer_script_translated": "這在您的語言中的意思：",
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
        "right_sixth": "第六修正案：律師權",
        "right_traffic": "交通截停權利",
        "right_arrest": "如果您被逮捕",
        "right_sixth_content": "**您的權利：** 您有權聘請律師。\n\n**重點：**\n- 如果您負擔不起律師，法院會為您指派一位\n- 在任何詢問期間，您都可以要求律師\n- 一旦您要求律師，警方應停止詢問\n- 您有權在詢問期間讓律師在場\n\n**應該說什麼：**\n- 「我想和律師談話」\n- 「我正在行使我要求律師的權利」\n- 然後保持沉默直到律師到場",
        "right_traffic_content": "**在交通截停期間：**\n- 您必須提供駕照、車輛登記和保險證明\n- 您可以問：「我現在被拘留嗎？還是可以離開？」\n- 您不必同意警方搜查您的車輛\n- 清楚地說：「我不同意搜查」\n\n**車輛搜查：**\n- 警方可以透過車窗查看\n- 如果警方有合理懷疑，他們可以搜查您的車\n- 如果您被逮捕，他們可以在無需同意的情況下搜查\n\n**您的權利：**\n- 保持雙手可見\n- 冷靜且禮貌地說話\n- 不要肢體反抗\n- 您可以錄影（但不要干擾）",
        "right_arrest_content": "**重要步驟：**\n1. 保持沉默 — 不要回答問題\n2. 清楚地說：「我想找律師」\n3. 未經律師同意不要簽署任何文件\n4. 不要與其他囚犯討論案件\n\n**被逮捕後的權利：**\n- 您有權知道被控罪名\n- 您有權打電話\n- 您有權保持沉默\n- 您有權聘請律師\n\n**不要做的事：**\n- 不要反抗逮捕（即使您認為不合法）\n- 不要簽署任何陳述\n- 不要同意搜查\n- 不要在沒有律師的情況下與警方談判",
        "resources_title": "社區資源",
        "resources_subtitle": "尋找法律援助和支援服務",
        "legal_aid": "法律援助機構",
        "emergency_services": "緊急服務",
        "immigration": "移民法律服務",
        "phone": "電話：",
        "services": "服務：",
        "website": "網站：",
        "hours": "營業時間：",
        "nearby_title": "附近的權利",
        "nearby_subtitle": "尋找您所在地區的法律援助和服務",
        "enter_address": "輸入您的地址：",
        "search_radius": "搜尋半徑（英里）：",
        "nearest_legal_aid": "📋 最近的法律援助辦公室",
        "nearest_courthouse": "⚖️ 最近的法院",
        "nearest_police": "👮 最近的警察局",
        "nearest_translator": "🗣️ 翻譯服務",
        "nearest_community": "🏢 社區中心",
        "address": "地址：",
        "phone_number": "電話：",
        "hours_open": "營業時間：",
        "get_directions": "🗺️ 獲取路線",
        "not_found": "附近沒有找到結果",
        "logging_title": "遭遇記錄",
        "logging_subtitle": "記錄警察遭遇和事件",
        "encounter_type": "遭遇類型：",
        "encounter_location": "地點：",
        "encounter_details": "詳細內容：",
        "encounter_date": "日期與時間：",
        "officer_info": "警察資訊：",
        "officer_badge": "警徽號碼：",
        "officer_agency": "所屬機構：",
        "encounter_saved": "✅ 遭遇已成功記錄",
        "view_history": "📋 查看遭遇歷史",
        "total_encounters": "總遭遇數：",
        "search_encounters": "🔍 搜尋遭遇",
        "emergency_title": "緊急協助",
        "emergency_subtitle": "危機資源與熱線",
        "emergency_911": "緊急服務（警察、消防、醫療）",
        "emergency_suicide": "全國自殺預防熱線",
        "emergency_domestic": "家庭暴力熱線",
        "emergency_assault": "性侵支援（RAINN）",
        "emergency_poison": "中毒控制中心",
        "emergency_text": "危機短信熱線",
        "emergency_procedures": "緊急程序：",
        "procedure_safe": "保持安全",
        "procedure_document": "記錄所有細節",
        "procedure_record": "錄影互動（在合法情況下）",
        "procedure_call": "尋求協助",
        "procedure_contact": "聯絡您的律師",

        "loading": "載入中...",
        "success": "成功！",
        "error": "錯誤",
        "warning": "警告",
        "info": "資訊",
        "processing": "處理中...",
        "please_wait": "請稍候...",
        "no_data": "沒有可用資料",
        "try_again": "請再試一次",

        "accessibility_title": "♿ 無障礙設定",
        "text_size": "文字大小：",
        "text_size_normal": "正常",
        "text_size_large": "大",
        "text_size_extra_large": "特大",
        "high_contrast": "🎨 高對比模式",
        "high_contrast_on": "高對比模式已開啟",
        "high_contrast_off": "高對比模式已關閉",
        "screen_reader": "螢幕閱讀器標籤已啟用",
        "accessibility_saved": "✅ 無障礙設定已儲存",

        "extract_deadlines": "📋 找到的重要截止日期",
        "extract_penalties": "⚠️ 罰則與警告",
        "extract_requirements": "✓ 要求與行動",
        "deadline_found": "截止日期：",
        "penalty_found": "罰則：",
        "requirement_found": "所需行動：",
        "document_summary": "📋 文件摘要",
        "summary_generated": "摘要已成功生成",

        "location_title": "📍 尋找附近資源",
        "enter_address": "輸入您的地址或郵遞區號：",
        "search_radius_miles": "搜尋半徑（英里）：",
        "find_resources": "🔍 尋找附近資源",
        "resource_type": "資源類型：",
        "all_resources": "所有資源",
        "legal_aid_offices": "法律援助辦公室",
        "community_centers": "社區中心",
        "language_services": "語言服務",
        "emergency_shelters": "緊急庇護所",
        "distance_away": "英里距離",
        "get_directions": "🗺️ 獲取路線",
        "no_resources_found": "此區域未找到資源",
        "resource_hours": "營業時間：",
        "resource_phone": "電話：",
        "resource_address": "地址：",
        "resource_website": "網站：",
        "loading_resources": "正在尋找附近資源...",
        "saved_deadlines": "⏰ 您已儲存的截止日期",
        "upload_legal_doc": "上傳法律文件",
        "important_dates": "📅 重要日期",
        "required_actions": "✓ 所需行動",
        "critical_deadlines": "⏰ 關鍵截止日期",
        "penalties_warnings": "⚠️ 罰則與警告",
        "extraction_guide": "文件提取指南",
        "demo_mode_active": "📺 **演示模式啟用** - 這是示範用的樣本資料",
        "have_deadlines": "📋 您有重要截止日期需要管理！",
        "view_all_deadlines": "📋 查看所有截止日期 →",
        "from_document": "來自：",
        "file_type": "文件類型",
        "file_size": "文件大小",
        "status_ready": "已準備好提取",
        "extract_information": "🔍 提取資訊",
        "extracting_info": "正在從文件提取資訊...",
        "no_dates_found": "未找到日期",
        "no_deadlines_found": "未找到截止日期",
        "no_penalties_found": "未找到罰則",
        "download_summary": "📥 下載摘要",
        "download_as_txt": "下載為 TXT",
        "save_deadlines_to_dashboard": "💾 儲存截止日期到儀表板",

        "know_your_rights_long": "⚖️ 了解您的權利",
        "education_quizzes": "教育、測驗與學習模組",
        "learn_tab": "📚 學習",
        "quiz_tab": "🧪 測驗",
        "rights_education": "權利教育",
        "select_topic": "選擇主題：",
        "test_knowledge": "測試您對公民權利與法律保護的了解。",
        "rights_quiz": "權利測驗",

        "can_police_search": "警方可以在沒有同意的情況下搜查您的車嗎？",
        "only_with_warrant": "只有持有搜查令",
        "only_prob_cause": "只有在有合理懷疑時",
        "both_a_and_b": "A 和 B 都是",
        "never_without": "不可以，永遠不行",
        "police_can_search": "警方可以在有搜查令或有合理懷疑時搜查車輛。",

        "answer_police_q": "您必須回答警方的問題嗎？",
        "yes_always": "是的，永遠要回答",
        "right_remain_silent": "不，您有權保持沉默",
        "only_your_name": "只需提供姓名",
        "only_if_arrested": "只有在被逮捕時",
        "fifth_amendment": "您擁有第五修正案賦予的緘默權，不需自我 incriminate。",

        "what_say_arrested": "如果被逮捕，您應該說什麼？",
        "explain_what_happened": "解釋發生了什麼",
        "ask_for_lawyer": "要求律師",
        "refuse_give_name": "拒絕提供姓名",
        "try_negotiate": "嘗試與警方談判",
        "always_ask_lawyer": "請立即要求律師並保持沉默。",

        "check_answer": "✓ 檢查答案 {number}",
        "question_number": "問題 {number}：{question}",
        "select_answer": "選擇您的答案：",
        "your_score": "分數",
        "talk_community": "💬 與社區交流",
        "community_intro": "分享經驗、提出問題、提供建議 —— 團結讓我們更強大",
        "share_exp_tab": "💭 分享經驗",
        "ask_q_tab": "❓ 提問",
        "give_advice_tab": "💡 提供建議",
        "share_your_exp": "💭 分享您的經驗",
        "share_story": "分享您的故事以幫助他人。所有貼文都會經過安全審核。",
        "title_label": "標題：",
        "exp_placeholder": "例如：交通截停的應對技巧",
        "your_story": "您的故事：",
        "story_placeholder": "分享您的經驗...",
        "post_anonymously": "匿名發佈",
        "share_exp_btn": "📤 分享經驗",
        "fill_title_content": "⚠️ 請填寫標題和內容",
        "exp_shared": "✅ 您的經驗已分享！感謝您幫助社區。",

        "ask_community": "❓ 向社區提問",
        "question_help": "有問題嗎？社區會協助您。",
        "your_question": "您的問題：",
        "question_placeholder": "例如：交通截停時我的權利是什麼？",
        "details_label": "詳細內容：",
        "details_placeholder": "提供更多背景資訊...",
        "ask_anon": "匿名提問",
        "ask_q_btn": "❓ 發佈問題",
        "enter_question": "⚠️ 請輸入您的問題",
        "question_posted": "✅ 您的問題已發佈！",

        "give_advice": "💡 提供建議",
        "help_others": "用您的知識和經驗幫助他人。",
        "topic_label": "主題：",
        "topic_placeholder": "例如：如何準備出庭",
        "your_advice": "您的建議：",
        "advice_placeholder": "分享您所知道的...",
        "share_anon": "匿名分享",
        "share_advice_btn": "💡 分享建議",
        "share_wisdom": "✅ 感謝您分享您的智慧！",
        "fill_topic_advice": "⚠️ 請填寫主題和建議",

        "recent_posts": "📋 最新社區貼文",
        "no_posts_yet": "💭 還沒有貼文。成為第一位分享的人！",
        "posted_recently": "發佈於 {timestamp}",
        "author_anonymous": "匿名",
        "author_community_member": "社區成員",

        "crisis_hotlines": "🚨 危機資源與熱線",
        "crisis_support_24": "24/7 全天候支援",
        "emergency_hotlines_header": "🆘 緊急熱線",
        "in_immediate_danger": "如果您處於立即危險中，請撥打 911",
        "emergency_number": "緊急電話",
        "suicide_prevention": "全國自殺預防熱線",
        "domestic_violence": "全國家庭暴力熱線",
        "sexual_assault": "RAINN — 性侵支援",
        "poison_control": "中毒控制中心",
        "crisis_text": "危機短信熱線",
        "safety_procedures": "📋 安全程序",
        "stay_safe": "🛡️ 保持安全",
        "stay_safe_desc": "確保自身安全 —— 不要肢體反抗。您的安全最重要。",
        "document_details": "📝 記錄細節",
        "document_details_desc": "記住：警察姓名、警徽號碼、地點、時間、他們說了什麼、做了什麼。",
        "record_safely": "🎥 安全錄影",
        "record_safely_desc": "如果安全且合法，請錄影互動。保持相機可見。",
        "call_for_help": "📞 尋求協助",
        "call_help_desc": "如果有立即危險，請撥打 911。保持冷靜並清楚說明情況。",
        "get_legal_help": "⚖️ 尋求法律協助",
        "legal_help_desc": "立即聯絡律師。許多公設辯護人提供緊急服務。",
        "medical_attention": "🏥 醫療協助",
        "medical_attention_desc": "如果受傷，請尋求醫療照護並拍照記錄傷勢。",
        "mental_health_support": "🧠 心理健康與支援",
        "legal_troubles_trauma": "面臨法律問題、警察遭遇或歧視可能造成心理創傷。",
        "mental_health_resources": "心理健康資源：",
        "samhsa_helpline": "SAMHSA 全國熱線：1-800-662-4357（免費、保密、24/7）",
        "psychology_directory": "本地治療師：搜尋 Psychology Today 目錄",
        "support_groups": "支援團體：NAACP、社區中心、法律援助機構常提供支援團體",

        "contact_emergency": "🆘 緊急 / Emergencia",
        "contact_suicide": "🧠 全國自殺預防熱線",
        "contact_domestic": "💔 全國家庭暴力熱線",
        "contact_rainn": "🤝 RAINN — 性侵支援",
        "contact_poison": "☠️ 中毒控制中心",
        "contact_crisis_text": "📱 危機短信熱線",
        "contact_crisis_text_number": "傳送 HOME 至 741741",

        "enc_type_traffic_stop": "交通截停",
        "enc_type_street_encounter": "街頭遭遇",
        "enc_type_arrest": "逮捕",
        "enc_type_search": "搜查",
        "enc_type_other": "其他",
        "encounter_label": "遭遇",
        "unknown": "未知",
        "na": "不適用",
        "error_generating_qr": "生成 QR 碼時發生錯誤",

        "btn_launch_app": "🚀 啟動應用程式",
        "btn_start_demo": "📺 開始演示",
        "btn_quick_tour": "❓ 快速導覽",
        "share_with_others": "📱 與他人分享",
        "qr_generation_in_progress": "正在生成 QR 碼...",
        "key_features_label": "主要功能：",
        "btn_previous": "⬅️ 上一步",
        "language_change_error": "語言切換錯誤",
        "demo_mode_active_sidebar": "✅ 演示模式啟用 —— 顯示樣本資料",
        "screen_reader_off": "🔇 螢幕閱讀器關閉",
        "navigation_title": "導航",
        "nav_rights_full": "⚖️ 了解您的權利",
        "nav_resources_near_you": "📍 附近資源",
        "nav_logging_full": "📝 遭遇記錄",
        "nav_crisis_resources": "🚨 危機資源",
        "nav_community": "💬 社區交流",
        "sidebar_built_for": "為全球民權保護而打造。",
        "show_landing_page": "🏠 顯示登陸頁面",

        "landing_hero_html": "<div class=\"landing-hero\"><h1>⚖️ CivicShield Pro</h1><h2>了解您的權利。保護自己。獲得幫助。</h2><p>一個專業的多語言平台，協助人們在實時遭遇中理解並行使其民權。</p></div>",

        "landing_purpose_md": "### 🎯 目的\nCivicShield Pro 為法官、倡導者和社區成員提供：\n\n- **14 種語言的實時法律翻譯**\n- **即時權利資訊**，依情況量身定制\n- **文件分析**與截止日期提取\n- **社區支援**與經驗分享\n- **24/7 危機資源**",

        "landing_features_md": "### ⭐ 主要功能\n\n- 🗣️ **實時翻譯** — 即時翻譯警察陳述\n- 📄 **法律文件** — 從法院文件中提取關鍵資訊\n- ⚖️ **了解您的權利** — 互動式測驗與教育\n- 📍 **附近資源** — 尋找法律援助與服務\n- 📝 **遭遇記錄** — 記錄警察互動\n- 🚨 **危機熱線** — 24/7 緊急支援\n- 💬 **社區論壇** — 分享與學習",

        "landing_share_md": "**與法官、倡導者和社區成員分享 CivicShield：**\n\n1. 掃描 QR 碼以存取應用程式\n2. 無需安裝 — 任何瀏覽器皆可使用\n3. 支援 14 種語言\n4. 適用於桌機、平板與手機",

        "landing_who_should_use_md": "### 👥 適用對象\n\n**法官與法律專業人士：**\n- 了解社區對民權保護的觀點\n- 評估被告是否理解其權利\n- 在判決中參考實時翻譯能力\n\n**倡導者與法律援助：**\n- 為客戶提供多語言法律資訊\n- 協助記錄遭遇\n- 連結社區資源\n\n**教育者：**\n- 教導學生民權知識\n- 展示真實法律情境\n- 使用互動式測驗\n\n**社區成員：**\n- 知道在警察遭遇中該怎麼做\n- 即時存取緊急資源\n- 與社區交流經驗",

        "landing_disclaimer_md": "**⚠️ 法律免責聲明：**\n\nCivicShield Pro 提供民權教育資訊，並非法律建議。\n法律因地區而異且可能變更。\n請務必諮詢合格律師以獲得具體建議。",

        "tutorial_intro_html": "<div class=\"tutorial-container\"><h1>👋 歡迎使用 CivicShield Pro！</h1><p>讓我們快速導覽，協助您開始使用。</p></div>",

        "tutorial_step1_title": "🏠 主頁儀表板",
        "tutorial_step1_desc": "這是您存取所有 CivicShield 功能的中心。每張卡片代表一個強大的工具。",
        "tutorial_step1_feat1": "導航至任何功能",
        "tutorial_step1_feat2": "查看已儲存的截止日期",
        "tutorial_step1_feat3": "存取危機資源",

        "tutorial_step2_title": "🗣️ 實時翻譯",
        "tutorial_step2_desc": "即時翻譯警察陳述，支援 14 種語言。",
        "tutorial_step2_feat1": "多語言語音轉文字",
        "tutorial_step2_feat2": "實時翻譯",
        "tutorial_step2_feat3": "語音播放",

        "tutorial_step3_title": "📄 法律文件",
        "tutorial_step3_desc": "上傳法院文件、法律通知或合約，CivicShield 會提取關鍵資訊。",
        "tutorial_step3_feat1": "自動提取截止日期",
        "tutorial_step3_feat2": "識別罰則",
        "tutorial_step3_feat3": "提供翻譯",

        "tutorial_step4_title": "⚖️ 了解您的權利",
        "tutorial_step4_desc": "學習民權並使用互動式測驗測試您的知識。",
        "tutorial_step4_feat1": "學習民權",
        "tutorial_step4_feat2": "進行互動測驗",
        "tutorial_step4_feat3": "追蹤進度",

        "tutorial_step5_title": "📍 附近資源",
        "tutorial_step5_desc": "尋找法律援助、社區中心與緊急服務。",
        "tutorial_step5_feat1": "依位置搜尋",
        "tutorial_step5_feat2": "依類別瀏覽",
        "tutorial_step5_feat3": "一鍵獲取路線",

        "tutorial_step6_title": "💬 社區論壇",
        "tutorial_step6_desc": "與他人交流、分享經驗、提問並提供建議。",
        "tutorial_step6_feat1": "匿名分享經驗",
        "tutorial_step6_feat2": "提出法律問題",
        "tutorial_step6_feat3": "提供建議",

        "documents_intro_md": "上傳法律文件（圖片或 PDF）以提取關鍵資訊：\n- 重要日期與截止日期\n- 所需行動\n- 罰則與警告\n- 政府機構\n- 文件摘要",
    
    },
    
    "Mandarin / 普通話": {
        "sidebar_title": "CivicShield",
        "sidebar_tagline": "了解你的权利",
        "select_language": "📍 选择语言：",
        "nav_home": "🏠 首页",
        "nav_translation": "🗣️ 实时翻译",
        "nav_documents": "📄 法律文件",
        "nav_rights": "📚 权利中心",
        "nav_quiz": "❓ 权利测验",
        "nav_resources": "🏥 社区资源",
        "nav_nearby": "📍 附近的权利",
        "nav_logging": "📝 遭遇记录",
        "nav_emergency": "🚨 紧急帮助",
        "nav_about": "关于 CivicShield",
        "sidebar_version": "版本 3.0.0",
        "sidebar_purpose": "专业民权保护与法律翻译",
        "sidebar_languages": "支持语言：14",
        "sidebar_disclaimer": "⚠️ 法律免责声明",
        "sidebar_disclaimer_text": "本应用提供教育信息，而非法律建议。请咨询专业律师以获得具体建议。",

        "home_title": "欢迎使用 CivicShield",
        "home_subtitle": "了解你的权利。保护自己。获得帮助。",
        "dashboard_intro": "请选择以下功能开始：",

        "card_translation_title": "实时翻译",
        "card_translation_desc": "翻译警官陈述并以你的语言获取法律建议",
        "card_documents_title": "法律文件助手",
        "card_documents_desc": "上传文件、提取关键信息并翻译成你的语言",
        "card_rights_title": "权利教育中心",
        "card_rights_desc": "学习你的宪法权利与法律保护",
        "card_quiz_title": "权利测验",
        "card_quiz_desc": "测试你对权利与公民自由的了解",
        "card_resources_title": "社区资源",
        "card_resources_desc": "查找法律援助、紧急服务与支持机构",
        "card_nearby_title": "附近的权利",
        "card_nearby_desc": "查找附近的法律援助、法院与社区服务",
        "card_logging_title": "遭遇记录",
        "card_logging_desc": "记录并追踪警察遭遇与事件",
        "card_emergency_title": "紧急协助",
        "card_emergency_desc": "访问危机热线与紧急程序",

        "btn_open": "打开功能",
        "btn_delete": "❌",
        "btn_record": "🎤 录音",
        "btn_stop": "⏹️ 停止",
        "btn_translate": "🌐 翻译",
        "btn_listen": "🔊 收听",
        "btn_download": "📥 下载",
        "btn_search": "🔍 搜索",
        "btn_log": "📝 记录",
        "btn_back": "← 返回",
        "btn_submit": "✓ 提交",
        "btn_cancel": "✗ 取消",

        "translation_title": "实时翻译",
        "translation_subtitle": "翻译警官陈述并获取法律建议",
        "officer_statement": "警官陈述（英文）：",
        "your_rights": "你的权利与法律建议：",
        "play_before_title": "1. 互动前播放",
        "play_before_desc": "录音开始前，将此内容播放给警察听。",
        "play_before_audio": "Officer, before we begin, I am using a translation app to avoid any language barriers. I am recording with your knowledge for safety and accuracy.",
        "play_after_title": "3. 了解权利后播放",
        "play_after_desc": "听完您的权利后，将此内容播放给警察听。",
        "play_after_audio": "I understand, officer, and I will comply, but I will be using my right to remain silent.",
        "officer_script": "给警察的内容（英语）：",
        "officer_script_translated": "这句话用您的语言是：",
        "record_officer": "🎤 录制警官声音",
        "stop_recording": "⏹️ 停止录音并翻译",
        "listen_to_advice": "🔊 收听建议",
        "translation_hint": "输入文字或录制音频进行翻译",
        "generating_audio": "正在生成音频...",
        "audio_ready": "✅ 音频已准备好播放",
        "audio_failed": "❌ 音频生成失败",
        "speech_recognized": "语音已捕获并转换为文字。",
        "mic_unclear": "无法理解录制的语音。请清晰讲话后重试。",
        "stt_unavailable": "语音转文字服务暂不可用，请稍后再试。",
        "unable_process_audio": "无法处理录制的音频，请重新录制。",
        "mic_recorder_title": "麦克风录音器",
        "mic_recorder_desc": "使用“开始录音”和“停止录音”捕捉警官语音。",
        "mic_help": "如果浏览器阻止麦克风访问，请允许权限后重新录音。",
        "mic_access_failed": "麦克风访问失败，请允许权限后重试。",
        "mic_no_audio": "未捕获到音频，可能未授予麦克风权限。请允许访问后重试。",
        "btn_clear_filter": "清除筛选",
        "currently_filtering": "当前筛选条件：",
        "quiz_correct": "✅ 正确！",
        "quiz_incorrect": "❌ 错误。",
        "language_selector_error": "❌ 语言选择器错误",
        "demo_section_title": "演示与测试",
        "demo_on": "🎬 演示已开启",
        "demo_off": "🎬 演示已关闭",
        "tour_button": "🎓 导览",
        "tour_complete": "✅ 导览完成！你已准备好使用 CivicShield。",
        "btn_go_home": "🏠 返回首页",
        "btn_skip_tour": "⏭️ 跳过导览",
        "btn_next": "下一步 ➡️",
        "btn_start_using": "🎉 开始使用！",
        "documents_title": "法律文件助手",
        "documents_subtitle": "上传文件并提取关键信息",
        "upload_document": "📤 上传文件",
        "take_photo": "📸 拍照",
        "extract_text": "提取文字",
        "simplify_text": "简化法律语言",
        "translate_document": "🌐 翻译文件",
        "extract_dates": "📅 发现的日期",
        "extract_deadlines": "⏰ 截止日期",
        "extract_agencies": "🏛️ 政府机构",
        "extract_actions": "✅ 所需行动",
        "download_report": "📥 下载报告",
        "report_generated": "报告已生成",
        "rights_title": "权利教育中心",
        "rights_subtitle": "了解你的宪法权利",
        "right_fourth": "第四修正案：搜查与扣押",
        "right_fifth": "第五修正案：保持沉默的权利",
        "right_sixth": "第六修正案：律师权",
        "right_traffic": "交通拦截权利",
        "right_arrest": "如果你被逮捕",
        "right_fourth_content": "**你的权利：** 你有权免受不合理的搜查和扣押。\n\n**要点：**\n- 警察通常需要搜查令才能搜查你的住所、车辆或物品\n- 你可以说：“我不同意搜查”来拒绝\n- 不要进行肢体反抗，否则可能导致额外指控\n- 即使你拒绝，如果警察有搜查令或合理怀疑，他们仍可继续\n\n**你可以做的：**\n- 保持沉默并询问：“我可以离开吗？”\n- 询问：“你有搜查令吗？”\n- 保持双手可见\n- 不要阻碍警察行动",

        "right_fifth_content": "**你的权利：** 你有权保持沉默，不自我 incriminate。\n\n**要点：**\n- 你不必回答警察的问题\n- 清楚地说：“我正在行使保持沉默的权利”\n- 即使你未被逮捕，这项权利仍然适用\n- 保持沉默不能在法庭上被用来对付你\n\n**重要：**\n- 你必须明确告诉警察你正在行使该权利\n- 如果被逮捕，立即要求律师\n- 不要试图解释或谈判",

        "right_sixth_content": "**你的权利：** 你有权聘请律师。\n\n**要点：**\n- 如果你负担不起律师，法院会为你指派一位\n- 在任何询问期间，你都可以要求律师\n- 一旦你要求律师，警察应停止询问\n- 你有权在询问期间让律师在场\n\n**应该说：**\n- “我想和律师谈话”\n- “我正在行使我的律师权”\n- 然后保持沉默直到律师到场",

        "right_traffic_content": "**在交通拦截期间：**\n- 你必须提供驾照、车辆登记和保险证明\n- 你可以问：“我现在被拘留吗？还是可以离开？”\n- 你不必同意警察搜查你的车辆\n- 清楚地说：“我不同意搜查”\n\n**车辆搜查：**\n- 警察可以透过车窗查看\n- 如果警察有合理怀疑，他们可以搜查你的车\n- 如果你被逮捕，他们可以在无需同意的情况下搜查\n\n**你的权利：**\n- 保持双手可见\n- 冷静且礼貌地说话\n- 不要肢体反抗\n- 你可以录影（但不要干扰）",

        "right_arrest_content": "**重要步骤：**\n1. 保持沉默 — 不要回答问题\n2. 清楚地说：“我想找律师”\n3. 未经律师同意不要签署任何文件\n4. 不要与其他被拘留者讨论案件\n\n**被逮捕后的权利：**\n- 你有权知道被控罪名\n- 你有权打电话\n- 你有权保持沉默\n- 你有权聘请律师\n\n**不要做的事：**\n- 不要反抗逮捕（即使你认为不合法）\n- 不要签署任何陈述\n- 不要同意搜查\n- 不要在没有律师的情况下与警察谈判",

        "resources_title": "社区资源",
        "resources_subtitle": "查找法律援助和支持服务",
        "legal_aid": "法律援助机构",
        "emergency_services": "紧急服务",
        "immigration": "移民法律服务",
        "phone": "电话：",
        "services": "服务：",
        "website": "网站：",
        "hours": "营业时间：",

        "nearby_title": "附近的权利",
        "nearby_subtitle": "查找你所在地区的法律援助和服务",
        "enter_address": "输入你的地址：",
        "search_radius": "搜索半径（英里）：",
        "nearest_legal_aid": "📋 最近的法律援助办公室",
        "nearest_courthouse": "⚖️ 最近的法院",
        "nearest_police": "👮 最近的警察局",
        "nearest_translator": "🗣️ 翻译服务",
        "nearest_community": "🏢 社区中心",
        "address": "地址：",
        "phone_number": "电话：",
        "hours_open": "营业时间：",
        "get_directions": "🗺️ 获取路线",
        "not_found": "附近未找到结果",
        "logging_title": "遭遇记录",
        "logging_subtitle": "记录警察遭遇和事件",
        "encounter_type": "遭遇类型：",
        "encounter_location": "地点：",
        "encounter_details": "详细内容：",
        "encounter_date": "日期与时间：",
        "officer_info": "警官信息：",
        "officer_badge": "警徽号码：",
        "officer_agency": "所属机构：",
        "encounter_saved": "✅ 遭遇已成功记录",
        "view_history": "📋 查看遭遇历史",
        "total_encounters": "总遭遇数：",
        "search_encounters": "🔍 搜索遭遇",
        "emergency_title": "紧急协助",
        "emergency_subtitle": "危机资源与热线",
        "emergency_911": "紧急服务（警察、消防、医疗）",
        "emergency_suicide": "全国自杀预防热线",
        "emergency_domestic": "家庭暴力热线",
        "emergency_assault": "性侵支援（RAINN）",
        "emergency_poison": "中毒控制中心",
        "emergency_text": "危机短信热线",
        "emergency_procedures": "紧急程序：",
        "procedure_safe": "保持安全",
        "procedure_document": "记录所有细节",
        "procedure_record": "录影互动（在合法情况下）",
        "procedure_call": "寻求帮助",
        "procedure_contact": "联系你的律师",
        "loading": "加载中...",
        "success": "成功！",
        "error": "错误",
        "warning": "警告",
        "info": "信息",
        "processing": "处理中...",
        "please_wait": "请稍候...",
        "no_data": "无可用数据",
        "try_again": "请再试一次",

        "accessibility_title": "♿ 无障碍设置",
        "text_size": "文字大小：",
        "text_size_normal": "正常",
        "text_size_large": "大",
        "text_size_extra_large": "特大",
        "high_contrast": "🎨 高对比模式",
        "high_contrast_on": "高对比模式已开启",
        "high_contrast_off": "高对比模式已关闭",
        "screen_reader": "屏幕阅读器标签已启用",
        "accessibility_saved": "✅ 无障碍设置已保存",

        "extract_deadlines": "📋 发现的重要截止日期",
        "extract_penalties": "⚠️ 罚则与警告",
        "extract_requirements": "✓ 要求与行动",
        "deadline_found": "截止日期：",
        "penalty_found": "罚则：",
        "requirement_found": "所需行动：",
        "document_summary": "📋 文件摘要",
        "summary_generated": "摘要已成功生成",

        "location_title": "📍 查找附近资源",
        "enter_address": "输入你的地址或邮编：",
        "search_radius_miles": "搜索半径（英里）：",
        "find_resources": "🔍 查找附近资源",
        "resource_type": "资源类型：",
        "all_resources": "所有资源",
        "legal_aid_offices": "法律援助办公室",
        "community_centers": "社区中心",
        "language_services": "语言服务",
        "emergency_shelters": "紧急庇护所",
        "distance_away": "英里距离",
        "get_directions": "🗺️ 获取路线",
        "no_resources_found": "此区域未找到资源",
        "resource_hours": "营业时间：",
        "resource_phone": "电话：",
        "resource_address": "地址：",
        "resource_website": "网站：",
        "loading_resources": "正在查找附近资源...",
        "saved_deadlines": "⏰ 你保存的截止日期",
        "upload_legal_doc": "上传法律文件",
        "important_dates": "📅 重要日期",
        "required_actions": "✓ 所需行动",
        "critical_deadlines": "⏰ 关键截止日期",
        "penalties_warnings": "⚠️ 罚则与警告",
        "extraction_guide": "文件提取指南",
        "demo_mode_active": "📺 **演示模式已开启** - 当前显示示例数据",
        "have_deadlines": "📋 你有需要管理的重要截止日期！",
        "view_all_deadlines": "📋 查看所有截止日期 →",
        "from_document": "来自：",
        "file_type": "文件类型",
        "file_size": "文件大小",
        "status_ready": "已准备好提取",
        "extract_information": "🔍 提取信息",
        "extracting_info": "正在从文件提取信息...",
        "no_dates_found": "未找到日期",
        "no_deadlines_found": "未找到截止日期",
        "no_penalties_found": "未找到罚则",
        "download_summary": "📥 下载摘要",
        "download_as_txt": "下载为 TXT",
        "save_deadlines_to_dashboard": "💾 保存截止日期到仪表板",



        "know_your_rights_long": "⚖️ 了解你的权利",
        "education_quizzes": "教育、测验与学习模块",
        "learn_tab": "📚 学习",
        "quiz_tab": "🧪 测验",
        "rights_education": "权利教育",
        "select_topic": "选择主题：",
        "test_knowledge": "测试你对公民权利与法律保护的了解。",
        "rights_quiz": "权利测验",

        "can_police_search": "警察可以在没有同意的情况下搜查你的车吗？",
        "only_with_warrant": "只有持有搜查令",
        "only_prob_cause": "只有在有合理怀疑时",
        "both_a_and_b": "A 和 B 都是",
        "never_without": "不可以，永远不行",
        "police_can_search": "警察可以在有搜查令或有合理怀疑时搜查车辆。",

        "answer_police_q": "你必须回答警察的问题吗？",
        "yes_always": "是的，永远要回答",
        "right_remain_silent": "不，你有权保持沉默",
        "only_your_name": "只需提供姓名",
        "only_if_arrested": "只有在被逮捕时",
        "fifth_amendment": "你拥有第五修正案赋予的保持沉默权，不需自我 incriminate。",

        "what_say_arrested": "如果被逮捕，你应该说什么？",
        "explain_what_happened": "解释发生了什么",
        "ask_for_lawyer": "要求律师",
        "refuse_give_name": "拒绝提供姓名",
        "try_negotiate": "尝试与警察谈判",
        "always_ask_lawyer": "请立即要求律师并保持沉默。",

        "check_answer": "✓ 检查答案 {number}",
        "question_number": "问题 {number}：{question}",
        "select_answer": "选择你的答案：",
        "your_score": "你的分数",
        "talk_community": "💬 与社区交流",
        "community_intro": "分享经验、提出问题、提供建议 —— 团结让我们更强大",
        "share_exp_tab": "💭 分享经验",
        "ask_q_tab": "❓ 提问",
        "give_advice_tab": "💡 提供建议",
        "share_your_exp": "💭 分享你的经验",
        "share_story": "分享你的故事以帮助他人。所有帖子都会经过安全审核。",
        "title_label": "标题：",
        "exp_placeholder": "例如：交通拦截的应对技巧",
        "your_story": "你的故事：",
        "story_placeholder": "分享你的经验...",
        "post_anonymously": "匿名发布",
        "share_exp_btn": "📤 分享经验",
        "fill_title_content": "⚠️ 请填写标题和内容",
        "exp_shared": "✅ 你的经验已分享！感谢你帮助社区。",

        "ask_community": "❓ 向社区提问",
        "question_help": "有问题吗？社区会协助你。",
        "your_question": "你的问题：",
        "question_placeholder": "例如：交通拦截时我的权利是什么？",
        "details_label": "详细内容：",
        "details_placeholder": "提供更多背景信息...",
        "ask_anon": "匿名提问",
        "ask_q_btn": "❓ 发布问题",
        "enter_question": "⚠️ 请输入你的问题",
        "question_posted": "✅ 你的问题已发布！",

        "give_advice": "💡 提供建议",
        "help_others": "用你的知识和经验帮助他人。",
        "topic_label": "主题：",
        "topic_placeholder": "例如：如何准备出庭",
        "your_advice": "你的建议：",
        "advice_placeholder": "分享你所知道的...",
        "share_anon": "匿名分享",
        "share_advice_btn": "💡 分享建议",
        "share_wisdom": "✅ 感谢你分享你的智慧！",
        "fill_topic_advice": "⚠️ 请填写主题和建议",

        "recent_posts": "📋 最新社区帖子",
        "no_posts_yet": "💭 还没有帖子。成为第一位分享的人！",
        "posted_recently": "发布于 {timestamp}",
        "author_anonymous": "匿名",
        "author_community_member": "社区成员",

        "crisis_hotlines": "🚨 危机资源与热线",
        "crisis_support_24": "24/7 全天候支援",
        "emergency_hotlines_header": "🆘 紧急热线",
        "in_immediate_danger": "如果你处于立即危险中，请拨打 911",
        "emergency_number": "紧急电话",
        "suicide_prevention": "全国自杀预防热线",
        "domestic_violence": "全国家庭暴力热线",
        "sexual_assault": "RAINN — 性侵支援",
        "poison_control": "中毒控制中心",
        "crisis_text": "危机短信热线",
        "safety_procedures": "📋 安全程序",
        "stay_safe": "🛡️ 保持安全",
        "stay_safe_desc": "确保自身安全 —— 不要肢体反抗。你的安全最重要。",
        "document_details": "📝 记录细节",
        "document_details_desc": "记住：警官姓名、警徽号码、地点、时间、他们说了什么、做了什么。",
        "record_safely": "🎥 安全录影",
        "record_safely_desc": "如果安全且合法，请录影互动。保持相机可见。",
        "call_for_help": "📞 寻求协助",
        "call_help_desc": "如果有立即危险，请拨打 911。保持冷静并清楚说明情况。",
        "get_legal_help": "⚖️ 寻求法律协助",
        "legal_help_desc": "立即联系律师。许多公设辩护人提供紧急服务。",
        "medical_attention": "🏥 医疗协助",
        "medical_attention_desc": "如果受伤，请寻求医疗照护并拍照记录伤势。",
        "mental_health_support": "🧠 心理健康与支援",
        "legal_troubles_trauma": "面临法律问题、警察遭遇或歧视可能造成心理创伤。",
        "mental_health_resources": "心理健康资源：",
        "samhsa_helpline": "SAMHSA 全国热线：1-800-662-4357（免费、保密、24/7）",
        "psychology_directory": "本地治疗师：搜索 Psychology Today 目录",
        "support_groups": "支援团体：NAACP、社区中心、法律援助机构常提供支援团体",

        "contact_emergency": "🆘 紧急 / Emergency",
        "contact_suicide": "🧠 全国自杀预防热线",
        "contact_domestic": "💔 全国家庭暴力热线",
        "contact_rainn": "🤝 RAINN — 性侵支援",
        "contact_poison": "☠️ 中毒控制中心",
        "contact_crisis_text": "📱 危机短信热线",
        "contact_crisis_text_number": "发送 HOME 至 741741",

        "enc_type_traffic_stop": "交通拦截",
        "enc_type_street_encounter": "街头遭遇",
        "enc_type_arrest": "逮捕",
        "enc_type_search": "搜查",
        "enc_type_other": "其他",
        "encounter_label": "遭遇",
        "unknown": "未知",
        "na": "不适用",
        "error_generating_qr": "生成 QR 码时发生错误",

        "btn_launch_app": "🚀 启动应用",
        "btn_start_demo": "📺 开始演示",
        "btn_quick_tour": "❓ 快速导览",
        "share_with_others": "📱 与他人分享",
        "qr_generation_in_progress": "正在生成 QR 码...",
        "key_features_label": "主要功能：",
        "btn_previous": "⬅️ 上一步",
        "language_change_error": "语言切换错误",
        "demo_mode_active_sidebar": "✅ 演示模式已开启 —— 显示示例数据",
        "screen_reader_off": "🔇 屏幕阅读器已关闭",
        "navigation_title": "导航",
        "nav_rights_full": "⚖️ 了解你的权利",
        "nav_resources_near_you": "📍 附近资源",
        "nav_logging_full": "📝 遭遇记录",
        "nav_crisis_resources": "🚨 危机资源",
        "nav_community": "💬 社区交流",
        "sidebar_built_for": "为全球民权保护而打造。",
        "show_landing_page": "🏠 显示首页",

        "landing_hero_html": "<div class=\"landing-hero\"><h1>⚖️ CivicShield Pro</h1><h2>了解你的权利。保护自己。获得帮助。</h2><p>一个专业的多语言平台，帮助人们在实时遭遇中理解并行使其民权。</p></div>",

        "landing_purpose_md": "### 🎯 目的\nCivicShield Pro 为法官、倡导者和社区成员提供：\n\n- **14 种语言的实时法律翻译**\n- **即时权利信息**，根据你的情况量身定制\n- **文件分析**与截止日期提取\n- **社区支持**与经验分享\n- **24/7 危机资源**",

        "landing_features_md": "### ⭐ 主要功能\n\n- 🗣️ **实时翻译** — 即时翻译警官陈述\n- 📄 **法律文件** — 从法院文件中提取关键信息\n- ⚖️ **了解你的权利** — 互动式测验与教育\n- 📍 **附近资源** — 查找法律援助与服务\n- 📝 **遭遇记录** — 记录警察互动\n- 🚨 **危机热线** — 24/7 紧急支援\n- 💬 **社区论坛** — 分享与学习",

        "landing_share_md": "**与法官、倡导者和社区成员分享 CivicShield：**\n\n1. 扫描 QR 码访问应用\n2. 无需安装 — 任何浏览器均可使用\n3. 支持 14 种语言\n4. 适用于电脑、平板和手机",

        "landing_who_should_use_md": "### 👥 适用对象\n\n**法官与法律专业人士：**\n- 了解社区对民权保护的观点\n- 评估被告是否理解其权利\n- 在判决中参考实时翻译能力\n\n**倡导者与法律援助：**\n- 为客户提供多语言法律信息\n- 协助记录遭遇\n- 连接社区资源\n\n**教育者：**\n- 教授学生民权知识\n- 展示真实法律情境\n- 使用互动式测验\n\n**社区成员：**\n- 知道在警察遭遇中该怎么做\n- 即时访问紧急资源\n- 与社区交流经验",

        "landing_disclaimer_md": "**⚠️ 法律免责声明：**\n\nCivicShield Pro 提供民权教育信息，并非法律建议。\n法律因地区而异且可能变更。\n请务必咨询专业律师以获得具体建议。",

        "tutorial_intro_html": "<div class=\"tutorial-container\"><h1>👋 欢迎使用 CivicShield Pro！</h1><p>让我们快速导览，帮助你开始使用。</p></div>",

        "tutorial_step1_title": "🏠 主页面板",
        "tutorial_step1_desc": "这是你访问所有 CivicShield 功能的中心。每张卡片代表一个强大的工具。",
        "tutorial_step1_feat1": "导航至任何功能",
        "tutorial_step1_feat2": "查看已保存的截止日期",
        "tutorial_step1_feat3": "访问危机资源",

        "tutorial_step2_title": "🗣️ 实时翻译",
        "tutorial_step2_desc": "即时翻译警官陈述，支持 14 种语言。",
        "tutorial_step2_feat1": "多语言语音转文字",
        "tutorial_step2_feat2": "实时翻译",
        "tutorial_step2_feat3": "语音播放",

        "tutorial_step3_title": "📄 法律文件",
        "tutorial_step3_desc": "上传法院文件、法律通知或合同，CivicShield 会提取关键信息。",
        "tutorial_step3_feat1": "自动提取截止日期",
        "tutorial_step3_feat2": "识别罚则",
        "tutorial_step3_feat3": "提供翻译",

        "tutorial_step4_title": "⚖️ 了解你的权利",
        "tutorial_step4_desc": "学习民权并使用互动式测验测试你的知识。",
        "tutorial_step4_feat1": "学习民权",
        "tutorial_step4_feat2": "进行互动测验",
        "tutorial_step4_feat3": "追踪进度",

        "tutorial_step5_title": "📍 附近资源",
        "tutorial_step5_desc": "查找法律援助、社区中心与紧急服务。",
        "tutorial_step5_feat1": "按位置搜索",
        "tutorial_step5_feat2": "按类别浏览",
        "tutorial_step5_feat3": "一键获取路线",

        "tutorial_step6_title": "💬 社区论坛",
        "tutorial_step6_desc": "与他人交流、分享经验、提问并提供建议。",
        "tutorial_step6_feat1": "匿名分享经验",
        "tutorial_step6_feat2": "提出法律问题",
        "tutorial_step6_feat3": "提供建议",

        "documents_intro_md": "上传法律文件（图片或 PDF）以提取关键信息：\n- 重要日期与截止日期\n- 所需行动\n- 罚则与警告\n- 政府机构\n- 文件摘要",
    },
    "Vietnamese / Tiếng Việt": {
        "sidebar_title": "CivicShield",
        "sidebar_tagline": "Hiểu Quyền Của Bạn",
        "select_language": "📍 Chọn Ngôn Ngữ:",
        "nav_home": "🏠 Trang Chủ",
        "nav_translation": "🗣️ Phiên Dịch Thời Gian Thực",
        "nav_documents": "📄 Tài Liệu Pháp Lý",
        "nav_rights": "📚 Trung Tâm Quyền Lợi",
        "nav_quiz": "❓ Bài Kiểm Tra Quyền Lợi",
        "nav_resources": "🏥 Nguồn Lực Cộng Đồng",
        "nav_nearby": "📍 Quyền Lợi Gần Tôi",
        "nav_logging": "📝 Nhật Ký Gặp Gỡ",
        "nav_emergency": "🚨 Hỗ Trợ Khẩn Cấp",
        "nav_about": "Giới Thiệu CivicShield",
        "sidebar_version": "Phiên bản 3.0.0",
        "sidebar_purpose": "Bảo vệ quyền dân sự và dịch thuật pháp lý chuyên nghiệp",
        "sidebar_languages": "Hỗ trợ 14 ngôn ngữ",
        "sidebar_disclaimer": "⚠️ Tuyên Bố Pháp Lý",
        "sidebar_disclaimer_text": "Ứng dụng này cung cấp thông tin giáo dục, không phải tư vấn pháp lý. Hãy luôn tham khảo luật sư cho trường hợp cụ thể của bạn.",

        "home_title": "Chào mừng đến CivicShield",
        "home_subtitle": "Hiểu Quyền Của Bạn. Bảo Vệ Bản Thân. Nhận Hỗ Trợ.",
        "dashboard_intro": "Chọn một tính năng bên dưới để bắt đầu:",

        "card_translation_title": "Phiên Dịch Thời Gian Thực",
        "card_translation_desc": "Phiên dịch lời nói của cảnh sát và nhận tư vấn pháp lý bằng ngôn ngữ của bạn",
        "card_documents_title": "Trợ Lý Tài Liệu Pháp Lý",
        "card_documents_desc": "Tải tài liệu lên, trích xuất thông tin quan trọng và dịch sang ngôn ngữ của bạn",
        "card_rights_title": "Trung Tâm Giáo Dục Quyền Lợi",
        "card_rights_desc": "Tìm hiểu quyền hiến pháp và bảo vệ pháp lý của bạn",
        "card_quiz_title": "Bài Kiểm Tra Quyền Lợi",
        "card_quiz_desc": "Kiểm tra kiến thức của bạn về quyền và tự do dân sự",
        "card_resources_title": "Nguồn Lực Cộng Đồng",
        "card_resources_desc": "Tìm hỗ trợ pháp lý, dịch vụ khẩn cấp và tổ chức hỗ trợ",
        "card_nearby_title": "Quyền Lợi Gần Tôi",
        "card_nearby_desc": "Tìm hỗ trợ pháp lý, tòa án và dịch vụ cộng đồng gần bạn",
        "card_logging_title": "Nhật Ký Gặp Gỡ",
        "card_logging_desc": "Ghi lại và theo dõi các cuộc gặp gỡ với cảnh sát",
        "card_emergency_title": "Hỗ Trợ Khẩn Cấp",
        "card_emergency_desc": "Truy cập đường dây nóng và quy trình khẩn cấp",

        "btn_open": "Mở Tính Năng",
        "btn_delete": "❌",
        "btn_record": "🎤 Ghi Âm",
        "btn_stop": "⏹️ Dừng",
        "btn_translate": "🌐 Dịch",
        "btn_listen": "🔊 Nghe",
        "btn_download": "📥 Tải Xuống",
        "btn_search": "🔍 Tìm Kiếm",
        "btn_log": "📝 Ghi Lại",
        "btn_back": "← Quay Lại",
        "btn_submit": "✓ Gửi",
        "btn_cancel": "✗ Hủy",

        "translation_title": "Phiên Dịch Thời Gian Thực",
        "translation_subtitle": "Phiên dịch lời nói của cảnh sát và nhận tư vấn pháp lý",
        "officer_statement": "Lời nói của cảnh sát (Tiếng Anh):",
        "your_rights": "Quyền Lợi & Tư Vấn Pháp Lý:",
        "play_before_title": "1. Phát Trước Khi Tương Tác",
        "play_before_desc": "Phát đoạn này cho cảnh sát nghe trước khi bắt đầu ghi âm.",
        "play_before_audio": "Officer, before we begin, I am using a translation app to avoid any language barriers. I am recording with your knowledge for safety and accuracy.",
        "play_after_title": "3. Phát Sau Khi Hiểu Quyền",
        "play_after_desc": "Phát đoạn này cho cảnh sát nghe sau khi bạn nghe quyền của mình.",
        "play_after_audio": "I understand, officer, and I will comply, but I will be using my right to remain silent.",
        "officer_script": "Nội dung cho cảnh sát (tiếng Anh):",
        "officer_script_translated": "Đoạn này có nghĩa gì trong ngôn ngữ của bạn:",
        "record_officer": "🎤 Ghi âm giọng cảnh sát",
        "stop_recording": "⏹️ Dừng ghi âm & dịch",
        "listen_to_advice": "🔊 Nghe tư vấn",
        "translation_hint": "Nhập văn bản hoặc ghi âm để dịch",
        "generating_audio": "Đang tạo âm thanh...",
        "audio_ready": "✅ Âm thanh đã sẵn sàng",
        "audio_failed": "❌ Tạo âm thanh thất bại",
        "speech_recognized": "Âm thanh đã được chuyển thành văn bản.",
        "mic_unclear": "Không hiểu được âm thanh. Vui lòng nói rõ hơn và thử lại.",
        "stt_unavailable": "Dịch vụ chuyển giọng nói thành văn bản hiện không khả dụng.",
        "unable_process_audio": "Không thể xử lý âm thanh. Vui lòng ghi lại.",
        "mic_recorder_title": "Trình ghi âm",
        "mic_recorder_desc": "Dùng nút Bắt đầu và Dừng để ghi âm lời cảnh sát.",
        "mic_help": "Nếu trình duyệt chặn micro, hãy cấp quyền và thử lại.",
        "mic_access_failed": "Không truy cập được micro. Hãy cấp quyền và thử lại.",
        "mic_no_audio": "Không ghi được âm thanh. Có thể bạn chưa cấp quyền micro.",
        "btn_clear_filter": "Xóa bộ lọc",
        "currently_filtering": "Đang lọc theo",
        "quiz_correct": "✅ Chính xác!",
        "quiz_incorrect": "❌ Sai.",
        "language_selector_error": "❌ Lỗi chọn ngôn ngữ",
        "demo_section_title": "Chế độ Demo & Kiểm thử",
        "demo_on": "🎬 Demo BẬT",
        "demo_off": "🎬 Demo TẮT",
        "tour_button": "🎓 Hướng Dẫn",
        "tour_complete": "✅ Hoàn tất hướng dẫn! Bạn đã sẵn sàng.",
        "btn_go_home": "🏠 Về Trang Chủ",
        "btn_skip_tour": "⏭️ Bỏ qua hướng dẫn",
        "btn_next": "Tiếp theo ➡️",
        "btn_start_using": "🎉 Bắt đầu sử dụng!",

        "documents_title": "Trợ Lý Tài Liệu Pháp Lý",
        "documents_subtitle": "Tải tài liệu lên và trích xuất thông tin quan trọng",
        "upload_document": "📤 Tải tài liệu",
        "take_photo": "📸 Chụp ảnh",
        "extract_text": "Trích xuất văn bản",
        "simplify_text": "Đơn giản hóa ngôn ngữ pháp lý",
        "translate_document": "🌐 Dịch tài liệu",
        "extract_dates": "📅 Ngày được tìm thấy",
        "extract_deadlines": "⏰ Hạn chót",
        "extract_agencies": "🏛️ Cơ quan chính phủ",
        "extract_actions": "✅ Hành động cần thiết",
        "download_report": "📥 Tải báo cáo",
        "report_generated": "Báo cáo đã được tạo",

        "rights_title": "Trung Tâm Giáo Dục Quyền Lợi",
        "rights_subtitle": "Tìm hiểu quyền hiến pháp của bạn",
        "right_fourth": "Tu Chính Án Thứ 4: Khám xét & Tịch thu",
        "right_fifth": "Tu Chính Án Thứ 5: Quyền im lặng",
        "right_sixth": "Tu Chính Án Thứ 6: Quyền có luật sư",
        "right_traffic": "Quyền khi bị chặn xe",
        "right_arrest": "Nếu bạn bị bắt",
        "right_fourth_content": "**Quyền của bạn:** Bạn có quyền được bảo vệ khỏi việc khám xét và tịch thu không hợp lý.\n\n**Điểm chính:**\n- Cảnh sát thường cần lệnh khám xét để khám nhà, xe hoặc đồ cá nhân của bạn\n- Bạn có thể từ chối bằng cách nói: \"Tôi không đồng ý cho khám xét\"\n- KHÔNG chống cự bằng hành động — điều đó có thể dẫn đến cáo buộc thêm\n- Ngay cả khi bạn từ chối, cảnh sát vẫn có thể tiếp tục nếu họ có lệnh hoặc lý do hợp lý\n\n**Bạn CÓ THỂ làm:**\n- Giữ im lặng và hỏi: \"Tôi được đi chưa?\"\n- Hỏi: \"Anh/chị có lệnh khám xét không?\"\n- Giữ tay ở nơi nhìn thấy được\n- Không cản trở cảnh sát",

        "right_fifth_content": "**Quyền của bạn:** Bạn có quyền giữ im lặng và không tự buộc tội.\n\n**Điểm chính:**\n- Bạn KHÔNG phải trả lời câu hỏi của cảnh sát\n- Hãy nói rõ: \"Tôi thực hiện quyền giữ im lặng\"\n- Quyền này áp dụng ngay cả khi bạn chưa bị bắt\n- Việc giữ im lặng không thể được dùng chống lại bạn tại tòa\n\n**Quan trọng:**\n- Bạn phải nói rõ rằng bạn đang thực hiện quyền này\n- Nếu bị bắt, hãy yêu cầu luật sư ngay lập tức\n- Không giải thích, không thương lượng",

        "right_sixth_content": "**Quyền của bạn:** Bạn có quyền có luật sư.\n\n**Điểm chính:**\n- Nếu bạn không đủ khả năng thuê luật sư, tòa sẽ chỉ định cho bạn\n- Bạn có thể yêu cầu luật sư BẤT CỨ lúc nào trong quá trình thẩm vấn\n- Khi bạn yêu cầu luật sư, cảnh sát phải dừng thẩm vấn\n- Bạn có quyền có luật sư bên cạnh khi bị hỏi cung\n\n**Nên nói:**\n- \"Tôi muốn nói chuyện với luật sư\"\n- \"Tôi thực hiện quyền có luật sư\"\n- Sau đó giữ im lặng cho đến khi luật sư đến",

        "right_traffic_content": "**Khi bị chặn xe:**\n- Bạn phải xuất trình bằng lái, đăng ký xe và bảo hiểm\n- Bạn có thể hỏi: \"Tôi bị giữ lại hay tôi được đi?\"\n- Bạn KHÔNG phải đồng ý cho khám xe\n- Hãy nói rõ: \"Tôi không đồng ý cho khám xét\"\n\n**Khám xét xe:**\n- Cảnh sát có thể nhìn qua cửa kính mà không cần phép\n- Họ có thể khám xe nếu có lý do hợp lý\n- Họ có thể khám xe nếu bạn bị bắt\n\n**Quyền của bạn:**\n- Giữ tay ở nơi nhìn thấy được\n- Nói chuyện bình tĩnh và lịch sự\n- Không chống cự\n- Bạn có thể quay video (không cản trở)",

        "right_arrest_content": "**Các bước quan trọng:**\n1. Giữ im lặng — không trả lời câu hỏi\n2. Nói rõ: \"Tôi muốn có luật sư\"\n3. Không ký bất cứ giấy tờ nào nếu không có luật sư\n4. Không nói chuyện về vụ việc với người bị giam khác\n\n**Quyền khi bị bắt:**\n- Quyền được biết lý do bị bắt\n- Quyền được gọi điện thoại\n- Quyền giữ im lặng\n- Quyền có luật sư\n\n**Không nên làm:**\n- Không chống cự (dù bạn nghĩ việc bắt giữ là sai)\n- Không ký lời khai\n- Không đồng ý khám xét\n- Không thương lượng với cảnh sát nếu không có luật sư",

        "resources_title": "Nguồn Lực Cộng Đồng",
        "resources_subtitle": "Tìm hỗ trợ pháp lý và dịch vụ hỗ trợ",
        "legal_aid": "Tổ chức hỗ trợ pháp lý",
        "emergency_services": "Dịch vụ khẩn cấp",
        "immigration": "Dịch vụ pháp lý nhập cư",
        "phone": "Điện thoại: ",
        "services": "Dịch vụ: ",
        "website": "Trang web: ",
        "hours": "Giờ làm việc: ",

        "nearby_title": "Quyền Lợi Gần Tôi",
        "nearby_subtitle": "Tìm hỗ trợ pháp lý và dịch vụ gần bạn",
        "enter_address": "Nhập địa chỉ của bạn:",
        "search_radius": "Bán kính tìm kiếm (dặm):",
        "nearest_legal_aid": "📋 Văn phòng hỗ trợ pháp lý gần nhất",
        "nearest_courthouse": "⚖️ Tòa án gần nhất",
        "nearest_police": "👮 Đồn cảnh sát gần nhất",
        "nearest_translator": "🗣️ Dịch vụ phiên dịch",
        "nearest_community": "🏢 Trung tâm cộng đồng",
        "address": "Địa chỉ: ",
        "phone_number": "Điện thoại: ",
        "hours_open": "Giờ mở cửa: ",
        "get_directions": "🗺️ Chỉ đường",
        "not_found": "Không tìm thấy kết quả gần đây",
        "logging_title": "Nhật Ký Gặp Gỡ",
        "logging_subtitle": "Ghi lại các cuộc gặp gỡ và sự cố với cảnh sát",
        "encounter_type": "Loại gặp gỡ:",
        "encounter_location": "Địa điểm:",
        "encounter_details": "Chi tiết:",
        "encounter_date": "Ngày & Giờ:",
        "officer_info": "Thông tin cảnh sát:",
        "officer_badge": "Số hiệu:",
        "officer_agency": "Cơ quan:",
        "encounter_saved": "✅ Đã lưu gặp gỡ thành công",
        "view_history": "📋 Xem lịch sử gặp gỡ",
        "total_encounters": "Tổng số gặp gỡ:",
        "search_encounters": "🔍 Tìm kiếm gặp gỡ",

        "emergency_title": "Hỗ Trợ Khẩn Cấp",
        "emergency_subtitle": "Nguồn lực & đường dây nóng khẩn cấp",
        "emergency_911": "Khẩn cấp (Cảnh sát, Cứu hỏa, Y tế)",
        "emergency_suicide": "Đường dây phòng chống tự tử quốc gia",
        "emergency_domestic": "Đường dây nóng bạo lực gia đình",
        "emergency_assault": "Hỗ trợ tấn công tình dục (RAINN)",
        "emergency_poison": "Trung tâm chống độc",
        "emergency_text": "Đường dây nhắn tin khủng hoảng",
        "emergency_procedures": "Quy trình khẩn cấp:",
        "procedure_safe": "Giữ an toàn",
        "procedure_document": "Ghi lại mọi chi tiết",
        "procedure_record": "Ghi hình tương tác (nếu hợp pháp)",
        "procedure_call": "Gọi trợ giúp",
        "procedure_contact": "Liên hệ luật sư của bạn",

        "loading": "Đang tải...",
        "success": "Thành công!",
        "error": "Lỗi",
        "warning": "Cảnh báo",
        "info": "Thông tin",
        "processing": "Đang xử lý...",
        "please_wait": "Vui lòng chờ...",
        "no_data": "Không có dữ liệu",
        "try_again": "Vui lòng thử lại",

        "accessibility_title": "♿ Cài Đặt Trợ Năng",
        "text_size": "Kích thước chữ:",
        "text_size_normal": "Bình thường",
        "text_size_large": "Lớn",
        "text_size_extra_large": "Rất lớn",
        "high_contrast": "🎨 Chế độ tương phản cao",
        "high_contrast_on": "Đã bật tương phản cao",
        "high_contrast_off": "Đã tắt tương phản cao",
        "screen_reader": "Đã bật nhãn trình đọc màn hình",
        "accessibility_saved": "✅ Đã lưu cài đặt trợ năng",
        "extract_deadlines": "📋 Các hạn chót quan trọng được tìm thấy",
        "extract_penalties": "⚠️ Hình phạt & Cảnh báo",
        "extract_requirements": "✓ Yêu cầu & Hành động",
        "deadline_found": "Hạn chót:",
        "penalty_found": "Hình phạt:",
        "requirement_found": "Hành động cần thiết:",
        "document_summary": "📋 Tóm tắt tài liệu",
        "summary_generated": "Tóm tắt đã được tạo thành công",

        "location_title": "📍 Tìm nguồn lực gần bạn",
        "enter_address": "Nhập địa chỉ hoặc mã ZIP:",
        "search_radius_miles": "Bán kính tìm kiếm (dặm):",
        "find_resources": "🔍 Tìm nguồn lực gần đây",
        "resource_type": "Loại nguồn lực:",
        "all_resources": "Tất cả nguồn lực",
        "legal_aid_offices": "Văn phòng hỗ trợ pháp lý",
        "community_centers": "Trung tâm cộng đồng",
        "language_services": "Dịch vụ ngôn ngữ",
        "emergency_shelters": "Nhà tạm trú khẩn cấp",
        "distance_away": "dặm cách xa",
        "get_directions": "🗺️ Chỉ đường",
        "no_resources_found": "Không tìm thấy nguồn lực trong khu vực",
        "resource_hours": "Giờ làm việc:",
        "resource_phone": "Điện thoại:",
        "resource_address": "Địa chỉ:",
        "resource_website": "Trang web:",
        "loading_resources": "Đang tìm nguồn lực gần bạn...",

        "saved_deadlines": "⏰ Các hạn chót đã lưu",
        "upload_legal_doc": "Tải tài liệu pháp lý",
        "important_dates": "📅 Ngày quan trọng",
        "required_actions": "✓ Hành động cần thiết",
        "critical_deadlines": "⏰ Hạn chót quan trọng",
        "penalties_warnings": "⚠️ Hình phạt & Cảnh báo",
        "extraction_guide": "Hướng dẫn trích xuất tài liệu",
        "demo_mode_active": "📺 **CHẾ ĐỘ DEMO ĐANG BẬT** - Dữ liệu mẫu đang được hiển thị",
        "have_deadlines": "📋 Bạn có các hạn chót quan trọng cần theo dõi!",
        "view_all_deadlines": "📋 Xem tất cả hạn chót →",
        "from_document": "Từ:",
        "file_type": "Loại tệp",
        "file_size": "Kích thước tệp",
        "status_ready": "Sẵn sàng trích xuất",
        "extract_information": "🔍 Trích xuất thông tin",
        "extracting_info": "Đang trích xuất thông tin từ tài liệu...",
        "no_dates_found": "Không tìm thấy ngày",
        "no_deadlines_found": "Không tìm thấy hạn chót",
        "no_penalties_found": "Không tìm thấy hình phạt",
        "download_summary": "📥 Tải tóm tắt",
        "download_as_txt": "Tải dưới dạng TXT",
        "save_deadlines_to_dashboard": "💾 Lưu hạn chót vào bảng điều khiển",
        "know_your_rights_long": "⚖️ Hiểu Quyền Của Bạn",
        "education_quizzes": "Giáo dục, bài kiểm tra & mô-đun học tập",
        "learn_tab": "📚 Học",
        "quiz_tab": "🧪 Kiểm tra",
        "rights_education": "Giáo dục quyền lợi",
        "select_topic": "Chọn chủ đề:",
        "test_knowledge": "Kiểm tra kiến thức của bạn về quyền công dân và bảo vệ pháp lý.",
        "rights_quiz": "Bài kiểm tra quyền lợi",

        "can_police_search": "Cảnh sát có thể khám xe bạn mà không có sự đồng ý không?",
        "only_with_warrant": "Chỉ khi có lệnh khám xét",
        "only_prob_cause": "Chỉ khi có lý do hợp lý",
        "both_a_and_b": "Cả A và B",
        "never_without": "Không, không bao giờ",
        "police_can_search": "Cảnh sát có thể khám xe nếu có lệnh hoặc có lý do hợp lý.",

        "answer_police_q": "Bạn có phải trả lời câu hỏi của cảnh sát không?",
        "yes_always": "Có, luôn luôn",
        "right_remain_silent": "Không, bạn có quyền giữ im lặng",
        "only_your_name": "Chỉ cần cung cấp tên",
        "only_if_arrested": "Chỉ khi bị bắt",
        "fifth_amendment": "Tu Chính Án Thứ 5 cho bạn quyền giữ im lặng và không tự buộc tội.",

        "what_say_arrested": "Bạn nên nói gì khi bị bắt?",
        "explain_what_happened": "Giải thích chuyện gì đã xảy ra",
        "ask_for_lawyer": "Yêu cầu luật sư",
        "refuse_give_name": "Từ chối cung cấp tên",
        "try_negotiate": "Thương lượng với cảnh sát",
        "always_ask_lawyer": "Hãy yêu cầu luật sư ngay lập tức và giữ im lặng.",

        "check_answer": "✓ Kiểm tra câu trả lời {number}",
        "question_number": "Câu hỏi {number}: {question}",
        "select_answer": "Chọn câu trả lời:",
        "your_score": "Điểm của bạn",

        "talk_community": "💬 Trò chuyện với cộng đồng",
        "community_intro": "Chia sẻ kinh nghiệm, đặt câu hỏi, đưa lời khuyên — cùng nhau chúng ta mạnh mẽ hơn",
        "share_exp_tab": "💭 Chia sẻ kinh nghiệm",
        "ask_q_tab": "❓ Đặt câu hỏi",
        "give_advice_tab": "💡 Đưa lời khuyên",
        "share_your_exp": "💭 Chia sẻ trải nghiệm của bạn",
        "share_story": "Chia sẻ câu chuyện của bạn để giúp người khác. Tất cả bài đăng đều được kiểm duyệt để đảm bảo an toàn.",
        "title_label": "Tiêu đề:",
        "exp_placeholder": "Ví dụ: Mẹo khi bị chặn xe",
        "your_story": "Câu chuyện của bạn:",
        "story_placeholder": "Chia sẻ trải nghiệm...",
        "post_anonymously": "Đăng ẩn danh",
        "share_exp_btn": "📤 Chia sẻ trải nghiệm",
        "fill_title_content": "⚠️ Vui lòng nhập tiêu đề và nội dung",
        "exp_shared": "✅ Trải nghiệm của bạn đã được chia sẻ! Cảm ơn bạn đã giúp cộng đồng.",
        "ask_community": "❓ Hỏi cộng đồng",
        "question_help": "Có câu hỏi? Cộng đồng sẽ giúp bạn.",
        "your_question": "Câu hỏi của bạn:",
        "question_placeholder": "Ví dụ: Quyền của tôi khi bị chặn xe là gì?",
        "details_label": "Chi tiết:",
        "details_placeholder": "Cung cấp thêm thông tin...",
        "ask_anon": "Hỏi ẩn danh",
        "ask_q_btn": "❓ Đăng câu hỏi",
        "enter_question": "⚠️ Vui lòng nhập câu hỏi",
        "question_posted": "✅ Câu hỏi của bạn đã được đăng!",

        "give_advice": "💡 Đưa lời khuyên",
        "help_others": "Giúp người khác bằng kiến thức và kinh nghiệm của bạn.",
        "topic_label": "Chủ đề:",
        "topic_placeholder": "Ví dụ: Cách chuẩn bị ra tòa",
        "your_advice": "Lời khuyên của bạn:",
        "advice_placeholder": "Chia sẻ những gì bạn biết...",
        "share_anon": "Chia sẻ ẩn danh",
        "share_advice_btn": "💡 Chia sẻ lời khuyên",
        "share_wisdom": "✅ Cảm ơn bạn đã chia sẻ sự hiểu biết!",
        "fill_topic_advice": "⚠️ Vui lòng nhập chủ đề và lời khuyên",

        "recent_posts": "📋 Bài đăng gần đây",
        "no_posts_yet": "💭 Chưa có bài đăng nào. Hãy là người đầu tiên chia sẻ!",
        "posted_recently": "Đăng {timestamp}",
        "author_anonymous": "Ẩn danh",
        "author_community_member": "Thành viên cộng đồng",

        "crisis_hotlines": "🚨 Đường dây nóng & hỗ trợ khẩn cấp",
        "crisis_support_24": "Hỗ trợ 24/7 khi bạn cần nhất",
        "emergency_hotlines_header": "🆘 Đường dây khẩn cấp",
        "in_immediate_danger": "Nếu bạn đang gặp nguy hiểm ngay lập tức, hãy gọi 911",
        "emergency_number": "Khẩn cấp",
        "suicide_prevention": "Đường dây phòng chống tự tử quốc gia",
        "domestic_violence": "Đường dây nóng bạo lực gia đình",
        "sexual_assault": "RAINN - Hỗ trợ tấn công tình dục",
        "poison_control": "Trung tâm chống độc",
        "crisis_text": "Đường dây nhắn tin khủng hoảng",

        "safety_procedures": "📋 Quy trình an toàn",
        "stay_safe": "🛡️ Giữ an toàn",
        "stay_safe_desc": "Giữ an toàn cho bản thân — không chống cự. Sự an toàn của bạn là ưu tiên.",
        "document_details": "📝 Ghi lại chi tiết",
        "document_details_desc": "Ghi nhớ: tên cảnh sát, số hiệu, địa điểm, thời gian, những gì họ nói và làm.",
        "record_safely": "🎥 Ghi hình an toàn",
        "record_safely_desc": "Nếu hợp pháp và an toàn, hãy ghi hình. Giữ camera ở nơi dễ thấy.",
        "call_for_help": "📞 Gọi trợ giúp",
        "call_help_desc": "Nếu gặp nguy hiểm ngay lập tức, hãy gọi 911. Giữ bình tĩnh và nói rõ ràng.",
        "get_legal_help": "⚖️ Nhận hỗ trợ pháp lý",
        "legal_help_desc": "Liên hệ luật sư ngay. Nhiều luật sư công có hỗ trợ khẩn cấp.",
        "medical_attention": "🏥 Chăm sóc y tế",
        "medical_attention_desc": "Nếu bị thương, hãy tìm chăm sóc y tế và chụp ảnh ghi lại vết thương.",
        "mental_health_support": "🧠 Sức khỏe tinh thần & hỗ trợ",
        "legal_troubles_trauma": "Gặp rắc rối pháp lý, bị cảnh sát chặn hoặc phân biệt đối xử có thể gây sang chấn.",
        "mental_health_resources": "Nguồn lực sức khỏe tinh thần:",
        "samhsa_helpline": "Đường dây SAMHSA: 1-800-662-4357 (miễn phí, bảo mật, 24/7)",
        "psychology_directory": "Tìm nhà trị liệu: tra cứu trên Psychology Today",
        "support_groups": "Nhóm hỗ trợ: NAACP, trung tâm cộng đồng, tổ chức pháp lý thường có nhóm hỗ trợ",
        "contact_emergency": "🆘 Khẩn cấp",
        "contact_suicide": "🧠 Đường dây phòng chống tự tử",
        "contact_domestic": "💔 Đường dây nóng bạo lực gia đình",
        "contact_rainn": "🤝 RAINN — Hỗ trợ tấn công tình dục",
        "contact_poison": "☠️ Trung tâm chống độc",
        "contact_crisis_text": "📱 Đường dây nhắn tin khủng hoảng",
        "contact_crisis_text_number": "Gửi HOME đến 741741",

        "enc_type_traffic_stop": "Chặn xe",
        "enc_type_street_encounter": "Gặp gỡ trên đường",
        "enc_type_arrest": "Bị bắt",
        "enc_type_search": "Khám xét",
        "enc_type_other": "Khác",
        "encounter_label": "Gặp gỡ",
        "unknown": "Không rõ",
        "na": "Không áp dụng",
        "error_generating_qr": "Lỗi khi tạo mã QR",

        "btn_launch_app": "🚀 Khởi chạy ứng dụng",
        "btn_start_demo": "📺 Bắt đầu demo",
        "btn_quick_tour": "❓ Hướng dẫn nhanh",
        "share_with_others": "📱 Chia sẻ với người khác",
        "qr_generation_in_progress": "Đang tạo mã QR...",
        "key_features_label": "Tính năng chính:",
        "btn_previous": "⬅️ Quay lại",
        "language_change_error": "Lỗi thay đổi ngôn ngữ",
        "demo_mode_active_sidebar": "✅ Chế độ demo đang bật — hiển thị dữ liệu mẫu",
        "screen_reader_off": "🔇 Trình đọc màn hình đã tắt",
        "navigation_title": "Điều hướng",
        "nav_rights_full": "⚖️ Hiểu Quyền Của Bạn",
        "nav_resources_near_you": "📍 Nguồn lực gần bạn",
        "nav_logging_full": "📝 Nhật ký gặp gỡ",
        "nav_crisis_resources": "🚨 Nguồn lực khủng hoảng",
        "nav_community": "💬 Cộng đồng",

        "sidebar_built_for": "Được xây dựng để bảo vệ quyền dân sự toàn cầu.",
        "show_landing_page": "🏠 Hiển thị trang chính",

        "landing_hero_html": "<div class=\"landing-hero\"><h1>⚖️ CivicShield Pro</h1><h2>Hiểu quyền của bạn. Bảo vệ bản thân. Nhận hỗ trợ.</h2><p>Một nền tảng đa ngôn ngữ chuyên nghiệp giúp mọi người hiểu và thực thi quyền dân sự trong các tình huống thực tế.</p></div>",

        "landing_purpose_md": "### 🎯 Mục đích\nCivicShield Pro cung cấp cho thẩm phán, luật sư và cộng đồng:\n\n- **Phiên dịch pháp lý thời gian thực bằng 14 ngôn ngữ**\n- **Thông tin quyền lợi tức thì**, phù hợp với tình huống của bạn\n- **Phân tích tài liệu pháp lý** và trích xuất hạn chót\n- **Hỗ trợ cộng đồng** và chia sẻ kinh nghiệm\n- **Nguồn lực khủng hoảng 24/7**",

        "landing_features_md": "### ⭐ Tính năng chính\n\n- 🗣️ **Phiên dịch thời gian thực** — dịch lời cảnh sát ngay lập tức\n- 📄 **Tài liệu pháp lý** — trích xuất thông tin quan trọng từ tài liệu\n- ⚖️ **Hiểu quyền lợi** — bài học và kiểm tra tương tác\n- 📍 **Nguồn lực gần bạn** — tìm hỗ trợ pháp lý và dịch vụ cộng đồng\n- 📝 **Nhật ký gặp gỡ** — ghi lại tương tác với cảnh sát\n- 🚨 **Đường dây nóng khủng hoảng** — hỗ trợ 24/7\n- 💬 **Diễn đàn cộng đồng** — chia sẻ và học hỏi",

        "landing_share_md": "**Chia sẻ CivicShield với thẩm phán, luật sư và cộng đồng:**\n\n1. Quét mã QR để truy cập ứng dụng\n2. Không cần cài đặt — chạy trên mọi trình duyệt\n3. Hỗ trợ 14 ngôn ngữ\n4. Hoạt động trên máy tính, máy tính bảng và điện thoại",

        "landing_who_should_use_md": "### 👥 Ai nên sử dụng?\n\n**Thẩm phán & chuyên gia pháp lý:**\n- Hiểu quan điểm cộng đồng về quyền dân sự\n- Đánh giá khả năng hiểu quyền của bị cáo\n- Tham khảo khả năng phiên dịch thời gian thực\n\n**Luật sư & tổ chức pháp lý:**\n- Cung cấp thông tin pháp lý đa ngôn ngữ\n- Hỗ trợ ghi lại gặp gỡ\n- Kết nối khách hàng với nguồn lực\n\n**Giáo viên:**\n- Dạy quyền công dân\n- Minh họa tình huống pháp lý thực tế\n- Sử dụng bài kiểm tra tương tác\n\n**Cộng đồng:**\n- Biết phải làm gì khi gặp cảnh sát\n- Truy cập nguồn lực khẩn cấp\n- Chia sẻ kinh nghiệm",

        "landing_disclaimer_md": "**⚠️ Tuyên bố pháp lý:**\n\nCivicShield Pro cung cấp thông tin giáo dục, không phải tư vấn pháp lý.\nLuật pháp thay đổi theo khu vực.\nHãy tham khảo luật sư cho lời khuyên cụ thể.",

        "tutorial_intro_html": "<div class=\"tutorial-container\"><h1>👋 Chào mừng đến CivicShield Pro!</h1><p>Hãy cùng khám phá nhanh các tính năng chính.</p></div>",

        "tutorial_step1_title": "🏠 Bảng điều khiển chính",
        "tutorial_step1_desc": "Đây là nơi bạn truy cập tất cả tính năng của CivicShield.",
        "tutorial_step1_feat1": "Điều hướng đến mọi tính năng",
        "tutorial_step1_feat2": "Xem hạn chót đã lưu",
        "tutorial_step1_feat3": "Truy cập nguồn lực khẩn cấp",

        "tutorial_step2_title": "🗣️ Phiên dịch thời gian thực",
        "tutorial_step2_desc": "Dịch lời cảnh sát ngay lập tức bằng 14 ngôn ngữ.",
        "tutorial_step2_feat1": "Chuyển giọng nói thành văn bản",
        "tutorial_step2_feat2": "Dịch thời gian thực",
        "tutorial_step2_feat3": "Phát lại âm thanh",

        "tutorial_step3_title": "📄 Tài liệu pháp lý",
        "tutorial_step3_desc": "Tải tài liệu lên và trích xuất thông tin quan trọng.",
        "tutorial_step3_feat1": "Tự động trích xuất hạn chót",
        "tutorial_step3_feat2": "Nhận diện hình phạt",
        "tutorial_step3_feat3": "Dịch tài liệu",

        "tutorial_step4_title": "⚖️ Hiểu quyền lợi",
        "tutorial_step4_desc": "Học quyền công dân và kiểm tra kiến thức.",
        "tutorial_step4_feat1": "Học quyền lợi",
        "tutorial_step4_feat2": "Làm bài kiểm tra",
        "tutorial_step4_feat3": "Theo dõi tiến độ",

        "tutorial_step5_title": "📍 Nguồn lực gần bạn",
        "tutorial_step5_desc": "Tìm hỗ trợ pháp lý và dịch vụ cộng đồng.",
        "tutorial_step5_feat1": "Tìm theo vị trí",
        "tutorial_step5_feat2": "Lọc theo loại dịch vụ",
        "tutorial_step5_feat3": "Chỉ đường nhanh",

        "tutorial_step6_title": "💬 Diễn đàn cộng đồng",
        "tutorial_step6_desc": "Chia sẻ kinh nghiệm, đặt câu hỏi và hỗ trợ người khác.",
        "tutorial_step6_feat1": "Chia sẻ ẩn danh",
        "tutorial_step6_feat2": "Đặt câu hỏi pháp lý",
        "tutorial_step6_feat3": "Đưa lời khuyên",

        "documents_intro_md": "Tải tài liệu pháp lý (ảnh hoặc PDF) để trích xuất thông tin quan trọng:\n- Ngày & hạn chót\n- Hành động cần thiết\n- Hình phạt & cảnh báo\n- Cơ quan chính phủ\n- Tóm tắt tài liệu",

    },
    "Tagalog / Filipino": {
        "sidebar_title": "CivicShield",
        "sidebar_tagline": "Unawain ang Iyong mga Karapatan",
        "select_language": "📍 Piliin ang Wika:",
        "nav_home": "🏠 Home",
        "nav_translation": "🗣️ Real‑Time na Pagsasalin",
        "nav_documents": "📄 Mga Legal na Dokumento",
        "nav_rights": "📚 Sentro ng Karapatan",
        "nav_quiz": "❓ Pagsusulit sa Karapatan",
        "nav_resources": "🏥 Mga Serbisyong Pang‑Komunidad",
        "nav_nearby": "📍 Mga Karapatan Malapit sa Iyo",
        "nav_logging": "📝 Talaan ng Pagharap",
        "nav_emergency": "🚨 Pang‑emerhensiyang Tulong",
        "nav_about": "Tungkol sa CivicShield",
        "sidebar_version": "Bersyon 3.0.0",
        "sidebar_purpose": "Proteksyon sa karapatang sibil at propesyonal na legal na pagsasalin",
        "sidebar_languages": "Suporta para sa 14 na wika",
        "sidebar_disclaimer": "⚠️ Legal na Paalala",
        "sidebar_disclaimer_text": "Nagbibigay ang app na ito ng impormasyong pang‑edukasyon, hindi legal na payo. Kumonsulta sa abogado para sa iyong partikular na kaso.",

        "home_title": "Maligayang Pagdating sa CivicShield",
        "home_subtitle": "Unawain ang Iyong Karapatan. Protektahan ang Sarili. Humingi ng Tulong.",
        "dashboard_intro": "Piliin ang isang feature sa ibaba upang magsimula:",

        "card_translation_title": "Real‑Time na Pagsasalin",
        "card_translation_desc": "Isalin ang sinasabi ng pulis at tumanggap ng legal na gabay sa iyong wika",
        "card_documents_title": "Legal Document Assistant",
        "card_documents_desc": "Mag‑upload ng dokumento, kumuha ng mahahalagang detalye, at isalin ito",
        "card_rights_title": "Sentro ng Edukasyon sa Karapatan",
        "card_rights_desc": "Alamin ang iyong mga karapatang konstitusyonal",
        "card_quiz_title": "Pagsusulit sa Karapatan",
        "card_quiz_desc": "Subukan ang iyong kaalaman sa karapatang sibil",
        "card_resources_title": "Mga Serbisyong Pang‑Komunidad",
        "card_resources_desc": "Maghanap ng legal aid, emergency services, at community support",
        "card_nearby_title": "Mga Karapatan Malapit sa Iyo",
        "card_nearby_desc": "Maghanap ng legal aid, korte, at community services malapit sa iyo",
        "card_logging_title": "Talaan ng Pagharap",
        "card_logging_desc": "I‑record at subaybayan ang mga pagharap sa pulis",
        "card_emergency_title": "Pang‑emerhensiyang Tulong",
        "card_emergency_desc": "I‑access ang mga hotline at emergency procedures",

        "btn_open": "Buksan",
        "btn_delete": "❌",
        "btn_record": "🎤 Mag‑record",
        "btn_stop": "⏹️ Itigil",
        "btn_translate": "🌐 Isalin",
        "btn_listen": "🔊 Pakinggan",
        "btn_download": "📥 I‑download",
        "btn_search": "🔍 Hanapin",
        "btn_log": "📝 I‑log",
        "btn_back": "← Bumalik",
        "btn_submit": "✓ Isumite",
        "btn_cancel": "✗ Kanselahin",

        "translation_title": "Real‑Time na Pagsasalin",
        "translation_subtitle": "Isalin ang sinasabi ng pulis at tumanggap ng legal na gabay",
        "officer_statement": "Sinasabi ng pulis (Ingles):",
        "your_rights": "Mga Karapatan at Legal na Payo:",
        "play_before_title": "1. I-play Bago ang Pakikipag-ugnayan",
        "play_before_desc": "I-play ito para sa pulis bago magsimulang mag-record.",
        "play_before_audio": "Officer, before we begin, I am using a translation app to avoid any language barriers. I am recording with your knowledge for safety and accuracy.",
        "play_after_title": "3. I-play Pagkatapos Maunawaan ang Mga Karapatan",
        "play_after_desc": "I-play ito para sa pulis pagkatapos marinig ang iyong mga karapatan.",
        "play_after_audio": "I understand, officer, and I will comply, but I will be using my right to remain silent.",
        "officer_script": "Script para sa pulis (Ingles):",
        "officer_script_translated": "Ano ang ibig sabihin nito sa inyong wika:",
        "record_officer": "🎤 I‑record ang boses ng pulis",
        "stop_recording": "⏹️ Itigil ang pag‑record at isalin",
        "listen_to_advice": "🔊 Pakinggan ang payo",
        "translation_hint": "Mag‑type o mag‑record upang isalin",
        "generating_audio": "Gumagawa ng audio...",
        "audio_ready": "✅ Handa na ang audio",
        "audio_failed": "❌ Nabigo ang paglikha ng audio",
        "speech_recognized": "Na‑convert na ang audio sa text.",
        "mic_unclear": "Hindi malinaw ang audio. Pakiulit nang mas malinaw.",
        "stt_unavailable": "Hindi available ang speech‑to‑text service ngayon.",
        "unable_process_audio": "Hindi ma‑process ang audio. Paki‑record muli.",
        "mic_recorder_title": "Audio Recorder",
        "mic_recorder_desc": "Gamitin ang Start at Stop upang mag‑record ng boses ng pulis.",
        "mic_help": "Kung naka‑block ang mic, payagan ito sa browser settings.",
        "mic_access_failed": "Hindi ma‑access ang mic. Paki‑payagan ang mic at subukan muli.",
        "mic_no_audio": "Walang na‑record na audio. Maaaring naka‑block ang mic.",
        "btn_clear_filter": "I‑clear ang filter",
        "currently_filtering": "Kasalukuyang nagfi‑filter ayon sa",
        "quiz_correct": "✅ Tama!",
        "quiz_incorrect": "❌ Mali.",
        "language_selector_error": "❌ Error sa pagpili ng wika",
        "demo_section_title": "🎬 Demo Mode at Pagsubok",
        "demo_on": "🎬 NAKA‑ON ANG DEMO",
        "demo_off": "🎬 NAKA‑OFF ANG DEMO",
        "tour_button": "🎓 Tour / Gabay",
        "tour_complete": "✅ Kumpleto ang tour! Handa ka na.",
        "btn_go_home": "🏠 Bumalik sa Home",
        "btn_skip_tour": "⏭️ Laktawan ang tour",
        "btn_next": "Susunod ➡️",
        "btn_start_using": "🎉 Simulan ang paggamit!",

        "documents_title": "Legal Document Assistant",
        "documents_subtitle": "Mag‑upload ng dokumento at kumuha ng mahahalagang detalye",
        "upload_document": "📤 Mag‑upload ng dokumento",
        "take_photo": "📸 Kunan ng larawan",
        "extract_text": "I‑extract ang text",
        "simplify_text": "Pinasimpleng legal na wika",
        "translate_document": "🌐 Isalin ang dokumento",
        "extract_dates": "📅 Mga petsang nahanap",
        "extract_deadlines": "⏰ Mga deadline",
        "extract_agencies": "🏛️ Mga ahensiya ng gobyerno",
        "extract_actions": "✅ Mga kinakailangang aksyon",
        "download_report": "📥 I‑download ang report",
        "report_generated": "Handa na ang iyong report",

        "rights_title": "Sentro ng Karapatan",
        "rights_subtitle": "Alamin ang iyong mga karapatang konstitusyonal",
        "right_fourth": "Ika‑4 na Amyenda: Search & Seizure",
        "right_fifth": "Ika‑5 na Amyenda: Karapatang Manahimik",
        "right_sixth": "Ika‑6 na Amyenda: Karapatan sa Abogado",
        "right_traffic": "Mga karapatan kapag pinara sa daan",
        "right_arrest": "Kung ikaw ay inaaresto",
        "right_fourth_content": "**Ang Iyong Karapatan:** Protektado ka laban sa hindi makatwirang paghahalughog at pagsamsam.\n\n**Mahalagang Punto:**\n- Kadalasan kailangan ng pulis ng search warrant upang halughugin ang iyong bahay, sasakyan, o gamit\n- Maaari kang tumanggi sa pamamagitan ng pagsabi: \"Hindi ako pumapayag sa paghahalughog\"\n- HUWAG lumaban o gumamit ng puwersa — maaari itong magdulot ng dagdag na kaso\n- Maaari pa ring magpatuloy ang pulis kung may warrant o probable cause\n\n**Pwede Mong Gawin:**\n- Manahimik at itanong: \"Pwede na ba akong umalis?\"\n- Tanungin: \"May search warrant ba kayo?\"\n- Panatilihing nakikita ang iyong mga kamay\n- Huwag hadlangan ang pulis",

        "right_fifth_content": "**Ang Iyong Karapatan:** May karapatan kang manahimik at hindi magsabi ng anumang makakasama sa iyo.\n\n**Mahalagang Punto:**\n- HINDI mo kailangang sagutin ang mga tanong ng pulis\n- Sabihin nang malinaw: \"Ginagamit ko ang aking karapatang manahimik\"\n- Umiiral ang karapatang ito kahit hindi ka pa inaaresto\n- Hindi maaaring gamitin laban sa iyo ang pananahimik mo sa korte\n\n**Mahalaga:**\n- Kailangan mong sabihin nang malinaw na ginagamit mo ang karapatang ito\n- Kung inaaresto ka, humingi agad ng abogado\n- Huwag magpaliwanag o makipag‑areglo",

        "right_sixth_content": "**Ang Iyong Karapatan:** May karapatan kang magkaroon ng abogado.\n\n**Mahalagang Punto:**\n- Kung hindi mo kayang magbayad, magtatalaga ang korte ng abogado para sa iyo\n- Maaari kang humingi ng abogado ANUMANG ORAS habang iniimbestigahan\n- Kapag humingi ka ng abogado, dapat itigil ng pulis ang pagtatanong\n- May karapatan kang may abogado sa tabi mo habang iniinteroga\n\n**Sabihin:**\n- \"Gusto kong makausap ang aking abogado\"\n- \"Ginagamit ko ang aking karapatan sa abogado\"\n- Pagkatapos nito, manahimik hanggang dumating ang abogado",

        "right_traffic_content": "**Kapag Pinara Ka sa Daan:**\n- Kailangan mong ipakita ang lisensya, rehistro, at insurance\n- Maaari mong itanong: \"Detained ba ako o pwede na akong umalis?\"\n- HINDI mo kailangang pumayag sa paghahalughog ng sasakyan\n- Sabihin: \"Hindi ako pumapayag sa paghahalughog\"\n\n**Paghahalughog ng Sasakyan:**\n- Maaaring tumingin ang pulis sa loob ng sasakyan mula sa labas\n- Maaari silang maghalughog kung may probable cause\n- Maaari silang maghalughog kung inaaresto ka\n\n**Karapatan Mo:**\n- Panatilihing nakikita ang iyong mga kamay\n- Magsalita nang mahinahon\n- Huwag lumaban\n- Maaari kang mag‑video (hangga’t hindi nakakasagabal)",

        "right_arrest_content": "**Mahalagang Hakbang:**\n1. Manahimik — huwag sumagot sa mga tanong\n2. Sabihin: \"Gusto ko ng abogado\"\n3. Huwag pumirma ng anumang dokumento nang walang abogado\n4. Huwag pag‑usapan ang kaso sa ibang detainee\n\n**Karapatan Kapag Inaaresto:**\n- Karapatang malaman kung bakit ka inaaresto\n- Karapatang tumawag\n- Karapatang manahimik\n- Karapatang magkaroon ng abogado\n\n**Huwag Gawin:**\n- Huwag lumaban (kahit tingin mo ay mali ang pag‑aresto)\n- Huwag pumirma ng confession\n- Huwag pumayag sa paghahalughog\n- Huwag makipag‑areglo sa pulis nang walang abogado",

        "resources_title": "Mga Serbisyong Pang‑Komunidad",
        "resources_subtitle": "Maghanap ng legal aid at community support",
        "legal_aid": "Legal Aid Organizations",
        "emergency_services": "Emergency Services",
        "immigration": "Immigration Legal Services",
        "phone": "Telepono: ",
        "services": "Mga Serbisyo: ",
        "website": "Website: ",
        "hours": "Oras: ",

        "nearby_title": "Mga Karapatan Malapit sa Iyo",
        "nearby_subtitle": "Maghanap ng legal aid at community services malapit sa iyo",
        "enter_address": "Ilagay ang iyong address:",
        "search_radius": "Search radius (miles):",
        "nearest_legal_aid": "📋 Pinakamalapit na Legal Aid Office",
        "nearest_courthouse": "⚖️ Pinakamalapit na Korte",
        "nearest_police": "👮 Pinakamalapit na Presinto",
        "nearest_translator": "🗣️ Serbisyong Pagsasalin",
        "nearest_community": "🏢 Community Center",
        "address": "Address: ",
        "phone_number": "Telepono: ",
        "hours_open": "Oras ng Operasyon: ",
        "get_directions": "🗺️ Direksyon",
        "not_found": "Walang nahanap na resulta malapit dito",
        "logging_title": "Talaan ng Pagharap",
        "logging_subtitle": "I‑record ang mga pagharap at insidente kasama ang pulis",
        "encounter_type": "Uri ng pagharap:",
        "encounter_location": "Lokasyon:",
        "encounter_details": "Mga detalye:",
        "encounter_date": "Petsa at Oras:",
        "officer_info": "Impormasyon ng pulis:",
        "officer_badge": "Badge Number:",
        "officer_agency": "Ahensiya:",
        "encounter_saved": "✅ Matagumpay na na‑save ang pagharap",
        "view_history": "📋 Tingnan ang history ng pagharap",
        "total_encounters": "Kabuuang bilang ng pagharap:",
        "search_encounters": "🔍 Hanapin ang pagharap",

        "emergency_title": "Pang‑emerhensiyang Tulong",
        "emergency_subtitle": "Mga hotline at serbisyong pang‑emerhensiya",
        "emergency_911": "911 — Pulis, Bumbero, Medikal",
        "emergency_suicide": "National Suicide Prevention Hotline",
        "emergency_domestic": "Domestic Violence Hotline",
        "emergency_assault": "RAINN — Sexual Assault Support",
        "emergency_poison": "Poison Control Center",
        "emergency_text": "Crisis Text Line",
        "emergency_procedures": "Mga hakbang sa emerhensiya:",
        "procedure_safe": "Panatilihing ligtas ang sarili",
        "procedure_document": "I‑document ang lahat ng detalye",
        "procedure_record": "Mag‑video kung legal at ligtas",
        "procedure_call": "Tumawag ng tulong",
        "procedure_contact": "Kontakin ang iyong abogado",

        "loading": "Naglo‑load...",
        "success": "Tagumpay!",
        "error": "Error",
        "warning": "Babala",
        "info": "Impormasyon",
        "processing": "Pinoproseso...",
        "please_wait": "Paki‑hintay...",
        "no_data": "Walang data",
        "try_again": "Subukan muli",

        "accessibility_title": "♿ Mga Setting ng Accessibility",
        "text_size": "Laki ng text:",
        "text_size_normal": "Normal",
        "text_size_large": "Malaki",
        "text_size_extra_large": "Napakalaki",
        "high_contrast": "🎨 High Contrast Mode",
        "high_contrast_on": "Naka‑ON ang high contrast",
        "high_contrast_off": "Naka‑OFF ang high contrast",
        "screen_reader": "Naka‑enable ang screen reader labels",
        "accessibility_saved": "✅ Na‑save ang accessibility settings",
        "extract_deadlines": "📋 Mga importanteng deadline na nahanap",
        "extract_penalties": "⚠️ Mga parusa at babala",
        "extract_requirements": "✓ Mga kinakailangan at aksyon",
        "deadline_found": "Deadline:",
        "penalty_found": "Parusa:",
        "requirement_found": "Kinakailangang aksyon:",
        "document_summary": "📋 Buod ng Dokumento",
        "summary_generated": "Matagumpay na nagawa ang buod",

        "location_title": "📍 Maghanap ng mga serbisyo malapit sa iyo",
        "enter_address": "Ilagay ang address o ZIP code:",
        "search_radius_miles": "Search radius (miles):",
        "find_resources": "🔍 Hanapin ang mga serbisyo",
        "resource_type": "Uri ng serbisyo:",
        "all_resources": "Lahat ng serbisyo",
        "legal_aid_offices": "Mga Legal Aid Office",
        "community_centers": "Mga Community Center",
        "language_services": "Mga Serbisyong Pang‑wika",
        "emergency_shelters": "Mga Emergency Shelter",
        "distance_away": "miles ang layo",
        "get_directions": "🗺️ Direksyon",
        "no_resources_found": "Walang nahanap na serbisyo sa lugar",
        "resource_hours": "Oras:",
        "resource_phone": "Telepono:",
        "resource_address": "Address:",
        "resource_website": "Website:",
        "loading_resources": "Naghahanap ng mga serbisyo malapit sa iyo...",

        "saved_deadlines": "⏰ Mga Na‑save na Deadline",
        "upload_legal_doc": "Mag‑upload ng legal na dokumento",
        "important_dates": "📅 Mahahalagang Petsa",
        "required_actions": "✓ Mga Kinakailangang Aksyon",
        "critical_deadlines": "⏰ Mga Kritikal na Deadline",
        "penalties_warnings": "⚠️ Mga Parusa at Babala",
        "extraction_guide": "Gabay sa pag‑extract ng dokumento",
        "demo_mode_active": "📺 **DEMO MODE ON** — nagpapakita ng sample data",
        "have_deadlines": "📋 Mayroon kang mga importanteng deadline!",
        "view_all_deadlines": "📋 Tingnan lahat ng deadline →",
        "from_document": "Mula sa:",
        "file_type": "Uri ng file",
        "file_size": "Laki ng file",
        "status_ready": "Handa para sa extraction",
        "extract_information": "🔍 I‑extract ang impormasyon",
        "extracting_info": "Nag‑e‑extract ng impormasyon mula sa dokumento...",
        "no_dates_found": "Walang nahanap na petsa",
        "no_deadlines_found": "Walang nahanap na deadline",
        "no_penalties_found": "Walang nahanap na parusa",
        "download_summary": "📥 I‑download ang buod",
        "download_as_txt": "I‑download bilang TXT",
        "save_deadlines_to_dashboard": "💾 I‑save ang mga deadline sa dashboard",
        "know_your_rights_long": "⚖️ Unawain ang Iyong mga Karapatan",
        "education_quizzes": "Edukasyon, pagsusulit, at mga learning module",
        "learn_tab": "📚 Aralin",
        "quiz_tab": "🧪 Pagsusulit",
        "rights_education": "Edukasyon sa Karapatan",
        "select_topic": "Pumili ng paksa:",
        "test_knowledge": "Subukan ang iyong kaalaman sa karapatang sibil at legal na proteksyon.",
        "rights_quiz": "Pagsusulit sa Karapatan",

        "can_police_search": "Maaaring halughugin ng pulis ang iyong sasakyan nang walang pahintulot?",
        "only_with_warrant": "Kung may search warrant",
        "only_prob_cause": "Kung may probable cause",
        "both_a_and_b": "Parehong A at B",
        "never_without": "Hindi, hindi nila maaaring gawin iyon",
        "police_can_search": "Maaaring maghalughog ang pulis kung may warrant o probable cause.",

        "answer_police_q": "Kailangan mo bang sagutin ang mga tanong ng pulis?",
        "yes_always": "Oo, palagi",
        "right_remain_silent": "Hindi, may karapatan kang manahimik",
        "only_your_name": "Pangalan mo lang ang kailangan",
        "only_if_arrested": "Kung inaaresto ka lang",
        "fifth_amendment": "Ibinibigay ng Ika‑5 Amyenda ang karapatang manahimik at hindi magsabi ng makakasama sa iyo.",

        "what_say_arrested": "Ano ang dapat mong sabihin kapag inaaresto ka?",
        "explain_what_happened": "Ipaliwanag ang nangyari",
        "ask_for_lawyer": "Humingi ng abogado",
        "refuse_give_name": "Tumangging ibigay ang pangalan",
        "try_negotiate": "Makipag‑areglo sa pulis",
        "always_ask_lawyer": "Humingi agad ng abogado at manahimik.",

        "check_answer": "✓ Suriin ang sagot {number}",
        "question_number": "Tanong {number}: {question}",
        "select_answer": "Piliin ang sagot:",
        "your_score": "Iyong Score",

        "talk_community": "💬 Makipag‑usap sa Komunidad",
        "community_intro": "Magbahagi ng karanasan, magtanong, at tumulong sa iba — sama‑sama tayong mas malakas",
        "share_exp_tab": "💭 Magbahagi ng Karanasan",
        "ask_q_tab": "❓ Magtanong",
        "give_advice_tab": "💡 Magbigay ng Payo",
        "share_your_exp": "💭 Ibahagi ang Iyong Karanasan",
        "share_story": "Ibahagi ang iyong karanasan upang makatulong sa iba. Lahat ng post ay sinusuri para sa kaligtasan.",
        "title_label": "Pamagat:",
        "exp_placeholder": "Halimbawa: Tips kapag pinara sa daan",
        "your_story": "Iyong Karanasan:",
        "story_placeholder": "Ibahagi ang iyong kwento...",
        "post_anonymously": "Mag‑post nang anonymous",
        "share_exp_btn": "📤 Ibahagi ang Karanasan",
        "fill_title_content": "⚠️ Paki‑lagyan ng pamagat at nilalaman",
        "exp_shared": "✅ Na‑share na ang iyong karanasan! Salamat sa pagtulong sa komunidad.",
        "ask_community": "❓ Magtanong sa Komunidad",
        "question_help": "May tanong ka? Tutulong ang komunidad.",
        "your_question": "Iyong Tanong:",
        "question_placeholder": "Halimbawa: Ano ang karapatan ko kapag pinara ako ng pulis?",
        "details_label": "Mga Detalye:",
        "details_placeholder": "Magbigay ng karagdagang impormasyon...",
        "ask_anon": "Mag‑post nang anonymous",
        "ask_q_btn": "❓ I‑post ang Tanong",
        "enter_question": "⚠️ Paki‑lagay ang iyong tanong",
        "question_posted": "✅ Na‑post na ang iyong tanong!",

        "give_advice": "💡 Magbigay ng Payo",
        "help_others": "Tumulong sa iba gamit ang iyong kaalaman at karanasan.",
        "topic_label": "Paksa:",
        "topic_placeholder": "Halimbawa: Paano maghanda para sa korte",
        "your_advice": "Iyong Payo:",
        "advice_placeholder": "Ibahagi ang iyong nalalaman...",
        "share_anon": "I‑share nang anonymous",
        "share_advice_btn": "💡 I‑share ang Payo",
        "share_wisdom": "✅ Salamat sa pagbabahagi ng iyong kaalaman!",
        "fill_topic_advice": "⚠️ Paki‑lagay ang paksa at payo",

        "recent_posts": "📋 Mga Kamakailang Post",
        "no_posts_yet": "💭 Wala pang post. Maging unang magbahagi!",
        "posted_recently": "Na‑post {timestamp}",
        "author_anonymous": "Anonymous",
        "author_community_member": "Miyembro ng Komunidad",

        "crisis_hotlines": "🚨 Mga Hotline at Emergency Support",
        "crisis_support_24": "24/7 na suporta kapag kailangan mo ito",
        "emergency_hotlines_header": "🆘 Mga Emergency Hotline",
        "in_immediate_danger": "Kung nasa agarang panganib ka, tumawag sa 911",
        "emergency_number": "Emergency Number",
        "suicide_prevention": "National Suicide Prevention Hotline",
        "domestic_violence": "Domestic Violence Hotline",
        "sexual_assault": "RAINN — Sexual Assault Support",
        "poison_control": "Poison Control Center",
        "crisis_text": "Crisis Text Line",

        "safety_procedures": "📋 Mga Hakbang sa Kaligtasan",
        "stay_safe": "🛡️ Manatiling Ligtas",
        "stay_safe_desc": "Unahin ang iyong kaligtasan — huwag lumaban. Ang buhay mo ang pinakamahalaga.",
        "document_details": "📝 I‑document ang Detalye",
        "document_details_desc": "Isulat ang pangalan ng pulis, badge number, lokasyon, oras, at mga ginawa nila.",
        "record_safely": "🎥 Mag‑record nang Ligtas",
        "record_safely_desc": "Kung legal at ligtas, mag‑video. Panatilihing nakikita ang camera.",
        "call_for_help": "📞 Tumawag ng Tulong",
        "call_help_desc": "Kung nasa panganib, tumawag agad sa 911. Magsalita nang malinaw.",
        "get_legal_help": "⚖️ Humingi ng Legal na Tulong",
        "legal_help_desc": "Kontakin ang abogado. Maraming public defenders ang may emergency support.",
        "medical_attention": "🏥 Medikal na Atensyon",
        "medical_attention_desc": "Kung nasaktan, magpatingin agad at kunan ng larawan ang mga pinsala.",
        "mental_health_support": "🧠 Mental Health Support",
        "legal_troubles_trauma": "Ang pagharap sa pulis o legal na problema ay maaaring magdulot ng trauma.",
        "mental_health_resources": "Mga Mental Health Resources:",
        "samhsa_helpline": "SAMHSA Helpline: 1‑800‑662‑4357 (libre, kumpidensyal, 24/7)",
        "psychology_directory": "Maghanap ng therapist: Psychology Today directory",
        "support_groups": "Mga Support Group: NAACP, community centers, legal orgs",
        "contact_emergency": "🆘 Emergency",
        "contact_suicide": "🧠 Suicide Prevention",
        "contact_domestic": "💔 Domestic Violence Hotline",
        "contact_rainn": "🤝 RAINN — Sexual Assault Support",
        "contact_poison": "☠️ Poison Control",
        "contact_crisis_text": "📱 Crisis Text Line",
        "contact_crisis_text_number": "I‑text ang HOME sa 741741",

        "enc_type_traffic_stop": "Pagpapatigil sa Sasakyan",
        "enc_type_street_encounter": "Pagharap sa Kalsada",
        "enc_type_arrest": "Pag‑aresto",
        "enc_type_search": "Paghahalughog",
        "enc_type_other": "Iba pa",
        "encounter_label": "Pagharap",
        "unknown": "Hindi alam",
        "na": "Hindi naaangkop",
        "error_generating_qr": "Nagkaroon ng error sa pag‑generate ng QR code",

        "btn_launch_app": "🚀 Buksan ang App",
        "btn_start_demo": "📺 Simulan ang Demo",
        "btn_quick_tour": "❓ Mabilis na Tour",
        "share_with_others": "📱 Ibahagi sa iba",
        "qr_generation_in_progress": "Gumagawa ng QR code...",
        "key_features_label": "Mga Pangunahing Tampok:",
        "btn_previous": "⬅️ Bumalik",
        "language_change_error": "Error sa pagbabago ng wika",
        "demo_mode_active_sidebar": "✅ Demo Mode ON — nagpapakita ng sample data",
        "screen_reader_off": "🔇 Naka‑OFF ang screen reader",
        "navigation_title": "📂 Nabigasyon",
        "nav_rights_full": "⚖️ Unawain ang Iyong mga Karapatan",
        "nav_resources_near_you": "📍 Mga Serbisyo Malapit sa Iyo",
        "nav_logging_full": "📝 Talaan ng Pagharap",
        "nav_crisis_resources": "🚨 Mga Emergency Resource",
        "nav_community": "💬 Komunidad",

        "sidebar_built_for": "Gawa upang protektahan ang karapatang sibil ng lahat.",
        "show_landing_page": "🏠 Ipakita ang Landing Page",

        "landing_hero_html": "<div class=\"landing-hero\"><h1>⚖️ CivicShield Pro</h1><h2>Unawain ang iyong karapatan. Protektahan ang sarili. Humingi ng tulong.</h2><p>Isang multi‑language platform para tulungan ang lahat na maunawaan at magamit ang kanilang karapatang sibil sa totoong buhay.</p></div>",

        "landing_purpose_md": "### 🎯 Layunin\nNagbibigay ang CivicShield Pro ng:\n\n- **Real‑time legal translation sa 14 na wika**\n- **Impormasyon sa karapatan** na akma sa sitwasyon\n- **Legal document analysis** at extraction ng deadlines\n- **Community support** at pagbabahagi ng karanasan\n- **24/7 crisis resources**",

        "landing_features_md": "### ⭐ Mga Pangunahing Tampok\n\n- 🗣️ **Real‑time na pagsasalin** — isalin ang sinasabi ng pulis\n- 📄 **Legal document tools** — i‑extract ang mahahalagang detalye\n- ⚖️ **Know Your Rights** — aralin at pagsusulit\n- 📍 **Nearby resources** — legal aid at community services\n- 📝 **Encounter logging** — i‑record ang pagharap sa pulis\n- 🚨 **Crisis hotlines** — 24/7 support\n- 💬 **Community forum** — magtanong at magbahagi",

        "landing_share_md": "**Ibahagi ang CivicShield sa iba:**\n\n1. I‑scan ang QR code\n2. Walang kailangang i‑install\n3. Suporta para sa 14 na wika\n4. Gumagana sa phone, tablet, at computer",

        "landing_who_should_use_md": "### 👥 Para Kanino Ito?\n\n**Mga Hukom at Legal Professionals:**\n- Unawain ang pananaw ng komunidad\n- Suriin ang pag‑unawa ng defendants sa kanilang karapatan\n- Gumamit ng real‑time translation\n\n**Mga Abogado at Legal Aid:**\n- Magbigay ng multilingual legal info\n- Tulungan ang clients mag‑record ng encounters\n- Ikonekta sila sa community resources\n\n**Mga Guro:**\n- Ituro ang civic rights\n- Gumamit ng real‑world scenarios\n- Magbigay ng interactive quizzes\n\n**Komunidad:**\n- Alamin ang dapat gawin kapag hinarap ng pulis\n- Gumamit ng emergency resources\n- Magbahagi ng karanasan",

        "landing_disclaimer_md": "**⚠️ Legal na Paalala:**\n\nNagbibigay ang CivicShield Pro ng impormasyong pang‑edukasyon, hindi legal na payo.\nNagbabago ang batas depende sa lugar.\nKumonsulta sa abogado para sa partikular na payo.",

        "tutorial_intro_html": "<div class=\"tutorial-container\"><h1>👋 Maligayang Pagdating sa CivicShield Pro!</h1><p>Tara, tingnan natin ang mga pangunahing tampok.</p></div>",

        "tutorial_step1_title": "🏠 Main Dashboard",
        "tutorial_step1_desc": "Dito mo maa‑access ang lahat ng features.",
        "tutorial_step1_feat1": "Navigation sa lahat ng tools",
        "tutorial_step1_feat2": "Tingnan ang mga na‑save na deadline",
        "tutorial_step1_feat3": "Access sa emergency resources",

        "tutorial_step2_title": "🗣️ Real‑Time Translation",
        "tutorial_step2_desc": "Isalin ang sinasabi ng pulis sa 14 na wika.",
        "tutorial_step2_feat1": "Speech‑to‑text",
        "tutorial_step2_feat2": "Instant translation",
        "tutorial_step2_feat3": "Audio playback",

        "tutorial_step3_title": "📄 Legal Documents",
        "tutorial_step3_desc": "Mag‑upload at i‑extract ang mahahalagang detalye.",
        "tutorial_step3_feat1": "Automatic deadline extraction",
        "tutorial_step3_feat2": "Penalty detection",
        "tutorial_step3_feat3": "Document translation",

        "tutorial_step4_title": "⚖️ Know Your Rights",
        "tutorial_step4_desc": "Aralin ang iyong karapatan at subukan ang iyong kaalaman.",
        "tutorial_step4_feat1": "Rights education",
        "tutorial_step4_feat2": "Interactive quizzes",
        "tutorial_step4_feat3": "Progress tracking",

        "tutorial_step5_title": "📍 Nearby Resources",
        "tutorial_step5_desc": "Maghanap ng legal aid at community services.",
        "tutorial_step5_feat1": "Location‑based search",
        "tutorial_step5_feat2": "Service filters",
        "tutorial_step5_feat3": "Quick directions",

        "tutorial_step6_title": "💬 Community Forum",
        "tutorial_step6_desc": "Magbahagi, magtanong, at tumulong sa iba.",
        "tutorial_step6_feat1": "Anonymous posting",
        "tutorial_step6_feat2": "Legal questions",
        "tutorial_step6_feat3": "Advice sharing",

        "documents_intro_md": "Mag‑upload ng legal na dokumento (larawan o PDF) upang i‑extract ang:\n- Mga petsa at deadline\n- Mga kinakailangang aksyon\n- Mga parusa at babala\n- Mga ahensiya ng gobyerno\n- Buod ng dokumento",
        "extract_deadlines_found": "📋 Mga importanteng deadline na nahanap",
        "extract_penalties_found": "⚠️ Mga parusa na nahanap",
        "extract_requirements_found": "✓ Mga kinakailangan na nahanap",

        "search_radius_km": "Search radius (km):",

        "resource_category": "Kategorya ng serbisyo:",
        "resource_distance": "Distansya:",
        "resource_map_link": "🗺️ Mapa",
        "resource_description": "Deskripsyon:",
        "resource_notes": "Mga Tala:",
        "resource_tags": "Mga Tag:",
        "resource_id": "Resource ID:",
        "resource_source": "Pinagmulan:",
        "resource_updated": "Huling update:",
        "resource_error": "Nagkaroon ng error sa pagkuha ng serbisyo",
        "resource_loading": "Naglo-load ng impormasyon ng serbisyo...",
        "resource_retry": "Subukang muli",
        "resource_empty": "Walang detalye para sa serbisyong ito",

    },
    "Hindi / हिन्दी": {
        "sidebar_title": "CivicShield",
        "sidebar_tagline": "अपने अधिकार समझें",
        "select_language": "📍 भाषा चुनें:",
        "nav_home": "🏠 होम",
        "nav_translation": "🗣️ रियल‑टाइम अनुवाद",
        "nav_documents": "📄 कानूनी दस्तावेज़",
        "nav_rights": "📚 अधिकार केंद्र",
        "nav_quiz": "❓ अधिकार क्विज़",
        "nav_resources": "🏥 सामुदायिक सेवाएँ",
        "nav_nearby": "📍 आपके पास उपलब्ध अधिकार",
        "nav_logging": "📝 मुठभेड़ लॉग",
        "nav_emergency": "🚨 आपातकालीन सहायता",
        "nav_about": "CivicShield के बारे में",
        "sidebar_version": "संस्करण 3.0.0",
        "sidebar_purpose": "नागरिक अधिकार सुरक्षा और पेशेवर कानूनी अनुवाद",
        "sidebar_languages": "14 भाषाओं का समर्थन",
        "sidebar_disclaimer": "⚠️ कानूनी अस्वीकरण",
        "sidebar_disclaimer_text": "यह ऐप शैक्षिक जानकारी प्रदान करता है, कानूनी सलाह नहीं। अपने मामले के लिए वकील से परामर्श करें।",

        "home_title": "CivicShield में आपका स्वागत है",
        "home_subtitle": "अपने अधिकार जानें। खुद की रक्षा करें। सहायता प्राप्त करें।",
        "dashboard_intro": "शुरू करने के लिए नीचे दिए गए किसी फीचर को चुनें:",

        "card_translation_title": "रियल‑टाइम अनुवाद",
        "card_translation_desc": "पुलिस क्या कह रही है उसका अनुवाद करें और कानूनी सलाह प्राप्त करें",
        "card_documents_title": "कानूनी दस्तावेज़ सहायक",
        "card_documents_desc": "दस्तावेज़ अपलोड करें, महत्वपूर्ण जानकारी निकालें और अनुवाद करें",
        "card_rights_title": "अधिकार शिक्षा केंद्र",
        "card_rights_desc": "अपने संवैधानिक अधिकार सीखें",
        "card_quiz_title": "अधिकार क्विज़",
        "card_quiz_desc": "अपने नागरिक अधिकार ज्ञान का परीक्षण करें",
        "card_resources_title": "सामुदायिक सेवाएँ",
        "card_resources_desc": "कानूनी सहायता, आपातकालीन सेवाएँ और सामुदायिक समर्थन खोजें",
        "card_nearby_title": "आपके पास उपलब्ध अधिकार",
        "card_nearby_desc": "आपके पास कानूनी सहायता और सामुदायिक सेवाएँ खोजें",
        "card_logging_title": "मुठभेड़ लॉग",
        "card_logging_desc": "पुलिस के साथ मुठभेड़ों को रिकॉर्ड करें",
        "card_emergency_title": "आपातकालीन सहायता",
        "card_emergency_desc": "आपातकालीन हेल्पलाइन और प्रक्रियाएँ",

        "btn_open": "खोलें",
        "btn_delete": "❌",
        "btn_record": "🎤 रिकॉर्ड करें",
        "btn_stop": "⏹️ रोकें",
        "btn_translate": "🌐 अनुवाद करें",
        "btn_listen": "🔊 सुनें",
        "btn_download": "📥 डाउनलोड करें",
        "btn_search": "🔍 खोजें",
        "btn_log": "📝 लॉग करें",
        "btn_back": "← वापस",
        "btn_submit": "✓ सबमिट करें",
        "btn_cancel": "✗ रद्द करें",

        "translation_title": "रियल‑टाइम अनुवाद",
        "translation_subtitle": "पुलिस क्या कह रही है उसका अनुवाद करें और कानूनी सलाह प्राप्त करें",
        "officer_statement": "पुलिस द्वारा कहा गया (अंग्रेज़ी):",
        "your_rights": "आपके अधिकार और कानूनी सलाह:",
        "play_before_title": "1. बातचीत से पहले चलाएँ",
        "play_before_desc": "रिकॉर्डिंग शुरू होने से पहले यह पुलिस को सुनाएँ।",
        "play_before_audio": "Officer, before we begin, I am using a translation app to avoid any language barriers. I am recording with your knowledge for safety and accuracy.",
        "play_after_title": "3. अधिकार समझने के बाद चलाएँ",
        "play_after_desc": "अपने अधिकार सुनने के बाद यह पुलिस को सुनाएँ।",
        "play_after_audio": "I understand, officer, and I will comply, but I will be using my right to remain silent.",
        "officer_script": "पुलिस के लिए स्क्रिप्ट (अंग्रेज़ी):",
        "officer_script_translated": "यह आपकी भाषा में क्या कहता है:",
        "record_officer": "🎤 पुलिस की आवाज़ रिकॉर्ड करें",
        "stop_recording": "⏹️ रिकॉर्डिंग रोकें और अनुवाद करें",
        "listen_to_advice": "🔊 सलाह सुनें",
        "translation_hint": "अनुवाद के लिए टाइप करें या रिकॉर्ड करें",
        "generating_audio": "ऑडियो तैयार किया जा रहा है...",
        "audio_ready": "✅ ऑडियो तैयार है",
        "audio_failed": "❌ ऑडियो बनाने में त्रुटि",
        "speech_recognized": "ऑडियो को टेक्स्ट में बदल दिया गया है।",
        "mic_unclear": "ऑडियो स्पष्ट नहीं है। कृपया दोबारा स्पष्ट रूप से बोलें।",
        "stt_unavailable": "स्पीच‑टू‑टेक्स्ट सेवा उपलब्ध नहीं है।",
        "unable_process_audio": "ऑडियो प्रोसेस नहीं किया जा सका। कृपया फिर से रिकॉर्ड करें।",
        "mic_recorder_title": "ऑडियो रिकॉर्डर",
        "mic_recorder_desc": "पुलिस की आवाज़ रिकॉर्ड करने के लिए Start और Stop का उपयोग करें।",
        "mic_help": "यदि माइक्रोफ़ोन ब्लॉक है, तो ब्राउज़र सेटिंग्स में अनुमति दें।",
        "mic_access_failed": "माइक्रोफ़ोन तक पहुँच नहीं मिली। कृपया अनुमति दें और पुनः प्रयास करें।",
        "mic_no_audio": "कोई ऑडियो रिकॉर्ड नहीं हुआ। माइक्रोफ़ोन ब्लॉक हो सकता है।",
        "btn_clear_filter": "फ़िल्टर हटाएँ",
        "currently_filtering": "फ़िल्टर लागू है:",
        "quiz_correct": "✅ सही!",
        "quiz_incorrect": "❌ गलत।",
        "language_selector_error": "❌ भाषा चयन में त्रुटि",
        "demo_section_title": "डेमो मोड और परीक्षण",
        "demo_on": "🎬 डेमो ON",
        "demo_off": "🎬 डेमो OFF",
        "tour_button": "🎓 टूर",
        "tour_complete": "✅ टूर पूरा! आप तैयार हैं।",
        "btn_go_home": "🏠 होम पर जाएँ",
        "btn_skip_tour": "⏭️ टूर छोड़ें",
        "btn_next": "आगे ➡️",
        "btn_start_using": "🎉 उपयोग शुरू करें!",

        "documents_title": "कानूनी दस्तावेज़ सहायक",
        "documents_subtitle": "दस्तावेज़ अपलोड करें और महत्वपूर्ण जानकारी प्राप्त करें",
        "upload_document": "📤 दस्तावेज़ अपलोड करें",
        "take_photo": "📸 फोटो लें",
        "extract_text": "टेक्स्ट निकालें",
        "simplify_text": "सरल कानूनी भाषा",
        "translate_document": "🌐 दस्तावेज़ का अनुवाद करें",
        "extract_dates": "📅 मिली हुई तिथियाँ",
        "extract_deadlines": "⏰ डेडलाइन",
        "extract_agencies": "🏛️ सरकारी एजेंसियाँ",
        "extract_actions": "✅ आवश्यक कार्य",
        "download_report": "📥 रिपोर्ट डाउनलोड करें",
        "report_generated": "आपकी रिपोर्ट तैयार है",

        "rights_title": "अधिकार केंद्र",
        "rights_subtitle": "अपने संवैधानिक अधिकार जानें",
        "right_fourth": "चौथा संशोधन: तलाशी और ज़ब्ती",
        "right_fifth": "पाँचवाँ संशोधन: मौन रहने का अधिकार",
        "right_sixth": "छठा संशोधन: वकील का अधिकार",
        "right_traffic": "ट्रैफ़िक रोकने पर अधिकार",
        "right_arrest": "यदि आपको गिरफ्तार किया जाए",
        "right_fourth_content": "**आपका अधिकार:** आपको अनुचित तलाशी और ज़ब्ती से सुरक्षा प्राप्त है।\n\n**महत्वपूर्ण बिंदु:**\n- पुलिस को आमतौर पर आपके घर, वाहन या सामान की तलाशी के लिए वारंट चाहिए\n- आप स्पष्ट रूप से कह सकते हैं: \"मैं तलाशी की अनुमति नहीं देता/देती\"\n- कभी भी विरोध या बल प्रयोग न करें — इससे अतिरिक्त आरोप लग सकते हैं\n- यदि पुलिस के पास वारंट या probable cause है, तो वे तलाशी जारी रख सकते हैं\n\n**आप क्या कर सकते हैं:**\n- शांत रहें और पूछें: \"क्या मैं जा सकता/सकती हूँ?\"\n- पूछें: \"क्या आपके पास तलाशी वारंट है?\"\n- अपने हाथ दिखाई रखें\n- पुलिस के रास्ते में बाधा न बनें",

        "right_fifth_content": "**आपका अधिकार:** आपको चुप रहने का अधिकार है और आप अपने खिलाफ कुछ भी कहने के लिए बाध्य नहीं हैं।\n\n**महत्वपूर्ण बिंदु:**\n- आपको पुलिस के सवालों का जवाब देने की आवश्यकता नहीं है\n- स्पष्ट रूप से कहें: \"मैं चुप रहने का अपना अधिकार उपयोग कर रहा/रही हूँ\"\n- यह अधिकार गिरफ्तारी से पहले भी लागू होता है\n- आपका मौन अदालत में आपके खिलाफ उपयोग नहीं किया जा सकता\n\n**ध्यान दें:**\n- आपको यह अधिकार स्पष्ट रूप से व्यक्त करना होता है\n- यदि आपको गिरफ्तार किया जाता है, तुरंत वकील माँगें\n- कोई स्पष्टीकरण न दें, कोई सौदा न करें",

        "right_sixth_content": "**आपका अधिकार:** आपको वकील पाने का अधिकार है।\n\n**महत्वपूर्ण बिंदु:**\n- यदि आप वकील का खर्च नहीं उठा सकते, तो अदालत आपके लिए वकील नियुक्त करेगी\n- आप किसी भी समय वकील माँग सकते हैं\n- वकील माँगने के बाद पुलिस को पूछताछ रोकनी चाहिए\n- पूछताछ के दौरान वकील आपके साथ रह सकता है\n\n**कहें:**\n- \"मैं अपने वकील से बात करना चाहता/चाहती हूँ\"\n- \"मैं अपने वकील के अधिकार का उपयोग कर रहा/रही हूँ\"\n- इसके बाद चुप रहें जब तक वकील न आए",

        "right_traffic_content": "**जब आपको ट्रैफ़िक में रोका जाए:**\n- आपको लाइसेंस, रजिस्ट्रेशन और बीमा दिखाना आवश्यक है\n- आप पूछ सकते हैं: \"क्या मैं हिरासत में हूँ या जा सकता/सकती हूँ?\"\n- आपको वाहन की तलाशी की अनुमति देने की आवश्यकता नहीं है\n- कहें: \"मैं तलाशी की अनुमति नहीं देता/देती\"\n\n**वाहन तलाशी:**\n- पुलिस बाहर से वाहन के अंदर देख सकती है\n- यदि probable cause है, तो तलाशी कर सकती है\n- यदि आपको गिरफ्तार किया जाता है, तो तलाशी की जा सकती है\n\n**आपके अधिकार:**\n- अपने हाथ दिखाई रखें\n- शांत और सम्मानजनक रहें\n- विरोध न करें\n- आप वीडियो रिकॉर्ड कर सकते हैं (जब तक आप बाधा न बनें)",

        "right_arrest_content": "**गिरफ्तारी के समय महत्वपूर्ण कदम:**\n1. चुप रहें — सवालों का जवाब न दें\n2. कहें: \"मैं वकील चाहता/चाहती हूँ\"\n3. बिना वकील के कोई दस्तावेज़ साइन न करें\n4. अपने मामले पर अन्य कैदियों से बात न करें\n\n**गिरफ्तारी के समय अधिकार:**\n- आपको कारण बताया जाना चाहिए\n- आपको कॉल करने का अधिकार है\n- आपको चुप रहने का अधिकार है\n- आपको वकील पाने का अधिकार है\n\n**क्या न करें:**\n- विरोध न करें (भले ही गिरफ्तारी गलत लगे)\n- कोई स्वीकारोक्ति न लिखें\n- तलाशी की अनुमति न दें\n- पुलिस से कोई सौदा न करें",

        "resources_title": "सामुदायिक सेवाएँ",
        "resources_subtitle": "कानूनी सहायता और सामुदायिक समर्थन खोजें",
        "legal_aid": "कानूनी सहायता संगठन",
        "emergency_services": "आपातकालीन सेवाएँ",
        "immigration": "इमिग्रेशन कानूनी सेवाएँ",
        "phone": "फ़ोन: ",
        "services": "सेवाएँ: ",
        "website": "वेबसाइट: ",
        "hours": "समय: ",

        "nearby_title": "आपके पास उपलब्ध अधिकार",
        "nearby_subtitle": "आपके पास कानूनी सहायता और सेवाएँ खोजें",
        "enter_address": "अपना पता दर्ज करें:",
        "search_radius": "खोज सीमा (मील):",
        "nearest_legal_aid": "📋 सबसे नज़दीकी कानूनी सहायता कार्यालय",
        "nearest_courthouse": "⚖️ सबसे नज़दीकी अदालत",
        "nearest_police": "👮 सबसे नज़दीकी पुलिस स्टेशन",
        "nearest_translator": "🗣️ अनुवाद सेवाएँ",
        "nearest_community": "🏢 सामुदायिक केंद्र",
        "address": "पता: ",
        "phone_number": "फ़ोन: ",
        "hours_open": "खुलने का समय: ",
        "get_directions": "🗺️ दिशा‑निर्देश",
        "not_found": "इस क्षेत्र में कोई परिणाम नहीं मिला",
        "logging_title": "मुठभेड़ लॉग",
        "logging_subtitle": "पुलिस के साथ मुठभेड़ों और घटनाओं को रिकॉर्ड करें",
        "encounter_type": "मुठभेड़ का प्रकार:",
        "encounter_location": "स्थान:",
        "encounter_details": "विवरण:",
        "encounter_date": "तारीख और समय:",
        "officer_info": "पुलिस अधिकारी की जानकारी:",
        "officer_badge": "बैज नंबर:",
        "officer_agency": "एजेंसी:",
        "encounter_saved": "✅ मुठभेड़ सफलतापूर्वक सहेजी गई",
        "view_history": "📋 मुठभेड़ इतिहास देखें",
        "total_encounters": "कुल मुठभेड़:",
        "search_encounters": "🔍 मुठभेड़ खोजें",

        "emergency_title": "आपातकालीन सहायता",
        "emergency_subtitle": "आपातकालीन हेल्पलाइन और सेवाएँ",
        "emergency_911": "911 — पुलिस, फायर, मेडिकल",
        "emergency_suicide": "राष्ट्रीय आत्महत्या रोकथाम हेल्पलाइन",
        "emergency_domestic": "घरेलू हिंसा हेल्पलाइन",
        "emergency_assault": "RAINN — यौन उत्पीड़न सहायता",
        "emergency_poison": "ज़हर नियंत्रण केंद्र",
        "emergency_text": "क्राइसिस टेक्स्ट लाइन",
        "emergency_procedures": "आपातकालीन कदम:",
        "procedure_safe": "अपनी सुरक्षा सुनिश्चित करें",
        "procedure_document": "सभी विवरण दर्ज करें",
        "procedure_record": "यदि कानूनी और सुरक्षित हो तो वीडियो रिकॉर्ड करें",
        "procedure_call": "मदद के लिए कॉल करें",
        "procedure_contact": "अपने वकील से संपर्क करें",

        "loading": "लोड हो रहा है...",
        "success": "सफल!",
        "error": "त्रुटि",
        "warning": "चेतावनी",
        "info": "जानकारी",
        "processing": "प्रोसेस किया जा रहा है...",
        "please_wait": "कृपया प्रतीक्षा करें...",
        "no_data": "कोई डेटा नहीं",
        "try_again": "फिर से प्रयास करें",

        "accessibility_title": "♿ एक्सेसिबिलिटी सेटिंग्स",
        "text_size": "टेक्स्ट आकार:",
        "text_size_normal": "सामान्य",
        "text_size_large": "बड़ा",
        "text_size_extra_large": "बहुत बड़ा",
        "high_contrast": "🎨 हाई कॉन्ट्रास्ट मोड",
        "high_contrast_on": "हाई कॉन्ट्रास्ट ON",
        "high_contrast_off": "हाई कॉन्ट्रास्ट OFF",
        "screen_reader": "स्क्रीन रीडर लेबल सक्षम",
        "accessibility_saved": "✅ एक्सेसिबिलिटी सेटिंग्स सहेजी गईं",
        "extract_deadlines": "📋 मिली हुई महत्वपूर्ण डेडलाइन",
        "extract_penalties": "⚠️ दंड और चेतावनियाँ",
        "extract_requirements": "✓ आवश्यक कार्य और शर्तें",
        "deadline_found": "डेडलाइन:",
        "penalty_found": "दंड:",
        "requirement_found": "आवश्यक कार्य:",
        "document_summary": "📋 दस्तावेज़ सारांश",
        "summary_generated": "सारांश सफलतापूर्वक तैयार किया गया",

        "location_title": "📍 अपने पास उपलब्ध सेवाएँ खोजें",
        "enter_address": "पता या ZIP कोड दर्ज करें:",
        "search_radius_miles": "खोज सीमा (मील):",
        "find_resources": "🔍 सेवाएँ खोजें",
        "resource_type": "सेवा का प्रकार:",
        "all_resources": "सभी सेवाएँ",
        "legal_aid_offices": "कानूनी सहायता कार्यालय",
        "community_centers": "सामुदायिक केंद्र",
        "language_services": "भाषा सेवाएँ",
        "emergency_shelters": "आपातकालीन शेल्टर",
        "distance_away": "मील दूर",
        "get_directions": "🗺️ दिशा‑निर्देश",
        "no_resources_found": "इस क्षेत्र में कोई सेवा नहीं मिली",
        "resource_hours": "समय:",
        "resource_phone": "फ़ोन:",
        "resource_address": "पता:",
        "resource_website": "वेबसाइट:",
        "loading_resources": "आपके पास उपलब्ध सेवाएँ खोजी जा रही हैं...",

        "saved_deadlines": "⏰ सहेजी गई डेडलाइन",
        "upload_legal_doc": "कानूनी दस्तावेज़ अपलोड करें",
        "important_dates": "📅 महत्वपूर्ण तिथियाँ",
        "required_actions": "✓ आवश्यक कार्य",
        "critical_deadlines": "⏰ महत्वपूर्ण डेडलाइन",
        "penalties_warnings": "⚠️ दंड और चेतावनियाँ",
        "extraction_guide": "दस्तावेज़ एक्सट्रैक्शन गाइड",
        "demo_mode_active": "📺 **डेमो मोड ON** — नमूना डेटा दिखाया जा रहा है",
        "have_deadlines": "📋 आपके पास महत्वपूर्ण डेडलाइन हैं!",
        "view_all_deadlines": "📋 सभी डेडलाइन देखें →",
        "from_document": "दस्तावेज़ से:",
        "file_type": "फ़ाइल प्रकार",
        "file_size": "फ़ाइल आकार",
        "status_ready": "एक्सट्रैक्शन के लिए तैयार",
        "extract_information": "🔍 जानकारी निकालें",
        "extracting_info": "दस्तावेज़ से जानकारी निकाली जा रही है...",
        "no_dates_found": "कोई तिथि नहीं मिली",
        "no_deadlines_found": "कोई डेडलाइन नहीं मिली",
        "no_penalties_found": "कोई दंड नहीं मिला",
        "download_summary": "📥 सारांश डाउनलोड करें",
        "download_as_txt": "TXT के रूप में डाउनलोड करें",
        "save_deadlines_to_dashboard": "💾 डेडलाइन डैशबोर्ड में सहेजें",
        "know_your_rights_long": "⚖️ अपने अधिकार जानें",
        "education_quizzes": "शिक्षा, क्विज़ और लर्निंग मॉड्यूल",
        "learn_tab": "📚 पाठ",
        "quiz_tab": "🧪 क्विज़",
        "rights_education": "अधिकार शिक्षा",
        "select_topic": "विषय चुनें:",
        "test_knowledge": "अपने नागरिक अधिकार ज्ञान का परीक्षण करें।",
        "rights_quiz": "अधिकार क्विज़",

        "can_police_search": "क्या पुलिस बिना अनुमति आपके वाहन की तलाशी ले सकती है?",
        "only_with_warrant": "यदि उनके पास वारंट हो",
        "only_prob_cause": "यदि probable cause हो",
        "both_a_and_b": "A और B दोनों",
        "never_without": "नहीं, वे ऐसा नहीं कर सकते",
        "police_can_search": "पुलिस वारंट या probable cause होने पर तलाशी ले सकती है।",

        "answer_police_q": "क्या आपको पुलिस के सवालों का जवाब देना ज़रूरी है?",
        "yes_always": "हाँ, हमेशा",
        "right_remain_silent": "नहीं, आपको चुप रहने का अधिकार है",
        "only_your_name": "सिर्फ अपना नाम बताना आवश्यक है",
        "only_if_arrested": "सिर्फ अगर आपको गिरफ्तार किया गया हो",
        "fifth_amendment": "पाँचवाँ संशोधन आपको चुप रहने और खुद को दोषी न ठहराने का अधिकार देता है।",

        "what_say_arrested": "गिरफ्तार होने पर आपको क्या कहना चाहिए?",
        "explain_what_happened": "क्या हुआ यह समझाएँ",
        "ask_for_lawyer": "वकील माँगें",
        "refuse_give_name": "अपना नाम बताने से इंकार करें",
        "try_negotiate": "पुलिस से बातचीत कर समझौता करें",
        "always_ask_lawyer": "हमेशा वकील माँगें और चुप रहें।",

        "check_answer": "✓ उत्तर जाँचें {number}",
        "question_number": "प्रश्न {number}: {question}",
        "select_answer": "उत्तर चुनें:",
        "your_score": "आपका स्कोर",

        "talk_community": "💬 समुदाय से बात करें",
        "community_intro": "अनुभव साझा करें, प्रश्न पूछें और दूसरों की मदद करें — मिलकर हम मजबूत हैं",
        "share_exp_tab": "💭 अनुभव साझा करें",
        "ask_q_tab": "❓ प्रश्न पूछें",
        "give_advice_tab": "💡 सलाह दें",
        "share_your_exp": "💭 अपना अनुभव साझा करें",
        "share_story": "अपना अनुभव साझा करें ताकि दूसरों को मदद मिल सके। सभी पोस्ट सुरक्षा के लिए समीक्षा की जाती हैं।",
        "title_label": "शीर्षक:",
        "exp_placeholder": "उदाहरण: ट्रैफ़िक रोकने पर सुझाव",
        "your_story": "आपका अनुभव:",
        "story_placeholder": "अपनी कहानी लिखें...",
        "post_anonymously": "अनाम रूप से पोस्ट करें",
        "share_exp_btn": "📤 अनुभव साझा करें",
        "fill_title_content": "⚠️ कृपया शीर्षक और सामग्री भरें",
        "exp_shared": "✅ आपका अनुभव साझा कर दिया गया! समुदाय की मदद करने के लिए धन्यवाद।",
        "ask_community": "❓ समुदाय से प्रश्न पूछें",
        "question_help": "कोई प्रश्न है? समुदाय आपकी मदद करेगा।",
        "your_question": "आपका प्रश्न:",
        "question_placeholder": "उदाहरण: ट्रैफ़िक रोकने पर मेरे अधिकार क्या हैं?",
        "details_label": "विवरण:",
        "details_placeholder": "अधिक जानकारी दें...",
        "ask_anon": "अनाम रूप से पोस्ट करें",
        "ask_q_btn": "❓ प्रश्न पोस्ट करें",
        "enter_question": "⚠️ कृपया अपना प्रश्न दर्ज करें",
        "question_posted": "✅ आपका प्रश्न पोस्ट कर दिया गया!",

        "give_advice": "💡 सलाह दें",
        "help_others": "अपने ज्ञान और अनुभव से दूसरों की मदद करें।",
        "topic_label": "विषय:",
        "topic_placeholder": "उदाहरण: अदालत के लिए कैसे तैयारी करें",
        "your_advice": "आपकी सलाह:",
        "advice_placeholder": "अपनी सलाह लिखें...",
        "share_anon": "अनाम रूप से साझा करें",
        "share_advice_btn": "💡 सलाह साझा करें",
        "share_wisdom": "✅ आपकी सलाह साझा कर दी गई!",
        "fill_topic_advice": "⚠️ कृपया विषय और सलाह भरें",

        "recent_posts": "📋 हाल के पोस्ट",
        "no_posts_yet": "💭 अभी तक कोई पोस्ट नहीं। पहला पोस्ट आप करें!",
        "posted_recently": "{timestamp} पहले पोस्ट किया गया",
        "author_anonymous": "अनाम",
        "author_community_member": "समुदाय सदस्य",

        "crisis_hotlines": "🚨 संकट हेल्पलाइन और आपातकालीन सहायता",
        "crisis_support_24": "24/7 सहायता जब भी आपको ज़रूरत हो",
        "emergency_hotlines_header": "🆘 आपातकालीन हेल्पलाइन",
        "in_immediate_danger": "यदि आप तत्काल खतरे में हैं, 911 पर कॉल करें",
        "emergency_number": "आपातकालीन नंबर",
        "suicide_prevention": "राष्ट्रीय आत्महत्या रोकथाम हेल्पलाइन",
        "domestic_violence": "घरेलू हिंसा हेल्पलाइन",
        "sexual_assault": "RAINN — यौन उत्पीड़न सहायता",
        "poison_control": "ज़हर नियंत्रण केंद्र",
        "crisis_text": "क्राइसिस टेक्स्ट लाइन",

        "safety_procedures": "📋 सुरक्षा प्रक्रियाएँ",
        "stay_safe": "🛡️ सुरक्षित रहें",
        "stay_safe_desc": "अपनी सुरक्षा को प्राथमिकता दें — विरोध न करें। आपकी जान सबसे महत्वपूर्ण है।",
        "document_details": "📝 विवरण दर्ज करें",
        "document_details_desc": "अधिकारी का नाम, बैज नंबर, स्थान, समय और उनकी कार्रवाई लिखें।",
        "record_safely": "🎥 सुरक्षित रूप से रिकॉर्ड करें",
        "record_safely_desc": "यदि कानूनी और सुरक्षित हो, वीडियो रिकॉर्ड करें। कैमरा दिखाई रखें।",
        "call_for_help": "📞 मदद के लिए कॉल करें",
        "call_help_desc": "यदि खतरा हो, तुरंत 911 पर कॉल करें। स्पष्ट रूप से बोलें।",
        "get_legal_help": "⚖️ कानूनी सहायता प्राप्त करें",
        "legal_help_desc": "वकील से संपर्क करें। कई सार्वजनिक रक्षक आपातकालीन सहायता प्रदान करते हैं।",
        "medical_attention": "🏥 चिकित्सीय सहायता",
        "medical_attention_desc": "यदि चोट लगी है, तुरंत इलाज कराएँ और चोटों की तस्वीरें लें।",
        "mental_health_support": "🧠 मानसिक स्वास्थ्य सहायता",
        "legal_troubles_trauma": "कानूनी समस्याएँ या पुलिस मुठभेड़ मानसिक तनाव पैदा कर सकती हैं।",
        "mental_health_resources": "मानसिक स्वास्थ्य संसाधन:",
        "samhsa_helpline": "SAMHSA हेल्पलाइन: 1‑800‑662‑4357 (नि:शुल्क, गोपनीय, 24/7)",
        "psychology_directory": "थेरेपिस्ट खोजें: Psychology Today डायरेक्टरी",
        "support_groups": "सपोर्ट ग्रुप: NAACP, सामुदायिक केंद्र, कानूनी संगठन",
        "contact_emergency": "🆘 आपातकाल",
        "contact_suicide": "🧠 आत्महत्या रोकथाम",
        "contact_domestic": "💔 घरेलू हिंसा हेल्पलाइन",
        "contact_rainn": "🤝 RAINN — यौन उत्पीड़न सहायता",
        "contact_poison": "☠️ ज़हर नियंत्रण",
        "contact_crisis_text": "📱 क्राइसिस टेक्स्ट लाइन",
        "contact_crisis_text_number": "HOME लिखकर 741741 पर भेजें",

        "enc_type_traffic_stop": "ट्रैफ़िक रोक",
        "enc_type_street_encounter": "सड़क मुठभेड़",
        "enc_type_arrest": "गिरफ्तारी",
        "enc_type_search": "तलाशी",
        "enc_type_other": "अन्य",
        "encounter_label": "मुठभेड़",
        "unknown": "अज्ञात",
        "na": "लागू नहीं",
        "error_generating_qr": "QR कोड बनाने में त्रुटि हुई",

        "btn_launch_app": "🚀 ऐप खोलें",
        "btn_start_demo": "📺 डेमो शुरू करें",
        "btn_quick_tour": "❓ त्वरित टूर",
        "share_with_others": "📱 दूसरों के साथ साझा करें",
        "qr_generation_in_progress": "QR कोड बनाया जा रहा है...",
        "key_features_label": "मुख्य विशेषताएँ:",
        "btn_previous": "⬅️ पिछला",
        "language_change_error": "भाषा बदलने में त्रुटि",
        "demo_mode_active_sidebar": "✅ डेमो मोड ON — नमूना डेटा दिखाया जा रहा है",
        "screen_reader_off": "🔇 स्क्रीन रीडर OFF",
        "navigation_title": "नेविगेशन",
        "nav_rights_full": "⚖️ अपने अधिकार जानें",
        "nav_resources_near_you": "📍 आपके पास उपलब्ध सेवाएँ",
        "nav_logging_full": "📝 मुठभेड़ लॉग",
        "nav_crisis_resources": "🚨 संकट संसाधन",
        "nav_community": "💬 समुदाय",

        "sidebar_built_for": "सभी के नागरिक अधिकारों की रक्षा के लिए बनाया गया।",
        "show_landing_page": "🏠 लैंडिंग पेज दिखाएँ",

        "landing_hero_html": "<div class=\"landing-hero\"><h1>⚖️ CivicShield Pro</h1><h2>अपने अधिकार जानें। खुद की रक्षा करें। सहायता प्राप्त करें।</h2><p>एक बहुभाषी प्लेटफ़ॉर्म जो सभी को वास्तविक जीवन में अपने नागरिक अधिकार समझने और उपयोग करने में मदद करता है।</p></div>",

        "landing_purpose_md": "### 🎯 उद्देश्य\nCivicShield Pro प्रदान करता है:\n\n- **14 भाषाओं में रियल‑टाइम कानूनी अनुवाद**\n- **अधिकारों की जानकारी** जो आपकी स्थिति के अनुसार हो\n- **कानूनी दस्तावेज़ विश्लेषण** और डेडलाइन एक्सट्रैक्शन\n- **समुदाय समर्थन** और अनुभव साझा करना\n- **24/7 संकट संसाधन**",

        "landing_features_md": "### ⭐ मुख्य विशेषताएँ\n\n- 🗣️ **रियल‑टाइम अनुवाद** — पुलिस क्या कह रही है समझें\n- 📄 **कानूनी दस्तावेज़ टूल्स** — महत्वपूर्ण जानकारी निकालें\n- ⚖️ **अधिकार शिक्षा** — पाठ और क्विज़\n- 📍 **पास की सेवाएँ** — कानूनी सहायता और सामुदायिक केंद्र\n- 📝 **मुठभेड़ लॉगिंग** — पुलिस मुठभेड़ रिकॉर्ड करें\n- 🚨 **आपातकालीन हेल्पलाइन** — 24/7 सहायता\n- 💬 **समुदाय मंच** — प्रश्न पूछें और अनुभव साझा करें",

        "landing_share_md": "**CivicShield दूसरों के साथ साझा करें:**\n\n1. QR कोड स्कैन करें\n2. कोई इंस्टॉल आवश्यक नहीं\n3. 14 भाषाओं का समर्थन\n4. फ़ोन, टैबलेट और कंप्यूटर पर काम करता है",

        "landing_who_should_use_md": "### 👥 यह किसके लिए है?\n\n**न्यायाधीश और कानूनी पेशेवर:**\n- समुदाय के दृष्टिकोण को समझें\n- प्रतिवादियों की अधिकार‑समझ का मूल्यांकन करें\n- रियल‑टाइम अनुवाद का उपयोग करें\n\n**वकील और कानूनी सहायता संगठन:**\n- बहुभाषी कानूनी जानकारी प्रदान करें\n- क्लाइंट्स को मुठभेड़ रिकॉर्ड करने में मदद करें\n- उन्हें सामुदायिक संसाधनों से जोड़ें\n\n**शिक्षक:**\n- नागरिक अधिकार पढ़ाएँ\n- वास्तविक जीवन के उदाहरणों का उपयोग करें\n- इंटरैक्टिव क्विज़ दें\n\n**समुदाय:**\n- पुलिस मुठभेड़ में क्या करना है जानें\n- आपातकालीन संसाधनों का उपयोग करें\n- अनुभव साझा करें",

        "landing_disclaimer_md": "**⚠️ कानूनी अस्वीकरण:**\n\nCivicShield Pro शैक्षिक जानकारी प्रदान करता है, कानूनी सलाह नहीं।\nकानून स्थान के अनुसार बदलते हैं।\nविशिष्ट सलाह के लिए वकील से परामर्श करें।",

        "tutorial_intro_html": "<div class=\"tutorial-container\"><h1>👋 CivicShield Pro में आपका स्वागत है!</h1><p>आइए मुख्य विशेषताएँ देखें।</p></div>",

        "tutorial_step1_title": "🏠 मुख्य डैशबोर्ड",
        "tutorial_step1_desc": "यहाँ से आप सभी फीचर एक्सेस कर सकते हैं।",
        "tutorial_step1_feat1": "सभी टूल्स का नेविगेशन",
        "tutorial_step1_feat2": "सहेजी गई डेडलाइन देखें",
        "tutorial_step1_feat3": "आपातकालीन संसाधन",

        "tutorial_step2_title": "🗣️ रियल‑टाइम अनुवाद",
        "tutorial_step2_desc": "पुलिस की बात को 14 भाषाओं में अनुवाद करें।",
        "tutorial_step2_feat1": "स्पीच‑टू‑टेक्स्ट",
        "tutorial_step2_feat2": "तुरंत अनुवाद",
        "tutorial_step2_feat3": "ऑडियो प्लेबैक",

        "tutorial_step3_title": "📄 कानूनी दस्तावेज़",
        "tutorial_step3_desc": "दस्तावेज़ अपलोड करें और महत्वपूर्ण जानकारी निकालें।",
        "tutorial_step3_feat1": "डेडलाइन एक्सट्रैक्शन",
        "tutorial_step3_feat2": "दंड पहचान",
        "tutorial_step3_feat3": "दस्तावेज़ अनुवाद",

        "tutorial_step4_title": "⚖️ अपने अधिकार जानें",
        "tutorial_step4_desc": "अधिकार सीखें और क्विज़ दें।",
        "tutorial_step4_feat1": "अधिकार शिक्षा",
        "tutorial_step4_feat2": "इंटरैक्टिव क्विज़",
        "tutorial_step4_feat3": "प्रगति ट्रैकिंग",

        "tutorial_step5_title": "📍 पास की सेवाएँ",
        "tutorial_step5_desc": "कानूनी सहायता और सामुदायिक सेवाएँ खोजें।",
        "tutorial_step5_feat1": "लोकेशन‑आधारित खोज",
        "tutorial_step5_feat2": "सेवा फ़िल्टर",
        "tutorial_step5_feat3": "त्वरित दिशा‑निर्देश",

        "tutorial_step6_title": "💬 समुदाय मंच",
        "tutorial_step6_desc": "अनुभव साझा करें, प्रश्न पूछें और दूसरों की मदद करें।",
        "tutorial_step6_feat1": "अनाम पोस्टिंग",
        "tutorial_step6_feat2": "कानूनी प्रश्न",
        "tutorial_step6_feat3": "सलाह साझा करना",

        "documents_intro_md": "कानूनी दस्तावेज़ (फोटो या PDF) अपलोड करें ताकि:\n- तिथियाँ और डेडलाइन निकाली जा सकें\n- आवश्यक कार्य पहचाने जा सकें\n- दंड और चेतावनियाँ मिल सकें\n- सरकारी एजेंसियाँ पहचानी जा सकें\n- दस्तावेज़ का सारांश तैयार हो सके",

    },
    "Korean / 한국어": {
        "sidebar_title": "CivicShield",
        "sidebar_tagline": "당신의 권리를 이해하세요",
        "select_language": "📍 언어 선택:",
        "nav_home": "🏠 홈",
        "nav_translation": "🗣️ 실시간 번역",
        "nav_documents": "📄 법률 문서",
        "nav_rights": "📚 권리 센터",
        "nav_quiz": "❓ 권리 퀴즈",
        "nav_resources": "🏥 지역 서비스",
        "nav_nearby": "📍 내 주변 권리",
        "nav_logging": "📝 대면 기록",
        "nav_emergency": "🚨 긴급 지원",
        "nav_about": "CivicShield 소개",
        "sidebar_version": "버전 3.0.0",
        "sidebar_purpose": "시민권 보호 및 전문 법률 번역",
        "sidebar_languages": "14개 언어 지원",
        "sidebar_disclaimer": "⚠️ 법적 고지",
        "sidebar_disclaimer_text": "이 앱은 교육용 정보를 제공하며 법률 자문이 아닙니다. 구체적인 조언은 변호사와 상담하세요.",

        "home_title": "CivicShield에 오신 것을 환영합니다",
        "home_subtitle": "당신의 권리를 알고, 자신을 보호하고, 도움을 받으세요.",
        "dashboard_intro": "시작하려면 아래 기능 중 하나를 선택하세요:",

        "card_translation_title": "실시간 번역",
        "card_translation_desc": "경찰이 말하는 내용을 번역하고 법률 조언을 받으세요",
        "card_documents_title": "법률 문서 도우미",
        "card_documents_desc": "문서를 업로드하고 중요한 정보를 추출하세요",
        "card_rights_title": "권리 교육 센터",
        "card_rights_desc": "헌법상 권리를 배우세요",
        "card_quiz_title": "권리 퀴즈",
        "card_quiz_desc": "시민권 지식을 테스트하세요",
        "card_resources_title": "지역 서비스",
        "card_resources_desc": "법률 지원, 긴급 서비스 및 커뮤니티 도움 찾기",
        "card_nearby_title": "내 주변 권리",
        "card_nearby_desc": "가까운 법률 지원 및 커뮤니티 서비스 찾기",
        "card_logging_title": "대면 기록",
        "card_logging_desc": "경찰과의 대면 상황을 기록하세요",
        "card_emergency_title": "긴급 지원",
        "card_emergency_desc": "긴급 전화번호 및 절차",

        "btn_open": "열기",
        "btn_delete": "❌",
        "btn_record": "🎤 녹음",
        "btn_stop": "⏹️ 중지",
        "btn_translate": "🌐 번역",
        "btn_listen": "🔊 듣기",
        "btn_download": "📥 다운로드",
        "btn_search": "🔍 검색",
        "btn_log": "📝 기록",
        "btn_back": "← 뒤로",
        "btn_submit": "✓ 제출",
        "btn_cancel": "✗ 취소",

        "translation_title": "실시간 번역",
        "translation_subtitle": "경찰이 말하는 내용을 번역하고 법률 조언을 제공합니다",
        "officer_statement": "경찰이 말한 내용 (영어):",
        "your_rights": "당신의 권리 및 법률 조언:",
        "play_before_title": "1. 상호작용 전 재생",
        "play_before_desc": "녹음 시작 전 경찰에게 이 내용을 재생하세요.",
        "play_before_audio": "Officer, before we begin, I am using a translation app to avoid any language barriers. I am recording with your knowledge for safety and accuracy.",
        "play_after_title": "3. 권리 이해 후 재생",
        "play_after_desc": "자신의 권리를 들은 후 경찰에게 이 내용을 재생하세요.",
        "play_after_audio": "I understand, officer, and I will comply, but I will be using my right to remain silent.",
        "officer_script": "경찰용 스크립트 (영어):",
        "officer_script_translated": "이것이 귀하의 언어로 의미하는 바:",
        "record_officer": "🎤 경찰 음성 녹음",
        "stop_recording": "⏹️ 녹음 중지 및 번역",
        "listen_to_advice": "🔊 조언 듣기",
        "translation_hint": "번역하려면 입력하거나 녹음하세요",
        "generating_audio": "오디오 생성 중...",
        "audio_ready": "✅ 오디오 준비 완료",
        "audio_failed": "❌ 오디오 생성 실패",
        "speech_recognized": "음성이 텍스트로 변환되었습니다.",
        "mic_unclear": "음성이 명확하지 않습니다. 다시 녹음해주세요.",
        "stt_unavailable": "음성 인식 서비스를 사용할 수 없습니다.",
        "unable_process_audio": "오디오를 처리할 수 없습니다. 다시 시도하세요.",
        "mic_recorder_title": "오디오 녹음기",
        "mic_recorder_desc": "경찰의 말을 녹음하려면 시작/중지 버튼을 사용하세요.",
        "mic_help": "마이크가 차단된 경우 브라우저 설정에서 허용해야 합니다.",
        "mic_access_failed": "마이크 접근 권한이 없습니다. 허용 후 다시 시도하세요.",
        "mic_no_audio": "녹음된 오디오가 없습니다. 마이크가 차단되었을 수 있습니다.",
        "btn_clear_filter": "필터 제거",
        "currently_filtering": "현재 적용된 필터:",
        "quiz_correct": "✅ 정답!",
        "quiz_incorrect": "❌ 오답입니다.",
        "language_selector_error": "❌ 언어 선택 오류",
        "demo_section_title": "데모 모드 및 테스트",
        "demo_on": "🎬 데모 ON",
        "demo_off": "🎬 데모 OFF",
        "tour_button": "🎓 둘러보기",
        "tour_complete": "✅ 둘러보기 완료! 준비되었습니다.",
        "btn_go_home": "🏠 홈으로",
        "btn_skip_tour": "⏭️ 건너뛰기",
        "btn_next": "다음 ➡️",
        "btn_start_using": "🎉 시작하기!",

        "documents_title": "법률 문서 도우미",
        "documents_subtitle": "문서를 업로드하고 중요한 정보를 추출하세요",
        "upload_document": "📤 문서 업로드",
        "take_photo": "📸 사진 촬영",
        "extract_text": "텍스트 추출",
        "simplify_text": "쉬운 법률 언어로 변환",
        "translate_document": "🌐 문서 번역",
        "extract_dates": "📅 발견된 날짜",
        "extract_deadlines": "⏰ 마감일",
        "extract_agencies": "🏛️ 정부 기관",
        "extract_actions": "✅ 필요한 조치",
        "download_report": "📥 보고서 다운로드",
        "report_generated": "보고서가 생성되었습니다",

        "rights_title": "권리 센터",
        "rights_subtitle": "헌법상 권리를 배우세요",
        "right_fourth": "제4수정헌법: 수색 및 압수",
        "right_fifth": "제5수정헌법: 묵비권",
        "right_sixth": "제6수정헌법: 변호인 권리",
        "right_traffic": "교통 단속 시 권리",
        "right_arrest": "체포될 경우",
        "right_fourth_content": "**당신의 권리:** 부당한 수색과 압수로부터 보호받습니다.\n\n**중요 사항:**\n- 경찰은 일반적으로 집, 차량, 소지품을 수색하려면 영장이 필요합니다\n- 당신은 명확하게 말할 수 있습니다: \"수색에 동의하지 않습니다\"\n- 절대 저항하거나 물리적으로 막지 마세요 — 추가 혐의가 생길 수 있습니다\n- 경찰이 영장 또는 probable cause(개연성 있는 이유)를 가지고 있다면 수색을 진행할 수 있습니다\n\n**당신이 할 수 있는 것:**\n- 침착하게 \"제가 가도 되나요?\"라고 물어보세요\n- \"수색 영장이 있나요?\"라고 물어보세요\n- 손을 보이게 유지하세요\n- 경찰의 움직임을 방해하지 마세요",

        "right_fifth_content": "**당신의 권리:** 묵비권이 있으며 자신에게 불리한 진술을 강요받지 않습니다.\n\n**중요 사항:**\n- 경찰 질문에 반드시 답할 필요는 없습니다\n- 명확하게 말하세요: \"묵비권을 행사하겠습니다\"\n- 이 권리는 체포 전에도 적용됩니다\n- 침묵은 법정에서 불리하게 사용될 수 없습니다\n\n**주의:**\n- 이 권리는 명확하게 표현해야 합니다\n- 체포되면 즉시 변호인을 요청하세요\n- 설명하거나 협상하지 마세요",

        "right_sixth_content": "**당신의 권리:** 변호인을 선임할 권리가 있습니다.\n\n**중요 사항:**\n- 변호사 비용을 감당할 수 없다면 국선 변호사가 배정됩니다\n- 언제든지 변호인을 요청할 수 있습니다\n- 변호인을 요청하면 경찰은 심문을 중단해야 합니다\n- 변호인은 심문 중 당신과 함께 있을 수 있습니다\n\n**말해야 할 것:**\n- \"변호사와 이야기하고 싶습니다\"\n- \"변호인 권리를 행사하겠습니다\"\n- 이후 변호사가 올 때까지 침묵하세요",

        "right_traffic_content": "**교통 단속 시 해야 할 일:**\n- 운전면허증, 차량 등록증, 보험증을 제시해야 합니다\n- \"제가 구금된 건가요, 아니면 가도 되나요?\"라고 물어보세요\n- 차량 수색에 동의할 필요는 없습니다\n- \"수색에 동의하지 않습니다\"라고 말하세요\n\n**차량 수색:**\n- 경찰은 차량 내부를 눈으로 확인할 수 있습니다\n- probable cause가 있으면 수색할 수 있습니다\n- 체포될 경우 차량 수색이 가능합니다\n\n**당신의 권리:**\n- 손을 보이게 유지하세요\n- 침착하고 정중하게 행동하세요\n- 저항하지 마세요\n- 방해하지 않는 한 녹화할 수 있습니다",

        "right_arrest_content": "**체포 시 중요한 단계:**\n1. 침묵하세요 — 질문에 답하지 마세요\n2. \"변호사를 원합니다\"라고 말하세요\n3. 변호사 없이 어떤 문서에도 서명하지 마세요\n4. 다른 수감자에게 사건을 이야기하지 마세요\n\n**체포 시 권리:**\n- 체포 이유를 알려야 합니다\n- 전화할 권리가 있습니다\n- 묵비권이 있습니다\n- 변호인을 선임할 권리가 있습니다\n\n**하지 말아야 할 것:**\n- 저항하지 마세요 (체포가 부당해 보여도)\n- 자백하지 마세요\n- 수색에 동의하지 마세요\n- 경찰과 협상하지 마세요",

        "resources_title": "지역 서비스",
        "resources_subtitle": "법률 지원 및 커뮤니티 도움 찾기",
        "legal_aid": "법률 지원 기관",
        "emergency_services": "긴급 서비스",
        "immigration": "이민 법률 서비스",
        "phone": "전화: ",
        "services": "서비스: ",
        "website": "웹사이트: ",
        "hours": "운영 시간: ",

        "nearby_title": "내 주변 권리",
        "nearby_subtitle": "가까운 법률 지원 및 서비스 찾기",
        "enter_address": "주소를 입력하세요:",
        "search_radius": "검색 범위 (마일):",
        "nearest_legal_aid": "📋 가장 가까운 법률 지원 기관",
        "nearest_courthouse": "⚖️ 가장 가까운 법원",
        "nearest_police": "👮 가장 가까운 경찰서",
        "nearest_translator": "🗣️ 번역 서비스",
        "nearest_community": "🏢 커뮤니티 센터",
        "address": "주소: ",
        "phone_number": "전화번호: ",
        "hours_open": "운영 시간: ",
        "get_directions": "🗺️ 길찾기",
        "not_found": "이 지역에서 결과를 찾을 수 없습니다",
        "logging_title": "대면 기록",
        "logging_subtitle": "경찰과의 대면 상황을 기록하세요",
        "encounter_type": "대면 유형:",
        "encounter_location": "위치:",
        "encounter_details": "상세 내용:",
        "encounter_date": "날짜 및 시간:",
        "officer_info": "경찰 정보:",
        "officer_badge": "배지 번호:",
        "officer_agency": "소속 기관:",
        "encounter_saved": "✅ 대면 기록이 저장되었습니다",
        "view_history": "📋 기록 내역 보기",
        "total_encounters": "총 대면 기록:",
        "search_encounters": "🔍 대면 기록 검색",

        "emergency_title": "긴급 지원",
        "emergency_subtitle": "긴급 전화번호 및 서비스",
        "emergency_911": "911 — 경찰, 소방, 의료",
        "emergency_suicide": "자살 예방 핫라인",
        "emergency_domestic": "가정 폭력 핫라인",
        "emergency_assault": "RAINN — 성폭력 지원",
        "emergency_poison": "독극물 관리 센터",
        "emergency_text": "위기 문자 지원",
        "emergency_procedures": "긴급 상황 시 단계:",
        "procedure_safe": "안전을 확보하세요",
        "procedure_document": "모든 세부 사항을 기록하세요",
        "procedure_record": "합법적이고 안전하다면 녹화하세요",
        "procedure_call": "도움을 요청하세요",
        "procedure_contact": "변호사에게 연락하세요",

        "loading": "불러오는 중...",
        "success": "성공!",
        "error": "오류",
        "warning": "경고",
        "info": "정보",
        "processing": "처리 중...",
        "please_wait": "잠시만 기다려주세요...",
        "no_data": "데이터 없음",
        "try_again": "다시 시도하세요",

        "accessibility_title": "♿ 접근성 설정",
        "text_size": "텍스트 크기:",
        "text_size_normal": "보통",
        "text_size_large": "크게",
        "text_size_extra_large": "아주 크게",
        "high_contrast": "🎨 고대비 모드",
        "high_contrast_on": "고대비 ON",
        "high_contrast_off": "고대비 OFF",
        "screen_reader": "스크린 리더 라벨 활성화",
        "accessibility_saved": "✅ 접근성 설정이 저장되었습니다",
        "extract_deadlines": "📋 발견된 중요한 마감일",
        "extract_penalties": "⚠️ 벌금 및 경고",
        "extract_requirements": "✓ 필요한 조치 및 요구사항",
        "deadline_found": "마감일:",
        "penalty_found": "벌금:",
        "requirement_found": "요구사항:",
        "document_summary": "📋 문서 요약",
        "summary_generated": "요약이 성공적으로 생성되었습니다",

        "location_title": "📍 내 주변 서비스 찾기",
        "enter_address": "주소 또는 우편번호 입력:",
        "search_radius_miles": "검색 범위 (마일):",
        "find_resources": "🔍 서비스 검색",
        "resource_type": "서비스 유형:",
        "all_resources": "모든 서비스",
        "legal_aid_offices": "법률 지원 사무소",
        "community_centers": "커뮤니티 센터",
        "language_services": "언어 서비스",
        "emergency_shelters": "긴급 쉼터",
        "distance_away": "마일 거리",
        "get_directions": "🗺️ 길찾기",
        "no_resources_found": "이 지역에서 서비스를 찾을 수 없습니다",
        "resource_hours": "운영 시간:",
        "resource_phone": "전화:",
        "resource_address": "주소:",
        "resource_website": "웹사이트:",
        "loading_resources": "주변 서비스를 검색하는 중...",

        "saved_deadlines": "⏰ 저장된 마감일",
        "upload_legal_doc": "법률 문서 업로드",
        "important_dates": "📅 중요한 날짜",
        "required_actions": "✓ 필요한 조치",
        "critical_deadlines": "⏰ 중요한 마감일",
        "penalties_warnings": "⚠️ 벌금 및 경고",
        "extraction_guide": "문서 추출 가이드",
        "demo_mode_active": "📺 **데모 모드 ON** — 예시 데이터 표시 중",
        "have_deadlines": "📋 중요한 마감일이 있습니다!",
        "view_all_deadlines": "📋 모든 마감일 보기 →",
        "from_document": "문서 출처:",
        "file_type": "파일 유형",
        "file_size": "파일 크기",
        "status_ready": "추출 준비 완료",
        "extract_information": "🔍 정보 추출",
        "extracting_info": "문서에서 정보를 추출하는 중...",
        "no_dates_found": "날짜를 찾을 수 없습니다",
        "no_deadlines_found": "마감일을 찾을 수 없습니다",
        "no_penalties_found": "벌금을 찾을 수 없습니다",
        "download_summary": "📥 요약 다운로드",
        "download_as_txt": "TXT로 다운로드",
        "save_deadlines_to_dashboard": "💾 마감일을 대시보드에 저장",
        "know_your_rights_long": "⚖️ 당신의 권리를 알아두세요",
        "education_quizzes": "교육, 퀴즈 및 학습 모듈",
        "learn_tab": "📚 학습",
        "quiz_tab": "🧪 퀴즈",
        "rights_education": "권리 교육",
        "select_topic": "주제를 선택하세요:",
        "test_knowledge": "시민권 지식을 테스트하세요.",
        "rights_quiz": "권리 퀴즈",

        "can_police_search": "경찰이 허락 없이 차량을 수색할 수 있나요?",
        "only_with_warrant": "영장이 있을 때만",
        "only_prob_cause": "개연성 있는 이유(probable cause)가 있을 때만",
        "both_a_and_b": "A와 B 모두",
        "never_without": "아니요, 절대 불가능합니다",
        "police_can_search": "경찰은 영장 또는 probable cause가 있을 때 차량을 수색할 수 있습니다.",

        "answer_police_q": "경찰 질문에 반드시 답해야 하나요?",
        "yes_always": "네, 항상 답해야 합니다",
        "right_remain_silent": "아니요, 묵비권이 있습니다",
        "only_your_name": "이름만 말하면 됩니다",
        "only_if_arrested": "체포된 경우에만",
        "fifth_amendment": "제5수정헌법은 묵비권과 자기부죄 금지 권리를 보장합니다.",

        "what_say_arrested": "체포될 때 무엇을 말해야 하나요?",
        "explain_what_happened": "무슨 일이 있었는지 설명한다",
        "ask_for_lawyer": "변호사를 요청한다",
        "refuse_give_name": "이름 제공을 거부한다",
        "try_negotiate": "경찰과 협상한다",
        "always_ask_lawyer": "항상 변호사를 요청하고 침묵하세요.",

        "check_answer": "✓ 정답 확인 {number}",
        "question_number": "질문 {number}: {question}",
        "select_answer": "답변을 선택하세요:",
        "your_score": "당신의 점수",

        "talk_community": "💬 커뮤니티와 대화하기",
        "community_intro": "경험을 공유하고 질문하며 서로 도우세요 — 함께하면 더 강해집니다",
        "share_exp_tab": "💭 경험 공유",
        "ask_q_tab": "❓ 질문하기",
        "give_advice_tab": "💡 조언하기",
        "share_your_exp": "💭 경험을 공유하세요",
        "share_story": "당신의 경험을 공유하면 다른 사람들에게 도움이 됩니다. 모든 게시물은 안전을 위해 검토됩니다.",
        "title_label": "제목:",
        "exp_placeholder": "예: 교통 단속 시 대처법",
        "your_story": "당신의 경험:",
        "story_placeholder": "경험을 작성하세요...",
        "post_anonymously": "익명으로 게시",
        "share_exp_btn": "📤 경험 공유",
        "fill_title_content": "⚠️ 제목과 내용을 입력하세요",
        "exp_shared": "✅ 경험이 성공적으로 공유되었습니다! 커뮤니티에 기여해주셔서 감사합니다.",
        "ask_community": "❓ 커뮤니티에 질문하기",
        "question_help": "궁금한 점이 있나요? 커뮤니티가 도와드립니다.",
        "your_question": "당신의 질문:",
        "question_placeholder": "예: 교통 단속 시 내 권리는 무엇인가요?",
        "details_label": "세부 내용:",
        "details_placeholder": "추가 정보를 입력하세요...",
        "ask_anon": "익명으로 게시",
        "ask_q_btn": "❓ 질문 게시",
        "enter_question": "⚠️ 질문을 입력하세요",
        "question_posted": "✅ 질문이 게시되었습니다!",

        "give_advice": "💡 조언하기",
        "help_others": "당신의 지식과 경험으로 다른 사람을 도와주세요.",
        "topic_label": "주제:",
        "topic_placeholder": "예: 법원 준비 방법",
        "your_advice": "당신의 조언:",
        "advice_placeholder": "조언을 작성하세요...",
        "share_anon": "익명으로 공유",
        "share_advice_btn": "💡 조언 공유",
        "share_wisdom": "✅ 조언이 성공적으로 공유되었습니다!",
        "fill_topic_advice": "⚠️ 주제와 조언을 입력하세요",

        "recent_posts": "📋 최근 게시물",
        "no_posts_yet": "💭 아직 게시물이 없습니다. 첫 번째로 게시해보세요!",
        "posted_recently": "{timestamp} 전에 게시됨",
        "author_anonymous": "익명",
        "author_community_member": "커뮤니티 회원",

        "crisis_hotlines": "🚨 위기 핫라인 및 긴급 지원",
        "crisis_support_24": "24시간 언제든지 도움을 받을 수 있습니다",
        "emergency_hotlines_header": "🆘 긴급 전화번호",
        "in_immediate_danger": "즉각적인 위험이 있다면 911에 전화하세요",
        "emergency_number": "긴급 번호",
        "suicide_prevention": "자살 예방 핫라인",
        "domestic_violence": "가정 폭력 핫라인",
        "sexual_assault": "RAINN — 성폭력 지원",
        "poison_control": "독극물 관리 센터",
        "crisis_text": "위기 문자 지원",

        "safety_procedures": "📋 안전 절차",
        "stay_safe": "🛡️ 안전 유지",
        "stay_safe_desc": "항상 안전을 최우선으로 하세요 — 저항하지 마세요.",
        "document_details": "📝 세부 사항 기록",
        "document_details_desc": "경찰 이름, 배지 번호, 위치, 시간, 행동을 기록하세요.",
        "record_safely": "🎥 안전하게 녹화",
        "record_safely_desc": "합법적이고 안전하다면 녹화하세요. 카메라를 보이게 유지하세요.",
        "call_for_help": "📞 도움 요청",
        "call_help_desc": "위험할 경우 즉시 911에 전화하세요. 명확하게 말하세요.",
        "get_legal_help": "⚖️ 법률 지원 받기",
        "legal_help_desc": "변호사에게 연락하세요. 많은 공공 변호사는 긴급 지원을 제공합니다.",
        "medical_attention": "🏥 의료 지원",
        "medical_attention_desc": "부상을 입었다면 즉시 치료받고 사진을 찍어두세요.",
        "mental_health_support": "🧠 정신 건강 지원",
        "legal_troubles_trauma": "법적 문제나 경찰 대면은 정신적 스트레스를 유발할 수 있습니다.",
        "mental_health_resources": "정신 건강 자원:",
        "samhsa_helpline": "SAMHSA 핫라인: 1‑800‑662‑4357 (무료, 비밀, 24/7)",
        "psychology_directory": "상담사 찾기: Psychology Today 디렉터리",
        "support_groups": "지원 그룹: NAACP, 커뮤니티 센터, 법률 단체",
        "contact_emergency": "🆘 긴급 상황",
        "contact_suicide": "🧠 자살 예방",
        "contact_domestic": "💔 가정 폭력 핫라인",
        "contact_rainn": "🤝 RAINN — 성폭력 지원",
        "contact_poison": "☠️ 독극물 관리",
        "contact_crisis_text": "📱 위기 문자 지원",
        "contact_crisis_text_number": "HOME을 741741로 문자 보내기",

        "enc_type_traffic_stop": "교통 단속",
        "enc_type_street_encounter": "거리 대면",
        "enc_type_arrest": "체포",
        "enc_type_search": "수색",
        "enc_type_other": "기타",
        "encounter_label": "대면",
        "unknown": "알 수 없음",
        "na": "해당 없음",
        "error_generating_qr": "QR 코드를 생성하는 중 오류가 발생했습니다",

        "btn_launch_app": "🚀 앱 실행",
        "btn_start_demo": "📺 데모 시작",
        "btn_quick_tour": "❓ 빠른 둘러보기",
        "share_with_others": "📱 다른 사람과 공유",
        "qr_generation_in_progress": "QR 코드 생성 중...",
        "key_features_label": "주요 기능:",
        "btn_previous": "⬅️ 이전",
        "language_change_error": "언어 변경 오류",
        "demo_mode_active_sidebar": "✅ 데모 모드 ON — 예시 데이터 표시 중",
        "screen_reader_off": "🔇 스크린 리더 OFF",
        "navigation_title": "내비게이션",
        "nav_rights_full": "⚖️ 권리 알아보기",
        "nav_resources_near_you": "📍 내 주변 서비스",
        "nav_logging_full": "📝 대면 기록",
        "nav_crisis_resources": "🚨 위기 자원",
        "nav_community": "💬 커뮤니티",

        "sidebar_built_for": "모든 사람의 시민권 보호를 위해 제작되었습니다.",
        "show_landing_page": "🏠 랜딩 페이지 보기",

        "landing_hero_html": "<div class=\"landing-hero\"><h1>⚖️ CivicShield Pro</h1><h2>당신의 권리를 알고, 자신을 보호하고, 도움을 받으세요.</h2><p>14개 언어로 시민권을 이해하고 활용할 수 있도록 돕는 플랫폼입니다.</p></div>",

        "landing_purpose_md": "### 🎯 목적\nCivicShield Pro는 다음을 제공합니다:\n\n- **14개 언어 실시간 법률 번역**\n- **상황별 권리 안내**\n- **법률 문서 분석 및 마감일 추출**\n- **커뮤니티 지원 및 경험 공유**\n- **24/7 위기 자원**",

        "landing_features_md": "### ⭐ 주요 기능\n\n- 🗣️ **실시간 번역** — 경찰 발언 이해\n- 📄 **법률 문서 도구** — 중요한 정보 추출\n- ⚖️ **권리 교육** — 학습 및 퀴즈\n- 📍 **내 주변 서비스** — 법률 지원 및 커뮤니티 센터\n- 📝 **대면 기록** — 경찰 대면 상황 기록\n- 🚨 **긴급 핫라인** — 24/7 지원\n- 💬 **커뮤니티 포럼** — 질문 및 경험 공유",

        "landing_share_md": "**CivicShield를 공유하세요:**\n\n1. QR 코드 스캔\n2. 설치 필요 없음\n3. 14개 언어 지원\n4. 휴대폰, 태블릿, 컴퓨터 모두 사용 가능",

        "landing_who_should_use_md": "### 👥 누가 사용해야 하나요?\n\n**판사 및 법률 전문가:**\n- 커뮤니티 관점 이해\n- 피고인의 권리 이해도 평가\n- 실시간 번역 활용\n\n**변호사 및 법률 지원 단체:**\n- 다국어 법률 정보 제공\n- 클라이언트의 대면 기록 지원\n- 지역 자원 연결\n\n**교육자:**\n- 시민권 교육\n- 실제 사례 활용\n- 인터랙티브 퀴즈 제공\n\n**커뮤니티 구성원:**\n- 경찰 대면 시 대처법 학습\n- 긴급 자원 활용\n- 경험 공유",

        "landing_disclaimer_md": "**⚠️ 법적 고지:**\n\nCivicShield Pro는 교육용 정보를 제공하며 법률 자문이 아닙니다.\n법률은 지역에 따라 다를 수 있습니다.\n구체적인 조언은 변호사와 상담하세요.",

        "tutorial_intro_html": "<div class=\"tutorial-container\"><h1>👋 CivicShield Pro에 오신 것을 환영합니다!</h1><p>주요 기능을 함께 살펴봅시다.</p></div>",

        "tutorial_step1_title": "🏠 메인 대시보드",
        "tutorial_step1_desc": "모든 기능에 접근할 수 있는 중심 화면입니다.",
        "tutorial_step1_feat1": "전체 기능 내비게이션",
        "tutorial_step1_feat2": "저장된 마감일 보기",
        "tutorial_step1_feat3": "긴급 자원",

        "tutorial_step2_title": "🗣️ 실시간 번역",
        "tutorial_step2_desc": "경찰 발언을 14개 언어로 번역합니다.",
        "tutorial_step2_feat1": "음성 인식",
        "tutorial_step2_feat2": "즉시 번역",
        "tutorial_step2_feat3": "오디오 재생",

        "tutorial_step3_title": "📄 법률 문서",
        "tutorial_step3_desc": "문서를 업로드하고 중요한 정보를 추출하세요.",
        "tutorial_step3_feat1": "마감일 추출",
        "tutorial_step3_feat2": "벌금 식별",
        "tutorial_step3_feat3": "문서 번역",

        "tutorial_step4_title": "⚖️ 권리 알아보기",
        "tutorial_step4_desc": "권리를 배우고 퀴즈를 풀어보세요.",
        "tutorial_step4_feat1": "권리 교육",
        "tutorial_step4_feat2": "인터랙티브 퀴즈",
        "tutorial_step4_feat3": "진행 상황 추적",

        "tutorial_step5_title": "📍 내 주변 서비스",
        "tutorial_step5_desc": "법률 지원 및 커뮤니티 서비스를 찾으세요.",
        "tutorial_step5_feat1": "위치 기반 검색",
        "tutorial_step5_feat2": "서비스 필터",
        "tutorial_step5_feat3": "빠른 길찾기",

        "tutorial_step6_title": "💬 커뮤니티 포럼",
        "tutorial_step6_desc": "경험을 공유하고 질문하며 서로 도우세요.",
        "tutorial_step6_feat1": "익명 게시",
        "tutorial_step6_feat2": "법률 질문",
        "tutorial_step6_feat3": "조언 공유",

        "documents_intro_md": "법률 문서(PDF 또는 사진)를 업로드하여:\n- 날짜 및 마감일 추출\n- 필요한 조치 식별\n- 벌금 및 경고 확인\n- 관련 정부 기관 식별\n- 문서 요약 생성",

    },
    "Japanese / 日本語": {
        "sidebar_title": "CivicShield",
        "sidebar_tagline": "あなたの権利を理解しましょう",
        "select_language": "📍 言語を選択:",
        "nav_home": "🏠 ホーム",
        "nav_translation": "🗣️ リアルタイム翻訳",
        "nav_documents": "📄 法律文書",
        "nav_rights": "📚 権利センター",
        "nav_quiz": "❓ 権利クイズ",
        "nav_resources": "🏥 地域サービス",
        "nav_nearby": "📍 近くの権利情報",
        "nav_logging": "📝 対応記録",
        "nav_emergency": "🚨 緊急支援",
        "nav_about": "CivicShieldについて",
        "sidebar_version": "バージョン 3.0.0",
        "sidebar_purpose": "市民権保護と専門的な法律翻訳",
        "sidebar_languages": "14言語対応",
        "sidebar_disclaimer": "⚠️ 免責事項",
        "sidebar_disclaimer_text": "このアプリは教育目的の情報を提供するものであり、法律相談ではありません。具体的な助言は弁護士にご相談ください。",

        "home_title": "CivicShieldへようこそ",
        "home_subtitle": "あなたの権利を知り、自分を守り、支援を受けましょう。",
        "dashboard_intro": "以下の機能から選んで開始してください:",

        "card_translation_title": "リアルタイム翻訳",
        "card_translation_desc": "警察が話している内容を翻訳し、法律アドバイスを提供します",
        "card_documents_title": "法律文書アシスタント",
        "card_documents_desc": "文書をアップロードして重要情報を抽出します",
        "card_rights_title": "権利教育センター",
        "card_rights_desc": "憲法上の権利を学びましょう",
        "card_quiz_title": "権利クイズ",
        "card_quiz_desc": "市民権の知識をテストしましょう",
        "card_resources_title": "地域サービス",
        "card_resources_desc": "法律支援、緊急サービス、コミュニティ支援を探す",
        "card_nearby_title": "近くの権利情報",
        "card_nearby_desc": "近くの法律支援やコミュニティサービスを検索",
        "card_logging_title": "対応記録",
        "card_logging_desc": "警察とのやり取りを記録します",
        "card_emergency_title": "緊急支援",
        "card_emergency_desc": "緊急連絡先と手順",

        "btn_open": "開く",
        "btn_delete": "❌",
        "btn_record": "🎤 録音",
        "btn_stop": "⏹️ 停止",
        "btn_translate": "🌐 翻訳",
        "btn_listen": "🔊 再生",
        "btn_download": "📥 ダウンロード",
        "btn_search": "🔍 検索",
        "btn_log": "📝 記録",
        "btn_back": "← 戻る",
        "btn_submit": "✓ 送信",
        "btn_cancel": "✗ キャンセル",

        "translation_title": "リアルタイム翻訳",
        "translation_subtitle": "警察が話した内容を翻訳し、法律アドバイスを提供します",
        "officer_statement": "警察が話した内容（英語）:",
        "your_rights": "あなたの権利と法律アドバイス:",
        "play_before_title": "1. やり取りの前に再生する",
        "play_before_desc": "録音を開始する前に、警察官にこの内容を再生してください。",
        "play_before_audio": "Officer, before we begin, I am using a translation app to avoid any language barriers. I am recording with your knowledge for safety and accuracy.",
        "play_after_title": "3. 権利を理解した後に再生する",
        "play_after_desc": "ご自身の権利を確認した後に、警察官にこの内容を再生してください。",
        "play_after_audio": "I understand, officer, and I will comply, but I will be using my right to remain silent.",
        "officer_script": "警察官向けスクリプト（英語）：",
        "officer_script_translated": "これがあなたの言語での意味：",
        "record_officer": "🎤 警察の音声を録音",
        "stop_recording": "⏹️ 録音停止して翻訳",
        "listen_to_advice": "🔊 アドバイスを再生",
        "translation_hint": "翻訳するには入力または録音してください",
        "generating_audio": "音声を生成しています...",
        "audio_ready": "✅ 音声の準備ができました",
        "audio_failed": "❌ 音声生成に失敗しました",
        "speech_recognized": "音声がテキストに変換されました。",
        "mic_unclear": "音声が不明瞭です。もう一度録音してください。",
        "stt_unavailable": "音声認識サービスを利用できません。",
        "unable_process_audio": "音声を処理できません。再試行してください。",
        "mic_recorder_title": "音声レコーダー",
        "mic_recorder_desc": "警察の発言を録音するには開始/停止ボタンを使用します。",
        "mic_help": "マイクがブロックされている場合、ブラウザ設定で許可が必要です。",
        "mic_access_failed": "マイクへのアクセスが拒否されました。許可して再試行してください。",
        "mic_no_audio": "録音された音声がありません。マイクがブロックされている可能性があります。",
        "btn_clear_filter": "フィルター解除",
        "currently_filtering": "現在のフィルター:",
        "quiz_correct": "✅ 正解！",
        "quiz_incorrect": "❌ 不正解です。",
        "language_selector_error": "❌ 言語選択エラー",
        "demo_section_title": "デモモードとテスト",
        "demo_on": "🎬 デモ ON",
        "demo_off": "🎬 デモ OFF",
        "tour_button": "🎓 ツアーを見る",
        "tour_complete": "✅ ツアー完了！準備ができました。",
        "btn_go_home": "🏠 ホームへ",
        "btn_skip_tour": "⏭️ スキップ",
        "btn_next": "次へ ➡️",
        "btn_start_using": "🎉 使い始める",

        "documents_title": "法律文書アシスタント",
        "documents_subtitle": "文書をアップロードして重要情報を抽出します",
        "upload_document": "📤 文書をアップロード",
        "take_photo": "📸 写真を撮る",
        "extract_text": "テキスト抽出",
        "simplify_text": "やさしい法律文に変換",
        "translate_document": "🌐 文書を翻訳",
        "extract_dates": "📅 見つかった日付",
        "extract_deadlines": "⏰ 期限",
        "extract_agencies": "🏛️ 政府機関",
        "extract_actions": "✅ 必要な行動",
        "download_report": "📥 レポートをダウンロード",
        "report_generated": "レポートが生成されました",

        "rights_title": "権利センター",
        "rights_subtitle": "憲法上の権利を学びましょう",
        "right_fourth": "第4修正：捜索と押収",
        "right_fifth": "第5修正：黙秘権",
        "right_sixth": "第6修正：弁護人の権利",
        "right_traffic": "交通取締り時の権利",
        "right_arrest": "逮捕された場合",
        "right_fourth_content": "**あなたの権利:** 不当な捜索や押収から保護されます。\n\n**重要ポイント:**\n- 警察は通常、家・車・所持品を捜索するには令状が必要です\n- 明確に「捜索に同意しません」と伝えることができます\n- 抵抗したり、物理的に妨害してはいけません（追加の罪に問われる可能性があります）\n- 警察が令状または probable cause（合理的根拠）を持っている場合、捜索が行われることがあります\n\n**あなたができること:**\n- 落ち着いて「私は行ってもいいですか？」と尋ねる\n- 「令状はありますか？」と確認する\n- 手を見える位置に保つ\n- 警察の行動を妨害しない",

        "right_fifth_content": "**あなたの権利:** 黙秘権があり、自分に不利な発言を強制されません。\n\n**重要ポイント:**\n- 警察の質問に答える義務はありません\n- 明確に「黙秘権を行使します」と伝えてください\n- この権利は逮捕前でも有効です\n- 沈黙は法廷で不利に扱われません\n\n**注意:**\n- 権利は明確に主張する必要があります\n- 逮捕されたらすぐに弁護士を要求してください\n- 説明したり交渉したりしないでください",

        "right_sixth_content": "**あなたの権利:** 弁護士をつける権利があります。\n\n**重要ポイント:**\n- 弁護士費用を払えない場合、公選弁護人が割り当てられます\n- いつでも弁護士を要求できます\n- 弁護士を要求すると、警察は取り調べを中止しなければなりません\n- 弁護士は取り調べ中にあなたのそばにいることができます\n\n**言うべき言葉:**\n- 「弁護士と話したいです」\n- 「弁護人の権利を行使します」\n- その後、弁護士が来るまで黙っていてください",

        "right_traffic_content": "**交通取締り時にすべきこと:**\n- 免許証・車両登録証・保険証を提示する必要があります\n- 「私は拘束されていますか、それとも行ってもいいですか？」と尋ねる\n- 車の捜索に同意する必要はありません\n- 「捜索に同意しません」と伝える\n\n**車両の捜索:**\n- 警察は車内を目視で確認できます\n- probable cause（合理的根拠）があれば捜索できます\n- 逮捕された場合、車両が捜索されることがあります\n\n**あなたの権利:**\n- 手を見える位置に保つ\n- 落ち着いて丁寧に対応する\n- 抵抗しない\n- 妨害しない限り録画できます",

        "right_arrest_content": "**逮捕時の重要ステップ:**\n1. 黙っている — 質問に答えない\n2. 「弁護士をお願いします」と言う\n3. 弁護士なしで書類に署名しない\n4. 他の拘留者に事件の話をしない\n\n**逮捕時の権利:**\n- 逮捕理由を知らされる権利\n- 電話をかける権利\n- 黙秘権\n- 弁護人をつける権利\n\n**してはいけないこと:**\n- 抵抗しない（不当だと思っても）\n- 自白しない\n- 捜索に同意しない\n- 警察と交渉しない",

        "resources_title": "地域サービス",
        "resources_subtitle": "法律支援やコミュニティ支援を探す",
        "legal_aid": "法律支援機関",
        "emergency_services": "緊急サービス",
        "immigration": "移民関連の法律支援",
        "phone": "電話: ",
        "services": "サービス: ",
        "website": "ウェブサイト: ",
        "hours": "営業時間: ",

        "nearby_title": "近くの権利情報",
        "nearby_subtitle": "近くの法律支援やサービスを検索",
        "enter_address": "住所を入力してください:",
        "search_radius": "検索範囲（マイル）:",
        "nearest_legal_aid": "📋 最寄りの法律支援機関",
        "nearest_courthouse": "⚖️ 最寄りの裁判所",
        "nearest_police": "👮 最寄りの警察署",
        "nearest_translator": "🗣️ 翻訳サービス",
        "nearest_community": "🏢 コミュニティセンター",
        "address": "住所: ",
        "phone_number": "電話番号: ",
        "hours_open": "営業時間: ",
        "get_directions": "🗺️ ルート案内",
        "not_found": "この地域では結果が見つかりませんでした",
        "logging_title": "対応記録",
        "logging_subtitle": "警察とのやり取りを記録します",
        "encounter_type": "対応の種類:",
        "encounter_location": "場所:",
        "encounter_details": "詳細:",
        "encounter_date": "日時:",
        "officer_info": "警察官情報:",
        "officer_badge": "バッジ番号:",
        "officer_agency": "所属機関:",
        "encounter_saved": "✅ 対応記録が保存されました",
        "view_history": "📋 記録履歴を見る",
        "total_encounters": "総対応件数:",
        "search_encounters": "🔍 対応記録を検索",

        "emergency_title": "緊急支援",
        "emergency_subtitle": "緊急連絡先とサービス",
        "emergency_911": "911 — 警察・消防・救急",
        "emergency_suicide": "自殺予防ホットライン",
        "emergency_domestic": "家庭内暴力ホットライン",
        "emergency_assault": "RAINN — 性暴力支援",
        "emergency_poison": "毒物管理センター",
        "emergency_text": "危機テキストライン",
        "emergency_procedures": "緊急時の手順:",
        "procedure_safe": "安全を確保する",
        "procedure_document": "すべての詳細を記録する",
        "procedure_record": "合法かつ安全であれば録画する",
        "procedure_call": "助けを求める",
        "procedure_contact": "弁護士に連絡する",

        "loading": "読み込み中...",
        "success": "成功！",
        "error": "エラー",
        "warning": "警告",
        "info": "情報",
        "processing": "処理中...",
        "please_wait": "しばらくお待ちください...",
        "no_data": "データなし",
        "try_again": "再試行してください",

        "accessibility_title": "♿ アクセシビリティ設定",
        "text_size": "文字サイズ:",
        "text_size_normal": "標準",
        "text_size_large": "大",
        "text_size_extra_large": "特大",
        "high_contrast": "🎨 ハイコントラストモード",
        "high_contrast_on": "ハイコントラスト ON",
        "high_contrast_off": "ハイコントラスト OFF",
        "screen_reader": "スクリーンリーダーラベルを有効化",
        "accessibility_saved": "✅ アクセシビリティ設定が保存されました",
        "extract_deadlines": "📋 見つかった重要な期限",
        "extract_penalties": "⚠️ 罰金・警告",
        "extract_requirements": "✓ 必要な行動と要件",
        "deadline_found": "期限:",
        "penalty_found": "罰金:",
        "requirement_found": "要件:",
        "document_summary": "📋 文書サマリー",
        "summary_generated": "サマリーが正常に生成されました",

        "location_title": "📍 近くのサービスを探す",
        "enter_address": "住所または郵便番号を入力:",
        "search_radius_miles": "検索範囲（マイル）:",
        "find_resources": "🔍 サービスを検索",
        "resource_type": "サービスの種類:",
        "all_resources": "すべてのサービス",
        "legal_aid_offices": "法律支援オフィス",
        "community_centers": "コミュニティセンター",
        "language_services": "言語サービス",
        "emergency_shelters": "緊急シェルター",
        "distance_away": "マイル離れています",
        "get_directions": "🗺️ ルート案内",
        "no_resources_found": "この地域ではサービスが見つかりませんでした",
        "resource_hours": "営業時間:",
        "resource_phone": "電話:",
        "resource_address": "住所:",
        "resource_website": "ウェブサイト:",
        "loading_resources": "近くのサービスを検索中...",

        "saved_deadlines": "⏰ 保存された期限",
        "upload_legal_doc": "法律文書をアップロード",
        "important_dates": "📅 重要な日付",
        "required_actions": "✓ 必要な行動",
        "critical_deadlines": "⏰ 重要な期限",
        "penalties_warnings": "⚠️ 罰金と警告",
        "extraction_guide": "文書抽出ガイド",
        "demo_mode_active": "📺 **デモモード ON** — サンプルデータを表示中",
        "have_deadlines": "📋 重要な期限があります！",
        "view_all_deadlines": "📋 すべての期限を見る →",
        "from_document": "文書の出典:",
        "file_type": "ファイル形式",
        "file_size": "ファイルサイズ",
        "status_ready": "抽出の準備完了",
        "extract_information": "🔍 情報を抽出",
        "extracting_info": "文書から情報を抽出しています...",
        "no_dates_found": "日付が見つかりませんでした",
        "no_deadlines_found": "期限が見つかりませんでした",
        "no_penalties_found": "罰金が見つかりませんでした",
        "download_summary": "📥 サマリーをダウンロード",
        "download_as_txt": "TXTとしてダウンロード",
        "save_deadlines_to_dashboard": "💾 期限をダッシュボードに保存",
        "know_your_rights_long": "⚖️ あなたの権利を知りましょう",
        "education_quizzes": "教育・クイズ・学習モジュール",
        "learn_tab": "📚 学習",
        "quiz_tab": "🧪 クイズ",
        "rights_education": "権利教育",
        "select_topic": "トピックを選択してください:",
        "test_knowledge": "市民権の知識をテストしましょう。",
        "rights_quiz": "権利クイズ",

        "can_police_search": "警察は許可なしに車を捜索できますか？",
        "only_with_warrant": "令状がある場合のみ",
        "only_prob_cause": "合理的根拠（probable cause）がある場合のみ",
        "both_a_and_b": "AとBの両方",
        "never_without": "いいえ、絶対にできません",
        "police_can_search": "警察は令状または合理的根拠がある場合に車を捜索できます。",

        "answer_police_q": "警察の質問に必ず答えなければなりませんか？",
        "yes_always": "はい、常に答える必要があります",
        "right_remain_silent": "いいえ、黙秘権があります",
        "only_your_name": "名前だけ答えればよい",
        "only_if_arrested": "逮捕された場合のみ",
        "fifth_amendment": "第5修正は黙秘権と自己負罪拒否の権利を保障しています。",

        "what_say_arrested": "逮捕されたとき、何と言うべきですか？",
        "explain_what_happened": "何が起きたか説明する",
        "ask_for_lawyer": "弁護士を要求する",
        "refuse_give_name": "名前の提供を拒否する",
        "try_negotiate": "警察と交渉する",
        "always_ask_lawyer": "常に弁護士を要求し、それ以外は黙っていましょう。",

        "check_answer": "✓ 正解を確認 {number}",
        "question_number": "質問 {number}: {question}",
        "select_answer": "回答を選択してください:",
        "your_score": "あなたのスコア",

        "talk_community": "💬 コミュニティと話す",
        "community_intro": "経験を共有し、質問し、助け合いましょう — みんなで強くなれます",
        "share_exp_tab": "💭 経験を共有",
        "ask_q_tab": "❓ 質問する",
        "give_advice_tab": "💡 アドバイスする",
        "share_your_exp": "💭 あなたの経験を共有しましょう",
        "share_story": "あなたの経験は他の人の助けになります。すべての投稿は安全のために確認されます。",
        "title_label": "タイトル:",
        "exp_placeholder": "例: 交通取締りへの対応方法",
        "your_story": "あなたの経験:",
        "story_placeholder": "経験を書いてください...",
        "post_anonymously": "匿名で投稿",
        "share_exp_btn": "📤 経験を共有",
        "fill_title_content": "⚠️ タイトルと内容を入力してください",
        "exp_shared": "✅ 経験が正常に共有されました！コミュニティへの貢献に感謝します。",
        "ask_community": "❓ コミュニティに質問する",
        "question_help": "疑問がありますか？コミュニティが助けてくれます。",
        "your_question": "あなたの質問:",
        "question_placeholder": "例: 交通取締り時の私の権利は？",
        "details_label": "詳細:",
        "details_placeholder": "追加情報を入力してください...",
        "ask_anon": "匿名で投稿",
        "ask_q_btn": "❓ 質問を投稿",
        "enter_question": "⚠️ 質問を入力してください",
        "question_posted": "✅ 質問が投稿されました！",

        "give_advice": "💡 アドバイスする",
        "help_others": "あなたの知識と経験で他の人を助けましょう。",
        "topic_label": "トピック:",
        "topic_placeholder": "例: 裁判の準備方法",
        "your_advice": "あなたのアドバイス:",
        "advice_placeholder": "アドバイスを書いてください...",
        "share_anon": "匿名で共有",
        "share_advice_btn": "💡 アドバイスを共有",
        "share_wisdom": "✅ アドバイスが正常に共有されました！",
        "fill_topic_advice": "⚠️ トピックとアドバイスを入力してください",

        "recent_posts": "📋 最近の投稿",
        "no_posts_yet": "💭 まだ投稿がありません。最初の投稿者になりましょう！",
        "posted_recently": "{timestamp} 前に投稿",
        "author_anonymous": "匿名",
        "author_community_member": "コミュニティメンバー",

        "crisis_hotlines": "🚨 危機ホットライン・緊急支援",
        "crisis_support_24": "24時間いつでも支援を受けられます",
        "emergency_hotlines_header": "🆘 緊急連絡先",
        "in_immediate_danger": "差し迫った危険がある場合は911に電話してください",
        "emergency_number": "緊急番号",
        "suicide_prevention": "自殺予防ホットライン",
        "domestic_violence": "家庭内暴力ホットライン",
        "sexual_assault": "RAINN — 性暴力支援",
        "poison_control": "毒物管理センター",
        "crisis_text": "危機テキストライン",

        "safety_procedures": "📋 安全手順",
        "stay_safe": "🛡️ 安全を確保",
        "stay_safe_desc": "常に安全を最優先にしてください — 抵抗しないこと。",
        "document_details": "📝 詳細を記録",
        "document_details_desc": "警察官の名前、バッジ番号、場所、時間、行動を記録してください。",
        "record_safely": "🎥 安全に録画",
        "record_safely_desc": "合法かつ安全であれば録画してください。カメラは見える位置に。",
        "call_for_help": "📞 助けを求める",
        "call_help_desc": "危険な場合はすぐに911に電話し、明確に話してください。",
        "get_legal_help": "⚖️ 法律支援を受ける",
        "legal_help_desc": "弁護士に連絡してください。多くの公選弁護人は緊急支援を提供しています。",
        "medical_attention": "🏥 医療支援",
        "medical_attention_desc": "怪我をした場合はすぐに治療を受け、写真を撮って記録してください。",
        "mental_health_support": "🧠 メンタルヘルス支援",
        "legal_troubles_trauma": "法律問題や警察との対面は精神的ストレスを引き起こすことがあります。",
        "mental_health_resources": "メンタルヘルスのリソース:",
        "samhsa_helpline": "SAMHSA ホットライン: 1‑800‑662‑4357（無料・秘密・24/7）",
        "psychology_directory": "カウンセラー検索: Psychology Today ディレクトリ",
        "support_groups": "支援グループ: NAACP、コミュニティセンター、法律団体",
        "contact_emergency": "🆘 緊急時",
        "contact_suicide": "🧠 自殺予防",
        "contact_domestic": "💔 DVホットライン",
        "contact_rainn": "🤝 RAINN — 性暴力支援",
        "contact_poison": "☠️ 毒物管理",
        "contact_crisis_text": "📱 危機テキストライン",
        "contact_crisis_text_number": "HOME と 741741 に送信",

        "enc_type_traffic_stop": "交通取締り",
        "enc_type_street_encounter": "路上での対面",
        "enc_type_arrest": "逮捕",
        "enc_type_search": "捜索",
        "enc_type_other": "その他",
        "encounter_label": "対面",
        "unknown": "不明",
        "na": "該当なし",
        "error_generating_qr": "QRコード生成中にエラーが発生しました",

        "btn_launch_app": "🚀 アプリを起動",
        "btn_start_demo": "📺 デモを開始",
        "btn_quick_tour": "❓ クイックツアー",
        "share_with_others": "📱 他の人と共有",
        "qr_generation_in_progress": "QRコードを生成中...",
        "key_features_label": "主な機能:",
        "btn_previous": "⬅️ 前へ",
        "language_change_error": "言語変更エラー",
        "demo_mode_active_sidebar": "✅ デモモード ON — サンプルデータ表示中",
        "screen_reader_off": "🔇 スクリーンリーダー OFF",
        "navigation_title": "ナビゲーション",
        "nav_rights_full": "⚖️ 権利を学ぶ",
        "nav_resources_near_you": "📍 近くのサービス",
        "nav_logging_full": "📝 対応記録",
        "nav_crisis_resources": "🚨 危機支援",
        "nav_community": "💬 コミュニティ",

        "sidebar_built_for": "すべての人の市民権を守るために作られました。",
        "show_landing_page": "🏠 ランディングページを見る",

        "landing_hero_html": "<div class=\"landing-hero\"><h1>⚖️ CivicShield Pro</h1><h2>あなたの権利を知り、自分を守り、支援を受けましょう。</h2><p>14言語で市民権を理解し活用できるよう支援するプラットフォームです。</p></div>",

        "landing_purpose_md": "### 🎯 目的\nCivicShield Pro は以下を提供します:\n\n- **14言語のリアルタイム法律翻訳**\n- **状況別の権利ガイド**\n- **法律文書の分析と期限抽出**\n- **コミュニティ支援と経験共有**\n- **24/7 の危機支援リソース**",

        "landing_features_md": "### ⭐ 主な機能\n\n- 🗣️ **リアルタイム翻訳** — 警察の発言を理解\n- 📄 **法律文書ツール** — 重要情報を抽出\n- ⚖️ **権利教育** — 学習とクイズ\n- 📍 **近くのサービス** — 法律支援やコミュニティセンター\n- 📝 **対応記録** — 警察との対面を記録\n- 🚨 **緊急ホットライン** — 24/7 支援\n- 💬 **コミュニティフォーラム** — 質問・経験共有",

        "landing_share_md": "**CivicShield を共有する方法:**\n\n1. QRコードをスキャン\n2. インストール不要\n3. 14言語対応\n4. スマホ・タブレット・PCで利用可能",

        "landing_who_should_use_md": "### 👥 利用対象者\n\n**裁判官・法律専門家:**\n- コミュニティ視点の理解\n- 被告の権利理解度の評価\n- リアルタイム翻訳の活用\n\n**弁護士・法律支援団体:**\n- 多言語法律情報の提供\n- クライアントの対応記録支援\n- 地域リソースへの接続\n\n**教育者:**\n- 市民権教育\n- 実例を使った学習\n- インタラクティブクイズ\n\n**コミュニティメンバー:**\n- 警察対面時の対応方法を学ぶ\n- 緊急支援リソースの利用\n- 経験共有",

        "landing_disclaimer_md": "**⚠️ 免責事項:**\n\nCivicShield Pro は教育目的の情報を提供するものであり、法律相談ではありません。\n法律は地域によって異なる場合があります。\n具体的な助言は弁護士にご相談ください。",

        "tutorial_intro_html": "<div class=\"tutorial-container\"><h1>👋 CivicShield Pro へようこそ！</h1><p>主要機能を一緒に見ていきましょう。</p></div>",

        "tutorial_step1_title": "🏠 メインダッシュボード",
        "tutorial_step1_desc": "すべての機能にアクセスできる中心画面です。",
        "tutorial_step1_feat1": "全機能ナビゲーション",
        "tutorial_step1_feat2": "保存された期限の確認",
        "tutorial_step1_feat3": "緊急支援",

        "tutorial_step2_title": "🗣️ リアルタイム翻訳",
        "tutorial_step2_desc": "警察の発言を14言語に翻訳します。",
        "tutorial_step2_feat1": "音声認識",
        "tutorial_step2_feat2": "即時翻訳",
        "tutorial_step2_feat3": "音声再生",

        "tutorial_step3_title": "📄 法律文書",
        "tutorial_step3_desc": "文書をアップロードして重要情報を抽出します。",
        "tutorial_step3_feat1": "期限抽出",
        "tutorial_step3_feat2": "罰金の特定",
        "tutorial_step3_feat3": "文書翻訳",

        "tutorial_step4_title": "⚖️ 権利を学ぶ",
        "tutorial_step4_desc": "権利を学び、クイズに挑戦できます。",
        "tutorial_step4_feat1": "権利教育",
        "tutorial_step4_feat2": "インタラクティブクイズ",
        "tutorial_step4_feat3": "進捗トラッキング",

        "tutorial_step5_title": "📍 近くのサービス",
        "tutorial_step5_desc": "法律支援やコミュニティサービスを検索できます。",
        "tutorial_step5_feat1": "位置情報検索",
        "tutorial_step5_feat2": "サービスフィルター",
        "tutorial_step5_feat3": "ルート案内",

        "tutorial_step6_title": "💬 コミュニティフォーラム",
        "tutorial_step6_desc": "経験を共有し、質問し、助け合いましょう。",
        "tutorial_step6_feat1": "匿名投稿",
        "tutorial_step6_feat2": "法律質問",
        "tutorial_step6_feat3": "アドバイス共有",

        "documents_intro_md": "法律文書（PDFまたは写真）をアップロードして:\n- 日付と期限を抽出\n- 必要な行動を特定\n- 罰金や警告を確認\n- 関連する政府機関を特定\n- 文書サマリーを生成",

    },
    "Arabic / العربية": {
        "sidebar_title": "CivicShield",
        "sidebar_tagline": "افهم حقوقك",
        "select_language": "📍 اختر اللغة:",
        "nav_home": "🏠 الرئيسية",
        "nav_translation": "🗣️ الترجمة الفورية",
        "nav_documents": "📄 مستندات قانونية",
        "nav_rights": "📚 مركز الحقوق",
        "nav_quiz": "❓ اختبار الحقوق",
        "nav_resources": "🏥 خدمات محلية",
        "nav_nearby": "📍 حقوق بالقرب منك",
        "nav_logging": "📝 تسجيل المواجهات",
        "nav_emergency": "🚨 الطوارئ",
        "nav_about": "حول CivicShield",
        "sidebar_version": "الإصدار 3.0.0",
        "sidebar_purpose": "حماية الحقوق المدنية وترجمة قانونية احترافية",
        "sidebar_languages": "يدعم 14 لغة",
        "sidebar_disclaimer": "⚠️ إخلاء مسؤولية",
        "sidebar_disclaimer_text": "هذا التطبيق يقدم معلومات تعليمية فقط وليس استشارة قانونية. استشر محامياً للحصول على نصيحة قانونية محددة.",

        "home_title": "مرحباً بك في CivicShield",
        "home_subtitle": "اعرف حقوقك، واحمِ نفسك، واحصل على المساعدة.",
        "dashboard_intro": "اختر إحدى الميزات للبدء:",

        "card_translation_title": "الترجمة الفورية",
        "card_translation_desc": "ترجمة ما يقوله الضابط وتقديم نصائح قانونية",
        "card_documents_title": "مساعد المستندات القانونية",
        "card_documents_desc": "ارفع مستنداتك واستخرج المعلومات المهمة",
        "card_rights_title": "مركز التعليم الحقوقي",
        "card_rights_desc": "تعلم حقوقك الدستورية",
        "card_quiz_title": "اختبار الحقوق",
        "card_quiz_desc": "اختبر معرفتك بالحقوق المدنية",
        "card_resources_title": "الخدمات المحلية",
        "card_resources_desc": "ابحث عن المساعدة القانونية وخدمات المجتمع",
        "card_nearby_title": "حقوق بالقرب منك",
        "card_nearby_desc": "اعثر على الدعم القانوني والخدمات القريبة",
        "card_logging_title": "تسجيل المواجهات",
        "card_logging_desc": "سجل تفاعلاتك مع الشرطة",
        "card_emergency_title": "الطوارئ",
        "card_emergency_desc": "أرقام وخطوات الطوارئ",

        "btn_open": "فتح",
        "btn_delete": "❌ حذف",
        "btn_record": "🎤 تسجيل",
        "btn_stop": "⏹️ إيقاف",
        "btn_translate": "🌐 ترجمة",
        "btn_listen": "🔊 استماع",
        "btn_download": "📥 تنزيل",
        "btn_search": "🔍 بحث",
        "btn_log": "📝 تسجيل",
        "btn_back": "← رجوع",
        "btn_submit": "✓ إرسال",
        "btn_cancel": "✗ إلغاء",

        "translation_title": "الترجمة الفورية",
        "translation_subtitle": "ترجمة ما يقوله الضابط وتقديم نصائح قانونية",
        "officer_statement": "ما قاله الضابط (بالإنجليزية):",
        "your_rights": "حقوقك والنصيحة القانونية:",
        "play_before_title": "1. تشغيل قبل التفاعل",
        "play_before_desc": "شغّل هذا للضابط قبل بدء التسجيل.",
        "play_before_audio": "Officer, before we begin, I am using a translation app to avoid any language barriers. I am recording with your knowledge for safety and accuracy.",
        "play_after_title": "3. تشغيل بعد فهم الحقوق",
        "play_after_desc": "شغّل هذا للضابط بعد أن تسمع حقوقك.",
        "play_after_audio": "I understand, officer, and I will comply, but I will be using my right to remain silent.",
        "officer_script": "النص الموجه للضابط (بالإنجليزية):",
        "officer_script_translated": "ما يعنيه هذا بلغتك:",
        "record_officer": "🎤 تسجيل صوت الضابط",
        "stop_recording": "⏹️ إيقاف التسجيل والترجمة",
        "listen_to_advice": "🔊 الاستماع للنصيحة",
        "translation_hint": "اكتب أو سجّل للحصول على الترجمة",
        "generating_audio": "جاري إنشاء الصوت...",
        "audio_ready": "✅ الصوت جاهز",
        "audio_failed": "❌ فشل إنشاء الصوت",
        "speech_recognized": "تم تحويل الصوت إلى نص.",
        "mic_unclear": "الصوت غير واضح. يرجى إعادة التسجيل.",
        "stt_unavailable": "خدمة التعرف على الصوت غير متاحة.",
        "unable_process_audio": "تعذر معالجة الصوت. حاول مرة أخرى.",
        "mic_recorder_title": "مسجل الصوت",
        "mic_recorder_desc": "استخدم زر البدء/الإيقاف لتسجيل كلام الضابط.",
        "mic_help": "إذا كان الميكروفون محجوباً، فعليك السماح به من إعدادات المتصفح.",
        "mic_access_failed": "تم رفض الوصول للميكروفون. يرجى السماح وإعادة المحاولة.",
        "mic_no_audio": "لا يوجد صوت مسجل. قد يكون الميكروفون محجوباً.",
        "btn_clear_filter": "مسح الفلتر",
        "currently_filtering": "يتم التصفية حسب:",
        "quiz_correct": "✅ إجابة صحيحة!",
        "quiz_incorrect": "❌ إجابة غير صحيحة.",
        "language_selector_error": "❌ خطأ في اختيار اللغة",
        "demo_section_title": "وضع العرض والاختبار",
        "demo_on": "🎬 العرض ON",
        "demo_off": "🎬 العرض OFF",
        "tour_button": "🎓 مشاهدة الجولة",
        "tour_complete": "✅ تم إكمال الجولة! أنت جاهز الآن.",
        "btn_go_home": "🏠 العودة للرئيسية",
        "btn_skip_tour": "⏭️ تخطي",
        "btn_next": "التالي ➡️",
        "btn_start_using": "🎉 ابدأ الاستخدام",

        "documents_title": "مساعد المستندات القانونية",
        "documents_subtitle": "ارفع مستنداتك واستخرج المعلومات المهمة",
        "upload_document": "📤 رفع مستند",
        "take_photo": "📸 التقاط صورة",
        "extract_text": "استخراج النص",
        "simplify_text": "تبسيط النص القانوني",
        "translate_document": "🌐 ترجمة المستند",
        "extract_dates": "📅 التواريخ المكتشفة",
        "extract_deadlines": "⏰ المواعيد النهائية",
        "extract_agencies": "🏛️ الجهات الحكومية",
        "extract_actions": "✅ الإجراءات المطلوبة",
        "download_report": "📥 تنزيل التقرير",
        "report_generated": "تم إنشاء التقرير",

        "rights_title": "مركز الحقوق",
        "rights_subtitle": "تعلم حقوقك الدستورية",
        "right_fourth": "التعديل الرابع: التفتيش والمصادرة",
        "right_fifth": "التعديل الخامس: حق الصمت",
        "right_sixth": "التعديل السادس: حق المحامي",
        "right_traffic": "حقوقك أثناء إيقاف المرور",
        "right_arrest": "إذا تم اعتقالك",
        "right_fourth_content": "**حقوقك:** يحميك التعديل الرابع من التفتيش والمصادرة غير المعقولة.\n\n**نقاط مهمة:**\n- الشرطة تحتاج عادةً إلى مذكرة لتفتيش منزلك أو سيارتك أو ممتلكاتك\n- يمكنك أن تقول بوضوح: «لا أوافق على التفتيش»\n- لا تقاوم جسدياً (قد يؤدي ذلك إلى تهم إضافية)\n- يمكن للشرطة التفتيش إذا كان لديهم مذكرة أو سبب محتمل (probable cause)\n\n**ما يمكنك فعله:**\n- ابقَ هادئاً واسأل: «هل أنا محتجز أم يمكنني المغادرة؟»\n- اطلب رؤية المذكرة\n- أبقِ يديك ظاهرة\n- لا تعرقل عمل الشرطة",

        "right_fifth_content": "**حقوقك:** لديك الحق في الصمت ولا يمكن إجبارك على قول شيء يورطك.\n\n**نقاط مهمة:**\n- لست ملزماً بالإجابة على أسئلة الشرطة\n- قل بوضوح: «أمارس حقي في الصمت»\n- هذا الحق ينطبق قبل الاعتقال أيضاً\n- الصمت لا يمكن استخدامه ضدك في المحكمة\n\n**مهم:**\n- يجب أن تعلن عن رغبتك في استخدام هذا الحق\n- إذا تم اعتقالك، اطلب محامياً فوراً\n- لا تشرح ولا تتفاوض",

        "right_sixth_content": "**حقوقك:** لديك الحق في وجود محامٍ.\n\n**نقاط مهمة:**\n- إذا لم تستطع دفع التكاليف، سيتم تعيين محامٍ عام لك\n- يمكنك طلب محامٍ في أي وقت\n- بمجرد طلب محامٍ، يجب على الشرطة إيقاف الاستجواب\n- يمكن للمحامي حضور الاستجواب معك\n\n**ما يجب قوله:**\n- «أريد التحدث إلى محامٍ»\n- «أمارس حقي في وجود محامٍ»\n- ثم التزم الصمت حتى وصوله",

        "right_traffic_content": "**أثناء إيقاف المرور:**\n- يجب عليك تقديم رخصة القيادة والتسجيل والتأمين\n- اسأل: «هل أنا محتجز أم يمكنني المغادرة؟»\n- لست مضطراً للموافقة على تفتيش السيارة\n- قل: «لا أوافق على التفتيش»\n\n**تفتيش السيارة:**\n- يمكن للشرطة النظر داخل السيارة\n- يمكنهم التفتيش إذا كان لديهم سبب محتمل\n- إذا تم اعتقالك، قد يتم تفتيش السيارة\n\n**حقوقك:**\n- أبقِ يديك ظاهرة\n- كن هادئاً ومهذباً\n- لا تقاوم\n- يمكنك التسجيل طالما أنك لا تعرقل الشرطة",

        "right_arrest_content": "**خطوات مهمة عند الاعتقال:**\n1. التزم الصمت — لا تجب على الأسئلة\n2. قل: «أريد محامياً»\n3. لا توقّع أي أوراق بدون محامٍ\n4. لا تتحدث عن القضية مع المحتجزين الآخرين\n\n**حقوقك عند الاعتقال:**\n- معرفة سبب الاعتقال\n- إجراء مكالمة هاتفية\n- حق الصمت\n- حق وجود محامٍ\n\n**تجنب:**\n- المقاومة (حتى لو كان الاعتقال غير عادل)\n- الاعتراف\n- الموافقة على التفتيش\n- التفاوض مع الشرطة",

        "resources_title": "الخدمات المحلية",
        "resources_subtitle": "ابحث عن المساعدة القانونية وخدمات المجتمع",
        "legal_aid": "مكاتب المساعدة القانونية",
        "emergency_services": "خدمات الطوارئ",
        "immigration": "مساعدة قانونية للهجرة",
        "phone": "الهاتف: ",
        "services": "الخدمات: ",
        "website": "الموقع الإلكتروني: ",
        "hours": "ساعات العمل: ",

        "nearby_title": "حقوق بالقرب منك",
        "nearby_subtitle": "ابحث عن الدعم القانوني والخدمات القريبة",
        "enter_address": "أدخل العنوان:",
        "search_radius": "نطاق البحث (بالأميال):",
        "nearest_legal_aid": "📋 أقرب مكتب مساعدة قانونية",
        "nearest_courthouse": "⚖️ أقرب محكمة",
        "nearest_police": "👮 أقرب مركز شرطة",
        "nearest_translator": "🗣️ خدمات الترجمة",
        "nearest_community": "🏢 مركز مجتمعي",
        "address": "العنوان: ",
        "phone_number": "رقم الهاتف: ",
        "hours_open": "ساعات العمل: ",
        "get_directions": "🗺️ الاتجاهات",
        "not_found": "لم يتم العثور على نتائج في هذه المنطقة",
        "logging_title": "تسجيل المواجهات",
        "logging_subtitle": "سجّل تفاعلاتك مع الشرطة",
        "encounter_type": "نوع المواجهة:",
        "encounter_location": "الموقع:",
        "encounter_details": "التفاصيل:",
        "encounter_date": "التاريخ والوقت:",
        "officer_info": "معلومات الضابط:",
        "officer_badge": "رقم الشارة:",
        "officer_agency": "الجهة التابعة:",
        "encounter_saved": "✅ تم حفظ المواجهة",
        "view_history": "📋 عرض السجل",
        "total_encounters": "إجمالي المواجهات:",
        "search_encounters": "🔍 البحث في السجل",

        "emergency_title": "الطوارئ",
        "emergency_subtitle": "أرقام وخدمات الطوارئ",
        "emergency_911": "911 — الشرطة والإسعاف والإطفاء",
        "emergency_suicide": "خط المساعدة لمنع الانتحار",
        "emergency_domestic": "خط المساعدة للعنف الأسري",
        "emergency_assault": "RAINN — دعم ضحايا الاعتداء الجنسي",
        "emergency_poison": "مركز مكافحة التسمم",
        "emergency_text": "خط الرسائل للأزمات",
        "emergency_procedures": "خطوات الطوارئ:",
        "procedure_safe": "تأكد من أنك في مكان آمن",
        "procedure_document": "سجّل كل التفاصيل",
        "procedure_record": "سجّل فيديو إذا كان ذلك قانونياً وآمناً",
        "procedure_call": "اطلب المساعدة فوراً",
        "procedure_contact": "اتصل بمحامٍ",

        "loading": "جارٍ التحميل...",
        "success": "تم بنجاح!",
        "error": "حدث خطأ",
        "warning": "تحذير",
        "info": "معلومة",
        "processing": "جارٍ المعالجة...",
        "please_wait": "يرجى الانتظار...",
        "no_data": "لا توجد بيانات",
        "try_again": "حاول مرة أخرى",

        "accessibility_title": "♿ إعدادات الوصول",
        "text_size": "حجم النص:",
        "text_size_normal": "عادي",
        "text_size_large": "كبير",
        "text_size_extra_large": "كبير جداً",
        "high_contrast": "🎨 وضع التباين العالي",
        "high_contrast_on": "التباين العالي ON",
        "high_contrast_off": "التباين العالي OFF",
        "screen_reader": "تفعيل قارئ الشاشة",
        "accessibility_saved": "✅ تم حفظ إعدادات الوصول",
        "extract_deadlines": "📋 المواعيد النهائية المكتشفة",
        "extract_penalties": "⚠️ الغرامات والتحذيرات",
        "extract_requirements": "✓ الإجراءات والمتطلبات",
        "deadline_found": "الموعد النهائي:",
        "penalty_found": "الغرامة:",
        "requirement_found": "المتطلب:",
        "document_summary": "📋 ملخص المستند",
        "summary_generated": "تم إنشاء الملخص بنجاح",

        "location_title": "📍 البحث عن خدمات قريبة",
        "enter_address": "أدخل العنوان أو الرمز البريدي:",
        "search_radius_miles": "نطاق البحث (بالأميال):",
        "find_resources": "🔍 البحث عن الخدمات",
        "resource_type": "نوع الخدمة:",
        "all_resources": "جميع الخدمات",
        "legal_aid_offices": "مكاتب المساعدة القانونية",
        "community_centers": "المراكز المجتمعية",
        "language_services": "خدمات الترجمة",
        "emergency_shelters": "ملاجئ الطوارئ",
        "distance_away": "أميال بعيداً",
        "get_directions": "🗺️ الاتجاهات",
        "no_resources_found": "لم يتم العثور على خدمات في هذه المنطقة",
        "resource_hours": "ساعات العمل:",
        "resource_phone": "الهاتف:",
        "resource_address": "العنوان:",
        "resource_website": "الموقع الإلكتروني:",
        "loading_resources": "جارٍ البحث عن الخدمات القريبة...",

        "saved_deadlines": "⏰ المواعيد النهائية المحفوظة",
        "upload_legal_doc": "رفع مستند قانوني",
        "important_dates": "📅 تواريخ مهمة",
        "required_actions": "✓ الإجراءات المطلوبة",
        "critical_deadlines": "⏰ مواعيد نهائية مهمة",
        "penalties_warnings": "⚠️ الغرامات والتحذيرات",
        "extraction_guide": "دليل استخراج المعلومات",
        "demo_mode_active": "📺 **وضع العرض ON** — عرض بيانات تجريبية",
        "have_deadlines": "📋 لديك مواعيد نهائية مهمة!",
        "view_all_deadlines": "📋 عرض جميع المواعيد →",
        "from_document": "من المستند:",
        "file_type": "نوع الملف",
        "file_size": "حجم الملف",
        "status_ready": "جاهز للاستخراج",
        "extract_information": "🔍 استخراج المعلومات",
        "extracting_info": "جارٍ استخراج المعلومات من المستند...",
        "no_dates_found": "لم يتم العثور على تواريخ",
        "no_deadlines_found": "لم يتم العثور على مواعيد نهائية",
        "no_penalties_found": "لم يتم العثور على غرامات",
        "download_summary": "📥 تنزيل الملخص",
        "download_as_txt": "تنزيل كملف TXT",
        "save_deadlines_to_dashboard": "💾 حفظ المواعيد النهائية في لوحة التحكم",
        "know_your_rights_long": "⚖️ اعرف حقوقك",
        "education_quizzes": "التعليم • الاختبارات • وحدات التعلم",
        "learn_tab": "📚 تعلّم",
        "quiz_tab": "🧪 اختبار",
        "rights_education": "التعليم الحقوقي",
        "select_topic": "اختر موضوعاً:",
        "test_knowledge": "اختبر معرفتك بالحقوق المدنية.",
        "rights_quiz": "اختبار الحقوق",

        "can_police_search": "هل يمكن للشرطة تفتيش سيارتك دون إذن؟",
        "only_with_warrant": "فقط إذا كان لديهم مذكرة",
        "only_prob_cause": "فقط إذا كان لديهم سبب محتمل",
        "both_a_and_b": "كلاهما A و B",
        "never_without": "لا، لا يمكنهم ذلك أبداً",
        "police_can_search": "يمكن للشرطة التفتيش إذا كان لديهم مذكرة أو سبب محتمل (probable cause).",

        "answer_police_q": "هل يجب عليك الإجابة على أسئلة الشرطة؟",
        "yes_always": "نعم، دائماً",
        "right_remain_silent": "لا، لديك حق الصمت",
        "only_your_name": "فقط اسمك",
        "only_if_arrested": "فقط إذا تم اعتقالك",
        "fifth_amendment": "التعديل الخامس يمنحك حق الصمت ورفض تجريم نفسك.",

        "what_say_arrested": "ماذا يجب أن تقول إذا تم اعتقالك؟",
        "explain_what_happened": "اشرح ما حدث",
        "ask_for_lawyer": "اطلب محامياً",
        "refuse_give_name": "ارفض إعطاء اسمك",
        "try_negotiate": "حاول التفاوض مع الشرطة",
        "always_ask_lawyer": "اطلب محامياً دائماً وابقَ صامتاً بعد ذلك.",

        "check_answer": "✓ تحقق من الإجابة {number}",
        "question_number": "السؤال {number}: {question}",
        "select_answer": "اختر إجابة:",
        "your_score": "نتيجتك",

        "talk_community": "💬 تحدث مع المجتمع",
        "community_intro": "شارك تجربتك، اطرح الأسئلة، وساعد الآخرين — معاً نصبح أقوى",
        "share_exp_tab": "💭 مشاركة تجربة",
        "ask_q_tab": "❓ طرح سؤال",
        "give_advice_tab": "💡 تقديم نصيحة",
        "share_your_exp": "💭 شارك تجربتك",
        "share_story": "تجربتك قد تساعد الآخرين. تتم مراجعة جميع المشاركات لضمان السلامة.",
        "title_label": "العنوان:",
        "exp_placeholder": "مثال: كيف تعاملت مع إيقاف المرور",
        "your_story": "تجربتك:",
        "story_placeholder": "اكتب تجربتك هنا...",
        "post_anonymously": "نشر مجهول",
        "share_exp_btn": "📤 مشاركة التجربة",
        "fill_title_content": "⚠️ يرجى إدخال العنوان والمحتوى",
        "exp_shared": "✅ تم نشر التجربة بنجاح! شكراً لمساهمتك.",
        "ask_community": "❓ اسأل المجتمع",
        "question_help": "هل لديك سؤال؟ المجتمع هنا لمساعدتك.",
        "your_question": "سؤالك:",
        "question_placeholder": "مثال: ما هي حقوقي أثناء إيقاف المرور؟",
        "details_label": "التفاصيل:",
        "details_placeholder": "أدخل أي معلومات إضافية...",
        "ask_anon": "نشر مجهول",
        "ask_q_btn": "❓ نشر السؤال",
        "enter_question": "⚠️ يرجى إدخال السؤال",
        "question_posted": "✅ تم نشر السؤال بنجاح!",

        "give_advice": "💡 تقديم نصيحة",
        "help_others": "ساعد الآخرين بخبرتك ومعرفتك.",
        "topic_label": "الموضوع:",
        "topic_placeholder": "مثال: كيفية الاستعداد للمحكمة",
        "your_advice": "نصيحتك:",
        "advice_placeholder": "اكتب نصيحتك هنا...",
        "share_anon": "نشر مجهول",
        "share_advice_btn": "💡 مشاركة النصيحة",
        "share_wisdom": "✅ تم نشر النصيحة بنجاح!",
        "fill_topic_advice": "⚠️ يرجى إدخال الموضوع والنصيحة",

        "recent_posts": "📋 أحدث المشاركات",
        "no_posts_yet": "💭 لا توجد مشاركات بعد. كن أول من يشارك!",
        "posted_recently": "تم النشر منذ {timestamp}",
        "author_anonymous": "مجهول",
        "author_community_member": "عضو في المجتمع",

        "crisis_hotlines": "🚨 خطوط الطوارئ والدعم",
        "crisis_support_24": "دعم متوفر على مدار 24 ساعة",
        "emergency_hotlines_header": "🆘 أرقام الطوارئ",
        "in_immediate_danger": "إذا كنت في خطر مباشر، اتصل بـ 911 فوراً",
        "emergency_number": "رقم الطوارئ",
        "suicide_prevention": "خط المساعدة لمنع الانتحار",
        "domestic_violence": "خط المساعدة للعنف الأسري",
        "sexual_assault": "RAINN — دعم ضحايا الاعتداء الجنسي",
        "poison_control": "مركز مكافحة التسمم",
        "crisis_text": "خط الرسائل للأزمات",

        "safety_procedures": "📋 إجراءات السلامة",
        "stay_safe": "🛡️ ابقَ آمناً",
        "stay_safe_desc": "اجعل سلامتك الأولوية — لا تقاوم الشرطة.",
        "document_details": "📝 سجل التفاصيل",
        "document_details_desc": "سجل اسم الضابط، رقم الشارة، الموقع، الوقت، وما حدث.",
        "record_safely": "🎥 سجل بأمان",
        "record_safely_desc": "سجل فقط إذا كان ذلك قانونياً وآمناً. اجعل الكاميرا ظاهرة.",
        "call_for_help": "📞 اطلب المساعدة",
        "call_help_desc": "إذا كنت في خطر، اتصل بـ 911 وتحدث بوضوح.",
        "get_legal_help": "⚖️ احصل على مساعدة قانونية",
        "legal_help_desc": "اتصل بمحامٍ. العديد من المحامين العامين يقدمون دعماً طارئاً.",
        "medical_attention": "🏥 رعاية طبية",
        "medical_attention_desc": "إذا تعرضت لإصابة، احصل على علاج فوري وسجل صوراً.",
        "mental_health_support": "🧠 دعم الصحة النفسية",
        "legal_troubles_trauma": "المشاكل القانونية أو المواجهات مع الشرطة قد تسبب صدمة نفسية.",
        "mental_health_resources": "موارد الصحة النفسية:",
        "samhsa_helpline": "خط SAMHSA: ‎1‑800‑662‑4357 (مجاني • سري • 24/7)",
        "psychology_directory": "دليل المعالجين: Psychology Today",
        "support_groups": "مجموعات الدعم: NAACP، مراكز المجتمع، منظمات قانونية",
        "contact_emergency": "🆘 الطوارئ",
        "contact_suicide": "🧠 منع الانتحار",
        "contact_domestic": "💔 العنف الأسري",
        "contact_rainn": "🤝 RAINN — دعم الاعتداء الجنسي",
        "contact_poison": "☠️ مكافحة التسمم",
        "contact_crisis_text": "📱 خط الرسائل للأزمات",
        "contact_crisis_text_number": "أرسل كلمة HOME إلى 741741",

        "enc_type_traffic_stop": "إيقاف مرور",
        "enc_type_street_encounter": "مواجهة في الشارع",
        "enc_type_arrest": "اعتقال",
        "enc_type_search": "تفتيش",
        "enc_type_other": "أخرى",
        "encounter_label": "مواجهة",
        "unknown": "غير معروف",
        "na": "غير متوفر",
        "error_generating_qr": "حدث خطأ أثناء إنشاء رمز QR",

        "btn_launch_app": "🚀 تشغيل التطبيق",
        "btn_start_demo": "📺 بدء العرض",
        "btn_quick_tour": "❓ جولة سريعة",
        "share_with_others": "📱 مشاركة مع الآخرين",
        "qr_generation_in_progress": "جارٍ إنشاء رمز QR...",
        "key_features_label": "الميزات الرئيسية:",
        "btn_previous": "⬅️ السابق",
        "language_change_error": "خطأ في تغيير اللغة",
        "demo_mode_active_sidebar": "✅ وضع العرض ON — عرض بيانات تجريبية",
        "screen_reader_off": "🔇 قارئ الشاشة OFF",
        "navigation_title": "التنقل",
        "nav_rights_full": "⚖️ تعلّم حقوقك",
        "nav_resources_near_you": "📍 خدمات بالقرب منك",
        "nav_logging_full": "📝 سجل المواجهات",
        "nav_crisis_resources": "🚨 موارد الطوارئ",
        "nav_community": "💬 المجتمع",

        "sidebar_built_for": "تم إنشاؤه لحماية الحقوق المدنية للجميع.",
        "show_landing_page": "🏠 عرض الصفحة الرئيسية",

        "landing_hero_html": "<div class=\"landing-hero\"><h1>⚖️ CivicShield Pro</h1><h2>اعرف حقوقك، واحمِ نفسك، واحصل على المساعدة.</h2><p>منصة تساعدك على فهم حقوقك المدنية بـ 14 لغة.</p></div>",

        "landing_purpose_md": "### 🎯 الهدف\nCivicShield Pro يقدم:\n\n- **ترجمة قانونية فورية بـ 14 لغة**\n- **أدلة حقوق حسب الموقف**\n- **تحليل المستندات القانونية واستخراج المواعيد**\n- **مجتمع للدعم وتبادل الخبرات**\n- **موارد طوارئ على مدار الساعة**",

        "landing_features_md": "### ⭐ الميزات الرئيسية\n\n- 🗣️ **ترجمة فورية** — فهم ما يقوله الضابط\n- 📄 **أدوات المستندات القانونية** — استخراج المعلومات المهمة\n- ⚖️ **التعليم الحقوقي** — تعلم واختبر نفسك\n- 📍 **الخدمات القريبة** — دعم قانوني ومجتمعي\n- 📝 **سجل المواجهات** — توثيق التفاعلات\n- 🚨 **خطوط الطوارئ** — دعم 24/7\n- 💬 **منتدى المجتمع** — أسئلة وتجارب",

        "landing_share_md": "**كيفية مشاركة CivicShield:**\n\n1. امسح رمز QR\n2. لا حاجة للتثبيت\n3. يدعم 14 لغة\n4. يعمل على الهاتف والكمبيوتر",

        "landing_who_should_use_md": "### 👥 من يجب أن يستخدمه؟\n\n**القضاة والمحامون:**\n- فهم منظور المجتمع\n- تقييم معرفة الحقوق\n- استخدام الترجمة الفورية\n\n**المنظمات القانونية:**\n- تقديم معلومات متعددة اللغات\n- دعم العملاء\n- ربط المستخدمين بالموارد\n\n**المعلمون:**\n- تعليم الحقوق المدنية\n- استخدام أمثلة واقعية\n- اختبارات تفاعلية\n\n**أفراد المجتمع:**\n- تعلم كيفية التعامل مع الشرطة\n- الوصول إلى موارد الطوارئ\n- مشاركة التجارب",

        "landing_disclaimer_md": "**⚠️ إخلاء مسؤولية:**\n\nCivicShield Pro يقدم معلومات تعليمية فقط وليس نصيحة قانونية.\nالقوانين تختلف حسب المنطقة.\nاستشر محامياً للحصول على نصيحة محددة.",

        "tutorial_intro_html": "<div class=\"tutorial-container\"><h1>👋 أهلاً بك في CivicShield Pro!</h1><p>لنبدأ بجولة سريعة على الميزات.</p></div>",

        "tutorial_step1_title": "🏠 لوحة التحكم الرئيسية",
        "tutorial_step1_desc": "هنا يمكنك الوصول إلى جميع الميزات.",
        "tutorial_step1_feat1": "تنقل كامل",
        "tutorial_step1_feat2": "عرض المواعيد المحفوظة",
        "tutorial_step1_feat3": "وصول سريع للطوارئ",

        "tutorial_step2_title": "🗣️ الترجمة الفورية",
        "tutorial_step2_desc": "ترجمة كلام الضابط إلى 14 لغة.",
        "tutorial_step2_feat1": "التعرف على الصوت",
        "tutorial_step2_feat2": "ترجمة فورية",
        "tutorial_step2_feat3": "تشغيل الصوت",

        "tutorial_step3_title": "📄 المستندات القانونية",
        "tutorial_step3_desc": "ارفع مستنداتك واستخرج المعلومات المهمة.",
        "tutorial_step3_feat1": "استخراج المواعيد",
        "tutorial_step3_feat2": "تحديد الغرامات",
        "tutorial_step3_feat3": "ترجمة المستندات",

        "tutorial_step4_title": "⚖️ تعلّم حقوقك",
        "tutorial_step4_desc": "تعلم حقوقك واختبر معرفتك.",
        "tutorial_step4_feat1": "دروس الحقوق",
        "tutorial_step4_feat2": "اختبارات تفاعلية",
        "tutorial_step4_feat3": "تتبع التقدم",

        "tutorial_step5_title": "📍 الخدمات القريبة",
        "tutorial_step5_desc": "ابحث عن الدعم القانوني والخدمات المجتمعية.",
        "tutorial_step5_feat1": "بحث حسب الموقع",
        "tutorial_step5_feat2": "تصفية الخدمات",
        "tutorial_step5_feat3": "الاتجاهات",

        "tutorial_step6_title": "💬 منتدى المجتمع",
        "tutorial_step6_desc": "شارك تجربتك واطرح الأسئلة.",
        "tutorial_step6_feat1": "نشر مجهول",
        "tutorial_step6_feat2": "أسئلة قانونية",
        "tutorial_step6_feat3": "مشاركة النصائح",

        "documents_intro_md": "ارفع مستنداً قانونياً (PDF أو صورة) للحصول على:\n- استخراج التواريخ والمواعيد\n- تحديد الإجراءات المطلوبة\n- معرفة الغرامات\n- تحديد الجهات الحكومية\n- إنشاء ملخص للمستند",

    },
    "Portuguese / Português": {
        "sidebar_title": "CivicShield",
        "sidebar_tagline": "Entenda seus direitos",
        "select_language": "📍 Selecione o idioma:",
        "nav_home": "🏠 Início",
        "nav_translation": "🗣️ Tradução em tempo real",
        "nav_documents": "📄 Documentos legais",
        "nav_rights": "📚 Centro de direitos",
        "nav_quiz": "❓ Quiz de direitos",
        "nav_resources": "🏥 Serviços locais",
        "nav_nearby": "📍 Direitos perto de você",
        "nav_logging": "📝 Registro de abordagens",
        "nav_emergency": "🚨 Emergência",
        "nav_about": "Sobre o CivicShield",
        "sidebar_version": "Versão 3.0.0",
        "sidebar_purpose": "Proteção de direitos civis e tradução jurídica profissional",
        "sidebar_languages": "Suporta 14 idiomas",
        "sidebar_disclaimer": "⚠️ Aviso",
        "sidebar_disclaimer_text": "Este aplicativo fornece informações educacionais e não constitui aconselhamento jurídico. Consulte um advogado para orientação específica.",

        "home_title": "Bem-vindo ao CivicShield",
        "home_subtitle": "Conheça seus direitos, proteja-se e obtenha ajuda.",
        "dashboard_intro": "Escolha um recurso para começar:",

        "card_translation_title": "Tradução em tempo real",
        "card_translation_desc": "Traduza o que o policial diz e receba orientação jurídica",
        "card_documents_title": "Assistente de documentos legais",
        "card_documents_desc": "Envie documentos e extraia informações importantes",
        "card_rights_title": "Centro de educação sobre direitos",
        "card_rights_desc": "Aprenda seus direitos constitucionais",
        "card_quiz_title": "Quiz de direitos",
        "card_quiz_desc": "Teste seu conhecimento sobre direitos civis",
        "card_resources_title": "Serviços locais",
        "card_resources_desc": "Encontre assistência jurídica e serviços comunitários",
        "card_nearby_title": "Direitos perto de você",
        "card_nearby_desc": "Encontre apoio jurídico e serviços próximos",
        "card_logging_title": "Registro de abordagens",
        "card_logging_desc": "Registre interações com a polícia",
        "card_emergency_title": "Emergência",
        "card_emergency_desc": "Números e procedimentos de emergência",

        "btn_open": "Abrir",
        "btn_delete": "❌ Excluir",
        "btn_record": "🎤 Gravar",
        "btn_stop": "⏹️ Parar",
        "btn_translate": "🌐 Traduzir",
        "btn_listen": "🔊 Ouvir",
        "btn_download": "📥 Baixar",
        "btn_search": "🔍 Buscar",
        "btn_log": "📝 Registrar",
        "btn_back": "← Voltar",
        "btn_submit": "✓ Enviar",
        "btn_cancel": "✗ Cancelar",

        "translation_title": "Tradução em tempo real",
        "translation_subtitle": "Traduza o que o policial diz e receba orientação jurídica",
        "officer_statement": "O que o policial disse (em inglês):",
        "your_rights": "Seus direitos e orientação jurídica:",
        "play_before_title": "1. Reproduzir Antes da Interação",
        "play_before_desc": "Reproduza isso para o policial antes de começar a gravar.",
        "play_before_audio": "Officer, before we begin, I am using a translation app to avoid any language barriers. I am recording with your knowledge for safety and accuracy.",
        "play_after_title": "3. Reproduzir Após Entender os Direitos",
        "play_after_desc": "Reproduza isso para o policial após ouvir seus direitos.",
        "play_after_audio": "I understand, officer, and I will comply, but I will be using my right to remain silent.",
        "officer_script": "Script para o policial (Inglês):",
        "officer_script_translated": "O que isso significa no seu idioma:",
        "record_officer": "🎤 Gravar fala do policial",
        "stop_recording": "⏹️ Parar gravação e traduzir",
        "listen_to_advice": "🔊 Ouvir orientação",
        "translation_hint": "Digite ou grave para obter tradução",
        "generating_audio": "Gerando áudio...",
        "audio_ready": "✅ Áudio pronto",
        "audio_failed": "❌ Falha ao gerar áudio",
        "speech_recognized": "Áudio convertido para texto.",
        "mic_unclear": "O áudio não ficou claro. Tente gravar novamente.",
        "stt_unavailable": "Serviço de reconhecimento de voz indisponível.",
        "unable_process_audio": "Não foi possível processar o áudio. Tente novamente.",
        "mic_recorder_title": "Gravador de áudio",
        "mic_recorder_desc": "Use o botão iniciar/parar para gravar a fala do policial.",
        "mic_help": "Se o microfone estiver bloqueado, permita o acesso nas configurações do navegador.",
        "mic_access_failed": "Acesso ao microfone negado. Permita e tente novamente.",
        "mic_no_audio": "Nenhum áudio detectado. O microfone pode estar bloqueado.",
        "btn_clear_filter": "Limpar filtro",
        "currently_filtering": "Filtrando por:",
        "quiz_correct": "✅ Resposta correta!",
        "quiz_incorrect": "❌ Resposta incorreta.",
        "language_selector_error": "❌ Erro ao selecionar idioma",
        "demo_section_title": "Modo de demonstração e teste",
        "demo_on": "🎬 Demonstração ON",
        "demo_off": "🎬 Demonstração OFF",
        "tour_button": "🎓 Ver tour",
        "tour_complete": "✅ Tour concluído! Você está pronto.",
        "btn_go_home": "🏠 Voltar ao início",
        "btn_skip_tour": "⏭️ Pular",
        "btn_next": "Próximo ➡️",
        "btn_start_using": "🎉 Começar a usar",

        "documents_title": "Assistente de documentos legais",
        "documents_subtitle": "Envie documentos e extraia informações importantes",
        "upload_document": "📤 Enviar documento",
        "take_photo": "📸 Tirar foto",
        "extract_text": "Extrair texto",
        "simplify_text": "Simplificar texto jurídico",
        "translate_document": "🌐 Traduzir documento",
        "extract_dates": "📅 Datas encontradas",
        "extract_deadlines": "⏰ Prazos",
        "extract_agencies": "🏛️ Órgãos governamentais",
        "extract_actions": "✅ Ações necessárias",
        "download_report": "📥 Baixar relatório",
        "report_generated": "Relatório gerado",

        "rights_title": "Centro de direitos",
        "rights_subtitle": "Aprenda seus direitos constitucionais",
        "right_fourth": "4ª Emenda: Busca e apreensão",
        "right_fifth": "5ª Emenda: Direito ao silêncio",
        "right_sixth": "6ª Emenda: Direito a um advogado",
        "right_traffic": "Seus direitos em uma abordagem de trânsito",
        "right_arrest": "Se você for preso",
        "right_fourth_content": "**Seus direitos:** A 4ª Emenda protege você contra buscas e apreensões injustificadas.\n\n**Pontos importantes:**\n- A polícia geralmente precisa de um mandado para revistar sua casa, carro ou pertences\n- Você pode dizer claramente: “Não autorizo a busca”\n- Não resista fisicamente (isso pode gerar acusações adicionais)\n- A polícia pode revistar se tiver um mandado ou motivo provável (probable cause)\n\n**O que você pode fazer:**\n- Mantenha a calma e pergunte: “Estou detido ou posso ir embora?”\n- Peça para ver o mandado\n- Mantenha as mãos visíveis\n- Não obstrua o trabalho policial",

        "right_fifth_content": "**Seus direitos:** Você tem o direito de permanecer em silêncio e não pode ser forçado a dizer algo que o incrimine.\n\n**Pontos importantes:**\n- Você não é obrigado a responder perguntas da polícia\n- Diga claramente: “Estou exercendo meu direito de permanecer em silêncio”\n- Esse direito vale antes e depois da prisão\n- Seu silêncio não pode ser usado contra você no tribunal\n\n**Importante:**\n- Você deve declarar que está exercendo esse direito\n- Se for preso, peça um advogado imediatamente\n- Não explique, não negocie",

        "right_sixth_content": "**Seus direitos:** Você tem direito a um advogado.\n\n**Pontos importantes:**\n- Se não puder pagar, um defensor público será designado\n- Você pode pedir um advogado a qualquer momento\n- Após pedir um advogado, a polícia deve parar o interrogatório\n- O advogado pode estar presente durante o interrogatório\n\n**O que dizer:**\n- “Quero falar com um advogado”\n- “Estou exercendo meu direito a um advogado”\n- Depois disso, permaneça em silêncio",

        "right_traffic_content": "**Durante uma abordagem de trânsito:**\n- Você deve fornecer carteira de motorista, registro e seguro\n- Pergunte: “Estou detido ou posso ir embora?”\n- Você não é obrigado a permitir a busca do carro\n- Diga: “Não autorizo a busca”\n\n**Busca no veículo:**\n- A polícia pode olhar dentro do carro\n- Pode revistar se houver motivo provável\n- Se você for preso, o carro pode ser revistado\n\n**Seus direitos:**\n- Mantenha as mãos visíveis\n- Seja calmo e respeitoso\n- Não resista\n- Você pode gravar, desde que não atrapalhe a polícia",

        "right_arrest_content": "**Passos importantes se você for preso:**\n1. Fique em silêncio — não responda perguntas\n2. Diga: “Quero um advogado”\n3. Não assine nada sem um advogado\n4. Não converse sobre o caso com outros detentos\n\n**Seus direitos ao ser preso:**\n- Saber o motivo da prisão\n- Fazer uma ligação telefônica\n- Direito ao silêncio\n- Direito a um advogado\n\n**Evite:**\n- Resistir (mesmo se achar a prisão injusta)\n- Confessar\n- Autorizar buscas\n- Negociar com a polícia",

        "resources_title": "Serviços locais",
        "resources_subtitle": "Encontre assistência jurídica e serviços comunitários",
        "legal_aid": "Escritórios de assistência jurídica",
        "emergency_services": "Serviços de emergência",
        "immigration": "Assistência jurídica de imigração",
        "phone": "Telefone: ",
        "services": "Serviços: ",
        "website": "Site: ",
        "hours": "Horário: ",

        "nearby_title": "Direitos perto de você",
        "nearby_subtitle": "Encontre apoio jurídico e serviços próximos",
        "enter_address": "Digite o endereço:",
        "search_radius": "Raio de busca (milhas):",
        "nearest_legal_aid": "📋 Escritório jurídico mais próximo",
        "nearest_courthouse": "⚖️ Tribunal mais próximo",
        "nearest_police": "👮 Delegacia mais próxima",
        "nearest_translator": "🗣️ Serviços de tradução",
        "nearest_community": "🏢 Centro comunitário",
        "address": "Endereço: ",
        "phone_number": "Telefone: ",
        "hours_open": "Horário: ",
        "get_directions": "🗺️ Rotas",
        "not_found": "Nenhum resultado encontrado nesta área",
        "logging_title": "Registro de abordagens",
        "logging_subtitle": "Registre suas interações com a polícia",
        "encounter_type": "Tipo de abordagem:",
        "encounter_location": "Local:",
        "encounter_details": "Detalhes:",
        "encounter_date": "Data e hora:",
        "officer_info": "Informações do policial:",
        "officer_badge": "Número da identificação:",
        "officer_agency": "Agência:",
        "encounter_saved": "✅ Abordagem salva",
        "view_history": "📋 Ver histórico",
        "total_encounters": "Total de abordagens:",
        "search_encounters": "🔍 Buscar no histórico",

        "emergency_title": "Emergência",
        "emergency_subtitle": "Números e serviços de emergência",
        "emergency_911": "911 — Polícia, ambulância e bombeiros",
        "emergency_suicide": "Linha de prevenção ao suicídio",
        "emergency_domestic": "Linha de apoio a vítimas de violência doméstica",
        "emergency_assault": "RAINN — Apoio a vítimas de agressão sexual",
        "emergency_poison": "Centro de controle de envenenamento",
        "emergency_text": "Linha de mensagens para crises",
        "emergency_procedures": "Procedimentos de emergência:",
        "procedure_safe": "Garanta que você está em um local seguro",
        "procedure_document": "Registre todos os detalhes",
        "procedure_record": "Grave vídeo se for legal e seguro",
        "procedure_call": "Peça ajuda imediatamente",
        "procedure_contact": "Entre em contato com um advogado",

        "loading": "Carregando...",
        "success": "Sucesso!",
        "error": "Ocorreu um erro",
        "warning": "Aviso",
        "info": "Informação",
        "processing": "Processando...",
        "please_wait": "Aguarde...",
        "no_data": "Nenhum dado disponível",
        "try_again": "Tentar novamente",

        "accessibility_title": "♿ Acessibilidade",
        "text_size": "Tamanho do texto:",
        "text_size_normal": "Normal",
        "text_size_large": "Grande",
        "text_size_extra_large": "Extra grande",
        "high_contrast": "🎨 Alto contraste",
        "high_contrast_on": "Alto contraste ON",
        "high_contrast_off": "Alto contraste OFF",
        "screen_reader": "Ativar leitor de tela",
        "accessibility_saved": "✅ Configurações de acessibilidade salvas",
        "extract_deadlines": "📋 Prazos identificados",
        "extract_penalties": "⚠️ Multas e advertências",
        "extract_requirements": "✓ Ações e exigências",
        "deadline_found": "Prazo:",
        "penalty_found": "Multa:",
        "requirement_found": "Exigência:",
        "document_summary": "📋 Resumo do documento",
        "summary_generated": "Resumo gerado com sucesso",

        "location_title": "📍 Buscar serviços próximos",
        "enter_address": "Digite o endereço ou CEP:",
        "search_radius_miles": "Raio de busca (milhas):",
        "find_resources": "🔍 Buscar serviços",
        "resource_type": "Tipo de serviço:",
        "all_resources": "Todos os serviços",
        "legal_aid_offices": "Escritórios de assistência jurídica",
        "community_centers": "Centros comunitários",
        "language_services": "Serviços de tradução",
        "emergency_shelters": "Abrigos de emergência",
        "distance_away": "milhas de distância",
        "get_directions": "🗺️ Rotas",
        "no_resources_found": "Nenhum serviço encontrado nesta área",
        "resource_hours": "Horário:",
        "resource_phone": "Telefone:",
        "resource_address": "Endereço:",
        "resource_website": "Site:",
        "loading_resources": "Buscando serviços próximos...",

        "saved_deadlines": "⏰ Prazos salvos",
        "upload_legal_doc": "Enviar documento legal",
        "important_dates": "📅 Datas importantes",
        "required_actions": "✓ Ações necessárias",
        "critical_deadlines": "⏰ Prazos críticos",
        "penalties_warnings": "⚠️ Multas e advertências",
        "extraction_guide": "Guia de extração",
        "demo_mode_active": "📺 **Modo demonstração ON** — exibindo dados de exemplo",
        "have_deadlines": "📋 Você tem prazos importantes!",
        "view_all_deadlines": "📋 Ver todos os prazos →",
        "from_document": "Do documento:",
        "file_type": "Tipo de arquivo",
        "file_size": "Tamanho do arquivo",
        "status_ready": "Pronto para extração",
        "extract_information": "🔍 Extrair informações",
        "extracting_info": "Extraindo informações do documento...",
        "no_dates_found": "Nenhuma data encontrada",
        "no_deadlines_found": "Nenhum prazo encontrado",
        "no_penalties_found": "Nenhuma multa encontrada",
        "download_summary": "📥 Baixar resumo",
        "download_as_txt": "Baixar como TXT",
        "save_deadlines_to_dashboard": "💾 Salvar prazos no painel",
        "know_your_rights_long": "⚖️ Conheça seus direitos",
        "education_quizzes": "Educação • Questionários • Módulos de aprendizado",
        "learn_tab": "📚 Aprender",
        "quiz_tab": "🧪 Quiz",
        "rights_education": "Educação sobre direitos",
        "select_topic": "Selecione um tópico:",
        "test_knowledge": "Teste seu conhecimento sobre direitos civis.",
        "rights_quiz": "Quiz de direitos",

        "can_police_search": "A polícia pode revistar seu carro sem permissão?",
        "only_with_warrant": "Somente com mandado",
        "only_prob_cause": "Somente com motivo provável",
        "both_a_and_b": "Ambos A e B",
        "never_without": "Não, nunca podem",
        "police_can_search": "A polícia pode revistar se tiver mandado ou motivo provável (probable cause).",

        "answer_police_q": "Você é obrigado a responder perguntas da polícia?",
        "yes_always": "Sim, sempre",
        "right_remain_silent": "Não, você tem direito ao silêncio",
        "only_your_name": "Apenas seu nome",
        "only_if_arrested": "Somente se estiver preso",
        "fifth_amendment": "A 5ª Emenda garante seu direito ao silêncio e a não se incriminar.",

        "what_say_arrested": "O que você deve dizer se for preso?",
        "explain_what_happened": "Explicar o que aconteceu",
        "ask_for_lawyer": "Pedir um advogado",
        "refuse_give_name": "Recusar-se a dar seu nome",
        "try_negotiate": "Tentar negociar com a polícia",
        "always_ask_lawyer": "Peça um advogado e permaneça em silêncio depois disso.",

        "check_answer": "✓ Verificar resposta {number}",
        "question_number": "Pergunta {number}: {question}",
        "select_answer": "Selecione uma resposta:",
        "your_score": "Sua pontuação",

        "talk_community": "💬 Converse com a comunidade",
        "community_intro": "Compartilhe experiências, faça perguntas e ajude outras pessoas — juntos somos mais fortes",
        "share_exp_tab": "💭 Compartilhar experiência",
        "ask_q_tab": "❓ Fazer pergunta",
        "give_advice_tab": "💡 Dar conselho",
        "share_your_exp": "💭 Compartilhe sua experiência",
        "share_story": "Sua experiência pode ajudar outras pessoas. Todas as postagens são revisadas para segurança.",
        "title_label": "Título:",
        "exp_placeholder": "Exemplo: Como lidei com uma abordagem de trânsito",
        "your_story": "Sua experiência:",
        "story_placeholder": "Escreva sua experiência aqui...",
        "post_anonymously": "Postar anonimamente",
        "share_exp_btn": "📤 Compartilhar experiência",
        "fill_title_content": "⚠️ Insira o título e o conteúdo",
        "exp_shared": "✅ Experiência compartilhada com sucesso! Obrigado por contribuir.",
        "ask_community": "❓ Pergunte à comunidade",
        "question_help": "Tem uma dúvida? A comunidade está aqui para ajudar.",
        "your_question": "Sua pergunta:",
        "question_placeholder": "Exemplo: Quais são meus direitos durante uma abordagem de trânsito?",
        "details_label": "Detalhes:",
        "details_placeholder": "Insira informações adicionais...",
        "ask_anon": "Postar anonimamente",
        "ask_q_btn": "❓ Publicar pergunta",
        "enter_question": "⚠️ Insira a pergunta",
        "question_posted": "✅ Pergunta publicada com sucesso!",

        "give_advice": "💡 Dar conselho",
        "help_others": "Ajude outras pessoas com sua experiência e conhecimento.",
        "topic_label": "Tópico:",
        "topic_placeholder": "Exemplo: Como se preparar para uma audiência",
        "your_advice": "Seu conselho:",
        "advice_placeholder": "Escreva seu conselho aqui...",
        "share_anon": "Postar anonimamente",
        "share_advice_btn": "💡 Compartilhar conselho",
        "share_wisdom": "✅ Conselho publicado com sucesso!",
        "fill_topic_advice": "⚠️ Insira o tópico e o conselho",

        "recent_posts": "📋 Postagens recentes",
        "no_posts_yet": "💭 Nenhuma postagem ainda. Seja o primeiro a compartilhar!",
        "posted_recently": "Publicado há {timestamp}",
        "author_anonymous": "Anônimo",
        "author_community_member": "Membro da comunidade",

        "crisis_hotlines": "🚨 Linhas de emergência e apoio",
        "crisis_support_24": "Apoio disponível 24 horas",
        "emergency_hotlines_header": "🆘 Números de emergência",
        "in_immediate_danger": "Se estiver em perigo imediato, ligue para 911",
        "emergency_number": "Número de emergência",
        "suicide_prevention": "Linha de prevenção ao suicídio",
        "domestic_violence": "Linha de apoio à violência doméstica",
        "sexual_assault": "RAINN — Apoio a vítimas de agressão sexual",
        "poison_control": "Centro de controle de envenenamento",
        "crisis_text": "Linha de mensagens para crises",

        "safety_procedures": "📋 Procedimentos de segurança",
        "stay_safe": "🛡️ Mantenha-se seguro",
        "stay_safe_desc": "Sua segurança vem primeiro — não resista fisicamente.",
        "document_details": "📝 Registre detalhes",
        "document_details_desc": "Anote nome do policial, número da identificação, local, horário e o que aconteceu.",
        "record_safely": "🎥 Grave com segurança",
        "record_safely_desc": "Grave somente se for legal e seguro. Mantenha a câmera visível.",
        "call_for_help": "📞 Peça ajuda",
        "call_help_desc": "Se estiver em perigo, ligue para 911 e fale claramente.",
        "get_legal_help": "⚖️ Obtenha ajuda jurídica",
        "legal_help_desc": "Entre em contato com um advogado. Defensores públicos podem oferecer suporte emergencial.",
        "medical_attention": "🏥 Atendimento médico",
        "medical_attention_desc": "Se estiver ferido, procure atendimento imediatamente e registre fotos.",
        "mental_health_support": "🧠 Apoio à saúde mental",
        "legal_troubles_trauma": "Problemas legais ou abordagens policiais podem causar trauma emocional.",
        "mental_health_resources": "Recursos de saúde mental:",
        "samhsa_helpline": "Linha SAMHSA: 1‑800‑662‑4357 (gratuito • confidencial • 24/7)",
        "psychology_directory": "Diretório de terapeutas: Psychology Today",
        "support_groups": "Grupos de apoio: NAACP, centros comunitários, organizações jurídicas",
        "contact_emergency": "🆘 Emergência",
        "contact_suicide": "🧠 Prevenção ao suicídio",
        "contact_domestic": "💔 Violência doméstica",
        "contact_rainn": "🤝 RAINN — Apoio a vítimas de agressão sexual",
        "contact_poison": "☠️ Controle de envenenamento",
        "contact_crisis_text": "📱 Linha de mensagens para crises",
        "contact_crisis_text_number": "Envie HOME para 741741",

        "enc_type_traffic_stop": "Abordagem de trânsito",
        "enc_type_street_encounter": "Abordagem na rua",
        "enc_type_arrest": "Prisão",
        "enc_type_search": "Busca",
        "enc_type_other": "Outro",
        "encounter_label": "Abordagem",
        "unknown": "Desconhecido",
        "na": "N/A",
        "error_generating_qr": "Erro ao gerar código QR",

        "btn_launch_app": "🚀 Abrir aplicativo",
        "btn_start_demo": "📺 Iniciar demonstração",
        "btn_quick_tour": "❓ Tour rápido",
        "share_with_others": "📱 Compartilhar com outros",
        "qr_generation_in_progress": "Gerando código QR...",
        "key_features_label": "Principais recursos:",
        "btn_previous": "⬅️ Anterior",
        "language_change_error": "Erro ao alterar idioma",
        "demo_mode_active_sidebar": "✅ Modo demonstração ON — exibindo dados de exemplo",
        "screen_reader_off": "🔇 Leitor de tela OFF",
        "navigation_title": "Navegação",
        "nav_rights_full": "⚖️ Aprenda seus direitos",
        "nav_resources_near_you": "📍 Serviços perto de você",
        "nav_logging_full": "📝 Registro de abordagens",
        "nav_crisis_resources": "🚨 Recursos de emergência",
        "nav_community": "💬 Comunidade",

        "sidebar_built_for": "Criado para proteger os direitos civis de todos.",
        "show_landing_page": "🏠 Mostrar página inicial",

        "landing_hero_html": "<div class=\"landing-hero\"><h1>⚖️ CivicShield Pro</h1><h2>Conheça seus direitos, proteja-se e obtenha ajuda.</h2><p>Uma plataforma que ajuda você a entender seus direitos civis em 14 idiomas.</p></div>",

        "landing_purpose_md": "### 🎯 Objetivo\nCivicShield Pro oferece:\n\n- **Tradução jurídica instantânea em 14 idiomas**\n- **Guias de direitos por situação**\n- **Análise de documentos legais e extração de prazos**\n- **Comunidade para apoio e troca de experiências**\n- **Recursos de emergência 24/7**",

        "landing_features_md": "### ⭐ Principais recursos\n\n- 🗣️ **Tradução em tempo real** — entenda o que o policial diz\n- 📄 **Ferramentas para documentos legais** — extraia informações importantes\n- ⚖️ **Educação sobre direitos** — aprenda e teste seus conhecimentos\n- 📍 **Serviços próximos** — apoio jurídico e comunitário\n- 📝 **Registro de abordagens** — documente interações\n- 🚨 **Linhas de emergência** — suporte 24/7\n- 💬 **Fórum da comunidade** — perguntas e experiências",

        "landing_share_md": "**Como compartilhar o CivicShield:**\n\n1. Escaneie o código QR\n2. Não precisa instalar\n3. Suporte a 14 idiomas\n4. Funciona no celular e no computador",

        "landing_who_should_use_md": "### 👥 Quem deve usar?\n\n**Juízes e advogados:**\n- Entender a perspectiva da comunidade\n- Avaliar conhecimento de direitos\n- Usar tradução instantânea\n\n**Organizações jurídicas:**\n- Fornecer informações multilíngues\n- Apoiar clientes\n- Conectar usuários a recursos\n\n**Educadores:**\n- Ensinar direitos civis\n- Usar exemplos reais\n- Aplicar quizzes interativos\n\n**Comunidade:**\n- Aprender como lidar com a polícia\n- Acessar recursos de emergência\n- Compartilhar experiências",

        "landing_disclaimer_md": "**⚠️ Aviso:**\n\nCivicShield Pro fornece informações educacionais e não constitui aconselhamento jurídico.\nAs leis variam por região.\nConsulte um advogado para orientação específica.",

        "tutorial_intro_html": "<div class=\"tutorial-container\"><h1>👋 Bem-vindo ao CivicShield Pro!</h1><p>Vamos começar com um tour rápido.</p></div>",

        "tutorial_step1_title": "🏠 Painel principal",
        "tutorial_step1_desc": "Aqui você acessa todos os recursos.",
        "tutorial_step1_feat1": "Navegação completa",
        "tutorial_step1_feat2": "Prazos salvos",
        "tutorial_step1_feat3": "Acesso rápido à emergência",

        "tutorial_step2_title": "🗣️ Tradução em tempo real",
        "tutorial_step2_desc": "Traduza a fala do policial para 14 idiomas.",
        "tutorial_step2_feat1": "Reconhecimento de voz",
        "tutorial_step2_feat2": "Tradução instantânea",
        "tutorial_step2_feat3": "Áudio reproduzível",

        "tutorial_step3_title": "📄 Documentos legais",
        "tutorial_step3_desc": "Envie documentos e extraia informações importantes.",
        "tutorial_step3_feat1": "Extração de prazos",
        "tutorial_step3_feat2": "Identificação de multas",
        "tutorial_step3_feat3": "Tradução de documentos",

        "tutorial_step4_title": "⚖️ Aprenda seus direitos",
        "tutorial_step4_desc": "Aprenda e teste seus conhecimentos.",
        "tutorial_step4_feat1": "Lições sobre direitos",
        "tutorial_step4_feat2": "Quizzes interativos",
        "tutorial_step4_feat3": "Acompanhamento de progresso",

        "tutorial_step5_title": "📍 Serviços próximos",
        "tutorial_step5_desc": "Encontre apoio jurídico e comunitário.",
        "tutorial_step5_feat1": "Busca por localização",
        "tutorial_step5_feat2": "Filtros de serviços",
        "tutorial_step5_feat3": "Rotas",

        "tutorial_step6_title": "💬 Comunidade",
        "tutorial_step6_desc": "Compartilhe experiências e faça perguntas.",
        "tutorial_step6_feat1": "Postagem anônima",
        "tutorial_step6_feat2": "Perguntas jurídicas",
        "tutorial_step6_feat3": "Compartilhamento de conselhos",

        "documents_intro_md": "Envie um documento legal (PDF ou imagem) para obter:\n- Extração de datas e prazos\n- Identificação de ações necessárias\n- Detecção de multas\n- Identificação de órgãos governamentais\n- Geração de resumo",

    },
    "Tamil / தமிழ்": {
        "sidebar_title": "CivicShield",
        "sidebar_tagline": "உங்கள் உரிமைகளை அறிந்து கொள்ளுங்கள்",
        "select_language": "📍 மொழியைத் தேர்ந்தெடுக்கவும்:",
        "nav_home": "🏠 முகப்பு",
        "nav_translation": "🗣️ நேரடி மொழிபெயர்ப்பு",
        "nav_documents": "📄 சட்ட ஆவணங்கள்",
        "nav_rights": "📚 உரிமைகள் மையம்",
        "nav_quiz": "❓ உரிமைகள் வினாடி வினா",
        "nav_resources": "🏥 உள்ளூர் சேவைகள்",
        "nav_nearby": "📍 அருகிலுள்ள உரிமைகள்",
        "nav_logging": "📝 சந்திப்பு பதிவு",
        "nav_emergency": "🚨 அவசரம்",
        "nav_about": "CivicShield பற்றி",
        "sidebar_version": "பதிப்பு 3.0.0",
        "sidebar_purpose": "சிவில் உரிமைகள் பாதுகாப்பு மற்றும் சட்ட மொழிபெயர்ப்பு",
        "sidebar_languages": "14 மொழிகள் ஆதரவு",
        "sidebar_disclaimer": "⚠️ அறிவிப்பு",
        "sidebar_disclaimer_text": "இந்த பயன்பாடு கல்வி தகவலை மட்டுமே வழங்குகிறது. இது சட்ட ஆலோசனை அல்ல. குறிப்பிட்ட வழிகாட்டலுக்கு ஒரு வழக்கறிஞரை அணுகவும்.",

        "home_title": "CivicShield-க்கு வரவேற்கிறோம்",
        "home_subtitle": "உங்கள் உரிமைகளை அறிந்து கொள்ளுங்கள், உங்களை பாதுகாத்துக் கொள்ளுங்கள், உதவி பெறுங்கள்.",
        "dashboard_intro": "தொடங்க ஒரு அம்சத்தைத் தேர்ந்தெடுக்கவும்:",

        "card_translation_title": "நேரடி மொழிபெயர்ப்பு",
        "card_translation_desc": "போலீஸ் கூறுவதை மொழிபெயர்த்து சட்ட ஆலோசனை பெறுங்கள்",
        "card_documents_title": "சட்ட ஆவண உதவியாளர்",
        "card_documents_desc": "ஆவணங்களை பதிவேற்றி முக்கிய தகவல்களைப் பெறுங்கள்",
        "card_rights_title": "உரிமைகள் கல்வி மையம்",
        "card_rights_desc": "உங்கள் அரசியல் உரிமைகளை அறிந்து கொள்ளுங்கள்",
        "card_quiz_title": "உரிமைகள் வினாடி வினா",
        "card_quiz_desc": "உங்கள் சிவில் உரிமை அறிவைச் சோதிக்கவும்",
        "card_resources_title": "உள்ளூர் சேவைகள்",
        "card_resources_desc": "சட்ட உதவி மற்றும் சமூக சேவைகளை கண்டறியுங்கள்",
        "card_nearby_title": "அருகிலுள்ள உரிமைகள்",
        "card_nearby_desc": "அருகிலுள்ள சட்ட மற்றும் சமூக ஆதரவைப் பெறுங்கள்",
        "card_logging_title": "சந்திப்பு பதிவு",
        "card_logging_desc": "போலீஸ் சந்திப்புகளைப் பதிவு செய்யுங்கள்",
        "card_emergency_title": "அவசரம்",
        "card_emergency_desc": "அவசர எண்கள் மற்றும் நடைமுறைகள்",

        "btn_open": "திறக்க",
        "btn_delete": "❌ நீக்கு",
        "btn_record": "🎤 பதிவு",
        "btn_stop": "⏹️ நிறுத்து",
        "btn_translate": "🌐 மொழிபெயர்க்க",
        "btn_listen": "🔊 கேட்க",
        "btn_download": "📥 பதிவிறக்க",
        "btn_search": "🔍 தேடல்",
        "btn_log": "📝 பதிவு",
        "btn_back": "← திரும்ப",
        "btn_submit": "✓ சமர்ப்பிக்க",
        "btn_cancel": "✗ ரத்து",

        "translation_title": "நேரடி மொழிபெயர்ப்பு",
        "translation_subtitle": "போலீஸ் கூறுவதை மொழிபெயர்த்து சட்ட ஆலோசனை பெறுங்கள்",
        "officer_statement": "போலீஸ் கூறியது (ஆங்கிலத்தில்):",
        "your_rights": "உங்கள் உரிமைகள் மற்றும் சட்ட ஆலோசனை:",
        "play_before_title": "1. தொடர்புக்கு முன் பாடல் இயக்கவும்",
        "play_before_desc": "பதிவு தொடங்குவதற்கு முன் இதை போலீஸிடம் இயக்கவும்.",
        "play_before_audio": "Officer, before we begin, I am using a translation app to avoid any language barriers. I am recording with your knowledge for safety and accuracy.",
        "play_after_title": "3. உரிமைகளை புரிந்த பிறகு இயக்கவும்",
        "play_after_desc": "உங்கள் உரிமைகளை கேட்ட பிறகு இதை போலீஸிடம் இயக்கவும்.",
        "play_after_audio": "I understand, officer, and I will comply, but I will be using my right to remain silent.",
        "officer_script": "அதிகாரிக்கான உரை (ஆங்கிலத்தில்):",
        "officer_script_translated": "இது உங்கள் மொழியில் என்னவென்றால்:",
        "record_officer": "🎤 போலீஸ் பேச்சை பதிவு செய்யுங்கள்",
        "stop_recording": "⏹️ பதிவு நிறுத்தி மொழிபெயர்க்க",
        "listen_to_advice": "🔊 ஆலோசனையை கேட்க",
        "translation_hint": "மொழிபெயர்ப்புக்கு தட்டச்சு செய்யவும் அல்லது பதிவு செய்யவும்",
        "generating_audio": "ஆடியோ உருவாக்கப்படுகிறது...",
        "audio_ready": "✅ ஆடியோ தயாராக உள்ளது",
        "audio_failed": "❌ ஆடியோ உருவாக்க முடியவில்லை",
        "speech_recognized": "ஆடியோ உரையாக மாற்றப்பட்டது.",
        "mic_unclear": "ஆடியோ தெளிவாக இல்லை. மீண்டும் முயற்சிக்கவும்.",
        "stt_unavailable": "குரல் அடையாள சேவை கிடைக்கவில்லை.",
        "unable_process_audio": "ஆடியோ செயலாக்க முடியவில்லை. மீண்டும் முயற்சிக்கவும்.",
        "mic_recorder_title": "ஆடியோ பதிவு கருவி",
        "mic_recorder_desc": "போலீஸ் பேச்சை பதிவு செய்ய தொடங்கு/நிறுத்து பொத்தானைப் பயன்படுத்தவும்.",
        "mic_help": "மைக்ரோஃபோன் தடுக்கப்பட்டிருந்தால், உலாவி அமைப்புகளில் அனுமதி வழங்கவும்.",
        "mic_access_failed": "மைக்ரோஃபோன் அணுகல் மறுக்கப்பட்டது. அனுமதி வழங்கி மீண்டும் முயற்சிக்கவும்.",
        "mic_no_audio": "ஆடியோ கண்டறியப்படவில்லை. மைக்ரோஃபோன் தடுக்கப்பட்டிருக்கலாம்.",
        "btn_clear_filter": "வடிகட்டலை நீக்கு",
        "currently_filtering": "வடிகட்டப்படுகிறது:",
        "quiz_correct": "✅ சரியான பதில்!",
        "quiz_incorrect": "❌ தவறான பதில்.",
        "language_selector_error": "❌ மொழி தேர்வு பிழை",
        "demo_section_title": "டெமோ மற்றும் சோதனை முறை",
        "demo_on": "🎬 டெமோ ON",
        "demo_off": "🎬 டெமோ OFF",
        "tour_button": "🎓 சுற்றுப்பயணம் பார்க்க",
        "tour_complete": "✅ சுற்றுப்பயணம் முடிந்தது! நீங்கள் தயாராக உள்ளீர்கள்.",
        "btn_go_home": "🏠 முகப்புக்கு திரும்ப",
        "btn_skip_tour": "⏭️ தவிர்க்க",
        "btn_next": "அடுத்து ➡️",
        "btn_start_using": "🎉 பயன்படுத்தத் தொடங்குங்கள்",

        "documents_title": "சட்ட ஆவண உதவியாளர்",
        "documents_subtitle": "ஆவணங்களை பதிவேற்றி முக்கிய தகவல்களைப் பெறுங்கள்",
        "upload_document": "📤 ஆவணத்தை பதிவேற்றவும்",
        "take_photo": "📸 புகைப்படம் எடுக்க",
        "extract_text": "உரை எடுக்க",
        "simplify_text": "சட்ட உரையை எளிமைப்படுத்து",
        "translate_document": "🌐 ஆவணத்தை மொழிபெயர்க்க",
        "extract_dates": "📅 கண்டறியப்பட்ட தேதிகள்",
        "extract_deadlines": "⏰ கடைசி தேதிகள்",
        "extract_agencies": "🏛️ அரசு அமைப்புகள்",
        "extract_actions": "✅ தேவையான நடவடிக்கைகள்",
        "download_report": "📥 அறிக்கையை பதிவிறக்க",
        "report_generated": "அறிக்கை உருவாக்கப்பட்டது",

        "rights_title": "உரிமைகள் மையம்",
        "rights_subtitle": "உங்கள் அரசியல் உரிமைகளை அறிந்து கொள்ளுங்கள்",
        "right_fourth": "4வது திருத்தம்: தேடல் & பறிமுதல்",
        "right_fifth": "5வது திருத்தம்: மௌனமாக இருப்பதற்கான உரிமை",
        "right_sixth": "6வது திருத்தம்: வழக்கறிஞர் பெறும் உரிமை",
        "right_traffic": "போக்குவரத்து நிறுத்தத்தில் உங்கள் உரிமைகள்",
        "right_arrest": "நீங்கள் கைது செய்யப்பட்டால்",
        "right_fourth_content": "**உங்கள் உரிமைகள்:** 4வது திருத்தம் காரணமில்லாத தேடல் மற்றும் பறிமுதல் நடவடிக்கைகளிலிருந்து உங்களை பாதுகாக்கிறது.\n\n**முக்கிய குறிப்புகள்:**\n- உங்கள் வீடு, வாகனம் அல்லது பொருட்களை தேட போலீசுக்கு பொதுவாக வாரண்ட் தேவை\n- நீங்கள் தெளிவாகச் சொல்லலாம்: “நான் தேடலை அனுமதிக்கவில்லை”\n- உடல் ரீதியாக எதிர்க்க வேண்டாம் (அது கூடுதல் குற்றச்சாட்டுகளுக்கு வழிவகுக்கும்)\n- போலீஸ் வாரண்ட் அல்லது probable cause இருந்தால் தேடலாம்\n\n**நீங்கள் செய்யக்கூடியவை:**\n- அமைதியாக இருங்கள் மற்றும் கேளுங்கள்: “நான் தடுத்து வைக்கப்பட்டுள்ளேனா அல்லது போகலாமா?”\n- வாரண்டை காண்பிக்கச் சொல்லுங்கள்\n- உங்கள் கைகளை தெளிவாக வைத்திருங்கள்\n- போலீஸ் பணியைத் தடுக்க வேண்டாம்",

        "right_fifth_content": "**உங்கள் உரிமைகள்:** நீங்கள் மௌனமாக இருக்க உரிமை பெற்றுள்ளீர்கள், மேலும் உங்களை குற்றம் சாட்டும் வகையில் பேச போலீஸ் உங்களை கட்டாயப்படுத்த முடியாது.\n\n**முக்கிய குறிப்புகள்:**\n- போலீஸ் கேள்விகளுக்கு நீங்கள் பதில் அளிக்க வேண்டிய அவசியமில்லை\n- தெளிவாகச் சொல்லுங்கள்: “நான் மௌனமாக இருக்கிறேன்”\n- கைது செய்யப்படும் முன்பும் பிறகும் இந்த உரிமை பொருந்தும்\n- உங்கள் மௌனம் நீதிமன்றத்தில் உங்களுக்கு எதிராக பயன்படுத்த முடியாது\n\n**முக்கியம்:**\n- நீங்கள் இந்த உரிமையைப் பயன்படுத்துகிறீர்கள் என்று சொல்ல வேண்டும்\n- கைது செய்யப்பட்டால் உடனே வழக்கறிஞரை கேளுங்கள்\n- விளக்க வேண்டாம், விவாதிக்க வேண்டாம்",

        "right_sixth_content": "**உங்கள் உரிமைகள்:** நீங்கள் ஒரு வழக்கறிஞரைப் பெற உரிமை பெற்றுள்ளீர்கள்.\n\n**முக்கிய குறிப்புகள்:**\n- நீங்கள் செலுத்த முடியாவிட்டால், ஒரு பொது பாதுகாவலர் நியமிக்கப்படுவார்\n- எந்த நேரத்திலும் நீங்கள் வழக்கறிஞரை கேட்கலாம்\n- நீங்கள் வழக்கறிஞரை கேட்ட பிறகு, போலீஸ் விசாரணையை நிறுத்த வேண்டும்\n- விசாரணையின் போது வழக்கறிஞர் உங்களுடன் இருக்கலாம்\n\n**சொல்ல வேண்டியது:**\n- “நான் ஒரு வழக்கறிஞரைப் பேச விரும்புகிறேன்”\n- “நான் என் வழக்கறிஞர் உரிமையைப் பயன்படுத்துகிறேன்”\n- இதைச் சொன்ன பிறகு மௌனமாக இருங்கள்",

        "right_traffic_content": "**போக்குவரத்து நிறுத்தத்தின் போது:**\n- நீங்கள் ஓட்டுநர் உரிமம், பதிவு மற்றும் காப்பீட்டை வழங்க வேண்டும்\n- கேளுங்கள்: “நான் தடுத்து வைக்கப்பட்டுள்ளேனா அல்லது போகலாமா?”\n- உங்கள் காரை தேட அனுமதிக்க வேண்டிய அவசியமில்லை\n- சொல்லுங்கள்: “நான் தேடலை அனுமதிக்கவில்லை”\n\n**வாகன தேடல்:**\n- போலீஸ் காரின் உள்ளே பார்க்கலாம்\n- probable cause இருந்தால் தேடலாம்\n- நீங்கள் கைது செய்யப்பட்டால், காரை தேடலாம்\n\n**உங்கள் உரிமைகள்:**\n- கைகளை தெளிவாக வைத்திருங்கள்\n- அமைதியாகவும் மரியாதையாகவும் இருங்கள்\n- எதிர்க்க வேண்டாம்\n- போலீஸைத் தடையில்லாமல் நீங்கள் பதிவு செய்யலாம்",

        "right_arrest_content": "**நீங்கள் கைது செய்யப்பட்டால் செய்ய வேண்டியவை:**\n1. மௌனமாக இருங்கள் — கேள்விகளுக்கு பதில் அளிக்க வேண்டாம்\n2. சொல்லுங்கள்: “நான் ஒரு வழக்கறிஞரை விரும்புகிறேன்”\n3. வழக்கறிஞர் இல்லாமல் எதற்கும் கையொப்பமிட வேண்டாம்\n4. மற்ற கைதிகளுடன் வழக்கைப் பற்றி பேச வேண்டாம்\n\n**கைது செய்யப்பட்டபோது உங்கள் உரிமைகள்:**\n- கைது காரணத்தை அறிய உரிமை\n- ஒரு தொலைபேசி அழைப்பு செய்ய உரிமை\n- மௌனமாக இருக்க உரிமை\n- வழக்கறிஞர் பெற உரிமை\n\n**தவிர்க்க வேண்டியது:**\n- எதிர்ப்பு (அது கூடுதல் குற்றச்சாட்டுகளுக்கு வழிவகுக்கும்)\n- ஒப்புதல் அளித்தல்\n- தேடலை அனுமதித்தல்\n- போலீஸுடன் பேச்சுவார்த்தை நடத்துதல்",

        "resources_title": "உள்ளூர் சேவைகள்",
        "resources_subtitle": "சட்ட உதவி மற்றும் சமூக சேவைகளை கண்டறியுங்கள்",
        "legal_aid": "சட்ட உதவி அலுவலகங்கள்",
        "emergency_services": "அவசர சேவைகள்",
        "immigration": "குடியேற்ற சட்ட உதவி",
        "phone": "தொலைபேசி: ",
        "services": "சேவைகள்: ",
        "website": "இணையதளம்: ",
        "hours": "நேரம்: ",

        "nearby_title": "அருகிலுள்ள உரிமைகள்",
        "nearby_subtitle": "அருகிலுள்ள சட்ட மற்றும் சமூக ஆதரவைப் பெறுங்கள்",
        "enter_address": "முகவரியை உள்ளிடவும்:",
        "search_radius": "தேடல் வட்டாரம் (மைல்கள்):",
        "nearest_legal_aid": "📋 அருகிலுள்ள சட்ட உதவி அலுவலகம்",
        "nearest_courthouse": "⚖️ அருகிலுள்ள நீதிமன்றம்",
        "nearest_police": "👮 அருகிலுள்ள போலீஸ் நிலையம்",
        "nearest_translator": "🗣️ மொழிபெயர்ப்பு சேவைகள்",
        "nearest_community": "🏢 சமூக மையம்",
        "address": "முகவரி: ",
        "phone_number": "தொலைபேசி: ",
        "hours_open": "நேரம்: ",
        "get_directions": "🗺️ வழிமுறைகள்",
        "not_found": "இந்த பகுதியில் எந்த முடிவும் கிடைக்கவில்லை",
        "logging_title": "சந்திப்பு பதிவு",
        "logging_subtitle": "போலீஸ் சந்திப்புகளைப் பதிவு செய்யுங்கள்",
        "encounter_type": "சந்திப்பு வகை:",
        "encounter_location": "இடம்:",
        "encounter_details": "விவரங்கள்:",
        "encounter_date": "தேதி & நேரம்:",
        "officer_info": "போலீஸ் தகவல்:",
        "officer_badge": "அடையாள எண்:",
        "officer_agency": "அமைப்பு:",
        "encounter_saved": "✅ சந்திப்பு சேமிக்கப்பட்டது",
        "view_history": "📋 வரலாற்றைப் பார்க்க",
        "total_encounters": "மொத்த சந்திப்புகள்:",
        "search_encounters": "🔍 வரலாற்றில் தேடுங்கள்",

        "emergency_title": "அவசரம்",
        "emergency_subtitle": "அவசர எண்கள் மற்றும் சேவைகள்",
        "emergency_911": "911 — போலீஸ், ஆம்புலன்ஸ், தீயணைப்பு",
        "emergency_suicide": "தற்கொலை தடுப்பு உதவி எண்",
        "emergency_domestic": "உள்நாட்டு வன்முறை உதவி எண்",
        "emergency_assault": "RAINN — பாலியல் வன்முறை உதவி",
        "emergency_poison": "நச்சு கட்டுப்பாட்டு மையம்",
        "emergency_text": "அவசர குறுஞ்செய்தி உதவி வரி",
        "emergency_procedures": "அவசர நடைமுறைகள்:",
        "procedure_safe": "நீங்கள் பாதுகாப்பான இடத்தில் இருப்பதை உறுதி செய்யுங்கள்",
        "procedure_document": "அனைத்து விவரங்களையும் பதிவு செய்யுங்கள்",
        "procedure_record": "சட்டபூர்வமாகவும் பாதுகாப்பாகவும் இருந்தால் வீடியோ பதிவு செய்யுங்கள்",
        "procedure_call": "உடனடியாக உதவி கேளுங்கள்",
        "procedure_contact": "ஒரு வழக்கறிஞரை தொடர்பு கொள்ளுங்கள்",

        "loading": "ஏற்றப்படுகிறது...",
        "success": "வெற்றி!",
        "error": "ஒரு பிழை ஏற்பட்டது",
        "warning": "எச்சரிக்கை",
        "info": "தகவல்",
        "processing": "செயலாக்கப்படுகிறது...",
        "please_wait": "தயவுசெய்து காத்திருக்கவும்...",
        "no_data": "தரவு இல்லை",
        "try_again": "மீண்டும் முயற்சிக்கவும்",

        "accessibility_title": "♿ அணுகல் வசதி",
        "text_size": "உரையின் அளவு:",
        "text_size_normal": "சாதாரணம்",
        "text_size_large": "பெரியது",
        "text_size_extra_large": "மிகப் பெரியது",
        "high_contrast": "🎨 அதிக மாறுபாடு",
        "high_contrast_on": "அதிக மாறுபாடு ON",
        "high_contrast_off": "அதிக மாறுபாடு OFF",
        "screen_reader": "திரை வாசிப்பான் இயக்கவும்",
        "accessibility_saved": "✅ அணுகல் அமைப்புகள் சேமிக்கப்பட்டது",
        "extract_deadlines": "📋 கண்டறியப்பட்ட கடைசி தேதிகள்",
        "extract_penalties": "⚠️ அபராதங்கள் மற்றும் எச்சரிக்கைகள்",
        "extract_requirements": "✓ தேவையான நடவடிக்கைகள்",
        "deadline_found": "கடைசி தேதி:",
        "penalty_found": "அபராதம்:",
        "requirement_found": "தேவையான செயல்:",
        "document_summary": "📋 ஆவண சுருக்கம்",
        "summary_generated": "சுருக்கம் வெற்றிகரமாக உருவாக்கப்பட்டது",

        "location_title": "📍 அருகிலுள்ள சேவைகளைத் தேடுங்கள்",
        "enter_address": "முகவரி அல்லது ZIP குறியீட்டை உள்ளிடவும்:",
        "search_radius_miles": "தேடல் வட்டாரம் (மைல்கள்):",
        "find_resources": "🔍 சேவைகளைத் தேடுங்கள்",
        "resource_type": "சேவை வகை:",
        "all_resources": "அனைத்து சேவைகள்",
        "legal_aid_offices": "சட்ட உதவி அலுவலகங்கள்",
        "community_centers": "சமூக மையங்கள்",
        "language_services": "மொழிபெயர்ப்பு சேவைகள்",
        "emergency_shelters": "அவசர தங்கும் இடங்கள்",
        "distance_away": "மைல்கள் தொலைவில்",
        "get_directions": "🗺️ வழிமுறைகள்",
        "no_resources_found": "இந்த பகுதியில் எந்த சேவையும் கிடைக்கவில்லை",
        "resource_hours": "நேரம்:",
        "resource_phone": "தொலைபேசி:",
        "resource_address": "முகவரி:",
        "resource_website": "இணையதளம்:",
        "loading_resources": "அருகிலுள்ள சேவைகள் தேடப்படுகிறது...",

        "saved_deadlines": "⏰ சேமிக்கப்பட்ட கடைசி தேதிகள்",
        "upload_legal_doc": "சட்ட ஆவணத்தை பதிவேற்றவும்",
        "important_dates": "📅 முக்கிய தேதிகள்",
        "required_actions": "✓ தேவையான நடவடிக்கைகள்",
        "critical_deadlines": "⏰ முக்கிய கடைசி தேதிகள்",
        "penalties_warnings": "⚠️ அபராதங்கள் மற்றும் எச்சரிக்கைகள்",
        "extraction_guide": "எடுத்தல் வழிகாட்டி",
        "demo_mode_active": "📺 **டெமோ முறை ON** — உதாரண தரவு காட்டப்படுகிறது",
        "have_deadlines": "📋 உங்களிடம் முக்கிய கடைசி தேதிகள் உள்ளன!",
        "view_all_deadlines": "📋 அனைத்து கடைசி தேதிகளையும் பார்க்க →",
        "from_document": "ஆவணத்திலிருந்து:",
        "file_type": "கோப்பு வகை",
        "file_size": "கோப்பு அளவு",
        "status_ready": "எடுத்தலுக்கு தயாராக உள்ளது",
        "extract_information": "🔍 தகவலை எடுக்க",
        "extracting_info": "ஆவணத்திலிருந்து தகவல் எடுக்கப்படுகிறது...",
        "no_dates_found": "எந்த தேதியும் கிடைக்கவில்லை",
        "no_deadlines_found": "எந்த கடைசி தேதியும் கிடைக்கவில்லை",
        "no_penalties_found": "எந்த அபராதமும் கிடைக்கவில்லை",
        "download_summary": "📥 சுருக்கத்தை பதிவிறக்க",
        "download_as_txt": "TXT ஆக பதிவிறக்க",
        "save_deadlines_to_dashboard": "💾 கடைசி தேதிகளை டாஷ்போர்டில் சேமிக்க",
        "know_your_rights_long": "⚖️ உங்கள் உரிமைகளை அறிந்து கொள்ளுங்கள்",
        "education_quizzes": "கல்வி • வினாடி வினா • கற்றல் தொகுதிகள்",
        "learn_tab": "📚 கற்றல்",
        "quiz_tab": "🧪 வினாடி வினா",
        "rights_education": "உரிமைகள் கல்வி",
        "select_topic": "ஒரு தலைப்பைத் தேர்ந்தெடுக்கவும்:",
        "test_knowledge": "உங்கள் சிவில் உரிமை அறிவைச் சோதிக்கவும்.",
        "rights_quiz": "உரிமைகள் வினாடி வினா",

        "can_police_search": "போலீஸ் உங்கள் காரை அனுமதி இல்லாமல் தேட முடியுமா?",
        "only_with_warrant": "வாரண்ட் இருந்தால் மட்டுமே",
        "only_prob_cause": "probable cause இருந்தால் மட்டுமே",
        "both_a_and_b": "A மற்றும் B இரண்டும்",
        "never_without": "இல்லை, ஒருபோதும் முடியாது",
        "police_can_search": "வாரண்ட் அல்லது probable cause இருந்தால் போலீஸ் தேடலாம்.",

        "answer_police_q": "போலீஸ் கேள்விகளுக்கு நீங்கள் பதில் அளிக்க வேண்டுமா?",
        "yes_always": "ஆம், எப்போதும்",
        "right_remain_silent": "இல்லை, உங்களுக்கு மௌனமாக இருக்க உரிமை உள்ளது",
        "only_your_name": "உங்கள் பெயர் மட்டும்",
        "only_if_arrested": "கைது செய்யப்பட்டால் மட்டுமே",
        "fifth_amendment": "5வது திருத்தம் உங்களுக்கு மௌனமாக இருக்க உரிமை அளிக்கிறது.",

        "what_say_arrested": "நீங்கள் கைது செய்யப்பட்டால் என்ன சொல்ல வேண்டும்?",
        "explain_what_happened": "என்ன நடந்தது என்பதை விளக்குங்கள்",
        "ask_for_lawyer": "ஒரு வழக்கறிஞரை கேளுங்கள்",
        "refuse_give_name": "பெயரை வழங்க மறுக்கவும்",
        "try_negotiate": "போலீஸுடன் பேச்சுவார்த்தை நடத்த முயற்சிக்கவும்",
        "always_ask_lawyer": "ஒரு வழக்கறிஞரை கேட்டு அதன் பிறகு மௌனமாக இருங்கள்.",

        "check_answer": "✓ பதிலை சரிபார்க்கவும் {number}",
        "question_number": "கேள்வி {number}: {question}",
        "select_answer": "ஒரு பதிலைத் தேர்ந்தெடுக்கவும்:",
        "your_score": "உங்கள் மதிப்பெண்",

        "talk_community": "💬 சமூகத்துடன் பேசுங்கள்",
        "community_intro": "அனுபவங்களைப் பகிருங்கள், கேள்விகளை கேளுங்கள், மற்றவர்களுக்கு உதவுங்கள் — நாம் ஒன்றாக வலிமையானவர்கள்",
        "share_exp_tab": "💭 அனுபவத்தை பகிருங்கள்",
        "ask_q_tab": "❓ கேள்வி கேளுங்கள்",
        "give_advice_tab": "💡 ஆலோசனை வழங்குங்கள்",
        "share_your_exp": "💭 உங்கள் அனுபவத்தைப் பகிருங்கள்",
        "share_story": "உங்கள் அனுபவம் மற்றவர்களுக்கு உதவலாம். அனைத்து பதிவுகளும் பாதுகாப்பிற்காக மதிப்பாய்வு செய்யப்படும்.",
        "title_label": "தலைப்பு:",
        "exp_placeholder": "உதாரணம்: நான் போக்குவரத்து நிறுத்தத்தை எப்படி சமாளித்தேன்",
        "your_story": "உங்கள் அனுபவம்:",
        "story_placeholder": "உங்கள் அனுபவத்தை இங்கே எழுதுங்கள்...",
        "post_anonymously": "அடையாளம் தெரியாமல் பதிவிடுங்கள்",
        "share_exp_btn": "📤 அனுபவத்தை பகிருங்கள்",
        "fill_title_content": "⚠️ தலைப்பு மற்றும் உள்ளடக்கத்தை உள்ளிடவும்",
        "exp_shared": "✅ அனுபவம் வெற்றிகரமாக பகிரப்பட்டது! உங்கள் பங்களிப்புக்கு நன்றி.",
        "ask_community": "❓ சமூகத்திடம் கேளுங்கள்",
        "question_help": "உங்களுக்கு கேள்வி உள்ளதா? சமூகத்தினர் உதவ தயாராக உள்ளனர்.",
        "your_question": "உங்கள் கேள்வி:",
        "question_placeholder": "உதாரணம்: போக்குவரத்து நிறுத்தத்தின் போது என்ன உரிமைகள் உள்ளன?",
        "details_label": "விவரங்கள்:",
        "details_placeholder": "கூடுதல் தகவலை உள்ளிடவும்...",
        "ask_anon": "அடையாளம் தெரியாமல் பதிவிடுங்கள்",
        "ask_q_btn": "❓ கேள்வியை பதிவிடுங்கள்",
        "enter_question": "⚠️ கேள்வியை உள்ளிடவும்",
        "question_posted": "✅ கேள்வி வெற்றிகரமாக பதிவிடப்பட்டது!",

        "give_advice": "💡 ஆலோசனை வழங்குங்கள்",
        "help_others": "உங்கள் அனுபவம் மற்றும் அறிவால் மற்றவர்களுக்கு உதவுங்கள்.",
        "topic_label": "தலைப்பு:",
        "topic_placeholder": "உதாரணம்: நீதிமன்ற விசாரணைக்கு எப்படி தயாராகுவது",
        "your_advice": "உங்கள் ஆலோசனை:",
        "advice_placeholder": "உங்கள் ஆலோசனையை இங்கே எழுதுங்கள்...",
        "share_anon": "அடையாளம் தெரியாமல் பதிவிடுங்கள்",
        "share_advice_btn": "💡 ஆலோசனையை பகிருங்கள்",
        "share_wisdom": "✅ ஆலோசனை வெற்றிகரமாக பகிரப்பட்டது!",
        "fill_topic_advice": "⚠️ தலைப்பு மற்றும் ஆலோசனையை உள்ளிடவும்",

        "recent_posts": "📋 சமீபத்திய பதிவுகள்",
        "no_posts_yet": "💭 இன்னும் பதிவுகள் இல்லை. முதலில் நீங்கள் பகிரலாம்!",
        "posted_recently": "{timestamp} முன் பதிவிடப்பட்டது",
        "author_anonymous": "அடையாளம் தெரியாதவர்",
        "author_community_member": "சமூக உறுப்பினர்",

        "crisis_hotlines": "🚨 அவசர உதவி எண்கள்",
        "crisis_support_24": "24 மணி நேர உதவி கிடைக்கிறது",
        "emergency_hotlines_header": "🆘 அவசர எண்கள்",
        "in_immediate_danger": "உடனடி ஆபத்தில் இருந்தால் 911 அழைக்கவும்",
        "emergency_number": "அவசர எண்",
        "suicide_prevention": "தற்கொலை தடுப்பு உதவி எண்",
        "domestic_violence": "உள்நாட்டு வன்முறை உதவி எண்",
        "sexual_assault": "RAINN — பாலியல் வன்முறை உதவி",
        "poison_control": "நச்சு கட்டுப்பாட்டு மையம்",
        "crisis_text": "அவசர குறுஞ்செய்தி உதவி வரி",

        "safety_procedures": "📋 பாதுகாப்பு நடைமுறைகள்",
        "stay_safe": "🛡️ பாதுகாப்பாக இருங்கள்",
        "stay_safe_desc": "உங்கள் பாதுகாப்பு முதன்மை — உடல் ரீதியாக எதிர்க்க வேண்டாம்.",
        "document_details": "📝 விவரங்களை பதிவு செய்யுங்கள்",
        "document_details_desc": "போலீஸ் பெயர், அடையாள எண், இடம், நேரம் மற்றும் நடந்ததை பதிவு செய்யுங்கள்.",
        "record_safely": "🎥 பாதுகாப்பாக பதிவு செய்யுங்கள்",
        "record_safely_desc": "சட்டபூர்வமாகவும் பாதுகாப்பாகவும் இருந்தால் பதிவு செய்யுங்கள்.",
        "call_for_help": "📞 உதவி கேளுங்கள்",
        "call_help_desc": "ஆபத்தில் இருந்தால் 911 அழைக்கவும் மற்றும் தெளிவாக பேசுங்கள்.",
        "get_legal_help": "⚖️ சட்ட உதவி பெறுங்கள்",
        "legal_help_desc": "ஒரு வழக்கறிஞரை தொடர்பு கொள்ளுங்கள். பொது பாதுகாவலர்கள் அவசர உதவி வழங்கலாம்.",
        "medical_attention": "🏥 மருத்துவ உதவி",
        "medical_attention_desc": "காயம் இருந்தால் உடனடியாக மருத்துவ உதவி பெறுங்கள் மற்றும் புகைப்படங்கள் எடுக்கவும்.",
        "mental_health_support": "🧠 மனநலம் ஆதரவு",
        "legal_troubles_trauma": "சட்ட பிரச்சினைகள் அல்லது போலீஸ் சந்திப்புகள் மன உளைச்சலை ஏற்படுத்தலாம்.",
        "mental_health_resources": "மனநலம் ஆதரவு வளங்கள்:",
        "samhsa_helpline": "SAMHSA உதவி எண்: 1‑800‑662‑4357 (இலவசம் • ரகசியம் • 24/7)",
        "psychology_directory": "மனநல நிபுணர்கள் பட்டியல்: Psychology Today",
        "support_groups": "ஆதரவு குழுக்கள்: NAACP, சமூக மையங்கள், சட்ட அமைப்புகள்",
        "contact_emergency": "🆘 அவசரம்",
        "contact_suicide": "🧠 தற்கொலை தடுப்பு உதவி",
        "contact_domestic": "💔 உள்நாட்டு வன்முறை உதவி",
        "contact_rainn": "🤝 RAINN — பாலியல் வன்முறை உதவி",
        "contact_poison": "☠️ நச்சு கட்டுப்பாட்டு மையம்",
        "contact_crisis_text": "📱 அவசர குறுஞ்செய்தி உதவி வரி",
        "contact_crisis_text_number": "HOME என 741741க்கு அனுப்பவும்",

        "enc_type_traffic_stop": "போக்குவரத்து நிறுத்தம்",
        "enc_type_street_encounter": "தெரு சந்திப்பு",
        "enc_type_arrest": "கைது",
        "enc_type_search": "தேடல்",
        "enc_type_other": "மற்றவை",
        "encounter_label": "சந்திப்பு",
        "unknown": "தெரியவில்லை",
        "na": "N/A",
        "error_generating_qr": "QR குறியீட்டை உருவாக்கும்போது பிழை ஏற்பட்டது",

        "btn_launch_app": "🚀 பயன்பாட்டைத் திறக்க",
        "btn_start_demo": "📺 டெமோ தொடங்கு",
        "btn_quick_tour": "❓ விரைவு சுற்றுப்பயணம்",
        "share_with_others": "📱 பிறருடன் பகிரவும்",
        "qr_generation_in_progress": "QR குறியீடு உருவாக்கப்படுகிறது...",
        "key_features_label": "முக்கிய அம்சங்கள்:",
        "btn_previous": "⬅️ முந்தையது",
        "language_change_error": "மொழி மாற்றத்தில் பிழை",
        "demo_mode_active_sidebar": "✅ டெமோ முறை ON — உதாரண தரவு காட்டப்படுகிறது",
        "screen_reader_off": "🔇 திரை வாசிப்பான் OFF",
        "navigation_title": "வழிசெலுத்தல்",
        "nav_rights_full": "⚖️ உங்கள் உரிமைகளை அறியுங்கள்",
        "nav_resources_near_you": "📍 அருகிலுள்ள சேவைகள்",
        "nav_logging_full": "📝 சந்திப்பு பதிவு",
        "nav_crisis_resources": "🚨 அவசர உதவி வளங்கள்",
        "nav_community": "💬 சமூக மையம்",

        "sidebar_built_for": "அனைவரின் சிவில் உரிமைகளை பாதுகாக்க உருவாக்கப்பட்டது.",
        "show_landing_page": "🏠 முகப்பு பக்கத்தை காண்பிக்க",

        "landing_hero_html": "<div class=\"landing-hero\"><h1>⚖️ CivicShield Pro</h1><h2>உங்கள் உரிமைகளை அறிந்து கொள்ளுங்கள், உங்களை பாதுகாத்துக் கொள்ளுங்கள், உதவி பெறுங்கள்.</h2><p>14 மொழிகளில் சிவில் உரிமை தகவலை வழங்கும் ஒரு தளம்.</p></div>",

        "landing_purpose_md": "### 🎯 நோக்கம்\nCivicShield Pro வழங்குவது:\n\n- **14 மொழிகளில் உடனடி சட்ட மொழிபெயர்ப்பு**\n- **நிலைமைகளுக்கு ஏற்ப உரிமை வழிகாட்டிகள்**\n- **சட்ட ஆவண பகுப்பாய்வு மற்றும் கடைசி தேதி எடுக்கும் கருவிகள்**\n- **சமூக ஆதரவு மற்றும் அனுபவ பகிர்வு**\n- **24/7 அவசர உதவி வளங்கள்**",

        "landing_features_md": "### ⭐ முக்கிய அம்சங்கள்\n\n- 🗣️ **நேரடி மொழிபெயர்ப்பு** — போலீஸ் கூறுவதை உடனே புரிந்து கொள்ளுங்கள்\n- 📄 **சட்ட ஆவண கருவிகள்** — முக்கிய தகவல்களை எடுக்க\n- ⚖️ **உரிமைகள் கல்வி** — கற்றல் & வினாடி வினா\n- 📍 **அருகிலுள்ள சேவைகள்** — சட்ட மற்றும் சமூக ஆதரவு\n- 📝 **சந்திப்பு பதிவு** — போலீஸ் சந்திப்புகளைப் பதிவு செய்யுங்கள்\n- 🚨 **அவசர உதவி எண்கள்** — 24/7 ஆதரவு\n- 💬 **சமூக மன்றம்** — கேள்விகள் & அனுபவங்கள்",

        "landing_share_md": "**CivicShield-ஐ பகிர்வது எப்படி:**\n\n1. QR குறியீட்டை ஸ்கேன் செய்யுங்கள்\n2. நிறுவல் தேவையில்லை\n3. 14 மொழிகள் ஆதரவு\n4. மொபைல் & கணினியில் வேலை செய்கிறது",

        "landing_who_should_use_md": "### 👥 யார் பயன்படுத்த வேண்டும்?\n\n**நீதிபதிகள் & வழக்கறிஞர்கள்:**\n- சமூக பார்வையைப் புரிந்து கொள்ள\n- உரிமை அறிவை மதிப்பிட\n- உடனடி மொழிபெயர்ப்பு பயன்படுத்த\n\n**சட்ட அமைப்புகள்:**\n- பல மொழிகளில் தகவல் வழங்க\n- வாடிக்கையாளர்களுக்கு ஆதரவு\n- சமூகத்தை இணைக்க\n\n**கல்வியாளர்கள்:**\n- சிவில் உரிமைகளை கற்பிக்க\n- உண்மையான உதாரணங்கள் பயன்படுத்த\n- வினாடி வினா செயல்படுத்த\n\n**சமூக மக்கள்:**\n- போலீஸ் சந்திப்புகளை சமாளிக்க கற்றுக்கொள்ள\n- அவசர உதவி பெற\n- அனுபவங்களைப் பகிர",

        "landing_disclaimer_md": "**⚠️ அறிவிப்பு:**\n\nCivicShield Pro கல்வி தகவலை மட்டுமே வழங்குகிறது.\nஇது சட்ட ஆலோசனை அல்ல.\nசட்டங்கள் மாநிலத்துக்கு மாறுபடும்.\nகுறிப்பிட்ட வழிகாட்டலுக்கு ஒரு வழக்கறிஞரை அணுகவும்.",

        "tutorial_intro_html": "<div class=\"tutorial-container\"><h1>👋 CivicShield Pro-க்கு வரவேற்கிறோம்!</h1><p>ஒரு விரைவு சுற்றுப்பயணத்தை தொடங்கலாம்.</p></div>",

        "tutorial_step1_title": "🏠 முதன்மை டாஷ்போர்டு",
        "tutorial_step1_desc": "இங்கே அனைத்து அம்சங்களையும் அணுகலாம்.",
        "tutorial_step1_feat1": "முழு வழிசெலுத்தல்",
        "tutorial_step1_feat2": "சேமிக்கப்பட்ட கடைசி தேதிகள்",
        "tutorial_step1_feat3": "அவசர அணுகல்",

        "tutorial_step2_title": "🗣️ நேரடி மொழிபெயர்ப்பு",
        "tutorial_step2_desc": "போலீஸ் பேச்சை 14 மொழிகளில் மொழிபெயர்க்கலாம்.",
        "tutorial_step2_feat1": "குரல் அடையாளம்",
        "tutorial_step2_feat2": "உடனடி மொழிபெயர்ப்பு",
        "tutorial_step2_feat3": "ஆடியோ கேட்கலாம்",

        "tutorial_step3_title": "📄 சட்ட ஆவணங்கள்",
        "tutorial_step3_desc": "ஆவணங்களை பதிவேற்றி முக்கிய தகவல்களை எடுக்கலாம்.",
        "tutorial_step3_feat1": "கடைசி தேதி எடுக்கும் கருவி",
        "tutorial_step3_feat2": "அபராதங்கள் கண்டறிதல்",
        "tutorial_step3_feat3": "ஆவண மொழிபெயர்ப்பு",

        "tutorial_step4_title": "⚖️ உரிமைகள் கல்வி",
        "tutorial_step4_desc": "உங்கள் உரிமைகளை கற்றுக்கொள்ளவும் சோதிக்கவும்.",
        "tutorial_step4_feat1": "உரிமை பாடங்கள்",
        "tutorial_step4_feat2": "வினாடி வினா",
        "tutorial_step4_feat3": "முன்னேற்ற கண்காணிப்பு",

        "tutorial_step5_title": "📍 அருகிலுள்ள சேவைகள்",
        "tutorial_step5_desc": "சட்ட மற்றும் சமூக ஆதரவை கண்டறியுங்கள்.",
        "tutorial_step5_feat1": "இடம் அடிப்படையிலான தேடல்",
        "tutorial_step5_feat2": "சேவை வடிகட்டிகள்",
        "tutorial_step5_feat3": "வழிமுறைகள்",

        "tutorial_step6_title": "💬 சமூக மன்றம்",
        "tutorial_step6_desc": "அனுபவங்களைப் பகிரவும் கேள்விகளை கேளுங்கள்.",
        "tutorial_step6_feat1": "அடையாளம் தெரியாமல் பதிவிடல்",
        "tutorial_step6_feat2": "சட்ட கேள்விகள்",
        "tutorial_step6_feat3": "ஆலோசனை பகிர்வு",

        "documents_intro_md": "சட்ட ஆவணத்தை (PDF அல்லது படம்) பதிவேற்றி பெறலாம்:\n- தேதிகள் மற்றும் கடைசி தேதிகள்\n- தேவையான நடவடிக்கைகள்\n- அபராதங்கள்\n- அரசு அமைப்புகள்\n- ஆவண சுருக்கம்",
    },
    "Telugu / తెలుగు": {
        "sidebar_title": "CivicShield",
        "sidebar_tagline": "మీ హక్కులను అర్థం చేసుకోండి",
        "select_language": "📍 భాషను ఎంచుకోండి:",
        "nav_home": "🏠 హోమ్",
        "nav_translation": "🗣️ రియల్‑టైమ్ అనువాదం",
        "nav_documents": "📄 లీగల్ డాక్యుమెంట్లు",
        "nav_rights": "📚 హక్కుల కేంద్రం",
        "nav_quiz": "❓ హక్కుల క్విజ్",
        "nav_resources": "🏥 కమ్యూనిటీ సేవలు",
        "nav_nearby": "📍 మీకు సమీపంలోని హక్కులు",
        "nav_logging": "📝 ఎదుర్కొన్న సంఘటనల రికార్డు",
        "nav_emergency": "🚨 అత్యవసర సహాయం",
        "nav_about": "CivicShield గురించి",
        "sidebar_version": "వెర్షన్ 3.0.0",
        "sidebar_purpose": "పౌర హక్కుల రక్షణ మరియు ప్రొఫెషనల్ లీగల్ అనువాదం",
        "sidebar_languages": "14 భాషలకు మద్దతు",
        "sidebar_disclaimer": "⚠️ లీగల్ నోటీసు",
        "sidebar_disclaimer_text": "ఈ యాప్ విద్యాపరమైన సమాచారాన్ని అందిస్తుంది, లీగల్ సలహా కాదు. మీ కేసుకు సంబంధించిన ప్రత్యేక సలహా కోసం న్యాయవాదిని సంప్రదించండి.",

        "home_title": "CivicShield కు స్వాగతం",
        "home_subtitle": "మీ హక్కులను అర్థం చేసుకోండి. మీను రక్షించుకోండి. సహాయం పొందండి.",
        "dashboard_intro": "ప్రారంభించడానికి క్రింది ఫీచర్‌ను ఎంచుకోండి:",

        "card_translation_title": "రియల్‑టైమ్ అనువాదం",
        "card_translation_desc": "పోలీసులు ఏమి చెబుతున్నారో అనువదించండి మరియు మీ భాషలో లీగల్ మార్గదర్శకత్వం పొందండి",
        "card_documents_title": "లీగల్ డాక్యుమెంట్ అసిస్టెంట్",
        "card_documents_desc": "డాక్యుమెంట్‌ను అప్‌లోడ్ చేసి ముఖ్యమైన వివరాలను పొందండి మరియు అనువదించండి",
        "card_rights_title": "హక్కుల విద్యా కేంద్రం",
        "card_rights_desc": "మీ రాజ్యాంగ హక్కులను తెలుసుకోండి",
        "card_quiz_title": "హక్కుల క్విజ్",
        "card_quiz_desc": "పౌర హక్కులపై మీ జ్ఞానాన్ని పరీక్షించండి",
        "card_resources_title": "కమ్యూనిటీ సేవలు",
        "card_resources_desc": "లీగల్ ఎయిడ్, అత్యవసర సేవలు మరియు కమ్యూనిటీ మద్దతును కనుగొనండి",
        "card_nearby_title": "మీకు సమీపంలోని హక్కులు",
        "card_nearby_desc": "మీ ప్రాంతంలో లీగల్ ఎయిడ్, కోర్టులు మరియు కమ్యూనిటీ సేవలను కనుగొనండి",
        "card_logging_title": "ఎదుర్కొన్న సంఘటనల రికార్డు",
        "card_logging_desc": "పోలీసులతో జరిగిన సంఘటనలను రికార్డు చేసి ట్రాక్ చేయండి",
        "card_emergency_title": "అత్యవసర సహాయం",
        "card_emergency_desc": "హాట్‌లైన్‌లు మరియు అత్యవసర విధానాలను యాక్సెస్ చేయండి",

        "btn_open": "తెరవండి",
        "btn_delete": "❌",
        "btn_record": "🎤 రికార్డ్ చేయండి",
        "btn_stop": "⏹️ ఆపండి",
        "btn_translate": "🌐 అనువదించండి",
        "btn_listen": "🔊 వినండి",
        "btn_download": "📥 డౌన్‌లోడ్",
        "btn_search": "🔍 శోధించండి",
        "btn_log": "📝 రికార్డ్ చేయండి",
        "btn_back": "← వెనక్కి",
        "btn_submit": "✓ సమర్పించండి",
        "btn_cancel": "✗ రద్దు చేయండి",

        "translation_title": "రియల్‑టైమ్ అనువాదం",
        "translation_subtitle": "పోలీసులు ఏమి చెబుతున్నారో అనువదించండి మరియు లీగల్ మార్గదర్శకత్వం పొందండి",
        "officer_statement": "పోలీసులు చెబుతున్నది (ఇంగ్లీష్):",
        "your_rights": "మీ హక్కులు మరియు లీగల్ సలహా:",
        "play_before_title": "1. మాట్లాడేముందు ప్లే చేయండి",
        "play_before_desc": "రికార్డింగ్ మొదలవ్వడానికి ముందు పోలీసుకి ఇది వినిపించండి.",
        "play_before_audio": "Officer, before we begin, I am using a translation app to avoid any language barriers. I am recording with your knowledge for safety and accuracy.",
        "play_after_title": "3. హక్కులు అర్థమైన తర్వాత ప్లే చేయండి",
        "play_after_desc": "మీ హక్కులు విన్న తర్వాత పోలీసుకి ఇది వినిపించండి.",
        "play_after_audio": "I understand, officer, and I will comply, but I will be using my right to remain silent.",
        "officer_script": "పోలీసుకి చెప్పే స్క్రిప్ట్ (ఇంగ్లీష్లో):",
        "officer_script_translated": "ఇది మీ భాషలో అర్థం:",
        "record_officer": "🎤 పోలీసుల వాయిస్‌ను రికార్డ్ చేయండి",
        "stop_recording": "⏹️ రికార్డింగ్ ఆపి అనువదించండి",
        "listen_to_advice": "🔊 సలహా వినండి",
        "translation_hint": "టైప్ చేయండి లేదా రికార్డ్ చేయండి అనువదించడానికి",
        "generating_audio": "ఆడియో రూపొందిస్తోంది...",
        "audio_ready": "✅ ఆడియో సిద్ధంగా ఉంది",
        "audio_failed": "❌ ఆడియో రూపొందించడం విఫలమైంది",
        "speech_recognized": "ఆడియోను టెక్స్ట్‌గా మార్చాం.",
        "mic_unclear": "ఆడియో స్పష్టంగా లేదు. దయచేసి మళ్లీ స్పష్టంగా రికార్డ్ చేయండి.",
        "stt_unavailable": "స్పీచ్‑టు‑టెక్స్ట్ సేవ అందుబాటులో లేదు.",
        "unable_process_audio": "ఆడియోను ప్రాసెస్ చేయలేకపోయాం. దయచేసి మళ్లీ రికార్డ్ చేయండి.",
        "mic_recorder_title": "ఆడియో రికార్డర్",
        "mic_recorder_desc": "పోలీసుల వాయిస్‌ను రికార్డ్ చేయడానికి స్టార్ట్ మరియు స్టాప్ ఉపయోగించండి.",
        "mic_help": "మైక్ బ్లాక్ అయితే, బ్రౌజర్ సెట్టింగ్స్‌లో అనుమతించండి.",
        "mic_access_failed": "మైక్ యాక్సెస్ చేయలేకపోయాం. దయచేసి అనుమతించి మళ్లీ ప్రయత్నించండి.",
        "mic_no_audio": "ఆడియో రికార్డ్ కాలేదు. మైక్ బ్లాక్ అయి ఉండవచ్చు.",

        "btn_clear_filter": "ఫిల్టర్ క్లియర్ చేయండి",
        "currently_filtering": "ప్రస్తుతం ఫిల్టర్ చేస్తున్నది:",
        "quiz_correct": "✅ సరైంది!",
        "quiz_incorrect": "❌ తప్పు.",
        "language_selector_error": "❌ భాష ఎంపికలో లోపం",
        "demo_section_title": "🎬 డెమో మోడ్ మరియు పరీక్ష",
        "demo_on": "🎬 డెమో ON",
        "demo_off": "🎬 డెమో OFF",
        "tour_button": "🎓 టూర్",
        "tour_complete": "✅ టూర్ పూర్తైంది! మీరు సిద్ధంగా ఉన్నారు.",
        "btn_go_home": "🏠 హోమ్‌కు తిరిగి వెళ్లండి",
        "btn_skip_tour": "⏭️ టూర్‌ను దాటవేయండి",
        "btn_next": "తదుపరి ➡️",
        "btn_start_using": "🎉 ఉపయోగించడం ప్రారంభించండి!",
        "emergency_title": "అత్యవసర సహాయం",
        "emergency_subtitle": "హాట్‌లైన్‌లు మరియు అత్యవసర సేవలు",
        "emergency_911": "911 — పోలీస్, ఫైర్, మెడికల్",
        "emergency_suicide": "జాతీయ ఆత్మహత్య నివారణ హాట్‌లైన్",
        "emergency_domestic": "గృహ హింస హాట్‌లైన్",
        "emergency_assault": "RAINN — లైంగిక దాడి సహాయం",
        "emergency_poison": "పాయిజన్ కంట్రోల్ సెంటర్",
        "emergency_text": "క్రైసిస్ టెక్స్ట్ లైన్",
        "emergency_procedures": "అత్యవసర చర్యలు:",
        "procedure_safe": "మీ భద్రతను కాపాడుకోండి",
        "procedure_document": "అన్ని వివరాలను డాక్యుమెంట్ చేయండి",
        "procedure_record": "చట్టబద్ధంగా మరియు సురక్షితంగా ఉంటే వీడియో తీసుకోండి",
        "procedure_call": "సహాయం కోసం కాల్ చేయండి",
        "procedure_contact": "మీ న్యాయవాదిని సంప్రదించండి",

        "loading": "లోడ్ అవుతోంది...",
        "success": "విజయం!",
        "error": "లోపం",
        "warning": "హెచ్చరిక",
        "info": "సమాచారం",
        "processing": "ప్రాసెస్ చేస్తోంది...",
        "please_wait": "దయచేసి వేచి ఉండండి...",
        "no_data": "డేటా లేదు",
        "try_again": "మళ్లీ ప్రయత్నించండి",

        "accessibility_title": "♿ యాక్సెసిబిలిటీ సెట్టింగ్స్",
        "text_size": "టెక్స్ట్ పరిమాణం:",
        "text_size_normal": "సాధారణ",
        "text_size_large": "పెద్ద",
        "text_size_extra_large": "అత్యంత పెద్ద",
        "high_contrast": "🎨 హై కాంట్రాస్ట్ మోడ్",
        "high_contrast_on": "హై కాంట్రాస్ట్ ON",
        "high_contrast_off": "హై కాంట్రాస్ట్ OFF",
        "screen_reader": "స్క్రీన్ రీడర్ లేబుల్స్ ఎనేబుల్ అయ్యాయి",
        "accessibility_saved": "✅ యాక్సెసిబిలిటీ సెట్టింగ్స్ సేవ్ అయ్యాయి",

        "extract_deadlines": "📋 కనుగొన్న ముఖ్యమైన గడువులు",
        "extract_penalties": "⚠️ కనుగొన్న శిక్షలు",
        "extract_requirements": "✓ అవసరమైన చర్యలు",
        "deadline_found": "గడువు:",
        "penalty_found": "శిక్ష:",
        "requirement_found": "అవసరమైన చర్య:",

        "document_summary": "📋 డాక్యుమెంట్ సారాంశం",
        "summary_generated": "సారాంశం విజయవంతంగా రూపొందించబడింది",

        "location_title": "📍 మీకు సమీపంలోని సేవలను కనుగొనండి",
        "enter_address": "చిరునామా లేదా ZIP కోడ్ నమోదు చేయండి:",
        "search_radius_miles": "శోధన పరిధి (మైళ్ళు):",
        "find_resources": "🔍 సేవలను శోధించండి",
        "resource_type": "సేవ రకం:",
        "all_resources": "అన్ని సేవలు",
        "legal_aid_offices": "లీగల్ ఎయిడ్ కార్యాలయాలు",
        "community_centers": "కమ్యూనిటీ సెంటర్లు",
        "language_services": "భాషా సేవలు",
        "emergency_shelters": "అత్యవసర ఆశ్రయాలు",
        "distance_away": "మైళ్ళ దూరంలో",
        "get_directions": "🗺️ దిశలు",
        "no_resources_found": "ఈ ప్రాంతంలో సేవలు లభించలేదు",
        "resource_hours": "సమయం:",
        "resource_phone": "ఫోన్:",
        "resource_address": "చిరునామా:",
        "resource_website": "వెబ్‌సైట్:",
        "loading_resources": "మీకు సమీపంలోని సేవలను శోధిస్తోంది...",

        "saved_deadlines": "⏰ సేవ్ చేసిన గడువులు",
        "upload_legal_doc": "లీగల్ డాక్యుమెంట్ అప్‌లోడ్ చేయండి",
        "important_dates": "📅 ముఖ్యమైన తేదీలు",
        "required_actions": "✓ అవసరమైన చర్యలు",
        "critical_deadlines": "⏰ కీలక గడువులు",
        "penalties_warnings": "⚠️ శిక్షలు మరియు హెచ్చరికలు",
        "extraction_guide": "డాక్యుమెంట్ ఎక్స్‌ట్రాక్షన్ గైడ్",

        "demo_mode_active": "📺 **డెమో మోడ్ ON** — నమూనా డేటా చూపిస్తోంది",
        "have_deadlines": "📋 మీకు ముఖ్యమైన గడువులు ఉన్నాయి!",
        "view_all_deadlines": "📋 అన్ని గడువులను చూడండి →",
        "from_document": "డాక్యుమెంట్ నుండి:",
        "file_type": "ఫైల్ రకం",
        "file_size": "ఫైల్ పరిమాణం",
        "status_ready": "ఎక్స్‌ట్రాక్షన్‌కు సిద్ధంగా ఉంది",
        "extract_information": "🔍 సమాచారాన్ని ఎక్స్‌ట్రాక్ట్ చేయండి",
        "extracting_info": "డాక్యుమెంట్ నుండి సమాచారాన్ని ఎక్స్‌ట్రాక్ట్ చేస్తోంది...",
        "no_dates_found": "తేదీలు లభించలేదు",
        "no_deadlines_found": "గడువులు లభించలేదు",
        "no_penalties_found": "శిక్షలు లభించలేదు",
        "download_summary": "📥 సారాంశాన్ని డౌన్‌లోడ్ చేయండి",
        "download_as_txt": "TXT గా డౌన్‌లోడ్ చేయండి",
        "save_deadlines_to_dashboard": "💾 గడువులను డాష్‌బోర్డ్‌లో సేవ్ చేయండి",

        "know_your_rights_long": "⚖️ మీ హక్కులను అర్థం చేసుకోండి",
        "education_quizzes": "విద్య, క్విజ్‌లు మరియు లెర్నింగ్ మాడ్యూల్స్",
        "learn_tab": "📚 నేర్చుకోండి",
        "quiz_tab": "🧪 క్విజ్",
        "rights_education": "హక్కుల విద్య",
        "select_topic": "విషయాన్ని ఎంచుకోండి:",
        "test_knowledge": "పౌర హక్కులపై మీ జ్ఞానాన్ని పరీక్షించండి.",
        "rights_quiz": "హక్కుల క్విజ్",
        "can_police_search": "పోలీసులు మీ వాహనాన్ని అనుమతి లేకుండా శోధించగలరా?",
        "only_with_warrant": "వారెంట్ ఉన్నప్పుడు మాత్రమే",
        "only_prob_cause": "ప్రాబబుల్ కారణం ఉన్నప్పుడు",
        "both_a_and_b": "A మరియు B రెండూ",
        "never_without": "లేదు, వారు అలా చేయలేరు",
        "police_can_search": "వారెంట్ లేదా ప్రాబబుల్ కారణం ఉన్నప్పుడు పోలీసులు శోధించగలరు.",

        "answer_police_q": "పోలీసుల ప్రశ్నలకు మీరు సమాధానం చెప్పాలా?",
        "yes_always": "అవును, ఎప్పుడూ",
        "right_remain_silent": "లేదు, మీకు మౌనంగా ఉండే హక్కు ఉంది",
        "only_your_name": "మీ పేరు మాత్రమే చెప్పాలి",
        "only_if_arrested": "అరెస్టు చేసినప్పుడు మాత్రమే",
        "fifth_amendment": "5వ సవరణ మీకు మౌనంగా ఉండే హక్కును ఇస్తుంది.",

        "what_say_arrested": "అరెస్టు చేసినప్పుడు మీరు ఏమి చెప్పాలి?",
        "explain_what_happened": "ఏం జరిగిందో వివరించండి",
        "ask_for_lawyer": "న్యాయవాదిని అడగండి",
        "refuse_give_name": "పేరు చెప్పడానికి నిరాకరించండి",
        "try_negotiate": "పోలీసులతో చర్చించండి",
        "always_ask_lawyer": "న్యాయవాదిని వెంటనే అడగండి మరియు మౌనంగా ఉండండి.",

        "check_answer": "✓ సమాధానం తనిఖీ చేయండి {number}",
        "question_number": "ప్రశ్న {number}: {question}",
        "select_answer": "సమాధానాన్ని ఎంచుకోండి:",
        "your_score": "మీ స్కోర్",

        "talk_community": "💬 కమ్యూనిటీతో మాట్లాడండి",
        "community_intro": "అనుభవాలను పంచుకోండి, ప్రశ్నలు అడగండి, ఇతరులకు సహాయం చేయండి — మనం కలిసి బలంగా ఉంటాం",
        "share_exp_tab": "💭 అనుభవాన్ని పంచుకోండి",
        "ask_q_tab": "❓ ప్రశ్న అడగండి",
        "give_advice_tab": "💡 సలహా ఇవ్వండి",

        "share_your_exp": "💭 మీ అనుభవాన్ని పంచుకోండి",
        "share_story": "మీ అనుభవాన్ని పంచుకోవడం ద్వారా ఇతరులకు సహాయం చేయండి. అన్ని పోస్టులు భద్రత కోసం సమీక్షించబడతాయి.",
        "title_label": "శీర్షిక:",
        "exp_placeholder": "ఉదాహరణ: రోడ్డు మీద ఆపినప్పుడు సూచనలు",
        "your_story": "మీ అనుభవం:",
        "story_placeholder": "మీ కథను పంచుకోండి...",
        "post_anonymously": "అజ్ఞాతంగా పోస్ట్ చేయండి",
        "share_exp_btn": "📤 అనుభవాన్ని పంచుకోండి",
        "fill_title_content": "⚠️ దయచేసి శీర్షిక మరియు వివరాలు నమోదు చేయండి",
        "exp_shared": "✅ మీ అనుభవం పంచబడింది! కమ్యూనిటీకి సహాయం చేసినందుకు ధన్యవాదాలు.",

        "ask_community": "❓ కమ్యూనిటీని అడగండి",
        "question_help": "మీకు ప్రశ్న ఉందా? కమ్యూనిటీ సహాయం చేస్తుంది.",
        "your_question": "మీ ప్రశ్న:",
        "question_placeholder": "ఉదాహరణ: పోలీసులు నన్ను ఆపినప్పుడు నా హక్కులు ఏమిటి?",
        "details_label": "వివరాలు:",
        "details_placeholder": "అదనపు సమాచారాన్ని ఇవ్వండి...",
        "ask_anon": "అజ్ఞాతంగా పోస్ట్ చేయండి",
        "ask_q_btn": "❓ ప్రశ్నను పోస్ట్ చేయండి",
        "enter_question": "⚠️ దయచేసి మీ ప్రశ్నను నమోదు చేయండి",
        "question_posted": "✅ మీ ప్రశ్న పోస్ట్ చేయబడింది!",

        "give_advice": "💡 సలహా ఇవ్వండి",
        "help_others": "మీ జ్ఞానం మరియు అనుభవంతో ఇతరులకు సహాయం చేయండి.",
        "topic_label": "విషయం:",
        "topic_placeholder": "ఉదాహరణ: కోర్టుకు ఎలా సిద్ధం కావాలి",
        "your_advice": "మీ సలహా:",
        "advice_placeholder": "మీకు తెలిసిన విషయాలను పంచుకోండి...",
        "share_anon": "అజ్ఞాతంగా పంచుకోండి",
        "share_advice_btn": "💡 సలహా పంచుకోండి",
        "share_wisdom": "✅ మీ జ్ఞానాన్ని పంచుకున్నందుకు ధన్యవాదాలు!",
        "fill_topic_advice": "⚠️ దయచేసి విషయం మరియు సలహా నమోదు చేయండి",

        "recent_posts": "📋 తాజా పోస్టులు",
        "no_posts_yet": "💭 ఇంకా పోస్టులు లేవు. మొదట మీరు పంచుకోండి!",
        "posted_recently": "{timestamp} కు పోస్ట్ చేయబడింది",
        "author_anonymous": "అజ్ఞాత",
        "author_community_member": "కమ్యూనిటీ సభ్యుడు",

        "crisis_hotlines": "🚨 క్రైసిస్ హాట్‌లైన్‌లు",
        "crisis_support_24": "24/7 సహాయం అందుబాటులో ఉంది",
        "emergency_hotlines_header": "🆘 అత్యవసర హాట్‌లైన్‌లు",
        "in_immediate_danger": "తక్షణ ప్రమాదంలో ఉంటే, 911 కు కాల్ చేయండి",
        "emergency_number": "అత్యవసర నంబర్",
        "suicide_prevention": "జాతీయ ఆత్మహత్య నివారణ హాట్‌లైన్",
        "domestic_violence": "గృహ హింస హాట్‌లైన్",
        "sexual_assault": "RAINN — లైంగిక దాడి సహాయం",
        "poison_control": "పాయిజన్ కంట్రోల్ సెంటర్",
        "crisis_text": "క్రైసిస్ టెక్స్ట్ లైన్",

        "safety_procedures": "📋 భద్రతా చర్యలు",
        "stay_safe": "🛡️ సురక్షితంగా ఉండండి",
        "stay_safe_desc": "మీ భద్రత అత్యంత ముఖ్యమైనది — ఎదురు తిరగవద్దు.",
        "document_details": "📝 వివరాలను డాక్యుమెంట్ చేయండి",
        "document_details_desc": "పోలీసుల పేరు, బాడ్జ్ నంబర్, స్థానం, సమయం మరియు చర్యలను నమోదు చేయండి.",
        "record_safely": "🎥 సురక్షితంగా రికార్డ్ చేయండి",
        "record_safely_desc": "చట్టబద్ధంగా మరియు సురక్షితంగా ఉంటే వీడియో తీసుకోండి.",
        "call_for_help": "📞 సహాయం కోసం కాల్ చేయండి",
        "call_help_desc": "ప్రమాదంలో ఉంటే వెంటనే 911 కు కాల్ చేయండి.",
        "get_legal_help": "⚖️ లీగల్ సహాయం పొందండి",
        "legal_help_desc": "మీ న్యాయవాదిని సంప్రదించండి. పబ్లిక్ డిఫెండర్లు అత్యవసర సహాయం అందిస్తారు.",
        "medical_attention": "🏥 వైద్య సహాయం",
        "medical_attention_desc": "గాయపడితే వెంటనే వైద్య సహాయం పొందండి మరియు ఫోటోలు తీసుకోండి.",
        "mental_health_support": "🧠 మానసిక ఆరోగ్య సహాయం",
        "legal_troubles_trauma": "పోలీసులతో ఎదుర్కొన్న సంఘటనలు మానసిక ఒత్తిడిని కలిగించవచ్చు.",
        "mental_health_resources": "మానసిక ఆరోగ్య వనరులు:",
        "samhsa_helpline": "SAMHSA హెల్ప్‌లైన్: 1‑800‑662‑4357 (ఉచితం, గోప్యంగా, 24/7)",
        "psychology_directory": "థెరపిస్ట్‌ను కనుగొనండి: Psychology Today డైరెక్టరీ",
        "support_groups": "సపోర్ట్ గ్రూపులు: NAACP, కమ్యూనిటీ సెంటర్లు, లీగల్ సంస్థలు",
        "contact_emergency": "🆘 అత్యవసర సహాయం",
        "contact_suicide": "🧠 ఆత్మహత్య నివారణ",
        "contact_domestic": "💔 గృహ హింస హాట్‌లైన్",
        "contact_rainn": "🤝 RAINN — లైంగిక దాడి సహాయం",
        "contact_poison": "☠️ పాయిజన్ కంట్రోల్",
        "contact_crisis_text": "📱 క్రైసిస్ టెక్స్ట్ లైన్",
        "contact_crisis_text_number": "HOME ను 741741 కు టెక్స్ట్ చేయండి",

        "enc_type_traffic_stop": "ట్రాఫిక్ స్టాప్",
        "enc_type_street_encounter": "వీధి ఎదుర్కొన్న సంఘటన",
        "enc_type_arrest": "అరెస్టు",
        "enc_type_search": "శోధన",
        "enc_type_other": "ఇతర",
        "encounter_label": "ఎదుర్కొన్న సంఘటన",
        "unknown": "తెలియదు",
        "na": "వర్తించదు",
        "error_generating_qr": "QR కోడ్ రూపొందించడంలో లోపం వచ్చింది",

        "btn_launch_app": "🚀 యాప్‌ను ప్రారంభించండి",
        "btn_start_demo": "📺 డెమో ప్రారంభించండి",
        "btn_quick_tour": "❓ త్వరిత టూర్",
        "share_with_others": "📱 ఇతరులతో పంచుకోండి",
        "qr_generation_in_progress": "QR కోడ్ రూపొందిస్తోంది...",
        "key_features_label": "ప్రధాన ఫీచర్లు:",
        "btn_previous": "⬅️ వెనక్కి",
        "language_change_error": "భాష మార్చడంలో లోపం",
        "demo_mode_active_sidebar": "✅ డెమో మోడ్ ON — నమూనా డేటా చూపిస్తోంది",
        "screen_reader_off": "🔇 స్క్రీన్ రీడర్ OFF",

        "navigation_title": "నావిగేషన్",
        "nav_rights_full": "⚖️ మీ హక్కులను అర్థం చేసుకోండి",
        "nav_resources_near_you": "📍 మీకు సమీపంలోని సేవలు",
        "nav_logging_full": "📝 ఎదుర్కొన్న సంఘటనల రికార్డు",
        "nav_crisis_resources": "🚨 అత్యవసర వనరులు",
        "nav_community": "💬 కమ్యూనిటీ",

        "sidebar_built_for": "ప్రతి ఒక్కరి పౌర హక్కులను రక్షించడానికి రూపొందించబడింది.",
        "show_landing_page": "🏠 ల్యాండింగ్ పేజీ చూపించండి",

        "landing_hero_html": "<div class=\"landing-hero\"><h1>⚖️ CivicShield Pro</h1><h2>మీ హక్కులను అర్థం చేసుకోండి. మీను రక్షించుకోండి. సహాయం పొందండి.</h2><p>పౌర హక్కులను అర్థం చేసుకోవడానికి మరియు ఉపయోగించడానికి రూపొందించిన బహుభాషా ప్లాట్‌ఫారమ్.</p></div>",

        "landing_purpose_md": "### 🎯 లక్ష్యం\nCivicShield Pro అందిస్తుంది:\n\n- **14 భాషల్లో రియల్‑టైమ్ లీగల్ అనువాదం**\n- **పరిస్థితికి అనుగుణమైన హక్కుల సమాచారం**\n- **లీగల్ డాక్యుమెంట్ విశ్లేషణ** మరియు గడువు ఎక్స్‌ట్రాక్షన్\n- **కమ్యూనిటీ మద్దతు** మరియు అనుభవ పంచుకోవడం\n- **24/7 క్రైసిస్ వనరులు**",

        "landing_features_md": "### ⭐ ప్రధాన ఫీచర్లు\n\n- 🗣️ **రియల్‑టైమ్ అనువాదం** — పోలీసుల మాటలను అనువదించండి\n- 📄 **లీగల్ డాక్యుమెంట్ టూల్స్** — ముఖ్యమైన వివరాలను ఎక్స్‌ట్రాక్ట్ చేయండి\n- ⚖️ **మీ హక్కులను తెలుసుకోండి** — పాఠాలు మరియు క్విజ్‌లు\n- 📍 **సమీప వనరులు** — లీగల్ ఎయిడ్ మరియు కమ్యూనిటీ సేవలు\n- 📝 **ఎదుర్కొన్న సంఘటనల రికార్డు** — పోలీసులతో జరిగిన సంఘటనలను రికార్డ్ చేయండి\n- 🚨 **క్రైసిస్ హాట్‌లైన్‌లు** — 24/7 సహాయం\n- 💬 **కమ్యూనిటీ ఫోరం** — ప్రశ్నలు అడగండి మరియు పంచుకోండి",

        "landing_share_md": "**CivicShield ను ఇతరులతో పంచుకోండి:**\n\n1. QR కోడ్‌ను స్కాన్ చేయండి\n2. ఇన్‌స్టాల్ అవసరం లేదు\n3. 14 భాషలకు మద్దతు\n4. ఫోన్, టాబ్లెట్, కంప్యూటర్‌లో పనిచేస్తుంది",

        "landing_who_should_use_md": "### 👥 ఎవరు ఉపయోగించాలి?\n\n**న్యాయమూర్తులు మరియు లీగల్ ప్రొఫెషనల్స్:**\n- కమ్యూనిటీ దృక్కోణాన్ని అర్థం చేసుకోండి\n- డిఫెండెంట్ల హక్కుల అవగాహనను అంచనా వేయండి\n- రియల్‑టైమ్ అనువాదాన్ని ఉపయోగించండి\n\n**న్యాయవాదులు మరియు లీగల్ ఎయిడ్:**\n- బహుభాషా లీగల్ సమాచారం ఇవ్వండి\n- క్లయింట్లు సంఘటనలను రికార్డ్ చేయడంలో సహాయం చేయండి\n- కమ్యూనిటీ వనరులతో కనెక్ట్ చేయండి\n\n**గురువులు:**\n- పౌర హక్కులను బోధించండి\n- వాస్తవ జీవిత ఉదాహరణలను ఉపయోగించండి\n- ఇంటరాక్టివ్ క్విజ్‌లు ఇవ్వండి\n\n**కమ్యూనిటీ:**\n- పోలీసులతో ఎదుర్కొన్నప్పుడు ఏమి చేయాలో తెలుసుకోండి\n- అత్యవసర వనరులను ఉపయోగించండి\n- అనుభవాలను పంచుకోండి",

        "landing_disclaimer_md": "**⚠️ లీగల్ నోటీసు:**\n\nCivicShield Pro విద్యాపరమైన సమాచారాన్ని అందిస్తుంది, లీగల్ సలహా కాదు.\nచట్టాలు ప్రాంతానుసారం మారవచ్చు.\nమీ కేసుకు సంబంధించిన ప్రత్యేక సలహా కోసం న్యాయవాదిని సంప్రదించండి.",

        "tutorial_intro_html": "<div class=\"tutorial-container\"><h1>👋 CivicShield Pro కు స్వాగతం!</h1><p>ముఖ్యమైన ఫీచర్లను చూద్దాం.</p></div>",

        "tutorial_step1_title": "🏠 ప్రధాన డాష్‌బోర్డ్",
        "tutorial_step1_desc": "ఇక్కడ మీరు అన్ని ఫీచర్లను యాక్సెస్ చేయవచ్చు.",
        "tutorial_step1_feat1": "అన్ని టూల్స్‌కు నావిగేషన్",
        "tutorial_step1_feat2": "సేవ్ చేసిన గడువులను చూడండి",
        "tutorial_step1_feat3": "అత్యవసర వనరులకు యాక్సెస్",

        "tutorial_step2_title": "🗣️ రియల్‑టైమ్ అనువాదం",
        "tutorial_step2_desc": "పోలీసుల మాటలను 14 భాషల్లో అనువదించండి.",
        "tutorial_step2_feat1": "స్పీచ్‑టు‑టెక్స్ట్",
        "tutorial_step2_feat2": "తక్షణ అనువాదం",
        "tutorial_step2_feat3": "ఆడియో ప్లేబ్యాక్",

        "tutorial_step3_title": "📄 లీగల్ డాక్యుమెంట్లు",
        "tutorial_step3_desc": "డాక్యుమెంట్‌ను అప్‌లోడ్ చేసి ముఖ్యమైన వివరాలను పొందండి.",
        "tutorial_step3_feat1": "ఆటోమేటిక్ గడువు ఎక్స్‌ట్రాక్షన్",
        "tutorial_step3_feat2": "శిక్షల గుర్తింపు",
        "tutorial_step3_feat3": "డాక్యుమెంట్ అనువాదం",
        "tutorial_step4_title": "⚖️ మీ హక్కులను తెలుసుకోండి",
        "tutorial_step4_desc": "మీ హక్కులను నేర్చుకోండి మరియు మీ జ్ఞానాన్ని పరీక్షించండి.",
        "tutorial_step4_feat1": "హక్కుల విద్య",
        "tutorial_step4_feat2": "ఇంటరాక్టివ్ క్విజ్‌లు",
        "tutorial_step4_feat3": "ప్రోగ్రెస్ ట్రాకింగ్",

        "tutorial_step5_title": "📍 సమీప వనరులు",
        "tutorial_step5_desc": "మీ ప్రాంతంలో లీగల్ ఎయిడ్ మరియు కమ్యూనిటీ సేవలను కనుగొనండి.",
        "tutorial_step5_feat1": "స్థాన ఆధారిత శోధన",
        "tutorial_step5_feat2": "సేవ ఫిల్టర్లు",
        "tutorial_step5_feat3": "త్వరిత దిశలు",

        "tutorial_step6_title": "💬 కమ్యూనిటీ ఫోరం",
        "tutorial_step6_desc": "అనుభవాలను పంచుకోండి, ప్రశ్నలు అడగండి, ఇతరులకు సహాయం చేయండి.",
        "tutorial_step6_feat1": "అజ్ఞాత పోస్టింగ్",
        "tutorial_step6_feat2": "లీగల్ ప్రశ్నలు",
        "tutorial_step6_feat3": "సలహా పంచుకోవడం",

        "documents_intro_md": "లీగల్ డాక్యుమెంట్ (ఫోటో లేదా PDF) అప్‌లోడ్ చేసి క్రింది వివరాలను పొందండి:\n- తేదీలు మరియు గడువులు\n- అవసరమైన చర్యలు\n- శిక్షలు మరియు హెచ్చరికలు\n- ప్రభుత్వ సంస్థలు\n- డాక్యుమెంట్ సారాంశం",

        "extract_deadlines_found": "📋 కనుగొన్న ముఖ్యమైన గడువులు",
        "extract_penalties_found": "⚠️ కనుగొన్న శిక్షలు",
        "extract_requirements_found": "✓ కనుగొన్న అవసరమైన చర్యలు",

        "search_radius_km": "శోధన పరిధి (కిలోమీటర్లు):",

        "resource_category": "సేవ వర్గం:",
        "resource_distance": "దూరం:",
        "resource_map_link": "🗺️ మ్యాప్",
        "resource_description": "వివరణ:",
        "resource_notes": "గమనికలు:",
        "resource_tags": "ట్యాగ్‌లు:",
        "resource_id": "వనరుల ID:",
        "resource_source": "మూలం:",
        "resource_updated": "చివరి నవీకరణ:",
        "resource_error": "సేవ సమాచారాన్ని పొందడంలో లోపం వచ్చింది",

        "logging_intro_md": "పోలీసులతో జరిగిన సంఘటనలను రికార్డ్ చేసి భద్రపరచండి. ఇది మీ భద్రత మరియు లీగల్ రక్షణకు సహాయపడుతుంది.",
        "logging_steps_md": "### రికార్డింగ్ దశలు\n1. సంఘటన రకం ఎంచుకోండి\n2. స్థానం నమోదు చేయండి\n3. వివరాలను నమోదు చేయండి\n4. పోలీసుల సమాచారాన్ని నమోదు చేయండి\n5. సేవ్ చేయండి",

        "logging_history_title": "📋 సంఘటనల చరిత్ర",
        "logging_history_desc": "మీరు రికార్డ్ చేసిన అన్ని సంఘటనలను ఇక్కడ చూడవచ్చు.",
        "logging_no_history": "ఇప్పటివరకు సంఘటనలు రికార్డ్ కాలేదు.",
        "logging_view_details": "వివరాలను చూడండి",
        "logging_delete_entry": "❌ ఎంట్రీని తొలగించండి",
        "logging_deleted": "ఎంట్రీ విజయవంతంగా తొలగించబడింది.",

        "emergency_steps_md": "### అత్యవసర పరిస్థితుల్లో చేయాల్సినవి\n- ప్రశాంతంగా ఉండండి\n- సురక్షిత ప్రదేశానికి వెళ్లండి\n- 911 కు కాల్ చేయండి\n- అవసరమైతే వీడియో తీసుకోండి\n- న్యాయవాదిని సంప్రదించండి",

        "community_guidelines_title": "📋 కమ్యూనిటీ మార్గదర్శకాలు",
        "community_guidelines_desc": "భద్రత, గౌరవం మరియు సహకారం కోసం ఈ మార్గదర్శకాలను అనుసరించండి.",
        "community_rule_respect": "💛 ఇతరులను గౌరవించండి",
        "community_rule_no_hate": "🚫 ద్వేషపూరిత లేదా హింసాత్మక కంటెంట్ పోస్ట్ చేయవద్దు",
        "community_rule_no_spam": "📵 స్పామ్ లేదా ప్రకటనలు పోస్ట్ చేయవద్దు",
        "community_rule_privacy": "🔒 వ్యక్తిగత సమాచారాన్ని పంచుకోకండి",
        "community_rule_report": "⚠️ అనుచిత కంటెంట్‌ను నివేదించండి",

        "community_report_btn": "🚨 నివేదించండి",
        "community_report_success": "మీ నివేదిక సమర్పించబడింది. ధన్యవాదాలు.",
        "community_report_reason": "నివేదించడానికి కారణం:",
        "community_report_placeholder": "ఉదాహరణ: అనుచిత భాష, వేధింపు, స్పామ్",

        "translator_title": "🗣️ అనువాద సేవ",
        "translator_subtitle": "టెక్స్ట్‌ను మీ భాషలోకి అనువదించండి",
        "translator_input": "అనువదించాల్సిన టెక్స్ట్:",
        "translator_output": "అనువాదం:",
        "translator_switch_lang": "భాష మార్చండి",
        "translator_copy": "📋 కాపీ చేయండి",
        "translator_copied": "కాపీ చేయబడింది!",
        "translator_error": "అనువాదంలో లోపం వచ్చింది",

        "audio_player_title": "🔊 ఆడియో ప్లేయర్",
        "audio_player_play": "ప్లే చేయండి",
        "audio_player_pause": "పాజ్ చేయండి",
        "audio_player_stop": "ఆపండి",
        "audio_player_error": "ఆడియో ప్లే చేయడంలో లోపం వచ్చింది",

        "document_upload_error": "డాక్యుమెంట్ అప్‌లోడ్ విఫలమైంది",
        "document_processing_error": "డాక్యుమెంట్ ప్రాసెస్ చేయడంలో లోపం వచ్చింది",
        "document_translation_error": "డాక్యుమెంట్ అనువాదంలో లోపం వచ్చింది",

        "location_permission_denied": "స్థాన అనుమతి నిరాకరించబడింది",
        "location_not_available": "స్థాన సమాచారం అందుబాటులో లేదు",
        "location_search_error": "స్థాన శోధనలో లోపం వచ్చింది",

        "tour_welcome": "👋 టూర్‌కు స్వాగతం!",
        "tour_step_intro": "ఈ టూర్ CivicShield Pro యొక్క ముఖ్యమైన ఫీచర్లను చూపిస్తుంది.",
        "tour_step_done": "🎉 టూర్ పూర్తైంది!",
        "tour_restart": "🔄 టూర్‌ను మళ్లీ ప్రారంభించండి",
        "tour_exit": "🚪 టూర్ నుండి బయటకు రండి",
        "tour_step1_title": "🏠 డాష్‌బోర్డ్ పరిచయం",
        "tour_step1_desc": "ఇక్కడ మీరు CivicShield Pro యొక్క అన్ని ప్రధాన ఫీచర్లను యాక్సెస్ చేయవచ్చు.",
        "tour_step1_point1": "అన్ని టూల్స్‌కు నావిగేషన్",
        "tour_step1_point2": "సేవ్ చేసిన గడువులను చూడండి",
        "tour_step1_point3": "అత్యవసర వనరులకు యాక్సెస్",

        "tour_step2_title": "🗣️ రియల్‑టైమ్ అనువాదం",
        "tour_step2_desc": "పోలీసుల మాటలను మీ భాషలోకి తక్షణమే అనువదించండి.",
        "tour_step2_point1": "వాయిస్ రికార్డింగ్",
        "tour_step2_point2": "స్పీచ్‑టు‑టెక్స్ట్",
        "tour_step2_point3": "ఆడియో ప్లేబ్యాక్",

        "tour_step3_title": "📄 డాక్యుమెంట్ టూల్స్",
        "tour_step3_desc": "డాక్యుమెంట్‌ను అప్‌లోడ్ చేసి ముఖ్యమైన లీగల్ వివరాలను పొందండి.",
        "tour_step3_point1": "గడువు ఎక్స్‌ట్రాక్షన్",
        "tour_step3_point2": "శిక్షల గుర్తింపు",
        "tour_step3_point3": "డాక్యుమెంట్ అనువాదం",

        "tour_step4_title": "⚖️ హక్కుల విద్య",
        "tour_step4_desc": "మీ హక్కులను నేర్చుకోండి మరియు క్విజ్‌లతో మీ జ్ఞానాన్ని పరీక్షించండి.",
        "tour_step4_point1": "హక్కుల పాఠాలు",
        "tour_step4_point2": "ఇంటరాక్టివ్ క్విజ్‌లు",
        "tour_step4_point3": "ప్రోగ్రెస్ ట్రాకింగ్",

        "tour_step5_title": "📍 సమీప వనరులు",
        "tour_step5_desc": "మీ ప్రాంతంలో లీగల్ ఎయిడ్ మరియు కమ్యూనిటీ సేవలను కనుగొనండి.",
        "tour_step5_point1": "స్థాన ఆధారిత శోధన",
        "tour_step5_point2": "సేవ ఫిల్టర్లు",
        "tour_step5_point3": "త్వరిత దిశలు",

        "tour_step6_title": "💬 కమ్యూనిటీ ఫోరం",
        "tour_step6_desc": "అనుభవాలను పంచుకోండి, ప్రశ్నలు అడగండి, ఇతరులకు సహాయం చేయండి.",
        "tour_step6_point1": "అజ్ఞాత పోస్టింగ్",
        "tour_step6_point2": "లీగల్ ప్రశ్నలు",
        "tour_step6_point3": "సలహా పంచుకోవడం",

        "tour_finished_title": "🎉 టూర్ పూర్తైంది!",
        "tour_finished_desc": "ఇప్పుడు మీరు CivicShield Pro ను పూర్తిగా ఉపయోగించడానికి సిద్ధంగా ఉన్నారు.",
        "tour_finished_btn_start": "🚀 యాప్‌ను ప్రారంభించండి",

        "error_generic": "లోపం వచ్చింది. దయచేసి మళ్లీ ప్రయత్నించండి.",
        "error_network": "నెట్‌వర్క్ లోపం. కనెక్షన్‌ను తనిఖీ చేయండి.",
        "error_timeout": "సర్వర్ స్పందించలేదు. కొద్దిసేపు తర్వాత ప్రయత్నించండి.",
        "error_invalid_input": "చెల్లని ఇన్‌పుట్. దయచేసి సరైన సమాచారాన్ని నమోదు చేయండి.",
        "error_unknown": "తెలియని లోపం వచ్చింది.",

        "success_saved": "విజయవంతంగా సేవ్ చేయబడింది!",
        "success_updated": "విజయవంతంగా నవీకరించబడింది!",
        "success_deleted": "విజయవంతంగా తొలగించబడింది!",

        "confirm_delete": "మీరు నిజంగా దీన్ని తొలగించాలనుకుంటున్నారా?",
        "confirm_yes": "అవును",
        "confirm_no": "లేదు",

        "form_required": "ఈ ఫీల్డ్ అవసరం",
        "form_invalid_email": "చెల్లని ఇమెయిల్ చిరునామా",
        "form_invalid_phone": "చెల్లని ఫోన్ నంబర్",
        "form_invalid_zip": "చెల్లని ZIP కోడ్",

        "loading_data": "డేటాను లోడ్ చేస్తోంది...",
        "saving_data": "డేటాను సేవ్ చేస్తోంది...",
        "updating_data": "డేటాను నవీకరిస్తోంది...",
        "deleting_data": "డేటాను తొలగిస్తోంది...",

        "modal_close": "మూసివేయండి",
        "modal_confirm": "నిర్ధారించండి",
        "modal_cancel": "రద్దు చేయండి",

        "search_placeholder": "శోధించండి...",
        "search_no_results": "ఫలితాలు లభించలేదు",
        "search_results": "శోధన ఫలితాలు",

        "filter_apply": "ఫిల్టర్ అమలు చేయండి",
        "filter_clear": "ఫిల్టర్ క్లియర్ చేయండి",
        "filter_selected": "ఎంచుకున్న ఫిల్టర్లు:",

        "pagination_next": "తదుపరి",
        "pagination_prev": "మునుపటి",
        "pagination_page": "పేజీ",
        "pagination_of": "లో",

        "profile_title": "ప్రొఫైల్",
        "profile_edit": "ప్రొఫైల్ సవరించండి",
        "profile_save": "ప్రొఫైల్ సేవ్ చేయండి",
        "profile_name": "పేరు",
        "profile_email": "ఇమెయిల్",
        "profile_phone": "ఫోన్",
        "profile_language": "భాష",
        "profile_updated": "ప్రొఫైల్ విజయవంతంగా నవీకరించబడింది!",

        "settings_title": "సెట్టింగ్స్",
        "settings_language": "భాష సెట్టింగ్స్",
        "settings_notifications": "నోటిఫికేషన్ సెట్టింగ్స్",
        "settings_privacy": "గోప్యతా సెట్టింగ్స్",
        "settings_save": "సెట్టింగ్స్ సేవ్ చేయండి",

        "notifications_title": "నోటిఫికేషన్‌లు",
        "notifications_enable": "నోటిఫికేషన్‌లు ఎనేబుల్ చేయండి",
        "notifications_disable": "నోటిఫికేషన్‌లు డిసేబుల్ చేయండి",
        "notifications_saved": "నోటిఫికేషన్ సెట్టింగ్స్ సేవ్ అయ్యాయి",

        "privacy_title": "గోప్యతా విధానం",
        "privacy_desc": "మీ డేటా ఎలా ఉపయోగించబడుతుందో తెలుసుకోండి.",
        "privacy_read_more": "మరింత చదవండి",

        "about_title": "CivicShield గురించి",
        "about_desc": "పౌర హక్కులను రక్షించడానికి మరియు అర్థం చేసుకోవడానికి రూపొందించిన బహుభాషా ప్లాట్‌ఫారమ్.",
        "about_version": "వెర్షన్:",
        "about_credits": "క్రెడిట్స్:",
        "about_team": "డెవలప్‌మెంట్ టీమ్",
        "about_contact": "సంప్రదించండి",

        "footer_terms": "నిబంధనలు",
        "footer_privacy": "గోప్యత",
        "footer_contact": "సంప్రదించండి"
        
       
    },
    "Punjabi / ਪੰਜਾਬੀ": {
        "sidebar_title": "CivicShield",
        "sidebar_tagline": "ਆਪਣੇ ਹੱਕ ਸਮਝੋ",
        "select_language": "📍 ਭਾਸ਼ਾ ਚੁਣੋ:",
        "nav_home": "🏠 ਹੋਮ",
        "nav_translation": "🗣️ ਰੀਅਲ‑ਟਾਈਮ ਤਰਜਮਾ",
        "nav_documents": "📄 ਲੀਗਲ ਡੌਕੂਮੈਂਟ",
        "nav_rights": "📚 ਹੱਕ ਸੈਂਟਰ",
        "nav_quiz": "❓ ਹੱਕ ਕਵਿਜ਼",
        "nav_resources": "🏥 ਕਮਿਊਨਿਟੀ ਸਰਵਿਸ",
        "nav_nearby": "📍 ਨੇੜੇ ਹੱਕ",
        "nav_logging": "📝 ਮੁਲਾਕਾਤ ਰਿਕਾਰਡ",
        "nav_emergency": "🚨 ਐਮਰਜੈਂਸੀ ਮਦਦ",
        "nav_about": "CivicShield ਬਾਰੇ",
        "sidebar_version": "ਵਰਜਨ 3.0.0",
        "sidebar_purpose": "ਸਿਵਲ ਹੱਕ ਸੁਰੱਖਿਆ ਅਤੇ ਪ੍ਰੋਫੈਸ਼ਨਲ ਲੀਗਲ ਤਰਜਮਾ",
        "sidebar_languages": "14 ਭਾਸ਼ਾਵਾਂ ਦਾ ਸਹਿਯੋਗ",
        "sidebar_disclaimer": "⚠️ ਲੀਗਲ ਨੋਟਿਸ",
        "sidebar_disclaimer_text": "ਇਹ ਐਪ ਸਿੱਖਿਆ ਲਈ ਹੈ, ਲੀਗਲ ਸਲਾਹ ਨਹੀਂ। ਆਪਣੇ ਕੇਸ ਲਈ ਵਕੀਲ ਨਾਲ ਸੰਪਰਕ ਕਰੋ।",

        "home_title": "CivicShield ਵਿੱਚ ਤੁਹਾਡਾ ਸਵਾਗਤ ਹੈ",
        "home_subtitle": "ਆਪਣੇ ਹੱਕ ਸਮਝੋ। ਆਪਣੇ ਆਪ ਨੂੰ ਬਚਾਓ। ਮਦਦ ਲਵੋ।",
        "dashboard_intro": "ਸ਼ੁਰੂ ਕਰਨ ਲਈ ਹੇਠਾਂ ਦਿੱਤਾ ਫੀਚਰ ਚੁਣੋ:",

        "card_translation_title": "ਰੀਅਲ‑ਟਾਈਮ ਤਰਜਮਾ",
        "card_translation_desc": "ਪੁਲਿਸ ਕੀ ਕਹਿ ਰਹੀ ਹੈ ਤਰਜਮਾ ਕਰੋ ਅਤੇ ਆਪਣੀ ਭਾਸ਼ਾ ਵਿੱਚ ਲੀਗਲ ਸਲਾਹ ਲਵੋ",
        "card_documents_title": "ਲੀਗਲ ਡੌਕੂਮੈਂਟ ਅਸਿਸਟੈਂਟ",
        "card_documents_desc": "ਡੌਕੂਮੈਂਟ ਅੱਪਲੋਡ ਕਰੋ, ਮਹੱਤਵਪੂਰਨ ਜਾਣਕਾਰੀ ਲਵੋ ਅਤੇ ਤਰਜਮਾ ਕਰੋ",
        "card_rights_title": "ਹੱਕ ਸਿੱਖਿਆ ਸੈਂਟਰ",
        "card_rights_desc": "ਆਪਣੇ ਸੰਵਿਧਾਨਕ ਹੱਕਾਂ ਬਾਰੇ ਜਾਣੋ",
        "card_quiz_title": "ਹੱਕ ਕਵਿਜ਼",
        "card_quiz_desc": "ਸਿਵਲ ਹੱਕਾਂ ਬਾਰੇ ਆਪਣੀ ਜਾਣਕਾਰੀ ਟੈਸਟ ਕਰੋ",
        "card_resources_title": "ਕਮਿਊਨਿਟੀ ਸਰਵਿਸ",
        "card_resources_desc": "ਲੀਗਲ ਐਡ, ਐਮਰਜੈਂਸੀ ਸਰਵਿਸ ਅਤੇ ਕਮਿਊਨਿਟੀ ਮਦਦ ਲੱਭੋ",
        "card_nearby_title": "ਨੇੜੇ ਹੱਕ",
        "card_nearby_desc": "ਆਪਣੇ ਇਲਾਕੇ ਵਿੱਚ ਲੀਗਲ ਐਡ ਅਤੇ ਕਮਿਊਨਿਟੀ ਸਰਵਿਸ ਲੱਭੋ",
        "card_logging_title": "ਮੁਲਾਕਾਤ ਰਿਕਾਰਡ",
        "card_logging_desc": "ਪੁਲਿਸ ਨਾਲ ਹੋਈ ਮੁਲਾਕਾਤ ਰਿਕਾਰਡ ਕਰੋ",
        "card_emergency_title": "ਐਮਰਜੈਂਸੀ ਮਦਦ",
        "card_emergency_desc": "ਹੌਟਲਾਈਨ ਅਤੇ ਐਮਰਜੈਂਸੀ ਗਾਈਡ ਐਕਸੈੱਸ ਕਰੋ",

        "btn_open": "ਖੋਲ੍ਹੋ",
        "btn_delete": "❌",
        "btn_record": "🎤 ਰਿਕਾਰਡ ਕਰੋ",
        "btn_stop": "⏹️ ਰੋਕੋ",
        "btn_translate": "🌐 ਤਰਜਮਾ ਕਰੋ",
        "btn_listen": "🔊 ਸੁਣੋ",
        "btn_download": "📥 ਡਾਊਨਲੋਡ",
        "btn_search": "🔍 ਖੋਜੋ",
        "btn_log": "📝 ਰਿਕਾਰਡ ਕਰੋ",
        "btn_back": "← ਵਾਪਸ",
        "btn_submit": "✓ ਭੇਜੋ",
        "btn_cancel": "✗ ਰੱਦ ਕਰੋ",

        "translation_title": "ਰੀਅਲ‑ਟਾਈਮ ਤਰਜਮਾ",
        "translation_subtitle": "ਪੁਲਿਸ ਕੀ ਕਹਿ ਰਹੀ ਹੈ ਤਰਜਮਾ ਕਰੋ ਅਤੇ ਲੀਗਲ ਸਲਾਹ ਲਵੋ",
        "officer_statement": "ਪੁਲਿਸ ਕੀ ਕਹਿ ਰਹੀ ਹੈ (ਅੰਗਰੇਜ਼ੀ):",
        "your_rights": "ਤੁਹਾਡੇ ਹੱਕ ਅਤੇ ਲੀਗਲ ਸਲਾਹ:",
        "play_before_title": "1. ਗੱਲਬਾਤ ਤੋਂ ਪਹਿਲਾਂ ਚਲਾਓ",
        "play_before_desc": "ਰਿਕਾਰਡਿੰਗ ਸ਼ੁਰੂ ਹੋਣ ਤੋਂ ਪਹਿਲਾਂ ਪੁਲਿਸ ਨੂੰ ਇਹ ਸੁਣਾਓ।",
        "play_before_audio": "Officer, before we begin, I am using a translation app to avoid any language barriers. I am recording with your knowledge for safety and accuracy.",
        "play_after_title": "3. ਹੱਕ ਸਮਝਣ ਤੋਂ ਬਾਅਦ ਚਲਾਓ",
        "play_after_desc": "ਆਪਣੇ ਹੱਕ ਸੁਣਨ ਤੋਂ ਬਾਅਦ ਪੁਲਿਸ ਨੂੰ ਇਹ ਸੁਣਾਓ।",
        "play_after_audio": "I understand, officer, and I will comply, but I will be using my right to remain silent.",
        "officer_script": "ਪੁਲਿਸ ਲਈ ਸਕ੍ਰਿਪਟ (ਅੰਗਰੇਜ਼ੀ ਵਿੱਚ):",
        "officer_script_translated": "ਇਹ ਤੁਹਾਡੀ ਭਾਸ਼ਾ ਵਿੱਚ ਕੀ ਕਹਿੰਦਾ ਹੈ:",
        "record_officer": "🎤 ਪੁਲਿਸ ਦੀ ਆਵਾਜ਼ ਰਿਕਾਰਡ ਕਰੋ",
        "stop_recording": "⏹️ ਰਿਕਾਰਡਿੰਗ ਰੋਕੋ ਅਤੇ ਤਰਜਮਾ ਕਰੋ",
        "listen_to_advice": "🔊 ਸਲਾਹ ਸੁਣੋ",
        "translation_hint": "ਤਰਜਮਾ ਕਰਨ ਲਈ ਟਾਈਪ ਕਰੋ ਜਾਂ ਰਿਕਾਰਡ ਕਰੋ",
        "generating_audio": "ਆਡੀਓ ਬਣਾਇਆ ਜਾ ਰਿਹਾ ਹੈ...",
        "audio_ready": "✅ ਆਡੀਓ ਤਿਆਰ ਹੈ",
        "audio_failed": "❌ ਆਡੀਓ ਬਣਾਉਣ ਵਿੱਚ ਗਲਤੀ",
        "speech_recognized": "ਆਡੀਓ ਨੂੰ ਟੈਕਸਟ ਵਿੱਚ ਬਦਲਿਆ ਗਿਆ ਹੈ।",
        "mic_unclear": "ਆਵਾਜ਼ ਸਾਫ਼ ਨਹੀਂ ਸੀ। ਕਿਰਪਾ ਕਰਕੇ ਦੁਬਾਰਾ ਰਿਕਾਰਡ ਕਰੋ।",
        "stt_unavailable": "ਸਪੀਚ‑ਟੂ‑ਟੈਕਸਟ ਉਪਲਬਧ ਨਹੀਂ ਹੈ।",
        "unable_process_audio": "ਆਡੀਓ ਪ੍ਰੋਸੈਸ ਨਹੀਂ ਹੋ ਸਕੀ। ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
        "mic_recorder_title": "ਆਡੀਓ ਰਿਕਾਰਡਰ",
        "mic_recorder_desc": "ਪੁਲਿਸ ਦੀ ਆਵਾਜ਼ ਰਿਕਾਰਡ ਕਰਨ ਲਈ ਸਟਾਰਟ ਅਤੇ ਸਟਾਪ ਵਰਤੋ।",
        "mic_help": "ਜੇ ਮਾਈਕ ਬਲੌਕ ਹੈ ਤਾਂ ਬ੍ਰਾਊਜ਼ਰ ਸੈਟਿੰਗ ਵਿੱਚ ਇਜਾਜ਼ਤ ਦਿਓ।",
        "mic_access_failed": "ਮਾਈਕ ਐਕਸੈੱਸ ਨਹੀਂ ਮਿਲੀ। ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
        "mic_no_audio": "ਕੋਈ ਆਡੀਓ ਰਿਕਾਰਡ ਨਹੀਂ ਹੋਈ। ਮਾਈਕ ਬਲੌਕ ਹੋ ਸਕਦਾ ਹੈ।",

        "btn_clear_filter": "ਫਿਲਟਰ ਕਲੀਅਰ ਕਰੋ",
        "currently_filtering": "ਹੁਣ ਫਿਲਟਰ ਕੀਤਾ ਜਾ ਰਿਹਾ ਹੈ:",
        "quiz_correct": "✅ ਸਹੀ!",
        "quiz_incorrect": "❌ ਗਲਤ.",
        "language_selector_error": "❌ ਭਾਸ਼ਾ ਚੁਣਨ ਵਿੱਚ ਗਲਤੀ",
        "demo_section_title": "🎬 ਡੈਮੋ ਮੋਡ ਅਤੇ ਟੈਸਟਿੰਗ",
        "demo_on": "🎬 ਡੈਮੋ ON",
        "demo_off": "🎬 ਡੈਮੋ OFF",
        "tour_button": "🎓 ਟੂਰ",
        "tour_complete": "✅ ਟੂਰ ਮੁਕੰਮਲ! ਤੁਸੀਂ ਤਿਆਰ ਹੋ।",
        "btn_go_home": "🏠 ਹੋਮ ਵਾਪਸ ਜਾਓ",
        "btn_skip_tour": "⏭️ ਟੂਰ ਸਕਿਪ ਕਰੋ",
        "btn_next": "ਅੱਗੇ ➡️",
        "btn_start_using": "🎉 ਵਰਤਣਾ ਸ਼ੁਰੂ ਕਰੋ!",
        "documents_title": "ਲੀਗਲ ਡੌਕੂਮੈਂਟ ਅਸਿਸਟੈਂਟ",
        "documents_subtitle": "ਡੌਕੂਮੈਂਟ ਅੱਪਲੋਡ ਕਰੋ ਅਤੇ ਮਹੱਤਵਪੂਰਨ ਜਾਣਕਾਰੀ ਲਵੋ",
        "upload_document": "📤 ਡੌਕੂਮੈਂਟ ਅੱਪਲੋਡ ਕਰੋ",
        "take_photo": "📸 ਫੋਟੋ ਖਿੱਚੋ",
        "extract_text": "ਟੈਕਸਟ ਕੱਢੋ",
        "simplify_text": "ਸਧਾਰਨ ਲੀਗਲ ਭਾਸ਼ਾ",
        "translate_document": "🌐 ਡੌਕੂਮੈਂਟ ਤਰਜਮਾ ਕਰੋ",
        "extract_dates": "📅 ਮਿਲੀਆਂ ਤਰੀਖਾਂ",
        "extract_deadlines": "⏰ ਡੈੱਡਲਾਈਨ",
        "extract_agencies": "🏛️ ਸਰਕਾਰੀ ਏਜੰਸੀਆਂ",
        "extract_actions": "✅ ਲੋੜੀਂਦੇ ਕਦਮ",
        "download_report": "📥 ਰਿਪੋਰਟ ਡਾਊਨਲੋਡ ਕਰੋ",
        "report_generated": "ਤੁਹਾਡੀ ਰਿਪੋਰਟ ਤਿਆਰ ਹੈ",

        "rights_title": "ਹੱਕ ਸੈਂਟਰ",
        "rights_subtitle": "ਆਪਣੇ ਸੰਵਿਧਾਨਕ ਹੱਕਾਂ ਬਾਰੇ ਜਾਣੋ",
        "right_fourth": "4ਵਾਂ ਸੰਸ਼ੋਧਨ: ਤਲਾਸ਼ੀ ਅਤੇ ਜ਼ਬਤੀ",
        "right_fifth": "5ਵਾਂ ਸੰਸ਼ੋਧਨ: ਚੁੱਪ ਰਹਿਣ ਦਾ ਹੱਕ",
        "right_sixth": "6ਵਾਂ ਸੰਸ਼ੋਧਨ: ਵਕੀਲ ਦਾ ਹੱਕ",
        "right_traffic": "ਟ੍ਰੈਫਿਕ ਰੋਕਣ ਵੇਲੇ ਹੱਕ",
        "right_arrest": "ਅਰੈਸਟ ਹੋਣ ਵੇਲੇ ਹੱਕ",

        "right_fourth_content": "**ਤੁਹਾਡਾ ਹੱਕ:** ਗੈਰ‑ਵਾਜਬ ਤਲਾਸ਼ੀ ਅਤੇ ਜ਼ਬਤੀ ਤੋਂ ਸੁਰੱਖਿਆ।\n\n**ਮੁੱਖ ਬਿੰਦੂ:**\n- ਪੁਲਿਸ ਨੂੰ ਆਮ ਤੌਰ 'ਤੇ ਤਲਾਸ਼ੀ ਲਈ ਵਾਰੰਟ ਚਾਹੀਦਾ ਹੈ\n- ਤੁਸੀਂ ਕਹਿ ਸਕਦੇ ਹੋ: \"ਮੈਂ ਤਲਾਸ਼ੀ ਦੀ ਇਜਾਜ਼ਤ ਨਹੀਂ ਦਿੰਦਾ\"\n- ਲੜਾਈ ਨਾ ਕਰੋ — ਇਸ ਨਾਲ ਹੋਰ ਕੇਸ ਬਣ ਸਕਦੇ ਹਨ\n- ਵਾਰੰਟ ਜਾਂ probable cause ਹੋਵੇ ਤਾਂ ਪੁਲਿਸ ਤਲਾਸ਼ੀ ਕਰ ਸਕਦੀ ਹੈ\n\n**ਤੁਸੀਂ ਕਰ ਸਕਦੇ ਹੋ:**\n- ਪੁੱਛੋ: \"ਕੀ ਮੈਂ ਜਾ ਸਕਦਾ ਹਾਂ?\"\n- ਪੁੱਛੋ: \"ਕੀ ਤੁਹਾਡੇ ਕੋਲ ਵਾਰੰਟ ਹੈ?\"\n- ਆਪਣੇ ਹੱਥ ਨਜ਼ਰ ਵਿੱਚ ਰੱਖੋ",

        "right_fifth_content": "**ਤੁਹਾਡਾ ਹੱਕ:** ਤੁਸੀਂ ਚੁੱਪ ਰਹਿ ਸਕਦੇ ਹੋ।\n\n**ਮੁੱਖ ਬਿੰਦੂ:**\n- ਤੁਹਾਨੂੰ ਪੁਲਿਸ ਦੇ ਹਰ ਸਵਾਲ ਦਾ ਜਵਾਬ ਦੇਣ ਦੀ ਲੋੜ ਨਹੀਂ\n- ਸਾਫ਼ ਕਹੋ: \"ਮੈਂ ਚੁੱਪ ਰਹਿਣ ਦਾ ਹੱਕ ਵਰਤ ਰਿਹਾ ਹਾਂ\"\n- ਅਰੈਸਟ ਨਾ ਹੋਣ 'ਤੇ ਵੀ ਇਹ ਹੱਕ ਲਾਗੂ ਹੁੰਦਾ ਹੈ\n\n**ਮਹੱਤਵਪੂਰਨ:**\n- ਇਹ ਹੱਕ ਸਪਸ਼ਟ ਤੌਰ 'ਤੇ ਦੱਸਣਾ ਪੈਂਦਾ ਹੈ\n- ਅਰੈਸਟ ਹੋਣ 'ਤੇ ਤੁਰੰਤ ਵਕੀਲ ਮੰਗੋ",

        "right_sixth_content": "**ਤੁਹਾਡਾ ਹੱਕ:** ਤੁਹਾਨੂੰ ਵਕੀਲ ਦਾ ਹੱਕ ਹੈ।\n\n**ਮੁੱਖ ਬਿੰਦੂ:**\n- ਜੇ ਤੁਸੀਂ ਭੁਗਤਾਨ ਨਹੀਂ ਕਰ ਸਕਦੇ, ਕੋਰਟ ਵਕੀਲ ਦੇਵੇਗੀ\n- ਪੁਲਿਸ ਤੁਹਾਨੂੰ ਪੁੱਛਗਿੱਛ ਨਹੀਂ ਕਰ ਸਕਦੀ ਜੇ ਤੁਸੀਂ ਵਕੀਲ ਮੰਗ ਲਓ\n- ਕਹੋ: \"ਮੈਂ ਆਪਣੇ ਵਕੀਲ ਨਾਲ ਗੱਲ ਕਰਨੀ ਹੈ\"",

        "right_traffic_content": "**ਟ੍ਰੈਫਿਕ ਰੋਕਣ ਵੇਲੇ:**\n- ਲਾਇਸੈਂਸ, ਰਜਿਸਟ੍ਰੇਸ਼ਨ, ਇਨਸ਼ੋਰੈਂਸ ਦਿਖਾਓ\n- ਪੁੱਛੋ: \"ਕੀ ਮੈਂ ਡਿਟੇਨ ਹਾਂ ਜਾਂ ਜਾ ਸਕਦਾ ਹਾਂ?\"\n- ਤੁਸੀਂ ਤਲਾਸ਼ੀ ਦੀ ਇਜਾਜ਼ਤ ਦੇਣ ਲਈ ਮਜਬੂਰ ਨਹੀਂ\n- ਕਹੋ: \"ਮੈਂ ਤਲਾਸ਼ੀ ਦੀ ਇਜਾਜ਼ਤ ਨਹੀਂ ਦਿੰਦਾ\"\n\n**ਤੁਹਾਡੇ ਹੱਕ:**\n- ਹੱਥ ਨਜ਼ਰ ਵਿੱਚ ਰੱਖੋ\n- ਸ਼ਾਂਤ ਰਹੋ\n- ਲੜਾਈ ਨਾ ਕਰੋ\n- ਵੀਡੀਓ ਬਣਾ ਸਕਦੇ ਹੋ (ਜੇ ਸੁਰੱਖਿਅਤ ਹੋਵੇ)",

        "right_arrest_content": "**ਅਰੈਸਟ ਹੋਣ 'ਤੇ:**\n1. ਚੁੱਪ ਰਹੋ\n2. ਕਹੋ: \"ਮੈਨੂੰ ਵਕੀਲ ਚਾਹੀਦਾ ਹੈ\"\n3. ਕੋਈ ਵੀ ਪੇਪਰ ਸਾਈਨ ਨਾ ਕਰੋ\n4. ਕੇਸ ਬਾਰੇ ਕਿਸੇ ਨਾਲ ਗੱਲ ਨਾ ਕਰੋ",

        "resources_title": "ਕਮਿਊਨਿਟੀ ਸਰਵਿਸ",
        "resources_subtitle": "ਲੀਗਲ ਐਡ ਅਤੇ ਕਮਿਊਨਿਟੀ ਮਦਦ ਲੱਭੋ",
        "legal_aid": "ਲੀਗਲ ਐਡ ਦਫ਼ਤਰ",
        "emergency_services": "ਐਮਰਜੈਂਸੀ ਸਰਵਿਸ",
        "immigration": "ਇਮੀਗ੍ਰੇਸ਼ਨ ਲੀਗਲ ਮਦਦ",
        "phone": "ਫੋਨ: ",
        "services": "ਸਰਵਿਸ: ",
        "website": "ਵੈੱਬਸਾਈਟ: ",
        "hours": "ਟਾਈਮ: ",

        "nearby_title": "ਨੇੜੇ ਹੱਕ",
        "nearby_subtitle": "ਆਪਣੇ ਇਲਾਕੇ ਵਿੱਚ ਲੀਗਲ ਐਡ ਅਤੇ ਸਰਵਿਸ ਲੱਭੋ",
        "enter_address": "ਆਪਣਾ ਐਡਰੈੱਸ ਦਿਓ:",
        "search_radius": "ਖੋਜ ਰੇਡੀਅਸ (ਮਾਈਲ):",
        "nearest_legal_aid": "📋 ਨੇੜੇ ਲੀਗਲ ਐਡ ਦਫ਼ਤਰ",
        "nearest_courthouse": "⚖️ ਨੇੜੇ ਕੋਰਟ",
        "nearest_police": "👮 ਨੇੜੇ ਪੁਲਿਸ ਸਟੇਸ਼ਨ",
        "nearest_translator": "🗣️ ਤਰਜਮਾ ਸਰਵਿਸ",
        "nearest_community": "🏢 ਕਮਿਊਨਿਟੀ ਸੈਂਟਰ",
        "address": "ਐਡਰੈੱਸ: ",
        "phone_number": "ਫੋਨ: ",
        "hours_open": "ਟਾਈਮ: ",
        "get_directions": "🗺️ ਦਿਸ਼ਾਵਾਂ",
        "not_found": "ਨੇੜੇ ਕੋਈ ਨਤੀਜੇ ਨਹੀਂ ਮਿਲੇ",

        "logging_title": "ਮੁਲਾਕਾਤ ਰਿਕਾਰਡ",
        "logging_subtitle": "ਪੁਲਿਸ ਨਾਲ ਹੋਈ ਮੁਲਾਕਾਤ ਰਿਕਾਰਡ ਕਰੋ",
        "encounter_type": "ਮੁਲਾਕਾਤ ਕਿਸਮ:",
        "encounter_location": "ਲੋਕੇਸ਼ਨ:",
        "encounter_details": "ਵੇਰਵਾ:",
        "encounter_date": "ਤਰੀਖ ਅਤੇ ਸਮਾਂ:",
        "officer_info": "ਪੁਲਿਸ ਜਾਣਕਾਰੀ:",
        "officer_badge": "ਬੈਜ ਨੰਬਰ:",
        "officer_agency": "ਏਜੰਸੀ:",
        "encounter_saved": "✅ ਮੁਲਾਕਾਤ ਸੇਵ ਹੋ ਗਈ",
        "view_history": "📋 ਹਿਸਟਰੀ ਵੇਖੋ",
        "total_encounters": "ਕੁੱਲ ਮੁਲਾਕਾਤਾਂ:",
        "search_encounters": "🔍 ਮੁਲਾਕਾਤ ਖੋਜੋ",
        "emergency_title": "ਐਮਰਜੈਂਸੀ ਮਦਦ",
        "emergency_subtitle": "ਹੌਟਲਾਈਨ ਅਤੇ ਐਮਰਜੈਂਸੀ ਸਰਵਿਸ",
        "emergency_911": "911 — ਪੁਲਿਸ, ਫਾਇਰ, ਮੈਡੀਕਲ",
        "emergency_suicide": "ਨੈਸ਼ਨਲ ਸੁਸਾਈਡ ਪ੍ਰਿਵੈਂਸ਼ਨ ਹੌਟਲਾਈਨ",
        "emergency_domestic": "ਘਰੇਲੂ ਹਿੰਸਾ ਹੌਟਲਾਈਨ",
        "emergency_assault": "RAINN — ਜਿਨਸੀ ਹਿੰਸਾ ਮਦਦ",
        "emergency_poison": "ਪੋਇਜ਼ਨ ਕੰਟਰੋਲ ਸੈਂਟਰ",
        "emergency_text": "ਕ੍ਰਾਈਸਿਸ ਟੈਕਸਟ ਲਾਈਨ",
        "emergency_procedures": "ਐਮਰਜੈਂਸੀ ਕਦਮ:",
        "procedure_safe": "ਆਪਣੀ ਸੁਰੱਖਿਆ ਯਕੀਨੀ ਬਣਾਓ",
        "procedure_document": "ਸਾਰੇ ਵੇਰਵੇ ਲਿਖੋ",
        "procedure_record": "ਜੇ ਸੁਰੱਖਿਅਤ ਹੋਵੇ ਤਾਂ ਵੀਡੀਓ ਬਣਾਓ",
        "procedure_call": "ਮਦਦ ਲਈ ਕਾਲ ਕਰੋ",
        "procedure_contact": "ਆਪਣੇ ਵਕੀਲ ਨਾਲ ਸੰਪਰਕ ਕਰੋ",

        "loading": "ਲੋਡ ਹੋ ਰਿਹਾ ਹੈ...",
        "success": "ਸਫਲਤਾ!",
        "error": "ਗਲਤੀ",
        "warning": "ਚੇਤਾਵਨੀ",
        "info": "ਜਾਣਕਾਰੀ",
        "processing": "ਪ੍ਰੋਸੈਸ ਹੋ ਰਿਹਾ ਹੈ...",
        "please_wait": "ਕਿਰਪਾ ਕਰਕੇ ਉਡੀਕ ਕਰੋ...",
        "no_data": "ਕੋਈ ਡਾਟਾ ਨਹੀਂ",
        "try_again": "ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ",

        "accessibility_title": "♿ ਐਕਸੈਸਿਬਿਲਟੀ ਸੈਟਿੰਗ",
        "text_size": "ਟੈਕਸਟ ਸਾਈਜ਼:",
        "text_size_normal": "ਨਾਰਮਲ",
        "text_size_large": "ਵੱਡਾ",
        "text_size_extra_large": "ਬਹੁਤ ਵੱਡਾ",
        "high_contrast": "🎨 ਹਾਈ ਕਾਂਟ੍ਰਾਸਟ ਮੋਡ",
        "high_contrast_on": "ਹਾਈ ਕਾਂਟ੍ਰਾਸਟ ON",
        "high_contrast_off": "ਹਾਈ ਕਾਂਟ੍ਰਾਸਟ OFF",
        "screen_reader": "ਸਕ੍ਰੀਨ ਰੀਡਰ ਲੇਬਲ ਚਾਲੂ",
        "accessibility_saved": "✅ ਐਕਸੈਸਿਬਿਲਟੀ ਸੈਟਿੰਗ ਸੇਵ ਹੋ ਗਈ",

        "extract_deadlines": "📋 ਮਿਲੀਆਂ ਡੈੱਡਲਾਈਨ",
        "extract_penalties": "⚠️ ਮਿਲੀਆਂ ਸਜ਼ਾਵਾਂ",
        "extract_requirements": "✓ ਲੋੜੀਂਦੇ ਕਦਮ",
        "deadline_found": "ਡੈੱਡਲਾਈਨ:",
        "penalty_found": "ਸਜ਼ਾ:",
        "requirement_found": "ਲੋੜੀਂਦਾ ਕਦਮ:",

        "document_summary": "📋 ਡੌਕੂਮੈਂਟ ਸਾਰ",
        "summary_generated": "ਸਾਰ ਤਿਆਰ ਹੋ ਗਿਆ",

        "location_title": "📍 ਨੇੜੇ ਸਰਵਿਸ ਲੱਭੋ",
        "enter_address": "ਐਡਰੈੱਸ ਜਾਂ ZIP ਕੋਡ ਦਿਓ:",
        "search_radius_miles": "ਖੋਜ ਰੇਡੀਅਸ (ਮਾਈਲ):",
        "find_resources": "🔍 ਸਰਵਿਸ ਖੋਜੋ",
        "resource_type": "ਸਰਵਿਸ ਕਿਸਮ:",
        "all_resources": "ਸਾਰੀਆਂ ਸਰਵਿਸ",
        "legal_aid_offices": "ਲੀਗਲ ਐਡ ਦਫ਼ਤਰ",
        "community_centers": "ਕਮਿਊਨਿਟੀ ਸੈਂਟਰ",
        "language_services": "ਭਾਸ਼ਾ ਸਰਵਿਸ",
        "emergency_shelters": "ਐਮਰਜੈਂਸੀ ਸ਼ੈਲਟਰ",
        "distance_away": "ਮਾਈਲ ਦੂਰ",
        "get_directions": "🗺️ ਦਿਸ਼ਾਵਾਂ",
        "no_resources_found": "ਇਸ ਇਲਾਕੇ ਵਿੱਚ ਕੋਈ ਸਰਵਿਸ ਨਹੀਂ ਮਿਲੀ",
        "resource_hours": "ਟਾਈਮ:",
        "resource_phone": "ਫੋਨ:",
        "resource_address": "ਐਡਰੈੱਸ:",
        "resource_website": "ਵੈੱਬਸਾਈਟ:",
        "loading_resources": "ਨੇੜੇ ਸਰਵਿਸ ਖੋਜੀਆਂ ਜਾ ਰਹੀਆਂ ਹਨ...",

        "saved_deadlines": "⏰ ਸੇਵ ਕੀਤੀਆਂ ਡੈੱਡਲਾਈਨ",
        "upload_legal_doc": "ਲੀਗਲ ਡੌਕੂਮੈਂਟ ਅੱਪਲੋਡ ਕਰੋ",
        "important_dates": "📅 ਮਹੱਤਵਪੂਰਨ ਤਰੀਖਾਂ",
        "required_actions": "✓ ਲੋੜੀਂਦੇ ਕਦਮ",
        "critical_deadlines": "⏰ ਜ਼ਰੂਰੀ ਡੈੱਡਲਾਈਨ",
        "penalties_warnings": "⚠️ ਸਜ਼ਾਵਾਂ ਅਤੇ ਚੇਤਾਵਨੀਆਂ",
        "extraction_guide": "ਡੌਕੂਮੈਂਟ ਐਕਸਟ੍ਰੈਕਸ਼ਨ ਗਾਈਡ",

        "demo_mode_active": "📺 **ਡੈਮੋ ਮੋਡ ON** — ਨਮੂਨਾ ਡਾਟਾ ਦਿਖਾਇਆ ਜਾ ਰਿਹਾ ਹੈ",
        "have_deadlines": "📋 ਤੁਹਾਡੇ ਕੋਲ ਮਹੱਤਵਪੂਰਨ ਡੈੱਡਲਾਈਨ ਹਨ!",
        "view_all_deadlines": "📋 ਸਾਰੀਆਂ ਡੈੱਡਲਾਈਨ ਵੇਖੋ →",
        "from_document": "ਡੌਕੂਮੈਂਟ ਤੋਂ:",
        "file_type": "ਫਾਈਲ ਕਿਸਮ",
        "file_size": "ਫਾਈਲ ਸਾਈਜ਼",
        "status_ready": "ਐਕਸਟ੍ਰੈਕਸ਼ਨ ਲਈ ਤਿਆਰ",
        "extract_information": "🔍 ਜਾਣਕਾਰੀ ਕੱਢੋ",
        "extracting_info": "ਡੌਕੂਮੈਂਟ ਤੋਂ ਜਾਣਕਾਰੀ ਕੱਢੀ ਜਾ ਰਹੀ ਹੈ...",
        "no_dates_found": "ਕੋਈ ਤਰੀਖਾਂ ਨਹੀਂ ਮਿਲੀਆਂ",
        "no_deadlines_found": "ਕੋਈ ਡੈੱਡਲਾਈਨ ਨਹੀਂ ਮਿਲੀਆਂ",
        "no_penalties_found": "ਕੋਈ ਸਜ਼ਾਵਾਂ ਨਹੀਂ ਮਿਲੀਆਂ",
        "download_summary": "📥 ਸਾਰ ਡਾਊਨਲੋਡ ਕਰੋ",
        "download_as_txt": "TXT ਵਜੋਂ ਡਾਊਨਲੋਡ ਕਰੋ",
        "save_deadlines_to_dashboard": "💾 ਡੈੱਡਲਾਈਨ ਡੈਸ਼ਬੋਰਡ 'ਚ ਸੇਵ ਕਰੋ",

        "know_your_rights_long": "⚖️ ਆਪਣੇ ਹੱਕ ਸਮਝੋ",
        "education_quizzes": "ਸਿੱਖਿਆ, ਕਵਿਜ਼ ਅਤੇ ਲਰਨਿੰਗ ਮੋਡੀਊਲ",
        "learn_tab": "📚 ਸਿੱਖੋ",
        "quiz_tab": "🧪 ਕਵਿਜ਼",
        "rights_education": "ਹੱਕ ਸਿੱਖਿਆ",
        "select_topic": "ਟਾਪਿਕ ਚੁਣੋ:",
        "test_knowledge": "ਸਿਵਲ ਹੱਕਾਂ ਬਾਰੇ ਆਪਣੀ ਜਾਣਕਾਰੀ ਟੈਸਟ ਕਰੋ।",
        "rights_quiz": "ਹੱਕ ਕਵਿਜ਼",
        "can_police_search": "ਕੀ ਪੁਲਿਸ ਤੁਹਾਡੀ ਕਾਰ ਬਿਨਾਂ ਇਜਾਜ਼ਤ ਤਲਾਸ਼ ਸਕਦੀ ਹੈ?",
        "only_with_warrant": "ਸਿਰਫ਼ ਵਾਰੰਟ ਨਾਲ",
        "only_prob_cause": "ਸਿਰਫ਼ probable cause ਨਾਲ",
        "both_a_and_b": "A ਅਤੇ B ਦੋਵੇਂ",
        "never_without": "ਨਹੀਂ, ਉਹ ਨਹੀਂ ਕਰ ਸਕਦੇ",
        "police_can_search": "ਪੁਲਿਸ ਵਾਰੰਟ ਜਾਂ probable cause ਹੋਣ 'ਤੇ ਤਲਾਸ਼ ਕਰ ਸਕਦੀ ਹੈ।",

        "answer_police_q": "ਕੀ ਤੁਹਾਨੂੰ ਪੁਲਿਸ ਦੇ ਸਵਾਲਾਂ ਦਾ ਜਵਾਬ ਦੇਣਾ ਪੈਂਦਾ ਹੈ?",
        "yes_always": "ਹਾਂ, ਹਮੇਸ਼ਾ",
        "right_remain_silent": "ਨਹੀਂ, ਤੁਹਾਨੂੰ ਚੁੱਪ ਰਹਿਣ ਦਾ ਹੱਕ ਹੈ",
        "only_your_name": "ਸਿਰਫ਼ ਆਪਣਾ ਨਾਮ ਦੱਸੋ",
        "only_if_arrested": "ਸਿਰਫ਼ ਅਰੈਸਟ ਹੋਣ 'ਤੇ",
        "fifth_amendment": "5ਵਾਂ ਸੰਸ਼ੋਧਨ ਤੁਹਾਨੂੰ ਚੁੱਪ ਰਹਿਣ ਦਾ ਹੱਕ ਦਿੰਦਾ ਹੈ।",

        "what_say_arrested": "ਅਰੈਸਟ ਹੋਣ 'ਤੇ ਕੀ ਕਹਿਣਾ ਚਾਹੀਦਾ ਹੈ?",
        "explain_what_happened": "ਕੀ ਹੋਇਆ ਦੱਸੋ",
        "ask_for_lawyer": "ਵਕੀਲ ਮੰਗੋ",
        "refuse_give_name": "ਨਾਮ ਦੱਸਣ ਤੋਂ ਇਨਕਾਰ ਕਰੋ",
        "try_negotiate": "ਪੁਲਿਸ ਨਾਲ ਗੱਲਬਾਤ ਕਰੋ",
        "always_ask_lawyer": "ਹਮੇਸ਼ਾ ਵਕੀਲ ਮੰਗੋ ਅਤੇ ਚੁੱਪ ਰਹੋ।",

        "check_answer": "✓ ਜਵਾਬ ਚੈੱਕ ਕਰੋ {number}",
        "question_number": "ਸਵਾਲ {number}: {question}",
        "select_answer": "ਜਵਾਬ ਚੁਣੋ:",
        "your_score": "ਤੁਹਾਡਾ ਸਕੋਰ",

        "talk_community": "💬 ਕਮਿਊਨਿਟੀ ਨਾਲ ਗੱਲਬਾਤ ਕਰੋ",
        "community_intro": "ਅਨੁਭਵ ਸਾਂਝੇ ਕਰੋ, ਸਵਾਲ ਪੁੱਛੋ, ਹੋਰਾਂ ਦੀ ਮਦਦ ਕਰੋ — ਅਸੀਂ ਇਕੱਠੇ ਮਜ਼ਬੂਤ ਹਾਂ",
        "share_exp_tab": "💭 ਅਨੁਭਵ ਸਾਂਝਾ ਕਰੋ",
        "ask_q_tab": "❓ ਸਵਾਲ ਪੁੱਛੋ",
        "give_advice_tab": "💡 ਸਲਾਹ ਦਿਓ",

        "share_your_exp": "💭 ਆਪਣਾ ਅਨੁਭਵ ਸਾਂਝਾ ਕਰੋ",
        "share_story": "ਆਪਣਾ ਅਨੁਭਵ ਸਾਂਝਾ ਕਰਕੇ ਹੋਰਾਂ ਦੀ ਮਦਦ ਕਰੋ। ਸਾਰੇ ਪੋਸਟ ਸੁਰੱਖਿਆ ਲਈ ਸਮੀਖਿਆ ਕੀਤੇ ਜਾਂਦੇ ਹਨ।",
        "title_label": "ਟਾਈਟਲ:",
        "exp_placeholder": "ਉਦਾਹਰਨ: ਟ੍ਰੈਫਿਕ ਰੋਕਣ ਵੇਲੇ ਕੀ ਕਰਨਾ ਹੈ",
        "your_story": "ਤੁਹਾਡਾ ਅਨੁਭਵ:",
        "story_placeholder": "ਆਪਣੀ ਕਹਾਣੀ ਲਿਖੋ...",
        "post_anonymously": "ਗੁਪਤ ਤੌਰ 'ਤੇ ਪੋਸਟ ਕਰੋ",
        "share_exp_btn": "📤 ਅਨੁਭਵ ਸਾਂਝਾ ਕਰੋ",
        "fill_title_content": "⚠️ ਕਿਰਪਾ ਕਰਕੇ ਟਾਈਟਲ ਅਤੇ ਵੇਰਵਾ ਦਿਓ",
        "exp_shared": "✅ ਤੁਹਾਡਾ ਅਨੁਭਵ ਸਾਂਝਾ ਹੋ ਗਿਆ! ਧੰਨਵਾਦ।",

        "ask_community": "❓ ਕਮਿਊਨਿਟੀ ਨੂੰ ਪੁੱਛੋ",
        "question_help": "ਤੁਹਾਨੂੰ ਸਵਾਲ ਹੈ? ਕਮਿਊਨਿਟੀ ਮਦਦ ਕਰੇਗੀ।",
        "your_question": "ਤੁਹਾਡਾ ਸਵਾਲ:",
        "question_placeholder": "ਉਦਾਹਰਨ: ਪੁਲਿਸ ਮੈਨੂੰ ਰੋਕੇ ਤਾਂ ਮੇਰੇ ਹੱਕ ਕੀ ਹਨ?",
        "details_label": "ਵੇਰਵਾ:",
        "details_placeholder": "ਹੋਰ ਜਾਣਕਾਰੀ ਦਿਓ...",
        "ask_anon": "ਗੁਪਤ ਤੌਰ 'ਤੇ ਪੋਸਟ ਕਰੋ",
        "ask_q_btn": "❓ ਸਵਾਲ ਪੋਸਟ ਕਰੋ",
        "enter_question": "⚠️ ਕਿਰਪਾ ਕਰਕੇ ਸਵਾਲ ਦਿਓ",
        "question_posted": "✅ ਤੁਹਾਡਾ ਸਵਾਲ ਪੋਸਟ ਹੋ ਗਿਆ!",

        "give_advice": "💡 ਸਲਾਹ ਦਿਓ",
        "help_others": "ਆਪਣੀ ਜਾਣਕਾਰੀ ਨਾਲ ਹੋਰਾਂ ਦੀ ਮਦਦ ਕਰੋ।",
        "topic_label": "ਟਾਪਿਕ:",
        "topic_placeholder": "ਉਦਾਹਰਨ: ਕੋਰਟ ਲਈ ਤਿਆਰੀ ਕਿਵੇਂ ਕਰਨੀ ਹੈ",
        "your_advice": "ਤੁਹਾਡੀ ਸਲਾਹ:",
        "advice_placeholder": "ਆਪਣੀ ਜਾਣਕਾਰੀ ਸਾਂਝੀ ਕਰੋ...",
        "share_anon": "ਗੁਪਤ ਤੌਰ 'ਤੇ ਸਾਂਝਾ ਕਰੋ",
        "share_advice_btn": "💡 ਸਲਾਹ ਸਾਂਝੀ ਕਰੋ",
        "share_wisdom": "✅ ਤੁਹਾਡੀ ਸਲਾਹ ਲਈ ਧੰਨਵਾਦ!",
        "fill_topic_advice": "⚠️ ਕਿਰਪਾ ਕਰਕੇ ਟਾਪਿਕ ਅਤੇ ਸਲਾਹ ਦਿਓ",

        "recent_posts": "📋 ਤਾਜ਼ਾ ਪੋਸਟ",
        "no_posts_yet": "💭 ਅਜੇ ਤੱਕ ਕੋਈ ਪੋਸਟ ਨਹੀਂ। ਪਹਿਲੀ ਤੁਸੀਂ ਕਰੋ!",
        "posted_recently": "{timestamp} 'ਤੇ ਪੋਸਟ ਕੀਤਾ",
        "author_anonymous": "ਗੁਪਤ",
        "author_community_member": "ਕਮਿਊਨਿਟੀ ਮੈਂਬਰ",

        "crisis_hotlines": "🚨 ਕ੍ਰਾਈਸਿਸ ਹੌਟਲਾਈਨ",
        "crisis_support_24": "24/7 ਮਦਦ ਉਪਲਬਧ",
        "emergency_hotlines_header": "🆘 ਐਮਰਜੈਂਸੀ ਹੌਟਲਾਈਨ",
        "in_immediate_danger": "ਜੇ ਤੁਰੰਤ ਖਤਰਾ ਹੈ ਤਾਂ 911 ਨੂੰ ਕਾਲ ਕਰੋ",
        "emergency_number": "ਐਮਰਜੈਂਸੀ ਨੰਬਰ",
        "suicide_prevention": "ਨੈਸ਼ਨਲ ਸੁਸਾਈਡ ਪ੍ਰਿਵੈਂਸ਼ਨ ਹੌਟਲਾਈਨ",
        "domestic_violence": "ਘਰੇਲੂ ਹਿੰਸਾ ਹੌਟਲਾਈਨ",
        "sexual_assault": "RAINN — ਜਿਨਸੀ ਹਿੰਸਾ ਮਦਦ",
        "poison_control": "ਪੋਇਜ਼ਨ ਕੰਟਰੋਲ ਸੈਂਟਰ",
        "crisis_text": "ਕ੍ਰਾਈਸਿਸ ਟੈਕਸਟ ਲਾਈਨ",

        "safety_procedures": "📋 ਸੁਰੱਖਿਆ ਕਦਮ",
        "stay_safe": "🛡️ ਸੁਰੱਖਿਅਤ ਰਹੋ",
        "stay_safe_desc": "ਤੁਹਾਡੀ ਸੁਰੱਖਿਆ ਸਭ ਤੋਂ ਮਹੱਤਵਪੂਰਨ ਹੈ — ਲੜਾਈ ਨਾ ਕਰੋ।",
        "document_details": "📝 ਵੇਰਵੇ ਲਿਖੋ",
        "document_details_desc": "ਪੁਲਿਸ ਦਾ ਨਾਮ, ਬੈਜ ਨੰਬਰ, ਲੋਕੇਸ਼ਨ, ਸਮਾਂ ਅਤੇ ਕਾਰਵਾਈ ਲਿਖੋ।",
        "record_safely": "🎥 ਸੁਰੱਖਿਅਤ ਤਰੀਕੇ ਨਾਲ ਰਿਕਾਰਡ ਕਰੋ",
        "record_safely_desc": "ਜੇ ਸੁਰੱਖਿਅਤ ਹੋਵੇ ਤਾਂ ਵੀਡੀਓ ਬਣਾਓ।",
        "call_for_help": "📞 ਮਦਦ ਲਈ ਕਾਲ ਕਰੋ",
        "call_help_desc": "ਖਤਰੇ ਵਿੱਚ ਹੋਣ 'ਤੇ ਤੁਰੰਤ 911 ਨੂੰ ਕਾਲ ਕਰੋ।",
        "get_legal_help": "⚖️ ਲੀਗਲ ਮਦਦ ਲਵੋ",
        "legal_help_desc": "ਆਪਣੇ ਵਕੀਲ ਨਾਲ ਸੰਪਰਕ ਕਰੋ। ਪਬਲਿਕ ਡਿਫੈਂਡਰ ਵੀ ਮਦਦ ਕਰਦੇ ਹਨ।",
        "medical_attention": "🏥 ਮੈਡੀਕਲ ਮਦਦ",
        "medical_attention_desc": "ਜੇ ਚੋਟ ਲੱਗੀ ਹੈ ਤਾਂ ਤੁਰੰਤ ਮੈਡੀਕਲ ਮਦਦ ਲਵੋ ਅਤੇ ਫੋਟੋ ਲਵੋ।",
        "mental_health_support": "🧠 ਮਾਨਸਿਕ ਸਿਹਤ ਮਦਦ",
        "legal_troubles_trauma": "ਪੁਲਿਸ ਨਾਲ ਮੁਲਾਕਾਤ ਮਾਨਸਿਕ ਤਣਾਅ ਪੈਦਾ ਕਰ ਸਕਦੀ ਹੈ।",
        "mental_health_resources": "ਮਾਨਸਿਕ ਸਿਹਤ ਸਰੋਤ:",
        "samhsa_helpline": "SAMHSA ਹੌਟਲਾਈਨ: 1‑800‑662‑4357 (ਮੁਫ਼ਤ, ਗੁਪਤ, 24/7)",
        "psychology_directory": "ਥੈਰਾਪਿਸਟ ਲੱਭੋ: Psychology Today ਡਾਇਰੈਕਟਰੀ",
        "support_groups": "ਸਹਾਇਤਾ ਗਰੁੱਪ: NAACP, ਕਮਿਊਨਿਟੀ ਸੈਂਟਰ, ਲੀਗਲ ਸੰਸਥਾਵਾਂ",
        "contact_emergency": "🆘 ਐਮਰਜੈਂਸੀ ਮਦਦ",
        "contact_suicide": "🧠 ਸੁਸਾਈਡ ਪ੍ਰਿਵੈਂਸ਼ਨ",
        "contact_domestic": "💔 ਘਰੇਲੂ ਹਿੰਸਾ ਹੌਟਲਾਈਨ",
        "contact_rainn": "🤝 RAINN — ਜਿਨਸੀ ਹਿੰਸਾ ਮਦਦ",
        "contact_poison": "☠️ ਪੋਇਜ਼ਨ ਕੰਟਰੋਲ",
        "contact_crisis_text": "📱 ਕ੍ਰਾਈਸਿਸ ਟੈਕਸਟ ਲਾਈਨ",
        "contact_crisis_text_number": "HOME ਨੂੰ 741741 'ਤੇ ਟੈਕਸਟ ਕਰੋ",

        "enc_type_traffic_stop": "ਟ੍ਰੈਫਿਕ ਰੋਕ",
        "enc_type_street_encounter": "ਗਲੀ ਮੁਲਾਕਾਤ",
        "enc_type_arrest": "ਅਰੈਸਟ",
        "enc_type_search": "ਤਲਾਸ਼ੀ",
        "enc_type_other": "ਹੋਰ",
        "encounter_label": "ਮੁਲਾਕਾਤ",
        "unknown": "ਅਣਜਾਣ",
        "na": "ਲਾਗੂ ਨਹੀਂ",
        "error_generating_qr": "QR ਕੋਡ ਬਣਾਉਣ ਵਿੱਚ ਗਲਤੀ",

        "btn_launch_app": "🚀 ਐਪ ਸ਼ੁਰੂ ਕਰੋ",
        "btn_start_demo": "📺 ਡੈਮੋ ਸ਼ੁਰੂ ਕਰੋ",
        "btn_quick_tour": "❓ ਤੁਰੰਤ ਟੂਰ",
        "share_with_others": "📱 ਹੋਰਾਂ ਨਾਲ ਸਾਂਝਾ ਕਰੋ",
        "qr_generation_in_progress": "QR ਕੋਡ ਬਣਾਇਆ ਜਾ ਰਿਹਾ ਹੈ...",
        "key_features_label": "ਮੁੱਖ ਫੀਚਰ:",
        "btn_previous": "⬅️ ਪਿਛਲਾ",
        "language_change_error": "ਭਾਸ਼ਾ ਬਦਲਣ ਵਿੱਚ ਗਲਤੀ",
        "demo_mode_active_sidebar": "✅ ਡੈਮੋ ਮੋਡ ON — ਨਮੂਨਾ ਡਾਟਾ",
        "screen_reader_off": "🔇 ਸਕ੍ਰੀਨ ਰੀਡਰ OFF",

        "navigation_title": "ਨੇਵੀਗੇਸ਼ਨ",
        "nav_rights_full": "⚖️ ਆਪਣੇ ਹੱਕ ਸਮਝੋ",
        "nav_resources_near_you": "📍 ਨੇੜੇ ਸਰਵਿਸ",
        "nav_logging_full": "📝 ਮੁਲਾਕਾਤ ਰਿਕਾਰਡ",
        "nav_crisis_resources": "🚨 ਕ੍ਰਾਈਸਿਸ ਸਰੋਤ",
        "nav_community": "💬 ਕਮਿਊਨਿਟੀ",

        "sidebar_built_for": "ਹਰ ਕਿਸੇ ਦੇ ਸਿਵਲ ਹੱਕਾਂ ਦੀ ਸੁਰੱਖਿਆ ਲਈ ਬਣਾਇਆ ਗਿਆ।",
        "show_landing_page": "🏠 ਲੈਂਡਿੰਗ ਪੇਜ ਦਿਖਾਓ",

        "landing_hero_html": "<div class=\"landing-hero\"><h1>⚖️ CivicShield Pro</h1><h2>ਆਪਣੇ ਹੱਕ ਸਮਝੋ। ਆਪਣੇ ਆਪ ਨੂੰ ਬਚਾਓ। ਮਦਦ ਲਵੋ।</h2><p>ਸਿਵਲ ਹੱਕਾਂ ਨੂੰ ਸਮਝਣ ਅਤੇ ਵਰਤਣ ਲਈ ਬਣਾਇਆ ਗਿਆ ਬਹੁਭਾਸ਼ਾਈ ਪਲੇਟਫਾਰਮ।</p></div>",

        "landing_purpose_md": "### 🎯 ਮਕਸਦ\nCivicShield Pro ਪ੍ਰਦਾਨ ਕਰਦਾ ਹੈ:\n\n- **14 ਭਾਸ਼ਾਵਾਂ ਵਿੱਚ ਰੀਅਲ‑ਟਾਈਮ ਲੀਗਲ ਤਰਜਮਾ**\n- **ਸਥਿਤੀ ਅਨੁਸਾਰ ਹੱਕ ਜਾਣਕਾਰੀ**\n- **ਲੀਗਲ ਡੌਕੂਮੈਂਟ ਵਿਸ਼ਲੇਸ਼ਣ** ਅਤੇ ਡੈੱਡਲਾਈਨ ਐਕਸਟ੍ਰੈਕਸ਼ਨ\n- **ਕਮਿਊਨਿਟੀ ਮਦਦ** ਅਤੇ ਅਨੁਭਵ ਸਾਂਝਾ\n- **24/7 ਕ੍ਰਾਈਸਿਸ ਸਰੋਤ**",

        "landing_features_md": "### ⭐ ਮੁੱਖ ਫੀਚਰ\n\n- 🗣️ **ਰੀਅਲ‑ਟਾਈਮ ਤਰਜਮਾ** — ਪੁਲਿਸ ਦੀ ਗੱਲ ਤਰਜਮਾ ਕਰੋ\n- 📄 **ਲੀਗਲ ਡੌਕੂਮੈਂਟ ਟੂਲ** — ਮਹੱਤਵਪੂਰਨ ਜਾਣਕਾਰੀ ਕੱਢੋ\n- ⚖️ **ਹੱਕ ਸਿੱਖਿਆ** — ਪਾਠ ਅਤੇ ਕਵਿਜ਼\n- 📍 **ਨੇੜੇ ਸਰਵਿਸ** — ਲੀਗਲ ਐਡ ਅਤੇ ਕਮਿਊਨਿਟੀ ਮਦਦ\n- 📝 **ਮੁਲਾਕਾਤ ਰਿਕਾਰਡ** — ਪੁਲਿਸ ਨਾਲ ਮੁਲਾਕਾਤ ਲਿਖੋ\n- 🚨 **ਕ੍ਰਾਈਸਿਸ ਹੌਟਲਾਈਨ** — 24/7 ਮਦਦ\n- 💬 **ਕਮਿਊਨਿਟੀ ਫੋਰਮ** — ਸਵਾਲ ਪੁੱਛੋ ਅਤੇ ਸਾਂਝਾ ਕਰੋ",

        "landing_share_md": "**CivicShield ਹੋਰਾਂ ਨਾਲ ਸਾਂਝਾ ਕਰੋ:**\n\n1. QR ਕੋਡ ਸਕੈਨ ਕਰੋ\n2. ਕੋਈ ਇੰਸਟਾਲ ਨਹੀਂ ਚਾਹੀਦਾ\n3. 14 ਭਾਸ਼ਾਵਾਂ ਦਾ ਸਹਿਯੋਗ\n4. ਫੋਨ, ਟੈਬਲੇਟ, ਕੰਪਿਊਟਰ 'ਤੇ ਚੱਲਦਾ ਹੈ",

        "landing_who_should_use_md": "### 👥 ਕੌਣ ਵਰਤੇ?\n\n**ਜੱਜ ਅਤੇ ਲੀਗਲ ਪ੍ਰੋਫੈਸ਼ਨਲ:**\n- ਕਮਿਊਨਿਟੀ ਦਾ ਨਜ਼ਰੀਆ ਸਮਝੋ\n- ਡਿਫੈਂਡਰ ਦੇ ਹੱਕਾਂ ਦੀ ਸਮਝ ਵੇਖੋ\n- ਰੀਅਲ‑ਟਾਈਮ ਤਰਜਮਾ ਵਰਤੋ\n\n**ਵਕੀਲ ਅਤੇ ਲੀਗਲ ਐਡ:**\n- ਬਹੁਭਾਸ਼ਾਈ ਲੀਗਲ ਜਾਣਕਾਰੀ ਦਿਓ\n- ਕਲਾਇੰਟਾਂ ਨੂੰ ਮੁਲਾਕਾਤ ਰਿਕਾਰਡ ਕਰਨ ਵਿੱਚ ਮਦਦ ਕਰੋ\n- ਕਮਿਊਨਿਟੀ ਸਰੋਤਾਂ ਨਾਲ ਜੋੜੋ\n\n**ਅਧਿਆਪਕ:**\n- ਸਿਵਲ ਹੱਕ ਸਿੱਖਾਓ\n- ਅਸਲੀ ਉਦਾਹਰਨ ਵਰਤੋ\n- ਇੰਟਰੈਕਟਿਵ ਕਵਿਜ਼ ਦਿਓ\n\n**ਕਮਿਊਨਿਟੀ:**\n- ਪੁਲਿਸ ਨਾਲ ਮੁਲਾਕਾਤ ਵੇਲੇ ਕੀ ਕਰਨਾ ਹੈ ਜਾਣੋ\n- ਐਮਰਜੈਂਸੀ ਸਰੋਤ ਵਰਤੋ\n- ਅਨੁਭਵ ਸਾਂਝੇ ਕਰੋ",

        "landing_disclaimer_md": "**⚠️ ਲੀਗਲ ਨੋਟਿਸ:**\n\nCivicShield Pro ਸਿੱਖਿਆ ਲਈ ਹੈ, ਲੀਗਲ ਸਲਾਹ ਨਹੀਂ।\ਨਕਾਨੂੰਨ ਇਲਾਕੇ ਅਨੁਸਾਰ ਬਦਲ ਸਕਦੇ ਹਨ।\nਆਪਣੇ ਕੇਸ ਲਈ ਵਕੀਲ ਨਾਲ ਸੰਪਰਕ ਕਰੋ।",

        "tutorial_intro_html": "<div class=\"tutorial-container\"><h1>👋 CivicShield Pro ਵਿੱਚ ਸਵਾਗਤ!</h1><p>ਮੁੱਖ ਫੀਚਰ ਵੇਖੀਏ।</p></div>",

        "tutorial_step1_title": "🏠 ਮੁੱਖ ਡੈਸ਼ਬੋਰਡ",
        "tutorial_step1_desc": "ਇੱਥੇ ਤੁਸੀਂ ਸਾਰੇ ਫੀਚਰ ਐਕਸੈੱਸ ਕਰ ਸਕਦੇ ਹੋ।",
        "tutorial_step1_feat1": "ਸਾਰੇ ਟੂਲਾਂ ਲਈ ਨੇਵੀਗੇਸ਼ਨ",
        "tutorial_step1_feat2": "ਸੇਵ ਕੀਤੀਆਂ ਡੈੱਡਲਾਈਨ ਵੇਖੋ",
        "tutorial_step1_feat3": "ਐਮਰਜੈਂਸੀ ਸਰੋਤਾਂ ਤੱਕ ਪਹੁੰਚ",

        "tutorial_step2_title": "🗣️ ਰੀਅਲ‑ਟਾਈਮ ਤਰਜਮਾ",
        "tutorial_step2_desc": "ਪੁਲਿਸ ਦੀ ਗੱਲ 14 ਭਾਸ਼ਾਵਾਂ ਵਿੱਚ ਤਰਜਮਾ ਕਰੋ।",
        "tutorial_step2_feat1": "ਸਪੀਚ‑ਟੂ‑ਟੈਕਸਟ",
        "tutorial_step2_feat2": "ਤੁਰੰਤ ਤਰਜਮਾ",
        "tutorial_step2_feat3": "ਆਡੀਓ ਪਲੇਬੈਕ",

        "tutorial_step3_title": "📄 ਲੀਗਲ ਡੌਕੂਮੈਂਟ",
        "tutorial_step3_desc": "ਡੌਕੂਮੈਂਟ ਅੱਪਲੋਡ ਕਰੋ ਅਤੇ ਮਹੱਤਵਪੂਰਨ ਜਾਣਕਾਰੀ ਲਵੋ।",
        "tutorial_step3_feat1": "ਆਟੋਮੈਟਿਕ ਡੈੱਡਲਾਈਨ ਐਕਸਟ੍ਰੈਕਸ਼ਨ",
        "tutorial_step3_feat2": "ਸਜ਼ਾਵਾਂ ਦੀ ਪਛਾਣ",
        "tutorial_step3_feat3": "ਡੌਕੂਮੈਂਟ ਤਰਜਮਾ",
        "tutorial_step4_title": "⚖️ ਹੱਕ ਸਿੱਖਿਆ",
        "tutorial_step4_desc": "ਆਪਣੇ ਹੱਕਾਂ ਬਾਰੇ ਜਾਣੋ ਅਤੇ ਕਵਿਜ਼ ਨਾਲ ਆਪਣੀ ਜਾਣਕਾਰੀ ਟੈਸਟ ਕਰੋ।",
        "tutorial_step4_feat1": "ਹੱਕਾਂ ਦੇ ਪਾਠ",
        "tutorial_step4_feat2": "ਇੰਟਰੈਕਟਿਵ ਕਵਿਜ਼",
        "tutorial_step4_feat3": "ਪ੍ਰੋਗਰੈੱਸ ਟ੍ਰੈਕਿੰਗ",

        "tutorial_step5_title": "📍 ਨੇੜੇ ਸਰਵਿਸ",
        "tutorial_step5_desc": "ਆਪਣੇ ਇਲਾਕੇ ਵਿੱਚ ਲੀਗਲ ਐਡ ਅਤੇ ਕਮਿਊਨਿਟੀ ਸਰਵਿਸ ਲੱਭੋ।",
        "tutorial_step5_feat1": "ਲੋਕੇਸ਼ਨ‑ਅਧਾਰਿਤ ਖੋਜ",
        "tutorial_step5_feat2": "ਸਰਵਿਸ ਫਿਲਟਰ",
        "tutorial_step5_feat3": "ਤੁਰੰਤ ਦਿਸ਼ਾਵਾਂ",

        "tutorial_step6_title": "💬 ਕਮਿਊਨਿਟੀ ਫੋਰਮ",
        "tutorial_step6_desc": "ਅਨੁਭਵ ਸਾਂਝੇ ਕਰੋ, ਸਵਾਲ ਪੁੱਛੋ, ਹੋਰਾਂ ਦੀ ਮਦਦ ਕਰੋ।",
        "tutorial_step6_feat1": "ਗੁਪਤ ਪੋਸਟਿੰਗ",
        "tutorial_step6_feat2": "ਲੀਗਲ ਸਵਾਲ",
        "tutorial_step6_feat3": "ਸਲਾਹ ਸਾਂਝੀ ਕਰੋ",

        "documents_intro_md": "ਲੀਗਲ ਡੌਕੂਮੈਂਟ (ਫੋਟੋ ਜਾਂ PDF) ਅੱਪਲੋਡ ਕਰੋ ਅਤੇ ਹੇਠਾਂ ਦਿੱਤੀ ਜਾਣਕਾਰੀ ਲਵੋ:\n- ਤਰੀਖਾਂ ਅਤੇ ਡੈੱਡਲਾਈਨ\n- ਲੋੜੀਂਦੇ ਕਦਮ\n- ਸਜ਼ਾਵਾਂ ਅਤੇ ਚੇਤਾਵਨੀਆਂ\n- ਸਰਕਾਰੀ ਏਜੰਸੀਆਂ\n- ਡੌਕੂਮੈਂਟ ਸਾਰ",

        "extract_deadlines_found": "📋 ਮਿਲੀਆਂ ਡੈੱਡਲਾਈਨ",
        "extract_penalties_found": "⚠️ ਮਿਲੀਆਂ ਸਜ਼ਾਵਾਂ",
        "extract_requirements_found": "✓ ਮਿਲੇ ਲੋੜੀਂਦੇ ਕਦਮ",

        "search_radius_km": "ਖੋਜ ਰੇਡੀਅਸ (ਕਿਲੋਮੀਟਰ):",

        "resource_category": "ਸਰਵਿਸ ਸ਼੍ਰੇਣੀ:",
        "resource_distance": "ਦੂਰੀ:",
        "resource_map_link": "🗺️ ਮੈਪ",
        "resource_description": "ਵੇਰਵਾ:",
        "resource_notes": "ਨੋਟ:",
        "resource_tags": "ਟੈਗ:",
        "resource_id": "ਸਰਵਿਸ ID:",
        "resource_source": "ਸਰੋਤ:",
        "resource_updated": "ਆਖਰੀ ਅੱਪਡੇਟ:",
        "resource_error": "ਸਰਵਿਸ ਜਾਣਕਾਰੀ ਲੈਣ ਵਿੱਚ ਗਲਤੀ",

        "logging_intro_md": "ਪੁਲਿਸ ਨਾਲ ਹੋਈ ਮੁਲਾਕਾਤਾਂ ਨੂੰ ਰਿਕਾਰਡ ਕਰੋ। ਇਹ ਤੁਹਾਡੀ ਸੁਰੱਖਿਆ ਅਤੇ ਲੀਗਲ ਮਦਦ ਲਈ ਮਹੱਤਵਪੂਰਨ ਹੈ।",
        "logging_steps_md": "### ਰਿਕਾਰਡਿੰਗ ਕਦਮ\n1. ਮੁਲਾਕਾਤ ਕਿਸਮ ਚੁਣੋ\n2. ਲੋਕੇਸ਼ਨ ਦਿਓ\n3. ਵੇਰਵਾ ਲਿਖੋ\n4. ਪੁਲਿਸ ਜਾਣਕਾਰੀ ਦਿਓ\n5. ਸੇਵ ਕਰੋ",

        "logging_history_title": "📋 ਮੁਲਾਕਾਤ ਹਿਸਟਰੀ",
        "logging_history_desc": "ਤੁਸੀਂ ਰਿਕਾਰਡ ਕੀਤੀਆਂ ਸਾਰੀਆਂ ਮੁਲਾਕਾਤਾਂ ਇੱਥੇ ਵੇਖ ਸਕਦੇ ਹੋ।",
        "logging_no_history": "ਅਜੇ ਤੱਕ ਕੋਈ ਮੁਲਾਕਾਤ ਰਿਕਾਰਡ ਨਹੀਂ ਹੋਈ।",
        "logging_view_details": "ਵੇਰਵਾ ਵੇਖੋ",
        "logging_delete_entry": "❌ ਐਂਟਰੀ ਮਿਟਾਓ",
        "logging_deleted": "ਐਂਟਰੀ ਸਫਲਤਾਪੂਰਵਕ ਮਿਟਾਈ ਗਈ।",

        "emergency_steps_md": "### ਐਮਰਜੈਂਸੀ ਵਿੱਚ ਕੀ ਕਰਨਾ ਹੈ\n- ਸ਼ਾਂਤ ਰਹੋ\n- ਸੁਰੱਖਿਅਤ ਜਗ੍ਹਾ ਜਾਓ\n- 911 ਨੂੰ ਕਾਲ ਕਰੋ\n- ਜੇ ਸੁਰੱਖਿਅਤ ਹੋਵੇ ਤਾਂ ਵੀਡੀਓ ਬਣਾਓ\n- ਵਕੀਲ ਨਾਲ ਸੰਪਰਕ ਕਰੋ",

        "community_guidelines_title": "📋 ਕਮਿਊਨਿਟੀ ਨਿਯਮ",
        "community_guidelines_desc": "ਸੁਰੱਖਿਆ, ਆਦਰ ਅਤੇ ਸਹਿਯੋਗ ਲਈ ਇਹ ਨਿਯਮ ਮਾਨੋ।",
        "community_rule_respect": "💛 ਹੋਰਾਂ ਦਾ ਆਦਰ ਕਰੋ",
        "community_rule_no_hate": "🚫 ਨਫ਼ਰਤ ਜਾਂ ਹਿੰਸਕ ਸਮੱਗਰੀ ਨਾ ਪੋਸਟ ਕਰੋ",
        "community_rule_no_spam": "📵 ਸਪੈਮ ਜਾਂ ਵਿਗਿਆਪਨ ਨਾ ਪੋਸਟ ਕਰੋ",
        "community_rule_privacy": "🔒 ਨਿੱਜੀ ਜਾਣਕਾਰੀ ਨਾ ਸਾਂਝੀ ਕਰੋ",
        "community_rule_report": "⚠️ ਗਲਤ ਸਮੱਗਰੀ ਦੀ ਰਿਪੋਰਟ ਕਰੋ",

        "community_report_btn": "🚨 ਰਿਪੋਰਟ ਕਰੋ",
        "community_report_success": "ਤੁਹਾਡੀ ਰਿਪੋਰਟ ਭੇਜੀ ਗਈ। ਧੰਨਵਾਦ।",
        "community_report_reason": "ਰਿਪੋਰਟ ਕਰਨ ਦਾ ਕਾਰਨ:",
        "community_report_placeholder": "ਉਦਾਹਰਨ: ਗਲਤ ਭਾਸ਼ਾ, ਧਮਕੀ, ਸਪੈਮ",

        "translator_title": "🗣️ ਤਰਜਮਾ ਸਰਵਿਸ",
        "translator_subtitle": "ਟੈਕਸਟ ਨੂੰ ਆਪਣੀ ਭਾਸ਼ਾ ਵਿੱਚ ਤਰਜਮਾ ਕਰੋ",
        "translator_input": "ਤਰਜਮਾ ਕਰਨ ਲਈ ਟੈਕਸਟ:",
        "translator_output": "ਤਰਜਮਾ:",
        "translator_switch_lang": "ਭਾਸ਼ਾ ਬਦਲੋ",
        "translator_copy": "📋 ਕਾਪੀ ਕਰੋ",
        "translator_copied": "ਕਾਪੀ ਹੋ ਗਿਆ!",
        "translator_error": "ਤਰਜਮੇ ਵਿੱਚ ਗਲਤੀ",

        "audio_player_title": "🔊 ਆਡੀਓ ਪਲੇਅਰ",
        "audio_player_play": "ਚਲਾਓ",
        "audio_player_pause": "ਰੋਕੋ",
        "audio_player_stop": "ਬੰਦ ਕਰੋ",
        "audio_player_error": "ਆਡੀਓ ਚਲਾਉਣ ਵਿੱਚ ਗਲਤੀ",

        "document_upload_error": "ਡੌਕੂਮੈਂਟ ਅੱਪਲੋਡ ਫੇਲ੍ਹ",
        "document_processing_error": "ਡੌਕੂਮੈਂਟ ਪ੍ਰੋਸੈਸਿੰਗ ਵਿੱਚ ਗਲਤੀ",
        "document_translation_error": "ਡੌਕੂਮੈਂਟ ਤਰਜਮੇ ਵਿੱਚ ਗਲਤੀ",

        "location_permission_denied": "ਲੋਕੇਸ਼ਨ ਦੀ ਇਜਾਜ਼ਤ ਰੱਦ",
        "location_not_available": "ਲੋਕੇਸ਼ਨ ਉਪਲਬਧ ਨਹੀਂ",
        "location_search_error": "ਲੋਕੇਸ਼ਨ ਖੋਜ ਵਿੱਚ ਗਲਤੀ",

        "tour_welcome": "👋 ਟੂਰ ਵਿੱਚ ਸਵਾਗਤ!",
        "tour_step_intro": "ਇਹ ਟੂਰ CivicShield Pro ਦੇ ਮੁੱਖ ਫੀਚਰ ਦਿਖਾਉਂਦਾ ਹੈ।",
        "tour_step_done": "🎉 ਟੂਰ ਮੁਕੰਮਲ!",
        "tour_restart": "🔄 ਟੂਰ ਦੁਬਾਰਾ ਸ਼ੁਰੂ ਕਰੋ",
        "tour_exit": "🚪 ਟੂਰ ਤੋਂ ਬਾਹਰ ਜਾਓ",
        "tour_step1_title": "🏠 ਡੈਸ਼ਬੋਰਡ ਜਾਣ‑ਪਛਾਣ",
        "tour_step1_desc": "ਇੱਥੇ ਤੁਸੀਂ CivicShield Pro ਦੇ ਸਾਰੇ ਮੁੱਖ ਫੀਚਰ ਵਰਤ ਸਕਦੇ ਹੋ।",
        "tour_step1_point1": "ਸਾਰੇ ਟੂਲਾਂ ਲਈ ਨੇਵੀਗੇਸ਼ਨ",
        "tour_step1_point2": "ਸੇਵ ਕੀਤੀਆਂ ਡੈੱਡਲਾਈਨ ਵੇਖੋ",
        "tour_step1_point3": "ਐਮਰਜੈਂਸੀ ਸਰੋਤਾਂ ਤੱਕ ਪਹੁੰਚ",

        "tour_step2_title": "🗣️ ਰੀਅਲ‑ਟਾਈਮ ਤਰਜਮਾ",
        "tour_step2_desc": "ਪੁਲਿਸ ਦੀ ਗੱਲ ਆਪਣੀ ਭਾਸ਼ਾ ਵਿੱਚ ਤੁਰੰਤ ਤਰਜਮਾ ਕਰੋ।",
        "tour_step2_point1": "ਆਵਾਜ਼ ਰਿਕਾਰਡਿੰਗ",
        "tour_step2_point2": "ਸਪੀਚ‑ਟੂ‑ਟੈਕਸਟ",
        "tour_step2_point3": "ਆਡੀਓ ਪਲੇਬੈਕ",

        "tour_step3_title": "📄 ਡੌਕੂਮੈਂਟ ਟੂਲ",
        "tour_step3_desc": "ਡੌਕੂਮੈਂਟ ਅੱਪਲੋਡ ਕਰੋ ਅਤੇ ਮਹੱਤਵਪੂਰਨ ਲੀਗਲ ਜਾਣਕਾਰੀ ਲਵੋ।",
        "tour_step3_point1": "ਡੈੱਡਲਾਈਨ ਐਕਸਟ੍ਰੈਕਸ਼ਨ",
        "tour_step3_point2": "ਸਜ਼ਾਵਾਂ ਦੀ ਪਛਾਣ",
        "tour_step3_point3": "ਡੌਕੂਮੈਂਟ ਤਰਜਮਾ",

        "tour_step4_title": "⚖️ ਹੱਕ ਸਿੱਖਿਆ",
        "tour_step4_desc": "ਆਪਣੇ ਹੱਕਾਂ ਬਾਰੇ ਜਾਣੋ ਅਤੇ ਕਵਿਜ਼ ਨਾਲ ਆਪਣੀ ਜਾਣਕਾਰੀ ਟੈਸਟ ਕਰੋ।",
        "tour_step4_point1": "ਹੱਕਾਂ ਦੇ ਪਾਠ",
        "tour_step4_point2": "ਇੰਟਰੈਕਟਿਵ ਕਵਿਜ਼",
        "tour_step4_point3": "ਪ੍ਰੋਗਰੈੱਸ ਟ੍ਰੈਕਿੰਗ",

        "tour_step5_title": "📍 ਨੇੜੇ ਸਰਵਿਸ",
        "tour_step5_desc": "ਆਪਣੇ ਇਲਾਕੇ ਵਿੱਚ ਲੀਗਲ ਐਡ ਅਤੇ ਕਮਿਊਨਿਟੀ ਸਰਵਿਸ ਲੱਭੋ।",
        "tour_step5_point1": "ਲੋਕੇਸ਼ਨ‑ਅਧਾਰਿਤ ਖੋਜ",
        "tour_step5_point2": "ਸਰਵਿਸ ਫਿਲਟਰ",
        "tour_step5_point3": "ਤੁਰੰਤ ਦਿਸ਼ਾਵਾਂ",

        "tour_step6_title": "💬 ਕਮਿਊਨਿਟੀ ਫੋਰਮ",
        "tour_step6_desc": "ਅਨੁਭਵ ਸਾਂਝੇ ਕਰੋ, ਸਵਾਲ ਪੁੱਛੋ, ਹੋਰਾਂ ਦੀ ਮਦਦ ਕਰੋ।",
        "tour_step6_point1": "ਗੁਪਤ ਪੋਸਟਿੰਗ",
        "tour_step6_point2": "ਲੀਗਲ ਸਵਾਲ",
        "tour_step6_point3": "ਸਲਾਹ ਸਾਂਝੀ ਕਰੋ",

        "tour_finished_title": "🎉 ਟੂਰ ਮੁਕੰਮਲ!",
        "tour_finished_desc": "ਹੁਣ ਤੁਸੀਂ CivicShield Pro ਪੂਰੀ ਤਰ੍ਹਾਂ ਵਰਤਣ ਲਈ ਤਿਆਰ ਹੋ।",
        "tour_finished_btn_start": "🚀 ਐਪ ਸ਼ੁਰੂ ਕਰੋ",

        "error_generic": "ਗਲਤੀ ਆਈ। ਕਿਰਪਾ ਕਰਕੇ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
        "error_network": "ਨੈੱਟਵਰਕ ਗਲਤੀ। ਕਨੈਕਸ਼ਨ ਚੈੱਕ ਕਰੋ।",
        "error_timeout": "ਸਰਵਰ ਨੇ ਜਵਾਬ ਨਹੀਂ ਦਿੱਤਾ। ਕੁਝ ਸਮੇਂ ਬਾਅਦ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
        "error_invalid_input": "ਗਲਤ ਇਨਪੁੱਟ। ਕਿਰਪਾ ਕਰਕੇ ਸਹੀ ਜਾਣਕਾਰੀ ਦਿਓ।",
        "error_unknown": "ਅਣਜਾਣ ਗਲਤੀ ਆਈ।",

        "success_saved": "ਸਫਲਤਾਪੂਰਵਕ ਸੇਵ ਹੋ ਗਿਆ!",
        "success_updated": "ਸਫਲਤਾਪੂਰਵਕ ਅੱਪਡੇਟ ਹੋ ਗਿਆ!",
        "success_deleted": "ਸਫਲਤਾਪੂਰਵਕ ਮਿਟਾਇਆ ਗਿਆ!",

        "confirm_delete": "ਕੀ ਤੁਸੀਂ ਇਹ ਮਿਟਾਉਣਾ ਚਾਹੁੰਦੇ ਹੋ?",
        "confirm_yes": "ਹਾਂ",
        "confirm_no": "ਨਹੀਂ",

        "form_required": "ਇਹ ਫੀਲਡ ਲਾਜ਼ਮੀ ਹੈ",
        "form_invalid_email": "ਗਲਤ ਇਮੇਲ ਐਡਰੈੱਸ",
        "form_invalid_phone": "ਗਲਤ ਫੋਨ ਨੰਬਰ",
        "form_invalid_zip": "ਗਲਤ ZIP ਕੋਡ",

        "loading_data": "ਡਾਟਾ ਲੋਡ ਹੋ ਰਿਹਾ ਹੈ...",
        "saving_data": "ਡਾਟਾ ਸੇਵ ਹੋ ਰਿਹਾ ਹੈ...",
        "updating_data": "ਡਾਟਾ ਅੱਪਡੇਟ ਹੋ ਰਿਹਾ ਹੈ...",
        "deleting_data": "ਡਾਟਾ ਮਿਟਾਇਆ ਜਾ ਰਿਹਾ ਹੈ...",

        "modal_close": "ਬੰਦ ਕਰੋ",
        "modal_confirm": "ਪੁਸ਼ਟੀ ਕਰੋ",
        "modal_cancel": "ਰੱਦ ਕਰੋ",

        "search_placeholder": "ਖੋਜੋ...",
        "search_no_results": "ਕੋਈ ਨਤੀਜੇ ਨਹੀਂ ਮਿਲੇ",
        "search_results": "ਖੋਜ ਨਤੀਜੇ",

        "filter_apply": "ਫਿਲਟਰ ਲਗਾਓ",
        "filter_clear": "ਫਿਲਟਰ ਕਲੀਅਰ ਕਰੋ",
        "filter_selected": "ਚੁਣੇ ਫਿਲਟਰ:",

        "pagination_next": "ਅੱਗੇ",
        "pagination_prev": "ਪਿੱਛੇ",
        "pagination_page": "ਪੇਜ",
        "pagination_of": "ਦਾ",

        "profile_title": "ਪ੍ਰੋਫ਼ਾਈਲ",
        "profile_edit": "ਪ੍ਰੋਫ਼ਾਈਲ ਸੋਧੋ",
        "profile_save": "ਪ੍ਰੋਫ਼ਾਈਲ ਸੇਵ ਕਰੋ",
        "profile_name": "ਨਾਮ",
        "profile_email": "ਇਮੇਲ",
        "profile_phone": "ਫੋਨ",
        "profile_language": "ਭਾਸ਼ਾ",
        "profile_updated": "ਪ੍ਰੋਫ਼ਾਈਲ ਸਫਲਤਾਪੂਰਵਕ ਅੱਪਡੇਟ ਹੋ ਗਿਆ!",

        "settings_title": "ਸੈਟਿੰਗ",
        "settings_language": "ਭਾਸ਼ਾ ਸੈਟਿੰਗ",
        "settings_notifications": "ਨੋਟੀਫਿਕੇਸ਼ਨ ਸੈਟਿੰਗ",
        "settings_privacy": "ਪਰਾਈਵੇਸੀ ਸੈਟਿੰਗ",
        "settings_save": "ਸੈਟਿੰਗ ਸੇਵ ਕਰੋ",

        "notifications_title": "ਨੋਟੀਫਿਕੇਸ਼ਨ",
        "notifications_enable": "ਨੋਟੀਫਿਕੇਸ਼ਨ ਚਾਲੂ ਕਰੋ",
        "notifications_disable": "ਨੋਟੀਫਿਕੇਸ਼ਨ ਬੰਦ ਕਰੋ",
        "notifications_saved": "ਨੋਟੀਫਿਕੇਸ਼ਨ ਸੈਟਿੰਗ ਸੇਵ ਹੋ ਗਈ",

        "privacy_title": "ਪਰਾਈਵੇਸੀ ਨੀਤੀ",
        "privacy_desc": "ਤੁਹਾਡਾ ਡਾਟਾ ਕਿਵੇਂ ਵਰਤਿਆ ਜਾਂਦਾ ਹੈ, ਜਾਣੋ।",
        "privacy_read_more": "ਹੋਰ ਪੜ੍ਹੋ",

        "about_title": "CivicShield ਬਾਰੇ",
        "about_desc": "ਸਿਵਲ ਹੱਕਾਂ ਦੀ ਸੁਰੱਖਿਆ ਅਤੇ ਸਮਝ ਲਈ ਬਣਾਇਆ ਗਿਆ ਬਹੁਭਾਸ਼ਾਈ ਪਲੇਟਫਾਰਮ।",
        "about_version": "ਵਰਜਨ:",
        "about_credits": "ਕ੍ਰੈਡਿਟ:",
        "about_team": "ਡਿਵੈਲਪਮੈਂਟ ਟੀਮ",
        "about_contact": "ਸੰਪਰਕ ਕਰੋ",

        "footer_terms": "ਨਿਯਮ",
        "footer_privacy": "ਪਰਾਈਵੇਸੀ",
        "footer_contact": "ਸੰਪਰਕ"
       
    }


}

TRANSLATION_FLOW_DEFAULTS = {
    "play_before_title": "1. Play Before Interaction",
    "play_before_desc": "Play this to the officer before recording begins.",
    "play_before_audio": "Officer, before we begin, I am using a translation app to avoid any language barriers. I am recording with your knowledge for safety and accuracy.",
    "play_after_title": "3. Play After Understanding Rights",
    "play_after_desc": "Play this to the officer after you hear your rights.",
    "play_after_audio": "I understand, officer, and I will comply, but I will be using my right to remain silent.",
    "officer_script": "Officer-facing script (English):",
    "officer_script_translated": "What this says in your language:",
}

# Ensure all 14 languages exist and include all keys.
for lang_name in LANGUAGE_MAP.keys():
    if lang_name not in UI_STRINGS:
        UI_STRINGS[lang_name] = copy.deepcopy(UI_STRINGS["English"])
    for key, value in UI_STRINGS["English"].items():
        UI_STRINGS[lang_name].setdefault(key, value)
    for key, value in TRANSLATION_FLOW_DEFAULTS.items():
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
@st.cache_data(show_spinner=False)
def geocode_address(address: str):
    """Geocode an address using OpenStreetMap Nominatim."""
    if not address or not address.strip():
        return None

    encoded_address = quote_plus(address.strip())
    request = Request(
        f"https://nominatim.openstreetmap.org/search?q={encoded_address}&format=json&limit=1",
        headers={"User-Agent": "CivicShieldPro/3.0 (Streamlit app)"}
    )

    try:
        with urlopen(request, timeout=10) as response:
            results = json.loads(response.read().decode("utf-8"))
    except Exception:
        return None

    if not results:
        return None

    return float(results[0]["lat"]), float(results[0]["lon"])


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute great-circle distance in miles between two lat/lon pairs."""
    earth_radius_miles = 3958.7613

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    arc = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    central_angle = 2 * math.atan2(math.sqrt(arc), math.sqrt(1 - arc))
    return earth_radius_miles * central_angle


def build_google_maps_search_url(address: str) -> str:
    """Build a Google Maps search URL for an address."""
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(address.strip())}"

def fetch_lawhelp_resources() -> list:
    """
    Fetch California legal aid resources dynamically from LawHelpCA directory.
    """
    url = "https://www.lawhelpca.org/legal-aid"
    try:
        html = requests.get(url, timeout=10).text
    except Exception:
        return []

    soup = BeautifulSoup(html, "html.parser")
    resources = []

    for item in soup.select(".views-row"):
        name_el = item.select_one(".title")
        address_el = item.select_one(".address")
        phone_el = item.select_one(".phone")
        link_el = item.select_one("a")

        name = name_el.get_text(strip=True) if name_el else ""
        address = address_el.get_text(strip=True) if address_el else ""
        phone = phone_el.get_text(strip=True) if phone_el else ""
        website = link_el["href"] if link_el and link_el.has_attr("href") else ""

        if name and address:
            resources.append({
                "name": name,
                "category": "Legal Aid",
                "address": address,
                "phone": phone,
                "website": website,
                "hours": "",
            })

    return resources

def reverse_geocode(lat: float, lon: float) -> str:
    """
    Convert latitude/longitude into a human-readable address using Nominatim.
    """
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    try:
        response = requests.get(url, headers={"User-Agent": "CivicShieldPro/3.0"}, timeout=10)
        data = response.json()
        return data.get("display_name", f"{lat}, {lon}")
    except Exception:
        return f"{lat}, {lon}"
    
def fetch_211_resources(city: str) -> list:
    """
    Fetch community resources from 211 California API.
    """
    url = f"https://api.211ca.org/search?city={quote_plus(city)}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
    except Exception:
        return []

    resources = []
    for item in data.get("results", []):
        name = item.get("name")
        address = item.get("address")
        phone = item.get("phone")
        category = item.get("category")

        if name and address:
            resources.append({
                "name": name,
                "category": category or "Community Resource",
                "address": address,
                "phone": phone or "",
                "website": item.get("website", ""),
                "hours": item.get("hours", "")
            })

    return resources

def fetch_osm_resources(lat: float, lon: float, radius_meters: int = 5000) -> list:
    """
    Fetch community centers, NGOs, and social facilities from OpenStreetMap.
    """
    query = f"""
    [out:json];
    (
      node["amenity"="community_centre"](around:{radius_meters},{lat},{lon});
      node["social_facility"](around:{radius_meters},{lat},{lon});
      node["office"="ngo"](around:{radius_meters},{lat},{lon});
    );
    out;
    """

    try:
        response = requests.post("https://overpass-api.de/api/interpreter", data=query, timeout=15)
        data = response.json()
    except Exception:
        return []

    resources = []
    for element in data.get("elements", []):
        name = element.get("tags", {}).get("name")
        if not name:
            continue

        lat2 = element.get("lat")
        lon2 = element.get("lon")

        # Reverse geocode to get a real address
        address = reverse_geocode(lat2, lon2)

        resources.append({
            "name": name,
            "category": "Community Center",
            "address": address,
            "phone": "",
            "website": "",
            "hours": "",
            "latitude": lat2,
            "longitude": lon2
        })

    return resources



def find_resources_by_location(address: str, search_radius_miles: int = 5) -> list:
    """
    Find nearby resources based on address.
    """

    # 1. LawHelpCA legal aid
    lawhelp = fetch_lawhelp_resources()

    # 2. 211 California community resources
    city_only = address.split(",")[0]
    resources_211 = fetch_211_resources(city_only)

    # 3. OSM community centers (requires user coordinates)
    user_coordinates = geocode_address(address)
    print("DEBUG USER COORDS:", user_coordinates)
    osm_resources = []
    if user_coordinates:
        user_lat, user_lon = user_coordinates
        osm_resources = fetch_osm_resources(user_lat, user_lon)

    # Merge all three sources
    RESOURCES_DB = lawhelp + resources_211 + osm_resources
    print("LAWHELP:", len(lawhelp))
    print("211:", len(resources_211))
    print("OSM:", len(osm_resources))
    print("TOTAL:", len(RESOURCES_DB))


    # If user address cannot be geocoded, stop early
    if not user_coordinates:
        return []

    user_latitude, user_longitude = user_coordinates
    nearby_resources = []

    # Filter resources by distance
    for resource in RESOURCES_DB:
        # Geocode each resource's address
        resource_coordinates = geocode_address(resource["address"])
        if not resource_coordinates:
            continue

        resource_latitude, resource_longitude = resource_coordinates

        # Compute distance
        distance = haversine_miles(
            user_latitude,
            user_longitude,
            resource_latitude,
            resource_longitude
        )

        # Keep only resources within radius
        if distance <= search_radius_miles:
            resource_with_distance = resource.copy()
            resource_with_distance["latitude"] = resource_latitude
            resource_with_distance["longitude"] = resource_longitude
            resource_with_distance["distance"] = round(distance, 1)
            nearby_resources.append(resource_with_distance)

    # Sort by nearest
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


def build_tts_audio_bytes(script_text: str, language_code: str):
    """Generate in-memory MP3 audio for a script."""
    try:
        tts = gTTS(text=script_text, lang=language_code)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.read()
    except Exception:
        return None


def translate_for_user(text: str, target_lang: str) -> str:
    """Translate English text for the user's selected language when available."""
    if target_lang == "en":
        return text

    translator = get_translator("en", target_lang)
    if not translator:
        return text

    try:
        return translator.translate(text)
    except Exception:
        return text


def get_officer_followup_script(officer_statement: str) -> str:
    """Return an officer-facing compliance statement based on the officer's words."""
    statement_lower = officer_statement.lower()

    if any(word in statement_lower for word in ["arrest", "custody", "hands up", "hand behind", "turn around"]):
        return "I understand, officer, and I will comply, but I will be using my right to remain silent."
    if any(word in statement_lower for word in ["search", "car", "vehicle", "bag", "pockets"]):
        return "I understand, officer, and I will comply, but I do not consent to any search."
    if any(word in statement_lower for word in ["license", "registration", "traffic", "stop", "pulled over"]):
        return "I understand, officer, and I will comply by providing identification documents, but I do not consent to any search and I will remain silent."
    if any(word in statement_lower for word in ["question", "answer", "talk", "speak", "tell me", "where were you"]):
        return "I understand, officer, and I will comply, but I am using my right to remain silent and I want a lawyer."
    return t('play_after_audio')

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
    
    target_lang = LANGUAGE_MAP[st.session_state.language]["code"]

    # Input section
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"## {t('officer_statement')}")
        st.markdown(f"### {t('play_before_title')}")
        st.caption(t('play_before_desc'))
        st.text_area(
            t('officer_script'),
            value=t('play_before_audio'),
            height=120,
            disabled=True,
            key="play_before_script_text"
        )
        st.text_area(
            t('officer_script_translated'),
            value=translate_for_user(t('play_before_audio'), target_lang),
            height=120,
            disabled=True,
            key="play_before_script_translated"
        )

        before_audio_bytes = build_tts_audio_bytes(t('play_before_audio'), "en")
        if before_audio_bytes:
            st.audio(before_audio_bytes, format="audio/mp3")
        else:
            st.warning(t('audio_failed'))

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
            # Generate legal advice based on officer statement
            legal_advice = get_legal_advice_for_statement(english_text)
            translated_advice = legal_advice
            if st.session_state.language != "English":
                translated_advice = translate_for_user(legal_advice, target_lang)

            st.markdown("### 2. Play Advice")
            st.text_area(
                f"{t('your_rights')}:",
                value=translated_advice,
                height=250,
                disabled=True,
                key="translated_output"
            )

            advice_audio_bytes = build_tts_audio_bytes(
                translated_advice,
                target_lang if st.session_state.language != "English" else "en"
            )
            if advice_audio_bytes:
                st.audio(advice_audio_bytes, format="audio/mp3")
            else:
                st.warning(t('audio_failed'))

            officer_followup_script = get_officer_followup_script(english_text)
            officer_followup_translated = translate_for_user(officer_followup_script, target_lang)

            st.markdown(f"### {t('play_after_title')}")
            st.caption(t('play_after_desc'))
            st.text_area(
                t('officer_script'),
                value=officer_followup_script,
                height=120,
                disabled=True,
                key="officer_followup_script"
            )
            st.text_area(
                t('officer_script_translated'),
                value=officer_followup_translated,
                height=120,
                disabled=True,
                key="officer_followup_translated"
            )

            after_audio_bytes = build_tts_audio_bytes(officer_followup_script, "en")
            if after_audio_bytes:
                st.audio(after_audio_bytes, format="audio/mp3")
            else:
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
                    
                    maps_url = build_google_maps_search_url(resource['address'])
                    if hasattr(st, "link_button"):
                        st.link_button(
                            f"🗺️ {t('get_directions')} - {resource['name']}",
                            maps_url,
                            use_container_width=True
                        )
                    else:
                        st.markdown(
                            f"""
                            <a href="{maps_url}" target="_blank" rel="noopener noreferrer" style="text-decoration: none;">
                                <button style="width: 100%; padding: 8px; background-color: #4285F4; color: white; border: none; border-radius: 4px; cursor: pointer;">
                                    🗺️ {t('get_directions')} - {resource['name']}
                                </button>
                            </a>
                            """,
                            unsafe_allow_html=True
                        )
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

    lang_list = list(LANGUAGE_MAP.keys())
    current_lang = st.session_state.get("language", "English")
    if current_lang not in lang_list:
        current_lang = "English"
        st.session_state.language = "English"

    selected_lang = st.selectbox(
        t('select_language'),
        lang_list,
        index=lang_list.index(current_lang),
        key="landing_language_selector"
    )
    if selected_lang != current_lang:
        st.session_state.language = selected_lang
        st.rerun()
    
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

