# Aggressive Inline Trick Generator - Integration Guide

## Overview

The trick generator web app now uses the new graph-based Python implementation with weighted sample pool approach. This provides much better difficulty distribution and prevents combos from being unreasonably hard.

## Architecture

```
┌─────────────────────┐
│   Web Frontend      │  sports/rollerblading/app.html
│   (HTML/JS)         │  - User interface
└──────────┬──────────┘  - Obstacle selection
           │             - Difficulty settings
           │ REST API
           ↓
┌─────────────────────┐
│   Flask Backend     │  sports/trick_api.py
│   (Python)          │  - REST API endpoint
└──────────┬──────────┘  - Parameter validation
           │
           ↓
┌─────────────────────┐
│ Graph Generator     │  sports/graph_generation_api.py
│ (Python)            │  - NetworkX graph-based logic
└─────────────────────┘  - Weighted sample pool approach
                         - Difficulty bands
```

## Quick Start

### Option 1: Using the startup script (Recommended)

```bash
./start.sh
```

This will:

1. Create a virtual environment (if needed)
2. Install dependencies
3. Start the Flask API on http://localhost:5000

Then open `sports/rollerblading/app.html` in your browser.

### Option 2: Manual setup

1. **Install dependencies:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Start the Flask API:**

   ```bash
   cd sports
   python3 trick_api.py
   ```

   The API will run on http://localhost:5000

3. **Open the web app:**
   - Open `sports/rollerblading/app.html` in your browser
   - OR serve it with a local web server:
     ```bash
     python3 -m http.server 8000
     ```
     Then visit http://localhost:8000/sports/rollerblading/app.html

## API Endpoints

### POST /api/generate

Generate a trick combo.

**Request:**

```json
{
  "difficulty": "beginner|intermediate|advanced|pro|insane",
  "numSwitchUps": 0-3,
  "obstacle": "rail|ledge|..." (optional),
  "obstacleLength": "short|medium|long" (optional)
}
```

**Response:**

```json
{
	"success": true,
	"trick": {
		"name": "Fakie Switch 180 Inspin Negative Mizou to 360 Fishbrain",
		"difficulty": 4.5,
		"components": [
			{ "trick": "Negative Mizou", "difficulty": 1.75 },
			{ "trick": "360 Fishbrain", "difficulty": 2.15 }
		],
		"totalDifficulty": 4.5,
		"individualDifficulties": [1.75, 2.15],
		"numSwitchUps": 2,
		"difficultyLevel": "advanced"
	}
}
```

### GET /api/health

Health check endpoint.

**Response:**

```json
{
	"status": "ok"
}
```

## How It Works

### Difficulty System

The new system uses **difficulty bands** with wider, overlapping ranges:

| Level        | Range   | Multiplier |
| ------------ | ------- | ---------- |
| Beginner     | 0-50%   | 8.0        |
| Intermediate | 35-70%  | 12.0       |
| Advanced     | 55-85%  | 25.0       |
| Pro          | 65-95%  | 50.0       |
| Insane       | 90-100% | 5.0        |

### Weighted Sample Pool Approach

Instead of direct inverse weighting, the system:

1. **Calculates inverse weights:** `weight = 1 / (difficulty ^ multiplier)`
2. **Creates a sample pool** of 3000 tricks where easier tricks appear more frequently
3. **Randomly selects** from this pre-weighted pool

This approach ensures:

- ADVANCED rarely gets 450°/540° spins (mostly 180-360°)
- PRO gets variety without all mega-spins
- Max 1-2 high spins per combo (approaching the ideal)
- Smooth difficulty distribution

### Switch-Up Penalties

Each additional switch-up increases difficulty weights:

```python
penalty_multiplier = min(n_switch_ups * 0.1, 0.4)
```

This prevents combos from getting exponentially harder with more switch-ups.

### Diminishing Returns

Combo difficulty is calculated with diminishing returns:

```python
combo_difficulty = tricks[0]
for i, trick in enumerate(tricks[1:], 1):
    scaling_factor = 1.0 / (1 + i * 0.15)
    combo_difficulty += trick * scaling_factor
```

This reflects that a 3-trick combo isn't 3x harder than a single trick.

## Files Modified

- `sports/trick_api.py` - **NEW** Flask REST API
- `sports/graph_generation_api.py` - **NEW** Refactored graph generator module
- `sports/rollerblading/app.html` - Updated to call API instead of JS generator
- `requirements.txt` - **NEW** Python dependencies
- `start.sh` - **NEW** Startup script

## Original Files (Preserved)

- `sports/graph_generation.py` - Original script (still works standalone)
- `sports/rollerblading/generator.js` - Old JS generator (no longer used)
- `sports/rollerblading/schema.json` - Schema (still used for UI metadata)

## Testing

### Test the API directly:

```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "advanced", "numSwitchUps": 2}'
```

### Test the standalone module:

```bash
cd sports
python3 graph_generation_api.py advanced 2
```

## Troubleshooting

### "Failed to connect to trick generator API"

- Make sure the Flask API is running (`python3 sports/trick_api.py`)
- Check that it's on http://localhost:5000
- Check browser console for CORS errors

### "Port 5000 already in use"

```bash
# Find and kill the process using port 5000
lsof -ti:5000 | xargs kill -9
```

Or change the port in `sports/trick_api.py`:

```python
app.run(debug=True, port=5001)  # Use port 5001 instead
```

Then update app.html to use the new port.

### Dependencies not installing

Make sure you're in the virtual environment:

```bash
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows
```

## Future Enhancements

Potential improvements:

- [ ] Add WebSocket support for real-time trick generation
- [ ] Cache tricks to reduce API calls
- [ ] Add trick history/favorites
- [ ] Support for more obstacle types
- [ ] Multiplayer sync for BLADE game mode
- [ ] Convert to JavaScript (remove Python dependency)

## License

This project is for personal/educational use.

---

**Questions?** Check the code comments in:

- `sports/graph_generation_api.py` - Core logic
- `sports/trick_api.py` - API implementation
- `sports/rollerblading/app.html` - Frontend integration
