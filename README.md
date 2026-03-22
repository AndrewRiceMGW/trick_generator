# 🔥 Extreme Trick Generator (Multi-Sport)

A comprehensive trick generator for extreme sports with sport-specific rules, terminology, and physical constraints. Each sport has its own unique generation system that creates valid, realistic trick combinations.

## 🎯 Supported Sports

### ✅ Active Sports
- **🛼 Aggressive Inline** - Full support with grinds, spins, switch-ups, and more

### 🚧 Coming Soon
- **🛹 Skateboarding** - Flip tricks, grinds, manuals, transitions
- **🚲 BMX** - Grinds, spins, barspins, tailwhips
- **🛴 Scooter** - Whips, grinds, spins, manuals
- **🏂 Snowboarding** - Spins, flips, rail/box tricks
- **🏄 Surfing** - Turns, aerials, barrels, cutbacks

## 📱 Quick Start

### Test Locally

```bash
cd /home/andrew/Documents/trick_generator
./start-server.sh
```

Open **http://localhost:8000** in your browser!

### Select Your Sport

1. Choose from the sport cards on the main screen
2. Each sport has its own dedicated trick generator
3. Navigate back to switch sports

## 🗂️ Project Structure

```
trick_generator/
├── index.html              # Main sport selection screen
├── sports-config.json      # Sports metadata and configuration
├── manifest.json           # PWA configuration
├── start-server.sh         # Quick start script
│
├── sports/
│   └── rollerblading/      # Aggressive inline module
│       ├── app.html        # Rollerblading trick generator UI
│       ├── schema.json     # Complete trick database
│       └── generator.js    # Generation logic
│
└── [skateboarding/]        # Future sport modules
    [bmx/]
    [scooter/]
    etc...
```

## 🎮 Current Features (Rollerblading)

### Generation Modes
- **Random** - Generate any valid trick
- **Obstacle** - Specific obstacles (rail, ledge, curb, stairs)
- **Difficulty** - Filter by skill level (Beginner → Insane)
- **Combo** - Generate 3-10 trick sequences

### Smart Rules
- ✅ Valid switch-up combinations only
- ✅ Obstacle length affects complexity
- ✅ Proper naming (Cab, Half Cab, Alley-Oop)
- ✅ Difficulty scoring system
- ✅ Stance tracking (Forward/Fakie/Switch)
- ✅ Entry/exit spins with proper rotations

### Trick Components
- **Stances:** Forward, Fakie, Switch
- **Entry/Exit Spins:** 180°, 270°, 360°, 450°, 540°, 720°
- **Grinds:** Soul, Mizou, Frontside, Backslide, Royale, Pornstar, Unity, etc.
- **Switch-ups:** Based on obstacle length (short = 0, long = 2-3)
- **Modifiers:** Topside, True Topside, Negative, Makio
- **Grabs:** Mute, Rocket, Japan, Stalefish (for airs)
- **Flips:** 540 Flip, 720 Flip, Misty, Bio (optional)

## 🏗️ Adding a New Sport

### 1. Create Sport Folder Structure

```bash
mkdir -p sports/YOUR_SPORT
```

### 2. Add to sports-config.json

```json
"your_sport": {
  "id": "your_sport",
  "name": "Your Sport Name",
  "emoji": "🎸",
  "status": "active",
  "description": "Brief description",
  "schema_file": "sports/your_sport/schema.json",
  "generator_file": "sports/your_sport/generator.js",
  "app_page": "sports/your_sport/app.html",
  "color_primary": "#hex",
  "color_secondary": "#hex",
  "categories": ["trick_type_1", "trick_type_2"]
}
```

### 3. Create Sport-Specific Files

**schema.json** - Define your tricks, obstacles, rules
**generator.js** - Implement generation logic
**app.html** - Build the UI (can copy from rollerblading template)

### 4. Test and Deploy

The sport will automatically appear on the main selection screen!

## 📱 Package for Android

### Method 1: PWA (Easiest)

1. Host online (GitHub Pages, Netlify, Vercel)
2. Open in Chrome on Android
3. Tap "Install App"
4. Works offline!

### Method 2: Capacitor (Full APK)

```bash
npm install -g @capacitor/cli
npx cap init
npx cap add android
npx cap open android
# Build APK in Android Studio
```

### Method 3: Cordova

```bash
npm install -g cordova
cordova create ExtremeGen com.extremegen.app "Extreme Tricks"
cd ExtremeGen
# Copy files to www/
cordova platform add android
cordova build android
```

See full Android packaging instructions in the original README.

## 🎨 Customization

### Change Sport Colors

Edit `sports-config.json`:
```json
"color_primary": "#YOUR_COLOR",
"color_secondary": "#YOUR_COLOR"
```

### Modify Trick Rules

Each sport's `schema.json` contains:
- All available tricks
- Valid combinations
- Difficulty values
- Obstacle constraints
- Naming rules

### UI Customization

Edit the sport's `app.html` file to modify:
- Layout and styling
- Mode options
- Display format

## 🧪 Development Workflow

1. **Start server:** `./start-server.sh`
2. **Make changes** to sport files
3. **Refresh browser** to test
4. **No build step needed!** Pure HTML/JS

## 📊 Difficulty System (Example: Rollerblading)

**Calculation:**
- Stance (1-2 points)
- Entry Spin (0-3.5 points)
- Primary Grind (1-3.5 points)
- Switch-ups (+grind difficulty + 1 per switch)
- Modifiers (1.5-2.5 points)
- Exit Spin (0-4.5 points)
- Obstacle multiplier (1.0-1.6x)

**Levels:**
- Beginner: 0-5
- Intermediate: 5-10
- Advanced: 10-15
- Pro: 15-25
- Insane: 25+

Each sport can define its own difficulty system!

## 🐛 Troubleshooting

### Sport won't load
- Check browser console (F12) for errors
- Verify sport paths in `sports-config.json`
- Ensure all three files exist: schema.json, generator.js, app.html

### Tricks seem invalid
- Review sport's `schema.json` for rule errors
- Check `switch_up_to` arrays for valid combinations
- Verify obstacle constraints

### App won't install on Android
- Enable "Install unknown apps" in Android settings
- Check that manifest.json is valid
- Ensure PWA requirements are met (HTTPS when hosted)

## 🚀 Roadmap

### v2.0 (Current)
- ✅ Sport selection screen
- ✅ Aggressive inline complete
- ✅ Multi-sport architecture

### v2.1
- [ ] Skateboarding support
- [ ] Street and park obstacles
- [ ] Flip trick combinations

### v2.2
- [ ] BMX support
- [ ] Barspin/tailwhip logic
- [ ] Peg grinds

### v2.3
- [ ] Scooter support
- [ ] Whip variations
- [ ] Deck grabs

### v3.0
- [ ] Cross-sport session mode
- [ ] Save favorite tricks
- [ ] Share tricks (screenshot/text)
- [ ] Video examples integration
- [ ] Offline mode improvements

## 🤝 Contributing

Want to add a sport or improve existing ones?

1. Fork the repo
2. Create sport folder and files
3. Add to `sports-config.json`
4. Test locally
5. Submit pull request!

### Sport Contribution Guidelines

- **Schema:** Must include comprehensive trick database
- **Rules:** Implement sport-specific constraints
- **Naming:** Use authentic terminology
- **Testing:** Verify trick combinations make sense
- **Documentation:** Comment complex logic

## 💡 Tips

- **Quick testing:** Use the built-in Python server
- **Sport dev:** Copy rollerblading folder as template
- **APK building:** Capacitor is most flexible
- **Updates:** PWA auto-updates when you push changes!
- **Performance:** Keep schema files under 500KB

## 📖 Sport-Specific READMEs

Each sport module can have its own README:
- `sports/rollerblading/README.md`
- `sports/skateboarding/README.md`
- etc.

## 🎯 Design Philosophy

1. **Authenticity** - Use real terminology
2. **Validity** - Only generate possible tricks
3. **Progression** - Difficulty should make sense
4. **Extensibility** - Easy to add new sports
5. **Simplicity** - No complex build process

## 📝 License

Free to use, modify, and distribute. Built for the extreme sports community.

---

## 🆘 Support

Questions? Issues? Ideas?

1. Check browser console for errors
2. Review sport schema files
3. Test with simple tricks first
4. Open an issue with details

---

Built with ❤️ for the extreme sports community 🔥

**Currently active:** 1 sport  
**In development:** 5+ sports  
**Community driven:** Open for contributions!
