# 🎥 LiveVision Integration Guide

## Overview
تم دمج خدمة الرؤية الحية (LiveVision) في تطبيق BioGuard AI لتوفير تحليل مستمر وفوري للمنتجات الغذائية باستخدام كاميرا الجهاز.

## ✨ Features / المميزات

### 1. **Continuous Scanning** / **المسح المستمر**
- Real-time video processing at 1-3 FPS
- Auto-triggers analysis after 3-second cooldown
- No need for manual capture (optional manual mode available)

### 2. **Barcode Detection** / **كشف الباركود**
- Supports EAN13, UPC-A, Code128, QR codes
- Automatic product lookup via OpenFoodFacts API
- Displays product name, brand, and nutrition info
- Caches results for faster repeated scans

### 3. **OCR Text Extraction** / **استخراج النص**
- Extracts text from product labels using Tesseract
- Supports English and Arabic text
- Parses nutrition labels automatically
- Identifies ingredients lists

### 4. **Health Conflict Detection** / **كشف التعارضات الصحية**
- Cross-references with user health profile
- Checks against knowledge graph for ingredient conflicts
- Alerts for:
  - Allergies
  - Chronic conditions (diabetes, hypertension)
  - Dietary restrictions

### 5. **Multilingual UI** / **واجهة متعددة اللغات**
- Supports 5 languages: Arabic, English, French, Spanish, German
- Auto-translation of analysis results (optional)
- Language-specific UI messages (23 strings)

### 6. **AR Overlay HUD** / **واجهة الواقع المعزز**
- Detection boxes around identified objects
- Status indicators (searching, detected, analyzing)
- Progress rings during analysis
- Flash toggle button (device-dependent)

## 🛠️ Technical Architecture

### New Files Created

#### 1. **services/barcode_scanner.py** (330 lines)
```python
class BarcodeScannerService:
    - scan_barcode(image) -> Dict[str, Any]
    - _lookup_barcode(barcode) -> Dict[str, Any]
    - extract_text_ocr(image) -> str
    - parse_nutrition_label(text) -> Dict[str, Any]
    - extract_ingredients_list(text) -> List[str]
```

**Key Features:**
- **Barcode Detection**: Uses pyzbar library
- **Product Lookup**: Queries OpenFoodFacts API
- **Caching**: Stores barcode results for 1 hour
- **OCR**: Adaptive thresholding and denoising
- **Nutrition Parsing**: Regex-based extraction for 7 nutrients

#### 2. **services/translation.py** (200+ lines)
```python
class TranslationService:
    - translate_text(text, target_language) -> str
    - translate_analysis_result(result, target_language) -> Dict
    - _translate_with_google() -> str
    - _translate_simple() -> str
```

**Key Features:**
- **Google Translate API**: For accurate translations
- **Fallback Dictionary**: 50+ common food/health terms
- **Caching**: Reduces API calls
- **Auto-translation**: Configurable via .env

### Modified Files

#### 1. **ui_components/camera_view.py** (450+ lines)
**Major Additions:**
- `LiveVisionProcessor(VideoProcessorBase)`: WebRTC video processor
  - Processes frames in recv() method
  - Auto-triggers analysis with cooldown
  - Caches detections
- `render_camera_view()`: Main rendering function
  - Session state management
  - Dynamic HUD with status indicators
  - Analysis history viewer
- `_get_ui_messages(language)`: Multilingual support
- `_render_upload_fallback()`: Enhanced fallback with barcode/OCR

#### 2. **config/settings.py**
**New Settings:**
```python
# Language Support
SUPPORTED_LANGUAGES = {
    "en": "English",
    "ar": "العربية",
    "fr": "Français",
    "es": "Español",
    "de": "Deutsch",
}
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "ar")

# Translation
AUTO_TRANSLATE_RESULTS = os.getenv("AUTO_TRANSLATE_RESULTS", "true").lower() == "true"
TRANSLATION_API_KEY = os.getenv("TRANSLATION_API_KEY", "")

# Vision Processing
DETECTION_FPS = int(os.getenv("DETECTION_FPS", "2"))
ANALYSIS_COOLDOWN = int(os.getenv("ANALYSIS_COOLDOWN", "3"))  # seconds
```

## 📦 Installation

### System Requirements

#### Windows:
```powershell
# Install Tesseract OCR
choco install tesseract

# Install libzbar (for barcode scanning)
# Download from: https://sourceforge.net/projects/zbar/files/zbar/
# Or use conda:
conda install -c conda-forge zbar
```

#### Linux (Ubuntu/Debian):
```bash
# Install Tesseract OCR
sudo apt-get install tesseract-ocr tesseract-ocr-ara

# Install libzbar
sudo apt-get install libzbar0
```

#### macOS:
```bash
# Install Tesseract OCR
brew install tesseract tesseract-lang

# Install zbar
brew install zbar
```

### Python Dependencies
```bash
pip install -r requirements.txt
```

**New Dependencies:**
- `pyzbar>=0.1.9` - Barcode scanning
- `pytesseract>=0.3.10` - OCR text extraction
- `av>=10.0.0` - Video processing for WebRTC

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Language Settings
DEFAULT_LANGUAGE=ar  # ar, en, fr, es, de
AUTO_TRANSLATE_RESULTS=true
TRANSLATION_API_KEY=your_google_translate_api_key  # Optional

# Vision Processing
DETECTION_FPS=2  # Frames per second for detection (1-3 recommended)
ANALYSIS_COOLDOWN=3  # Seconds between auto-analyses

# Tesseract Path (Windows only, if not in PATH)
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### Feature Flags (config/settings.py)
```python
FEATURE_FLAGS = {
    "live_ar_enabled": True,  # Enable AR overlays
    "knowledge_graph_enabled": True,  # Enable health conflict detection
    "digital_twin_enabled": False,  # Future feature
}
```

## 🚀 Usage

### 1. Start the Application
```bash
streamlit run main.py
```

### 2. Navigate to Camera View
- Click "📷 Live Scan" in the navigation menu
- Grant camera permissions when prompted

### 3. Select Language
- Choose your preferred language from the dropdown (top-right)
- UI messages will update automatically

### 4. Scan Products
**Automatic Mode:**
- Point camera at product
- YOLO will detect objects automatically
- Analysis triggers after 3 seconds
- View results in the HUD

**Manual Mode:**
- Click "📸 Capture & Analyze" button
- Wait for AI analysis
- Results appear below the video feed

**Fallback Mode (if WebRTC unavailable):**
- Upload product image
- Barcode and OCR extraction runs automatically
- Full nutrition parsing available

### 5. View Analysis History
- Last 5 scans displayed below the camera
- Click expander to see details
- Health conflicts highlighted in red

## 🎨 UI Components

### Status Indicators
- 🔍 **Searching**: Looking for products
- ✅ **Detected**: Product found (barcode or object)
- ⚙️ **Analyzing**: AI analysis in progress
- ✔️ **Complete**: Analysis finished

### HUD Elements
- **Detection Boxes**: Green boxes around detected objects
- **Progress Ring**: Animated ring during analysis
- **Barcode Display**: Shows detected barcode number
- **Status Messages**: Real-time feedback in selected language

### Buttons
- **📸 Capture & Analyze**: Manual capture mode
- **💡 Flash**: Toggle device flash (device-dependent)
- **Language Selector**: Dropdown for language switching

## 🔍 Troubleshooting

### Issue: "No barcode detected"
**Solution:**
- Ensure good lighting
- Hold barcode steady and straight
- Try closer/further distances
- Check if barcode is supported (EAN13, UPC-A, etc.)

### Issue: "OCR not working"
**Solution:**
- Verify Tesseract installation: `tesseract --version`
- Set TESSERACT_CMD in .env (Windows)
- Install language packs: `sudo apt-get install tesseract-ocr-ara`

### Issue: "WebRTC not starting"
**Solution:**
- Grant camera permissions in browser
- Use HTTPS or localhost (WebRTC requirement)
- Check if camera is used by another app
- Try different browser (Chrome/Edge recommended)

### Issue: "Translation not working"
**Solution:**
- Check TRANSLATION_API_KEY in .env
- Verify AUTO_TRANSLATE_RESULTS=true
- Fallback dictionary translations should still work
- Check logs for API errors

## 📊 Performance Optimization

### Recommended Settings

**Development (Testing):**
```bash
DETECTION_FPS=3  # Higher FPS for faster detection
ANALYSIS_COOLDOWN=1  # Faster analysis triggers
MAX_API_CALLS_PER_MINUTE=100
```

**Production (Battery-efficient):**
```bash
DETECTION_FPS=1  # Lower FPS to save battery
ANALYSIS_COOLDOWN=5  # Longer cooldown to reduce API costs
MAX_API_CALLS_PER_MINUTE=60
```

### Caching Strategy
- **Barcode Results**: 1 hour cache
- **Translations**: In-memory cache (session lifetime)
- **YOLO Detections**: 2-second cache per frame

## 🔒 Security Considerations

1. **Camera Access**: Only granted when user explicitly enables it
2. **API Keys**: Never exposed to client-side JavaScript
3. **HTTPS Required**: WebRTC requires secure context
4. **Data Privacy**: Images not stored on server (processed in-memory)
5. **Rate Limiting**: MAX_API_CALLS_PER_MINUTE enforced

## 🧪 Testing Checklist

- [ ] WebRTC stream starts successfully
- [ ] YOLO detections appear as AR overlays
- [ ] Auto-analysis triggers after cooldown
- [ ] Barcode scanning recognizes sample UPC/EAN
- [ ] OCR extracts text from nutrition labels
- [ ] Language switching updates UI messages
- [ ] Health conflicts detected for user profile
- [ ] Analysis history displays last 5 scans
- [ ] Flash toggle button functional (on supported devices)
- [ ] Fallback mode works without WebRTC

## 📈 Future Enhancements

### Pending Features
1. **Alternative Products**: Suggest healthier alternatives from same category
2. **Sound/Vibration Feedback**: Haptic feedback on detection
3. **Offline Mode**: Local database for barcode lookups
4. **Multi-product Detection**: Analyze multiple products simultaneously
5. **Voice Commands**: Hands-free operation
6. **Shopping List Integration**: Save scanned products to list

### Known Limitations
- Flash toggle requires JavaScript for device API access (not fully implemented)
- Translation API requires Google Cloud account (fallback dictionary available)
- WebRTC may not work on all mobile browsers (fallback upload mode available)

## 📚 API References

### OpenFoodFacts API
```
GET https://world.openfoodfacts.org/api/v0/product/{barcode}.json
Response: {
    product: {
        product_name: string,
        brands: string,
        nutriments: object,
        ingredients_text: string
    }
}
```

### Google Translate API
```
POST https://translation.googleapis.com/language/translate/v2
Params: {
    key: string,
    q: string,
    source: string,
    target: string
}
```

## 🤝 Contributing

To add new features to LiveVision:

1. **New Language Support**: Add translations to `_get_ui_messages()` in [camera_view.py](ui_components/camera_view.py#L45-L95)
2. **New Barcode Types**: Update `scan_barcode()` in [barcode_scanner.py](services/barcode_scanner.py#L30-L80)
3. **Enhanced OCR**: Modify `extract_text_ocr()` in [barcode_scanner.py](services/barcode_scanner.py#L120-L170)

## 📄 License
This integration follows the main project license.

## 🙏 Acknowledgments
- **OpenFoodFacts**: Product database API
- **YOLOv8**: Object detection model
- **Tesseract**: OCR engine
- **ZBar**: Barcode scanning library

---

**Last Updated**: 2024-01-XX  
**Version**: 1.0.0  
**Maintainer**: BioGuard AI Team
