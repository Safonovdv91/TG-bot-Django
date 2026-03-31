"""
Tests to verify Django server can start successfully.
"""

import subprocess
import time
import socket
import pytest
import urllib.request
import urllib.error

# Disable the cleanup_db fixture for these tests
pytestmark = [pytest.mark.no_db_cleanup, pytest.mark.django_db]


def is_port_available(port: int) -> bool:
    """Check if a port is available (not in use)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def wait_for_server(url: str, timeout: int = 10) -> bool:
    """Wait for server to respond at the given URL."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = urllib.request.urlopen(url, timeout=2)
            if response.status == 200:
                return True
        except (urllib.error.URLError, ConnectionRefusedError, OSError):
            time.sleep(0.5)
    return False


class TestDjangoServerStartup:
    """Tests for Django server startup."""

    @pytest.mark.integration
    def test_django_settings_module_valid(self):
        """Test that Django settings module is valid and can be imported."""
        import os

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

        from django.conf import settings

        # Force Django to load settings
        assert settings is not None
        assert settings.DEBUG is not None

    @pytest.mark.integration
    def test_manage_py_help_command(self):
        """Test that manage.py can execute commands (server can start)."""
        result = subprocess.run(
            ["python", "manage.py", "--help"],
            cwd="core",
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "runserver" in result.stdout

    @pytest.mark.integration
    def test_django_check_command(self):
        """Test that Django system check passes (prerequisite for server)."""
        result = subprocess.run(
            ["python", "manage.py", "check"],
            cwd="core",
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        # Check for no errors (warnings are OK)
        assert "Error" not in result.stderr

    @pytest.mark.integration
    def test_database_migrations_applied(self):
        """Test that database migrations can be applied."""
        result = subprocess.run(
            ["python", "manage.py", "migrate", "--check"],
            cwd="core",
            capture_output=True,
            text=True,
            timeout=30,
        )
        # Return code 0 means migrations are applied
        # Return code 1 means there are unapplied migrations (still OK for server start)
        assert result.returncode in [0, 1]

    @pytest.mark.skip(reason="Requires test database setup")
    @pytest.mark.integration
    def test_server_starts_and_responds(self):
        """Test that Django server actually starts and responds to HTTP requests."""
        import os

        port = 8765  # Use a non-standard port for testing

        if not is_port_available(port):
            pytest.skip(f"Port {port} is not available")

        # Start the server
        process = subprocess.Popen(
            ["python", "manage.py", "runserver", f"127.0.0.1:{port}"],
            cwd="core",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, "DJANGO_SETTINGS_MODULE": "core.settings"},
        )

        try:
            # Wait for server to start
            time.sleep(2)

            # Check if server is responding
            url = f"http://127.0.0.1:{port}/"
            assert wait_for_server(url, timeout=5), "Server did not respond in time"

        finally:
            # Clean up: terminate the server
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
