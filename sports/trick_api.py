"""
Flask API for Aggressive Inline Trick Generator
Wraps the graph-based trick generation and exposes it via REST API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from graph_generation_api import generate_trick_combo

app = Flask(__name__)
CORS(app)  # Enable CORS for web frontend


@app.route("/api/generate", methods=["POST"])
def generate_trick():
    """
    Generate a trick combo based on provided parameters

    Expected JSON payload:
    {
        "difficulty": "beginner|intermediate|advanced|pro|insane",
        "numSwitchUps": 0-3,
        "obstacle": "rail|ledge|etc" (optional, for future use),
        "obstacleLength": "short|medium|long" (optional, for future use)
    }

    Returns:
    {
        "success": true,
        "trick": {
            "name": "Full trick name",
            "difficulty": 4.5,
            "components": [
                {"trick": "Negative Mizou", "difficulty": 1.75},
                {"trick": "360 Fishbrain", "difficulty": 2.15}
            ],
            "totalDifficulty": 4.5,
            "individualDifficulties": [1.75, 2.15, ...]
        }
    }
    """
    try:
        data = request.get_json()

        # Extract parameters with defaults
        difficulty = data.get("difficulty", "advanced").lower()
        num_switch_ups = int(data.get("numSwitchUps", 2))

        # Validate parameters
        valid_difficulties = ["beginner", "intermediate", "advanced", "pro", "insane"]
        if difficulty not in valid_difficulties:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f'Invalid difficulty. Must be one of: {", ".join(valid_difficulties)}',
                    }
                ),
                400,
            )

        if not 0 <= num_switch_ups <= 3:
            return (
                jsonify(
                    {"success": False, "error": "numSwitchUps must be between 0 and 3"}
                ),
                400,
            )

        # Generate trick
        result = generate_trick_combo(
            difficulty_level=difficulty, n_switch_ups=num_switch_ups
        )

        return jsonify({"success": True, "trick": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print("🛼 Starting Aggressive Inline Trick Generator API...")
    print("📍 Running on http://localhost:5000")
    print("🔧 Endpoints:")
    print("   POST /api/generate - Generate a trick combo")
    print("   GET  /api/health   - Health check")
    app.run(debug=True, port=5000)
