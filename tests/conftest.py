"""
Pytest configuration and fixtures for BioGuard AI tests.
"""

import pytest
import os
import tempfile
from pathlib import Path

# Set test environment
os.environ['ENVIRONMENT'] = 'testing'
os.environ['JWT_SECRET_KEY'] = 'test-secret-key-for-testing-only'
os.environ['DATABASE_PATH'] = ':memory:'  # Use in-memory database for tests


@pytest.fixture
def temp_db_path():
    """Create temporary database path for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    # Cleanup
    try:
        os.unlink(db_path)
    except:
        pass


@pytest.fixture
def sample_image_bytes():
    """Provide sample image bytes for testing."""
    # Create a simple 100x100 red image
    from PIL import Image
    import io
    
    img = Image.new('RGB', (100, 100), color='red')
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    return buf.getvalue()


@pytest.fixture
def sample_user_data():
    """Provide sample user data for testing."""
    return {
        'username': 'test_user',
        'password': 'test_password_123',
        'email': 'test@bioguard.ai',
        'allergies': ['peanuts', 'dairy'],
        'health_conditions': ['diabetes'],
        'age': 30,
        'weight_kg': 70.0
    }


@pytest.fixture
def sample_analysis_result():
    """Provide sample analysis result for testing."""
    return {
        'product': 'Test Product',
        'health_score': 75,
        'verdict': 'SAFE',
        'warnings': ['High sugar content'],
        'ingredients': ['sugar', 'flour', 'water'],
        'nova_score': 3,
        'category': 'snack'
    }


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment after each test."""
    yield
    # Cleanup any test artifacts
    pass
