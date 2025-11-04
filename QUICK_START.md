# Quick Start - Manual Setup Required

## ⚠️ Action Required

The automated setup requires system packages to be installed. Please run these commands manually:

### Step 1: Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3.12-venv python3-pip
```

**Why?** These commands install:
- `python3.12-venv` - Allows creating virtual environments
- `python3-pip` - Python package installer

### Step 2: Run Automated Setup

Once the system packages are installed, run:

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- ✅ Create a virtual environment
- ✅ Install all Python dependencies
- ✅ Create configuration file
- ✅ Initialize the database
- ✅ Test all modules

## Alternative: Manual Setup

If you prefer to set up manually, follow these steps:

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create Configuration
```bash
cp config.example.yml config.yml
nano config.yml  # Edit and add your API keys
```

### 4. Test Installation
```bash
python main.py --stats
```

You should see:
```
Database Statistics:
Total properties: 0
```

### 5. Run Your First Scraper
```bash
# Example: Scrape HUD foreclosures in California
python main.py --scraper hud --state CA
```

### 6. View Results
```bash
# Start the web dashboard
python dashboard/app.py

# Open browser to: http://127.0.0.1:5000
```

## Required API Keys

### Google Maps (Required for geocoding)

1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable these APIs:
   - Geocoding API
   - Street View Static API (optional)
4. Create API key
5. Add to `config.yml`:

```yaml
api_keys:
  google_maps: YOUR_ACTUAL_API_KEY_HERE
```

**Free tier includes:**
- $200/month credit
- ~40,000 geocoding requests/month

### Other API Keys (Optional)

- **News API**: https://newsapi.org/ (100 req/day free)
- **Zillow**: Requires approval (harder to get)
- **Realtor.com**: Commercial use

## Quick Commands Reference

```bash
# Activate virtual environment (do this every time)
source venv/bin/activate

# View database statistics
python main.py --stats

# Run all scrapers
python main.py --all

# Run specific scraper
python main.py --scraper hud --state CA
python main.py --scraper foreclosure --state TX

# Export data
python main.py --export properties.csv
python main.py --export ca_properties.csv --state CA

# Start dashboard
python dashboard/app.py
```

## Troubleshooting

### "No module named 'requests'"
**Fix:** Activate virtual environment first:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Google Maps API key not configured"
**Fix:** Edit `config.yml` and add your actual API key.

### Empty scraper results
**Possible causes:**
1. Website structure changed (update selectors)
2. Network issues (check internet connection)
3. Rate limiting (increase delays in config)

## Project Structure

```
urbex-property-scraper/
├── scrapers/           # Scraper implementations
│   ├── base_scraper.py
│   ├── hud.py
│   ├── foreclosure.py
│   ├── tax_assessor.py
│   └── google_maps.py
├── database/           # Database code
│   ├── schema.sql
│   ├── models.py
│   └── db_manager.py
├── dashboard/          # Web interface
│   └── app.py
├── utils/              # Utilities
│   ├── validators.py
│   └── geocoding.py
├── data/               # SQLite database
├── logs/               # Log files
├── exports/            # CSV exports
└── config.yml          # Your configuration
```

## What Gets Scraped?

The scrapers collect:
- **Address & Location** (geocoded coordinates)
- **Property Details** (type, size, year built)
- **Tax Status** (delinquent, amount owed)
- **Foreclosure Status** (pre-foreclosure, auction, REO)
- **Abandonment Indicators** (violations, demolition permits)
- **Images** (Street View if Google API configured)

## Scoring System

Each property gets an **Abandonment Score (0-10)**:

- ✅ **0-3**: Low likelihood (active property)
- ✅ **4-6**: Moderate likelihood (watch list)
- ✅ **7-8**: High likelihood (good targets)
- ✅ **9-10**: Very high likelihood (prime locations)

Factors:
- Tax delinquency (2+ years) → +5 points
- In foreclosure → +4 points
- Has code violations → +2 points
- Condemned → +5 points
- No sale in 5+ years → +1 point
- Low assessed value (<$50k) → +1 point

## Legal & Ethical Use

✅ **Allowed:**
- Scraping public records
- Personal research
- Using publicly available APIs
- Respectful rate limiting

❌ **Not Allowed:**
- Trespassing on properties
- Overloading servers
- Commercial use without licensing
- Sharing private owner information

## Next Steps

1. **Read the documentation:**
   - `SETUP.md` - Detailed setup guide
   - `GETTING_STARTED.md` - Usage instructions
   - `PROJECT_OVERVIEW.md` - Architecture details

2. **Customize scrapers:**
   - Add your county's tax assessor
   - Update CSS selectors if sites change
   - Add new data sources

3. **Automate:**
   - Set up cron jobs for regular scraping
   - Configure email notifications
   - Export to external tools

## Getting Help

If stuck:
1. Check `SETUP.md` for troubleshooting
2. Review code comments in scrapers
3. Enable debug logging in `config.yml`
4. Inspect website HTML to verify selectors

## Summary

**To get started right now:**

```bash
# 1. Install system packages (requires password)
sudo apt update && sudo apt install -y python3.12-venv python3-pip

# 2. Run automated setup
chmod +x setup.sh && ./setup.sh

# 3. Edit configuration
nano config.yml  # Add your Google Maps API key

# 4. Run your first scraper
source venv/bin/activate
python main.py --scraper hud --state CA

# 5. View results
python dashboard/app.py
# Open: http://127.0.0.1:5000
```

**Happy property hunting!** 🏚️🔍
