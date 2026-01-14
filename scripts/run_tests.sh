#!/bin/bash
# Script to run tests for BlackMamba Cognitive Core

echo "================================================"
echo "BlackMamba Cognitive Core - Test Runner"
echo "================================================"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "Error: pytest is not installed"
    echo "Please install with: pip install -r requirements-dev.txt"
    exit 1
fi

# Default to all tests
TEST_PATH="${1:-tests/}"

echo "Running tests from: $TEST_PATH"
echo ""

# Run tests with coverage
pytest "$TEST_PATH" \
    --verbose \
    --cov=blackmamba \
    --cov-report=term-missing \
    --cov-report=html \
    -v

EXIT_CODE=$?

echo ""
echo "================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ All tests passed!"
    echo "Coverage report generated in htmlcov/index.html"
else
    echo "✗ Some tests failed"
fi
echo "================================================"

exit $EXIT_CODE
