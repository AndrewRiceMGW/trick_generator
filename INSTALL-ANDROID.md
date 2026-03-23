# Installing Trick Generator BETA on Android

This guide will help you install the Trick Generator as a Progressive Web App (PWA) on your Android device.

## Prerequisites

- Android device with Chrome, Edge, or Samsung Internet browser
- Your computer and phone on the same WiFi network (for local installation)
- OR deploy to a hosting service for internet access

---

## Option 1: Install via Local Network (Easiest for Testing)

### Step 1: Start the Server on Your Computer

```bash
cd /home/andrew/Documents/trick_generator
python3 -m http.server 8000
```

### Step 2: Find Your Computer's IP Address

```bash
# On Linux
hostname -I | awk '{print $1}'

# Or check your network settings
ip addr show | grep "inet " | grep -v 127.0.0.1
```

Example output: `192.168.1.100`

### Step 3: Access from Your Android Phone

1. Open Chrome on your Android device
2. Make sure you're on the same WiFi network as your computer
3. In the URL bar, type: `http://YOUR-IP-ADDRESS:8000`
   - Example: `http://192.168.1.100:8000`
4. The app should load!

### Step 4: Install as App

1. Tap the **three dots menu** (⋮) in the top right corner
2. Select **"Add to Home screen"** or **"Install app"**
3. Name it "Tricks BETA" (or whatever you prefer)
4. Tap **"Add"**
5. The app icon will appear on your home screen!

### Step 5: Use the App

- Tap the icon on your home screen to launch
- Works even when disconnected from your computer (cached offline!)
- Feels like a native Android app

---

## Option 2: Deploy Online (Access from Anywhere)

For permanent access without needing your computer running, deploy to a free hosting service:

### Using GitHub Pages (Free)

1. **Create a GitHub account** (if you don't have one): https://github.com

2. **Install git** (if not already installed):

   ```bash
   sudo apt install git
   ```

3. **Initialize and push your project**:

   ```bash
   cd /home/andrew/Documents/trick_generator
   git init
   git add .
   git commit -m "Initial commit - Trick Generator BETA v0.9.0"

   # Create a new repository on GitHub (name it "trick-generator")
   # Then run:
   git remote add origin https://github.com/YOUR-USERNAME/trick-generator.git
   git branch -M main
   git push -u origin main
   ```

4. **Enable GitHub Pages**:
   - Go to your repository on GitHub
   - Click **Settings** → **Pages**
   - Under "Source", select **main** branch
   - Click **Save**
   - Your site will be live at: `https://YOUR-USERNAME.github.io/trick-generator/`

5. **Install on Android**:
   - Open Chrome on your phone
   - Visit your GitHub Pages URL
   - Follow the "Install as App" steps from Option 1

### Using Netlify (Free, Easier)

1. **Create account**: https://netlify.com
2. **Drag and drop** your `trick_generator` folder onto Netlify
3. Your site is live instantly!
4. Install on Android using the provided URL

---

## Troubleshooting

### Can't access from phone (Option 1)

- **Check WiFi**: Both devices must be on the same network
- **Firewall**: Disable firewall temporarily or allow port 8000
  ```bash
  sudo ufw allow 8000
  ```
- **Wrong IP**: Double-check your computer's IP address

### "Add to Home screen" option missing

- **HTTPS required**: Some browsers need HTTPS. Use Option 2 (deploy online)
- **Browser compatibility**: Use Chrome, Edge, or Samsung Internet (not Firefox)

### App doesn't work offline

- Service worker needs time to cache. Visit all pages once while online.
- Check browser console for errors (Chrome DevTools)

### Icons are missing

- The app works without icons! They're optional.
- To add custom icons, see `ICONS.md`

---

## BETA Version Notes

This is version **0.9.0-beta**. Current features:

- ✅ Rollerblading trick generator with full physics-based constraints
- ✅ Obstacle-first workflow
- ✅ User-controlled switch-ups
- ✅ Position-aware difficulty calculations
- ✅ Spin direction support (alley-oop vs true spin)
- ✅ Topside/negative body positions
- ✅ PWA installation on Android

Coming soon:

- 🔄 5 additional sports (skateboarding, BMX, scooter, snowboarding, surfing)
- 🔄 Session tracking and favorites
- 🔄 Share tricks with friends

---

## Quick Commands

**Start server:**

```bash
cd /home/andrew/Documents/trick_generator && python3 -m http.server 8000
```

**Find your IP:**

```bash
hostname -I | awk '{print $1}'
```

**Stop server:**
Press `Ctrl+C` in the terminal

---

## Support

If you encounter issues:

1. Check the browser console for errors (F12 in Chrome)
2. Verify your phone and computer are on the same WiFi
3. Try using Chrome instead of other browsers
4. Clear browser cache and try again

Enjoy skating! 🛼
