#!/usr/bin/env python3
"""
Installation and Setup Script for BioGuard AI LiveVision Integration
Checks system dependencies and installs required packages.
"""

import subprocess
import sys
import platform
import os
from pathlib import Path


def print_header(text):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def print_success(text):
    """Print success message."""
    print(f"✅ {text}")


def print_warning(text):
    """Print warning message."""
    print(f"⚠️  {text}")


def print_error(text):
    """Print error message."""
    print(f"❌ {text}")


def check_python_version():
    """Check if Python version is 3.8 or higher."""
    print_header("Checking Python Version")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python 3.8+ required, found {version.major}.{version.minor}.{version.micro}")
        return False


def check_tesseract():
    """Check if Tesseract OCR is installed."""
    print_header("Checking Tesseract OCR")
    
    try:
        result = subprocess.run(
            ["tesseract", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print_success(f"Tesseract installed: {version}")
            return True
        else:
            print_warning("Tesseract not found")
            return False
            
    except FileNotFoundError:
        print_warning("Tesseract not found in PATH")
        return False
    except Exception as e:
        print_error(f"Error checking Tesseract: {e}")
        return False


def install_tesseract_instructions():
    """Print instructions for installing Tesseract."""
    system = platform.system()
    
    print("\n📋 Tesseract Installation Instructions:")
    print("-" * 60)
    
    if system == "Windows":
        print("""
Windows:
  Option 1 - Chocolatey:
    choco install tesseract
    
  Option 2 - Manual Download:
    1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
    2. Install to: C:\\Program Files\\Tesseract-OCR
    3. Add to PATH or set TESSERACT_CMD in .env:
       TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
""")
    
    elif system == "Linux":
        print("""
Linux (Ubuntu/Debian):
  sudo apt-get update
  sudo apt-get install tesseract-ocr tesseract-ocr-ara
  
Linux (Fedora):
  sudo dnf install tesseract tesseract-langpack-ara
""")
    
    elif system == "Darwin":  # macOS
        print("""
macOS:
  brew install tesseract tesseract-lang
""")


def check_zbar():
    """Check if libzbar is available."""
    print_header("Checking libzbar (Barcode Library)")
    
    try:
        import pyzbar.pyzbar as pyzbar
        print_success("pyzbar library found")
        return True
    except ImportError:
        print_warning("pyzbar not installed (will be installed with pip)")
        return False
    except Exception as e:
        print_warning(f"libzbar system library may be missing: {e}")
        return False


def install_zbar_instructions():
    """Print instructions for installing libzbar."""
    system = platform.system()
    
    print("\n📋 libzbar Installation Instructions:")
    print("-" * 60)
    
    if system == "Windows":
        print("""
Windows:
  Option 1 - Conda (Recommended):
    conda install -c conda-forge zbar
    
  Option 2 - Manual Download:
    1. Download from: https://sourceforge.net/projects/zbar/files/zbar/
    2. Extract DLL files
    3. Add to PATH or place in Python Scripts folder
""")
    
    elif system == "Linux":
        print("""
Linux (Ubuntu/Debian):
  sudo apt-get install libzbar0
  
Linux (Fedora):
  sudo dnf install zbar
""")
    
    elif system == "Darwin":
        print("""
macOS:
  brew install zbar
""")


def install_python_packages():
    """Install Python packages from requirements.txt."""
    print_header("Installing Python Packages")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print_error(f"requirements.txt not found at {requirements_file}")
        return False
    
    try:
        print("📦 Installing packages from requirements.txt...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success("All Python packages installed successfully")
            return True
        else:
            print_error(f"Package installation failed:\n{result.stderr}")
            return False
            
    except Exception as e:
        print_error(f"Error installing packages: {e}")
        return False


def check_env_file():
    """Check if .env file exists and has required variables."""
    print_header("Checking Environment Configuration")
    
    env_file = Path(__file__).parent / ".env"
    env_example = Path(__file__).parent / ".env.example"
    
    if not env_file.exists():
        print_warning(".env file not found")
        
        if env_example.exists():
            print("\n📋 Creating .env from .env.example...")
            try:
                with open(env_example, 'r') as src:
                    content = src.read()
                
                with open(env_file, 'w') as dst:
                    dst.write(content)
                
                print_success(".env file created from template")
                print("\n⚠️  IMPORTANT: Edit .env file and add your API keys:")
                print("   - JWT_SECRET_KEY (required for production)")
                print("   - OPENAI_API_KEY (for GPT-4 Vision)")
                print("   - GOOGLE_API_KEY (for Gemini)")
                print("   - TRANSLATION_API_KEY (optional, for translations)")
                return True
                
            except Exception as e:
                print_error(f"Failed to create .env: {e}")
                return False
        else:
            print_error("Neither .env nor .env.example found")
            return False
    else:
        print_success(".env file exists")
        
        # Check for critical variables
        with open(env_file, 'r') as f:
            content = f.read()
        
        critical_vars = ["JWT_SECRET_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY"]
        missing_vars = []
        
        for var in critical_vars:
            if var not in content or f"{var}=your_" in content or f"{var}=" in content and f"{var}=\n" in content:
                missing_vars.append(var)
        
        if missing_vars:
            print_warning(f"Missing or placeholder values: {', '.join(missing_vars)}")
            print("   Please update these values in .env file")
        else:
            print_success("All critical environment variables configured")
        
        return True


def create_directories():
    """Create required directories if they don't exist."""
    print_header("Creating Directories")
    
    dirs = ["logs", "data", "uploads", ".streamlit"]
    base_path = Path(__file__).parent
    
    for dir_name in dirs:
        dir_path = base_path / dir_name
        
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print_success(f"Created directory: {dir_name}/")
            except Exception as e:
                print_error(f"Failed to create {dir_name}/: {e}")
        else:
            print(f"   Directory exists: {dir_name}/")
    
    return True


def check_model_file():
    """Check if YOLOv8 model file exists."""
    print_header("Checking YOLO Model")
    
    model_file = Path(__file__).parent / "yolov8n.pt"
    
    if model_file.exists():
        size_mb = model_file.stat().st_size / (1024 * 1024)
        print_success(f"YOLOv8 model found ({size_mb:.1f} MB)")
        return True
    else:
        print_warning("yolov8n.pt not found")
        print("\n📋 The model will be downloaded automatically on first run")
        print("   Or download manually from: https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt")
        return True  # Not critical, will auto-download


def run_setup():
    """Run complete setup process."""
    print("\n" + "="*60)
    print("  BioGuard AI - LiveVision Integration Setup")
    print("="*60)
    
    system = platform.system()
    print(f"\n🖥️  Detected System: {system} {platform.release()}")
    
    all_ok = True
    
    # Check Python version
    if not check_python_version():
        all_ok = False
        return False
    
    # Check system dependencies
    tesseract_ok = check_tesseract()
    zbar_ok = check_zbar()
    
    if not tesseract_ok:
        install_tesseract_instructions()
        all_ok = False
    
    if not zbar_ok:
        install_zbar_instructions()
        # Don't fail yet, might be installed with pip
    
    # Install Python packages
    if not install_python_packages():
        all_ok = False
    
    # Check configuration
    if not check_env_file():
        all_ok = False
    
    # Create directories
    create_directories()
    
    # Check model
    check_model_file()
    
    # Final summary
    print_header("Setup Summary")
    
    if all_ok and tesseract_ok:
        print_success("✅ Setup completed successfully!")
        print("\n🚀 Next steps:")
        print("   1. Edit .env file with your API keys")
        print("   2. Run: streamlit run main.py")
        print("   3. Navigate to '📷 Live Scan' in the app")
    else:
        print_warning("⚠️  Setup completed with warnings")
        print("\n📋 Please install missing system dependencies:")
        
        if not tesseract_ok:
            print("   - Tesseract OCR (required for text extraction)")
        if not zbar_ok:
            print("   - libzbar (required for barcode scanning)")
        
        print("\n   Then run this script again to verify installation")
    
    return all_ok


if __name__ == "__main__":
    try:
        success = run_setup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
