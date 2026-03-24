# Physics-Based Schema Update

## New Fields Added to Each Grind:

### Positioning Fields:
- `back_foot_degree`: Angle of back foot relative to obstacle (0° = forward)
- `front_foot_degree`: Angle of front foot relative to obstacle  
- `back_foot_knee`: Knee direction ("neutral", "bent towards back", "bent towards front", "bent away front", "NA")
- `front_foot_knee`: Knee direction
- `back_foot_hblock_pointing`: H-block edge direction ("inner pointing towards back", "outer pointing towards front", "NA")
- `front_foot_hblock_pointing`: H-block edge direction
- `topside_or_regular`: Body position ("topside" or "regular")
- `can_be_grabbed`: Boolean - can trick be grabbed
- `cross_grab`: Boolean - can be cross-grabbed  
- `crossed_foot`: Which foot crosses ("back foot", "front foot", "NA")
- `spin_multiplier`: Spin increment (90 or 180)
- `balance_point`: Where balance is ("on top", "more back", "more front", "front foot", "back foot")
- `h_block_type`: H-block category ("front", "back", "both", "NA")

## Spin Increment Rules:

### Same Category Transitions:
- **Full h-block → Full h-block**: 0°, 180°, 360°, 540° only
- **Non-full h-block → Non-full h-block**: 0°, 180°, 360°, 540° only

### Cross Category Transitions:
- **Full h-block ↔ Non-full h-block**: 0°, 90°, 180°, 270°, 360°, 450°, 540°

## Switch-Up Difficulty Calculation:

### Factors:
1. **Foot Angle Changes** - Angular rotation per foot
2. **Edge Transitions** - Inner↔outer, h-block↔soul edges
3. **Knee Direction Changes** - Bent direction changes
4. **Balance Point Shifts** - Stability changes
5. **H-Block Resistance** - Edge pointing towards/away from other foot
6. **Topside Transitions** - Regular↔topside body position
7. **Grabbed State Changes** - Grabbed↔freestyle transitions

### Resistance Rules:
- Inner/outer edge pointing **towards** other foot = **MORE resistance** (harder)
- Inner/outer edge pointing **away** from other foot = **LESS resistance** (easier)
