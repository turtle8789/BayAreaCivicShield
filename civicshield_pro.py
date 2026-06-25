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
}

# Add fallback for all other languages (map to English)
for lang_name in LANGUAGE_MAP.keys():
    if lang_name not in UI_STRINGS:
        UI_STRINGS[lang_name] = UI_STRINGS["English"]

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
def init_session_state():
    """Initialize all session state variables on first run."""
    if "page" not in st.session_state:
        st.session_state.page = "Landing"  # Show landing page first
    if "selected_language" not in st.session_state:
        st.session_state.selected_language = "English"
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
    Get translated UI string for the current language.
    Fallback to English if translation not available.
    Usage: st.markdown(t('home_title'))
    """
    lang = st.session_state.selected_language
    if lang in UI_STRINGS and key in UI_STRINGS[lang]:
        return UI_STRINGS[lang][key]
    elif key in UI_STRINGS["English"]:
        return UI_STRINGS["English"][key]
    else:
        return key  # Return the key if not found

def t_bilingual(key: str) -> str:
    """
    Get bilingual text: Selected Language / English
    Example: Traduccion / Translation
    Usage: st.markdown(t_bilingual('translation_title'))
    """
    lang = st.session_state.selected_language
    if lang == "English":
        return t(key)
    
    selected_text = t(key)
    english_text = UI_STRINGS["English"].get(key, key)
    
    if selected_text != english_text:
        return f"{selected_text} / {english_text}"
    return selected_text

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
- Police can search your car if they find probable cause
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
        st.info("📺 **DEMO MODE ACTIVE** - This is sample data for demonstration purposes")
    
    st.markdown(f"# 🏠 {t_bilingual('home_title')}")
    st.markdown(f"## {t_bilingual('home_subtitle')}")
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
                if st.button("❌", key=f"del_deadline_{deadline.get('id')}"):
                    if not st.session_state.demo_mode:  # Don't delete in demo mode
                        delete_deadline(deadline.get('id'))
                        st.rerun()
        
        if st.button(t('view_all_deadlines'), use_container_width=True):
            st.session_state.page = "DocumentAssistant"
            st.rerun()
        st.divider()
    
    st.markdown(f"### {t_bilingual('dashboard_intro')}")
    
    # Create feature cards in a 2-column grid layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Real-Time Translation Card
        with st.container():
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-icon">🗣️</div>
                <div class="card-title">{t_bilingual('card_translation_title')}</div>
                <div class="card-description">{t('card_translation_desc')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("📖 Open Feature", use_container_width=True, key="open_translation"):
                st.session_state.page = "Translation"
                st.rerun()
        
        st.divider()
        
        # Legal Documents Card
        with st.container():
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-icon">📄</div>
                <div class="card-title">{t_bilingual('card_documents_title')}</div>
                <div class="card-description">{t('card_documents_desc')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("📖 Open Feature", use_container_width=True, key="open_documents"):
                st.session_state.page = "DocumentAssistant"
                st.rerun()
        
        st.divider()
        
        # Know Your Rights Card
        with st.container():
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-icon">⚖️</div>
                <div class="card-title">{t_bilingual('card_rights_title')}</div>
                <div class="card-description">{t('card_rights_desc')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("📖 Open Feature", use_container_width=True, key="open_rights"):
                st.session_state.page = "KnowYourRights"
                st.rerun()
        
        st.divider()
        
        # Resources Near You Card
        with st.container():
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-icon">📍</div>
                <div class="card-title">{t_bilingual('card_nearby_title')}</div>
                <div class="card-description">{t('card_nearby_desc')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("📖 Open Feature", use_container_width=True, key="open_nearby"):
                st.session_state.page = "ResourcesNearYou"
                st.rerun()
    
    with col2:
        # Encounter Log Card
        with st.container():
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-icon">📝</div>
                <div class="card-title">{t_bilingual('card_logging_title')}</div>
                <div class="card-description">{t('card_logging_desc')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("📖 Open Feature", use_container_width=True, key="open_logging"):
                st.session_state.page = "EncounterLogging"
                st.rerun()
        
        st.divider()
        
        # Crisis Resources Card
        with st.container():
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-icon">🚨</div>
                <div class="card-title">{t_bilingual('card_emergency_title')}</div>
                <div class="card-description">{t('card_emergency_desc')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("📖 Open Feature", use_container_width=True, key="open_crisis"):
                st.session_state.page = "CrisisResources"
                st.rerun()
        
        st.divider()
        
        # Community Discussion Card
        with st.container():
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-icon">💬</div>
                <div class="card-title">{t_bilingual('card_resources_title')}</div>
                <div class="card-description">{t('card_resources_desc')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("📖 Open Feature", use_container_width=True, key="open_community"):
                st.session_state.page = "CommunityDiscussion"
                st.rerun()

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
        st.markdown("""
        <div class="translation-shell">
            <h3>Microphone Recorder</h3>
            <p>Use Start Recording and Stop Recording to capture officer speech.</p>
            <div class="mic-help">If your browser blocks microphone access, allow microphone permission and record again.</div>
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
            st.session_state.translation_mic_error = (
                "Microphone access failed. Please allow browser microphone permission and try again."
            )

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
                    st.success("Speech captured and converted to text.")
                except sr.UnknownValueError:
                    st.session_state.translation_transcript = ""
                    st.session_state.translation_mic_error = "Could not understand the recorded speech. Please speak clearly and try again."
                except sr.RequestError:
                    st.session_state.translation_transcript = ""
                    st.session_state.translation_mic_error = "Speech-to-text service is currently unavailable. Please try again in a moment."
                except Exception:
                    st.session_state.translation_transcript = ""
                    st.session_state.translation_mic_error = "Unable to process recorded audio. Please record again."
            else:
                st.session_state.translation_mic_error = (
                    "No audio was captured. Microphone permission may be denied. Allow access and try recording again."
                )

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
            target_lang = LANGUAGE_MAP[st.session_state.selected_language]["code"]
            
            if st.session_state.selected_language != "English":
                try:
                    translator = get_translator("en", target_lang)
                    if translator:
                        translated = translator.translate(english_text)
                        st.text_area(
                            f"{t('card_translation_title')}:",
                            value=translated,
                            height=200,
                            disabled=True,
                            key="translated_output"
                        )

                        try:
                            tts = gTTS(text=translated, lang=target_lang)
                            audio_buffer = io.BytesIO()
                            tts.write_to_fp(audio_buffer)
                            audio_buffer.seek(0)
                            st.audio(audio_buffer.read(), format="audio/mp3")
                        except Exception:
                            st.warning(t('audio_failed'))
                except:
                    st.error(t('error'))
            else:
                st.info(f"{st.session_state.selected_language} - No translation needed")

def page_documents():
    """Legal document assistant page with OCR and extraction."""
    st.markdown(f"# 📄 {t_bilingual('documents_title')}")
    st.markdown(f"_{t_bilingual('documents_subtitle')}_")
    st.divider()
    
    st.markdown("""
    Upload a legal document (image or PDF) to extract key information:
    - Important dates and deadlines
    - Required actions
    - Penalties and warnings
    - Government agencies
    """)
    
    # Document upload interface
    tab1, tab2 = st.tabs([t('upload_document'), "📋 Document Extraction"])
    
    with tab1:
        st.markdown(f"### {t('upload_legal_doc')}")
        uploaded_file = st.file_uploader(
            "Choose a document (PDF, JPG, PNG)",
            type=["pdf", "jpg", "jpeg", "png"],
            key="doc_uploader"
        )
        
        if uploaded_file:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
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
                                        "language": st.session_state.selected_language
                                    }
                                    save_deadline(deadline_data)
                                st.success(f"✅ Saved {len(extracted['deadlines'])} deadline(s) to your dashboard!")
                            else:
                                st.warning("⚠️ No deadlines to save")
    
    with tab2:
        st.markdown(f"### {t('extraction_guide')}")
        st.markdown("""
        **This tool can extract:**
        - **Dates**: Court dates, deadlines, filing dates
        - **Deadlines**: "Must respond by...", "Appear on..."
        - **Actions**: What you need to do
        - **Penalties**: Fines, consequences for non-compliance
        - **Agencies**: Court, government offices mentioned
        
        **Works best with:**
        - ✅ Clear, printed documents
        - ✅ Good lighting and contrast
        - ✅ English language text
        - ✅ High resolution images
        
        **May have issues with:**
        - ❌ Handwritten documents
        - ❌ Very old or damaged documents
        - ❌ Multiple languages mixed
        - ❌ Low quality images
        """)

def page_resources_near_you():
    """Unified Resources Near You - location-based legal aid and community services finder."""
    st.markdown(f"# 📍 {t_bilingual('location_title')}")
    st.markdown(f"_{t_bilingual('nearby_subtitle')}_")
    st.divider()
    
    # Resource search interface
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        address = st.text_input(
            t_bilingual('enter_address'),
            placeholder="Enter address, city, or ZIP code",
            key="resource_address"
        )
        add_screen_reader_label(f"Enter address for resource search: {address}")
    
    with col2:
        radius = st.slider(
            t_bilingual('search_radius_miles'),
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
            st.success(f"✅ {t_bilingual('found_resources')}: {len(resources)} {t_bilingual('resources_found')} {t_bilingual('within_miles')} {radius}")
            
            # Display resources in modern cards
            for idx, resource in enumerate(resources):
                with st.container():
                    st.markdown(f"""
                    <div class="dashboard-card">
                        <div class="card-icon">📍</div>
                        <div class="card-title">{resource['name']}</div>
                        <div class="card-description">
                            <p><strong>{t_bilingual('distance_away')}:</strong> {resource['distance']} miles</p>
                            <p><strong>{t_bilingual('resource_address')}:</strong> {resource['address']}</p>
                            <p><strong>{t_bilingual('resource_phone')}:</strong> {resource['phone']}</p>
                            <p><strong>{t_bilingual('resource_hours')}:</strong> {resource['hours']}</p>
                            <p><strong>Website:</strong> {resource['website']}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Get Directions button - opens Google Maps
                    if st.button(f"🗺️ {t_bilingual('get_directions')} - {resource['name']}", use_container_width=True, key=f"directions_{idx}"):
                        # Build Google Maps URL
                        address_encoded = resource['address'].replace(' ', '+')
                        maps_url = f"https://www.google.com/maps/search/{address_encoded}/"
                        st.markdown(f"""
                        <a href="{maps_url}" target="_blank">
                        <button style="width: 100%; padding: 8px; background-color: #4285F4; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        🗺️ Open in Google Maps
                        </button>
                        </a>
                        """, unsafe_allow_html=True)
                        st.success(f"📍 Opening maps to: {resource['name']}")
        else:
            st.warning(f"⚠️ {t('no_resources_found')}")
    
    # Browse by Resource Type
    st.divider()
    st.markdown(f"### 📋 {t_bilingual('browse_resources')}")
    
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
        st.info(f"📁 Currently filtering by: **{st.session_state.resource_category_filter}**")
        if st.button("❌ Clear Filter", use_container_width=True):
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
        
        selected_right = st.selectbox(
            t('select_topic'),
            list(RIGHTS_EDUCATION.keys()),
            key="rights_select"
        )
        
        if selected_right:
            right = RIGHTS_EDUCATION[selected_right]
            st.markdown(f"### {right['title']}")
            st.markdown(right['content'])
            
            # Progress indicator
            progress_pct = (list(RIGHTS_EDUCATION.keys()).index(selected_right) + 1) / len(RIGHTS_EDUCATION) * 100
            st.progress(progress_pct / 100)
            st.caption(f"📖 Topic {list(RIGHTS_EDUCATION.keys()).index(selected_right) + 1} of {len(RIGHTS_EDUCATION)}")
    
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
                    st.success("✅ Correct!")
                    score += 1
                else:
                    st.error(f"❌ Incorrect. {q['explanation']}")
            st.divider()
        
            if quiz_pct:
                quiz_pct = (score / len(quiz_questions)) * 100
                st.progress(quiz_pct / 100)
                st.metric(t('your_score'), f"{score}/{len(quiz_questions)}", f"{quiz_pct:.0f}%")

def page_community_discussion():
    """Talk to Your Community - Safe community discussion space."""
    st.markdown(f"# 💬 Talk to Your Community")
    st.markdown(f"_Share experiences, ask questions, give advice - together we are stronger_")
    st.divider()
    
    # Tabs for different community features
    tab1, tab2, tab3 = st.tabs(["💭 Share Experiences", "❓ Ask Questions", "💡 Give Advice"])
    
    with tab1:
        st.markdown("### 💭 Share Your Experience")
        st.markdown("Share your story to help others. All posts are moderated for safety.")
        
        post_title = st.text_input("Title:", placeholder="e.g., Tips for dealing with traffic stops", key="exp_title")
        post_content = st.text_area("Your story:", placeholder="Share your experience...", height=200, key="exp_content")
        anonymous = st.checkbox("Post anonymously", value=True, key="exp_anon")
        
        if st.button(t('share_exp_btn'), use_container_width=True, key="submit_exp"):
            if post_title and post_content:
                post = {
                    "type": "experience",
                    "title": post_title,
                    "content": post_content,
                    "anonymous": anonymous,
                    "author": "Anonymous" if anonymous else "Community Member"
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
                    "author": "Anonymous" if anonymous else "Community Member",
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
                    "author": "Anonymous" if anonymous else "Community Member"
                }
                save_community_post(post)
                st.success(t('share_wisdom'))
            else:
                st.warning(t('fill_topic_advice'))
    
    # Display recent community posts
    st.divider()
    st.markdown("## 📋 Recent Community Posts")
    
    if st.session_state.community_posts:
        # Sort by newest first
        sorted_posts = sorted(st.session_state.community_posts, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]
        
        for post in sorted_posts:
            with st.expander(f"{post.get('type', '').title()} - {post['title']} - {post['author']}"):
                st.markdown(post.get("content", ""))
                st.caption(f"Posted {post.get('timestamp', 'recently')}")
    else:
        st.info("💭 No community posts yet. Be the first to share!")

def page_crisis_resources():
    """Crisis Resources & Hotlines - Emergency assistance and mental health support."""
    st.markdown(f"# {t('crisis_hotlines')}")
    st.markdown(f"_{t('crisis_support_24')}_")
    st.divider()
    
    # Critical hotlines section
    st.markdown(f"## {t('emergency_hotlines_header')}")
    st.markdown(f"**{t('in_immediate_danger')}**")
    
    crisis_contacts = {
        "🆘 Emergency / Emergencia": "911",
        "🧠 National Suicide Prevention Lifeline": "988",
        "💔 National Domestic Violence Hotline": "1-800-799-7233",
        "🤝 RAINN - Sexual Assault Support": "1-800-656-4673",
        "☠️ Poison Control Center": "1-800-222-1222",
        "📱 Crisis Text Line": "Text HOME to 741741"
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
        ("🛡️ Stay Safe", "Keep yourself safe - do not physically resist. Your safety is the priority."),
        ("📝 Document Details", "Remember: officer names, badge numbers, locations, times, what they said and did."),
        ("🎥 Record Safely", "If safe and legal in your area, record the interaction. Keep the camera visible."),
        ("📞 Call for Help", "Call 911 if in immediate danger. Stay calm and clear when explaining."),
        ("⚖️ Get Legal Help", "Contact an attorney immediately. Many public defenders offer emergency services."),
        ("🏥 Medical Attention", "If injured, seek medical care and document injuries with photos.")
    ]
    
    for title, desc in procedures:
        with st.container():
            st.markdown(f"### {title}")
            st.write(desc)
    
    st.divider()
    
    # Mental health and support
    st.markdown(f"## {t('mental_health_support')}")
    st.markdown("""
    Experiencing legal troubles, police encounters, or discrimination can be traumatic.
    
    **Mental health resources:**
    - **SAMHSA National Helpline**: 1-800-662-4357 (free, confidential, 24/7)
    - **Crisis Text Line**: Text HOME to 741741
    - **Local therapists**: Search Psychology Today's directory
    - **Support groups**: NAACP, community centers, legal aid organizations often host support groups
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
            ["Traffic Stop", "Street Encounter", "Arrest", "Search", "Other"],
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
                "language": st.session_state.selected_language
            }
            save_encounter(encounter)
            st.success(t('encounter_saved'))
    
    with tab2:
        st.markdown(f"## {t('view_history')}")
        encounters = st.session_state.encounter_log
        
        if encounters:
            st.write(f"{t('total_encounters')}{len(encounters)}")
            for i, enc in enumerate(reversed(encounters)):
                with st.expander(f"Encounter {len(encounters)-i}: {enc.get('type', 'Unknown')} - {enc.get('timestamp', 'N/A')}"):
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
        st.error(f"Error generating QR code: {e}")
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
    
    st.markdown("""
    <div class="landing-hero">
        <h1>⚖️ CivicShield Pro</h1>
        <h2>Know Your Rights. Protect Yourself. Get Help.</h2>
        <p>A professional, multi-language platform empowering people to understand and assert their civil rights in real-time encounters.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        ### 🎯 Purpose
        CivicShield Pro provides judges, advocates, and community members with:
        
        - **Real-time legal translation** in 14 languages
        - **Instant rights information** tailored to your situation
        - **Document analysis** with deadline extraction
        - **Community support** and shared experiences
        - **Crisis resources** available 24/7
        """)
    
    with col2:
        st.markdown("""
        ### ⭐ Key Features
        
        - 🗣️ **Real-Time Translation** - Translate officer statements instantly
        - 📄 **Legal Documents** - Extract key info from court documents
        - ⚖️ **Know Your Rights** - Learn civil rights with interactive quiz
        - 📍 **Resources Near You** - Find legal aid & services by location
        - 📝 **Encounter Log** - Document police interactions
        - 🚨 **Crisis Hotlines** - 24/7 emergency support
        - 💬 **Community Forum** - Share and learn from others
        """)
    
    st.divider()
    
    # Demo and Tutorial buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Launch App", use_container_width=True):
            st.session_state.skip_landing = True
            st.session_state.first_time_user = True
            st.session_state.page = "Tutorial"
            st.rerun()
    
    with col2:
        if st.button("📺 Start Demo", use_container_width=True):
            st.session_state.demo_mode = True
            st.session_state.skip_landing = True
            st.session_state.page = "Home"
            st.rerun()
    
    with col3:
        if st.button("❓ Quick Tour", use_container_width=True):
            st.session_state.skip_landing = True
            st.session_state.tutorial_step = 0
            st.session_state.page = "Tutorial"
            st.rerun()
    
    st.divider()
    
    # QR Code for easy sharing
    st.markdown("### 📱 Share with Others")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Share CivicShield with judges, advocates, and community members:**
        
        1. Scan the QR code to access the app
        2. No installation needed - works in any browser
        3. Available in 14 languages
        4. Works on desktop, tablet, and mobile
        """)
    
    with col2:
        # Generate QR code for app URL (in production, use actual deployment URL)
        try:
            app_url = "https://civicshield-pro.streamlit.app"  # Update with actual deployment URL
            qr_img = generate_qr_code(app_url)
            if qr_img:
                st.image(qr_img, use_column_width=True)
        except:
            st.info("QR code generation in progress...")
    
    st.divider()
    
    # Target users
    st.markdown("""
    ### 👥 Who Should Use CivicShield?
    
    **For Judges & Legal Professionals:**
    - Understand community perspective on civil rights protection
    - Assess whether defendants understand their rights
    - Reference real-time translation capabilities in decisions
    
    **For Advocates & Legal Aid:**
    - Provide clients with multi-language legal information
    - Help clients document encounters
    - Connect community members with resources
    
    **For Educators:**
    - Teach students about civil rights
    - Demonstrate real-world legal scenarios
    - Interactive learning with quizzes
    
    **For Community Members:**
    - Know what to do in a police encounter
    - Access emergency resources instantly
    - Connect with and learn from community experiences
    """)
    
    st.divider()
    
    # Footer with disclaimer
    st.warning("""
    **⚠️ Legal Disclaimer:**
    
    CivicShield Pro provides educational information about civil rights, not legal advice. 
    While we strive for accuracy, laws vary by jurisdiction and change frequently. 
    Always consult with a qualified attorney for your specific situation.
    """)

def page_tutorial():
    """First-time user tutorial with interactive walkthrough."""
    st.markdown("""
    <div class="tutorial-container">
        <h1>👋 Welcome to CivicShield Pro!</h1>
        <p>Let's take a quick tour to help you get started.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tutorial steps
    steps = [
        {
            "title": "🏠 Home Dashboard",
            "description": "Your central hub to access all CivicShield features. Each card represents a powerful tool for understanding and protecting your rights.",
            "features": ["Navigate to any feature", "View saved deadlines", "Access crisis resources"]
        },
        {
            "title": "🗣️ Real-Time Translation",
            "description": "Instantly translate officer statements into 14 languages. Record conversations and get immediate translations to ensure you understand your rights.",
            "features": ["Speech-to-text in any language", "Real-time translation", "Audio playback in your language"]
        },
        {
            "title": "📄 Legal Documents",
            "description": "Upload court documents, legal notices, or contracts. CivicShield extracts key information and identifies important deadlines.",
            "features": ["Extract deadlines automatically", "Identify penalties", "Get translations"]
        },
        {
            "title": "⚖️ Know Your Rights",
            "description": "Learn about civil rights with educational content and test your knowledge with interactive quizzes. Available in multiple languages.",
            "features": ["Learn civil rights", "Take interactive quizzes", "Track progress"]
        },
        {
            "title": "📍 Resources Near You",
            "description": "Find legal aid organizations, community centers, and emergency services near your location. Get directions with one click.",
            "features": ["Search by location", "Browse by category", "Get directions instantly"]
        },
        {
            "title": "💬 Community Forum",
            "description": "Connect with others, share experiences, ask questions, and get advice from community members. Fully anonymous if you choose.",
            "features": ["Share experiences anonymously", "Ask legal questions", "Give advice"]
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
            <h4>✨ Key Features:</h4>
        </div>
        """, unsafe_allow_html=True)
        
        for feature in step["features"]:
            st.markdown(f"- {feature}")
        
        st.divider()
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if step_idx > 0:
                if st.button("⬅️ Previous", use_container_width=True):
                    st.session_state.tutorial_step -= 1
                    st.rerun()
        
        with col2:
            if st.button("⏭️ Skip Tour", use_container_width=True):
                st.session_state.tutorial_step = 0
                st.session_state.page = "Home"
                st.rerun()
        
        with col3:
            if step_idx < len(steps) - 1:
                if st.button("Next ➡️", use_container_width=True):
                    st.session_state.tutorial_step += 1
                    st.rerun()
            else:
                if st.button("🎉 Start Using!", use_container_width=True):
                    st.session_state.tutorial_step = 0
                    st.session_state.first_time_user = False
                    st.session_state.page = "Home"
                    st.rerun()
    else:
        st.success("✅ Tour Complete! You're ready to use CivicShield.")
        if st.button("🏠 Go to Home", use_container_width=True):
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
    
    # Language selector in sidebar
    st.session_state.selected_language = st.sidebar.selectbox(
        t('select_language'),
        list(LANGUAGE_MAP.keys()),
        index=list(LANGUAGE_MAP.keys()).index(st.session_state.selected_language),
        key="language_selector"
    )
    
    st.sidebar.divider()
    
    # Demo Mode toggle
    st.sidebar.markdown("### 📺 Demo & Testing")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "🎬 Demo ON" if st.session_state.demo_mode else "🎬 Demo OFF",
            use_container_width=True,
            key="demo_toggle"
        ):
            st.session_state.demo_mode = not st.session_state.demo_mode
            st.rerun()
    with col2:
        if st.button("🎓 Tour", use_container_width=True, key="tour_button"):
            st.session_state.tutorial_step = 0
            st.session_state.page = "Tutorial"
            st.rerun()
    
    if st.session_state.demo_mode:
        st.sidebar.success("✅ Demo Mode Active - Sample data is displayed")
    
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
                f"📢 {t('screen_reader')}" if st.session_state.screen_reader_enabled else "🔇 Screen Reader OFF",
                use_container_width=True,
                key="screen_reader_toggle"
            ):
                st.session_state.screen_reader_enabled = not st.session_state.screen_reader_enabled
                st.rerun()
        
        st.success(t('accessibility_saved'))
    
    st.sidebar.divider()
    
    # Navigation menu
    st.sidebar.markdown("### 🧭 Navigation")
    
    nav_options = {
        t('nav_home'): "Home",
        t('nav_translation'): "Translation",
        t('nav_documents'): "DocumentAssistant",
        "⚖️ Know Your Rights": "KnowYourRights",
        "📍 Resources Near You": "ResourcesNearYou",
        "📝 Encounter Log": "EncounterLogging",
        "🚨 Crisis Resources": "CrisisResources",
        "💬 Talk to Your Community": "CommunityDiscussion",
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
    
    Built for civil rights protection worldwide.
    """)
    
    st.sidebar.divider()
    
    # Disclaimer
    st.sidebar.warning(f"""
    **{t('sidebar_disclaimer')}**
    
    {t('sidebar_disclaimer_text')}
    """)
    
    st.sidebar.divider()
    
    # Landing page quick link
    if st.sidebar.button("🏠 Show Landing Page", use_container_width=True):
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
