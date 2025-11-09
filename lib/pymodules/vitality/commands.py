import mudsys
import mud
from . import vitality_core
from . import vitality_regen
from . import vitality_damage
from . import vitality_injury
from . import death_handler

def cmd_damage(ch, cmd, arg):
    """
    Admin command to damage a mob for testing.
    Usage: damage <target> <amount>
    """
    if ch.room.hasBit("no_combat"):
        ch.send("You cannot fight here!")
        return

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
    
    #if target.is_pc:
    #    ch.send("That's a player, not a mob.")
    #    return
    
    # Get vitality data
    vit_aux = target.getAuxiliary("vitality_data")
    if not vit_aux:
        ch.send("%s has no vitality data." % target.name)
        return
    
    # Apply damage
    #old_hp = vit_aux.hp
    #vit_aux.hp = max(0, vit_aux.hp - damage_amount)
    
    #ch.send("You deal %d damage to %s. HP: %.1f -> %.1f" % 
    #        (damage_amount, target.name, old_hp, vit_aux.hp))
    
    old_hp = vit_aux.hp
    vitality_damage.take_damage(target, damage_amount, "admin_command", ch)
    ch.send("You deal %d damage to %s. HP: %.1f -> %.1f" % 
             (damage_amount, target.name, old_hp, vit_aux.hp))
    
    # Check for death
    #if vit_aux.hp <= 0:
    #    ch.send("%s has been slain!" % target.name)
    #    mud.log_string("%s was killed by admin command" % target.name)
    if vit_aux.is_dead:
        ch.send("%s has been slain!" % target.name)
        # Death handler would go here

def cmd_heal(ch, cmd, arg):
    """
    Admin command to heal a target.
    Usage: heal <target> [hp|sp|ep|all|wounds] [amount]
    
    Examples:
      heal self                    # Full heal (hp, sp, ep, wounds)
      heal kasan hp 50             # Heal 50 HP
      heal self wounds             # Remove all wounds
      heal guard sp 100            # Restore 100 SP
      heal self all                # Full heal everything
    """
    
    if not arg or not arg.strip():
        ch.send("Usage: heal <target> [hp|sp|ep|all|wounds] [amount]")
        return
    
    args = arg.split()
    target_name = args[0].lower()
    
    # Find target
    if target_name in ["self", "me"]:
        target = ch
    else:
        try:
            target = ch.room.get_character(target_name)
        except:
            ch.send("Target '%s' not found." % args[0])
            return
        
        if not target:
            ch.send("Target '%s' not found." % args[0])
            return
    
    # Parse heal type and amount
    heal_type = args[1].lower() if len(args) > 1 else "all"
    
    try:
        heal_amount = int(args[2]) if len(args) > 2 else 9999
    except ValueError:
        ch.send("Heal amount must be a number.")
        return
    
    # Get vitality data
    vit_aux = vitality_core.get_vitality(target)
    if not vit_aux:
        ch.send("%s has no vitality data." % target.name)
        return
    
    # Process heal command
    healed_hp = 0
    healed_sp = 0
    healed_ep = 0
    wounds_removed = 0
    
    if heal_type in ["hp", "all"]:
        old_hp = vit_aux.hp
        vit_aux.hp = min(vit_aux.max_hp, vit_aux.hp + heal_amount)
        healed_hp = vit_aux.hp - old_hp
    
    if heal_type in ["sp", "all"]:
        old_sp = vit_aux.sp
        vit_aux.sp = min(vit_aux.max_sp, vit_aux.sp + heal_amount)
        healed_sp = vit_aux.sp - old_sp
    
    if heal_type in ["ep", "all"]:
        old_ep = vit_aux.ep
        vit_aux.ep = min(vit_aux.max_ep, vit_aux.ep + heal_amount)
        healed_ep = vit_aux.ep - old_ep
    
    if heal_type in ["wounds", "all"]:
        # Remove all wounds
        injury_aux = target.getAuxiliary("injury_data")
        if injury_aux and hasattr(injury_aux, 'wounds'):
            wounds_removed = len(injury_aux.wounds)
            injury_aux.wounds = {}
    
    # Build response message
    if heal_type == "all":
        ch.send("Fully healed %s:" % target.name)
        ch.send("  HP: %.1f -> %.1f" % (vit_aux.hp - healed_hp, vit_aux.hp))
        ch.send("  SP: %.1f -> %.1f" % (vit_aux.sp - healed_sp, vit_aux.sp))
        ch.send("  EP: %.1f -> %.1f" % (vit_aux.ep - healed_ep, vit_aux.ep))
        if wounds_removed > 0:
            ch.send("  Removed %d wounds" % wounds_removed)
    elif heal_type == "wounds":
        if wounds_removed > 0:
            ch.send("Removed %d wounds from %s." % (wounds_removed, target.name))
        else:
            ch.send("%s has no wounds." % target.name)
    elif heal_type == "hp":
        ch.send("Healed %s for %.1f HP (%.1f -> %.1f)" % 
                (target.name, healed_hp, vit_aux.hp - healed_hp, vit_aux.hp))
    elif heal_type == "sp":
        ch.send("Restored %s for %.1f SP (%.1f -> %.1f)" % 
                (target.name, healed_sp, vit_aux.sp - healed_sp, vit_aux.sp))
    elif heal_type == "ep":
        ch.send("Restored %s for %.1f EP (%.1f -> %.1f)" % 
                (target.name, healed_ep, vit_aux.ep - healed_ep, vit_aux.ep))
    else:
        ch.send("Unknown heal type. Options: hp, sp, ep, all, wounds")
        return
    
    mud.log_string("ADMIN: %s healed %s (%s)" % (ch.name, target.name, heal_type))



def cmd_checkdeath(ch, cmd, arg):
    """Admin command to check death status."""
    vit_aux = ch.getAuxiliary("vitality_data")
    if vit_aux:
        ch.send("Dead: %s, Counter: %d" % (vit_aux.is_dead, vit_aux.death_count))
    else:
        ch.send("No vitality data.")

def register_commands():
    # Add to register_commands():
    mudsys.add_cmd("damage", None, cmd_damage, "admin", False)
    mudsys.add_cmd("checkdeath", None, cmd_checkdeath, "admin", False)
    mudsys.add_cmd("heal", None, cmd_heal, "admin", False)