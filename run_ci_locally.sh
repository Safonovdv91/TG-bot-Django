#!/usr/bin/env bash
#
# Local CI Checker
# Запускает те же команды, что и GitHub Actions CI
#

set -e

echo "========================================"
echo "  Local CI Simulation"
echo "========================================"
echo ""

# Step 1: Check Python version
echo "✓ Checking Python version..."
PYTHON_VERSION=$(uv run python --version 2>&1)
echo "  $PYTHON_VERSION"
echo ""

# Step 2: Run tests (like in CI)
echo "✓ Running tests (like in CI)..."
echo "  Command: uv run pytest core/tests/ -v --tb=short"
echo ""
uv run pytest core/tests/ -v --tb=short

echo ""
echo "========================================"
echo "  ✓ All CI checks passed!"
echo "========================================"
