#!/usr/bin/env python3
"""
Simple Flask dashboard to view property data
"""
from flask import Flask, render_template, request, jsonify
import yaml
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager

app = Flask(__name__)

# Load config
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

# Initialize database
db_path = config.get('database', {}).get('path', 'data/properties.db')
db = DatabaseManager(db_path)


@app.route('/')
def index():
    """Main dashboard page"""
    stats = db.get_statistics()
    return render_template('index.html', stats=stats)


@app.route('/api/properties')
def get_properties():
    """Get properties list (JSON API)"""
    # Get query parameters
    state = request.args.get('state')
    county = request.args.get('county')
    city = request.args.get('city')
    status = request.args.get('status')
    min_score = int(request.args.get('min_score', 0))
    limit = int(request.args.get('limit', 100))

    # Query database
    properties = db.get_properties(
        state=state,
        county=county,
        city=city,
        status=status,
        min_score=min_score,
        limit=limit
    )

    # Convert to JSON
    properties_json = [prop.to_dict() for prop in properties]

    return jsonify(properties_json)


@app.route('/api/property/<int:property_id>')
def get_property(property_id):
    """Get single property details"""
    prop = db.get_property_by_id(property_id)

    if prop:
        return jsonify(prop.to_dict())
    else:
        return jsonify({'error': 'Property not found'}), 404


@app.route('/api/map_data')
def get_map_data():
    """Get property coordinates for map visualization"""
    min_score = int(request.args.get('min_score', 5))

    properties = db.get_properties(min_score=min_score, limit=500)

    # Return GeoJSON format
    features = []
    for prop in properties:
        if prop.latitude and prop.longitude:
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [prop.longitude, prop.latitude]
                },
                'properties': {
                    'id': prop.id,
                    'address': prop.address,
                    'city': prop.city,
                    'state': prop.state,
                    'abandonment_score': prop.abandonment_score,
                    'status': prop.status,
                    'foreclosure_status': prop.foreclosure_status,
                }
            })

    return jsonify({
        'type': 'FeatureCollection',
        'features': features
    })


@app.route('/api/stats')
def get_stats():
    """Get database statistics"""
    return jsonify(db.get_statistics())


@app.route('/api/demolition_watch')
def get_demolition_watch():
    """Get properties scheduled for demolition"""
    days_ahead = int(request.args.get('days', 30))

    properties = db.get_demolition_scheduled(days_ahead)

    return jsonify([prop.to_dict() for prop in properties])


@app.route('/api/search')
def search_properties():
    """Search properties"""
    query = request.args.get('q', '')

    if len(query) < 3:
        return jsonify([])

    properties = db.search_properties(query)

    return jsonify([prop.to_dict() for prop in properties])


if __name__ == '__main__':
    # Get dashboard config
    dashboard_config = config.get('dashboard', {})
    host = dashboard_config.get('host', '127.0.0.1')
    port = dashboard_config.get('port', 5000)
    debug = dashboard_config.get('debug', True)

    print(f"\nStarting UrbEx Property Dashboard...")
    print(f"Open your browser to: http://{host}:{port}")
    print(f"Database: {db_path}")
    print(f"\nPress CTRL+C to stop\n")

    app.run(host=host, port=port, debug=debug)
