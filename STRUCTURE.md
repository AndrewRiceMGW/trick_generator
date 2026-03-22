# 🗺️ Project Structure Guide

## Current File Organization

```
trick_generator/
│
├── 📄 index.html                    # ⭐ Main sport selection screen (NEW!)
├── 📄 sports-config.json            # Sport metadata and configuration
├── 📄 manifest.json                 # PWA configuration (updated)
├── 🔧 start-server.sh               # Quick server launcher
├── 📖 README.md                     # Multi-sport documentation
│
├── 📁 sports/                       # ⭐ Sport modules folder (NEW!)
│   │
│   └── 📁 rollerblading/            # Aggressive inline module
│       ├── 📄 app.html              # Rollerblading trick generator UI
│       ├── 📄 schema.json           # Complete trick database (11+ grinds, spins, etc.)
│       └── 📄 generator.js          # Smart generation engine
│
├── 📁 [Future Sports]/              # Coming soon!
│   ├── 📁 skateboarding/
│   ├── 📁 bmx/
│   ├── 📁 scooter/
│   ├── 📁 snowboarding/
│   └── 📁 surfing/
│
└── 📁 [Backup Files]/               # Old versions (can be deleted)
    ├── index-old-rollerblading.html
    ├── trick-generator.js           # (now in sports/rollerblading/)
    ├── trick-schema.json            # (now in sports/rollerblading/)
    └── README-OLD.md
```

## 🎯 How Navigation Works

1. **User visits:** `index.html`
   - Sees sport selection grid
   - Clicks "Aggressive Inline" card

2. **Navigates to:** `sports/rollerblading/app.html`
   - Full trick generator loads
   - Can generate tricks immediately

3. **Click "Back to Sports"**
   - Returns to `index.html`
   - Can choose different sport

## 🔧 Adding a New Sport (Step-by-Step)

### Step 1: Create Folder

```bash
mkdir -p sports/YOUR_SPORT
```

### Step 2: Copy Template

```bash
cp sports/rollerblading/app.html sports/YOUR_SPORT/
cp sports/rollerblading/generator.js sports/YOUR_SPORT/
```

### Step 3: Create Schema

Create `sports/YOUR_SPORT/schema.json` with your sport's tricks, obstacles, and rules.

### Step 4: Register Sport

Add to `sports-config.json`:

```json
"your_sport": {
  "id": "your_sport",
  "name": "Your Sport",
  "emoji": "🎸",
  "status": "active",
  "description": "Your sport description",
  "schema_file": "sports/your_sport/schema.json",
  "generator_file": "sports/your_sport/generator.js",
  "app_page": "sports/your_sport/app.html",
  "color_primary": "#667eea",
  "color_secondary": "#764ba2",
  "categories": ["category1", "category2"]
}
```

### Step 5: Customize

- Edit `app.html` for UI
- Edit `generator.js` for logic
- Fill `schema.json` with tricks

### Step 6: Test

```bash
./start-server.sh
# Open http://localhost:8000
```

Your sport appears automatically!

## 📦 What Each File Does

### Core Files

| File                 | Purpose                | Edits Needed                    |
| -------------------- | ---------------------- | ------------------------------- |
| `index.html`         | Sport selection screen | Rarely (auto-loads from config) |
| `sports-config.json` | Sport metadata         | Add new sports here             |
| `manifest.json`      | PWA settings           | Update app name/colors          |
| `start-server.sh`    | Development server     | Never                           |

### Sport Files (per sport)

| File           | Purpose            | Sport Specific                |
| -------------- | ------------------ | ----------------------------- |
| `app.html`     | Trick generator UI | ✅ Yes - customize per sport  |
| `schema.json`  | Trick database     | ✅ Yes - completely different |
| `generator.js` | Generation logic   | ✅ Yes - sport rules          |

## 🎨 Theming a Sport

Each sport in `sports-config.json` has:

```json
"color_primary": "#667eea",    // Main color
"color_secondary": "#764ba2",  // Accent color
```

These automatically:

- Style the sport card on selection screen
- Don't affect individual sport pages (edit `app.html` for that)

## 🔍 Troubleshooting

### "Sport won't show on home screen"

✅ Check `sports-config.json` syntax (valid JSON?)
✅ Verify `"status": "active"` is set
✅ Refresh browser (Ctrl+F5)

### "Trick generator won't load"

✅ Check browser console (F12)
✅ Verify all 3 files exist: app.html, schema.json, generator.js
✅ Check file paths in sports-config.json

### "Back button doesn't work"

✅ Verify relative path in app.html: `href="../../index.html"`
✅ Check you're not opening files directly (use web server!)

## 🚀 Quick Commands

```bash
# Start server
./start-server.sh

# Create new sport
mkdir -p sports/bmx

# List sports
ls sports/

# Test specific sport
# Open: http://localhost:8000/sports/rollerblading/app.html

# View app structure
tree -L 3
```

## 📱 Mobile Installation

Once you've added multiple sports, the PWA installs as a single app with:

- Sport selection as home screen
- Each sport as a separate "page"
- Works offline after first load
- Updates automatically (if hosted online)

## 🎯 Benefits of This Structure

✅ **Modular** - Add sports without touching existing ones
✅ **Scalable** - Can have 20+ sports independently
✅ **Maintainable** - Each sport is self-contained
✅ **Collaborative** - Multiple people can work on different sports
✅ **Clean** - No sport-specific code in main index

## 📊 Current Status

| Sport                | Status         | Files Complete |
| -------------------- | -------------- | -------------- |
| 🛼 Aggressive Inline | ✅ Active      | 3/3            |
| 🛹 Skateboarding     | 🚧 Coming Soon | 0/3            |
| 🚲 BMX               | 🚧 Coming Soon | 0/3            |
| 🛴 Scooter           | 🚧 Coming Soon | 0/3            |
| 🏂 Snowboarding      | 🚧 Coming Soon | 0/3            |
| 🏄 Surfing           | 🚧 Coming Soon | 0/3            |

## 🎓 Next Steps

1. **Test the app:** Open http://localhost:8000
2. **Click Aggressive Inline:** Try generating tricks
3. **Click Back button:** Return to sport selection
4. **Plan next sport:** Choose skateboarding, BMX, or scooter
5. **Copy template:** Use rollerblading as base
6. **Customize:** Adapt rules to new sport

Ready to add your next sport? 🚀
