# Install Trick Generator on Android via USB

This guide will help you install the app on your Android phone using a USB cable.

---

## Method 1: Port Forwarding via ADB (Recommended)

This method lets your phone access your computer's local server through USB.

### Step 1: Enable Developer Options on Your Android Phone

1. Open **Settings** on your Android phone
2. Go to **About phone** (usually at the bottom)
3. Find **Build number** and tap it **7 times**
4. You'll see "You are now a developer!"

### Step 2: Enable USB Debugging

1. Go back to **Settings**
2. Go to **System** → **Developer options** (or just **Developer options**)
3. Toggle on **USB debugging**
4. Confirm when prompted

### Step 3: Install ADB on Your Computer

Run these commands:

```bash
# Install ADB tools
sudo apt update
sudo apt install android-tools-adb android-tools-fastboot -y

# Verify installation
adb --version
```

### Step 4: Connect Your Phone via USB

1. **Connect** your Android phone to your computer with USB cable
2. **On your phone**, you'll see a prompt "Allow USB debugging?"
   - Check "Always allow from this computer"
   - Tap **"OK"**

3. **Verify connection** on your computer:

```bash
adb devices
```

You should see your device listed like:

```
List of devices attached
ABC123XYZ    device
```

If you see "unauthorized", check your phone for the USB debugging prompt.

### Step 5: Make Sure the Server is Running

```bash
cd /home/andrew/Documents/trick_generator
python3 -m http.server 8000
```

Leave this terminal open!

### Step 6: Forward the Port to Your Phone

Open a **new terminal** and run:

```bash
adb reverse tcp:8000 tcp:8000
```

This makes your computer's port 8000 accessible as `localhost:8000` on your phone!

### Step 7: Open the App on Your Phone

**Option A: Open Chrome automatically via ADB**

```bash
adb shell am start -a android.intent.action.VIEW -d "http://localhost:8000"
```

**Option B: Open Chrome manually**

1. Open **Chrome** on your phone
2. Type in the address bar: `localhost:8000`
3. Press Enter

The app should load! 🎉

### Step 8: Install as PWA

1. In Chrome, tap the **three dots menu** (⋮)
2. Select **"Add to Home screen"** or **"Install app"**
3. Name it "Tricks BETA"
4. Tap **"Add"**
5. The app icon appears on your home screen!

### Step 9: Disconnect and Enjoy

Once installed, the app works offline! You can:

- Disconnect USB
- Close the server on your computer
- Use the app anytime from your home screen

---

## Method 2: Simple File Transfer (Alternative)

If you don't want to use ADB, you can access the online version:

### Option A: Use GitHub Pages (Coming Soon)

Enable GitHub Pages on your repository, then:

1. Visit `https://andrewricemgw.github.io/trick_generator/` on your phone
2. Install as PWA (see Step 8 above)

### Option B: Use Local Network

1. Make sure both devices are on the same WiFi
2. On your phone's Chrome, visit: `http://192.168.1.72:8000`
3. Install as PWA

---

## Troubleshooting

### "adb: command not found"

Install ADB tools:

```bash
sudo apt install android-tools-adb android-tools-fastboot
```

### "no devices/emulators found"

- Check USB cable is connected
- Enable USB Debugging on phone
- Accept the "Allow USB debugging" prompt on phone
- Try different USB port
- Check USB mode is not "Charging only" (change to "File Transfer" in notification)

### "device unauthorized"

- Check your phone for the USB debugging authorization prompt
- Unplug and replug the USB cable
- Revoke authorizations: Settings → Developer Options → Revoke USB debugging authorizations

### "adb reverse" not working

- Make sure your phone is Android 5.0+ (Lollipop or newer)
- Try `adb kill-server` then `adb start-server`
- Reconnect your phone

### Port forwarding stops working

If you disconnect USB or restart your phone, you need to run the reverse command again:

```bash
adb reverse tcp:8000 tcp:8000
```

### Can't access localhost:8000 on phone

- Verify port forwarding: `adb reverse --list`
- Make sure server is running on computer
- Try opening `http://127.0.0.1:8000` instead

---

## Quick Command Reference

**Check connection:**

```bash
adb devices
```

**Forward port:**

```bash
adb reverse tcp:8000 tcp:8000
```

**Open app on phone:**

```bash
adb shell am start -a android.intent.action.VIEW -d "http://localhost:8000"
```

**Remove port forwarding:**

```bash
adb reverse --remove tcp:8000
```

**Kill ADB server (if issues):**

```bash
adb kill-server
adb start-server
```

---

## Why This Method?

✅ **Pros:**

- Works without WiFi
- Direct USB connection is fast
- Server stays on your computer
- Easy to test changes

❌ **Cons:**

- Requires USB cable
- Need to set up ADB first
- Port forwarding needed each connection

**For permanent access**: Use GitHub Pages instead! (See INSTALL-ANDROID.md)

---

## Next Steps After Installation

Once the app is installed on your home screen:

1. ✅ Works offline after first load
2. ✅ Updates automatically when you visit while online
3. ✅ Feels like a native Android app
4. ✅ Can share tricks (coming soon)

Happy skating! 🛼
