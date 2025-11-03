"""
Geocoding and address standardization utilities
"""
import time
from typing import Optional, Dict, Tuple
from loguru import logger
import googlemaps
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


class Geocoder:
    """Handle geocoding operations"""

    def __init__(self, provider: str = 'google', api_key: Optional[str] = None):
        """
        Initialize geocoder

        Args:
            provider: 'google' or 'nominatim'
            api_key: API key for Google Maps (required for Google)
        """
        self.provider = provider
        self.cache = {}  # Simple in-memory cache

        if provider == 'google':
            if not api_key:
                raise ValueError("Google Maps API key required")
            self.client = googlemaps.Client(key=api_key)
        elif provider == 'nominatim':
            self.client = Nominatim(user_agent="urbex_property_scraper")
        else:
            raise ValueError(f"Unknown provider: {provider}")

        logger.info(f"Initialized geocoder: {provider}")

    def geocode(self, address: str) -> Optional[Dict[str, any]]:
        """
        Geocode an address to get coordinates and formatted address

        Args:
            address: Address string

        Returns:
            Dictionary with lat, lng, and formatted_address or None
        """
        # Check cache
        if address in self.cache:
            logger.debug(f"Cache hit for: {address}")
            return self.cache[address]

        try:
            if self.provider == 'google':
                result = self._geocode_google(address)
            else:
                result = self._geocode_nominatim(address)

            # Cache result
            if result:
                self.cache[address] = result

            return result

        except Exception as e:
            logger.error(f"Geocoding failed for '{address}': {e}")
            return None

    def _geocode_google(self, address: str) -> Optional[Dict[str, any]]:
        """Geocode using Google Maps API"""
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
            logger.error(f"Google geocoding error: {e}")

        return None

    def _geocode_nominatim(self, address: str) -> Optional[Dict[str, any]]:
        """Geocode using Nominatim (OpenStreetMap)"""
        try:
            time.sleep(1)  # Rate limiting for Nominatim
            location = self.client.geocode(address)

            if location:
                return {
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'formatted_address': location.address
                }

        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.error(f"Nominatim geocoding error: {e}")

        return None

    def reverse_geocode(self, lat: float, lng: float) -> Optional[str]:
        """
        Reverse geocode coordinates to address

        Args:
            lat: Latitude
            lng: Longitude

        Returns:
            Formatted address or None
        """
        try:
            if self.provider == 'google':
                results = self.client.reverse_geocode((lat, lng))
                if results:
                    return results[0]['formatted_address']

            else:  # nominatim
                time.sleep(1)
                location = self.client.reverse((lat, lng))
                if location:
                    return location.address

        except Exception as e:
            logger.error(f"Reverse geocoding failed: {e}")

        return None

    def validate_coordinates(self, lat: float, lng: float) -> bool:
        """
        Validate if coordinates are within valid ranges

        Args:
            lat: Latitude
            lng: Longitude

        Returns:
            True if valid
        """
        return -90 <= lat <= 90 and -180 <= lng <= 180


def parse_address(address_string: str) -> Dict[str, Optional[str]]:
    """
    Parse an address string into components

    Args:
        address_string: Full address string

    Returns:
        Dictionary with address, city, state, zip_code
    """
    import re

    # Simple regex-based parsing (not perfect but works for most cases)
    result = {
        'address': None,
        'city': None,
        'state': None,
        'zip_code': None
    }

    # Extract ZIP code
    zip_match = re.search(r'\b\d{5}(?:-\d{4})?\b', address_string)
    if zip_match:
        result['zip_code'] = zip_match.group()
        address_string = address_string.replace(result['zip_code'], '').strip()

    # Extract state (2-letter abbreviation)
    state_match = re.search(r'\b[A-Z]{2}\b', address_string)
    if state_match:
        result['state'] = state_match.group()
        address_string = address_string.replace(result['state'], '').strip()

    # Split by comma
    parts = [p.strip() for p in address_string.split(',')]

    if len(parts) >= 2:
        result['address'] = parts[0]
        result['city'] = parts[1] if len(parts) > 1 else None
    elif len(parts) == 1:
        result['address'] = parts[0]

    return result


def standardize_state(state: str) -> Optional[str]:
    """
    Standardize state name to 2-letter abbreviation

    Args:
        state: State name or abbreviation

    Returns:
        2-letter state code or None
    """
    state_mapping = {
        'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
        'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
        'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
        'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
        'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
        'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
        'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
        'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
        'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
        'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
        'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
        'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
        'wisconsin': 'WI', 'wyoming': 'WY'
    }

    state_lower = state.lower().strip()

    # Check if already an abbreviation
    if len(state) == 2 and state.isupper():
        return state

    # Look up in mapping
    return state_mapping.get(state_lower)


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate distance between two coordinates in miles using Haversine formula

    Args:
        lat1, lng1: First coordinate
        lat2, lng2: Second coordinate

    Returns:
        Distance in miles
    """
    import math

    # Convert to radians
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])

    # Haversine formula
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))

    # Radius of earth in miles
    radius = 3959

    return c * radius
