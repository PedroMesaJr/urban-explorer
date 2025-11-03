-- UrbEx Property Database Schema

-- Main properties table
CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Basic Information
    address TEXT NOT NULL,
    city TEXT,
    county TEXT,
    state TEXT NOT NULL,
    zip_code TEXT,

    -- Geocoding
    latitude REAL,
    longitude REAL,
    formatted_address TEXT,

    -- Property Details
    property_type TEXT,  -- Residential, Commercial, Industrial, etc.
    building_type TEXT,  -- House, Apartment, Mall, Factory, etc.
    year_built INTEGER,
    square_footage INTEGER,
    lot_size_sqft INTEGER,
    num_bedrooms INTEGER,
    num_bathrooms REAL,
    num_stories INTEGER,

    -- Ownership & Legal
    owner_name TEXT,
    owner_contact TEXT,
    last_sale_date DATE,
    last_sale_price REAL,
    current_assessed_value REAL,

    -- Abandonment Status
    status TEXT DEFAULT 'unknown',  -- active, abandoned, foreclosed, demolished, etc.
    abandonment_date DATE,
    years_abandoned REAL,

    -- Tax Information
    tax_delinquent BOOLEAN DEFAULT 0,
    tax_delinquency_years INTEGER DEFAULT 0,
    tax_delinquency_amount REAL DEFAULT 0,
    tax_id TEXT,

    -- Foreclosure Information
    foreclosure_status TEXT,  -- pre-foreclosure, auction, bank-owned, etc.
    foreclosure_date DATE,
    foreclosure_amount REAL,
    auction_date DATE,
    auction_url TEXT,

    -- Condition & Hazards
    structural_condition TEXT,  -- stable, deteriorating, unsafe, collapsed
    hazards TEXT,  -- JSON array: asbestos, mold, collapse risk, etc.
    has_security BOOLEAN DEFAULT 0,
    security_type TEXT,  -- fence, patrol, cameras, etc.

    -- Demolition
    demolition_scheduled BOOLEAN DEFAULT 0,
    demolition_date DATE,
    demolition_permit_number TEXT,

    -- Code Violations
    has_violations BOOLEAN DEFAULT 0,
    violation_count INTEGER DEFAULT 0,
    condemned BOOLEAN DEFAULT 0,

    -- Discovery & Metadata
    discovery_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_verified DATE,
    data_sources TEXT,  -- JSON array of source names

    -- Scoring
    abandonment_score INTEGER DEFAULT 0,  -- 0-10 likelihood of being abandoned
    exploration_score INTEGER DEFAULT 0,  -- 0-10 interest level for exploration

    -- Media
    thumbnail_url TEXT,
    street_view_url TEXT,

    -- Unique constraint
    UNIQUE(address, city, state)
);

-- Data sources tracking
CREATE TABLE IF NOT EXISTS data_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    source_name TEXT NOT NULL,
    source_url TEXT,
    scraped_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_data TEXT,  -- JSON blob of original data
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

-- Photos and media
CREATE TABLE IF NOT EXISTS property_media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    media_type TEXT NOT NULL,  -- photo, video, street_view, aerial
    url TEXT,
    local_path TEXT,
    caption TEXT,
    date_taken DATE,
    uploaded_by TEXT,
    uploaded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

-- Historical records (track changes over time)
CREATE TABLE IF NOT EXISTS property_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    field_name TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source TEXT,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

-- News articles and media mentions
CREATE TABLE IF NOT EXISTS news_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    title TEXT,
    url TEXT UNIQUE,
    source TEXT,
    published_date DATE,
    summary TEXT,
    full_text TEXT,
    sentiment TEXT,  -- positive, negative, neutral
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

-- Scraper logs
CREATE TABLE IF NOT EXISTS scraper_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scraper_name TEXT NOT NULL,
    run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT,  -- success, failure, partial
    properties_found INTEGER DEFAULT 0,
    properties_added INTEGER DEFAULT 0,
    properties_updated INTEGER DEFAULT 0,
    errors TEXT,
    duration_seconds REAL
);

-- User notes and custom data
CREATE TABLE IF NOT EXISTS property_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    note_text TEXT,
    tags TEXT,  -- JSON array of tags
    priority INTEGER DEFAULT 0,
    visited BOOLEAN DEFAULT 0,
    visit_date DATE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_properties_location ON properties(state, county, city);
CREATE INDEX IF NOT EXISTS idx_properties_status ON properties(status);
CREATE INDEX IF NOT EXISTS idx_properties_coords ON properties(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_properties_tax_delinquent ON properties(tax_delinquent);
CREATE INDEX IF NOT EXISTS idx_properties_foreclosure ON properties(foreclosure_status);
CREATE INDEX IF NOT EXISTS idx_properties_scores ON properties(abandonment_score, exploration_score);
CREATE INDEX IF NOT EXISTS idx_properties_demolition ON properties(demolition_scheduled, demolition_date);
CREATE INDEX IF NOT EXISTS idx_data_sources_property ON data_sources(property_id);
CREATE INDEX IF NOT EXISTS idx_property_media_property ON property_media(property_id);
CREATE INDEX IF NOT EXISTS idx_news_property ON news_articles(property_id);

-- Views for common queries
CREATE VIEW IF NOT EXISTS high_value_properties AS
SELECT
    p.*,
    COUNT(DISTINCT ds.source_name) as source_count,
    COUNT(DISTINCT pm.id) as media_count
FROM properties p
LEFT JOIN data_sources ds ON p.id = ds.property_id
LEFT JOIN property_media pm ON p.id = pm.property_id
WHERE p.abandonment_score >= 7
GROUP BY p.id
ORDER BY p.abandonment_score DESC, p.exploration_score DESC;

CREATE VIEW IF NOT EXISTS recently_discovered AS
SELECT *
FROM properties
WHERE discovery_date >= datetime('now', '-7 days')
ORDER BY discovery_date DESC;

CREATE VIEW IF NOT EXISTS demolition_watch AS
SELECT *
FROM properties
WHERE demolition_scheduled = 1
AND demolition_date >= date('now')
ORDER BY demolition_date ASC;
