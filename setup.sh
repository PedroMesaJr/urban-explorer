#!/bin/bash
# Setup script for UrbEx Property Scraper

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=================================="
echo "UrbEx Property Scraper Setup"
echo "=================================="
echo ""

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if running on WSL/Linux/Mac
echo "Checking system..."
if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
    print_success "System detected: $OSTYPE"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    print_warning "Windows detected. Please use WSL2 for best compatibility."
fi

# Check Python version
echo ""
echo "Checking Python version..."
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Found Python $python_version"

    # Check if version is 3.8+
    python_major=$(echo $python_version | cut -d. -f1)
    python_minor=$(echo $python_version | cut -d. -f2)

    if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 8 ]); then
        print_error "Python 3.8+ required. Found $python_version"
        exit 1
    fi
else
    print_error "Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check for venv module
echo ""
echo "Checking for python3-venv..."
if python3 -m venv --help &> /dev/null; then
    print_success "python3-venv is available"
else
    print_error "python3-venv not found"
    echo ""
    echo "Please install it with:"
    echo "  sudo apt update && sudo apt install -y python3-venv python3-pip"
    echo ""
    echo "Or on your system's equivalent package manager."
    exit 1
fi

# Check if venv already exists
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Skipping creation."
else
    # Create virtual environment
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel --quiet
print_success "pip upgraded"

# Install dependencies
echo ""
echo "Installing Python dependencies (this may take 5-10 minutes)..."
if pip install -r requirements.txt --quiet; then
    print_success "Dependencies installed successfully"
else
    print_error "Failed to install dependencies"
    echo "Try running manually:"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Create config file if it doesn't exist
echo ""
if [ ! -f config.yml ]; then
    echo "Creating config.yml from template..."
    cp config.example.yml config.yml
    print_success "Created config.yml"
    print_warning "IMPORTANT: Edit config.yml and add your API keys!"
else
    print_warning "config.yml already exists, skipping..."
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p data logs exports
print_success "Directories created"

# Check if database schema exists
if [ ! -f database/schema.sql ]; then
    print_warning "database/schema.sql not found. Database initialization may fail."
fi

# Initialize database
echo ""
echo "Initializing database..."
if python3 main.py --stats &> /dev/null; then
    print_success "Database initialized successfully"
else
    print_warning "Database initialization had warnings (this is normal for first run)"
fi

# Test import of key modules
echo ""
echo "Testing module imports..."
python3 -c "
import sys
try:
    from database.db_manager import DatabaseManager
    print('✓ Database module OK')
except Exception as e:
    print(f'✗ Database module error: {e}')
    sys.exit(1)

try:
    from scrapers.base_scraper import BaseScraper
    print('✓ Scraper module OK')
except Exception as e:
    print(f'✗ Scraper module error: {e}')
    sys.exit(1)

try:
    from utils.validators import validate_property_data
    print('✓ Validators module OK')
except Exception as e:
    print(f'✗ Validators module error: {e}')
    sys.exit(1)
" && print_success "All modules imported successfully"

echo ""
echo "=================================="
echo "✓ Setup Complete!"
echo "=================================="
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Edit config.yml with your settings:"
echo "   ${YELLOW}nano config.yml${NC}"
echo ""
echo "2. Add your Google Maps API key (required for geocoding)"
echo "   Get one at: https://console.cloud.google.com/"
echo ""
echo "3. Customize target locations in config.yml"
echo ""
echo "4. Activate the virtual environment (do this each time):"
echo "   ${GREEN}source venv/bin/activate${NC}"
echo ""
echo "5. Run your first scraper:"
echo "   ${GREEN}python main.py --scraper hud --state CA${NC}"
echo ""
echo "6. View results in the dashboard:"
echo "   ${GREEN}python dashboard/app.py${NC}"
echo "   Open browser to: http://127.0.0.1:5000"
echo ""
echo "7. Export data:"
echo "   ${GREEN}python main.py --export properties.csv${NC}"
echo ""
echo "📖 For detailed instructions, see:"
echo "   - SETUP.md (setup troubleshooting)"
echo "   - GETTING_STARTED.md (usage guide)"
echo "   - PROJECT_OVERVIEW.md (architecture)"
echo ""
echo "⚠️  Remember:"
echo "   - Respect robots.txt and rate limits"
echo "   - Only scrape public records"
echo "   - Don't trespass on properties"
echo ""
echo "Happy property hunting! 🏚️🔍"
echo ""
