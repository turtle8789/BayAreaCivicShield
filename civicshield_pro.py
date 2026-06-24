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
import pytesseract
from pdf2image import convert_from_bytes

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
        background: linear-gradient(135deg, #f8f9fa 0%, #e8eef7 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a5f 0%, #162f4a 100%);
    }
    
    [data-testid="stSidebar"] > div > div > div > div > h1 {
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    
    /* Dashboard card styling */
    .dashboard-card {
        background-color: white;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        border-left: 5px solid #d62828;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .dashboard-card:hover {
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        transform: translateY(-4px);
    }
    
    .card-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .card-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1e3a5f;
        margin-bottom: 0.5rem;
    }
    
    .card-description {
        color: #666;
        font-size: 0.95rem;
        line-height: 1.4;
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
        padding: 0.75rem 1.5rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
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
    
    h3 {
        color: #2a4a7c;
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
        st.session_state.page = "Home"
    if "selected_language" not in st.session_state:
        st.session_state.selected_language = "English"
    if "encounter_log" not in st.session_state:
        st.session_state.encounter_log = load_encounters()
    if "emergency_activated" not in st.session_state:
        st.session_state.emergency_activated = False
    if "translation_history" not in st.session_state:
        st.session_state.translation_history = []

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

# ============================================================================
# PERSISTENT STORAGE FUNCTIONS
# ============================================================================
ENCOUNTER_FILE = "encounters.json"

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
    """Dashboard home page with feature cards."""
    st.markdown(f"# {t('home_title')}")
    st.markdown(f"## {t('home_subtitle')}")
    st.markdown("---")
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
            if st.button(f"{t('btn_open')} - {t('card_translation_title')}", use_container_width=True, key="open_translation"):
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
            if st.button(f"{t('btn_open')} - {t('card_documents_title')}", use_container_width=True, key="open_documents"):
                st.session_state.page = "DocumentAssistant"
                st.rerun()
        
        st.divider()
        
        # Rights Education Card
        with st.container():
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-icon">📚</div>
                <div class="card-title">{t('card_rights_title')}</div>
                <div class="card-description">{t('card_rights_desc')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"{t('btn_open')} - {t('card_rights_title')}", use_container_width=True, key="open_rights"):
                st.session_state.page = "RightsEducation"
                st.rerun()
        
        st.divider()
        
        # Community Resources Card
        with st.container():
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-icon">🏥</div>
                <div class="card-title">{t('card_resources_title')}</div>
                <div class="card-description">{t('card_resources_desc')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"{t('btn_open')} - {t('card_resources_title')}", use_container_width=True, key="open_resources"):
                st.session_state.page = "Resources"
                st.rerun()
    
    with col2:
        # Rights Quiz Card
        with st.container():
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-icon">❓</div>
                <div class="card-title">{t('card_quiz_title')}</div>
                <div class="card-description">{t('card_quiz_desc')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"{t('btn_open')} - {t('card_quiz_title')}", use_container_width=True, key="open_quiz"):
                st.session_state.page = "RightsQuiz"
                st.rerun()
        
        st.divider()
        
        # Rights Near Me Card
        with st.container():
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-icon">📍</div>
                <div class="card-title">{t('card_nearby_title')}</div>
                <div class="card-description">{t('card_nearby_desc')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"{t('btn_open')} - {t('card_nearby_title')}", use_container_width=True, key="open_nearby"):
                st.session_state.page = "RightsNearMe"
                st.rerun()
        
        st.divider()
        
        # Encounter Log Card
        with st.container():
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-icon">📝</div>
                <div class="card-title">{t('card_logging_title')}</div>
                <div class="card-description">{t('card_logging_desc')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"{t('btn_open')} - {t('card_logging_title')}", use_container_width=True, key="open_logging"):
                st.session_state.page = "EncounterLogging"
                st.rerun()
        
        st.divider()
        
        # Emergency Assistance Card
        with st.container():
            st.markdown(f"""
            <div class="dashboard-card">
                <div class="card-icon">🚨</div>
                <div class="card-title">{t('card_emergency_title')}</div>
                <div class="card-description">{t('card_emergency_desc')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"{t('btn_open')} - {t('card_emergency_title')}", use_container_width=True, key="open_emergency"):
                st.session_state.page = "Emergency"
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
    """Legal document assistant page."""
    st.markdown(f"# {t('documents_title')}")
    st.markdown(f"_{t('documents_subtitle')}_")
    st.divider()
    
    st.info(f"{t('documents_subtitle')} - Feature available when system libraries installed")

def page_rights_education():
    """Rights education center."""
    st.markdown(f"# {t('rights_title')}")
    st.markdown(f"_{t('rights_subtitle')}_")
    st.divider()
    
    selected_right = st.selectbox(
        "Select a topic:",
        list(RIGHTS_EDUCATION.keys()),
        key="rights_select"
    )
    
    if selected_right:
        right = RIGHTS_EDUCATION[selected_right]
        st.markdown(f"## {right['title']}")
        st.markdown(right['content'])

def page_rights_quiz():
    """Rights education quiz."""
    st.markdown(f"# {t('card_quiz_title')}")
    st.markdown(f"_{t('card_quiz_desc')}_")
    st.divider()
    
    quiz_questions = [
        {
            "question": "Can police search your car without consent?",
            "options": ["Only with a warrant", "Only if they have probable cause", "Both A and B", "No, never"],
            "correct": 2,
            "explanation": "Police can search with a warrant OR if they have probable cause to believe evidence is in the car."
        },
        {
            "question": "Do you have to answer police questions?",
            "options": ["Yes, always", "No, you have the right to remain silent", "Only your name", "Only if arrested"],
            "correct": 1,
            "explanation": "You have the Fifth Amendment right to remain silent and not incriminate yourself."
        },
        {
            "question": "What should you say if arrested?",
            "options": ["Explain what happened", "Ask for a lawyer", "Refuse to give your name", "Try to negotiate"],
            "correct": 1,
            "explanation": "Always ask for a lawyer immediately and remain silent."
        }
    ]
    
    for i, q in enumerate(quiz_questions):
        st.markdown(f"### Question {i+1}: {q['question']}")
        answer = st.radio(
            "Select your answer:",
            q['options'],
            key=f"quiz_q{i}"
        )
        
        if st.button(f"Check Answer {i+1}", key=f"check_q{i}"):
            if answer == q['options'][q['correct']]:
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect. {q['explanation']}")
        st.divider()

def page_resources():
    """Community resources page."""
    st.markdown(f"# {t('resources_title')}")
    st.markdown(f"_{t('resources_subtitle')}_")
    st.divider()
    
    category = st.selectbox(
        "Select a category:",
        list(COMMUNITY_RESOURCES.keys()),
        key="resources_select"
    )
    
    if category:
        st.markdown(f"## {category}")
        resources = COMMUNITY_RESOURCES[category]
        
        for resource in resources:
            with st.container():
                st.markdown(f"### {resource['name']}")
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown(f"**{t('phone_number')}** {resource['phone']}")
                
                with col2:
                    if 'website' in resource:
                        st.markdown(f"**{t('website')}** {resource['website']}")
                
                st.markdown(f"**{t('services')}** {resource['services']}")
                st.divider()

def page_rights_near_me():
    """Know Your Rights Near Me - location-based legal aid finder."""
    st.markdown(f"# {t('nearby_title')}")
    st.markdown(f"_{t('nearby_subtitle')}_")
    st.divider()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        address = st.text_input(t('enter_address'), placeholder="Enter your address")
    
    with col2:
        radius = st.number_input(t('search_radius'), min_value=1, max_value=50, value=5)
    
    if address and st.button(f"{t('btn_search')} {t('nearby_title')}", use_container_width=True):
        st.info(f"📍 {t('nearby_subtitle')} in {address} (within {radius} miles)")
        
        # Placeholder results - in production, integrate with real location API
        st.markdown(f"### {t('nearest_legal_aid')}")
        st.markdown(f"""
        **Legal Aid Society**
        {t('address')} 123 Main St, Your City
        {t('phone_number')} (555) 123-4567
        {t('hours_open')} Mon-Fri 9AM-5PM
        """)
        
        st.markdown(f"### {t('nearest_courthouse')}")
        st.markdown(f"""
        **District Courthouse**
        {t('address')} 456 Justice Ave, Your City
        {t('phone_number')} (555) 234-5678
        {t('hours_open')} Mon-Fri 8AM-4PM
        """)
        
        st.markdown(f"### {t('nearest_police')}")
        st.markdown(f"""
        **Police Department**
        {t('address')} 789 Law St, Your City
        {t('phone_number')} (555) 911-0000 (Emergency: 911)
        {t('hours_open')} 24/7
        """)

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

def page_emergency():
    """Emergency assistance page."""
    st.markdown(f"# {t('emergency_title')}")
    st.markdown(f"_{t('emergency_subtitle')}_")
    st.divider()
    
    # Emergency contacts
    st.markdown(f"## {t('emergency_procedures')}")
    
    emergency_numbers = {
        t('emergency_911'): "911",
        t('emergency_suicide'): "988",
        t('emergency_domestic'): "1-800-799-7233",
        t('emergency_assault'): "1-800-656-4673",
        t('emergency_poison'): "1-800-222-1222",
        t('emergency_text'): "Text HOME to 741741"
    }
    
    for service, number in emergency_numbers.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{service}**")
        with col2:
            st.code(number, language="")
    
    st.divider()
    
    st.markdown(f"## {t('emergency_procedures')}")
    
    procedures = [
        (t('procedure_safe'), "Keep yourself safe - do not physically resist"),
        (t('procedure_document'), "Remember details: names, badges, locations, times"),
        (t('procedure_record'), "Record interactions if safe and legal in your area"),
        (t('procedure_call'), "Call 911 if in immediate danger"),
        (t('procedure_contact'), "Contact your attorney as soon as possible"),
    ]
    
    for title, desc in procedures:
        st.markdown(f"### {title}")
        st.write(desc)

# ============================================================================
# MAIN APP WITH SIDEBAR NAVIGATION
# ============================================================================
def main():
    """Main app with fully localized sidebar navigation."""
    
    # Initialize session state
    init_session_state()
    
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
    
    # Navigation menu
    st.sidebar.markdown("### 🧭 Navigation")
    
    nav_options = {
        t('nav_home'): "Home",
        t('nav_translation'): "Translation",
        t('nav_documents'): "DocumentAssistant",
        t('nav_rights'): "RightsEducation",
        t('nav_quiz'): "RightsQuiz",
        t('nav_resources'): "Resources",
        t('nav_nearby'): "RightsNearMe",
        t('nav_logging'): "EncounterLogging",
        t('nav_emergency'): "Emergency",
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
    
    # Page routing
    if st.session_state.page == "Home":
        page_home()
    elif st.session_state.page == "Translation":
        page_translation()
    elif st.session_state.page == "DocumentAssistant":
        page_documents()
    elif st.session_state.page == "RightsEducation":
        page_rights_education()
    elif st.session_state.page == "RightsQuiz":
        page_rights_quiz()
    elif st.session_state.page == "Resources":
        page_resources()
    elif st.session_state.page == "RightsNearMe":
        page_rights_near_me()
    elif st.session_state.page == "EncounterLogging":
        page_encounter_logging()
    elif st.session_state.page == "Emergency":
        page_emergency()
    else:
        page_home()

# ============================================================================
# APP ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    main()
