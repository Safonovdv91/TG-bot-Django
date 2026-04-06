"""
Configuration file for pytest tests in core/tests/.

Содержит фикстуры и настройку для тестов.
"""

pytest_plugins = [
    "tests.fixtures.database",
    "tests.fixtures.telegram",
    "tests.fixtures.users",
]
