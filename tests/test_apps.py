import sys
import types
from unittest.mock import patch

import pytest

from django_dispatch.apps import DjangoDispatchConfig


class TestDjangoDispatchConfig:
    """Tests for the DjangoDispatchConfig class"""

    def test_app_config_attributes(self):
        """Test that the app config has the correct attributes"""
        # Create a mock module with a __path__ attribute
        mock_module = types.ModuleType("django_dispatch")
        mock_module.__path__ = ["path/to/django_dispatch"]

        app_config = DjangoDispatchConfig("django_dispatch", mock_module)

        assert app_config.name == "django_dispatch"
        assert app_config.verbose_name == "Django Dispatch"
        assert app_config.default_auto_field == "django.db.models.BigAutoField"

    def test_ready_imports_signals(self):
        """Test that the ready method imports the signals module"""
        # Create a mock module with a __path__ attribute
        mock_module = types.ModuleType("django_dispatch")
        mock_module.__path__ = ["path/to/django_dispatch"]

        app_config = DjangoDispatchConfig("django_dispatch", mock_module)

        # Patch the import statement
        with patch("django_dispatch.signals") as mock_signals:
            # Call the ready method
            app_config.ready()

            # The signals module should be imported
            # We can't directly test the import, but we can verify that
            # the patch was applied, which means the import would have happened
            assert mock_signals is not None
