# 🎨 VISUAL COMMAND GUIDE - Super Easy!

## 🚀 THE EASIEST WAY TO START

### Option 1: Interactive Menu (RECOMMENDED!) ⭐

```bash
python menu.py
```

**That's it!** The interactive menu makes everything SUPER EASY:
- ✅ Beautiful colored interface
- ✅ Clear numbered options (just type 1, 2, 3, etc.)
- ✅ Step-by-step guidance
- ✅ NO command-line knowledge needed!

---

## 📺 WHAT YOU'LL SEE

### Main Menu Looks Like This:

```
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║  🏚️  URBEX PROPERTY SCRAPER - INTERACTIVE MENU 🔍                   ║
║                                                                       ║
║  Find Abandoned & Distressed Properties with Ease!                   ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════════
  📋 MAIN MENU - Choose an option
═══════════════════════════════════════════════════════════════════════

[1] 🚀 Quick Start
    Run your first scraper with default settings (Recommended for beginners)

[2] 🔍 Run Scraper
    Choose which scraper to run (HUD, Foreclosure, Tax Assessor, etc.)

[3] 📊 View Statistics
    See how many properties you've found and database stats

[4] 🌐 Start Dashboard
    Open the beautiful web interface to browse properties

[5] 💾 Export Data
    Save your properties to CSV/Excel format

[6] ⚙️  Configure Settings
    Edit API keys, target locations, and scraper settings

[7] 📚 Help & Documentation
    Learn how to use the scraper and troubleshooting

[8] 🧪 Test Installation
    Verify everything is working correctly

[9] ❌ Exit
    Close the interactive menu

Choose an option (1-9):
```

---

## 🎯 QUICK START GUIDE (For Complete Beginners)

### Step 1: Open Terminal
- **Windows**: Press `Windows + R`, type `wsl`, press Enter
- **Mac**: Press `Cmd + Space`, type `terminal`, press Enter
- **Linux**: Press `Ctrl + Alt + T`

### Step 2: Go to Project Folder

```bash
cd /mnt/c/Users/Pedro/urbex-property-scraper
```

### Step 3: Activate Virtual Environment

```bash
source venv/bin/activate
```

**You'll see `(venv)` appear in your terminal prompt!**

### Step 4: Start the Interactive Menu

```bash
python menu.py
```

### Step 5: Choose Option 1 (Quick Start)

Just type: `1` and press Enter!

**The menu will guide you through everything!** 🎉

---

## 📋 COMMAND CHEAT SHEET

### Essential Commands (Copy & Paste These!)

#### 🟢 ACTIVATE VIRTUAL ENVIRONMENT (Do this EVERY time!)
```bash
source venv/bin/activate
```

#### 🟢 START INTERACTIVE MENU (Easiest way!)
```bash
python menu.py
```

#### 🟢 VIEW DATABASE STATISTICS
```bash
python main.py --stats
```

#### 🟢 START WEB DASHBOARD
```bash
python dashboard/app.py
```
Then open browser to: **http://127.0.0.1:5000**

---

## 🔍 SCRAPING COMMANDS (Manual Method)

If you prefer typing commands instead of using the menu:

### Run HUD Scraper (Government Foreclosures)
```bash
python main.py --scraper hud --state CA
```
Change `CA` to your state (NY, TX, FL, etc.)

### Run Foreclosure Scraper
```bash
python main.py --scraper foreclosure --state TX
```

### Run Tax Assessor Scraper
```bash
python main.py --scraper tax_assessor --state NY --county "New York"
```

### Run ALL Scrapers
```bash
python main.py --all
```

---

## 💾 EXPORTING DATA

### Export All Properties to CSV
```bash
python main.py --export all_properties.csv
```

### Export California Properties Only
```bash
python main.py --export ca_properties.csv --state CA
```

### Export High Score Properties (7+)
```bash
python main.py --export high_score.csv --min-score 7
```

**Files are saved to:** `exports/` folder

---

## 🌐 WEB DASHBOARD GUIDE

### Start the Dashboard
```bash
python dashboard/app.py
```

### Open in Browser
Go to: **http://127.0.0.1:5000**

### What You Can Do:
- ✅ Browse all properties visually
- ✅ Filter by state, county, city
- ✅ Filter by abandonment score
- ✅ See property details
- ✅ View statistics

### Stop the Dashboard
Press `Ctrl + C` in the terminal

---

## ⚙️ CONFIGURATION

### Edit Settings
```bash
nano config.yml
```

**Important Settings:**

1. **Google Maps API Key** (Required for geocoding)
```yaml
api_keys:
  google_maps: YOUR_ACTUAL_KEY_HERE
```

2. **Target Locations**
```yaml
target_locations:
  - state: CA
    counties:
      - Los Angeles
      - Orange
```

3. **Rate Limits** (How fast to scrape)
```yaml
scrapers:
  rate_limits:
    default: 10  # Requests per minute
```

### Save Changes in Nano:
- Press `Ctrl + O` (save)
- Press `Enter` (confirm)
- Press `Ctrl + X` (exit)

---

## 🆘 TROUBLESHOOTING

### Problem: "No module named 'requests'"

**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Problem: "config.yml not found"

**Solution:**
```bash
cp config.example.yml config.yml
nano config.yml  # Add your API key
```

### Problem: "Database not found"

**Solution:**
```bash
python main.py --stats
```
This creates the database automatically!

### Problem: Menu looks weird/no colors

**Solution:**
Your terminal doesn't support colors. Use these commands instead:
```bash
python main.py --help
```

---

## 📊 UNDERSTANDING THE OUTPUT

### Abandonment Score (0-10)

- **0-3**: 🟢 Low likelihood (active property)
- **4-6**: 🟡 Medium likelihood (watch list)
- **7-8**: 🟠 High likelihood (good targets)
- **9-10**: 🔴 Very high (prime locations!)

### What Increases the Score:

| Factor | Points |
|--------|--------|
| Tax delinquent 2+ years | +5 |
| In foreclosure | +4 |
| Has code violations | +2 |
| Condemned | +5 |
| No sale in 5+ years | +1 |
| Low value (<$50k) | +1 |

---

## 🎓 USAGE EXAMPLES

### Example 1: Find Abandoned Houses in Los Angeles

```bash
# Step 1: Activate venv
source venv/bin/activate

# Step 2: Run scraper
python main.py --scraper hud --state CA

# Step 3: View results
python dashboard/app.py
# Open: http://127.0.0.1:5000

# Step 4: Filter by city
# In dashboard, type "Los Angeles" in City filter, click Search
```

### Example 2: Export High-Value Targets

```bash
# Step 1: Activate venv
source venv/bin/activate

# Step 2: Export high score properties
python main.py --export targets.csv --min-score 8

# Step 3: Open file
# File is in: exports/targets.csv
```

### Example 3: Check What You've Found

```bash
# Step 1: Activate venv
source venv/bin/activate

# Step 2: View stats
python main.py --stats
```

**Output will look like:**
```
Database Statistics:
══════════════════════════════════════════════

Total properties: 127
Tax delinquent properties: 45
Foreclosed properties: 23
High score properties (7+): 18

Properties by state:
  CA: 89
  TX: 38

Average abandonment score: 5.2
```

---

## 🎨 COLOR GUIDE

When you see these colors in the interactive menu:

- 🟢 **Green** = Success / Available / Good to go
- 🔵 **Blue** = Information / Sections
- 🟡 **Yellow** = Warning / Input needed
- 🔴 **Red** = Error / Problem
- 🟣 **Purple** = Headers / Titles

---

## 🚦 WORKFLOW DIAGRAM

```
┌─────────────────────┐
│  Install & Setup    │
│  (One time only)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Activate venv      │
│  (Every session)    │
│  source venv/bin/   │
│  activate           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Start Menu         │
│  python menu.py     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Choose Option:     │
│  1. Quick Start     │
│  2. Run Scraper     │
│  3. View Stats      │
│  4. Dashboard       │
│  etc.               │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  View Results in    │
│  Dashboard          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Export Data        │
│  (Optional)         │
└─────────────────────┘
```

---

## 💡 PRO TIPS

### Tip 1: Use Tab Completion
When typing file names, press `Tab` to auto-complete!

### Tip 2: Copy Commands
Right-click in terminal to paste commands from this guide.

### Tip 3: Keep Dashboard Open
Start dashboard in one terminal, run scrapers in another!

### Tip 4: Check Logs
If something breaks:
```bash
tail -f logs/scraper.log
```

### Tip 5: Start Small
Test with one state/county first before running everything!

---

## 📱 QUICK REFERENCE CARD

```
╔═══════════════════════════════════════════════════════════╗
║                    QUICK REFERENCE                        ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  START:        python menu.py                            ║
║  ACTIVATE:     source venv/bin/activate                  ║
║  STATS:        python main.py --stats                    ║
║  DASHBOARD:    python dashboard/app.py                   ║
║  SCRAPE:       python main.py --scraper hud --state CA   ║
║  EXPORT:       python main.py --export data.csv          ║
║  CONFIG:       nano config.yml                           ║
║  HELP:         python main.py --help                     ║
║                                                           ║
║  STOP PROGRAM: Ctrl + C                                  ║
║  EXIT MENU:    Type '9' then Enter                       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 🎯 YOUR FIRST SESSION (Step-by-Step)

### Copy and paste these commands one by one:

```bash
# 1. Go to project folder
cd /mnt/c/Users/Pedro/urbex-property-scraper

# 2. Activate virtual environment
source venv/bin/activate

# 3. Start interactive menu
python menu.py
```

### Then in the menu:
1. Type `1` and press Enter (Quick Start)
2. Type `y` and press Enter (Yes, start scraping)
3. Wait for scraping to complete
4. Type `y` and press Enter (Yes, open dashboard)
5. Open browser to http://127.0.0.1:5000
6. Browse your properties! 🎉

---

## 🏆 YOU'RE READY!

You now have:
- ✅ Interactive menu system
- ✅ Beautiful web dashboard
- ✅ Easy-to-use commands
- ✅ Visual guides

**Have fun finding abandoned properties!** 🏚️🔍

Questions? Check:
- **SETUP.md** - Installation help
- **GETTING_STARTED.md** - Usage guide
- **QUICK_START.md** - Fast reference

Or use the interactive menu: `python menu.py` → Option 7 (Help)
