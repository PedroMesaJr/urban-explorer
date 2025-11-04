#!/usr/bin/env python3
"""
Interactive Menu System for UrbEx Property Scraper
Makes it SUPER EASY to use the scraper!
"""

import os
import sys
import yaml
from datetime import datetime
from loguru import logger

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header():
    """Print beautiful ASCII art header"""
    header = f"""
{Colors.CYAN}╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║  {Colors.BOLD}🏚️  URBEX PROPERTY SCRAPER - INTERACTIVE MENU 🔍{Colors.END}{Colors.CYAN}                 ║
║                                                                       ║
║  {Colors.YELLOW}Find Abandoned & Distressed Properties with Ease!{Colors.END}{Colors.CYAN}               ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝{Colors.END}
"""
    print(header)

def print_section(title):
    """Print a section divider"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*75}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}  {title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*75}{Colors.END}\n")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ {message}{Colors.END}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def print_menu_option(number, title, description):
    """Print a menu option with nice formatting"""
    print(f"{Colors.BOLD}{Colors.GREEN}[{number}]{Colors.END} {Colors.BOLD}{title}{Colors.END}")
    print(f"    {Colors.CYAN}{description}{Colors.END}\n")

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def wait_for_enter():
    """Wait for user to press Enter"""
    input(f"\n{Colors.YELLOW}Press ENTER to continue...{Colors.END}")

def get_choice(prompt, valid_choices):
    """Get user choice with validation"""
    while True:
        choice = input(f"{Colors.BOLD}{Colors.YELLOW}{prompt}{Colors.END} ").strip()
        if choice in valid_choices:
            return choice
        print_error(f"Invalid choice. Please choose from: {', '.join(valid_choices)}")

def check_config():
    """Check if config file exists and is valid"""
    if not os.path.exists('config.yml'):
        print_error("Configuration file (config.yml) not found!")
        print_info("Creating config.yml from template...")
        os.system('cp config.example.yml config.yml')
        print_success("Config file created!")
        print_warning("Please edit config.yml and add your API keys before continuing.")
        return False

    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)

    api_key = config.get('api_keys', {}).get('google_maps', '')
    if 'YOUR_' in api_key or not api_key:
        print_warning("Google Maps API key not configured!")
        print_info("Some features (geocoding) won't work without it.")
        print_info("Get a free API key at: https://console.cloud.google.com/")

    return True

def show_main_menu():
    """Display the main menu"""
    clear_screen()
    print_header()

    print_section("📋 MAIN MENU - Choose an option")

    print_menu_option("1", "🚀 Quick Start",
                     "Run your first scraper with default settings (Recommended for beginners)")

    print_menu_option("2", "🔍 Run Scraper",
                     "Choose which scraper to run (HUD, Foreclosure, Tax Assessor, etc.)")

    print_menu_option("3", "📊 View Statistics",
                     "See how many properties you've found and database stats")

    print_menu_option("4", "🌐 Start Dashboard",
                     "Open the beautiful web interface to browse properties")

    print_menu_option("5", "💾 Export Data",
                     "Save your properties to CSV/Excel format")

    print_menu_option("6", "⚙️  Configure Settings",
                     "Edit API keys, target locations, and scraper settings")

    print_menu_option("7", "📚 Help & Documentation",
                     "Learn how to use the scraper and troubleshooting")

    print_menu_option("8", "🧪 Test Installation",
                     "Verify everything is working correctly")

    print_menu_option("9", "❌ Exit",
                     "Close the interactive menu")

    return get_choice("Choose an option (1-9):", ['1', '2', '3', '4', '5', '6', '7', '8', '9'])

def quick_start():
    """Quick start guide for beginners"""
    clear_screen()
    print_section("🚀 QUICK START GUIDE")

    print_info("This will run the HUD scraper for California properties.")
    print_info("It's the easiest scraper to get started with!")
    print()

    confirm = get_choice("Ready to start? (y/n):", ['y', 'n', 'Y', 'N'])

    if confirm.lower() == 'y':
        print()
        print_info("Starting HUD scraper for California...")
        print_info("This may take a few minutes...")
        print()

        os.system('python main.py --scraper hud --state CA')

        print()
        print_success("Scraping complete!")
        print_info("Would you like to view the results?")

        view = get_choice("Open dashboard? (y/n):", ['y', 'n', 'Y', 'N'])
        if view.lower() == 'y':
            start_dashboard()

    wait_for_enter()

def run_scraper():
    """Run a specific scraper"""
    clear_screen()
    print_section("🔍 RUN SCRAPER")

    print("Available scrapers:")
    print()
    print_menu_option("1", "HUD Scraper",
                     "Government foreclosures (easiest to start with)")
    print_menu_option("2", "Foreclosure Scraper",
                     "Foreclosure.com and similar sites")
    print_menu_option("3", "Tax Assessor",
                     "County tax delinquent properties (requires customization)")
    print_menu_option("4", "Run ALL Scrapers",
                     "Run all available scrapers (takes longer)")
    print_menu_option("5", "Back to Main Menu",
                     "Go back")

    choice = get_choice("Choose scraper (1-5):", ['1', '2', '3', '4', '5'])

    if choice == '5':
        return

    if choice == '4':
        print()
        print_info("Running all scrapers...")
        os.system('python main.py --all')
    else:
        # Get state
        print()
        state = input(f"{Colors.YELLOW}Enter state (e.g., CA, NY, TX): {Colors.END}").strip().upper()

        if not state:
            print_error("State is required!")
            wait_for_enter()
            return

        scraper_map = {
            '1': 'hud',
            '2': 'foreclosure',
            '3': 'tax_assessor'
        }

        scraper_name = scraper_map[choice]

        print()
        print_info(f"Running {scraper_name} scraper for {state}...")
        print()

        os.system(f'python main.py --scraper {scraper_name} --state {state}')

    print()
    print_success("Scraping complete!")
    wait_for_enter()

def view_statistics():
    """View database statistics"""
    clear_screen()
    print_section("📊 DATABASE STATISTICS")

    print_info("Fetching statistics...")
    print()

    os.system('python main.py --stats')

    wait_for_enter()

def start_dashboard():
    """Start the web dashboard"""
    clear_screen()
    print_section("🌐 STARTING WEB DASHBOARD")

    print_success("Dashboard starting...")
    print()
    print_info("📍 URL: http://127.0.0.1:5000")
    print_info("🔄 The dashboard will open in your terminal")
    print_info("🛑 Press CTRL+C to stop the dashboard")
    print()
    print_warning("Note: Your terminal will be busy while dashboard is running.")
    print()

    wait = get_choice("Start dashboard now? (y/n):", ['y', 'n', 'Y', 'N'])

    if wait.lower() == 'y':
        print()
        print_success("Starting dashboard...")
        print_info("Open your browser to: http://127.0.0.1:5000")
        print()

        try:
            os.system('python dashboard/app.py')
        except KeyboardInterrupt:
            print()
            print_success("Dashboard stopped!")

    wait_for_enter()

def export_data():
    """Export data to file"""
    clear_screen()
    print_section("💾 EXPORT DATA")

    print("Export options:")
    print()
    print_menu_option("1", "Export All Properties",
                     "Save all properties to CSV")
    print_menu_option("2", "Export by State",
                     "Export properties from a specific state")
    print_menu_option("3", "Export High Score Properties",
                     "Export only properties with score 7+")
    print_menu_option("4", "Back to Main Menu",
                     "Go back")

    choice = get_choice("Choose export option (1-4):", ['1', '2', '3', '4'])

    if choice == '4':
        return

    # Get filename
    print()
    default_name = f"properties_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filename = input(f"{Colors.YELLOW}Output filename (default: {default_name}): {Colors.END}").strip()

    if not filename:
        filename = default_name

    if not filename.endswith('.csv'):
        filename += '.csv'

    print()
    print_info(f"Exporting to: exports/{filename}")

    if choice == '1':
        os.system(f'python main.py --export {filename}')
    elif choice == '2':
        state = input(f"{Colors.YELLOW}Enter state (e.g., CA): {Colors.END}").strip().upper()
        os.system(f'python main.py --export {filename} --state {state}')
    elif choice == '3':
        os.system(f'python main.py --export {filename} --min-score 7')

    print()
    print_success(f"Export complete! File saved to: exports/{filename}")
    wait_for_enter()

def configure_settings():
    """Configure settings"""
    clear_screen()
    print_section("⚙️  CONFIGURE SETTINGS")

    print_info("Opening config.yml in your default text editor...")
    print()

    # Try to open with nano, vim, or default editor
    if os.system('which nano > /dev/null 2>&1') == 0:
        os.system('nano config.yml')
    elif os.system('which vim > /dev/null 2>&1') == 0:
        os.system('vim config.yml')
    else:
        print_warning("No text editor found!")
        print_info("Please edit config.yml manually with your preferred editor")
        print_info("Location: " + os.path.abspath('config.yml'))

    wait_for_enter()

def show_help():
    """Show help and documentation"""
    clear_screen()
    print_section("📚 HELP & DOCUMENTATION")

    print_info("Available documentation files:")
    print()

    docs = {
        '1': ('QUICK_START.md', 'Quick start guide - Get up and running fast!'),
        '2': ('SETUP.md', 'Detailed setup instructions and troubleshooting'),
        '3': ('GETTING_STARTED.md', 'Usage guide and examples'),
        '4': ('PROJECT_OVERVIEW.md', 'Project architecture and design'),
        '5': ('README.md', 'Project overview'),
    }

    for num, (filename, desc) in docs.items():
        print_menu_option(num, filename, desc)

    print_menu_option("6", "Back to Main Menu", "Go back")

    choice = get_choice("View documentation (1-6):", ['1', '2', '3', '4', '5', '6'])

    if choice == '6':
        return

    doc_file = docs[choice][0]

    if os.path.exists(doc_file):
        print()
        print_info(f"Opening {doc_file}...")
        print()

        # Try to open with less, more, or cat
        if os.system('which less > /dev/null 2>&1') == 0:
            os.system(f'less {doc_file}')
        elif os.system('which more > /dev/null 2>&1') == 0:
            os.system(f'more {doc_file}')
        else:
            os.system(f'cat {doc_file}')
    else:
        print_error(f"{doc_file} not found!")

    wait_for_enter()

def test_installation():
    """Test installation"""
    clear_screen()
    print_section("🧪 TEST INSTALLATION")

    print_info("Running installation tests...")
    print()

    # Test 1: Virtual environment
    print(f"{Colors.BOLD}Test 1: Virtual Environment{Colors.END}")
    if 'VIRTUAL_ENV' in os.environ:
        print_success("Virtual environment is active")
    else:
        print_warning("Virtual environment is NOT active")
        print_info("Run: source venv/bin/activate")
    print()

    # Test 2: Configuration
    print(f"{Colors.BOLD}Test 2: Configuration File{Colors.END}")
    if os.path.exists('config.yml'):
        print_success("config.yml exists")
    else:
        print_error("config.yml not found!")
    print()

    # Test 3: Database
    print(f"{Colors.BOLD}Test 3: Database{Colors.END}")
    if os.path.exists('data/properties.db'):
        print_success("Database file exists")
    else:
        print_warning("Database not initialized yet")
        print_info("It will be created on first run")
    print()

    # Test 4: Python modules
    print(f"{Colors.BOLD}Test 4: Python Modules{Colors.END}")
    try:
        import requests
        import bs4
        import flask
        import sqlalchemy
        print_success("All required modules installed")
    except ImportError as e:
        print_error(f"Missing module: {e}")
        print_info("Run: pip install -r requirements.txt")
    print()

    # Test 5: Run stats command
    print(f"{Colors.BOLD}Test 5: Database Connection{Colors.END}")
    result = os.system('python main.py --stats > /dev/null 2>&1')
    if result == 0:
        print_success("Database connection works!")
    else:
        print_error("Database connection failed!")
    print()

    print_success("Testing complete!")
    wait_for_enter()

def main():
    """Main menu loop"""

    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print_error("Please run this script from the project root directory!")
        print_info("Navigate to: urbex-property-scraper/")
        sys.exit(1)

    # Check configuration
    check_config()

    while True:
        try:
            choice = show_main_menu()

            if choice == '1':
                quick_start()
            elif choice == '2':
                run_scraper()
            elif choice == '3':
                view_statistics()
            elif choice == '4':
                start_dashboard()
            elif choice == '5':
                export_data()
            elif choice == '6':
                configure_settings()
            elif choice == '7':
                show_help()
            elif choice == '8':
                test_installation()
            elif choice == '9':
                clear_screen()
                print_header()
                print_success("Thanks for using UrbEx Property Scraper!")
                print_info("Happy property hunting! 🏚️🔍")
                print()
                break

        except KeyboardInterrupt:
            print()
            print()
            print_warning("Interrupted by user")
            confirm = get_choice("Really exit? (y/n):", ['y', 'n', 'Y', 'N'])
            if confirm.lower() == 'y':
                break
        except Exception as e:
            print()
            print_error(f"An error occurred: {e}")
            print_info("Check logs/scraper.log for details")
            wait_for_enter()

if __name__ == '__main__':
    main()
