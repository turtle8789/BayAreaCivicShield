import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
import io
import os

# 1. Page Layout Configuration
st.set_page_config(page_title="CivicShield BA", page_icon="None")

# 2. Complete 14-Language Matrix Mapping Dictionary
language_map = {
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
    "Punjabi / ਪੰਜਾਬီ": {"code": "pa", "native": "Punjabi"}
}

selected_display = st.selectbox(
    "Select Your Language:", 
    list(language_map.keys())
)

target_code = language_map[selected_display]["code"]
lang_name = language_map[selected_display]["native"]

# HIGH-SPEED OPTIMIZATION: Bypasses the cloud entirely for English and Spanish
@st.cache_resource(show_spinner=False)
def get_cached_ui_text(target_lang_code, lang_name):
    ui_strings = {
        "title": "CivicShield Bay Area",
        "caption": "Real-time legal translation and civil rights protection.",
        "info": "Community Impact: Forty-two percent of San Jose residents are foreign-born, and 20% face English language barriers. CivicShield provides real-time equity during critical encounters.",
        "emergency_btn": "EMERGENCY: HELP ME RIGHT NOW",
        "section_2": "Real-Time Officer Speech Translation",
        "mic_label": "Tap to record the officer speaking:",
        "manual_label": "Or type Officer's English Words manually:",
        "inst_title": "Follow these steps carefully:",
        "s1": "1. First, tap the red button above to play the English notification audio to the officer.",
        "s2": "2. Next, let the officer speak into the app using the microphone button below.",
        "s3": "3. Listen to the advice audio on the left side to understand your rights.",
        "s4": "4. Finally, play the second audio on the right side so the officer hears your legal answer in English."
    }
    
    if lang_name == "English":
        return ui_strings
        
    if lang_name == "Spanish":
        return {
            "title": "CivicShield Área de la Bahía",
            "caption": "Traducción legal en tiempo real y protección de derechos civiles.",
            "info": "Impacto comunitario: El 42% de los residentes de San José son nacidos en el extranjero y el 20% enfrenta barreras idiomáticas en inglés. CivicShield proporciona equidad en tiempo real.",
            "emergency_btn": "EMERGENCIA: AYÚDEME AHORA MISMO",
            "section_2": "Traducción de voz del oficial en tiempo real",
            "mic_label": "Toque para grabar al oficial hablando:",
            "manual_label": "O escriba las palabras en inglés del oficial manualmente:",
            "inst_title": "Siga estos pasos cuidadosamente:",
            "s1": "1. Primero, toque el botón rojo de arriba para reproducir el audio de notificación en inglés para el oficial.",
            "s2": "2. Luego, deje que el oficial hable en la aplicación usando el botón del micrófono de abajo.",
            "s3": "3. Escuche el audio de asesoramiento del lado izquierdo para comprender sus derechos.",
            "s4": "4. Finalmente, reproduzca el segundo audio del lado derecho para que el oficial escuche su respuesta legal en inglés."
        }
        
    translator = GoogleTranslator(source='en', target=target_lang_code)
    for key, text in ui_strings.items():
        ui_strings[key] = translator.translate(text)
    return ui_strings

ui = get_cached_ui_text(target_code, lang_name)
is_eng = (lang_name == "English")

st.title(ui["title"])
st.caption(ui["caption"])
st.info(ui["info"])

st.markdown("---")
st.subheader(ui["inst_title"])
st.write(ui["s1"])
st.write(ui["s2"])
st.write(ui["s3"])
st.write(ui["s4"])
st.markdown("---")

if st.button(ui["emergency_btn"], type="primary", use_container_width=True):
    audio_text = "Officer, I am using a translation app to protect my rights. Please speak into the device."
    tts = gTTS(text=audio_text, lang='en', slow=False)
    tts.save("emergency_warning.mp3")
    st.error("App Playing Audio to Officer: 'Officer, I am using a translation app to protect my rights. Please speak into the device.'")
    
    # TECHNICAL FIX: Forced byte reading mode for stable initialization
    with open("emergency_warning.mp3", "rb") as f:
        st.audio(f.read(), format="audio/mp3")

st.markdown("---")
st.subheader(ui["section_2"])
st.write(ui["mic_label"])

audio_record = mic_recorder(
    start_prompt="Record Officer's Voice",
    stop_prompt="Stop and Translate",
    format="wav",
    key='officer_recorder'
)

officer_text = ""

if audio_record:
    audio_bytes = audio_record['bytes']
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio_data = recognizer.record(source)
            officer_text = recognizer.recognize_google(audio_data, language="en-US")
            st.success(f"Speech Recognized: \"{officer_text}\"")
    except Exception as e:
        st.error("Could not understand the audio clearly. Please try speaking closer to the mic or type below.")

manual_input = st.text_input(ui["manual_label"], placeholder="e.g., Step out of the vehicle and let me search your car.")
final_input = manual_input if manual_input else officer_text

# Define template defaults to prevent rendering crashes
translated_advice = ""
officer_line_en = "Officer, I choose to remain silent."
advice_text_en = "Keep the app open, remain polite, keep your hands visible, and assert your right to remain silent if questioned."
alert_type = "success"

if final_input:
    if not is_eng:
        translated_text = GoogleTranslator(source='en', target=target_code).translate(final_input)
        st.write(f"**Translated Output ({lang_name}):** {translated_text}")
        
    st.markdown("---")
    
    immediate_safeguards_title = "Immediate Legal Safeguards (California Law):"
    if lang_name == "Spanish":
        immediate_safeguards_title = "Salvaguardias legales inmediatas (Ley de California):"
    elif not is_eng:
        immediate_safeguards_title = GoogleTranslator(source='en', target=target_code).translate(immediate_safeguards_title)
        
    st.subheader(immediate_safeguards_title)
    lower_input = final_input.lower()
    
    if "search" in lower_input or "look inside" in lower_input:
        advice_text_en = "FOURTH AMENDMENT ALERT: You have the legal right to refuse warrantless searches. Do not physically resist, but say clearly: 'I do not consent to a search.'"
        officer_line_en = "Officer, I do not consent to a search of my property."
        alert_type = "error"
    elif "step out" in lower_input or "get out" in lower_input:
        advice_text_en = "TRAFFIC STOP RULE: Under Pennsylvania v. Mimms, you must exit the vehicle if ordered, but you do NOT have to answer questions. Ask clearly: 'Am I free to go?'"
        officer_line_en = "Officer, am I free to go, or am I being detained?"
        alert_type = "warning"
    elif "handcuff" in lower_input or "arrest" in lower_input:
        advice_text_en = "FIFTH AMENDMENT ALERT: Do not resist physically. Protect your rights by stating clearly: 'I am exercising my right to remain silent and I want an attorney.'"
        officer_line_en = "Officer, I am invoking my right to remain silent and I want an attorney."
        alert_type = "error"

    if lang_name == "Spanish":
        if "search" in lower_input or "look inside" in lower_input:
            translated_advice = "ALERTA DE LA CUARTA ENMIENDA: Tiene el derecho legal de rechazar registros sin orden judicial. No se resista físicamente, pero diga claramente: 'No doy mi consentimiento para un registro'."
        elif "step out" in lower_input or "get out" in lower_input:
            translated_advice = "REGLA DE PARADA DE TRÁFICO: Según el caso Pennsylvania v. Mimms, debe salir del vehículo si se lo ordenan, pero NO tiene que responder preguntas. Pregunte claramente: '¿Soy libre de irme?'"
        elif "handcuff" in lower_input or "arrest" in lower_input:
            translated_advice = "ALERTA DE LA QUINTA ENMIENDA: No se resista físicamente. Proteja sus derechos declarando claramente: 'Estoy ejerciendo mi derecho a permanecer en silencio y quiero un abogado'."
        else:
            translated_advice = "Mantenga la aplicación abierta, sea cortés, mantenga las manos visibles y afirme su derecho a permanecer en silencio si le preguntan."
    elif not is_eng:
        translated_advice = GoogleTranslator(source='en', target=target_code).translate(advice_text_en)
    else:
        translated_advice = advice_text_en

    if alert_type == "error":
        st.error(f"**English:** {advice_text_en}\n\n**{lang_name}:** {translated_advice}")
    elif alert_type == "warning":
        st.warning(f"**English:** {advice_text_en}\n\n**{lang_name}:** {translated_advice}")
    else:
        st.success(f"**English:** {advice_text_en}\n\n**{lang_name}:** {translated_advice}")

st.markdown("---")
audio_coaching_title = "Audio Coaching & Defense Assistant"
listen_advice_label = f"Listen to Advice ({lang_name}):"
speak_officer_label = "Speak Aloud to Officer (First-Person English):"

if lang_name == "Spanish":
    audio_coaching_title = "Asistente de Audio y Defensa"

