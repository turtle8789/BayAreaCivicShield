import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
import io
import os

# 1. Page Layout Configuration
st.set_page_config(page_title="CivicShield BA", page_icon="None")

# 2. Complete 14-Language Matrix Mapping Dictionary (with Native Names)
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
    "Punjabi / ਪੰਜਾਬੀ": {"code": "pa", "native": "Punjabi"}
}

# Generate clean selector list from our dictionary keys
selected_display = st.selectbox(
    "Select Your Language / మీ భాషను ఎంచుకోండి:", 
    list(language_map.keys())
)

# Get the clean language name and ISO code
target_code = language_map[selected_display]["code"]
lang_name = language_map[selected_display]["native"]

# 3. Dynamic UI Translation Text Blocks
# We translate the core application layout instructions dynamically
title_text = "CivicShield Bay Area"
caption_text = "Real-time legal translation and civil rights protection."
info_text = "Community Impact: Forty-two percent of San Jose residents are foreign-born, and 20% face English language barriers. CivicShield provides real-time equity during critical encounters."

emergency_btn_text = "EMERGENCY: HELP ME RIGHT NOW"
emergency_play_text = "App Playing Audio to Officer: 'Officer, I am using a translation app to protect my rights. Please speak into the device.'"

section_2_text = "Real-Time Officer Speech Translation"
mic_label_text = "Tap to record the officer speaking:"
manual_label_text = "Or type Officer's English Words manually:"
manual_placeholder = "e.g., Step out of the vehicle and let me search your car."

# Step-by-Step System Instructions
instructions_title = "Follow these steps carefully:"
step_1 = "1. First, tap the red button above to play the English notification audio to the officer."
step_2 = "2. Next, let the officer speak into the app using the microphone button below."
step_3 = "3. Listen to the advice audio on the left side to understand your rights."
step_4 = "4. Finally, play the second audio on the right side so the officer hears your legal answer in English."

# Execute translation for the interface elements if English is not selected
if lang_name != "English":
    title_text = GoogleTranslator(source='en', target=target_code).translate(title_text)
    caption_text = GoogleTranslator(source='en', target=target_code).translate(caption_text)
    info_text = GoogleTranslator(source='en', target=target_code).translate(info_text)
    emergency_btn_text = GoogleTranslator(source='en', target=target_code).translate(emergency_btn_text)
    section_2_text = GoogleTranslator(source='en', target=target_code).translate(section_2_text)
    mic_label_text = GoogleTranslator(source='en', target=target_code).translate(mic_label_text)
    manual_label_text = GoogleTranslator(source='en', target=target_code).translate(manual_label_text)
    
    instructions_title = GoogleTranslator(source='en', target=target_code).translate(instructions_title)
    step_1 = GoogleTranslator(source='en', target=target_code).translate(step_1)
    step_2 = GoogleTranslator(source='en', target=target_code).translate(step_2)
    step_3 = GoogleTranslator(source='en', target=target_code).translate(step_3)
    step_4 = GoogleTranslator(source='en', target=target_code).translate(step_4)

# Render UI layout with the translated strings
st.title(title_text)
st.caption(caption_text)
st.info(info_text)

st.markdown("---")

# Display the customized user workflow guide
st.subheader(instructions_title)
st.write(step_1)
st.write(step_2)
st.write(step_3)
st.write(step_4)

st.markdown("---")

# 4. Core Emergency Operations
if st.button(emergency_btn_text, type="primary", use_container_width=True):
    audio_text = "Officer, I am using a translation app to protect my rights. Please speak into the device."
    tts = gTTS(text=audio_text, lang='en', slow=False)
    tts.save("emergency_warning.mp3")
    
    st.error(emergency_play_text)
    st.audio("emergency_warning.mp3", format="audio/mp3")

st.markdown("---")
st.subheader(section_2_text)

# Place the live microphone recorder permanently on the screen layout
st.write(mic_label_text)

audio_record = mic_recorder(
    start_prompt="Record Officer's Voice",
    stop_prompt="Stop and Translate",
    format="wav",
    key='officer_recorder'
)

# Variable to hold our text string for processing
officer_text = ""

# If the user records voice audio bytes
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

# Text input box acts as a permanent manual override/backup system
manual_input = st.text_input(manual_label_text, placeholder=manual_placeholder)

# If they used the microphone, use that text. Otherwise, use what they typed.
final_input = manual_input if manual_input else officer_text

# 5. Core Translation and Two-Way Audio Safeguards Engine
if final_input:
    # Execute dynamic cloud translation module
    if lang_name != "English":
        translated_text = GoogleTranslator(source='en', target=target_code).translate(final_input)
        st.write(f"**Translated Output ({lang_name}):** {translated_text}")
        
    st.markdown("---")
    
    immediate_safeguards_title = "Immediate Legal Safeguards (California Law):"
    if lang_name != "English":
        immediate_safeguards_title = GoogleTranslator(source='en', target=target_code).translate(immediate_safeguards_title)
        
    st.subheader(immediate_safeguards_title)
    lower_input = final_input.lower()
    
    # Text templates for legal advice
    advice_text_en = ""
    officer_line_en = ""
    
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
        
    else:
        advice_text_en = "Keep the app open, remain polite, keep your hands visible, and assert your right to remain silent if questioned."
        officer_line_en = "Officer, I choose to remain silent."
        alert_type = "success"

    # Execute translation for the advice text into the user's chosen language
    if lang_name != "English":
        translated_advice = GoogleTranslator(source='en', target=target_code).translate(advice_text_en)
    else:
        translated_advice = advice_text_en

    # Display the bilingual text fields on screen
    if alert_type == "error":
        st.error(f"**English:** {advice_text_en}\n\n**{lang_name}:** {translated_advice}")
    elif alert_type == "warning":
        st.warning(f"**English:** {advice_text_en}\n\n**{lang_name}:** {translated_advice}")
    else:
        st.success(f"**English:** {advice_text_en}\n\n**{lang_name}:** {translated_advice}")

    # GENERATE DUAL INTERACTIVE AUDIO CHANNELS
    audio_coaching_title = "Audio Coaching & Defense Assistant"
    listen_advice_label = f"Listen to Advice ({lang_name}):"
    speak_officer_label = "Speak Aloud to Officer (First-Person English):"
    
    if lang_name != "English":
        audio_coaching_title = GoogleTranslator(source='en', target=target_code).translate(audio_coaching_title)
        listen_advice_label = GoogleTranslator(source='en', target=target_code).translate(listen_advice_label)
        speak_officer_label = GoogleTranslator(source='en', target=target_code).translate(speak_officer_label)

    st.markdown(f"#### {audio_coaching_title}")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"🔊 **{listen_advice_label}**")
        # Generate coaching voice track in user's native language
        if lang_name != "English":
            tts_user = gTTS(text=translated_advice, lang=target_code, slow=False)
            tts_user.save("user_coaching.mp3")
            st.audio("user_coaching.mp3", format="audio/mp3")
        else:
            st.write("Language is set to English.")

