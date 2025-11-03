"""
Database manager for property data
"""
import os
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from loguru import logger

from database.models import (
    Base, Property, DataSource, PropertyMedia, PropertyHistory,
    NewsArticle, ScraperLog, PropertyNote
)


class DatabaseManager:
    """Manages database connections and operations"""

    def __init__(self, db_path: str = "data/properties.db"):
        """Initialize database connection"""
        self.db_path = db_path

        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Create engine
        self.engine = create_engine(
            f'sqlite:///{db_path}',
            connect_args={'check_same_thread': False},
            poolclass=StaticPool,
            echo=False
        )

        # Create tables
        Base.metadata.create_all(self.engine)

        # Create session factory
        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)

        logger.info(f"Database initialized: {db_path}")

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope for database operations"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()

    def add_or_update_property(self, property_data: Dict[str, Any], source_name: str) -> Property:
        """Add a new property or update existing one"""
        with self.session_scope() as session:
            # Check if property exists
            existing = session.query(Property).filter(
                and_(
                    Property.address == property_data.get('address'),
                    Property.city == property_data.get('city'),
                    Property.state == property_data.get('state')
                )
            ).first()

            if existing:
                # Update existing property
                for key, value in property_data.items():
                    if value is not None and hasattr(existing, key):
                        setattr(existing, key, value)

                existing.last_updated = datetime.utcnow()
                existing.add_data_source(source_name)
                logger.info(f"Updated property: {existing.address}")
                return existing
            else:
                # Create new property
                new_property = Property(**property_data)
                new_property.add_data_source(source_name)
                session.add(new_property)
                session.flush()  # Get the ID
                logger.info(f"Added new property: {new_property.address}")
                return new_property

    def get_property_by_id(self, property_id: int) -> Optional[Property]:
        """Get property by ID"""
        with self.session_scope() as session:
            return session.query(Property).filter(Property.id == property_id).first()

    def get_properties(
        self,
        state: Optional[str] = None,
        county: Optional[str] = None,
        city: Optional[str] = None,
        status: Optional[str] = None,
        min_score: int = 0,
        limit: int = 100
    ) -> List[Property]:
        """Get properties with filters"""
        with self.session_scope() as session:
            query = session.query(Property)

            if state:
                query = query.filter(Property.state == state)
            if county:
                query = query.filter(Property.county == county)
            if city:
                query = query.filter(Property.city == city)
            if status:
                query = query.filter(Property.status == status)
            if min_score > 0:
                query = query.filter(Property.abandonment_score >= min_score)

            return query.order_by(
                Property.abandonment_score.desc(),
                Property.exploration_score.desc()
            ).limit(limit).all()

    def get_tax_delinquent_properties(self, min_years: int = 1) -> List[Property]:
        """Get tax delinquent properties"""
        with self.session_scope() as session:
            return session.query(Property).filter(
                and_(
                    Property.tax_delinquent == True,
                    Property.tax_delinquency_years >= min_years
                )
            ).all()

    def get_foreclosure_properties(self) -> List[Property]:
        """Get properties in foreclosure"""
        with self.session_scope() as session:
            return session.query(Property).filter(
                Property.foreclosure_status.isnot(None)
            ).all()

    def get_demolition_scheduled(self, days_ahead: int = 30) -> List[Property]:
        """Get properties scheduled for demolition"""
        with self.session_scope() as session:
            future_date = datetime.now().date() + timedelta(days=days_ahead)
            return session.query(Property).filter(
                and_(
                    Property.demolition_scheduled == True,
                    Property.demolition_date <= future_date,
                    Property.demolition_date >= datetime.now().date()
                )
            ).order_by(Property.demolition_date).all()

    def search_properties(self, search_term: str) -> List[Property]:
        """Search properties by address or city"""
        with self.session_scope() as session:
            search = f"%{search_term}%"
            return session.query(Property).filter(
                or_(
                    Property.address.like(search),
                    Property.city.like(search),
                    Property.owner_name.like(search)
                )
            ).all()

    def add_data_source(self, property_id: int, source_name: str,
                       source_url: str = None, raw_data: Dict = None):
        """Add a data source record"""
        with self.session_scope() as session:
            import json
            data_source = DataSource(
                property_id=property_id,
                source_name=source_name,
                source_url=source_url,
                raw_data=json.dumps(raw_data) if raw_data else None
            )
            session.add(data_source)

    def add_media(self, property_id: int, media_type: str,
                  url: str = None, local_path: str = None, caption: str = None):
        """Add media to property"""
        with self.session_scope() as session:
            media = PropertyMedia(
                property_id=property_id,
                media_type=media_type,
                url=url,
                local_path=local_path,
                caption=caption
            )
            session.add(media)

    def log_scraper_run(self, scraper_name: str, status: str,
                       found: int = 0, added: int = 0, updated: int = 0,
                       errors: str = None, duration: float = 0):
        """Log scraper execution"""
        with self.session_scope() as session:
            log = ScraperLog(
                scraper_name=scraper_name,
                status=status,
                properties_found=found,
                properties_added=added,
                properties_updated=updated,
                errors=errors,
                duration_seconds=duration
            )
            session.add(log)

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.session_scope() as session:
            total = session.query(Property).count()
            abandoned = session.query(Property).filter(Property.status == 'abandoned').count()
            foreclosed = session.query(Property).filter(Property.foreclosure_status.isnot(None)).count()
            tax_delinquent = session.query(Property).filter(Property.tax_delinquent == True).count()
            high_score = session.query(Property).filter(Property.abandonment_score >= 7).count()

            return {
                'total_properties': total,
                'abandoned': abandoned,
                'foreclosed': foreclosed,
                'tax_delinquent': tax_delinquent,
                'high_score_properties': high_score,
                'database_path': self.db_path
            }

    def export_to_csv(self, output_file: str, filters: Dict[str, Any] = None):
        """Export properties to CSV"""
        import csv
        with self.session_scope() as session:
            query = session.query(Property)

            # Apply filters if provided
            if filters:
                if 'state' in filters:
                    query = query.filter(Property.state == filters['state'])
                if 'min_score' in filters:
                    query = query.filter(Property.abandonment_score >= filters['min_score'])

            properties = query.all()

            # Write to CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Header
                writer.writerow([
                    'ID', 'Address', 'City', 'County', 'State', 'Zip',
                    'Latitude', 'Longitude', 'Property Type', 'Status',
                    'Year Built', 'Square Footage', 'Owner',
                    'Tax Delinquent', 'Foreclosure Status',
                    'Abandonment Score', 'Exploration Score',
                    'Demolition Scheduled', 'Demolition Date'
                ])

                # Data
                for prop in properties:
                    writer.writerow([
                        prop.id, prop.address, prop.city, prop.county,
                        prop.state, prop.zip_code, prop.latitude, prop.longitude,
                        prop.property_type, prop.status, prop.year_built,
                        prop.square_footage, prop.owner_name,
                        prop.tax_delinquent, prop.foreclosure_status,
                        prop.abandonment_score, prop.exploration_score,
                        prop.demolition_scheduled,
                        prop.demolition_date.isoformat() if prop.demolition_date else None
                    ])

            logger.info(f"Exported {len(properties)} properties to {output_file}")

    def close(self):
        """Close database connections"""
        self.Session.remove()
        self.engine.dispose()
        logger.info("Database connections closed")
