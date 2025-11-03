"""
HUD (Housing and Urban Development) Foreclosure Listings Scraper

HUD properties are foreclosed homes owned by the government
Website: https://www.hudhomestore.gov/
"""
from typing import List, Dict, Any
from loguru import logger
from scrapers.base_scraper import BaseScraper
from utils.validators import validate_property_data


class HUDScraper(BaseScraper):
    """Scrape HUD foreclosure listings"""

    def __init__(self, config: Dict[str, Any], db_manager):
        super().__init__(config, db_manager)
        self.base_url = "https://www.hudhomestore.gov"
        self.api_url = "https://www.hudhomestore.gov/api"

    def scrape(self, state: str = None, city: str = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Scrape HUD foreclosure listings

        Args:
            state: Optional state filter
            city: Optional city filter

        Returns:
            List of property dictionaries
        """
        logger.info(f"Scraping HUD listings for {state or 'all states'}")

        properties = []

        # HUD has an API we can use
        # The actual API endpoints may require inspection of their website

        if state:
            properties.extend(self._scrape_state(state, city))
        else:
            # Scrape all states from config
            for location in self.config.get('target_locations', []):
                state_code = location.get('state')
                if state_code:
                    properties.extend(self._scrape_state(state_code))

        # Save properties
        for prop_data in properties:
            self.save_property(prop_data, source_name='HUD')

        return properties

    def _scrape_state(self, state: str, city: str = None) -> List[Dict[str, Any]]:
        """
        Scrape HUD listings for a specific state

        Args:
            state: State code
            city: Optional city filter

        Returns:
            List of properties
        """
        properties = []

        logger.info(f"Searching HUD listings in {state}")

        # HUD's search typically works through their API
        # The exact API structure requires reverse engineering their website

        # Example API call structure (needs verification):
        search_params = {
            'state': state,
            'page': 1,
            'pageSize': 100
        }

        if city:
            search_params['city'] = city

        # Try to fetch listings
        # NOTE: This is a template - actual API may differ
        url = f"{self.api_url}/properties/search"

        page = 1
        while True:
            search_params['page'] = page

            response = self.make_request(
                url,
                method='GET',
                params=search_params
            )

            if not response:
                break

            try:
                data = response.json()

                # Parse properties from response
                listings = data.get('properties', [])

                if not listings:
                    break

                for listing in listings:
                    prop_data = self._parse_hud_listing(listing)
                    if prop_data:
                        properties.append(prop_data)

                # Check if there are more pages
                if not data.get('hasMore', False):
                    break

                page += 1

            except Exception as e:
                logger.error(f"Error parsing HUD response: {e}")
                break

        logger.info(f"Found {len(properties)} HUD properties in {state}")
        return properties

    def _parse_hud_listing(self, listing: Dict) -> Dict[str, Any]:
        """
        Parse a HUD listing into our property format

        Args:
            listing: Raw HUD listing data

        Returns:
            Property dictionary
        """
        try:
            # Map HUD fields to our schema
            # Field names are examples - actual API may differ
            prop_data = {
                'address': listing.get('streetAddress'),
                'city': listing.get('city'),
                'state': listing.get('state'),
                'zip_code': listing.get('zipCode'),

                'property_type': 'Residential',
                'building_type': listing.get('propertyType', 'House'),

                'num_bedrooms': listing.get('bedrooms'),
                'num_bathrooms': listing.get('bathrooms'),
                'square_footage': listing.get('squareFeet'),

                'current_assessed_value': listing.get('listPrice'),

                'status': 'foreclosed',
                'foreclosure_status': 'HUD-owned',

                # HUD specific
                'auction_url': f"{self.base_url}/property/{listing.get('caseNumber')}",
                'auction_date': listing.get('bidOpenDate'),
            }

            # Validate and clean
            validated = validate_property_data(prop_data)

            return validated

        except Exception as e:
            logger.error(f"Error parsing HUD listing: {e}")
            return None

    def scrape_from_html(self, state: str) -> List[Dict[str, Any]]:
        """
        Alternative: Scrape from HTML if API doesn't work

        Args:
            state: State code

        Returns:
            List of properties
        """
        properties = []

        # Build search URL
        search_url = f"{self.base_url}/Home/Results.aspx?state={state}"

        response = self.make_request(search_url)
        if not response:
            return properties

        soup = self.parse_html(response.text)

        # Find property listings
        # CSS selectors need to match actual HTML structure
        listings = soup.select('.property-listing')  # Example selector

        for listing in listings:
            try:
                prop_data = {}

                # Extract address
                address_elem = listing.select_one('.property-address')
                if address_elem:
                    prop_data['address'] = address_elem.text.strip()

                # Extract city, state, zip
                location_elem = listing.select_one('.property-location')
                if location_elem:
                    location = location_elem.text.strip()
                    # Parse "City, ST ZIP"
                    parts = location.split(',')
                    if len(parts) >= 2:
                        prop_data['city'] = parts[0].strip()
                        state_zip = parts[1].strip().split()
                        if len(state_zip) >= 2:
                            prop_data['state'] = state_zip[0]
                            prop_data['zip_code'] = state_zip[1]

                # Extract price
                price_elem = listing.select_one('.property-price')
                if price_elem:
                    import re
                    price_text = price_elem.text.strip()
                    price_match = re.search(r'[\d,]+', price_text)
                    if price_match:
                        prop_data['current_assessed_value'] = float(
                            price_match.group().replace(',', '')
                        )

                # Extract bedrooms/bathrooms
                details_elem = listing.select_one('.property-details')
                if details_elem:
                    details_text = details_elem.text
                    # Parse "3 BD | 2 BA" format
                    import re
                    bed_match = re.search(r'(\d+)\s*BD', details_text)
                    bath_match = re.search(r'([\d.]+)\s*BA', details_text)

                    if bed_match:
                        prop_data['num_bedrooms'] = int(bed_match.group(1))
                    if bath_match:
                        prop_data['num_bathrooms'] = float(bath_match.group(1))

                # Set status
                prop_data['status'] = 'foreclosed'
                prop_data['foreclosure_status'] = 'HUD-owned'
                prop_data['property_type'] = 'Residential'

                # Validate
                if prop_data.get('address'):
                    validated = validate_property_data(prop_data)
                    properties.append(validated)

            except Exception as e:
                logger.error(f"Error parsing HUD listing: {e}")
                continue

        return properties


# Usage example:
"""
from database.db_manager import DatabaseManager
from scrapers.hud import HUDScraper
import yaml

# Load config
with open('config.yml') as f:
    config = yaml.safe_load(f)

# Initialize
db = DatabaseManager(config['database']['path'])
scraper = HUDScraper(config, db)

# Scrape California
properties = scraper.run(state='CA')

print(f"Found {len(properties)} HUD properties")
"""
