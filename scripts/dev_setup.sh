#!/bin/bash
# Development Environment Setup Script for Nerdouts

set -e  # Exit on error

echo "======================================"
echo "Nerdouts Development Setup"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check for uv package manager
if ! command -v uv &> /dev/null; then
    echo "${YELLOW}uv not found. Installing uv...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
else
    echo "${GREEN}✓ uv already installed${NC}"
fi

# Install dependencies
echo ""
echo "Installing production dependencies..."
uv sync

echo ""
echo "Installing development dependencies..."
uv pip install pytest pytest-cov ruff black mypy

# Check for secrets.yaml
echo ""
if [ ! -f "nerdouts/secrets.yaml" ]; then
    echo "${YELLOW}⚠ secrets.yaml not found${NC}"
    echo "Copying template to nerdouts/secrets.yaml..."
    cp nerdouts/secrets.yaml.template nerdouts/secrets.yaml
    echo "${YELLOW}⚠ Please edit nerdouts/secrets.yaml with your database credentials${NC}"
else
    echo "${GREEN}✓ secrets.yaml exists${NC}"
fi

# Initialize database
echo ""
read -p "Initialize database with sample data? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Initializing database..."
    python -m nerdouts.init_db --force --exercises nerdouts/exercises.json --static-workouts
    echo "${GREEN}✓ Database initialized${NC}"
fi

echo ""
echo "${GREEN}======================================"
echo "✓ Development setup complete!"
echo "======================================${NC}"
echo ""
echo "Available commands:"
echo "  make help          - Show all available commands"
echo "  make run           - Start the web server"
echo "  make test          - Run tests"
echo "  make all-checks    - Run all quality checks"
echo ""
echo "Start developing with: make run"
