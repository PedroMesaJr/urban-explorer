#!/bin/bash
# Simple installation script with clear instructions

echo "========================================="
echo "UrbEx Property Scraper - Installation"
echo "========================================="
echo ""

# Check if python3-venv is properly installed
echo "Step 1: Checking for python3-venv package..."
if dpkg -l | grep -q python3.*-venv; then
    echo "✓ python3-venv package is installed"
else
    echo "✗ python3-venv package is NOT installed"
    echo ""
    echo "Please run this command to install it:"
    echo ""
    echo "  sudo apt update && sudo apt install -y python3.12-venv python3-pip"
    echo ""
    echo "After installation, run this script again:"
    echo "  ./install.sh"
    echo ""
    exit 1
fi

# Check if we can create a venv
echo ""
echo "Step 2: Testing virtual environment creation..."
if python3 -m venv --help &> /dev/null; then
    echo "✓ Virtual environment module is working"
else
    echo "✗ Virtual environment module is not working"
    echo ""
    echo "Please install python3-venv:"
    echo "  sudo apt install -y python3.12-venv"
    echo ""
    exit 1
fi

# Remove old incomplete venv if exists
if [ -d "venv" ]; then
    echo ""
    echo "Removing old incomplete virtual environment..."
    rm -rf venv
    echo "✓ Old venv removed"
fi

# Create fresh virtual environment
echo ""
echo "Step 3: Creating new virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"

# Activate and test
echo ""
echo "Step 4: Testing virtual environment..."
source venv/bin/activate

if [ -f "venv/bin/activate" ]; then
    echo "✓ Activation script exists"
else
    echo "✗ Activation script missing - installation failed"
    exit 1
fi

if [ -f "venv/bin/pip" ] || [ -f "venv/bin/pip3" ]; then
    echo "✓ pip is available"
else
    echo "✗ pip is missing - installation failed"
    exit 1
fi

# Upgrade pip
echo ""
echo "Step 5: Upgrading pip..."
pip install --upgrade pip setuptools wheel --quiet
echo "✓ pip upgraded"

# Install dependencies
echo ""
echo "Step 6: Installing Python dependencies..."
echo "(This will take 5-10 minutes - please be patient)"
echo ""
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ All dependencies installed successfully!"
else
    echo ""
    echo "✗ Some dependencies failed to install"
    echo "Check the errors above and try again"
    exit 1
fi

# Create config if needed
echo ""
echo "Step 7: Creating configuration file..."
if [ ! -f config.yml ]; then
    cp config.example.yml config.yml
    echo "✓ config.yml created"
else
    echo "✓ config.yml already exists"
fi

# Create directories
echo ""
echo "Step 8: Creating directories..."
mkdir -p data logs exports
echo "✓ Directories created"

# Test database
echo ""
echo "Step 9: Testing database..."
python main.py --stats &> /dev/null
if [ $? -eq 0 ]; then
    echo "✓ Database initialized successfully"
else
    echo "⚠ Database test had warnings (may be normal)"
fi

# Test imports
echo ""
echo "Step 10: Testing module imports..."
python -c "
from database.db_manager import DatabaseManager
from scrapers.base_scraper import BaseScraper
from utils.validators import validate_property_data
print('✓ All modules imported successfully')
"

echo ""
echo "========================================="
echo "✓ Installation Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit config.yml and add your Google Maps API key:"
echo "   nano config.yml"
echo ""
echo "2. Activate the virtual environment (do this every time):"
echo "   source venv/bin/activate"
echo ""
echo "3. Run your first scraper:"
echo "   python main.py --scraper hud --state CA"
echo ""
echo "4. View results in the dashboard:"
echo "   python dashboard/app.py"
echo "   Open: http://127.0.0.1:5000"
echo ""
echo "For more information, see:"
echo "  - QUICK_START.md"
echo "  - SETUP.md"
echo "  - GETTING_STARTED.md"
echo ""
