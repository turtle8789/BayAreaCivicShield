import streamlit as st
from deep_translator import GoogleTranslator


# 1. Page Layout Configuration
st.set_page_config(page_title="CivicShield BA", page_icon="None")

st.title("CivicShield Bay Area")
st.caption("Real-time legal translation and civil rights protection.")

# 2. Local Visual Data Anchor
st.info("Community Impact: Forty-two percent of San Jose residents are foreign-born, and 20% face English language barriers. CivicShield provides real-time equity during critical encounters.")

# 3. Complete 14-Language Matrix Mapping Dictionary
language_map = {
    "English": "en",
    "Spanish": "es",
    "Cantonese": "zh-TW",  
    "Vietnamese": "vi",
    "Mandarin": "zh-CN",   
    "Tagalog": "tl",
    "Hindi": "hi",
    "Korean": "ko",
    "Japanese": "ja",
    "Portuguese": "pt",
    "Arabic": "ar",
    "Telugu": "te",
    "Tamil": "ta",
    "Punjabi": "pa"
}

# Generate clean selector list from our dictionary keys
selected_language = st.selectbox(
    "Select Your Language / Seleccione su idioma / Chon ngon ngu cua ban:", 
    list(language_map.keys())
)

st.markdown("---")

# 4. Core Emergency Operations
if st.button("EMERGENCY: HELP ME RIGHT NOW", type="primary", use_container_width=True):
    st.error("App Playing Audio to Officer: 'Officer, I am using a translation app to protect my rights. Please speak into the device.'")
    
    st.markdown("---")
    st.subheader("Real-Time Officer Speech Translation")
    
    # Text input mock for video demonstrations
    officer_input = st.text_input("Simulate Officer's English Words:", placeholder="e.g., Step out of the vehicle and let me search your car.")
    
    if officer_input:
        target_code = language_map[selected_language]
        
        # Execute real-time dynamic cloud translation
        if selected_language != "English":
            translated_text = GoogleTranslator(source='en', target=target_code).translate(officer_input)
            st.write(f"Translated Output ({selected_language}): {translated_text}")
            
        # 5. Conditional Core Legal Safeguards Logic
        st.markdown("### Immediate Legal Safeguards (California Law):")
        lower_input = officer_input.lower()
        
        if "search" in lower_input or "look inside" in lower_input:
            st.error("FOURTH AMENDMENT ALERT: You have the legal right to refuse warrantless searches. Say: 'I do not consent to a search.'")
        elif "step out" in lower_input or "get out" in lower_input:
            st.warning("TRAFFIC STOP RULE: Under Pennsylvania v. Mimms, you must step out if ordered, but you do NOT have to answer incriminating questions. Ask: 'Am I free to go?'")
        elif "handcuff" in lower_input or "arrest" in lower_input:
            st.error("FIFTH AMENDMENT ALERT: Do not resist physically. State: 'I am exercising my right to remain silent. I want an attorney.'")
        else:
            st.success("Keep the app open, remain polite, keep your hands visible, and assert your right to remain silent if questioned about your status.")
