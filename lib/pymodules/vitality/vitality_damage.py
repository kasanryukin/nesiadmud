"""
Vitality Damage System
======================
Handles damage application and death detection with hook support.
"""

import mud
import hooks


def take_damage(ch, amount, damage_type="physical", source=None):
    """
    Apply damage to a character and fire appropriate hooks.
    
    Args:
        ch: Character taking damage
        amount: Damage amount (float or int)
        damage_type: Type of damage (physical, magical, fire, etc.)
        source: Who/what dealt the damage (character, object, or string description)
    
    Returns:
        bool: True if damage was applied, False if character has no vitality data
    """
    vit_aux = ch.getAuxiliary("vitality_data")
    if not vit_aux:
        mud.log_string("take_damage: %s has no vitality data" % ch.name)
        return False
    
    # Don't damage if already dead
    if vit_aux.is_dead:
        return False
    
    old_hp = vit_aux.hp
    vit_aux.hp = max(0, vit_aux.hp - amount)
    
    mud.log_string("DAMAGE: %s took %.1f %s damage (%.1f -> %.1f HP)" % 
                   (ch.name, amount, damage_type, old_hp, vit_aux.hp))
    
    # Fire damage hook for combat effects, spells, etc.
    # Systems can listen to this to apply damage reduction, shields, etc.
    damage_info = hooks.build_info("ch int str ch", 
                                    (ch, amount, damage_type, source))
    hooks.run("on_damage", damage_info)
    
    # Check for death - only trigger if we just died (wasn't already at 0)
    if vit_aux.hp <= 0 and old_hp > 0:
        vit_aux.is_dead = True
        mud.log_string("DEATH: %s has died from %s damage" % (ch.name, damage_type))
        
        # Fire death hook - death handler will process this
        death_info = hooks.build_info("ch ch str", 
                                      (ch, source, damage_type))
        hooks.run("on_death", death_info)
    
    return True


def heal_damage(ch, amount, heal_type="healing"):
    """
    Restore HP to a character.
    
    Args:
        ch: Character being healed
        amount: Amount to heal
        heal_type: Type of healing (healing, regeneration, etc.)
    
    Returns:
        bool: True if healing was applied
    """
    vit_aux = ch.getAuxiliary("vitality_data")
    if not vit_aux:
        return False
    
    # Don't heal dead characters with normal healing
    if vit_aux.is_dead and heal_type != "resurrection":
        return False
    
    old_hp = vit_aux.hp
    vit_aux.hp = min(vit_aux.max_hp, vit_aux.hp + amount)
    
    actual_healed = vit_aux.hp - old_hp
    if actual_healed > 0:
        mud.log_string("HEAL: %s healed %.1f HP (%.1f -> %.1f)" % 
                       (ch.name, actual_healed, old_hp, vit_aux.hp))
    
    return True


def is_dead(ch):
    """Check if a character is dead."""
    vit_aux = ch.getAuxiliary("vitality_data")
    if not vit_aux:
        return False
    return vit_aux.is_dead


def get_hp_percentage(ch):
    """Get character's HP as a percentage (0-100)."""
    vit_aux = ch.getAuxiliary("vitality_data")
    if not vit_aux or vit_aux.max_hp <= 0:
        return 100.0
    return (vit_aux.hp / vit_aux.max_hp) * 100.0

