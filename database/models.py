"""
SQLAlchemy models for the property database
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Date, DateTime,
    ForeignKey, Text, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import json

Base = declarative_base()


class Property(Base):
    __tablename__ = 'properties'

    id = Column(Integer, primary_key=True)

    # Basic Information
    address = Column(String, nullable=False)
    city = Column(String)
    county = Column(String)
    state = Column(String, nullable=False)
    zip_code = Column(String)

    # Geocoding
    latitude = Column(Float)
    longitude = Column(Float)
    formatted_address = Column(String)

    # Property Details
    property_type = Column(String)
    building_type = Column(String)
    year_built = Column(Integer)
    square_footage = Column(Integer)
    lot_size_sqft = Column(Integer)
    num_bedrooms = Column(Integer)
    num_bathrooms = Column(Float)
    num_stories = Column(Integer)

    # Ownership & Legal
    owner_name = Column(String)
    owner_contact = Column(String)
    last_sale_date = Column(Date)
    last_sale_price = Column(Float)
    current_assessed_value = Column(Float)

    # Abandonment Status
    status = Column(String, default='unknown')
    abandonment_date = Column(Date)
    years_abandoned = Column(Float)

    # Tax Information
    tax_delinquent = Column(Boolean, default=False)
    tax_delinquency_years = Column(Integer, default=0)
    tax_delinquency_amount = Column(Float, default=0)
    tax_id = Column(String)

    # Foreclosure Information
    foreclosure_status = Column(String)
    foreclosure_date = Column(Date)
    foreclosure_amount = Column(Float)
    auction_date = Column(Date)
    auction_url = Column(String)

    # Condition & Hazards
    structural_condition = Column(String)
    hazards = Column(Text)  # JSON
    has_security = Column(Boolean, default=False)
    security_type = Column(String)

    # Demolition
    demolition_scheduled = Column(Boolean, default=False)
    demolition_date = Column(Date)
    demolition_permit_number = Column(String)

    # Code Violations
    has_violations = Column(Boolean, default=False)
    violation_count = Column(Integer, default=0)
    condemned = Column(Boolean, default=False)

    # Discovery & Metadata
    discovery_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_verified = Column(Date)
    data_sources = Column(Text)  # JSON

    # Scoring
    abandonment_score = Column(Integer, default=0)
    exploration_score = Column(Integer, default=0)

    # Media
    thumbnail_url = Column(String)
    street_view_url = Column(String)

    # Relationships
    sources = relationship('DataSource', back_populates='property', cascade='all, delete-orphan')
    media = relationship('PropertyMedia', back_populates='property', cascade='all, delete-orphan')
    history = relationship('PropertyHistory', back_populates='property', cascade='all, delete-orphan')
    news = relationship('NewsArticle', back_populates='property', cascade='all, delete-orphan')
    notes = relationship('PropertyNote', back_populates='property', cascade='all, delete-orphan')

    __table_args__ = (
        UniqueConstraint('address', 'city', 'state', name='unique_address'),
    )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'address': self.address,
            'city': self.city,
            'county': self.county,
            'state': self.state,
            'zip_code': self.zip_code,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'property_type': self.property_type,
            'building_type': self.building_type,
            'year_built': self.year_built,
            'status': self.status,
            'abandonment_score': self.abandonment_score,
            'exploration_score': self.exploration_score,
            'tax_delinquent': self.tax_delinquent,
            'foreclosure_status': self.foreclosure_status,
            'demolition_scheduled': self.demolition_scheduled,
            'demolition_date': self.demolition_date.isoformat() if self.demolition_date else None,
        }

    def get_hazards(self):
        """Parse hazards JSON"""
        if self.hazards:
            try:
                return json.loads(self.hazards)
            except:
                return []
        return []

    def set_hazards(self, hazards_list):
        """Set hazards as JSON"""
        self.hazards = json.dumps(hazards_list)

    def get_data_sources(self):
        """Parse data sources JSON"""
        if self.data_sources:
            try:
                return json.loads(self.data_sources)
            except:
                return []
        return []

    def add_data_source(self, source_name):
        """Add a data source"""
        sources = self.get_data_sources()
        if source_name not in sources:
            sources.append(source_name)
            self.data_sources = json.dumps(sources)


class DataSource(Base):
    __tablename__ = 'data_sources'

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.id'), nullable=False)
    source_name = Column(String, nullable=False)
    source_url = Column(String)
    scraped_date = Column(DateTime, default=datetime.utcnow)
    raw_data = Column(Text)  # JSON

    property = relationship('Property', back_populates='sources')


class PropertyMedia(Base):
    __tablename__ = 'property_media'

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.id'), nullable=False)
    media_type = Column(String, nullable=False)
    url = Column(String)
    local_path = Column(String)
    caption = Column(String)
    date_taken = Column(Date)
    uploaded_by = Column(String)
    uploaded_date = Column(DateTime, default=datetime.utcnow)

    property = relationship('Property', back_populates='media')


class PropertyHistory(Base):
    __tablename__ = 'property_history'

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.id'), nullable=False)
    field_name = Column(String, nullable=False)
    old_value = Column(String)
    new_value = Column(String)
    change_date = Column(DateTime, default=datetime.utcnow)
    source = Column(String)

    property = relationship('Property', back_populates='history')


class NewsArticle(Base):
    __tablename__ = 'news_articles'

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.id'), nullable=False)
    title = Column(String)
    url = Column(String, unique=True)
    source = Column(String)
    published_date = Column(Date)
    summary = Column(Text)
    full_text = Column(Text)
    sentiment = Column(String)

    property = relationship('Property', back_populates='news')


class ScraperLog(Base):
    __tablename__ = 'scraper_logs'

    id = Column(Integer, primary_key=True)
    scraper_name = Column(String, nullable=False)
    run_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String)
    properties_found = Column(Integer, default=0)
    properties_added = Column(Integer, default=0)
    properties_updated = Column(Integer, default=0)
    errors = Column(Text)
    duration_seconds = Column(Float)


class PropertyNote(Base):
    __tablename__ = 'property_notes'

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.id'), nullable=False)
    note_text = Column(Text)
    tags = Column(Text)  # JSON
    priority = Column(Integer, default=0)
    visited = Column(Boolean, default=False)
    visit_date = Column(Date)
    created_date = Column(DateTime, default=datetime.utcnow)

    property = relationship('Property', back_populates='notes')

    def get_tags(self):
        """Parse tags JSON"""
        if self.tags:
            try:
                return json.loads(self.tags)
            except:
                return []
        return []

    def set_tags(self, tags_list):
        """Set tags as JSON"""
        self.tags = json.dumps(tags_list)
