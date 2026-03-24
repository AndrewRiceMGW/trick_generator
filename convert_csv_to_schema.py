#!/usr/bin/env python3
import json
import csv

# Read the CSV file
with open('tricktable.csv', 'r') as f:
    reader = csv.DictReader(f)
    tricks = list(reader)

# Helper function to convert CSV values to schema format
def parse_value(value):
    if value == 'NA' or value == '':
        return None
    if value in ['yes', 'no']:
        return value == 'yes'
    try:
        return int(value)
    except ValueError:
        return value.strip()

# Helper function to create grind ID from name
def create_id(name):
    return name.lower().replace(' ', '_')

# Helper function to assign difficulty and weight
def get_difficulty_weight(name):
    name_lower = name.lower()
    
    # Simple tricks
    if name_lower in ['makio', 'soul', 'mizou', 'frontside', 'backside']:
        return 1.5, 30
    
    # Medium difficulty
    if name_lower in ['mistrial', 'topsoul', 'x grind', 'frontside royale', 'backside royale',
                      'frontside fastslide', 'backside fastslide', 'frontside pudslide', 'backside pudslide']:
        return 2.0, 20
    
    # Higher difficulty
    if name_lower in ['acid soul', 'topacid', 'frontside farv', 'backside farv',
                      'frontside backslide', 'backside backslide', 'frontside torque', 'backside torque']:
        return 2.5, 15
    
    # Advanced
    if name_lower in ['pstar', 'top pstar', 'sweatstance', 'frontside unity', 'backside unity',
                      'frontside savannah', 'backside savannah', 'top mistrial']:
        return 3.0, 10
    
    # Topside variations
    if 'topside' in name_lower or 'fishbrain' in name_lower or 'top ' in name_lower:
        return 2.5, 12
    
    # Default
    return 2.0, 15

# Read the original schema to preserve non-grind sections
with open('sports/rollerblading/schema.json', 'r') as f:
    original_schema = json.load(f)

# Build new grinds section
new_grinds = {}

for trick in tricks:
    name = trick['trick name'].strip()
    grind_id = create_id(name)
    
    # Use the explicit "soul or hblock" column from CSV
    trick_type = parse_value(trick['soul or hblock'])
    is_soul_trick = (trick_type == 'soul')
    is_hblock_trick = (trick_type == 'hblock')
    
    h_block_type = parse_value(trick['h block '])
    difficulty, weight = get_difficulty_weight(name)
    
    # Parse spin multiplier (e.g., "0, 180" or "0, 90")
    spin_mult_str = trick['spin multiplier'].strip().strip('"')
    if ',' in spin_mult_str:
        spin_multiplier = int(spin_mult_str.split(',')[1].strip())
    else:
        spin_multiplier = int(spin_mult_str)
    
    # Check if this is already a topside version (has "top" in name or topside in CSV)
    topside_or_regular = parse_value(trick['topside or regular'])
    is_inherently_topside = (topside_or_regular == 'topside')
    
    grind_entry = {
        "id": grind_id,
        "name": name.title(),
        "difficulty": difficulty,
        "soul_based": is_soul_trick,
        "h_block": is_hblock_trick,
        "is_topside_variation": is_inherently_topside,  # New field to identify pre-topside tricks
        "foot_position": "mixed",  # Generic, can be refined later
        "weight": weight,
        "physics": {
            "back_foot_degree": parse_value(trick['back foot degree']),
            "front_foot_degree": parse_value(trick['front foot degree']),
            "back_foot_knee": parse_value(trick['back foot knee']),
            "front_foot_knee": parse_value(trick['front foot knee']),
            "back_foot_hblock_pointing": parse_value(trick['back foot hblock pointing towards']),
            "front_foot_hblock_pointing": parse_value(trick['front foot hblock pointing towards']),
            "topside_or_regular": topside_or_regular,
            "can_be_grabbed": parse_value(trick['can be grabbed']),
            "cross_grab": parse_value(trick['cross grab']),
            "crossed_foot": parse_value(trick['crossed foot']),
            "spin_multiplier": spin_multiplier,
            "balance_point": parse_value(trick['balance point ']),
            "h_block_type": h_block_type if h_block_type != 'NA' else None
        }
    }
    
    new_grinds[grind_id] = grind_entry

# Build new schema
new_schema = {
    "metadata": original_schema["metadata"],
    "stances": original_schema["stances"],
    "obstacles": original_schema["obstacles"],
    "entry_spins": original_schema["entry_spins"],
    "exit_spins": original_schema["exit_spins"],
    "grinds": new_grinds,
    "modifiers": {
        "topside": original_schema["modifiers"]["topside"],
        "true_topside": original_schema["modifiers"]["true_topside"],
        "negative": original_schema["modifiers"]["negative"],
        "negative_true": original_schema["modifiers"]["negative_true"]
    },
    "grabs": original_schema["grabs"],
    "rolls": original_schema["rolls"],
    "flips": original_schema["flips"],
    "naming_rules": original_schema["naming_rules"],
    "difficulty_levels": original_schema["difficulty_levels"]
}

# Write new schema
with open('sports/rollerblading/schema_new.json', 'w') as f:
    json.dump(new_schema, f, indent=2)

print(f"✓ Created new schema with {len(new_grinds)} grinds")
print(f"✓ Removed backside/frontside modifiers (now part of trick names)")
print(f"✓ Preserved all other sections")
