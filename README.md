# UrbEx Property Scraper

A comprehensive data collection system for finding abandoned, foreclosed, and distressed properties from multiple public sources.

## Features

- Multi-source property data aggregation
- Automated scraping from public records
- Geographic data enrichment
- SQLite database storage
- Configurable scraping schedules
- Data deduplication and merging

## Data Sources

1. County Tax Assessor Websites (delinquent taxes)
2. Foreclosure Auction Sites (RealtyTrac, Auction.com)
3. HUD Foreclosure Listings
4. Zillow/Realtor.com (property history)
5. Demolition Permit Databases
6. Code Violation Records
7. Google Maps/Street View API
8. News APIs (closure stories)
9. Historical Preservation Databases
10. Manual user submissions

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure settings
cp config.example.yml config.yml
# Edit config.yml with your API keys and target locations
```

## Usage

```bash
# Run all scrapers
python main.py --all

# Run specific scraper
python main.py --scraper tax_assessor --state CA --county "Los Angeles"

# View collected data
python dashboard.py
```

## Project Structure

```
urbex-property-scraper/
├── config.yml              # Configuration and API keys
├── main.py                 # Main orchestrator
├── database/
│   ├── schema.sql          # Database schema
│   ├── models.py           # SQLAlchemy models
│   └── db_manager.py       # Database operations
├── scrapers/
│   ├── base_scraper.py     # Base scraper class
│   ├── tax_assessor.py     # County tax records
│   ├── foreclosure.py      # Foreclosure sites
│   ├── hud.py              # HUD listings
│   ├── zillow.py           # Zillow/Realtor.com
│   ├── permits.py          # Demolition permits
│   ├── violations.py       # Code violations
│   ├── google_maps.py      # Google Maps/Street View
│   └── news.py             # News article scraping
├── utils/
│   ├── geocoding.py        # Address standardization
│   ├── deduplication.py    # Merge duplicate properties
│   └── validators.py       # Data validation
├── dashboard/
│   ├── app.py              # Simple Flask dashboard
│   └── templates/          # HTML templates
└── data/
    └── properties.db       # SQLite database
```

## Legal Notice

This tool is for personal research and educational purposes only. Always:
- Respect robots.txt and terms of service
- Use rate limiting to avoid overloading servers
- Only access public records
- Comply with all local, state, and federal laws
- Never trespass on private property

## License

MIT License - Personal Use Only
