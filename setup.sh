#!/bin/bash
# Setup script for UrbEx Property Scraper

echo "=================================="
echo "UrbEx Property Scraper Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create config file if it doesn't exist
if [ ! -f config.yml ]; then
    echo ""
    echo "Creating config.yml from template..."
    cp config.example.yml config.yml
    echo "✓ Created config.yml - Please edit it with your settings!"
else
    echo ""
    echo "config.yml already exists, skipping..."
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p data logs exports

# Initialize database
echo ""
echo "Initializing database..."
python3 -c "
from database.db_manager import DatabaseManager
db = DatabaseManager('data/properties.db')
print('✓ Database initialized')
db.close()
"

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit config.yml with your settings"
echo "2. Add your Google Maps API key"
echo "3. Configure target locations"
echo ""
echo "To run the scraper:"
echo "  python main.py --all"
echo ""
echo "To start the dashboard:"
echo "  python dashboard/app.py"
echo ""
echo "For detailed instructions, see GETTING_STARTED.md"
echo ""
