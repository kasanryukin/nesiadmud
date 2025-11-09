"""
Vitality Injury System
======================
Manages character wounds by body part, progression, and scarring.
"""

import mud
import mudsys
import random
from . import vitality_core
from . import injury_penalties


# Configuration
INFECTION_CHECK_INTERVAL = 6000  # Heartbeats between infection/progression checks
VALID_WOUND_TYPES = ["surface", "internal", "nervous"]
VALID_INJURY_STATUS = ["bleeding", "poisoned", "diseased", "burned", "infected"]

# DR Wound Severity Levels (8 levels)
SEVERITY_LEVELS = [
    "none",           # 0 - no wound
    "insignificant",  # 1
    "negligible",     # 2
    "minor",          # 3
    "small",          # 4
    "moderate",       # 5
    "large",          # 6
    "severe",         # 7
    "critical"        # 8
]


def setup_injury_system():
    """Initialize injury system on character load"""
    pass  # Hooks and initialization handled by caller


def get_valid_body_parts(ch):
    """
    Get list of valid targetable body parts for a character.
    Excludes inventory-only locations marked with *.
    
    Args:
        ch: Character
    
    Returns:
        list: Valid body part names
    """
    # Inventory-only body parts that shouldn't be targetable
    INVENTORY_ONLY = [
        "about body", "floating about head", "held", "hooves"
    ]
    
    valid_parts = []
    
    try:
        # Get body parts from race/entity
        if hasattr(ch, 'body_parts'):
            for part in ch.body_parts:
                if part.lower() not in INVENTORY_ONLY:
                    valid_parts.append(part.lower())
        else:
            # Fallback to common humanoid parts
            valid_parts = [
                "head", "face", "neck", "torso", "waist",
                "left hand", "right hand", "left foot", "right foot",
                "left leg", "right leg", "left arm", "right arm",
                "eyes", "ear"
            ]
    except Exception as e:
        mud.log_string("ERROR: Failed to get body parts for %s: %s" % (ch.name, str(e)))
        valid_parts = ["torso"]  # Safe fallback
    
    return valid_parts


def create_wound(wound_type, severity=3):
    """
    Create a wound data structure.
    
    Args:
        wound_type: "surface", "internal", or "nervous"
        severity: 1-8 (see SEVERITY_LEVELS)
    
    Returns:
        dict: Wound object
    """
    if wound_type not in VALID_WOUND_TYPES:
        wound_type = "surface"
    
    severity = max(1, min(8, severity))  # Clamp 1-8
    
    return {
        "type": wound_type,
        "severity": severity,
        "status": [],  # bleeding, poisoned, diseased, burned, infected
        "age": 0,      # Heartbeats since wound creation
        "scar_created": False
    }


def apply_wound(ch, body_part=None, wound_type="surface", severity=3):
    """
    Apply a wound to a character on a specific body part.
    Stacks with existing wounds on that location.
    
    Args:
        ch: Character receiving wound
        body_part: Specific body part (if None, randomly selected)
        wound_type: "surface", "internal", or "nervous"
        severity: 1-8
    
    Returns:
        bool: True if wound applied successfully
    """
    # Get or create injury auxiliary
    injury_aux = ch.getAuxiliary("injury_data")
    if not injury_aux:
        mud.log_string("ERROR: %s has no injury data" % ch.name)
        return False
    
    # Select random body part if not specified
    if not body_part:
        valid_parts = get_valid_body_parts(ch)
        if not valid_parts:
            mud.log_string("ERROR: No valid body parts for %s" % ch.name)
            return False
        body_part = random.choice(valid_parts)
    
    body_part = body_part.lower()
    
    # Initialize wounds dict if needed
    if not hasattr(injury_aux, 'wounds'):
        injury_aux.wounds = {}
    
    # If body part already has a wound, increase severity (stacking)
    if body_part in injury_aux.wounds:
        existing_wound = injury_aux.wounds[body_part]
        existing_wound["severity"] = min(8, existing_wound["severity"] + severity)
        mud.log_string("INJURY: %s wound on %s increased to severity %d" % 
                       (ch.name, body_part, existing_wound["severity"]))
    else:
        # Create new wound
        injury_aux.wounds[body_part] = create_wound(wound_type, severity)
        mud.log_string("INJURY: %s received %s %s wound on %s (severity %d)" % 
                       (ch.name, SEVERITY_LEVELS[severity], wound_type, body_part, severity))
    
    return True


def add_wound_status(ch, body_part, status):
    """
    Add a status effect to an existing wound (bleeding, infected, etc).
    
    Args:
        ch: Character
        body_part: Body part with wound
        status: One of VALID_INJURY_STATUS
    
    Returns:
        bool: True if status added
    """
    if status not in VALID_INJURY_STATUS:
        return False
    
    injury_aux = ch.getAuxiliary("injury_data")
    if not injury_aux or not hasattr(injury_aux, 'wounds'):
        return False
    
    body_part = body_part.lower()
    if body_part not in injury_aux.wounds:
        return False
    
    wound = injury_aux.wounds[body_part]
    if status not in wound["status"]:
        wound["status"].append(status)
        mud.log_string("INJURY: %s wound on %s is now %s" % (ch.name, body_part, status))
        return True
    
    return False


def get_wounds(ch, body_part=None):
    """
    Get wound(s) for a character.
    
    Args:
        ch: Character
        body_part: Specific body part (if None, returns all)
    
    Returns:
        dict or wound object: Wound(s) or empty dict/None
    """
    injury_aux = ch.getAuxiliary("injury_data")
    if not injury_aux or not hasattr(injury_aux, 'wounds'):
        return {} if body_part is None else None
    
    if body_part is None:
        return injury_aux.wounds
    
    return injury_aux.wounds.get(body_part.lower(), None)


def get_severity_name(severity):
    """Get human-readable severity name"""
    if 0 <= severity < len(SEVERITY_LEVELS):
        return SEVERITY_LEVELS[severity]
    return "unknown"


def check_wound_progression(ch):
    """
    Check for wound progression (infection, bleeding escalation, etc).
    Called from heartbeat at configurable interval.
    
    Args:
        ch: Character to check
    """
    injury_aux = ch.getAuxiliary("injury_data")
    if not injury_aux or not hasattr(injury_aux, 'wounds'):
        return
    
    if not hasattr(injury_aux, 'progression_counter'):
        injury_aux.progression_counter = 0
    
    # Increment counter
    injury_aux.progression_counter += 1
    
    # Check if it's time to progress wounds
    if injury_aux.progression_counter < INFECTION_CHECK_INTERVAL:
        return
    
    # Reset counter
    injury_aux.progression_counter = 0
    
    # Check each wound for progression
    for body_part, wound in injury_aux.wounds.items():
        if not wound:
            continue
        
        # Increment wound age
        wound["age"] += INFECTION_CHECK_INTERVAL
        
        # Process status effects
        if "bleeding" in wound["status"]:
            # Bleeding increases wound severity
            old_sev = wound["severity"]
            wound["severity"] = min(8, wound["severity"] + 1)
            if wound["severity"] > old_sev:
                mud.log_string("INJURY: %s's %s wound worsened from bleeding (sev %d -> %d)" % 
                               (ch.name, body_part, old_sev, wound["severity"]))
        
        if "infected" in wound["status"]:
            # Infection increases wound severity faster
            old_sev = wound["severity"]
            wound["severity"] = min(8, wound["severity"] + 2)
            if wound["severity"] > old_sev:
                mud.log_string("INJURY: %s's %s wound worsened from infection (sev %d -> %d)" % 
                               (ch.name, body_part, old_sev, wound["severity"]))
            
            # Severe infection can lead to death - handled elsewhere
            if wound["severity"] >= 8:
                mud.log_string("INJURY: %s is dying from severe infection in %s" % 
                               (ch.name, body_part))
        
        if "poisoned" in wound["status"]:
            # Poison can escalate but slower than infection
            if random.random() < 0.3:  # 30% chance
                old_sev = wound["severity"]
                wound["severity"] = min(8, wound["severity"] + 1)
                if wound["severity"] > old_sev:
                    mud.log_string("INJURY: %s's %s wound worsened from poison (sev %d -> %d)" % 
                                   (ch.name, body_part, old_sev, wound["severity"]))
        
        if "diseased" in wound["status"]:
            # Disease progresses similar to infection but slightly slower
            old_sev = wound["severity"]
            wound["severity"] = min(8, wound["severity"] + 1)
            if wound["severity"] > old_sev:
                mud.log_string("INJURY: %s's %s wound worsened from disease (sev %d -> %d)" % 
                               (ch.name, body_part, old_sev, wound["severity"]))
        
        # Burned wounds don't progress the same way - handled differently later


def get_scar_penalties(ch):
    """
    Calculate cumulative penalties from all scars.
    
    Args:
        ch: Character
    
    Returns:
        dict: Skill -> penalty mapping
    """
    penalties = {}
    
    injury_aux = ch.getAuxiliary("injury_data")
    if not injury_aux or not hasattr(injury_aux, 'scars'):
        return penalties
    
    # Iterate through scars and accumulate penalties
    for body_part, scar_severity in injury_aux.scars.items():
        part_penalties = injury_penalties.get_penalties(body_part, scar_severity)
        for skill, penalty in part_penalties.items():
            penalties[skill] = penalties.get(skill, 0) + penalty
    
    return penalties

def setup_injuries(ch):
    """
    Initialize injury system for a character.
    Call this during character creation or load.
    
    Args:
        ch: Character to initialize
    """
    injury_aux = ch.getAuxiliary("injury_data")
    
    if injury_aux is None:
        # Create new injury data
        injury_aux = ch.createAuxiliary("injury_data")
        injury_aux.wounds = {}           # body_part -> wound dict
        injury_aux.scars = {}            # body_part -> scar severity
        injury_aux.progression_counter = 0
        mud.log_string("INJURY: Initialized injury system for %s" % ch.name)
    else:
        # Ensure required attributes exist (for old characters)
        if not hasattr(injury_aux, 'wounds'):
            injury_aux.wounds = {}
        if not hasattr(injury_aux, 'scars'):
            injury_aux.scars = {}
        if not hasattr(injury_aux, 'progression_counter'):
            injury_aux.progression_counter = 0
            
def modify_sp(ch, amount):
    """
    Modify character's SP (for spell casting, restoration, etc.)
    
    Args:
        ch: Character object
        amount: Amount to modify (negative to spend, positive to restore)
    
    Returns:
        bool: True if modification successful, False if insufficient SP
    """
    vit_aux = get_vitality(ch)
    if not vit_aux:
        return False
    
    new_sp = vit_aux.sp + amount
    
    # Check if trying to spend more than available
    if new_sp < 0:
        return False
    
    vit_aux.sp = min(vit_aux.max_sp, new_sp)
    return True


def modify_ep(ch, amount):
    """
    Modify character's EP (for abilities, actions, etc.)
    
    Args:
        ch: Character object
        amount: Amount to modify (negative to spend, positive to restore)
    
    Returns:
        bool: True if modification successful, False if insufficient EP
    """
    vit_aux = get_vitality(ch)
    if not vit_aux:
        return False
    
    new_ep = vit_aux.ep + amount
    
    # Check if trying to spend more than available
    if new_ep < 0:
        return False
    
    vit_aux.ep = min(vit_aux.max_ep, new_ep)
    return True


def get_vitality(ch):
    """
    Get a character's vitality auxiliary data.
    
    Args:
        ch: Character object
    
    Returns:
        VitalityAuxData: The character's vitality data, or None
    """
    return ch.getAuxiliary("vitality_data")


def ensure_vitality(ch):
    """
    Ensure a character has vitality data installed.
    
    Args:
        ch: Character object
    
    Returns:
        VitalityAuxData: The character's vitality data
    """
    aux = get_vitality(ch)
    if aux is None:
        # Auxiliary data is auto-created when accessed if properly installed
        return ch.getAuxiliary("vitality_data")
    return aux


def get_vitality_percent(ch, vitality_type="hp"):
    """
    Get the percentage of a vitality pool.
    
    Args:
        ch: Character object
        vitality_type: "hp", "sp", or "ep"
    
    Returns:
        float: Percentage (0.0 to 100.0)
    """
    vit_aux = get_vitality(ch)
    if not vit_aux:
        return 100.0
    
    if vitality_type == "hp":
        return (vit_aux.hp / vit_aux.max_hp * 100.0) if vit_aux.max_hp > 0 else 0.0
    elif vitality_type == "sp":
        return (vit_aux.sp / vit_aux.max_sp * 100.0) if vit_aux.max_sp > 0 else 0.0
    elif vitality_type == "ep":
        return (vit_aux.ep / vit_aux.max_ep * 100.0) if vit_aux.max_ep > 0 else 0.0
    
    return 0.0


def get_vitality_color(percent):
    """
    Get a color code based on vitality percentage.
    
    Args:
        percent: Vitality percentage (0-100)
    
    Returns:
        str: Color code for display
    """
    if percent >= 75:
        return "{G"  # Green - healthy
    elif percent >= 50:
        return "{Y"  # Yellow - wounded
    elif percent >= 25:
        return "{y"  # Dark yellow - badly wounded
    else:
        return "{R"  # Red - critical

from . import vitality_injury


def cmd_wounds(ch, cmd, arg):
    """
    Usage: wounds [body_part]
    
    Display wounds on your character or a specific body part.
    """
    
    wounds = vitality_injury.get_wounds(ch)
    
    if not wounds:
        ch.send("You have no wounds.")
        return
    
    # If specific body part requested
    if arg and arg.strip():
        body_part = arg.strip().lower()
        wound = wounds.get(body_part)
        
        if not wound:
            ch.send("You have no wound on the %s." % arg.strip())
            return
        
        # Display single wound in detail
        severity_name = vitality_injury.get_severity_name(wound["severity"])
        ch.send("{r%s:{n" % body_part.title())
        ch.send("  Type:     %s" % wound["type"])
        ch.send("  Severity: %s (%d/8)" % (severity_name, wound["severity"]))
        
        if wound["status"]:
            ch.send("  Status:   %s" % ", ".join(wound["status"]))
        else:
            ch.send("  Status:   Stable")
        
        ch.send("  Age:      %d heartbeats" % wound["age"])
        return
    
    # Display all wounds
    ch.send("{rYour Wounds:{n")
    ch.send("{b" + "-" * 60)
    
    for body_part, wound in sorted(wounds.items()):
        severity_name = vitality_injury.get_severity_name(wound["severity"])
        status_str = ", ".join(wound["status"]) if wound["status"] else "stable"
        
        ch.send("{c%-20s {w%-12s {y%-15s {g%s{n" % 
                (body_part.title(), 
                 severity_name, 
                 status_str,
                 wound["type"]))
    
    ch.send("{b" + "-" * 60)
    ch.send("Use 'wounds <body_part>' for details.")


def cmd_scars(ch, cmd, arg):
    """
    Usage: scars [body_part]
    
    Display scars on your character or skill penalties from a specific scar.
    """
    
    injury_aux = ch.getAuxiliary("injury_data")
    if not injury_aux or not hasattr(injury_aux, 'scars'):
        ch.send("You have no scars.")
        return
    
    scars = injury_aux.scars
    
    if not scars:
        ch.send("You have no scars.")
        return
    
    # If specific body part requested
    if arg and arg.strip():
        body_part = arg.strip().lower()
        
        if body_part not in scars:
            ch.send("You have no scar on the %s." % arg.strip())
            return
        
        severity = scars[body_part]
        severity_name = vitality_injury.get_severity_name(severity)
        
        ch.send("{r%s Scar:{n" % body_part.title())
        ch.send("  Severity: %s (%d/8)" % (severity_name, severity))
        
        # Show penalties
        from . import injury_penalties
        penalties = injury_penalties.get_penalties(body_part, severity)
        
        if penalties:
            ch.send("\n  Skill Penalties:")
            for skill, penalty in sorted(penalties.items()):
                if penalty < 0:
                    ch.send("    %s: {g+%d{n (bonus)" % (skill.title(), abs(penalty)))
                else:
                    ch.send("    %s: {r-%d{n" % (skill.title(), penalty))
        else:
            ch.send("  No skill penalties for this scar severity.")
        
        return
    
    # Display all scars
    ch.send("{rYour Scars:{n")
    ch.send("{b" + "-" * 60)
    
    for body_part, severity in sorted(scars.items()):
        severity_name = vitality_injury.get_severity_name(severity)
        ch.send("{c%-20s {w%-12s{n" % (body_part.title(), severity_name))
    
    ch.send("{b" + "-" * 60)
    
    # Show cumulative penalties
    cumulative = vitality_injury.get_scar_penalties(ch)
    if cumulative:
        ch.send("\n{rCumulative Skill Penalties:{n")
        for skill, penalty in sorted(cumulative.items()):
            if penalty < 0:
                ch.send("  %s: {g+%d{n (bonus)" % (skill.title(), abs(penalty)))
            else:
                ch.send("  %s: {r-%d{n" % (skill.title(), penalty))
    
    ch.send("\nUse 'scars <body_part>' for details.")


def cmd_injure(ch, cmd, arg):
    """
    Usage: injure <target> [body_part] [type] [severity]
    
    Admin command to apply a wound for testing.
    Target can be 'self', 'me', or another character's name.
    
    Examples:
      injure self left hand surface 5
      injure me torso internal 4
      injure guard torso internal 3
      injure self (random everything)
    """
    
    args = arg.split()
    if not args:
        ch.send("Usage: injure <target> [body_part] [type] [severity]")
        return
    
    # Find target
    target_name = args[0].lower()
    
    # Check if targeting self
    if target_name in ["self", "me"]:
        target = ch
    else:
        # Try to find the target in the room
        try:
            target = ch.room.get_character(target_name)
        except:
            ch.send("Target '%s' not found." % args[0])
            return
        
        if not target:
            ch.send("Target '%s' not found." % args[0])
            return
    
    # Parse optional parameters
    body_part = args[1] if len(args) > 1 else None
    wound_type = args[2] if len(args) > 2 else "surface"
    try:
        severity = int(args[3]) if len(args) > 3 else 3
    except ValueError:
        ch.send("Severity must be a number 1-8.")
        return
    
    # Validate wound type
    if wound_type not in vitality_injury.VALID_WOUND_TYPES:
        ch.send("Invalid wound type. Options: %s" % 
                ", ".join(vitality_injury.VALID_WOUND_TYPES))
        return
    
    # Ensure target has injury data
    vitality_injury.setup_injuries(target)
    
    # Apply wound
    if vitality_injury.apply_wound(target, body_part, wound_type, severity):
        severity_name = vitality_injury.get_severity_name(severity)
        
        # Get the actual body part that was wounded
        if body_part:
            actual_part = body_part.lower()
        else:
            wounds = vitality_injury.get_wounds(target)
            actual_part = list(wounds.keys())[-1]  # Last added wound
        
        ch.send("Applied %s %s wound to %s's %s." % 
                (severity_name, wound_type, target.name, actual_part))
        
        # Show the wound
        cmd_wounds(target, "wounds", actual_part)
    else:
        ch.send("Failed to apply wound.")


def cmd_infect(ch, cmd, arg):
    """
    Usage: infect <target> [body_part] [status]
    
    Admin command to add a status effect to an existing wound.
    Status options: bleeding, poisoned, diseased, burned, infected
    
    Examples:
      infect self left hand infected
      infect guard torso bleeding
    """
    
    args = arg.split()
    if len(args) < 2:
        ch.send("Usage: infect <target> [body_part] [status]")
        return
    
    # Find target
    target_name = args[0]
    try:
        target = ch.room.get_character(target_name)
    except:
        ch.send("Target '%s' not found." % target_name)
        return
    
    body_part = args[1] if len(args) > 1 else None
    status = args[2] if len(args) > 2 else "infected"
    
    # Validate status
    if status not in vitality_injury.VALID_INJURY_STATUS:
        ch.send("Invalid status. Options: %s" % 
                ", ".join(vitality_injury.VALID_INJURY_STATUS))
        return
    
    # If no body part specified, pick the first one with a wound
    if not body_part:
        wounds = vitality_injury.get_wounds(target)
        if wounds:
            body_part = list(wounds.keys())[0]
        else:
            ch.send("%s has no wounds to infect." % target.name)
            return
    
    # Add status
    if vitality_injury.add_wound_status(target, body_part, status):
        ch.send("Made %s's %s wound %s." % (target.name, body_part, status))
        cmd_wounds(target, "wounds", body_part)
    else:
        ch.send("Failed to add status (wound may not exist).")

def cmd_init_injury(ch, cmd, arg):
    """
    Force initialize the injury system on a character.
    
    Usage: init_injury [target]
    
    If no target specified, initializes self.
    Admin command for setting up injury data on existing characters.
    """
    
    # Determine target
    if not arg or not arg.strip():
        target = ch
        target_name = "yourself"
    else:
        target_name = arg.strip()
        # Try to find the target
        try:
            target = ch.room.get_character(target_name)
        except:
            ch.send("Target '%s' not found in this room." % target_name)
            return
        
        if not target:
            ch.send("Target '%s' not found." % target_name)
            return
    
    # Initialize the injury system
    try:
        vitality_injury.setup_injuries(target)
        ch.send("Injury system initialized for %s." % target.name)
        mud.log_string("ADMIN: %s initialized injury system for %s" % (ch.name, target.name))
    except Exception as e:
        ch.send("Failed to initialize injury system: %s" % str(e))
        mud.log_string("ERROR: Failed to initialize injury system for %s: %s" % (target.name, str(e)))

def register_commands():
    """Register all injury commands with the mud system"""
    mudsys.add_cmd("wounds", None, cmd_wounds, "player", False)
    mudsys.add_cmd("scars", None, cmd_scars, "player", False)
    mudsys.add_cmd("injure", None, cmd_injure, "admin", False)
    mudsys.add_cmd("infect", None, cmd_infect, "admin", False)
    mudsys.add_cmd("init_injury", None, cmd_init_injury, "admin", False)
    mud.log_string("Injury commands registered")