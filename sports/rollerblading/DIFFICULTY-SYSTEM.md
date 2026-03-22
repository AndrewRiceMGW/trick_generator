# 🎯 Obstacle-Specific Difficulty System

## Problem Statement

**Before:** A 900 spin had the same difficulty rating whether you're doing it over a jump box or on a ledge grind.

**Reality:** A 900 over a gap is extremely hard but possible. A 900 into/out of a ledge grind is nearly impossible.

## Solution: Context-Aware Difficulty

Each obstacle type now has **different constraints and multipliers** that make tricks realistic.

---

## 📊 Obstacle Comparison Table

| Obstacle   | Max Entry Spin  | Max Exit Spin   | Spin Multiplier | Why?                                 |
| ---------- | --------------- | --------------- | --------------- | ------------------------------------ |
| **Rail**   | 450° (1.25 rot) | 540° (1.5 rot)  | **2.5x**        | Must land locked into grind position |
| **Ledge**  | 540° (1.5 rot)  | 540° (1.5 rot)  | **2.2x**        | Similar to rail but wider surface    |
| **Curb**   | 360° (1 rot)    | 450° (1.25 rot) | **2.8x**        | Low obstacle, very technical         |
| **Stairs** | 1080° (3 rots)  | 1080° (3 rots)  | **1.0x**        | Pure air trick, no lock-in needed    |

---

## 🔢 Difficulty Calculation Examples

### Example 1: Rail vs Stairs (360 Spin)

**360 on Rail:**

- Base difficulty: 2.5
- Rail spin multiplier: **2.5x**
- **Total: 6.25 difficulty** ⚠️ Very hard!
- Why? Must land perfectly in grind position while rotating

**360 on Stairs:**

- Base difficulty: 2.5
- Stairs spin multiplier: **1.0x**
- **Total: 2.5 difficulty** ✅ Reasonable
- Why? Just spinning in the air, no grind lock-in

### Example 2: 720 Attempts

**720 Entry on Ledge:**

- ❌ **BLOCKED!** Ledge max entry = 540°
- Generator won't even attempt this trick
- Realistic constraint

**720 on Stairs:**

- Base difficulty: 5.0
- Stairs multiplier: 1.0x
- **Total: 5.0 difficulty** ✅ Hard but possible
- Generator will include this in rotation

### Example 3: 900 Spin (Air Only)

**900 on Rail/Ledge:**

- ❌ **BLOCKED!** Max spins too low
- Would be 9.0 × 2.5 = **22.5 difficulty** if allowed
- Physically unrealistic

**900 on 10-Stair:**

- Base difficulty: 7.0
- Stairs multiplier: 1.0x
- Height multiplier (10 stairs): 1.5x
- **Total: 10.5 difficulty** 🔥 Pro level!

---

## 🎬 Real-World Examples

### Beginner on Curb (Realistic Trick)

```
Obstacle: Curb (short)
Entry: No spin (0°)
Trick: Frontside grind
Exit: 180 out
```

**Calculation:**

- Stance: 1.0
- Frontside: 1.0
- 180 exit: 1.5 × 2.8 (curb spin multiplier) = **4.2**
- **Total: ~6.2 difficulty** (Intermediate)

### Pro on 12-Stair

```
Obstacle: 12-Stair
Entry: 720 spin
Grab: Mute
Exit: Land forward
```

**Calculation:**

- Stance: 1.0
- 720 spin: 5.0 × 1.0 (air multiplier) = 5.0
- Mute grab: 1.5
- Height (12 stairs): × 1.8
- **Total: (5.0 + 1.5) × 1.8 = 11.7 difficulty** (Advanced)

### Impossible Trick (Prevented)

```
Obstacle: Rail
Entry: 900 spin (BLOCKED!)
```

❌ Generator won't create this because:

- Rail max_entry_spin = 450°
- 900° exceeds the limit
- Physically unrealistic

---

## 📈 Difficulty Multiplier Breakdown

### Why Different Multipliers?

**Rail (2.5x):**

- Narrow surface, must land precisely
- Spinning while approaching makes lock-in extremely technical
- Higher spins = exponentially harder

**Ledge (2.2x):**

- Wider than rail, slightly more forgiving
- Still requires precise lock-in
- Still very technical with rotation

**Curb (2.8x):**

- Lowest obstacle, requires perfect precision
- Close to ground = less margin for error
- Most technical for spin tricks

**Stairs (1.0x):**

- Open air, no lock-in requirement
- Natural progression: higher spins = harder
- Standard difficulty scaling

---

## 🏗️ How It Works in Code

### 1. Schema Constraints

```json
"rail": {
  "max_entry_spin": 450,
  "max_exit_spin": 540,
  "spin_difficulty_multiplier": 2.5
}
```

### 2. Generator Filtering

```javascript
// Only include spins within obstacle limits
const spinOptions = Object.keys(entry_spins).filter((spin) => {
	return spin.degrees <= obstacleData.max_entry_spin;
});
```

### 3. Difficulty Application

```javascript
// Apply obstacle-specific multiplier
difficulty += spinData.difficulty * obstacleData.spin_difficulty_multiplier;
```

---

## 🎯 Spin Progression by Obstacle

### Rail (Grind Tricks)

- 0° - 180°: **Common** (no spin to half rotation)
- 270° - 360°: **Advanced** (technical lock-in)
- 450°: **Expert** (1.25 rotations, very rare)
- 540°+: ❌ **Blocked** (unrealistic)

### Ledge (Grind Tricks)

- 0° - 360°: **Common to Advanced**
- 450° - 540°: **Expert** (max realistic)
- 720°+: ❌ **Blocked**

### Curb (Street Grinds)

- 0° - 270°: **Common to Advanced**
- 360°: **Expert** (max realistic for most)
- 450°+: ❌ **Generally blocked**

### Stairs (Air Tricks)

- 0° - 540°: **Progressive difficulty**
- 720°: **Pro level** (2 full rotations)
- 900°: **Elite** (2.5 rotations)
- 1080°: **Legendary** (3 full rotations)

---

## 🎪 Height Multipliers (Stairs Only)

Bigger drops = harder tricks:

| Stairs   | Multiplier | Difficulty Impact |
| -------- | ---------- | ----------------- |
| 3 stair  | 0.8x       | Easier (learning) |
| 5 stair  | 1.0x       | Standard          |
| 7 stair  | 1.2x       | Moderate boost    |
| 10 stair | 1.5x       | Significant boost |
| 12 stair | 1.8x       | Very hard         |
| 15 stair | 2.2x       | Extreme           |

**Example:**

- 540 spin on 5-stair: 3.5 difficulty
- 540 spin on 15-stair: 3.5 × 2.2 = **7.7 difficulty**

---

## ✅ Benefits of This System

1. **Realistic Tricks** - No more impossible combinations
2. **Proper Scaling** - Same trick = different difficulty per obstacle
3. **Natural Progression** - Beginners can't accidentally get pro tricks on technical obstacles
4. **Educational** - Shows what's actually possible in real skating
5. **Extensible** - Easy to add new obstacles with their own constraints

---

## 🔮 Future Enhancements

- **Weather conditions** (wet rail = higher multiplier)
- **Obstacle material** (metal vs concrete)
- **Grind type compatibility** (some grinds easier on certain obstacles)
- **Approach speed requirements** (bigger gaps need more speed)

---

## 🎬 Summary

**Old System:** Trick difficulty = sum of component difficulties
**New System:** Trick difficulty = components × obstacle context

This makes the generator **realistic and educational** - showing what's actually possible in aggressive inline skating! 🛼
