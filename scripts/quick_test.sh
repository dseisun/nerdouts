#!/bin/bash
# Quick test runner for Nerdouts development
# Usage: ./scripts/quick_test.sh [test_file_or_pattern]

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

if [ -z "$1" ]; then
    echo "${YELLOW}Running all tests...${NC}"
    pytest -v
else
    echo "${YELLOW}Running tests: $1${NC}"
    pytest "$1" -v
fi

echo ""
echo "${GREEN}✓ Tests completed${NC}"
