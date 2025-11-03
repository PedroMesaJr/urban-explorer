#!/usr/bin/env python3
"""
UrbEx Property Scraper - Main Application

Orchestrates data collection from multiple sources
"""
import argparse
import yaml
import sys
from pathlib import Path
from loguru import logger
from datetime import datetime

# Database
from database.db_manager import DatabaseManager

# Scrapers
from scrapers.tax_assessor import TaxAssessorScraper
from scrapers.foreclosure import ForeclosureScraper
from scrapers.hud import HUDScraper
from scrapers.google_maps import GoogleMapsScraper


def setup_logging(config: dict):
    """Configure logging"""
    log_config = config.get('logging', {})
    log_level = log_config.get('level', 'INFO')
    log_file = log_config.get('log_file', 'logs/scraper.log')

    # Create logs directory
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    # Configure loguru
    logger.remove()  # Remove default handler

    # Console output
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=log_level
    )

    # File output
    logger.add(
        log_file,
        rotation=log_config.get('log_rotation', '100 MB'),
        retention=log_config.get('log_retention', '30 days'),
        level=log_level
    )

    logger.info("Logging configured")


def load_config(config_path: str = 'config.yml') -> dict:
    """Load configuration file"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        logger.info("Please copy config.example.yml to config.yml and configure it")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        sys.exit(1)


def run_all_scrapers(config: dict, db: DatabaseManager):
    """Run all configured scrapers"""
    logger.info("=" * 80)
    logger.info("Starting all scrapers...")
    logger.info("=" * 80)

    target_locations = config.get('target_locations', [])

    # Initialize scrapers
    tax_scraper = TaxAssessorScraper(config, db)
    foreclosure_scraper = ForeclosureScraper(config, db)
    hud_scraper = HUDScraper(config, db)
    google_scraper = GoogleMapsScraper(config, db)

    # Run each scraper for each location
    for location in target_locations:
        state = location.get('state')
        counties = location.get('counties', [])

        logger.info(f"\n{'=' * 80}")
        logger.info(f"Processing {state}")
        logger.info(f"{'=' * 80}\n")

        # Tax Assessor
        if counties:
            for county in counties:
                try:
                    logger.info(f"Running Tax Assessor scraper for {county}, {state}")
                    tax_scraper.run(state=state, county=county)
                except Exception as e:
                    logger.error(f"Tax Assessor scraper failed: {e}")

        # Foreclosure sites
        try:
            logger.info(f"Running Foreclosure scraper for {state}")
            foreclosure_scraper.run(state=state)
        except Exception as e:
            logger.error(f"Foreclosure scraper failed: {e}")

        # HUD
        try:
            logger.info(f"Running HUD scraper for {state}")
            hud_scraper.run(state=state)
        except Exception as e:
            logger.error(f"HUD scraper failed: {e}")

    # Enrich with Google Maps data
    try:
        logger.info("Running Google Maps enrichment")
        google_scraper.run()
    except Exception as e:
        logger.error(f"Google Maps scraper failed: {e}")

    # Clean up
    tax_scraper.close()
    foreclosure_scraper.close()
    hud_scraper.close()
    google_scraper.close()

    logger.info("\n" + "=" * 80)
    logger.info("All scrapers completed!")
    logger.info("=" * 80)

    # Print statistics
    stats = db.get_statistics()
    logger.info("\nDatabase Statistics:")
    logger.info(f"  Total Properties: {stats['total_properties']}")
    logger.info(f"  Abandoned: {stats['abandoned']}")
    logger.info(f"  Foreclosed: {stats['foreclosed']}")
    logger.info(f"  Tax Delinquent: {stats['tax_delinquent']}")
    logger.info(f"  High Score (7+): {stats['high_score_properties']}")


def run_specific_scraper(scraper_name: str, config: dict, db: DatabaseManager, **kwargs):
    """Run a specific scraper"""
    logger.info(f"Running {scraper_name} scraper...")

    if scraper_name == 'tax_assessor':
        scraper = TaxAssessorScraper(config, db)
    elif scraper_name == 'foreclosure':
        scraper = ForeclosureScraper(config, db)
    elif scraper_name == 'hud':
        scraper = HUDScraper(config, db)
    elif scraper_name == 'google_maps':
        scraper = GoogleMapsScraper(config, db)
    else:
        logger.error(f"Unknown scraper: {scraper_name}")
        return

    try:
        scraper.run(**kwargs)
    except Exception as e:
        logger.error(f"Scraper failed: {e}", exc_info=True)
    finally:
        scraper.close()


def export_data(db: DatabaseManager, output_file: str, filters: dict = None):
    """Export data to CSV"""
    logger.info(f"Exporting data to {output_file}...")

    try:
        db.export_to_csv(output_file, filters)
        logger.info(f"Export completed: {output_file}")
    except Exception as e:
        logger.error(f"Export failed: {e}")


def show_statistics(db: DatabaseManager):
    """Display database statistics"""
    stats = db.get_statistics()

    print("\n" + "=" * 60)
    print("DATABASE STATISTICS")
    print("=" * 60)
    print(f"Database Path: {stats['database_path']}")
    print(f"\nTotal Properties: {stats['total_properties']}")
    print(f"  - Abandoned: {stats['abandoned']}")
    print(f"  - Foreclosed: {stats['foreclosed']}")
    print(f"  - Tax Delinquent: {stats['tax_delinquent']}")
    print(f"  - High Score (7+): {stats['high_score_properties']}")
    print("=" * 60)


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description='UrbEx Property Scraper - Find abandoned and distressed properties'
    )

    parser.add_argument(
        '--config',
        default='config.yml',
        help='Path to configuration file (default: config.yml)'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all scrapers'
    )

    parser.add_argument(
        '--scraper',
        choices=['tax_assessor', 'foreclosure', 'hud', 'google_maps'],
        help='Run specific scraper'
    )

    parser.add_argument(
        '--state',
        help='State code (e.g., CA, NY)'
    )

    parser.add_argument(
        '--county',
        help='County name'
    )

    parser.add_argument(
        '--city',
        help='City name'
    )

    parser.add_argument(
        '--export',
        help='Export data to CSV file'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show database statistics'
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Setup logging
    setup_logging(config)

    # Initialize database
    db_path = config.get('database', {}).get('path', 'data/properties.db')
    db = DatabaseManager(db_path)

    try:
        if args.stats:
            # Show statistics
            show_statistics(db)

        elif args.export:
            # Export data
            filters = {}
            if args.state:
                filters['state'] = args.state

            export_data(db, args.export, filters)

        elif args.all:
            # Run all scrapers
            run_all_scrapers(config, db)

        elif args.scraper:
            # Run specific scraper
            kwargs = {}
            if args.state:
                kwargs['state'] = args.state
            if args.county:
                kwargs['county'] = args.county
            if args.city:
                kwargs['city'] = args.city

            run_specific_scraper(args.scraper, config, db, **kwargs)

        else:
            parser.print_help()

    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        db.close()

    logger.info("Application terminated")


if __name__ == '__main__':
    main()
