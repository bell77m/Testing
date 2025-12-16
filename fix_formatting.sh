#!/bin/bash

# Quick Fix: Format all Python code to pass GitLab CI lint checks
# This will fix the "10 files would be reformatted" error

echo "=================================================="
echo "🚀 Quick Fix: Formatting All Python Code"
echo "=================================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if we have the formatters installed
echo -e "\n${YELLOW}📦 Checking formatters...${NC}"

MISSING_PACKAGES=()

for package in black isort flake8; do
    if ! command -v $package &> /dev/null; then
        MISSING_PACKAGES+=($package)
    else
        VERSION=$($package --version 2>&1 | head -n 1)
        echo -e "${GREEN}✓ $package found${NC}"
    fi
done

# Install missing packages
if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "\n${YELLOW}Installing missing packages: ${MISSING_PACKAGES[*]}${NC}"
    pip install ${MISSING_PACKAGES[*]}
fi

# Show what will be formatted
echo -e "\n${BLUE}📁 Python files in project:${NC}"
find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" -not -path "./build/*" | head -n 20

# Format with isort
echo -e "\n${YELLOW}🔧 Step 1/3: Sorting imports with isort...${NC}"
isort . \
    --profile black \
    --line-length 120 \
    --skip venv \
    --skip .venv \
    --skip build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Imports sorted${NC}"
else
    echo -e "${RED}❌ isort had issues${NC}"
fi

# Format with black
echo -e "\n${YELLOW}🔧 Step 2/3: Formatting code with black...${NC}"
black . \
    --line-length 120 \
    --exclude '/(\.venv|venv|build|dist|\.git|__pycache__|\.pytest_cache)/'

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Code formatted${NC}"
else
    echo -e "${RED}❌ black had issues${NC}"
fi

# Check with flake8
echo -e "\n${YELLOW}🔧 Step 3/3: Checking with flake8...${NC}"
flake8 . \
    --max-line-length=120 \
    --ignore=E203,W503,E501 \
    --exclude=venv,.venv,build,dist,.git,__pycache__,.pytest_cache \
    --count \
    --statistics

FLAKE8_EXIT=$?

# Show git changes
echo -e "\n${BLUE}📊 Changes made:${NC}"
if git rev-parse --git-dir > /dev/null 2>&1; then
    git diff --stat

    if [ -n "$(git status --porcelain)" ]; then
        echo -e "\n${YELLOW}Modified files:${NC}"
        git status --short | grep "^ M.*\.py$" || echo "No Python files modified"
    else
        echo -e "${GREEN}No changes needed - code already formatted!${NC}"
    fi
else
    echo "Not a git repository - can't show diff"
fi

# Summary
echo ""
echo "=================================================="
echo -e "${GREEN}✅ Formatting Complete!${NC}"
echo "=================================================="
echo ""

if [ $FLAKE8_EXIT -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed!${NC}"
    echo ""
    echo "Your code is now formatted and ready for GitLab CI."
else
    echo -e "${YELLOW}⚠️  Some flake8 warnings remain (non-blocking)${NC}"
    echo ""
    echo "Your code is formatted, but there are style suggestions above."
fi

echo ""
echo "📝 Next steps:"
echo "   1. Review changes: git diff"
echo "   2. Stage changes: git add ."
echo "   3. Commit: git commit -m 'style: format code with black and isort'"
echo "   4. Push: git push"
echo ""
echo "💡 To prevent this in future:"
echo "   Run: ./setup_git_hooks.sh"
echo "   This will auto-format code before every commit!"
echo ""
echo "=================================================="

# Exit with success if formatting worked
if [ $? -eq 0 ]; then
    exit 0
else
    exit 1
fi