#!/bin/bash

# Setup Test Report Generation System
# This script sets up all necessary files and directories

echo "=================================================="
echo "🚀 Setting up Test Report Generation System"
echo "=================================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Create necessary directories
echo -e "\n${YELLOW}📁 Creating directories...${NC}"
mkdir -p scripts
mkdir -p utils
mkdir -p docs/generated_reports
mkdir -p reports/allure-results
mkdir -p logs

echo -e "${GREEN}✓ Directories created${NC}"

# Check if Python is installed
echo -e "\n${YELLOW}🐍 Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi

# Check if Pandoc is installed
echo -e "\n${YELLOW}📄 Checking Pandoc installation...${NC}"
if command -v pandoc &> /dev/null; then
    PANDOC_VERSION=$(pandoc --version | head -n 1)
    echo -e "${GREEN}✓ Pandoc found: $PANDOC_VERSION${NC}"
else
    echo -e "${YELLOW}⚠ Pandoc not found${NC}"
    echo "Pandoc is required for PDF/DOCX generation."
    echo ""
    echo "Install instructions:"
    echo "  macOS:   brew install pandoc"
    echo "  Ubuntu:  sudo apt-get install pandoc"
    echo "  Windows: Download from https://pandoc.org/installing.html"
    echo ""
    read -p "Continue without Pandoc? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install Python dependencies
echo -e "\n${YELLOW}📦 Installing Python dependencies...${NC}"
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}✗ requirements.txt not found${NC}"
fi

# Create __init__.py files
echo -e "\n${YELLOW}📝 Creating __init__.py files...${NC}"
touch scripts/__init__.py
touch utils/__init__.py
echo -e "${GREEN}✓ __init__.py files created${NC}"

# Test the setup
echo -e "\n${YELLOW}🧪 Testing setup...${NC}"

# Check if calculate_metrics.py exists
if [ -f scripts/calculate_metrics.py ]; then
    echo -e "${GREEN}✓ calculate_metrics.py found${NC}"
else
    echo -e "${YELLOW}⚠ calculate_metrics.py not found${NC}"
    echo "This file should have been created. Please check the artifacts."
fi

# Check if generate_reports.py exists
if [ -f scripts/generate_reports.py ]; then
    echo -e "${GREEN}✓ generate_reports.py found${NC}"
else
    echo -e "${YELLOW}⚠ generate_reports.py not found${NC}"
    echo "This file should have been created. Please check the artifacts."
fi

# Check if test_report_generator.py exists
if [ -f utils/test_report_generator.py ]; then
    echo -e "${GREEN}✓ test_report_generator.py found${NC}"
else
    echo -e "${YELLOW}⚠ test_report_generator.py not found${NC}"
    echo "This file should have been created. Please check the artifacts."
fi

# Create a test run to verify everything works
echo -e "\n${YELLOW}🔍 Running verification test...${NC}"

# Create a dummy test result for testing
mkdir -p reports/allure-results
cat > reports/allure-results/test-result.json << 'EOF'
{
  "uuid": "test-uuid-123",
  "name": "Test Setup Verification",
  "status": "passed",
  "statusDetails": {},
  "stage": "finished",
  "description": "This is a test result to verify the setup",
  "start": 1700000000000,
  "stop": 1700000001000,
  "steps": []
}
EOF

# Try to run calculate_metrics.py
if [ -f scripts/calculate_metrics.py ]; then
    echo -e "\n${YELLOW}Running calculate_metrics.py...${NC}"
    python3 scripts/calculate_metrics.py

    if [ -f metrics.txt ]; then
        echo -e "${GREEN}✓ Metrics file generated successfully${NC}"
        cat metrics.txt
    fi
fi

# Summary
echo -e "\n=================================================="
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo -e "=================================================="
echo ""
echo "📁 Created directories:"
echo "   • scripts/"
echo "   • utils/"
echo "   • docs/generated_reports/"
echo "   • reports/allure-results/"
echo ""
echo "📝 Next steps:"
echo "   1. Run tests: pytest tests/ --alluredir=reports/allure-results"
echo "   2. Generate metrics: python scripts/calculate_metrics.py"
echo "   3. Generate reports: python scripts/generate_reports.py"
echo ""
echo "🔗 Useful commands:"
echo "   • View metrics: cat metrics.txt"
echo "   • View summary: cat test-summary.md"
echo "   • Open HTML report: open docs/generated_reports/*.html"
echo ""
echo "📚 Documentation: See REPORT_SETUP.md for detailed instructions"
echo ""
echo "=================================================="

# Clean up test file
rm -f reports/allure-results/test-result.json