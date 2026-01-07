"""
Translation Service for multi-language support.
Provides automatic translation of analysis results and UI elements.
"""

import logging
from typing import Dict, Any, Optional
import requests
from app_config.settings import TRANSLATION_API_KEY, AUTO_TRANSLATE_RESULTS

logger = logging.getLogger(__name__)


class TranslationService:
    """Handle automatic translation of content."""
    
    def __init__(self):
        """Initialize translation service."""
        self.logger = logging.getLogger(__name__)
        self.cache = {}  # Cache translations
    
    def translate_text(
        self, 
        text: str, 
        target_language: str = 'ar',
        source_language: str = 'en'
    ) -> str:
        """
        Translate text to target language.
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code
            
        Returns:
            Translated text or original if translation fails
        """
        if not AUTO_TRANSLATE_RESULTS:
            return text
        
        if not text or text.strip() == '':
            return text
        
        # Check cache
        cache_key = f"{source_language}_{target_language}_{text[:50]}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Use Google Translate API if key available
            if TRANSLATION_API_KEY:
                translated = self._translate_with_google(text, target_language, source_language)
            else:
                # Fallback to simple dictionary-based translation for common terms
                translated = self._translate_simple(text, target_language)
            
            # Cache result
            self.cache[cache_key] = translated
            return translated
            
        except Exception as e:
            self.logger.error(f"Translation error: {e}")
            return text
    
    def _translate_with_google(
        self,
        text: str,
        target: str,
        source: str = 'en'
    ) -> str:
        """Translate using Google Translate API."""
        try:
            url = "https://translation.googleapis.com/language/translate/v2"
            params = {
                'key': TRANSLATION_API_KEY,
                'q': text,
                'source': source,
                'target': target,
                'format': 'text'
            }
            
            response = requests.post(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                translated_text = data['data']['translations'][0]['translatedText']
                self.logger.info(f"✅ Translated: {text[:30]}... -> {translated_text[:30]}...")
                return translated_text
            
            return text
            
        except Exception as e:
            self.logger.error(f"Google Translate API error: {e}")
            return text
    
    def _translate_simple(self, text: str, target_language: str) -> str:
        """
        Simple dictionary-based translation for common food/health terms.
        
        Args:
            text: Text to translate
            target_language: Target language
            
        Returns:
            Translated text
        """
        # Common translations dictionary
        translations = {
            'ar': {
                'SAFE': 'آمن',
                'WARNING': 'تحذير',
                'DANGER': 'خطر',
                'High sugar': 'سكر عالي',
                'High sodium': 'صوديوم عالي',
                'High fat': 'دهون عالية',
                'Moderate sodium': 'صوديوم معتدل',
                'Contains allergens': 'يحتوي على مسببات حساسية',
                'Artificial additives': 'إضافات صناعية',
                'Preservatives': 'مواد حافظة',
                'Unknown': 'غير معروف',
                'Snack': 'وجبة خفيفة',
                'Beverage': 'مشروب',
                'Food': 'طعام',
                'Product': 'منتج',
            },
            'fr': {
                'SAFE': 'Sûr',
                'WARNING': 'Attention',
                'DANGER': 'Danger',
                'High sugar': 'Sucre élevé',
                'High sodium': 'Sodium élevé',
                'High fat': 'Graisse élevée',
                'Moderate sodium': 'Sodium modéré',
                'Contains allergens': 'Contient des allergènes',
                'Artificial additives': 'Additifs artificiels',
                'Preservatives': 'Conservateurs',
                'Unknown': 'Inconnu',
                'Snack': 'Collation',
                'Beverage': 'Boisson',
                'Food': 'Nourriture',
                'Product': 'Produit',
            },
            'es': {
                'SAFE': 'Seguro',
                'WARNING': 'Advertencia',
                'DANGER': 'Peligro',
                'High sugar': 'Alto en azúcar',
                'High sodium': 'Alto en sodio',
                'High fat': 'Alto en grasa',
                'Moderate sodium': 'Sodio moderado',
                'Contains allergens': 'Contiene alérgenos',
                'Artificial additives': 'Aditivos artificiales',
                'Preservatives': 'Conservantes',
                'Unknown': 'Desconocido',
                'Snack': 'Bocadillo',
                'Beverage': 'Bebida',
                'Food': 'Comida',
                'Product': 'Producto',
            }
        }
        
        lang_dict = translations.get(target_language, {})
        
        # Try to translate known terms
        for eng_term, translated_term in lang_dict.items():
            if eng_term.lower() in text.lower():
                text = text.replace(eng_term, translated_term)
        
        return text
    
    def translate_analysis_result(
        self,
        result: Dict[str, Any],
        target_language: str = 'ar'
    ) -> Dict[str, Any]:
        """
        Translate analysis result fields to target language.
        
        Args:
            result: Analysis result dictionary
            target_language: Target language code
            
        Returns:
            Translated result dictionary
        """
        if target_language == 'en':
            return result  # Already in English
        
        translated = result.copy()
        
        # Translate specific fields
        if 'verdict' in translated:
            translated['verdict'] = self.translate_text(
                translated['verdict'],
                target_language
            )
        
        if 'warnings' in translated and isinstance(translated['warnings'], list):
            translated['warnings'] = [
                self.translate_text(warning, target_language)
                for warning in translated['warnings']
            ]
        
        if 'product' in translated:
            translated['product_translated'] = self.translate_text(
                translated['product'],
                target_language
            )
        
        # Add language indicator
        translated['translated_to'] = target_language
        
        return translated


# Global instance
translation_service = None


def get_translation_service() -> TranslationService:
    """Get or create global translation service instance."""
    global translation_service
    if translation_service is None:
        translation_service = TranslationService()
    return translation_service
