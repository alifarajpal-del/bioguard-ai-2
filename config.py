"""
BioGuard AI Configuration
"""
import os
from pathlib import Path

# App Info
APP_NAME = "BioGuard AI"
APP_VERSION = "2.0.0"
APP_AUTHOR = "Ali Riyad Faraj"
APP_LOCATION = "Palestine 🇵🇸"

# Database
DB_PATH = Path(__file__).parent / "bioguard.db"
DB_TIMEOUT = 30.0

# OpenAI Settings
OPENAI_MODEL_VISION = "gpt-4o-mini"  # For food analysis
OPENAI_MODEL_CHAT = "gpt-4o-mini"    # For chat
OPENAI_MAX_TOKENS_VISION = 2048
OPENAI_MAX_TOKENS_CHAT = 500
OPENAI_TEMPERATURE_VISION = 0.3
OPENAI_TEMPERATURE_CHAT = 0.7

# File Upload Settings
MAX_FILE_SIZE_MB = 10
ALLOWED_FILE_TYPES = ["pdf", "jpg", "jpeg", "png", "webp"]

# Analysis Settings
MAX_IMAGE_SIZE = (800, 800)
IMAGE_QUALITY = 85
PDF_TEXT_LIMIT = 4000  # Characters for PDF summarization

# UI Settings
DEFAULT_LANGUAGE = "en"
DEFAULT_THEME = "ocean"

