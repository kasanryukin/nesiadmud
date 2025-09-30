"""
Vitality System Implementation

Core vitality system for handling health, spell points, and energy points.
Includes damage, healing, regeneration, death mechanics, and auxiliary data.
"""
import mud, mudsys, auxiliary, storage, event, hooks, char
from .vitality_config import get_vitality_config


################################################################################
# Auxiliary Data
################################################################################
class VitalityAuxData:
    """Holds character vitality data - health, spell points, energy points"""
    
    def __init__(self, set = None):
        # Get config for defaults
        config = get_vitality_config()
        
        # Current stats
        self.hp = config.hp_hitdie if config else 10
        self.maxhp = config.hp_hitdie if config else 10
        self.sp = config.sp_hitdie if config else 10
        self.maxsp = config.sp_hitdie if config else 10
        self.ep = config.ep_hitdie if config else 10
        self.maxep = config.ep_hitdie if config else 10
        
        # Regeneration rates (per heartbeat)
        self.hp_regen = config.hp_regen if config else 1
        self.sp_regen = config.sp_regen if config else 1
        self.ep_regen = config.ep_regen if config else 1
        
        # Death status
        self.dead = False
        
        # Read from storage if provided
        if set != None:
            self.read(set)
    
    def copyTo(self, to):
        """Copy vitality data to another instance"""
        to.hp = self.hp
        to.maxhp = self.maxhp
        to.sp = self.sp
        to.maxsp = self.maxsp
        to.ep = self.ep
        to.maxep = self.maxep
        to.hp_regen = self.hp_regen
        to.sp_regen = self.sp_regen
        to.ep_regen = self.ep_regen
        to.dead = self.dead
    
    def copy(self):
        """Create a copy of this vitality data"""
        newdata = VitalityAuxData()
        self.copyTo(newdata)
        return newdata
    
    def store(self):
        """Store vitality data to a storage set"""
        set = storage.StorageSet()
        set.storeInt("hp", self.hp)
        set.storeInt("maxhp", self.maxhp)
        set.storeInt("sp", self.sp)
        set.storeInt("maxsp", self.maxsp)
        set.storeInt("ep", self.ep)
        set.storeInt("maxep", self.maxep)
        set.storeInt("hp_regen", self.hp_regen)
        set.storeInt("sp_regen", self.sp_regen)
        set.storeInt("ep_regen", self.ep_regen)
        set.storeBool("dead", self.dead)
        return set
    
    def read(self, set):
        """Read vitality data from a storage set"""
        if set.contains("hp"):
            self.hp = set.readInt("hp")
        if set.contains("maxhp"):
            self.maxhp = set.readInt("maxhp")
        if set.contains("sp"):
            self.sp = set.readInt("sp")
        if set.contains("maxsp"):
            self.maxsp = set.readInt("maxsp")
        if set.contains("ep"):
            self.ep = set.readInt("ep")
        if set.contains("maxep"):
            self.maxep = set.readInt("maxep")
        if set.contains("hp_regen"):
            self.hp_regen = set.readInt("hp_regen")
        if set.contains("sp_regen"):
            self.sp_regen = set.readInt("sp_regen")
        if set.contains("ep_regen"):
            self.ep_regen = set.readInt("ep_regen")
        if set.contains("dead"):
            self.dead = set.readBool("dead")

################################################################################
# Core Vitality Functions
################################################################################
def damage_character(ch, amount, stat_type="hp"):
    """Apply damage to a character's vitality stat"""
    aux = ch.getAuxiliary("vitality_data")
    
    # Run pre-damage hooks
    hooks.run("vitality_pre_damage", hooks.build_info("ch int str", (ch, amount, stat_type)))
    
    # Apply damage
    if stat_type == "hp":
        aux.hp = max(0, aux.hp - amount)
    elif stat_type == "sp":
        aux.sp = max(0, aux.sp - amount)
    elif stat_type == "ep":
        aux.ep = max(0, aux.ep - amount)
    
    # Run post-damage hooks
    hooks.run("vitality_post_damage", hooks.build_info("ch int str", (ch, amount, stat_type)))
    
    # Run stat change hooks
    hooks.run("vitality_stat_change", hooks.build_info("ch str int", (ch, stat_type, -amount)))
    
    # Check for death
    if stat_type == "hp" and aux.hp <= 0:
        handle_death(ch)

def heal_character(ch, amount, stat_type="hp"):
    """Apply healing to a character's vitality stat"""
    aux = ch.getAuxiliary("vitality_data")
    
    # Run pre-healing hooks
    hooks.run("vitality_pre_healing", hooks.build_info("ch int str", (ch, amount, stat_type)))
    
    # Apply healing
    if stat_type == "hp":
        old_hp = aux.hp
        aux.hp = min(aux.maxhp, aux.hp + amount)
        actual_heal = aux.hp - old_hp
    elif stat_type == "sp":
        old_sp = aux.sp
        aux.sp = min(aux.maxsp, aux.sp + amount)
        actual_heal = aux.sp - old_sp
    elif stat_type == "ep":
        old_ep = aux.ep
        aux.ep = min(aux.maxep, aux.ep + amount)
        actual_heal = aux.ep - old_ep
    
    # Run post-healing hooks
    hooks.run("vitality_post_healing", hooks.build_info("ch int str", (ch, actual_heal, stat_type)))
    
    # Run stat change hooks
    hooks.run("vitality_stat_change", hooks.build_info("ch str int", (ch, stat_type, actual_heal)))

def handle_death(ch):
    """Handle character death"""
    aux = ch.getAuxiliary("vitality_data")
    aux.dead = True
    
    # Run death hooks
    hooks.run("vitality_death", hooks.build_info("ch", (ch,)))
    
    # Default death behavior
    ch.send("You have died!")
    ch.sendaround(ch.name + " has died!")
    
    # Move to death room
    config = get_vitality_config()
    death_room = config.death_room if config else "limbo@limbo"
    
    try:
        room = mud.get_room(death_room)
        if room:
            ch.char_to_room(room)
            ch.send("You find yourself in the realm of the dead.")
            ch.act("look")
    except:
        mud.log_string("Error moving dead character to death room: " + death_room)

################################################################################
# Regeneration System
################################################################################
def vitality_heartbeat_hook(info):
    """Handle vitality regeneration on heartbeat"""
    config = get_vitality_config()
    if not config:
        return
        
    # Get regen frequency from config
    regen_heartbeat = config.regen_heartbeat
    
    # Only regen every N heartbeats
    if not hasattr(vitality_heartbeat_hook, 'counter'):
        vitality_heartbeat_hook.counter = 0
    
    vitality_heartbeat_hook.counter += 1
    if vitality_heartbeat_hook.counter < regen_heartbeat:
        return
    
    vitality_heartbeat_hook.counter = 0
    
    # Regenerate all characters
    for ch in char.char_list():
        if ch.is_pc and not ch.getAuxiliary("vitality_data").dead:
            regenerate_character(ch)

def regenerate_character(ch):
    """Regenerate a character's vitality stats"""
    aux = ch.getAuxiliary("vitality_data")
    config = get_vitality_config()
    if not config:
        return
    
    # Track if any regeneration occurred and if any stat reached 100%
    regen_occurred = False
    reached_full = []
    
    # Regenerate HP
    if aux.hp < aux.maxhp:
        old_hp = aux.hp
        heal_character(ch, aux.hp_regen, "hp")
        regen_occurred = True
        if aux.hp >= aux.maxhp and old_hp < aux.maxhp:
            reached_full.append("hp")
    
    # Regenerate SP
    if aux.sp < aux.maxsp:
        old_sp = aux.sp
        heal_character(ch, aux.sp_regen, "sp")
        regen_occurred = True
        if aux.sp >= aux.maxsp and old_sp < aux.maxsp:
            reached_full.append("sp")
    
    # Regenerate EP
    if aux.ep < aux.maxep:
        old_ep = aux.ep
        heal_character(ch, aux.ep_regen, "ep")
        regen_occurred = True
        if aux.ep >= aux.maxep and old_ep < aux.maxep:
            reached_full.append("ep")
    
    # Show status if any regeneration occurred and regen_display is enabled
    if regen_occurred and config.regen_display:
        ch.send("[Health: %d/%d  Spell: %d/%d  Energy: %d/%d]" % (aux.hp, aux.maxhp, aux.sp, aux.maxsp, aux.ep, aux.maxep))
    
    # Show 100% messages if regen_display_full is enabled
    if reached_full and config.regen_display_full:
        for stat in reached_full:
            if stat == "hp":
                ch.send(config.get_status_message("hp", aux.hp, aux.maxhp))
            elif stat == "sp":
                ch.send(config.get_status_message("sp", aux.sp, aux.maxsp))
            elif stat == "ep":
                ch.send(config.get_status_message("ep", aux.ep, aux.maxep))

################################################################################
# Character Generation Hook
################################################################################
def init_player_vitality(info):
    """Initialize vitality data for new characters"""
    ch, = hooks.parse_info(info)
    
    config = get_vitality_config()
    if not config:
        return
    
    aux = ch.getAuxiliary("vitality_data")
    aux.hp = config.hp_hitdie
    aux.maxhp = config.hp_hitdie
    aux.sp = config.sp_hitdie
    aux.maxsp = config.sp_hitdie
    aux.ep = config.ep_hitdie
    aux.maxep = config.ep_hitdie
    aux.hp_regen = config.hp_regen
    aux.sp_regen = config.sp_regen
    aux.ep_regen = config.ep_regen
    aux.dead = False

################################################################################
# Commands
################################################################################
def cmd_hp(ch, cmd, arg):
    """Display character's current vitality status"""
    aux = ch.getAuxiliary("vitality_data")
    config = get_vitality_config()
    
    ch.send("Health:  %d/%d" % (aux.hp, aux.maxhp))
    ch.send("Spell:   %d/%d" % (aux.sp, aux.maxsp))
    ch.send("Energy:  %d/%d" % (aux.ep, aux.maxep))
    ch.send("")
    
    if config:
        ch.send(config.get_status_message("hp", aux.hp, aux.maxhp))
        ch.send(config.get_status_message("sp", aux.sp, aux.maxsp))
        ch.send(config.get_status_message("ep", aux.ep, aux.maxep))

def cmd_damage(ch, cmd, arg):
    """Admin command to damage a character"""
    args = arg.split()
    
    if len(args) < 2:
        ch.send("Usage: damage <target> <amount> [hp|sp|ep]")
        return
    
    target_name = args[0]
    try:
        amount = int(args[1])
    except ValueError:
        ch.send("Amount must be a number.")
        return
    
    stat_type = args[2] if len(args) > 2 else "hp"
    
    if stat_type not in ["hp", "sp", "ep"]:
        ch.send("Stat type must be hp, sp, or ep")
        return
    
    # Find target using mud.generic_find like socials
    try:
        target, type = mud.generic_find(ch, target_name, "all", "immediate", False)
    except UnicodeDecodeError:
        target = None
        type = None
    
    if target is None or type != "char":
        ch.send("The person, %s, could not be found." % target_name)
        ch.send("Usage: damage <target> <amount> [hp|sp|ep]")
        return
    
    # Set damage messages based on stat type
    if stat_type == "hp":
        damage_msg = "You feel pain surge through your body!"
    elif stat_type == "sp":
        damage_msg = "You feel your mental energy drain away!"
    elif stat_type == "ep":
        damage_msg = "You feel exhaustion wash over you!"
    
    damage_character(target, amount, stat_type)
    ch.send("Damaged %s for %d %s." % (target.name, amount, stat_type))
    if target != ch:
        target.send(damage_msg)

def cmd_pray(ch, cmd, arg):
    """Prayer command to revive dead players in death room"""
    aux = ch.getAuxiliary("vitality_data")
    config = get_vitality_config()
    death_room = config.death_room if config else "limbo@limbo"
    
    # Check for divine argument and admin privileges
    is_divine = arg.strip().lower() == "divine"
    is_privileged = (ch.isInGroup("admin") or ch.isInGroup("wizard") or 
                    ch.isInGroup("scripter") or ch.isInGroup("builder"))
    
    # Check location requirements first
    current_room = str(ch.room)
    in_death_room = current_room == death_room
    can_use_anywhere = is_divine and is_privileged
    
    # If not dead, return -1 to allow fallthrough (except for divine users)
    if not aux.dead and not in_death_room and not is_divine:
        return -1
    
    # Divine users who are not dead get a message
    if not aux.dead and is_divine:
        ch.send("You are not dead. There is no need to pray for revival.")
        return
   
    if not can_use_anywhere and not in_death_room:
        ch.send("The gods do not hear your prayers here. You must be in the realm of the dead.")
        return
    
    
    # Revive the player
    aux.dead = False
    aux.hp = 1
    aux.sp = 1
    aux.ep = 1
    
    # Run revival hooks
    hooks.run("vitality_revival", hooks.build_info("ch", (ch,)))
    
    # Send appropriate messages based on revival type
    if is_divine and is_privileged:
        ch.send("Your divine powers restore your life force!")
        ch.sendaround(ch.name + " is restored by divine power!")
    else:
        ch.send("Your prayers are answered! You feel life returning to your body.")
        ch.sendaround(ch.name + " is revived by divine intervention!")
    
    # Move back to start room
    start_room = mudsys.sys_getval("start_room") or "limbo@limbo"
    try:
        room = mud.get_room(start_room)
        if room:
            ch.char_to_room(room)
            ch.send("You find yourself back among the living.")
            ch.act("look")
    except:
        mud.log_string("Error moving revived character to start room: " + start_room)

def cmd_heal(ch, cmd, arg):
    """Admin command to heal a character"""
    args = arg.split()
    
    if len(args) < 2:
        ch.send("Usage: heal <target> <amount> [hp|sp|ep]")
        return
    
    target_name = args[0]
    try:
        amount = int(args[1])
    except ValueError:
        ch.send("Amount must be a number.")
        return
    
    stat_type = args[2] if len(args) > 2 else "hp"
    
    if stat_type not in ["hp", "sp", "ep"]:
        ch.send("Stat type must be hp, sp, or ep")
        return
    
    # Find target using mud.generic_find like socials
    try:
        target, type = mud.generic_find(ch, target_name, "all", "immediate", False)
    except UnicodeDecodeError:
        target = None
        type = None
    
    if target is None or type != "char":
        ch.send("The person, %s, could not be found." % target_name)
        ch.send("Usage: heal <target> <amount> [hp|sp|ep]")
        return
    
    # Check current stats to calculate actual healing needed
    aux = target.getAuxiliary("vitality_data")
    
    if stat_type == "hp":
        current = aux.hp
        maximum = aux.maxhp
        feeling_msg = "You feel healthier!"
    elif stat_type == "sp":
        current = aux.sp
        maximum = aux.maxsp
        feeling_msg = "You feel more focused!"
    elif stat_type == "ep":
        current = aux.ep
        maximum = aux.maxep
        feeling_msg = "You feel more refreshed!"
    
    # Calculate actual healing needed
    needed = maximum - current
    actual_heal = min(amount, needed)
    
    if needed <= 0:
        ch.send("%s is already at full %s." % (target.name, stat_type))
        return
    
    # Apply healing
    heal_character(target, actual_heal, stat_type)
    
    # Send appropriate messages
    if actual_heal < amount:
        ch.send("Tried to heal %s for %d %s, but only %d was needed." % (target.name, amount, stat_type, actual_heal))
    else:
        ch.send("Healed %s for %d %s." % (target.name, actual_heal, stat_type))
    
    if target != ch:
        target.send(feeling_msg)

################################################################################
# Initialization
################################################################################

# Install auxiliary data
auxiliary.install("vitality_data", VitalityAuxData, "character")

# Add hooks
hooks.add("init_player", init_player_vitality)
hooks.add("heartbeat", vitality_heartbeat_hook)

# Add commands
mudsys.add_cmd("hp", None, cmd_hp, "player", False)
mudsys.add_cmd("damage", None, cmd_damage, "admin", False)
mudsys.add_cmd("heal", None, cmd_heal, "admin", False)
mudsys.add_cmd("pray", None, cmd_pray, "player", False)

def __unload__():
    """Clean up when module is unloaded"""
    hooks.remove("init_player", init_player_vitality)
    hooks.remove("heartbeat", vitality_heartbeat_hook)
