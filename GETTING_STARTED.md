# Getting Started with UrbEx Property Scraper

## Quick Start Guide

### 1. Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Copy configuration template
cp config.example.yml config.yml
```

### 2. Configuration

Edit `config.yml` and customize:

#### Required Settings:
- **target_locations**: Add your states and counties
- **api_keys.google_maps**: Add your Google Maps API key (for geocoding)

#### Optional but Recommended:
- **api_keys.news_api**: For news article scraping
- **scrapers.rate_limits**: Adjust if you get rate limited

Example minimal config:
```yaml
target_locations:
  - state: CA
    counties:
      - Los Angeles
      - Orange

api_keys:
  google_maps: YOUR_GOOGLE_MAPS_API_KEY
```

### 3. Run Your First Scrape

```bash
# Check database stats (should be empty initially)
python main.py --stats

# Run all scrapers
python main.py --all

# Or run specific scraper for a location
python main.py --scraper hud --state CA
```

### 4. View Results

```bash
# Start the web dashboard
python dashboard/app.py

# Open browser to: http://127.0.0.1:5000
```

### 5. Export Data

```bash
# Export all properties to CSV
python main.py --export data.csv

# Export only California properties
python main.py --export ca_properties.csv --state CA
```

---

## Understanding the Scrapers

### Tax Assessor Scraper
- **Source**: County tax assessor websites
- **Finds**: Properties with delinquent taxes
- **Status**: Template - requires customization per county
- **How to customize**: See `scrapers/tax_assessor.py`

Each county has different website structures. You'll need to:
1. Find your county's tax assessor website
2. Locate the delinquent tax search page
3. Inspect the HTML structure
4. Create custom parsing logic or use the generic scraper

### HUD Scraper
- **Source**: https://www.hudhomestore.gov/
- **Finds**: Government-owned foreclosed homes
- **Status**: Template with API structure
- **Note**: HUD's API may require reverse engineering

### Foreclosure Scraper
- **Source**: Foreclosure.com, RealtyStore.com, etc.
- **Finds**: Pre-foreclosure, auction, bank-owned properties
- **Status**: Template - may need updates as sites change

### Google Maps Scraper
- **Source**: Google Maps API
- **Purpose**: Geocode addresses, get Street View images
- **Requires**: Valid Google Maps API key
- **Cost**: ~$5 per 1000 geocoding requests

---

## API Keys Setup

### Google Maps API
1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable these APIs:
   - Geocoding API
   - Maps JavaScript API
   - Street View Static API
4. Create credentials (API key)
5. Add to `config.yml`

**Cost**: Google gives $200/month free credit
- Geocoding: ~$5 per 1000 requests
- Street View: ~$7 per 1000 requests

### News API (optional)
1. Go to https://newsapi.org/
2. Sign up for free account (100 requests/day)
3. Get API key
4. Add to `config.yml`

---

## Customizing for Your County

Most counties require custom scraper logic. Here's how:

### Example: Adding Cook County (Chicago)

1. Research the county website:
   - Find: https://www.cookcountyassessor.com/
   - Locate delinquent tax search
   - Inspect HTML structure

2. Create custom scraper method in `scrapers/tax_assessor.py`:

```python
def _scrape_cook_county(self) -> List[Dict[str, Any]]:
    """Scrape Cook County tax assessor"""
    properties = []

    url = "https://www.cookcountyassessor.com/tax-delinquent"
    response = self.make_request(url)
    soup = self.parse_html(response.text)

    # Parse property listings
    for row in soup.select('table.properties tr'):
        prop_data = {
            'address': row.select_one('td.address').text,
            'tax_delinquent': True,
            # ... extract other fields
        }

        validated = validate_property_data(prop_data)
        properties.append(validated)

    return properties
```

3. Add to main scrape method:
```python
elif state == 'IL' and county.lower() == 'cook':
    properties.extend(self._scrape_cook_county())
```

---

## Tips for Success

### 1. Start Small
- Begin with one county you know well
- Test scrapers frequently
- Verify data accuracy before scaling up

### 2. Respect Websites
- Use rate limiting (default: 10 req/min)
- Don't scrape during peak hours
- Follow robots.txt rules
- Use reasonable timeouts

### 3. Data Quality
- Always validate addresses with geocoding
- Cross-reference multiple sources
- Manually verify a sample of properties
- Update data regularly (monthly recommended)

### 4. Legal Considerations
- Only scrape public records
- Don't trespass on properties
- Respect property owner privacy
- Use data for research only

### 5. Costs to Consider
- Google Maps API: $5-20/month (depending on usage)
- VPS hosting (optional): $5-10/month
- Proxy services (optional): $10-50/month

---

## Troubleshooting

### "No scraper implemented for [county]"
- The scraper template doesn't have your county
- You need to add custom scraping logic
- See "Customizing for Your County" above

### "Google Maps API key not configured"
- Get API key from Google Cloud Console
- Add to config.yml under api_keys.google_maps
- Ensure Geocoding API is enabled

### "Rate limit exceeded"
- Increase delay in config.yml
- Use proxies for high-volume scraping
- Consider API-based sources (HUD, Zillow)

### Empty results
- Check if website structure changed
- Verify your filters aren't too restrictive
- Enable debug logging to see errors

### Database locked errors
- Close any open connections
- Only run one scraper at a time
- Use PostgreSQL for concurrent access

---

## Next Steps

1. **Enrich data**: Add more fields (photos, news articles)
2. **Automate**: Set up cron jobs for regular scraping
3. **Analyze**: Calculate trends, create heatmaps
4. **Integrate**: Connect with mapping tools (Google Maps, Mapbox)
5. **Scale**: Deploy to cloud, use PostgreSQL, add caching

---

## Need Help?

- Check the code comments in each scraper
- Review example implementations
- Inspect website HTML to understand structure
- Test with small datasets first

Remember: Most property data is public record, but always verify legality in your jurisdiction!
