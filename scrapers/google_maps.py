"""
Google Maps and Street View integration

Enriches property data with:
- Geocoded coordinates
- Formatted addresses
- Street View images
- Nearby amenities
"""
from typing import List, Dict, Any, Optional
from loguru import logger
from scrapers.base_scraper import BaseScraper
import googlemaps
from datetime import datetime
import os


class GoogleMapsScraper(BaseScraper):
    """Enrich properties with Google Maps data"""

    def __init__(self, config: Dict[str, Any], db_manager):
        super().__init__(config, db_manager)

        api_key = config.get('api_keys', {}).get('google_maps')
        if not api_key or api_key == 'YOUR_GOOGLE_MAPS_API_KEY_HERE':
            logger.warning("Google Maps API key not configured")
            self.client = None
        else:
            self.client = googlemaps.Client(key=api_key)
            logger.info("Google Maps client initialized")

    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Enrich existing properties with Google Maps data

        Returns:
            List of updated properties
        """
        if not self.client:
            logger.error("Google Maps client not initialized - check API key")
            return []

        logger.info("Enriching properties with Google Maps data...")

        # Get properties that need geocoding
        with self.db.session_scope() as session:
            from database.models import Property

            # Find properties without coordinates
            properties = session.query(Property).filter(
                Property.latitude == None
            ).limit(100).all()  # Limit to avoid API costs

            updated_properties = []

            for prop in properties:
                try:
                    # Build full address
                    full_address = self._build_full_address(prop)

                    # Geocode
                    geocode_data = self._geocode_address(full_address)

                    if geocode_data:
                        prop.latitude = geocode_data['latitude']
                        prop.longitude = geocode_data['longitude']
                        prop.formatted_address = geocode_data['formatted_address']

                        # Get Street View image
                        if geocode_data['latitude'] and geocode_data['longitude']:
                            street_view_url = self._get_street_view_url(
                                geocode_data['latitude'],
                                geocode_data['longitude']
                            )
                            prop.street_view_url = street_view_url

                        self.stats['updated'] += 1
                        updated_properties.append(prop.to_dict())
                        logger.debug(f"Enriched: {prop.address}")

                except Exception as e:
                    logger.error(f"Error enriching property {prop.id}: {e}")
                    self.stats['errors'] += 1

            session.commit()

        logger.info(f"Enriched {len(updated_properties)} properties with Google Maps data")
        return updated_properties

    def _build_full_address(self, property_obj) -> str:
        """Build full address string"""
        parts = []

        if property_obj.address:
            parts.append(property_obj.address)
        if property_obj.city:
            parts.append(property_obj.city)
        if property_obj.state:
            parts.append(property_obj.state)
        if property_obj.zip_code:
            parts.append(property_obj.zip_code)

        return ', '.join(parts)

    def _geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Geocode an address

        Args:
            address: Address string

        Returns:
            Dictionary with latitude, longitude, formatted_address
        """
        try:
            results = self.client.geocode(address)

            if results:
                location = results[0]['geometry']['location']
                return {
                    'latitude': location['lat'],
                    'longitude': location['lng'],
                    'formatted_address': results[0]['formatted_address']
                }

        except Exception as e:
            logger.error(f"Geocoding failed for '{address}': {e}")

        return None

    def _get_street_view_url(self, lat: float, lng: float, size: str = "600x400") -> str:
        """
        Generate Street View static image URL

        Args:
            lat: Latitude
            lng: Longitude
            size: Image size (e.g., "600x400")

        Returns:
            Street View image URL
        """
        api_key = self.config.get('api_keys', {}).get('google_maps', '')

        url = (
            f"https://maps.googleapis.com/maps/api/streetview"
            f"?size={size}"
            f"&location={lat},{lng}"
            f"&key={api_key}"
        )

        return url

    def download_street_view_image(self, lat: float, lng: float,
                                   output_path: str) -> bool:
        """
        Download Street View image

        Args:
            lat: Latitude
            lng: Longitude
            output_path: Path to save image

        Returns:
            True if successful
        """
        try:
            url = self._get_street_view_url(lat, lng, size="1200x800")

            response = self.make_request(url)
            if response and response.status_code == 200:
                # Check if image is valid (not "no image available")
                if len(response.content) > 1000:  # Basic check
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)

                    with open(output_path, 'wb') as f:
                        f.write(response.content)

                    logger.debug(f"Downloaded Street View image: {output_path}")
                    return True

        except Exception as e:
            logger.error(f"Failed to download Street View image: {e}")

        return False

    def get_nearby_places(self, lat: float, lng: float,
                         place_type: str = 'point_of_interest',
                         radius: int = 500) -> List[Dict]:
        """
        Get nearby places

        Args:
            lat: Latitude
            lng: Longitude
            place_type: Type of place to search
            radius: Search radius in meters

        Returns:
            List of nearby places
        """
        if not self.client:
            return []

        try:
            results = self.client.places_nearby(
                location=(lat, lng),
                radius=radius,
                type=place_type
            )

            return results.get('results', [])

        except Exception as e:
            logger.error(f"Error fetching nearby places: {e}")
            return []


# Usage:
"""
scraper = GoogleMapsScraper(config, db)

# Enrich all properties without coordinates
scraper.run()

# Or geocode a specific address
geocode_data = scraper._geocode_address("123 Main St, Los Angeles, CA")
print(geocode_data)
"""
