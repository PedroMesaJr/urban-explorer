"""
Data validation utilities
"""
import re
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger


def validate_address(address: str) -> bool:
    """
    Validate if address looks reasonable

    Args:
        address: Address string

    Returns:
        True if valid
    """
    if not address or len(address) < 5:
        return False

    # Should contain at least a number and some letters
    has_number = bool(re.search(r'\d', address))
    has_letters = bool(re.search(r'[a-zA-Z]', address))

    return has_number and has_letters


def validate_zip_code(zip_code: str) -> bool:
    """
    Validate US ZIP code

    Args:
        zip_code: ZIP code string

    Returns:
        True if valid
    """
    if not zip_code:
        return False

    # US ZIP: 5 digits or 5+4 format
    pattern = r'^\d{5}(-\d{4})?$'
    return bool(re.match(pattern, zip_code))


def validate_state(state: str) -> bool:
    """
    Validate US state code

    Args:
        state: 2-letter state code

    Returns:
        True if valid
    """
    valid_states = {
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
    }

    return state and state.upper() in valid_states


def validate_coordinates(lat: float, lng: float) -> bool:
    """
    Validate geographic coordinates

    Args:
        lat: Latitude
        lng: Longitude

    Returns:
        True if valid
    """
    try:
        lat = float(lat)
        lng = float(lng)
        return -90 <= lat <= 90 and -180 <= lng <= 180
    except (TypeError, ValueError):
        return False


def validate_price(price: Any) -> Optional[float]:
    """
    Validate and parse price value

    Args:
        price: Price value (string, int, or float)

    Returns:
        Float price or None if invalid
    """
    if price is None:
        return None

    try:
        # Remove currency symbols and commas
        if isinstance(price, str):
            price = re.sub(r'[$,]', '', price)

        price = float(price)

        # Sanity check (between $0 and $100M)
        if 0 <= price <= 100_000_000:
            return price

    except (ValueError, TypeError):
        pass

    return None


def validate_year(year: Any) -> Optional[int]:
    """
    Validate year value

    Args:
        year: Year value

    Returns:
        Integer year or None if invalid
    """
    try:
        year = int(year)

        # Reasonable range for building years
        current_year = datetime.now().year
        if 1700 <= year <= current_year:
            return year

    except (ValueError, TypeError):
        pass

    return None


def validate_square_footage(sqft: Any) -> Optional[int]:
    """
    Validate square footage

    Args:
        sqft: Square footage value

    Returns:
        Integer square footage or None if invalid
    """
    try:
        sqft = int(float(sqft))

        # Reasonable range (10 sqft to 1 million sqft)
        if 10 <= sqft <= 1_000_000:
            return sqft

    except (ValueError, TypeError):
        pass

    return None


def validate_date(date_str: str, formats: list = None) -> Optional[datetime]:
    """
    Validate and parse date string

    Args:
        date_str: Date string
        formats: List of date format strings to try

    Returns:
        datetime object or None if invalid
    """
    if not date_str:
        return None

    if formats is None:
        formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%m-%d-%Y',
            '%Y/%m/%d',
            '%B %d, %Y',
            '%b %d, %Y',
            '%d %B %Y',
            '%d %b %Y',
        ]

    for fmt in formats:
        try:
            return datetime.strptime(str(date_str).strip(), fmt)
        except (ValueError, AttributeError):
            continue

    logger.warning(f"Could not parse date: {date_str}")
    return None


def validate_phone(phone: str) -> Optional[str]:
    """
    Validate and format phone number

    Args:
        phone: Phone number string

    Returns:
        Formatted phone number or None if invalid
    """
    if not phone:
        return None

    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)

    # US phone: 10 digits
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"

    return None


def clean_text(text: str) -> str:
    """
    Clean and normalize text

    Args:
        text: Input text

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove extra whitespace
    text = ' '.join(text.split())

    # Remove special characters (keep alphanumeric, spaces, and common punctuation)
    text = re.sub(r'[^\w\s.,;:!?\-()\'\"]+', '', text)

    return text.strip()


def validate_property_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean property data dictionary

    Args:
        data: Raw property data

    Returns:
        Validated and cleaned property data
    """
    cleaned = {}

    # Required fields
    if 'address' in data:
        cleaned['address'] = clean_text(data['address'])
        if not validate_address(cleaned['address']):
            logger.warning(f"Invalid address: {cleaned['address']}")

    if 'state' in data:
        cleaned['state'] = data['state'].upper() if data['state'] else None
        if cleaned['state'] and not validate_state(cleaned['state']):
            logger.warning(f"Invalid state: {cleaned['state']}")

    # Optional fields with validation
    fields_to_clean = ['city', 'county', 'owner_name', 'property_type', 'building_type']
    for field in fields_to_clean:
        if field in data and data[field]:
            cleaned[field] = clean_text(data[field])

    # Zip code
    if 'zip_code' in data and data['zip_code']:
        cleaned['zip_code'] = str(data['zip_code']).strip()
        if not validate_zip_code(cleaned['zip_code']):
            logger.warning(f"Invalid ZIP code: {cleaned['zip_code']}")

    # Coordinates
    if 'latitude' in data and 'longitude' in data:
        if validate_coordinates(data['latitude'], data['longitude']):
            cleaned['latitude'] = float(data['latitude'])
            cleaned['longitude'] = float(data['longitude'])

    # Prices
    price_fields = ['last_sale_price', 'current_assessed_value', 'foreclosure_amount', 'tax_delinquency_amount']
    for field in price_fields:
        if field in data:
            validated_price = validate_price(data[field])
            if validated_price is not None:
                cleaned[field] = validated_price

    # Year
    if 'year_built' in data:
        validated_year = validate_year(data['year_built'])
        if validated_year:
            cleaned['year_built'] = validated_year

    # Square footage
    for field in ['square_footage', 'lot_size_sqft']:
        if field in data:
            validated_sqft = validate_square_footage(data[field])
            if validated_sqft:
                cleaned[field] = validated_sqft

    # Dates
    date_fields = ['last_sale_date', 'abandonment_date', 'foreclosure_date', 'auction_date', 'demolition_date']
    for field in date_fields:
        if field in data and data[field]:
            validated_date = validate_date(data[field])
            if validated_date:
                cleaned[field] = validated_date.date()

    # Boolean fields
    bool_fields = ['tax_delinquent', 'has_security', 'demolition_scheduled', 'has_violations', 'condemned']
    for field in bool_fields:
        if field in data:
            cleaned[field] = bool(data[field])

    # Integer fields
    int_fields = ['tax_delinquency_years', 'violation_count', 'num_bedrooms', 'num_stories']
    for field in int_fields:
        if field in data and data[field] is not None:
            try:
                cleaned[field] = int(data[field])
            except (ValueError, TypeError):
                pass

    # Float fields
    if 'num_bathrooms' in data and data['num_bathrooms'] is not None:
        try:
            cleaned['num_bathrooms'] = float(data['num_bathrooms'])
        except (ValueError, TypeError):
            pass

    # Pass through other fields
    passthrough_fields = [
        'status', 'foreclosure_status', 'structural_condition', 'hazards',
        'security_type', 'demolition_permit_number', 'tax_id',
        'formatted_address', 'thumbnail_url', 'street_view_url', 'auction_url'
    ]
    for field in passthrough_fields:
        if field in data and data[field]:
            cleaned[field] = data[field]

    return cleaned
