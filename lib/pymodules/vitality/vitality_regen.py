"""
Vitality Regeneration Module
=============================
Handles HP, SP, and EP regeneration over time.

This module hooks into the MUD's pulse system to regenerate vitality
based on character attributes, position, and status.

Regeneration Rates:
- Base rates calculated from attributes
- Modified by position (sleeping > resting > sitting > standing > fighting)
- Modified by status effects (future: injuries, buffs, etc.)
"""

import math
import hooks
import mud
import mudsys

# Try to import required modules
try:
    from . import vitality_core
    import attributes.attribute_aux as attribute_aux
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    mud.log_string("vitality_regen: Required modules not available")


# Regeneration tick rate (in seconds)
REGEN_TICK_RATE = 10  # Regenerate every 10 seconds

# Position modifiers for regeneration rates
POSITION_MODIFIERS = {
    "sleeping": 2.0,   # 200% regen while sleeping
    "resting": 1.5,    # 150% regen while resting
    "sitting": 1.2,    # 120% regen while sitting
    "standing": 1.0,   # 100% regen while standing
    "fighting": 0.5,   # 50% regen while fighting
    "dead": 0.0        # No regen while dead
}


def calculate_hp_regen_rate(ch):
    """
    Calculate HP regeneration per tick based on attributes.
    Base formula: (stamina * 0.1) + (discipline * 0.05)
    
    Args:
        ch: Character object
    
    Returns:
        float: HP regeneration per tick
    """
    if not MODULES_AVAILABLE:
        return 1.0
    
    attr_aux = attribute_aux.get_attributes(ch)
    if not attr_aux:
        return 1.0
    
    stamina = attr_aux.get_attribute("stamina")
    discipline = attr_aux.get_attribute("discipline")
    
    base_regen = (stamina * 0.1) + (discipline * 0.05)
    
    # TODO: Add guild modifiers
    # TODO: Add equipment bonuses
    # TODO: Add status effect modifiers (bleeding, poisoned, etc.)
    
    return max(0.1, base_regen)  # Minimum 0.1 HP per tick


def calculate_sp_regen_rate(ch):
    """
    Calculate SP regeneration per tick based on attributes.
    Base formula: (intelligence * 0.15) + (wisdom * 0.1)
    
    Args:
        ch: Character object
    
    Returns:
        float: SP regeneration per tick
    """
    if not MODULES_AVAILABLE:
        return 1.0
    
    attr_aux = attribute_aux.get_attributes(ch)
    if not attr_aux:
        return 1.0
    
    intelligence = attr_aux.get_attribute("intelligence")
    wisdom = attr_aux.get_attribute("wisdom")
    
    base_regen = (intelligence * 0.15) + (wisdom * 0.1)
    
    # TODO: Add guild modifiers
    # TODO: Add equipment bonuses
    # TODO: Add meditation bonuses
    
    return max(0.1, base_regen)  # Minimum 0.1 SP per tick


def calculate_ep_regen_rate(ch):
    """
    Calculate EP regeneration per tick based on attributes.
    Base formula: (stamina * 0.12) + (discipline * 0.08)
    
    Args:
        ch: Character object
    
    Returns:
        float: EP regeneration per tick
    """
    if not MODULES_AVAILABLE:
        return 1.0
    
    attr_aux = attribute_aux.get_attributes(ch)
    if not attr_aux:
        return 1.0
    
    stamina = attr_aux.get_attribute("stamina")
    discipline = attr_aux.get_attribute("discipline")
    
    base_regen = (stamina * 0.12) + (discipline * 0.08)
    
    # TODO: Add guild modifiers
    # TODO: Add equipment bonuses
    
    return max(0.1, base_regen)  # Minimum 0.1 EP per tick


def get_position_modifier(ch):
    """
    Get the regeneration modifier based on character position.
    
    Args:
        ch: Character object
    
    Returns:
        float: Position modifier (0.0 to 2.0)
    """
    position = ch.pos.lower()
    
    # Check for death first
    vit_aux = vitality_core.get_vitality(ch)
    if vit_aux and vit_aux.is_dead:
        return POSITION_MODIFIERS["dead"]
    
    # Return position modifier or default to standing
    return POSITION_MODIFIERS.get(position, POSITION_MODIFIERS["standing"])


def regenerate_vitality(ch):
    """
    Regenerate HP, SP, and EP for a character.
    Called by the pulse system every tick.
    
    Args:
        ch: Character object
    """
    if not MODULES_AVAILABLE:
        return
    
    vit_aux = vitality_core.get_vitality(ch)
    if not vit_aux:
        return
    
    # Don't regenerate if dead
    if vit_aux.is_dead:
        return
    
    # Get position modifier
    position_mod = get_position_modifier(ch)
    
    # Calculate regeneration amounts
    hp_regen = calculate_hp_regen_rate(ch) * position_mod
    sp_regen = calculate_sp_regen_rate(ch) * position_mod
    ep_regen = calculate_ep_regen_rate(ch) * position_mod
    
    # Apply regeneration
    old_hp = vit_aux.hp
    old_sp = vit_aux.sp
    old_ep = vit_aux.ep
    
    vit_aux.hp = min(vit_aux.max_hp, vit_aux.hp + hp_regen)
    vit_aux.sp = min(vit_aux.max_sp, vit_aux.sp + sp_regen)
    vit_aux.ep = min(vit_aux.max_ep, vit_aux.ep + ep_regen)
    
    # Notify if significant regeneration occurred (for future feedback)
    hp_gained = vit_aux.hp - old_hp
    sp_gained = vit_aux.sp - old_sp
    ep_gained = vit_aux.ep - old_ep
    
    # Hook: Allow other systems to react to regeneration
    if hp_gained > 0 or sp_gained > 0 or ep_gained > 0:
        hooks.run("vitality_regenerated", hooks.build_info("ch dbl dbl dbl", 
                  (ch, hp_gained, sp_gained, ep_gained)))


def regenerate_all_characters():
    """
    Regenerate vitality for all active characters.
    Called by the pulse system.
    """
    try:
        # Get all characters in the game
        char_list = mudsys.character_list()
        
        for ch in char_list:
            if ch and not ch.is_npc:  # Only regenerate player characters for now
                regenerate_vitality(ch)
    except Exception as e:
        mud.log_string(f"Error in regenerate_all_characters: {str(e)}")
        import traceback
        mud.log_string(traceback.format_exc())


def pulse_hook(info):
    """
    Hook function called by the MUD's pulse system.
    
    Args:
        info: Pulse info string (not used)
    """
    regenerate_all_characters()


def register_regen_pulse():
    """
    Register the regeneration pulse with the MUD's hook system.
    This function should be called during module initialization.
    """
    try:
        # Register for the pulse hook
        hooks.add("pulse", pulse_hook)
        mud.log_string(f"Vitality regeneration registered (every {REGEN_TICK_RATE}s)")
    except Exception as e:
        mud.log_string(f"Failed to register regeneration pulse: {str(e)}")
        import traceback
        mud.log_string(traceback.format_exc())


def show_regen_info(ch):
    """
    Show regeneration information to a character.
    Useful for debugging and player information.
    
    Args:
        ch: Character object
    
    Returns:
        str: Formatted regeneration info
    """
    if not MODULES_AVAILABLE:
        return "Regeneration system not available."
    
    # Get base rates
    hp_rate = calculate_hp_regen_rate(ch)
    sp_rate = calculate_sp_regen_rate(ch)
    ep_rate = calculate_ep_regen_rate(ch)
    
    # Get position modifier
    pos_mod = get_position_modifier(ch)
    position = ch.pos.lower()
    
    # Calculate actual rates
    actual_hp = hp_rate * pos_mod
    actual_sp = sp_rate * pos_mod
    actual_ep = ep_rate * pos_mod
    
    # Build output
    lines = [
        "{c┌─────────────────────────────────────────┐{x",
        "{c│{C        Regeneration Information       {c│{x",
        "{c├─────────────────────────────────────────┤{x",
        f"{{c│{{x Position: {{Y{position:15s}{{x ({pos_mod*100:.0f}%)  {{c│{{x",
        "{c├─────────────────────────────────────────┤{x",
        f"{{c│{{x Base HP Regen: {{G{hp_rate:7.2f}{{x/tick          {{c│{{x",
        f"{{c│{{x Base SP Regen: {{B{sp_rate:7.2f}{{x/tick          {{c│{{x",
        f"{{c│{{x Base EP Regen: {{Y{ep_rate:7.2f}{{x/tick          {{c│{{x",
        "{c├─────────────────────────────────────────┤{x",
        f"{{c│{{x Actual HP Regen: {{G{actual_hp:7.2f}{{x/tick       {{c│{{x",
        f"{{c│{{x Actual SP Regen: {{B{actual_sp:7.2f}{{x/tick       {{c│{{x",
        f"{{c│{{x Actual EP Regen: {{Y{actual_ep:7.2f}{{x/tick       {{c│{{x",
        "{c└─────────────────────────────────────────┘{x"
    ]
    
    return "\r\n".join(lines)


# Admin command to show regeneration info
def cmd_regeninfo(ch, cmd, arg):
    """
    Show regeneration information.
    
    Usage: regeninfo [target]
    """
    # Get target (self if not specified)
    target = ch
    if arg:
        target = ch.room.get_char_by_name(arg)
        if not target:
            ch.send("No one by that name is here.")
            return
    
    ch.send(show_regen_info(target))


def register_commands():
    """Register regeneration-related commands."""
    try:
        mudsys.add_cmd("regeninfo", None, cmd_regeninfo, "player", False)
        mud.log_string("Vitality regeneration commands registered")
    except Exception as e:
        mud.log_string(f"Failed to register regeneration commands: {str(e)}")
        import traceback
        mud.log_string(traceback.format_exc())