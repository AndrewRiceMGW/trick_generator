# Foot Position & Trick Complexity System

## Overview

Switch-up difficulty is calculated based on the physical complexity of changing foot positions during a grind. The system uses a **reference position (Makio)** to determine where each grind's feet are positioned, and accounts for body position variations (topside/negative) and spin combinations.

## Position Reference System

All soul-based tricks are positioned **relative to Makio** (neutral reference):

### **Front Positions** (in front of Makio foot)

- **Soul** - Front foot twisted inward on inner edge
- **Acid** - Front foot turned backwards/horizontally on h-block

### **Neutral Position** (Makio reference)

- **Makio** - Side soul on obstacle (one-footed), outer edge
- **Frontside** - Frame grind (no soul/h-block)
- **All H-Block tricks** - Backslide, Royale, Torque, Farv, Fastslide, Pudslide, Savannah, Unity

### **Back Positions** (behind Makio foot)

- **Mizou** - Like makio but back foot spreads out on h-block trailing behind
- **Pornstar/Sunny Day** - Front foot in makio position + back foot h-blocked behind
- **Mistrial** - Inner edge, back position

## Body Position Variations

### **Topside Tricks**

- Soul tricks done by **bending over the side** of the obstacle
- Examples: Fishbrain (topside makio), Sweatstance (topside mizou), Topside Soul, Topside Acid
- Significantly increases difficulty of switch-ups (+0.8 base, +0.5 for cross-body)

### **Negative Tricks**

- Soul tricks done from **underneath the obstacle**
- Body position makes switch-ups much more complex
- Same difficulty modifiers as topside

## Spin Direction

### **Out-Spin (True Spin)**

- Spinning **away from** the obstacle
- Uses base difficulty value
- More natural, easier to control

### **In-Spin (Alley-Oop)**

- Spinning **into/towards** the obstacle
- Uses `alleyoop_difficulty` value (higher)
- Example: 360 = 2.5 base, 3.5 alley-oop
- Harder due to blind approach and rotation against momentum

### **Spinning Switch-Ups**

- Switching up **while spinning** (e.g., 180 soul to makio)
- Very advanced technique (+1.2 difficulty)
- Requires precise timing and body control

## Switch-Up Difficulty Calculation

Base switch-up difficulty:

- **Grind difficulty** + **0.5** (base switch-up cost)

### Positional Difficulty Modifiers

**Same Position** (+0.2) - "Stepping Around"

- Example: **Makio → Acid** (both front)
- Example: **Mizou → Pornstar** (both back)
- Just rotating foot on same side = very easy

**To/From Neutral** (+0.5) - Moderate

- Example: **Makio → Soul** (neutral → front)
- Example: **Frontside → Mizou** (neutral → back)
- Moving in/out of reference position = moderate

**Cross-Body Movement** (+1.0) - Hard

- Example: **Soul → Mizou** (front → back)
- Example: **Acid → Mistrial** (front → back)
- Crossing from front to back or back to front = difficult

**Category Change** (+1.5) - Very Hard

- Example: **Backslide → Soul** (h-block → soul-based)
- Example: **Makio → Royale** (soul-based → h-block)
- Switching between fundamentally different techniques = very difficult

**With Modifiers** (+0.8 base, +0.5 cross-body) - Extra Hard

- Topside: Bending over side of obstacle
- Negative: From underneath obstacle
- Body position variations make any switch-up significantly more complex
- Cross-body movements with modifiers get additional +0.5 penalty

**Spinning Switch-Ups** (+1.2) - Very Advanced

- Switching up while spinning (e.g., 180 soul to makio)
- Requires precise timing and body control mid-rotation
- Rare combination trick

## Example Difficulty Calculations

### Easy: Makio → Acid

- Same position (both front): +0.2
- Base: 2.5 (acid) + 0.5 (switch) = 3.0
- **Total added: 3.2** ⭐ (just stepping around)

### Moderate: Makio → Soul

- Neutral to front: +0.5
- Base: 1.5 (soul) + 0.5 (switch) = 2.0
- **Total added: 2.5** ⭐⭐

### Hard: Soul → Mizou

- Front to back (cross-body): +1.0
- Base: 1.5 (mizou) + 0.5 (switch) = 2.0
- **Total added: 3.0** ⭐⭐⭐

### Very Hard: Topside Soul → Makio

- Front to neutral: +0.5
- With modifier (topside): +0.8
- Base: 1.5 (makio) + 0.5 (switch) = 2.0
- **Total added: 3.8** ⭐⭐⭐⭐ (bending over obstacle adds complexity)

### Very Hard: Fishbrain → Sweatstance (topside cross-body)

- Front to back (cross-body): +1.0
- With modifier: +0.8
- Cross-body with modifier: +0.5
- Base: 1.5 (mizou) + 0.5 (switch) = 2.0
- **Total added: 4.8** ⭐⭐⭐⭐⭐ (topside + cross-body = very difficult)

### Extremely Hard: Backslide → Soul

- Category change (h-block → soul): +1.5
- Neutral to front: +0.5
- Base: 1.5 (soul) + 0.5 (switch) = 2.0
- **Total added: 4.5** ⭐⭐⭐⭐⭐

### Insane: 180 Soul to Makio (spinning switch-up)

- Neutral to front: +0.5
- Spinning switch-up: +1.2
- Base: 1.5 (makio) + 0.5 (switch) = 2.0
- **Total added: 4.2** 🔥🔥 (switching while spinning)

### Ultra Insane: Alley-Oop 360 Topside Soul → Makio → Acid

1. Alley-oop 360 entry: 3.5 (vs 2.5 normal)
2. Topside Soul → Makio: +3.8
3. Makio → Acid: +3.2

- **Cumulative difficulty: 10.5+** 🔥🔥🔥🔥🔥

## Spin Direction Impact

**True Spin (Out-Spin)** - Base difficulty

- 360 True Spin Soul = 2.5 + 1.5 (soul) = 4.0

**Alley-Oop (In-Spin)** - Higher difficulty

- 360 Alley-Oop Soul = 3.5 + 1.5 (soul) = 5.0
- +1.0 difficulty for spinning into obstacle (blind rotation)

## Physical Constraints

The `switch_up_to` arrays define physically possible transitions. The position-aware difficulty system ensures that "easy looking" tricks that are actually simple (like makio to acid) receive appropriate low difficulty scores, while genuinely complex transitions (like negative soul to makio) are rated accurately.
