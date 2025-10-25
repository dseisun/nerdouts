#!/bin/bash
# Development Environment Reset Script for Nerdouts
# WARNING: This will delete your local database and cache files!

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "${RED}======================================"
echo "Nerdouts Development Reset"
echo "======================================${NC}"
echo ""
echo "${YELLOW}WARNING: This will:${NC}"
echo "  - Delete all .db database files"
echo "  - Remove Python cache files"
echo "  - Remove test coverage reports"
echo "  - Reinitialize the database"
echo ""
read -p "Are you sure you want to continue? (y/n) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "Cleaning up..."

# Clean build artifacts
echo "Removing cache files..."
make clean

# Remove database files
echo "Removing database files..."
make clean-db

# Reinitialize database
echo ""
read -p "Reinitialize database with sample data? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Reinitializing database..."
    python -m nerdouts.init_db --force --exercises nerdouts/exercises.json --static-workouts
    echo "${GREEN}✓ Database reinitialized${NC}"
fi

echo ""
echo "${GREEN}======================================"
echo "✓ Development environment reset!"
echo "======================================${NC}"
echo ""
echo "Ready to start fresh. Run: make run"
