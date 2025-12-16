#!/bin/bash

# Setup Git Hooks for Auto-formatting
# This will format your code automatically before each commit

echo "=================================================="
echo "🎨 Setting up Git Hooks for Auto-formatting"
echo "=================================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if we're in a git repository
if [ ! -d .git ]; then
    echo -e "${RED}❌ Error: Not a git repository${NC}"
    echo "Run this script from your project root"
    exit 1
fi

# Install required packages
echo -e "\n${YELLOW}📦 Installing formatters...${NC}"
pip install black isort flake8 pre-commit

# Create pre-commit hook
echo -e "\n${YELLOW}🔧 Creating pre-commit hook...${NC}"

cat > .git/hooks/pre-commit << 'HOOK_EOF'
#!/bin/bash

# Pre-commit hook: Auto-format Python code
echo "🎨 Auto-formatting Python code before commit..."

# Get list of Python files to commit
PYTHON_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ -z "$PYTHON_FILES" ]; then
    echo "✅ No Python files to format"
    exit 0
fi

echo "📝 Found Python files to format:"
echo "$PYTHON_FILES"

# Format with black
echo ""
echo "🔧 Running black..."
black --line-length=120 $PYTHON_FILES

# Sort imports with isort
echo ""
echo "🔧 Running isort..."
isort --profile=black --line-length=120 $PYTHON_FILES

# Add formatted files back to staging
git add $PYTHON_FILES

echo ""
echo "✅ Code formatted and staged!"
echo ""

# Optional: Run flake8 as a warning (don't block commit)
echo "🔍 Running flake8 (warnings only)..."
flake8 $PYTHON_FILES --max-line-length=120 --ignore=E203,W503,E501 || true

exit 0
HOOK_EOF

# Make hook executable
chmod +x .git/hooks/pre-commit

echo -e "${GREEN}✅ Pre-commit hook installed!${NC}"

# Setup pre-commit framework (optional but recommended)
echo -e "\n${YELLOW}🔧 Setting up pre-commit framework...${NC}"

if [ -f .pre-commit-config.yaml ]; then
    echo "✓ .pre-commit-config.yaml already exists"

    # Install pre-commit hooks
    pre-commit install

    echo -e "${GREEN}✅ Pre-commit framework installed!${NC}"
    echo ""
    echo "You can run hooks manually with:"
    echo "  pre-commit run --all-files"
else
    echo -e "${YELLOW}⚠️  .pre-commit-config.yaml not found${NC}"
    echo "Creating basic configuration..."

    cat > .pre-commit-config.yaml << 'PRECOMMIT_EOF'
# Pre-commit hooks for code quality
repos:
  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black
        language_version: python3.11
        args: [--line-length=120]

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: [--profile=black, --line-length=120]

  - repo: https://github.com/pycqa/flake8
    rev: 7.1.1
    hooks:
      - id: flake8
        args: [--max-line-length=120, --ignore=E203,W503,E501]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
      - id: detect-private-key
PRECOMMIT_EOF

    pre-commit install
    echo -e "${GREEN}✅ Pre-commit configuration created and installed!${NC}"
fi

# Test the setup
echo -e "\n${YELLOW}🧪 Testing the setup...${NC}"
echo ""
echo "Creating a test Python file..."

cat > /tmp/test_format.py << 'TEST_EOF'
import os,sys
import json

def bad_function(x,y):
    return x+y

class BadClass:
    def __init__(self,name):
        self.name=name
TEST_EOF

echo "Before formatting:"
cat /tmp/test_format.py

echo ""
echo "Running formatters..."
black --line-length=120 /tmp/test_format.py 2>&1 | head -n 5
isort --profile=black --line-length=120 /tmp/test_format.py 2>&1 | head -n 5

echo ""
echo "After formatting:"
cat /tmp/test_format.py

rm /tmp/test_format.py

# Summary
echo ""
echo "=================================================="
echo -e "${GREEN}✅ Git Hooks Setup Complete!${NC}"
echo "=================================================="
echo ""
echo "📝 What was installed:"
echo "   • Pre-commit hook (auto-formats on commit)"
echo "   • Pre-commit framework"
echo "   • Black (code formatter)"
echo "   • isort (import sorter)"
echo "   • flake8 (style checker)"
echo ""
echo "🎯 How it works:"
echo "   1. You make changes to Python files"
echo "   2. You run: git add <files>"
echo "   3. You run: git commit -m 'message'"
echo "   4. → Hook automatically formats your code"
echo "   5. → Formatted code is included in commit"
echo ""
echo "🔧 Manual commands:"
echo "   • Format all files: python scripts/format_code.py"
echo "   • Run hooks manually: pre-commit run --all-files"
echo "   • Format one file: black --line-length=120 <file>"
echo ""
echo "⚙️  Configuration:"
echo "   • Line length: 120 characters"
echo "   • Profile: black-compatible"
echo "   • Ignored rules: E203, W503, E501"
echo ""
echo "=================================================="