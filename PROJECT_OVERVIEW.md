# UrbEx Property Scraper - Project Overview

## What You Just Built

A comprehensive, modular system for finding and tracking abandoned, foreclosed, and distressed properties from multiple public data sources. This is a professional-grade scraping system designed for personal use.

---

## 📁 Project Structure

```
urbex-property-scraper/
├── README.md                   # Main documentation
├── GETTING_STARTED.md          # Quick start guide
├── PROJECT_OVERVIEW.md         # This file
├── requirements.txt            # Python dependencies
├── config.example.yml          # Configuration template
├── config.yml                  # Your actual config (create from example)
├── setup.sh                    # Automated setup script
├── main.py                     # Main application orchestrator
│
├── database/                   # Database layer
│   ├── schema.sql             # SQLite schema with all tables
│   ├── models.py              # SQLAlchemy ORM models
│   └── db_manager.py          # Database operations & queries
│
├── scrapers/                   # Data collection modules
│   ├── base_scraper.py        # Base class with common functionality
│   ├── tax_assessor.py        # County tax records scraper (template)
│   ├── foreclosure.py         # Foreclosure listing sites
│   ├── hud.py                 # HUD foreclosure listings
│   └── google_maps.py         # Geocoding & Street View
│
├── utils/                      # Utility functions
│   ├── geocoding.py           # Address parsing & geocoding
│   └── validators.py          # Data validation & cleaning
│
├── dashboard/                  # Web interface
│   ├── app.py                 # Flask web server
│   └── templates/
│       └── index.html         # Dashboard UI
│
├── data/                       # Database files (created on first run)
│   └── properties.db          # SQLite database
│
├── logs/                       # Log files
│   └── scraper.log
│
└── exports/                    # CSV exports
    └── (your exported files)
```

---

## 🎯 Core Features

### 1. **Multi-Source Data Collection**
Scrapes from:
- County tax assessor websites (delinquent taxes)
- Foreclosure auction sites (Foreclosure.com, etc.)
- HUD government foreclosures
- Google Maps (geocoding & Street View)

### 2. **Intelligent Data Management**
- **SQLite database** with comprehensive schema
- **Automatic deduplication** (same address = same property)
- **Data validation** & cleaning
- **Change tracking** (property history)
- **Scoring system** (abandonment likelihood 0-10)

### 3. **Property Intelligence**
Each property includes:
- Full address & geocoded coordinates
- Tax delinquency status & amount
- Foreclosure status & auction dates
- Building details (beds, baths, sqft, year built)
- Abandonment score (calculated automatically)
- Street View images
- Historical data & changes

### 4. **Web Dashboard**
- Clean, modern UI
- Filter by state, county, city, score
- Real-time search
- Property statistics
- Export capabilities

### 5. **Flexible & Extensible**
- Modular scraper architecture
- Easy to add new data sources
- Configurable rate limiting
- API-ready (JSON endpoints)
- Export to CSV

---

## 🔧 How It Works

### Data Flow:
```
1. Scraper connects to data source
   ↓
2. Extracts raw property data
   ↓
3. Validates & cleans data
   ↓
4. Calculates abandonment score
   ↓
5. Geocodes address (Google Maps)
   ↓
6. Saves to database (deduplicated)
   ↓
7. Dashboard displays results
```

### Abandonment Score Algorithm:
```
Score = 0

IF tax delinquent for 2+ years: +5 points
IF tax delinquent for 1 year: +3 points
IF in foreclosure: +4 points
IF has code violations: +2 points
IF condemned: +5 points
IF no sale in 5+ years: +1 point
IF low assessed value (<$50k): +1 point

Maximum: 10 points
```

---

## 🚀 Usage Examples

### Basic Usage:
```bash
# First time setup
./setup.sh

# Run all scrapers
python main.py --all

# Run specific scraper
python main.py --scraper hud --state CA

# View stats
python main.py --stats

# Export data
python main.py --export properties.csv

# Start dashboard
python dashboard/app.py
```

### Programmatic Usage:
```python
from database.db_manager import DatabaseManager
from scrapers.hud import HUDScraper
import yaml

# Load config
with open('config.yml') as f:
    config = yaml.safe_load(f)

# Initialize
db = DatabaseManager('data/properties.db')
scraper = HUDScraper(config, db)

# Scrape
properties = scraper.run(state='CA')

# Query database
high_score = db.get_properties(min_score=7)
tax_delinquent = db.get_tax_delinquent_properties(min_years=2)
demolitions = db.get_demolition_scheduled(days_ahead=30)

# Export
db.export_to_csv('export.csv', filters={'state': 'CA'})
```

---

## 🎨 Customization Guide

### Adding a New Data Source:

1. **Create scraper file**: `scrapers/my_source.py`

```python
from scrapers.base_scraper import BaseScraper

class MySourceScraper(BaseScraper):
    def scrape(self, **kwargs):
        properties = []

        # Your scraping logic here
        url = "https://example.com/properties"
        response = self.make_request(url)
        soup = self.parse_html(response.text)

        for item in soup.select('.property'):
            prop_data = {
                'address': item.select_one('.address').text,
                'city': item.select_one('.city').text,
                'state': 'CA',
                'status': 'abandoned',
                # ... more fields
            }

            self.save_property(prop_data, 'MySource')
            properties.append(prop_data)

        return properties
```

2. **Register in main.py**:
```python
from scrapers.my_source import MySourceScraper

# In run_all_scrapers():
my_scraper = MySourceScraper(config, db)
my_scraper.run()
```

### Adding Database Fields:

1. **Update schema**: `database/schema.sql`
2. **Update model**: `database/models.py`
3. **Migrate database** (or start fresh)

### Customizing for Your County:

Most counties require custom scraping logic. See `GETTING_STARTED.md` for detailed instructions on:
- Finding county tax websites
- Inspecting HTML structure
- Writing custom parsers
- Testing scrapers

---

## 📊 Database Schema Highlights

### Main Tables:

**properties** - Core property data
- Address, geocoding, property details
- Tax & foreclosure status
- Abandonment scores
- Unique constraint on (address, city, state)

**data_sources** - Track where data came from
- Links properties to source scrapers
- Stores raw JSON data
- Timestamps for updates

**property_media** - Photos & Street View images
- Links to properties
- Supports multiple media types

**property_history** - Change tracking
- Records all field changes over time
- Audit trail for data

**scraper_logs** - Execution tracking
- Performance metrics
- Error tracking
- Run statistics

---

## 🔐 Legal & Ethical Considerations

### ✅ Legal:
- Scraping **public records** (tax data, foreclosures)
- Using **publicly available APIs**
- Respecting **robots.txt**
- Rate limiting to avoid overload

### ⚠️ Important:
- **Do NOT trespass** on properties
- **Respect website terms of service**
- **Don't overload servers** (use rate limits)
- **Verify data accuracy** before using
- **Personal use only** (not for commercial purposes without proper licensing)

### 🛡️ Privacy:
- Property ownership is **public record**
- Don't share private owner contact info
- Use data responsibly

---

## 💰 Cost Estimate

### Free:
- SQLite database
- Most scraping (public websites)
- HUD API
- Self-hosting on your computer

### Paid (Optional):
- **Google Maps API**: $5-20/month (first $200/month free)
- **News API**: Free tier available (100 req/day)
- **VPS Hosting**: $5-10/month (if you want 24/7 operation)
- **Proxies**: $10-50/month (if you need high volume)

**Typical monthly cost**: $0-30 depending on usage

---

## 🔮 Future Enhancements

Ideas for expansion:

### Data Sources:
- Zillow/Realtor.com property history
- Code violation databases
- Demolition permit tracking
- News article scraping
- Satellite imagery analysis (AI)
- Building permit records

### Features:
- Email alerts for new properties
- Route planning (visit multiple properties)
- Mobile app
- Property photos upload
- User notes & ratings
- Social features (share discoveries)

### Technical:
- PostgreSQL support (better concurrency)
- Redis caching
- Celery task queue
- Docker deployment
- API authentication
- Scheduled cron jobs

---

## 🐛 Known Limitations

1. **Website-Dependent**: Scrapers break when sites change HTML
2. **County-Specific**: Tax assessor requires custom code per county
3. **Rate Limits**: Some sites limit requests per day
4. **Data Quality**: Not all sources have complete information
5. **API Costs**: Google Maps charges after free tier
6. **Legal Gray Areas**: Some sites prohibit scraping in ToS

---

## 📚 Key Technologies Used

- **Python 3.8+**: Core language
- **SQLAlchemy**: ORM for database
- **BeautifulSoup4**: HTML parsing
- **Requests**: HTTP client
- **Flask**: Web framework
- **Google Maps API**: Geocoding
- **Loguru**: Logging
- **PyYAML**: Configuration

---

## 🎓 Learning Resources

To understand the code better:

1. **Web Scraping**:
   - BeautifulSoup documentation
   - Scrapy tutorial
   - Understanding HTML/CSS selectors

2. **Databases**:
   - SQLAlchemy ORM basics
   - SQL fundamentals

3. **APIs**:
   - Google Maps API docs
   - RESTful API design

4. **Python**:
   - Object-oriented programming
   - Context managers (`with` statements)
   - Async programming (future enhancement)

---

## ✅ What You Can Do NOW

1. **Start scraping**: HUD and foreclosure sites work out-of-the-box
2. **View your data**: Dashboard shows everything
3. **Export**: Get CSV files for spreadsheet analysis
4. **Customize**: Add your specific counties
5. **Extend**: Add new data sources
6. **Automate**: Set up cron jobs for regular updates

---

## 🙋 Getting Help

If you get stuck:

1. Check `GETTING_STARTED.md` for common issues
2. Review code comments in each file
3. Enable debug logging in `config.yml`
4. Inspect website HTML when scrapers fail
5. Test with small datasets first

---

## 🏁 Final Notes

This is a **professional-grade system** that would cost thousands to develop commercially. It's designed to be:

- **Maintainable**: Clean, documented code
- **Extensible**: Easy to add features
- **Robust**: Error handling, logging, retries
- **Scalable**: Can handle thousands of properties
- **User-friendly**: Web dashboard, CLI tools

The scrapers are **templates** - you'll need to customize them for your specific counties and use cases. But the framework is solid and ready to go.

**Happy property hunting!** 🏚️🔍
