# UrbEx Property Scraper - Setup Guide

## Prerequisites

Before you begin, ensure you have:
- **Python 3.8+** installed (3.12 recommended)
- **sudo/admin access** for installing system packages
- **Internet connection** for downloading dependencies
- **Git** (optional, for version control)

## Quick Setup (Automated)

For most users, the automated setup script will handle everything:

```bash
# Make the setup script executable
chmod +x setup.sh

# Run the automated setup
./setup.sh
```

The script will:
1. Check Python version
2. Install python3-venv and pip (requires sudo)
3. Create a virtual environment
4. Install all Python dependencies
5. Create config.yml from template
6. Create necessary directories
7. Initialize the database
8. Run a quick test

## Manual Setup

If the automated setup doesn't work or you prefer manual installation:

### Step 1: Install System Dependencies

**Ubuntu/Debian/WSL:**
```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip
```

**macOS (with Homebrew):**
```bash
brew install python@3.12
```

**Windows:**
- Download Python 3.12 from [python.org](https://www.python.org/downloads/)
- Ensure "Add Python to PATH" is checked during installation
- Or use WSL2 (recommended)

### Step 2: Create Virtual Environment

```bash
# Navigate to project directory
cd urbex-property-scraper

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac/WSL:
source venv/bin/activate

# On Windows (PowerShell):
# venv\Scripts\Activate.ps1

# On Windows (CMD):
# venv\Scripts\activate.bat
```

**Important:** You'll need to activate the virtual environment every time you work on the project.

### Step 3: Install Python Dependencies

```bash
# Make sure venv is activated (you should see "(venv)" in your prompt)
pip install -r requirements.txt
```

This will install:
- **Web scraping:** requests, beautifulsoup4, selenium, scrapy
- **Database:** sqlalchemy, alembic
- **Data processing:** pandas, numpy
- **Geocoding:** geopy, googlemaps
- **Dashboard:** flask
- **Utilities:** loguru, pyyaml, pydantic
- And more...

**Note:** Installation may take 5-10 minutes depending on your internet speed.

### Step 4: Create Configuration File

```bash
# Copy the example configuration
cp config.example.yml config.yml

# Edit with your preferred editor
nano config.yml
# or
vim config.yml
# or
code config.yml  # VS Code
```

**Minimum required changes:**
```yaml
api_keys:
  google_maps: YOUR_ACTUAL_GOOGLE_MAPS_API_KEY
  # Other API keys are optional
```

**To get a Google Maps API key:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable these APIs:
   - Geocoding API
   - Maps JavaScript API (optional)
   - Street View Static API (optional)
4. Create credentials → API key
5. Copy the key to config.yml

**Free tier includes:**
- $200/month credit
- ~40,000 geocoding requests/month free
- Enough for most personal use cases

### Step 5: Verify Directory Structure

```bash
# These directories should already exist, but verify:
ls -la

# You should see:
# - data/          (database storage)
# - logs/          (log files)
# - exports/       (CSV/JSON exports)
# - scrapers/      (scraper modules)
# - database/      (database code)
# - utils/         (utilities)
# - dashboard/     (web interface)
```

### Step 6: Initialize Database

```bash
# The database will be created automatically on first run
python main.py --stats

# You should see output like:
# Database Statistics:
# Total properties: 0
# By state: {}
# Average abandonment score: N/A
```

If you see this, the database was created successfully!

### Step 7: Test the Installation

```bash
# Test 1: Check CLI help
python main.py --help

# Test 2: Check database stats
python main.py --stats

# Test 3: Try a test scrape (requires config)
# Note: This will attempt real scraping, so ensure you have API keys configured
python main.py --scraper hud --state CA

# Test 4: Start dashboard
python dashboard/app.py

# Open browser to: http://127.0.0.1:5000
```

## Troubleshooting

### Problem: "python3-venv not found"

**Solution:**
```bash
# Ubuntu/Debian/WSL
sudo apt update
sudo apt install python3.12-venv

# Or use your system's Python version
sudo apt install python3-venv
```

### Problem: "pip: command not found"

**Solution:**
```bash
# Ubuntu/Debian/WSL
sudo apt install python3-pip

# Or download pip manually
curl -sS https://bootstrap.pypa.io/get-pip.py | python3
```

### Problem: "externally-managed-environment" error

**Solution:** You MUST use a virtual environment. Don't use `--break-system-packages`.

```bash
# Create venv first
python3 -m venv venv
source venv/bin/activate

# Then install
pip install -r requirements.txt
```

### Problem: "Permission denied" when running setup.sh

**Solution:**
```bash
chmod +x setup.sh
./setup.sh
```

### Problem: Import errors when running scripts

**Solution:** Make sure virtual environment is activated:
```bash
# You should see (venv) in your prompt
source venv/bin/activate

# Then run your command
python main.py --stats
```

### Problem: "Google Maps API key not configured"

**Solution:**
1. Get API key from Google Cloud Console
2. Edit `config.yml`
3. Replace `YOUR_GOOGLE_MAPS_API_KEY_HERE` with actual key
4. Save file and retry

### Problem: "No module named 'bs4'" or similar

**Solution:**
```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Problem: Database locked errors

**Solution:**
- Close any other processes accessing the database
- Only run one scraper at a time
- Or use PostgreSQL instead of SQLite

### Problem: Scraper returns empty results

**Possible causes:**
1. Website HTML structure changed → Update selectors
2. Rate limiting → Increase delays in config.yml
3. Network issues → Check internet connection
4. API quota exceeded → Wait or upgrade plan

## Configuration Tips

### For Testing/Development:
```yaml
# config.yml
scrapers:
  rate_limits:
    default: 60  # Faster for testing
  timeout: 10

logging:
  level: DEBUG  # Verbose output

dashboard:
  debug: true  # Enable Flask debug mode
```

### For Production/Regular Use:
```yaml
# config.yml
scrapers:
  rate_limits:
    default: 10  # Respectful rate limiting
  timeout: 30

logging:
  level: INFO  # Standard output

dashboard:
  debug: false  # Disable debug mode
```

### For Maximum Privacy:
```yaml
# config.yml
scrapers:
  rotate_user_agents: true
  use_proxies: true
  proxy_list:
    - http://your-proxy:8080

geocoding:
  cache_results: true  # Minimize API calls
```

## Next Steps

Once setup is complete:

1. **Customize target locations** in `config.yml`
2. **Run your first scrape:** `python main.py --scraper hud --state CA`
3. **View results:** `python dashboard/app.py`
4. **Export data:** `python main.py --export properties.csv`
5. **Review scrapers** in `scrapers/` directory
6. **Customize for your county** (see GETTING_STARTED.md)

## Getting Help

If you encounter issues not covered here:

1. Check `GETTING_STARTED.md` for usage instructions
2. Review `PROJECT_OVERVIEW.md` for architecture details
3. Enable debug logging: `logging.level: DEBUG` in config.yml
4. Check logs in `logs/scraper.log`
5. Inspect HTML of target websites to verify selectors

## Security & Legal

**Remember:**
- ✅ Only scrape public records
- ✅ Respect robots.txt
- ✅ Use rate limiting
- ✅ Don't overload servers
- ❌ Never trespass on properties
- ❌ Don't share private owner information
- ❌ Personal use only (check terms of service for commercial use)

## System Requirements

**Minimum:**
- Python 3.8+
- 2GB RAM
- 500MB disk space
- Internet connection

**Recommended:**
- Python 3.12
- 4GB+ RAM
- 2GB+ disk space (for large datasets)
- Stable internet connection
- Linux/WSL2 (best compatibility)

## Performance Tips

**For faster scraping:**
1. Use multiple API keys (rotate them)
2. Use proxies for high-volume scraping
3. Run scrapers in parallel (different counties)
4. Cache geocoding results
5. Use PostgreSQL instead of SQLite for large datasets

**For lower costs:**
1. Enable geocoding cache
2. Only geocode when needed
3. Use free tier limits wisely
4. Consider alternative geocoding services (Nominatim is free)

## Updating the Project

```bash
# Activate venv
source venv/bin/activate

# Pull latest changes (if using git)
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Run database migrations (if any)
# python database/migrate.py
```

## Uninstalling

```bash
# Remove virtual environment
rm -rf venv

# Remove database (WARNING: deletes all data)
rm -rf data/properties.db

# Remove logs
rm -rf logs/*

# Remove exports
rm -rf exports/*

# Keep the code if you want to reinstall later
# Or delete the entire directory to remove everything
```

---

**Happy property hunting!** 🏚️🔍

For questions or issues, review the documentation or inspect the code comments.
