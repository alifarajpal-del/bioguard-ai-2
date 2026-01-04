"""
Tests for AI Engine module (services/engine.py)
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from services.engine import (
    analyze_image,
    analyze_image_sync,
    _build_provider_order,
    _analyze_with_gemini,
    _analyze_with_openai,
    _mock_analysis
)


class TestProviderOrdering:
    """Test provider fallback ordering logic."""
    
    def test_build_provider_order_gemini_preferred(self):
        """Test provider order when Gemini is preferred."""
        with patch('services.engine.GEMINI_API_KEY', 'test-key'):
            with patch('services.engine.OPENAI_API_KEY', 'test-key-2'):
                order = _build_provider_order('gemini')
                assert order[0] == 'gemini'
                assert 'openai' in order
                assert order[-1] == 'mock'
    
    def test_build_provider_order_openai_preferred(self):
        """Test provider order when OpenAI is preferred."""
        with patch('services.engine.OPENAI_API_KEY', 'test-key'):
            with patch('services.engine.GEMINI_API_KEY', 'test-key-2'):
                order = _build_provider_order('openai')
                assert order[0] == 'openai'
                assert 'gemini' in order
                assert order[-1] == 'mock'
    
    def test_build_provider_order_no_keys(self):
        """Test provider order when no API keys are available."""
        with patch('services.engine.GEMINI_API_KEY', ''):
            with patch('services.engine.OPENAI_API_KEY', ''):
                order = _build_provider_order('gemini')
                assert order == ['mock']


class TestMockAnalysis:
    """Test mock analysis fallback."""
    
    @pytest.mark.asyncio
    async def test_mock_analysis_returns_valid_structure(self):
        """Test that mock analysis returns valid data structure."""
        result = await _mock_analysis()
        
        assert 'product' in result
        assert 'health_score' in result
        assert 'verdict' in result
        assert 'warnings' in result
        assert isinstance(result['health_score'], int)
        assert 0 <= result['health_score'] <= 100
        assert result['verdict'] in ['SAFE', 'WARNING', 'DANGER']
    
    @pytest.mark.asyncio
    async def test_mock_analysis_is_fast(self):
        """Test that mock analysis completes quickly."""
        import time
        start = time.time()
        await _mock_analysis()
        duration = time.time() - start
        assert duration < 1.0  # Should complete in under 1 second


class TestImageAnalysis:
    """Test main image analysis function."""
    
    @pytest.mark.asyncio
    async def test_analyze_image_with_mock(self, sample_image_bytes):
        """Test image analysis with mock provider."""
        with patch('services.engine.GEMINI_API_KEY', ''):
            with patch('services.engine.OPENAI_API_KEY', ''):
                result = await analyze_image(sample_image_bytes, 'gemini')
                
                assert result is not None
                assert 'product' in result
                assert 'health_score' in result
                assert 'verdict' in result
    
    @pytest.mark.asyncio
    async def test_analyze_image_error_collection(self, sample_image_bytes):
        """Test that errors are collected during fallback."""
        with patch('services.engine.GEMINI_API_KEY', 'invalid-key'):
            with patch('services.engine.OPENAI_API_KEY', ''):
                with patch('services.engine._analyze_with_gemini', side_effect=RuntimeError("Test error")):
                    result = await analyze_image(sample_image_bytes, 'gemini')
                    
                    # Should fall back to mock
                    assert result is not None
                    assert any('mock data' in str(w).lower() for w in result.get('warnings', []))
    
    def test_analyze_image_sync(self, sample_image_bytes):
        """Test synchronous wrapper for analyze_image."""
        with patch('services.engine.GEMINI_API_KEY', ''):
            with patch('services.engine.OPENAI_API_KEY', ''):
                result = analyze_image_sync(sample_image_bytes, 'gemini')
                
                assert result is not None
                assert 'product' in result


class TestGeminiIntegration:
    """Test Gemini API integration."""
    
    @pytest.mark.asyncio
    async def test_analyze_with_gemini_missing_key(self, sample_image_bytes):
        """Test Gemini analysis fails without API key."""
        with patch('services.engine.GEMINI_API_KEY', ''):
            with pytest.raises(RuntimeError, match="GEMINI_API_KEY is missing"):
                await _analyze_with_gemini(sample_image_bytes)
    
    @pytest.mark.asyncio
    async def test_analyze_with_gemini_returns_structure(self, sample_image_bytes):
        """Test Gemini analysis returns expected structure."""
        mock_response = Mock()
        mock_response.text = '{"product": "Test", "health_score": 80}'
        
        mock_model = Mock()
        mock_model.generate_content = Mock(return_value=mock_response)
        
        with patch('services.engine.GEMINI_API_KEY', 'test-key'):
            with patch('google.generativeai.configure'):
                with patch('google.generativeai.GenerativeModel', return_value=mock_model):
                    result = await _analyze_with_gemini(sample_image_bytes)
                    
                    assert 'product' in result
                    assert 'health_score' in result


class TestOpenAIIntegration:
    """Test OpenAI API integration."""
    
    @pytest.mark.asyncio
    async def test_analyze_with_openai_missing_key(self, sample_image_bytes):
        """Test OpenAI analysis fails without API key."""
        with patch('services.engine.OPENAI_API_KEY', ''):
            with pytest.raises(RuntimeError, match="OPENAI_API_KEY is missing"):
                await _analyze_with_openai(sample_image_bytes)
    
    @pytest.mark.asyncio
    async def test_analyze_with_openai_returns_structure(self, sample_image_bytes):
        """Test OpenAI analysis returns expected structure."""
        mock_choice = Mock()
        mock_choice.message.content = "Product analysis: healthy snack"
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        mock_client = Mock()
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        
        with patch('services.engine.OPENAI_API_KEY', 'test-key'):
            with patch('openai.OpenAI', return_value=mock_client):
                result = await _analyze_with_openai(sample_image_bytes)
                
                assert 'product' in result
                assert 'health_score' in result


class TestErrorHandling:
    """Test error handling and resilience."""
    
    @pytest.mark.asyncio
    async def test_analyze_image_handles_network_error(self, sample_image_bytes):
        """Test that network errors don't crash the analysis."""
        with patch('services.engine.GEMINI_API_KEY', 'test-key'):
            with patch('services.engine._analyze_with_gemini', side_effect=ConnectionError("Network error")):
                result = await analyze_image(sample_image_bytes, 'gemini')
                
                # Should fall back to mock
                assert result is not None
                assert 'product' in result
    
    @pytest.mark.asyncio
    async def test_analyze_image_handles_invalid_response(self, sample_image_bytes):
        """Test handling of invalid API responses."""
        with patch('services.engine.GEMINI_API_KEY', 'test-key'):
            with patch('services.engine._analyze_with_gemini', side_effect=ValueError("Invalid JSON")):
                result = await analyze_image(sample_image_bytes, 'gemini')
                
                assert result is not None
                assert 'warnings' in result
