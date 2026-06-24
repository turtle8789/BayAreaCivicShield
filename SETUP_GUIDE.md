# CivicShield Pro - Complete Setup & Deployment Guide

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Running the App](#running-the-app)
5. [Dependency Explanations](#dependency-explanations)
6. [Features Overview](#features-overview)
7. [Troubleshooting](#troubleshooting)
8. [Production Deployment](#production-deployment)

---

## 🚀 Quick Start

### For Windows Users (Fastest Path)

```bash
# 1. Open PowerShell or Command Prompt in your project folder
# 2. Create Python virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run civicshield_pro.py

# Browser will open at http://localhost:8501
```

### For Mac/Linux Users

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run civicshield_pro.py
```

---

## 💻 System Requirements

### Minimum Requirements
- **OS:** Windows 10, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python:** 3.8 or higher
- **RAM:** 2GB minimum (4GB recommended)
- **Storage:** 500MB free space
- **Microphone:** Required for speech-to-text features
- **Internet:** Required (Google Translate API, Google Speech-to-Text)

### Recommended Specifications
- **OS:** Windows 11, macOS 12+, or Ubuntu 20.04+
- **Python:** 3.10 or 3.11
- **RAM:** 4GB or more
- **Storage:** 1GB available
- **CPU:** Multi-core processor
- **Network:** High-speed internet (10 Mbps+)

### Browser Requirements
- Chrome, Firefox, Safari, or Edge (latest versions)
- JavaScript enabled
- WebRTC support (for microphone access)

---

## 📦 Installation

### Step 1: Install Python

**Windows:**
- Download from https://www.python.org/downloads/
- During installation, CHECK "Add Python to PATH"
- Verify installation:
  ```bash
  python --version
  ```

**Mac:**
```bash
# Using Homebrew (recommended)
brew install python@3.11
python3 --version
```

**Linux (Ubuntu):**
```bash
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3-pip
python3.11 --version
```

### Step 2: Clone or Download Project

```bash
# Option A: If using git
git clone <repository-url>
cd civicshield-pro

# Option B: If downloading as ZIP
# Extract the ZIP file to your desired location
cd path/to/civicshield-pro
```

### Step 3: Create Virtual Environment

**Purpose:** Isolates project dependencies from your system Python

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 4: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Install all requirements
pip install -r requirements.txt

# Verify installation (optional but recommended)
pip list
```

**Expected Output Should Include:**
- streamlit (1.28+)
- deep-translator (1.11+)
- gTTS (2.4+)
- SpeechRecognition (3.10+)
- streamlit-mic-recorder (0.0.8+)

---

## ▶️ Running the App

### Start the Application

```bash
# Make sure your virtual environment is activated
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Run the app
streamlit run civicshield_pro.py
```

### What to Expect

1. Terminal shows: `Local URL: http://localhost:8501`
2. Browser opens automatically to the app
3. You'll see the CivicShield Pro interface
4. Try the translator on the Home page

### Stopping the App

```bash
# In the terminal, press: Ctrl + C
```

---

## 📚 Dependency Explanations

### 1. **Streamlit (1.28.1)** - Web Framework
```
What it does: Converts Python scripts into interactive web apps
Why we need it: Core framework for the entire application
Key features:
  - Session state management (persistent variables across interactions)
  - Multi-page routing (different sections of the app)
  - Interactive widgets (buttons, text inputs, selectboxes)
  - Real-time updates without page refreshes
  
When it's used: Every interaction in the app
Example: st.button(), st.selectbox(), st.markdown()
```

### 2. **deep-translator (1.11.4)** - Translation Engine
```
What it does: Interfaces with Google Translate API
Why we need it: Provides 14-language translation support
Key features:
  - No API key required for basic use
  - Supports 100+ languages
  - Fast translation
  - Works offline after initial setup
  
When it's used: 
  - Translating officer statements to user's language
  - Translating user responses to English
  - Translating legal advice to user's language
  
Performance: ~0.5-2 seconds per translation
```

### 3. **gTTS (2.4.0)** - Text-to-Speech
```
What it does: Converts text to natural-sounding speech
Why we need it: Audio guidance for legal rights
Key features:
  - Free (no API key needed)
  - Supports all 14 target languages
  - Generates MP3 files
  - Natural-sounding voices
  
When it's used:
  - Playing legal advice to users
  - Playing officer warning message
  - Playing suggested responses
  
Performance: ~2-5 seconds per audio generation
Languages: Full support for all 14 languages in the app
```

### 4. **SpeechRecognition (3.10.0)** - Speech-to-Text
```
What it does: Converts audio to text transcription
Why we need it: Records and understands officer statements
Key features:
  - Uses Google Speech-to-Text API
  - Works with microphone input
  - Handles multiple audio formats (WAV, MP3)
  - Error handling for unclear audio
  
When it's used:
  - Processing microphone recordings
  - Converting officer speech to text
  
Performance: ~1-3 seconds per 30-second audio clip
Accuracy: ~85-95% for clear English speech
```

### 5. **streamlit-mic-recorder (0.0.8)** - Microphone Access
```
What it does: Provides browser-based microphone recording
Why we need it: Allows users to record officer statements
Key features:
  - Works in browser (no desktop app needed)
  - One-click recording/stopping
  - WAV format output
  - Real-time recording UI
  
When it's used: Recording officer's voice in the translation interface
Permissions: App asks for microphone access on first use
Output: WAV audio bytes that SpeechRecognition processes
```

### 6. **python-dotenv (1.0.0)** - Environment Management
```
What it does: Loads environment variables from .env files
Why we need it: Secure credential management
Key features:
  - Prevents hardcoding sensitive data
  - .env files never committed to git
  - Easy configuration management
  
When it's used: Storing API keys, sensitive settings
Optional: Only needed if you add custom API keys later
```

---

## ✨ Features Overview

### 🏠 Home Page
- **Real-Time Translation Interface**
  - Record officer statements via microphone
  - Manual text input option
  - Automatic translation to user's language
  - Audio playback of legal advice
  - Suggested responses with audio

- **Emergency Mode**
  - One-click emergency activation
  - Automatic officer notification
  - Crisis resource links

### 📚 Rights Education Center
- **Constitutional Rights Education**
  - 4th Amendment: Search & Seizure Rights
  - 5th Amendment: Right to Remain Silent
  - 6th Amendment: Right to Attorney
  - Traffic Stop Rights (California)
  - Arrest Procedure Rights

- **Do's and Don'ts Guide**
  - What to do during encounters
  - What to avoid
  - Correct phrases to use

### 🏥 Community Resources
- **Legal Aid Organizations**
  - California Rural Legal Assistance (CRLA)
  - San Francisco Legal Aid Society
  - Public Defender Offices

- **Emergency Services**
  - Mental health crisis lines
  - Sexual assault support
  - Domestic violence resources

- **Immigration Services**
  - ACLU Immigration Rights
  - USCIS Information

### 📝 Encounter Logging
- **Log Police Encounters**
  - Type of encounter (traffic stop, questioning, arrest, etc.)
  - Language used
  - Location and officer badge info
  - Detailed notes
  - Outcome tracking

- **View Encounter History**
  - Statistics on logged encounters
  - Language usage trends
  - Encounter type breakdown
  - Searchable history

### 🚨 Emergency Assistance
- **Crisis Resources**
  - Emergency phone numbers (911, 988, etc.)
  - 24/7 hotlines
  - Mental health support
  - Domestic violence resources

- **What to Do Guides**
  - Medical emergencies
  - Active threat situations
  - Police encounter emergencies
  - Mental health crises

---

## 🔧 Configuration & Customization

### Change the Port
```bash
# Default is 8501, but you can change it:
streamlit run civicshield_pro.py --server.port 8000
```

### Disable Camera/Microphone Requirement
```bash
# Some browsers require HTTPs for microphone access
# For local testing, use:
streamlit run civicshield_pro.py --logger.level=debug
```

### Add Custom CSS
Edit the custom CSS section in the file (around line 85):
```python
st.markdown("""
<style>
    /* Your custom CSS here */
</style>
""", unsafe_allow_html=True)
```

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'streamlit'"

**Solution:**
```bash
# Make sure virtual environment is activated
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

### Issue: "No module named 'speech_recognition'"

**Solution:**
```bash
# Install missing module
pip install SpeechRecognition
```

### Issue: Microphone Not Detected

**Solutions:**
1. Check browser microphone permissions
   - Click the lock icon in address bar
   - Allow microphone access
   
2. Test microphone in browser:
   - Go to https://www.google.com/search?q=check+microphone
   - Test your microphone
   
3. Use manual text input instead of microphone

### Issue: Translation Fails / API Errors

**Solutions:**
1. Check internet connection
   ```bash
   ping google.com
   ```

2. Try again - may be temporary API issue

3. Use manual translation:
   - Type officer statement in text field
   - Use translation yourself

4. Check for API rate limiting (free tier has limits)

### Issue: Audio Playback Not Working

**Solutions:**
1. Check volume is not muted
2. Try a different browser
3. Update your browser
4. Check internet connection

### Issue: App Crashes on Startup

**Solutions:**
1. Check Python version (must be 3.8+)
   ```bash
   python --version
   ```

2. Reinstall all packages
   ```bash
   pip install --upgrade --force-reinstall -r requirements.txt
   ```

3. Check for port conflicts
   ```bash
   # On Windows PowerShell:
   netstat -ano | findstr 8501
   ```

---

## 🚀 Production Deployment

### Deploy to Streamlit Cloud (Recommended)

1. **Push code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial CivicShield commit"
   git push origin main
   ```

2. **Go to Streamlit Cloud**
   - Visit https://share.streamlit.io
   - Sign in with GitHub
   - Click "New app"
   - Select your repository and file
   - Click "Deploy"

3. **Set Environment Variables**
   - In Streamlit Cloud settings, add any API keys needed
   - Use `st.secrets` to access them in code

### Deploy to Heroku

```bash
# 1. Create Procfile
echo "web: streamlit run civicshield_pro.py --server.port=\$PORT" > Procfile

# 2. Create .streamlit/config.toml
mkdir .streamlit
echo "[client]
headless = true
" > .streamlit/config.toml

# 3. Deploy
heroku create your-app-name
git push heroku main
```

### Deploy to AWS/Google Cloud/Azure

Use Docker containerization:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "civicshield_pro.py"]
```

### Performance Optimization for Production

```python
# In civicshield_pro.py, these are already implemented:

# 1. Caching for translators
@st.cache_resource
def get_translator(source_lang, target_lang):
    return GoogleTranslator(...)

# 2. Caching for UI strings
@st.cache_data
def get_ui_strings(language_name, language_code):
    return {...}

# 3. Session state for persistent data
st.session_state.encounter_log
st.session_state.selected_language
```

---

## 📞 Support & Resources

### Getting Help

1. **GitHub Issues**
   - Report bugs at project repository

2. **Streamlit Documentation**
   - https://docs.streamlit.io

3. **Python Documentation**
   - https://docs.python.org/3/

4. **Stack Overflow**
   - Tag: `streamlit`
   - Search for your error message

### Community Resources

- **Legal Aid:**
  - https://crla.org (California Rural Legal Assistance)
  - https://sflas.org (San Francisco Legal Aid)

- **Crisis Support:**
  - 988 - Suicide & Crisis Lifeline
  - 1-800-799-7233 - Domestic Violence Hotline
  - 1-800-656-4673 - Sexual Assault Support (RAINN)

---

## 📄 License & Legal

**Disclaimer:** CivicShield provides educational information about legal rights, not legal advice. Always consult a qualified attorney for your specific situation.

**License:** [Your License Here]

**Version:** 2.0.0  
**Last Updated:** 2024

---

## 🎯 Next Steps

1. ✅ Install dependencies from requirements.txt
2. ✅ Run the app with `streamlit run civicshield_pro.py`
3. ✅ Test all features (translation, audio, logging)
4. ✅ Customize resources for your region
5. ✅ Deploy to production (Streamlit Cloud recommended)

**Questions?** Check the troubleshooting section or file an issue on GitHub.
