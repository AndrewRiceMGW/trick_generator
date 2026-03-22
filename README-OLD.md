# 🛼 Aggressive Inline Trick Generator

A smart trick generator for aggressive inline skating that creates valid, realistic trick combinations based on obstacle types, difficulty levels, and proper trick sequencing rules.

## 🎯 Features

- **Multiple Modes:**
  - **Random:** Generate any trick with customizable options
  - **Obstacle:** Choose specific obstacles (rail, ledge, curb, stairs)
  - **Difficulty:** Generate tricks within specific skill levels (Beginner → Insane)
  - **Combo:** Create sequences of multiple tricks

- **Smart Generation:**
  - Rule-based trick combinations (only valid switch-ups)
  - Obstacle-aware (rail length affects switch-ups)
  - Proper naming (Cab, Half Cab, Alley-Oop, etc.)
  - Difficulty scoring system

- **Trick Components:**
  - Stances (Forward, Fakie, Switch)
  - Entry/Exit spins (180°, 270°, 360°, etc.)
  - Grinds (Soul, Mizou, Frontside, Royale, etc.)
  - Switch-ups (based on obstacle length)
  - Modifiers (Topside, Negative, True Topside, etc.)
  - Grabs (for air tricks)
  - Flips (optional, for advanced tricks)

## 📁 Files

- `index.html` - Main app interface
- `trick-generator.js` - Core generation logic
- `trick-schema.json` - Complete trick database and rules

## 🚀 Quick Start (Test Locally)

### Option 1: Simple HTTP Server (Python)

```bash
# Navigate to the project folder
cd /home/andrew/Documents/trick_generator

# Python 3
python3 -m http.server 8000

# Python 2
python -m SimpleHTTPServer 8000
```

Then open your browser to: **http://localhost:8000**

### Option 2: Node.js HTTP Server

```bash
# Install http-server globally (one time)
npm install -g http-server

# Run server
cd /home/andrew/Documents/trick_generator
http-server -p 8000
```

Then open: **http://localhost:8000**

### Option 3: VS Code Live Server

1. Install "Live Server" extension in VS Code
2. Right-click on `index.html`
3. Select "Open with Live Server"

## 📱 Package for Android (Multiple Methods)

### Method 1: PWA + TWA (Simplest, No APK Build)

**What is it:** Turn your web app into an installable PWA (Progressive Web App) that works like a native app.

#### Step 1: Add PWA files

Create `manifest.json`:

```json
{
  "name": "Aggressive Inline Trick Generator",
  "short_name": "Trick Gen",
  "description": "Generate aggressive inline skating tricks",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#667eea",
  "theme_color": "#667eea",
  "icons": [
    {
      "src": "icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

Add to `<head>` in `index.html`:
```html
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#667eea">
```

#### Step 2: Host it online

Upload to:
- **GitHub Pages** (free)
- **Netlify** (free)
- **Vercel** (free)

#### Step 3: Install on Android

1. Open the hosted URL in Chrome on Android
2. Tap the menu (⋮) → "Install app" or "Add to Home Screen"
3. The app installs like a native app!

**No APK needed!** Works offline after first load.

---

### Method 2: Capacitor (Full Native APK)

**What is it:** Converts web apps to native Android/iOS apps.

#### Setup

```bash
# Install Capacitor
npm install -g @capacitor/cli @capacitor/core

# Initialize (in your project folder)
cd /home/andrew/Documents/trick_generator
npm init -y
npm install @capacitor/core @capacitor/cli
npx cap init

# Follow prompts:
# App name: Aggressive Inline Trick Generator
# Package ID: com.tricksgen.app
# Web asset directory: . (current directory)

# Add Android platform
npm install @capacitor/android
npx cap add android
```

#### Build APK

```bash
# Copy web files to native project
npx cap copy android

# Open in Android Studio
npx cap open android
```

In Android Studio:
1. Let it sync/download dependencies
2. Go to **Build** → **Build Bundle(s) / APK(s)** → **Build APK(s)**
3. APK will be in: `android/app/build/outputs/apk/debug/app-debug.apk`

#### Transfer to Phone

**Option A - USB:**
```bash
adb install android/app/build/outputs/apk/debug/app-debug.apk
```

**Option B - Manual:**
1. Copy `app-debug.apk` to phone (USB, Google Drive, email, etc.)
2. Tap the APK file on phone
3. Enable "Install unknown apps" when prompted
4. Install!

---

### Method 3: Cordova (Alternative to Capacitor)

```bash
# Install Cordova
npm install -g cordova

# Create project
cordova create TrickGen com.tricksgen.app "Trick Generator"
cd TrickGen

# Copy your files to www/ folder
cp /home/andrew/Documents/trick_generator/*.{html,js,json} www/

# Add Android platform
cordova platform add android

# Build APK
cordova build android
```

APK location: `platforms/android/app/build/outputs/apk/debug/app-debug.apk`

---

### Method 4: Android Studio (Full Native Development)

**For advanced users:** Build a native Kotlin/Java app with WebView.

1. Create new Android Studio project
2. Add WebView to MainActivity
3. Load your HTML files from assets
4. Build APK

---

## 🔧 Installation on Android Phone

### Enable Unknown Apps

1. Go to **Settings** → **Security** (or **Apps**)
2. Find **Install unknown apps**
3. Select your file manager or browser
4. Toggle **Allow from this source**

### Install APK

**Method 1: From Computer (ADB)**
```bash
# Enable USB Debugging on phone first
# Settings → About Phone → tap Build Number 7 times
# Settings → Developer Options → USB Debugging ON

# Install via ADB
adb install app-debug.apk
```

**Method 2: From File Manager**
1. Transfer APK to phone storage
2. Open file manager
3. Tap the APK file
4. Follow installation prompts

**Method 3: From Cloud**
1. Upload APK to Google Drive
2. Download on phone
3. Tap to install

---

## 🎮 How to Use the App

### Random Mode
1. Select obstacle type (or "Any")
2. Choose obstacle length
3. Toggle switch-ups and flips
4. Tap "Generate Trick"

### Difficulty Mode
1. Select difficulty level
2. Choose number of tricks to generate
3. Tap "Generate Trick"
4. App filters tricks within difficulty range

### Combo Mode
1. Select combo size (3, 5, or 10 tricks)
2. Tap "Generate Trick"
3. Get a full line/run sequence

### Obstacle Mode
Same as Random, but focused on specific obstacles

---

## 🛠️ Customization

### Add New Tricks

Edit `trick-schema.json`:

```json
"grinds": {
  "new_grind": {
    "id": "new_grind",
    "name": "My New Grind",
    "difficulty": 2.5,
    "soul_based": false,
    "switch_up_to": ["soul", "frontside"]
  }
}
```

### Adjust Difficulty

Modify difficulty values in schema (higher = harder):
- Grinds: 1-4
- Spins: 1.5-4.5
- Modifiers: 1.5-3

### Change Colors/Style

Edit the `<style>` section in `index.html`:
- Background: `background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);`
- Colors: Change hex codes throughout

---

## 📊 Difficulty System

Tricks are scored based on:
- **Stance** (Forward: 1, Fakie: 1.5, Switch: 2)
- **Entry Spin** (0-3.5 points)
- **Primary Grind** (1-3.5 points)
- **Switch-ups** (+grind difficulty + 1 per switch)
- **Modifiers** (1.5-2.5 points)
- **Exit Spin** (0-4.5 points)
- **Obstacle Multiplier** (based on length/type)

**Levels:**
- Beginner: 0-5
- Intermediate: 5-10
- Advanced: 10-15
- Pro: 15-25
- Insane: 25+

---

## 🐛 Troubleshooting

### App won't load locally
- Make sure you're using a web server (not just opening HTML file)
- Check browser console for errors (F12)

### JSON fails to load
- Ensure all three files are in the same folder
- Check for JSON syntax errors

### APK won't install
- Enable "Install unknown apps" for your file manager
- Check phone storage (need ~20MB free)

### Capacitor/Cordova errors
- Install Android Studio first
- Set ANDROID_HOME environment variable
- Install Java JDK 11+

---

## 🎯 Future Enhancements

Ideas for v2:
- [ ] Save favorite tricks
- [ ] Share tricks (screenshot/text)
- [ ] Session mode (track tricks you've landed)
- [ ] Video examples
- [ ] Custom trick builder
- [ ] Offline mode (already works with PWA!)
- [ ] Dark/light theme toggle

---

## 📝 License

Free to use, modify, and distribute. Built for skaters, by skaters.

---

## 🤝 Contributing

Want to add tricks or improve the logic?

1. Edit `trick-schema.json` for new tricks
2. Modify `trick-generator.js` for logic changes
3. Update `index.html` for UI improvements

Pull requests welcome!

---

## 💡 Tips

- **For quick testing:** Use PWA method (Method 1)
- **For distribution:** Build APK with Capacitor (Method 2)
- **For App Store:** Use Capacitor to build iOS version too
- **For updates:** Rebuild APK and reinstall (or use PWA for auto-updates!)

---

Built with ❤️ for the aggressive inline community 🛼
