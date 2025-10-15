"""
Attribute Data Definitions
===========================
Defines the attributes system, their ranges, and effects.
"""

import math

# Attribute definitions with (min, max) ranges
ATTRIBUTES = {
    "strength": {
        "abbr": "STR",
        "name": "Strength",
        "min": 2,
        "max": 255,
        "description": "Physical power, melee damage, carrying capacity"
    },
    "reflex": {
        "abbr": "REF",
        "name": "Reflex",
        "min": 2,
        "max": 255,
        "description": "Reaction speed, evasion, reflex saves"
    },
    "agility": {
        "abbr": "AGI",
        "name": "Agility",
        "min": 2,
        "max": 255,
        "description": "Coordination, weapon accuracy, dodge ability"
    },
    "charisma": {
        "abbr": "CHA",
        "name": "Charisma",
        "min": 2,
        "max": 255,
        "description": "Social influence, prices, spirit duration"
    },
    "discipline": {
        "abbr": "DIS",
        "name": "Discipline",
        "min": 2,
        "max": 255,
        "description": "Mental focus, status resistance, magic accuracy"
    },
    "wisdom": {
        "abbr": "WIS",
        "name": "Wisdom",
        "min": 2,
        "max": 255,
        "description": "Learning speed, magic damage, willpower"
    },
    "intelligence": {
        "abbr": "INT",
        "name": "Intelligence",
        "min": 2,
        "max": 255,
        "description": "Experience pool size, spell damage, mental capacity"
    },
    "stamina": {
        "abbr": "STA",
        "name": "Stamina",
        "min": 2,
        "max": 255,
        "description": "Health, endurance, physical resilience"
    }
}

# Display order for attributes (for consistent UI)
ATTRIBUTE_ORDER = [
    "strength",
    "reflex",
    "agility",
    "charisma",
    "discipline",
    "wisdom",
    "intelligence",
    "stamina"
]

# Human baseline values (10 is average)
HUMAN_BASELINE = {
    "strength": 10,
    "reflex": 10,
    "agility": 10,
    "charisma": 10,
    "discipline": 10,
    "wisdom": 10,
    "intelligence": 10,
    "stamina": 10
}

# Racial variance range (±4 from base)
RACIAL_VARIANCE = 4

# TDP (Time Development Points) configuration
TDP_CONFIG = {
    "starting_base": 500,  # Base TDP at character creation
    "per_level": 150,       # TDP gained per level
    "cost_formula": "exponential",  # "linear" or "exponential"
    "linear_cost": 2,     # Cost per point if linear
    "exponential_base": 1.1  # Multiplier if exponential
}


def get_attribute_names():
    """
    Returns a list of all attribute names in display order.
    
    Returns:
        list: Attribute names as strings
    """
    return ATTRIBUTE_ORDER.copy()


def get_attribute_abbrev(attr_name):
    """
    Get the abbreviation for an attribute.
    
    Args:
        attr_name (str): Full attribute name (e.g., "strength")
    
    Returns:
        str: Abbreviation (e.g., "STR")
    """
    return ATTRIBUTES.get(attr_name, {}).get("abbr", "???")


def get_attribute_full_name(attr_name):
    """
    Get the full display name for an attribute.
    
    Args:
        attr_name (str): Full attribute name (e.g., "strength")
    
    Returns:
        str: Display name (e.g., "Strength")
    """
    return ATTRIBUTES.get(attr_name, {}).get("name", attr_name.title())


def get_attribute_description(attr_name):
    """
    Get the description of what an attribute does.
    
    Args:
        attr_name (str): Full attribute name
    
    Returns:
        str: Description of the attribute's effects
    """
    return ATTRIBUTES.get(attr_name, {}).get("description", "Unknown attribute")


def validate_attribute_value(attr_name, value):
    """
    Ensures an attribute value is within valid range.
    
    Args:
        attr_name (str): Attribute name
        value (int): Value to validate
    
    Returns:
        int: Value clamped to valid range
    """
    attr_data = ATTRIBUTES.get(attr_name)
    if not attr_data:
        return 10  # Default fallback
    
    min_val = attr_data["min"]
    max_val = attr_data["max"]
    
    # Clamp value to valid range
    return max(min_val, min(max_val, value))


def calculate_tdp_cost(current_value, desired_value):
    """
    Calculate TDP cost to raise an attribute.
    Uses exponential scaling with different curves for different ranges:
    - Below 50: Gentle curve (2-50 TDP per point)
    - 50-74: Steep exponential (50-300 TDP per point)
    - 75+: Hard cap at 300 TDP per point
    
    Args:
        current_value (int): Current attribute value
        desired_value (int): Target attribute value
    
    Returns:
        int: TDP cost to train from current to desired
    """
    if desired_value <= current_value:
        return 0
    
    total_cost = 0
    
    for value in range(current_value, desired_value):
        if value < 50:
            # Gentle curve below 50
            # Formula: 2 + (value/50)^2 * 48
            # Results in: 2 TDP at value 0, 50 TDP at value 49
            cost = 2 + int((value / 50.0) ** 2 * 48)
        elif value < 75:
            # Steep exponential from 50-74
            # Formula: 50 + ((value-50)/25)^3 * 250
            # Results in: 50 TDP at value 50, 300 TDP at value 74
            normalized = (value - 50) / 25.0
            cost = 50 + int(normalized ** 3 * 250)
        else:
            # Hard cap at 300 TDP per point for 75+
            cost = 300
        
        total_cost += cost
    
    return total_cost


def calculate_starting_tdp(attributes):
    """
    Calculate bonus/penalty TDP based on starting attribute distribution.
    Characters who take penalties get more TDP to compensate.
    
    Args:
        attributes (dict): Dictionary of attribute values
    
    Returns:
        int: Total starting TDP
    """
    base_tdp = TDP_CONFIG["starting_base"]
    
    # Calculate total deviation from human baseline
    total_deviation = 0
    for attr_name, value in attributes.items():
        baseline = HUMAN_BASELINE.get(attr_name, 10)
        deviation = baseline - value  # Positive if below baseline
        total_deviation += deviation
    
    # Convert deviation to TDP bonus/penalty
    # For every 2 points below baseline, gain 50 TDP
    # For every 2 points above baseline, lose 50 TDP
    tdp_adjustment = (total_deviation // 2) * 50
    
    return base_tdp + tdp_adjustment


# Derived stat calculations
def calculate_max_hp(strength, discipline, stamina):
    """
    Calculate maximum health points from attributes.
    Formula: stamina + ((strength + discipline) * 0.125)
    
    Args:
        strength (int): STR value
        discipline (int): DIS value
        stamina (int): STA value
    
    Returns:
        float: Maximum HP (rounded up but stored as float)
    """
    result = stamina + ((strength + discipline) * 0.125)
    return math.ceil(result)


def calculate_max_sp(intelligence, discipline, wisdom):
    """
    Calculate maximum spell points from attributes.
    Formula: intelligence + ((discipline + wisdom) * 0.25)
    
    Args:
        intelligence (int): INT value
        discipline (int): DIS value
        wisdom (int): WIS value
    
    Returns:
        float: Maximum SP (rounded up but stored as float)
    """
    result = intelligence + ((discipline + wisdom) * 0.25)
    return math.ceil(result)


def calculate_max_ep(stamina, discipline, reflex, strength, agility):
    """
    Calculate maximum energy points from attributes.
    Formula: stamina + ((discipline + reflex + strength + agility) * 0.125)
    
    Args:
        stamina (int): STA value
        discipline (int): DIS value
        reflex (int): REF value
        strength (int): STR value
        agility (int): AGI value
    
    Returns:
        float: Maximum EP (rounded up but stored as float)
    """
    result = stamina + ((discipline + reflex + strength + agility) * 0.125)
    return math.ceil(result)


def calculate_carrying_capacity(strength, stamina):
    """
    Calculate how much weight a character can carry.
    This is a derived stat example - adjust formula as needed.
    
    Args:
        strength (int): STR value
        stamina (int): STA value
    
    Returns:
        float: Carrying capacity in pounds/stones
    """
    # Example formula: STR * 10 + STA * 5
    return (strength * 10) + (stamina * 5)


def get_attribute_effect_on_skill(attr_name, attr_value):
    """
    Calculate how much an attribute modifies skill checks.
    Can be used for skill rolls, learning rates, etc.
    
    Args:
        attr_name (str): Attribute name
        attr_value (int): Attribute value
    
    Returns:
        float: Modifier (e.g., 1.0 = no change, 1.5 = 50% bonus)
    """
    # Example: Every 10 points above/below 10 = 10% bonus/penalty
    baseline = 10
    difference = attr_value - baseline
    modifier = 1.0 + (difference * 0.01)
    return max(0.5, min(2.0, modifier))  # Cap at 50%-200%