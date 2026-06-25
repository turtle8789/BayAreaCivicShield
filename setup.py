#!/usr/bin/env python3
"""
CivicShield Pro - Quick Setup Script
Run this to install all dependencies and verify setup

Usage:
    python setup.py          # Full setup
    python setup.py --check  # Just verify setup
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and report status."""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, text=True)
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found. Make sure {cmd[0]} is installed.")
        return False

def check_python_version():
    """Verify Python version is 3.8+."""
    print(f"\n{'='*60}")
    print("🐍 Checking Python Version")
    print(f"{'='*60}")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    print(f"Current Python: {version_str}")
    
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python version OK (3.8+ required)")
        return True
    else:
        print(f"❌ Python 3.8+ required. Current: {version_str}")
        return False

def create_virtual_environment():
    """Create virtual environment."""
    if os.path.exists("venv"):
        print("ℹ️ Virtual environment already exists")
        return True
    
    return run_command(
        [sys.executable, "-m", "venv", "venv"],
        "Creating virtual environment"
    )

def upgrade_pip():
    """Upgrade pip, setuptools, and wheel."""
    if sys.platform == "win32":
        pip_cmd = ["venv\\Scripts\\python.exe", "-m", "pip"]
    else:
        pip_cmd = ["venv/bin/python", "-m", "pip"]
    
    cmd = pip_cmd + ["install", "--upgrade", "pip", "setuptools", "wheel"]
    return run_command(cmd, "Upgrading pip/setuptools/wheel")

def install_requirements():
    """Install dependencies from requirements.txt."""
    if sys.platform == "win32":
        pip_cmd = ["venv\\Scripts\\python.exe", "-m", "pip"]
    else:
        pip_cmd = ["venv/bin/python", "-m", "pip"]
    
    cmd = pip_cmd + ["install", "-r", "requirements.txt"]
    return run_command(cmd, "Installing dependencies from requirements.txt")

def verify_installation():
    """Verify all packages are installed."""
    print(f"\n{'='*60}")
    print("✓ Verifying Installation")
    print(f"{'='*60}")
    
    packages = [
        "streamlit",
        "deep_translator",
        "gtts",
        "speech_recognition",
        "streamlit_mic_recorder",
    ]
    
    all_ok = True
    for package in packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package:30} - Installed")
        except ImportError:
            print(f"❌ {package:30} - NOT FOUND")
            all_ok = False
    
    return all_ok

def show_next_steps():
    """Show user what to do next."""
    print(f"\n{'='*60}")
    print("🚀 Next Steps")
    print(f"{'='*60}")
    
    if sys.platform == "win32":
        activate_cmd = "venv\\Scripts\\activate"
        run_cmd = "streamlit run civicshield_pro_app.py"
    else:
        activate_cmd = "source venv/bin/activate"
        run_cmd = "streamlit run civicshield_pro_app.py"
    
    print(f"""
1. Activate virtual environment:
   {activate_cmd}

2. Run the app:
   {run_cmd}

3. Browser will open at:
   http://localhost:8501

4. Test the features:
   - Select a language
   - Try the translator
   - Test audio playback
   - Log an encounter
""")

def main():
    """Main setup flow."""
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║                    🛡️  CivicShield Pro Setup  🛡️                ║
    ║                    Production-Ready Rights App                   ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Python 3.8+ required")
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        print("\n⚠️  Virtual environment creation issue, but continuing...")
    
    # Upgrade pip
    if not upgrade_pip():
        print("\n⚠️  pip upgrade issue, but continuing...")
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Setup failed: Could not install requirements")
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("\n⚠️  Some packages may not be properly installed")
    
    # Show next steps
    show_next_steps()
    
    print(f"\n{'='*60}")
    print("✅ Setup Complete!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
