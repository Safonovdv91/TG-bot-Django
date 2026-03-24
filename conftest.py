"""
Configuration file for pytest.

All test settings are defined in core/core/test.py
No environment variables are required - tests are self-contained.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set default environment variables for tests (CI-friendly)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.test")
os.environ.setdefault("DJANGO_DEBUG", "True")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test_bot_token_for_ci")
os.environ.setdefault("GYMKHANA_CUP_TOKEN", "test_token_for_ci")


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line(
        "markers", "no_db_cleanup: skip database cleanup after test"
    )


def pytest_sessionstart(session):
    """Called after the Session object has been created."""
    print("\n" + "=" * 70)
    print("Pytest session started")
    print(f"Django settings: {os.environ.get('DJANGO_SETTINGS_MODULE', 'Not set')}")
    print(f"Database: Using in-memory SQLite (no external DB required)")
    print("=" * 70 + "\n")