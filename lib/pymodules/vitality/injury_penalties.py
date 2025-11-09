"""
Injury Penalties Configuration
==============================
Maps body parts and scar severity to skill penalties.
Easy-to-edit format for balancing.

Penalty values represent percentage reduction or difficulty increase.
Severity levels: 1=insignificant, 2=negligible, 3=minor, 4=small, 
                 5=moderate, 6=large, 7=severe, 8=critical
"""

# Define penalties per body part and severity
# Format: body_part -> {severity: {skill: penalty, ...}, ...}
PENALTY_MAP = {
    # HEAD/FACE SCARS
    "head": {
        3: {"perception": 5, "ranged_combat": 3},
        4: {"perception": 10, "ranged_combat": 5, "balance": 3},
        5: {"perception": 15, "ranged_combat": 10, "balance": 5, "swimming": 3},
        6: {"perception": 20, "ranged_combat": 15, "balance": 8, "swimming": 5},
        7: {"perception": 30, "ranged_combat": 20, "balance": 12, "swimming": 8},
        8: {"perception": 40, "ranged_combat": 25, "balance": 15, "swimming": 10},
    },
    
    "face": {
        3: {"persuasion": 3, "deception": 3},
        4: {"persuasion": 8, "deception": 8, "intimidation": -2},  # negative = bonus
        5: {"persuasion": 12, "deception": 12, "intimidation": -5},
        6: {"persuasion": 18, "deception": 15, "intimidation": -8},
        7: {"persuasion": 25, "deception": 20, "intimidation": -12},
        8: {"persuasion": 35, "deception": 30, "intimidation": -15},
    },
    
    "eyes": {
        3: {"ranged_combat": 5, "perception": 8},
        4: {"ranged_combat": 12, "perception": 15, "melee_combat": 3},
        5: {"ranged_combat": 20, "perception": 25, "melee_combat": 8},
        6: {"ranged_combat": 30, "perception": 35, "melee_combat": 12},
        7: {"ranged_combat": 40, "perception": 50, "melee_combat": 18},
        8: {"ranged_combat": 50, "perception": 65, "melee_combat": 25},
    },
    
    "ear": {
        3: {"perception": 3, "listening": 5},
        4: {"perception": 8, "listening": 12},
        5: {"perception": 12, "listening": 20},
        6: {"perception": 18, "listening": 28},
        7: {"perception": 25, "listening": 38},
        8: {"perception": 35, "listening": 50},
    },
    
    # NECK/TORSO
    "neck": {
        3: {"melee_combat": 3, "defense": 2},
        4: {"melee_combat": 8, "defense": 5, "running": 3},
        5: {"melee_combat": 15, "defense": 10, "running": 8},
        6: {"melee_combat": 22, "defense": 15, "running": 12},
        7: {"melee_combat": 30, "defense": 22, "running": 18},
        8: {"melee_combat": 40, "defense": 30, "running": 25},
    },
    
    "torso": {
        3: {"melee_combat": 2, "defense": 3, "athletics": 2},
        4: {"melee_combat": 5, "defense": 8, "athletics": 5},
        5: {"melee_combat": 10, "defense": 15, "athletics": 10, "swimming": 5},
        6: {"melee_combat": 15, "defense": 22, "athletics": 15, "swimming": 8},
        7: {"melee_combat": 25, "defense": 30, "athletics": 22, "swimming": 12},
        8: {"melee_combat": 35, "defense": 40, "athletics": 30, "swimming": 18},
    },
    
    "waist": {
        3: {"balance": 3, "climbing": 2},
        4: {"balance": 8, "climbing": 5, "running": 3},
        5: {"balance": 15, "climbing": 10, "running": 8},
        6: {"balance": 22, "climbing": 15, "running": 12},
        7: {"balance": 30, "climbing": 22, "running": 18},
        8: {"balance": 40, "climbing": 30, "running": 25},
    },
    
    # ARMS/HANDS
    "left arm": {
        3: {"melee_combat": 5, "defense": 3},
        4: {"melee_combat": 12, "defense": 8, "archery": 5},
        5: {"melee_combat": 20, "defense": 15, "archery": 12},
        6: {"melee_combat": 30, "defense": 22, "archery": 18},
        7: {"melee_combat": 42, "defense": 30, "archery": 28},
        8: {"melee_combat": 55, "defense": 40, "archery": 40},
    },
    
    "right arm": {
        3: {"melee_combat": 5, "defense": 3},
        4: {"melee_combat": 12, "defense": 8, "archery": 5},
        5: {"melee_combat": 20, "defense": 15, "archery": 12},
        6: {"melee_combat": 30, "defense": 22, "archery": 18},
        7: {"melee_combat": 42, "defense": 30, "archery": 28},
        8: {"melee_combat": 55, "defense": 40, "archery": 40},
    },
    
    "left hand": {
        3: {"lockpicking": 8, "pickpocketing": 8, "crafting": 5},
        4: {"lockpicking": 18, "pickpocketing": 18, "crafting": 12, "melee_combat": 8},
        5: {"lockpicking": 30, "pickpocketing": 30, "crafting": 22, "melee_combat": 15},
        6: {"lockpicking": 42, "pickpocketing": 42, "crafting": 32, "melee_combat": 22},
        7: {"lockpicking": 55, "pickpocketing": 55, "crafting": 45, "melee_combat": 30},
        8: {"lockpicking": 70, "pickpocketing": 70, "crafting": 60, "melee_combat": 40},
    },
    
    "right hand": {
        3: {"lockpicking": 8, "pickpocketing": 8, "crafting": 5},
        4: {"lockpicking": 18, "pickpocketing": 18, "crafting": 12, "melee_combat": 8},
        5: {"lockpicking": 30, "pickpocketing": 30, "crafting": 22, "melee_combat": 15},
        6: {"lockpicking": 42, "pickpocketing": 42, "crafting": 32, "melee_combat": 22},
        7: {"lockpicking": 55, "pickpocketing": 55, "crafting": 45, "melee_combat": 30},
        8: {"lockpicking": 70, "pickpocketing": 70, "crafting": 60, "melee_combat": 40},
    },
    
    "wrist": {
        3: {"lockpicking": 3, "crafting": 3, "defense": 2},
        4: {"lockpicking": 8, "crafting": 8, "defense": 5, "melee_combat": 3},
        5: {"lockpicking": 15, "crafting": 15, "defense": 10, "melee_combat": 8},
        6: {"lockpicking": 22, "crafting": 22, "defense": 15, "melee_combat": 12},
        7: {"lockpicking": 32, "crafting": 32, "defense": 22, "melee_combat": 18},
        8: {"lockpicking": 45, "crafting": 45, "defense": 30, "melee_combat": 25},
    },
    
    # LEGS/FEET
    "left leg": {
        3: {"running": 5, "balance": 3, "kicking": 5},
        4: {"running": 12, "balance": 8, "kicking": 12, "climbing": 5},
        5: {"running": 20, "balance": 15, "kicking": 20, "climbing": 10},
        6: {"running": 30, "balance": 22, "kicking": 30, "climbing": 15},
        7: {"running": 42, "balance": 32, "kicking": 42, "climbing": 22},
        8: {"running": 55, "balance": 45, "kicking": 55, "climbing": 30},
    },
    
    "right leg": {
        3: {"running": 5, "balance": 3, "kicking": 5},
        4: {"running": 12, "balance": 8, "kicking": 12, "climbing": 5},
        5: {"running": 20, "balance": 15, "kicking": 20, "climbing": 10},
        6: {"running": 30, "balance": 22, "kicking": 30, "climbing": 15},
        7: {"running": 42, "balance": 32, "kicking": 42, "climbing": 22},
        8: {"running": 55, "balance": 45, "kicking": 55, "climbing": 30},
    },
    
    "left foot": {
        3: {"running": 8, "balance": 5, "kicking": 8},
        4: {"running": 18, "balance": 12, "kicking": 18, "climbing": 8},
        5: {"running": 30, "balance": 22, "kicking": 30, "climbing": 15},
        6: {"running": 42, "balance": 32, "kicking": 42, "climbing": 22},
        7: {"running": 55, "balance": 45, "kicking": 55, "climbing": 32},
        8: {"running": 70, "balance": 60, "kicking": 70, "climbing": 45},
    },
    
    "right foot": {
        3: {"running": 8, "balance": 5, "kicking": 8},
        4: {"running": 18, "balance": 12, "kicking": 18, "climbing": 8},
        5: {"running": 30, "balance": 22, "kicking": 30, "climbing": 15},
        6: {"running": 42, "balance": 32, "kicking": 42, "climbing": 22},
        7: {"running": 55, "balance": 45, "kicking": 55, "climbing": 32},
        8: {"running": 70, "balance": 60, "kicking": 70, "climbing": 45},
    },
    
    # APPENDAGES
    "finger": {
        3: {"lockpicking": 5, "crafting": 3},
        4: {"lockpicking": 12, "crafting": 8},
        5: {"lockpicking": 20, "crafting": 15},
        6: {"lockpicking": 30, "crafting": 22},
        7: {"lockpicking": 42, "crafting": 32},
        8: {"lockpicking": 55, "crafting": 45},
    },
    
    "tail": {
        3: {"balance": 5},
        4: {"balance": 12, "running": 3},
        5: {"balance": 20, "running": 8},
        6: {"balance": 30, "running": 12},
        7: {"balance": 42, "running": 18},
        8: {"balance": 55, "running": 25},
    },
    
    "wing": {
        3: {"flying": 5},
        4: {"flying": 12},
        5: {"flying": 25},
        6: {"flying": 38},
        7: {"flying": 50},
        8: {"flying": 65},
    },
    
    "claw": {
        3: {"melee_combat": 3, "climbing": 3},
        4: {"melee_combat": 8, "climbing": 8},
        5: {"melee_combat": 15, "climbing": 15},
        6: {"melee_combat": 22, "climbing": 22},
        7: {"melee_combat": 32, "climbing": 32},
        8: {"melee_combat": 45, "climbing": 45},
    },
    
    "hoof": {
        3: {"kicking": 3, "running": 2},
        4: {"kicking": 8, "running": 5},
        5: {"kicking": 15, "running": 10},
        6: {"kicking": 22, "running": 15},
        7: {"kicking": 32, "running": 22},
        8: {"kicking": 45, "running": 32},
    },
}


def get_penalties(body_part, severity):
    """
    Get skill penalties for a scar on a body part at given severity.
    
    Args:
        body_part: Body part name
        severity: Scar severity level (3-8)
    
    Returns:
        dict: Skill -> penalty mapping
    """
    body_part = body_part.lower()
    
    if body_part not in PENALTY_MAP:
        return {}
    
    severity = max(3, min(8, severity))  # Clamp to valid range
    
    return PENALTY_MAP[body_part].get(severity, {})


def get_all_penalties(body_part):
    """
    Get all penalties for a body part across all severity levels.
    Useful for debugging/display.
    
    Args:
        body_part: Body part name
    
    Returns:
        dict: Severity -> {skill -> penalty} mapping
    """
    body_part = body_part.lower()
    return PENALTY_MAP.get(body_part, {})
