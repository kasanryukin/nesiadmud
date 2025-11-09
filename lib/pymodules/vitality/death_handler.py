"""
Death Handler Module
====================
Manages character death, respawn, and death messages.
"""

import mud
import hooks
import mudsys
from . import vitality_core


# Configuration
RESPAWN_DELAY = 5  # Heartbeats before respawn
RESPAWN_ROOM = "grandaltar@gtyr"  # Default respawn location


def setup_death_hooks():
    """Register death handler to listen for on_death hook"""
    hooks.add("on_death", handle_death)
    mud.log_string("Death handler registered for on_death hook")


def handle_death(info_string):
    """
    Handle character death.
    Called when on_death hook fires (HP <= 0).
    
    Args:
        info_string: Hook info string formatted by build_info (parsed by parse_info)
    """
    try:
        # Parse the hook info string back into objects
        # Format was: "ch ch str" -> (victim_ch, source_ch, damage_type_str)
        parsed = hooks.parse_info(info_string)
        
        if len(parsed) < 3:
            mud.log_string("ERROR: Death hook received invalid info: %s" % info_string)
            return
        
        ch = parsed[0]
        source = parsed[1]
        damage_type = parsed[2]
        
    except Exception as e:
        mud.log_string("ERROR: Failed to parse death hook info: %s" % str(e))
        return
    
    # Validate we have a valid character
    if not ch or not hasattr(ch, 'name'):
        mud.log_string("ERROR: Death handler received invalid character object")
        return
    
    mud.log_string("DEATH HANDLER: Processing death for %s" % ch.name)
    
    # Get vitality data
    vit_aux = ch.getAuxiliary("vitality_data")
    if not vit_aux:
        mud.log_string("ERROR: Death handler called but no vitality data for %s" % ch.name)
        return
    
    # Set death state
    vit_aux.is_dead = True
    vit_aux.death_count = RESPAWN_DELAY
    
    # Get death messages from the character (or use defaults)
    death_msg_self = get_death_message(ch, "death_msg_self", "%m is slain!")
    death_msg_room = get_death_message(ch, "death_msg_room", "%n has slain %m!")
    
    # Format messages
    formatted_self = format_death_message(death_msg_self, ch, source)
    formatted_room = format_death_message(death_msg_room, ch, source)
    
    # Send death messages
    if hasattr(ch, 'send'):
        ch.send("\n{r" + formatted_self + "{n\n")
    
    # Send to room (everyone except the dead character)
    if hasattr(ch, 'room') and ch.room and hasattr(ch.room, 'chars'):
        for other in ch.room.chars:
            if other != ch and hasattr(other, 'send'):
                other.send("{r" + formatted_room + "{n")
    
    mud.log_string("DEATH: %s killed by %s (%s damage)" % 
                   (ch.name, get_source_name(source), damage_type))
    
    # Handle NPCs vs Players differently
    if ch.is_npc:
        # NPCs are simply extracted - zone resets will handle respawning
        mud.log_string("DEATH: %s (NPC) extracted. Zone reset will respawn." % ch.name)
        mud.extract(ch)
    else:
        # Players respawn after a delay
        vit_aux.death_count = RESPAWN_DELAY
        mud.log_string("DEATH: %s (Player) will respawn in %d heartbeats" % (ch.name, RESPAWN_DELAY))
        #TODO: Actually kill players and respawn them once the ghost system is implemented.

def get_death_message(ch, attr_name, default):
    """
    Get a death message from a character attribute, or use default.
    
    Args:
        ch: Character
        attr_name: Attribute name (like "death_msg_self")
        default: Default message if attribute doesn't exist
    
    Returns:
        str: Death message
    """
    try:
        return getattr(ch, attr_name, default)
    except:
        return default


def format_death_message(message, victim, killer):
    """
    Format a death message with placeholders.
    
    Placeholders:
        %m - victim name
        %n - killer name
        %t - generic target
    
    Args:
        message: Message template with placeholders
        victim: Character who died
        killer: Who/what killed them (or None)
    
    Returns:
        str: Formatted message
    """
    result = message
    result = result.replace("%m", victim.name)
    result = result.replace("%n", get_source_name(killer))
    result = result.replace("%t", victim.name)
    return result


def get_source_name(source):
    """
    Get a readable name for the damage source.
    
    Args:
        source: Can be a character, object, or string
    
    Returns:
        str: Name of the source
    """
    if source is None:
        return "an unknown force"
    
    # Try to get name attribute (works for chars and objects)
    try:
        return source.name
    except:
        pass
    
    # If it's a string, return it
    if isinstance(source, str):
        return source
    
    return "something"


def check_respawn(ch):
    """
    Check if a dead character should respawn.
    Called from character heartbeat.
    
    Args:
        ch: Character to check
    """
    vit_aux = ch.getAuxiliary("vitality_data")
    if not vit_aux:
        return
    
    # Not dead, nothing to do
    if not vit_aux.is_dead:
        return
    
    # Decrement counter
    vit_aux.death_count -= 1
    
    # Time to respawn?
    if vit_aux.death_count <= 0:
        respawn_character(ch)


def respawn_character(ch):
    """
    Respawn a dead character at the respawn location.
    
    Args:
        ch: Character to respawn
    """
    vit_aux = ch.getAuxiliary("vitality_data")
    if not vit_aux:
        return
    
    mud.log_string("RESPAWN: Respawning %s at %s" % (ch.name, RESPAWN_ROOM))
    
    # Restore vitality
    vit_aux.hp = vit_aux.max_hp
    vit_aux.sp = vit_aux.max_sp
    vit_aux.ep = vit_aux.max_ep
    vit_aux.is_dead = False
    vit_aux.death_count = 0
    
    # Move to respawn location
    try:
        respawn_room = mudsys.get_room(RESPAWN_ROOM)
        if respawn_room:
            ch.room = respawn_room
            if hasattr(ch, 'send'):
                ch.send("\n{gYou have been resurrected!{n\n")
            if hasattr(ch, 'act'):
                ch.act("look")
            
            # Announce arrival
            if hasattr(ch.room, 'chars'):
                for other in ch.room.chars:
                    if other != ch and hasattr(other, 'send'):
                        other.send("%s materializes in a flash of light!" % ch.name)
        else:
            mud.log_string("ERROR: Respawn room %s not found!" % RESPAWN_ROOM)
    except Exception as e:
        mud.log_string("ERROR: Failed to respawn %s: %s" % (ch.name, str(e)))