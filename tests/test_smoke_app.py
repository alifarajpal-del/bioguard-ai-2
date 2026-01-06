"""Smoke tests to ensure basic app functionality and imports."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_import_main():
    """Test that main module can be imported."""
    try:
        import main
        assert main is not None
    except ImportError as e:
        pytest.fail(f"Failed to import main: {e}")


def test_import_services():
    """Test that service modules can be imported."""
    try:
        from services import nutrition_api, engine
        assert nutrition_api is not None
        assert engine is not None
    except ImportError as e:
        pytest.fail(f"Failed to import services: {e}")


def test_import_ui_components():
    """Test that UI component modules can be imported."""
    try:
        from ui_components import camera_view, dashboard_view, vault_view
        from ui_components import micro_ux, ui_kit, error_ui
        assert all([camera_view, dashboard_view, vault_view, micro_ux, ui_kit, error_ui])
    except ImportError as e:
        pytest.fail(f"Failed to import UI components: {e}")


def test_import_utils():
    """Test that utility modules can be imported."""
    try:
        from utils import helpers, validation, logging_setup
        assert all([helpers, validation, logging_setup])
    except ImportError as e:
        pytest.fail(f"Failed to import utils: {e}")


def test_config_settings():
    """Test that config settings can be loaded."""
    try:
        from config import settings
        assert hasattr(settings, 'CACHE_ENABLED')
        assert hasattr(settings, 'LOG_LEVEL')
    except ImportError as e:
        pytest.fail(f"Failed to import config: {e}")


if __name__ == "__main__":
    # Run tests manually without pytest
    print("Running smoke tests...")
    tests = [
        test_import_main,
        test_import_services,
        test_import_ui_components,
        test_import_utils,
        test_config_settings,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
