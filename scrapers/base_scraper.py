"""
Base scraper class with common functionality
"""
import time
import random
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from loguru import logger
from datetime import datetime


class BaseScraper(ABC):
    """Base class for all scrapers"""

    def __init__(self, config: Dict[str, Any], db_manager):
        """
        Initialize scraper

        Args:
            config: Configuration dictionary
            db_manager: DatabaseManager instance
        """
        self.config = config
        self.db = db_manager
        self.scraper_name = self.__class__.__name__
        self.session = requests.Session()

        # Get scraper-specific settings
        scraper_config = config.get('scrapers', {})
        self.rate_limit = scraper_config.get('rate_limits', {}).get('default', 10)
        self.timeout = scraper_config.get('timeout', 30)
        self.max_retries = scraper_config.get('max_retries', 3)
        self.retry_delay = scraper_config.get('retry_delay', 5)

        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        ]

        # Statistics
        self.stats = {
            'found': 0,
            'added': 0,
            'updated': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }

        logger.info(f"Initialized {self.scraper_name}")

    def get_random_user_agent(self) -> str:
        """Get a random user agent"""
        return random.choice(self.user_agents)

    def make_request(
        self,
        url: str,
        method: str = 'GET',
        params: Dict = None,
        data: Dict = None,
        headers: Dict = None,
        json_data: Dict = None
    ) -> Optional[requests.Response]:
        """
        Make HTTP request with retry logic and rate limiting

        Args:
            url: URL to request
            method: HTTP method
            params: Query parameters
            data: Form data
            headers: Custom headers
            json_data: JSON payload

        Returns:
            Response object or None on failure
        """
        if headers is None:
            headers = {}

        # Add user agent if not provided
        if 'User-Agent' not in headers:
            headers['User-Agent'] = self.get_random_user_agent()

        for attempt in range(self.max_retries):
            try:
                # Rate limiting
                time.sleep(60 / self.rate_limit)

                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    json=json_data,
                    headers=headers,
                    timeout=self.timeout
                )

                response.raise_for_status()
                return response

            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}"
                )

                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
                    self.stats['errors'] += 1
                    return None

        return None

    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content"""
        return BeautifulSoup(html, 'lxml')

    def calculate_abandonment_score(self, property_data: Dict[str, Any]) -> int:
        """
        Calculate abandonment likelihood score (0-10)

        Factors:
        - Tax delinquency: +3 points (1 year), +5 points (2+ years)
        - Foreclosure status: +4 points
        - Code violations: +2 points
        - Condemned: +5 points
        - No recent sale: +1 point (5+ years)
        - Low assessed value: +1 point
        """
        score = 0

        # Tax delinquency
        if property_data.get('tax_delinquent'):
            years = property_data.get('tax_delinquency_years', 0)
            if years >= 2:
                score += 5
            elif years >= 1:
                score += 3

        # Foreclosure
        if property_data.get('foreclosure_status'):
            score += 4

        # Violations
        if property_data.get('has_violations'):
            score += 2

        # Condemned
        if property_data.get('condemned'):
            score += 5

        # Old last sale
        if property_data.get('last_sale_date'):
            try:
                from datetime import datetime
                years_since_sale = (
                    datetime.now() - datetime.fromisoformat(str(property_data['last_sale_date']))
                ).days / 365
                if years_since_sale >= 5:
                    score += 1
            except:
                pass

        # Low value (possible abandonment)
        if property_data.get('current_assessed_value', 0) < 50000:
            score += 1

        return min(score, 10)  # Cap at 10

    def save_property(self, property_data: Dict[str, Any], source_name: str = None):
        """
        Save property to database

        Args:
            property_data: Property information
            source_name: Name of the data source
        """
        if source_name is None:
            source_name = self.scraper_name

        try:
            # Calculate abandonment score
            if 'abandonment_score' not in property_data:
                property_data['abandonment_score'] = self.calculate_abandonment_score(
                    property_data
                )

            # Save to database
            property_obj = self.db.add_or_update_property(property_data, source_name)

            if property_obj:
                self.stats['found'] += 1
                # Check if it was newly added or updated (simple heuristic)
                if property_obj.discovery_date.date() == datetime.now().date():
                    self.stats['added'] += 1
                else:
                    self.stats['updated'] += 1

                logger.debug(f"Saved property: {property_data.get('address')}")

        except Exception as e:
            logger.error(f"Failed to save property: {e}")
            self.stats['errors'] += 1

    @abstractmethod
    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Main scraping method - must be implemented by subclasses

        Returns:
            List of property dictionaries
        """
        pass

    def run(self, **kwargs):
        """
        Execute the scraper with logging

        Args:
            **kwargs: Arguments passed to scrape method
        """
        self.stats['start_time'] = datetime.now()
        logger.info(f"Starting {self.scraper_name}...")

        try:
            # Run the scraper
            results = self.scrape(**kwargs)

            self.stats['end_time'] = datetime.now()
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()

            # Log results
            self.db.log_scraper_run(
                scraper_name=self.scraper_name,
                status='success' if self.stats['errors'] == 0 else 'partial',
                found=self.stats['found'],
                added=self.stats['added'],
                updated=self.stats['updated'],
                errors=None if self.stats['errors'] == 0 else f"{self.stats['errors']} errors",
                duration=duration
            )

            logger.info(
                f"{self.scraper_name} completed: "
                f"Found={self.stats['found']}, "
                f"Added={self.stats['added']}, "
                f"Updated={self.stats['updated']}, "
                f"Errors={self.stats['errors']}, "
                f"Duration={duration:.1f}s"
            )

            return results

        except Exception as e:
            logger.error(f"{self.scraper_name} failed: {e}", exc_info=True)
            self.stats['end_time'] = datetime.now()
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()

            self.db.log_scraper_run(
                scraper_name=self.scraper_name,
                status='failure',
                found=self.stats['found'],
                added=self.stats['added'],
                updated=self.stats['updated'],
                errors=str(e),
                duration=duration
            )

            raise

    def close(self):
        """Clean up resources"""
        self.session.close()
        logger.info(f"Closed {self.scraper_name}")
