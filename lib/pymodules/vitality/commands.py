import mudsys
import mud
from . import vitality_core
from . import vitality_regen


def cmd_damage(ch, cmd, arg):
    """
    Admin command to damage a mob for testing.
    Usage: damage <target> <amount>
    """
    if not arg or not arg.strip():
        ch.send("Usage: damage <target> <amount>")
        return
    
    parts = arg.split()
    if len(parts) < 2:
        ch.send("Usage: damage <target> <amount>")
        return
    
    target_name = parts[0]
    try:
        damage_amount = int(parts[1])
    except ValueError:
        ch.send("Damage amount must be a number.")
        return
    
    # Find the target mob in the room
    target = None
    for char in ch.room.chars:
        if target_name.lower() in char.name.lower():
            target = char
            break
    
    if not target:
        ch.send("That target is not here.")
        return
    
    if target.is_pc:
        ch.send("That's a player, not a mob.")
        return
    
    # Get vitality data
    vit_aux = target.getAuxiliary("vitality_data")
    if not vit_aux:
        ch.send("%s has no vitality data." % target.name)
        return
    
    # Apply damage
    old_hp = vit_aux.hp
    vit_aux.hp = max(0, vit_aux.hp - damage_amount)
    
    ch.send("You deal %d damage to %s. HP: %.1f -> %.1f" % 
            (damage_amount, target.name, old_hp, vit_aux.hp))
    
    # Check for death
    if vit_aux.hp <= 0:
        ch.send("%s has been slain!" % target.name)
        mud.log_string("%s was killed by admin command" % target.name)
        # Death handler would go here

def register_commands():
    # Add to register_commands():
    mudsys.add_cmd("damage", None, cmd_damage, "admin", False)