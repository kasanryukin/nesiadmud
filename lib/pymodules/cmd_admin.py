'''
cmd_admin.py

commands available only to admins.
'''
import mudsys, inform, string, mudsock, mud, hooks, display, utils
import room as mudroom
import char as mudchar
import obj  as mudobj

def search_containers_for_object(ch, target_name):
    """
    Manually search for objects inside containers.
    Search order: room containers first, then inventory containers.
    Only searches one level deep.
    Returns (found_object, "obj") or (None, None) if not found.
    """
    # First search containers in the room
    room = ch.room
    for container in room.objs:
        # Check if this object is a container type
        try:
            if container.istype("container"):
                # Search inside this container
                for obj in container.contents:
                    if utils.is_keyword(obj.keywords, target_name, True):
                        return obj, "obj"
        except:
            # Skip if not a valid object or container check fails
            continue
    
    # Then search containers in inventory
    for container in ch.inv:
        # Check if this object is a container type
        try:
            if container.istype("container"):
                # Search inside this container
                for obj in container.contents:
                    if utils.is_keyword(obj.keywords, target_name, True):
                        return obj, "obj"
        except:
            # Skip if not a valid object or container check fails
            continue
    
    return None, None



################################################################################
# local variables
################################################################################

# a list of current instances, and their source zones
curr_instances = [ ]



################################################################################
# game commands
################################################################################
def cmd_shutdown(ch, cmd, arg):
    '''Shuts the mud down.'''
    mudsys.do_shutdown()

def cmd_shutdown_net(ch, cmd, arg):
    '''A trap to make sure we spell shutdown out completely.'''
    ch.send("You must spell out shutdown completely!")

def cmd_copyover(ch, cmd, arg):
    '''Restarts the mud, and keep all sockets connected.''' 
    mudsys.do_copyover()

def cmd_copyover_net(ch, cmd, arg):
    '''A trap to make sure we spell copyover out completely.'''
    ch.send("You must spell out copyover completely!")

def cmd_repeat(ch, cmd, arg):
    '''Usage: repeat <times> <command>

       Attempts to perform a single command multiple times. For example, one
       may want to load 20 copies of an item:

         > repeat 20 load obj beer@drinks
       '''
    try:
        times, arg = mud.parse_args(ch, True, cmd, arg, "int(times) string(command)")
    except: return

    if times < 1:
        ch.send("Commands may only be repeated a positive number of times.")
    else:
        for i in range(times):
            ch.act(arg, True)

def cmd_pulserate(ch, cmd, arg):
    '''Usage: pulserate <pulses>
    
      Changes the number of pulses the mud experiences each second. The mud
      makes one loop through the main game handler each pulse.
      '''
    if arg == '':
        ch.send("The mud currently has "+mudsys.sys_getval("pulses_per_second")+
                " pulses per second.")
    else:
        pulserate = string.atoi(arg)
        if pulserate == 0 or 1000 % pulse != 0:
            ch.send("The number of pulses per second must divide 1000.")
        else:
            mudsys.sys_setval("pulses_per_second", str(pulserate))
            ch.send("The mud's new pulse rate is %d pulses per second." %
                    pulserate)

def cmd_lockdown(ch, cmd, arg):
    '''Usage: lockdown [allowed groups | off]

       Locks the game for anyone not a member of one of the user groups
       specified. No argument will list all the user groups locked out of the
       mud. The off argument will remove all lockdowns.'''
    if arg == '':
        lockdown = mudsys.sys_getval("lockdown")
        if lockdown == '':
            ch.send("Lockdown is currently off.")
        else:
            ch.send("Lockdown is currently to members not of: " + lockdown)
            ch.send("To turn off lockdown, use {clockdown off{n")

    elif arg.lower() == "off":
        ch.send("Lockdown disabled.")
        mudsys.sys_setval("lockdown", "")

    # make sure we're not locking ourself out
    elif not ch.isInGroup(arg):
        ch.send("You cannot lock yourself out!")

    else:
        ch.send("MUD locked down to everyone not in groups: " + arg)
        mudsys.sys_setval("lockdown", arg)

        # kick out everyone who we've just locked out
        for ch in mudchar.char_list():
            if ch.is_pc and not ch.isInGroup(arg):
                ch.send("The mud has just been locked down to you.")
                mudsys.do_save(ch)
                mudsys.do_disconnect(ch)
                extract(ch)

def cmd_at(ch, cmd, arg):
    '''Usage: at <person | place> <command>

       Perform a command at another room or person while never leaving your
       current room.'''
    try:
        found, type, arg = mud.parse_args(ch, True, cmd, arg,
                                          "{ room ch.world.noself } string(command)")
    except: return

    # figure out what room we're doing the command at
    if type == "char":
        room = found.room
    else:
        room = found

    # transfer us over to the new room, do the command, then transfer back
    old_room = ch.room
    ch.room  = room
    ch.act(arg, True)
    ch.room  = old_room

def try_force(ch, vict, cmd):
    '''tries to force a person to do something'''
    if ch == vict:
        ch.send("Why don't you just try doing it?")
    elif vict.isInGroup("admin"):
        ch.send("But " + ch.see_as(vict) + " has just as many priviledges as you!")
    else:
        ch.send("You force " + vict.name + " to '" + cmd + "'")
        vict.send(vict.see_as(ch) + " forces you to '" + cmd + "'")
        vict.act(cmd, False)

def cmd_force(ch, cmd, arg):
    '''Usage: force <person> <command>
    
       Attempts to make the specified perform a command of your choosing.'''
    try:
        found, multi, arg = mud.parse_args(ch, True, cmd, arg,
                                           "ch.world.noself.multiple string(command)")
    except: return

    if multi == False:
        try_force(ch, found, arg)
    else:
        for vict in found:
            try_force(ch, vict, arg)

def cmd_goto(ch, cmd, arg):
    '''Usage: goto <person | place | thing>

       Transfer yourself to a specified room, object, or person in game. Rooms
       are referenced by their zone key.
       '''
    try:
        found, type = mud.parse_args(ch, True, cmd, arg, "{ room ch.world.noself }")
    except: return

    # what did we find?
    if type == "char":
        dest = found.room
    else:
        dest = found

    mud.message(ch, None, None, None, True, "to_room",
                "$n disappears in a puff of smoke.")
    ch.room = dest
    ch.act("look")
    mud.message(ch, None, None, None, True, "to_room",
                "$n appears in a puff of smoke.")
    hooks.run("enter", hooks.build_info("ch rm", (ch, ch.room)))
    
def do_transfer(ch, tgt, dest):
    '''ch transfers tgt to dest'''
    if tgt.room == dest:
        ch.send(ch.see_as(tgt) + " is already there")
    else:
        tgt.send(tgt.see_as(ch) + " has transferred you to " + dest.name)
        mud.message(tgt, None, None, None, True, "to_room",
                    "$n disappears in a puff of smoke.")
        tgt.room = dest
        tgt.act("look", False)
        mud.message(tgt, None, None, None, True, "to_room",
                    "$n arrives in a puff of smoke.")

def cmd_transfer(ch, cmd, arg):
    '''Usage: transfer <person> [[to] room]

       The opposite of goto. Instead of moving to a specified location, it
       takes the target to the user. If an additional argument is supplied,
       instead transfers the target to the specifie room.'''
    try:
        found, multi, dest = mud.parse_args(ch, True, cmd, arg,
                                            "ch.world.multiple.noself | [to] room")
    except: return

    # if we didn't supply a room, use our own
    if dest == None:
        dest = ch.room

    # do our transfers
    if multi == False:
        do_transfer(ch, found, dest)
    else:
        for tgt in found:
            do_transfer(ch, tgt, dest)

def cmd_eval(ch, cmd, arg):
    '''Usage: eval <python statement>

       Evaluates a Python statement and sends its return value to the user.
       For example:

       > eval "Your name is " + ch.name
       Evaluation: Your name is Alister

       > eval dir()
       Evaluation: ['arg', 'ch', 'cmd']

       > eval dir(ch)
       '''
    if arg == "":
        ch.send("What python statement do you want to evaluate?")
    else:
        ret = eval(arg)
        ch.send("Evaluation: " + str(ret))

def cmd_exec(ch, cmd, arg):
    '''Usage: exec <python statement>

       Execute any one-line python statement.'''
    if arg == "":
        ch.send("What python statement do you want to evaluate?")
    else:
        exec(arg)
        ch.send("Command executed.")

def cmd_instance(ch, cmd, arg):
    '''Create an instanced version of the specified room'''
    try:
        source, dest = mud.parse_args(ch, True, cmd, arg, "word(source) [as] word(dest)")
    except: return

    room = mudroom.instance(source, dest)
    ch.send("You instance " + source + " as " + room.proto + ".")

def do_zinstance(zone):
    '''create a new instance of the specified zone.'''
    # sanitize the zone key
    if sum([(not v in string.ascii_letters+string.digits+"_") for v in zone]):
        return None
    elif len(zone) == 0:
        return None

    # find all of our room keys
    rnames = mudsys.list_zone_contents(zone, "rproto")
    if len(rnames) == 0:
        return None
            
    to_instance = [ ]
    for name in rnames:
        key = name + "@" + zone
        if not mudroom.is_abstract(key):
            to_instance.append(name)

    # instantiate and reset all of the relevant rooms
    uid     = mudsys.next_uid()
    inszone = zone + str(uid)
    for name in to_instance:
        key = name + "@" + zone
        ins = name + "@" + inszone
        rm  = mudroom.instance(key, ins)
        rm.reset()

    # append this to the list of instanced zones
    curr_instances.append((inszone, zone))

    # success
    return inszone

def cmd_zinstance(ch, cmd, arg):
    '''create an instanced copy of the specified zone.'''
    if arg == "":
        if len(curr_instances) == 0:
            ch.send("No zones currently instanced.")
        else:
            ch.send("{w %-40s %36s " % ("Instance", "Source"))
            ch.send("{b" + display.seperator)
            for pair in curr_instances:
                ch.send("{c %-40s %36s{n" % pair)
        return

    # try creating the instance, and returning the zone key
    instance = do_zinstance(arg)
        
    if instance != None:
        ch.send("Zone has been instanced with zone key, %s. zinstance for a list of current instances." % instance)
    elif sum([(not v in string.ascii_letters+string.digits+"_") for v in arg]):
        ch.send("Invalid zone key.")
    elif len(mudsys.list_zone_contents(arg, "rproto")):
        ch.send("Source zone contained no rooms to instance.")
    else:
        ch.send("Socket %d was not found." % uid)


def cmd_connections(ch, cmd, arg):
    '''lists all of the currently connected sockets, their status, and where
       they are connected from.'''

    tosend = [ ]

    fmt = " %2s   %-11s %-11s %-11s %s"

    tosend.append(("{w"+fmt) % ("Id", "Character", "Account", "Status", "Host"))
    tosend.append("{b" + display.seperator + "{c")
    for sock in mudsock.socket_list():
        chname  = "none"
        accname = "none"
        state   = sock.state
        host    = sock.hostname
        id      = sock.uid

        if sock.ch != None:
            chname  = sock.ch.name
        if sock.account != None:
            accname = sock.account.name
        tosend.append(fmt % (id, chname, accname, state, host))
    tosend.append("{n")
    ch.page("\r\n".join(tosend))

def cmd_disconnect(ch, cmd, arg):
    """Usage: disconnect <uid>

       Disconnects a socket with the given uid. Use 'connections' to see
       current connected sockets."""
    try:
        uid, = mud.parse_args(ch, True, cmd, arg, "int(uid)")
    except: return

    for sock in mudsock.socket_list():
        if sock.uid == uid:
            ch.send("You disconnect socket %d." % uid)
            sock.close()
            break

def cmd_clone(ch, cmd, arg):
    """Usage: clone <prototype_key>
    
       Creates a copy of the specified prototype. Automatically detects whether
       the prototype is a mobile or object. The key should be in the format
       name@zone or just name (uses current zone).
       
       Examples:
         > clone guard@castle
         > clone sword@weapons
         > clone beer (uses current zone)
    """
    if not arg or not arg.strip():
        ch.send("What did you want to clone?")
        return
        
    # Parse the key - handle both full keys (name@zone) and relative keys (name)
    key = arg.strip()
    
    # If no @ symbol, use the current room's zone
    if '@' not in key:
        current_zone = ch.room.proto.split('@')[-1] if '@' in ch.room.proto else 'default'
        key = key + '@' + current_zone
    
    # Split into name and zone
    try:
        name, zone = key.split('@', 1)
    except ValueError:
        ch.send("Invalid prototype key format. Use 'name@zone' or just 'name'.")
        return
    
    # Check if it's a malformed key (basic validation)
    if not name or not zone:
        ch.send("You entered a malformed content key.")
        return
    
    # Check what types exist for this key
    try:
        mob_list = mudsys.list_zone_contents(zone, "mproto")
        obj_list = mudsys.list_zone_contents(zone, "oproto")
    except:
        ch.send("Could not access zone '%s'." % zone)
        return
    
    is_mob = name in mob_list
    is_obj = name in obj_list
    
    if is_mob and is_obj:
        ch.send("Ambiguous prototype key '%s' - exists as both mobile and object. Please use 'load mob %s' or 'load obj %s' instead." % (key, key, key))
        return
    elif is_mob:
        # Load mobile
        try:
            mob = mudchar.load_mob(key, ch.room)
            if mob:
                ch.send("You clone %s." % mob.name)
            else:
                ch.send("Failed to create mobile from prototype '%s'." % key)
        except Exception as e:
            ch.send("Error creating mobile: %s" % str(e))
    elif is_obj:
        # Load object
        try:
            obj = mudobj.load_obj(key, ch)
            if obj:
                ch.send("You clone %s." % obj.name)
            else:
                ch.send("Failed to create object from prototype '%s'." % key)
        except Exception as e:
            ch.send("Error creating object: %s" % str(e))
    else:
        ch.send("No prototype exists with key '%s'. Checked both mobile and object prototypes in zone '%s'." % (key, zone))

def cmd_purge(ch, cmd, arg):
    """Usage: purge [target]
           zap [target]
    
       Removes objects or characters from the game. If no target is specified,
       purges all objects and non-player characters from the current room.
       
       Safety: Cannot purge players or characters with equal/higher privileges.
       
       Examples:
         > purge           # Purge entire room
         > purge guard     # Purge specific character
         > zap sword       # Purge specific object
    """
    if not arg or not arg.strip():
        # Purge everything in the current room
        room = ch.room
        
        ch.send("You purge the room.")
        mud.message(ch, None, None, None, True, "to_room",
                   "$n raises $s arms, and white flames engulf the entire room.")
        
        # Purge all objects in the room - create copy to avoid iteration issues
        objects_to_purge = list(room.objs)
        for obj in objects_to_purge:
            mud.extract(obj)
        
        # Purge all NPCs in the room (but not players or the purger)
        chars_to_purge = []
        for target in room.chars:
            if target != ch and not target.is_pc:
                chars_to_purge.append(target)
        
        for target in chars_to_purge:
            mud.extract(target)
            
    else:
        # Try to find the target - now searches inventory, room, and equipped
        found = None
        found_type = None
        
        # First try parse_args for direct searches (inventory, room, equipped)
        try:
            found, found_type = mud.parse_args(ch, True, cmd, arg, "{ ch.room.noself obj.room.inv.eq }")
        except:
            # parse_args failed, will try container search below
            pass
        
        # If parse_args didn't find anything, manually search containers
        if found is None:
            found, found_type = search_containers_for_object(ch, arg)
        
        if found_type == "char":
            # Purging a character - check privileges
            target = found
            
            # Handle player characters (zap functionality)
            if target.is_pc:
                # Cannot zap yourself
                if target == ch:
                    ch.send("You cannot zap yourself.")
                    return
                
                # Check privileges - can only zap players with lower privileges
                if not utils.has_more_user_groups(ch, target):
                    pronoun = "He" if target.sex == "male" else ("She" if target.sex == "female" else "They")
                    ch.send("You cannot zap %s. %s has equal or higher privileges than you." % 
                           (target.name, pronoun))
                    return
                
                # Get the target's socket
                target_sock = None
                for sock in mudsock.socket_list():
                    if sock.ch == target:
                        target_sock = sock
                        break
                
                if target_sock is None:
                    ch.send("%s is not connected." % target.name)
                    return
                
                # Send dramatic zap messages
                admin_pronoun = "his" if ch.sex == "male" else ("her" if ch.sex == "female" else "their")
                
                # Message to the target being zapped
                target.send("{R%s raises %s hands and you feel yourself engulfed in white flames!{n" % 
                           (ch.name, admin_pronoun))
                
                # Message to the admin
                ch.send("You raise your hands and engulf %s in white flames, disconnecting them." % target.name)
                
                # Message to the room (excluding admin and target)
                mud.message(ch, target, None, None, True, "to_room",
                           "$n raises $s hands and white flames engulf $N before $E vanishes!")
                
                # Save and disconnect the target properly
                mudsys.do_save(target)
                mudsys.do_disconnect(target)
                return
                
            # Handle NPCs (original purge functionality)
            # Check if target has equal or higher privileges (only for PCs, not NPCs)
            if not target.is_npc and not utils.has_more_user_groups(ch, target):
                pronoun = "He" if target.sex == "male" else ("She" if target.sex == "female" else "It")
                ch.send("Erm, you better not try that on %s. %s has just as much privileges as you." % 
                       (target.name, pronoun))
                return
                
            ch.send("You purge %s." % target.name)
            mud.message(ch, target, None, None, True, "to_room",
                       "$n raises $s arms, and white flames engulf $N.")
            mud.extract(target)
            
        elif found_type == "obj":
            # Purging an object - detect location for appropriate messaging
            obj = found
            
            # Determine where the object is located for messaging
            if obj.wearer == ch:
                # Object is equipped/worn by the character
                ch.send("You remove %s from your body and hold it up as white flames engulf it." % obj.name)
                mud.message(ch, None, obj, None, True, "to_room",
                           "$n removes $o from $s body and raises it as white flames engulf it.")
            elif obj.container:
                # Object is inside a container - check where the container is
                container = obj.container
                if container.carrier == ch:
                    # Container is in character's inventory
                    ch.send("You take %s out of %s and hold it up as white flames engulf it." % (obj.name, container.name))
                    mud.message(ch, None, obj, container, True, "to_room",
                               "$n takes $o out of a $O and white flames engulf it.")
                else:
                    # Container is in the room
                    ch.send("You take %s out of %s and hold it up as white flames engulf it." % (obj.name, container.name))
                    mud.message(ch, None, obj, container, True, "to_room",
                               "$n takes $o out of the $O and white flames engulf it.")
            elif obj.carrier == ch:
                # Object is directly in character's inventory
                ch.send("You hold up %s as white flames engulf it." % obj.name)
                mud.message(ch, None, obj, None, True, "to_room",
                           "$n holds up $o as white flames engulf it.")
            else:
                # Object is in the room
                ch.send("You raise %s in the air as white flames engulf it." % obj.name)
                mud.message(ch, None, obj, None, True, "to_room",
                           "$n raises $o in the air as white flames engulf it.")
            
            mud.extract(obj)



################################################################################
# add our commands
################################################################################
mudsys.add_cmd("shutdow",     None, cmd_shutdown_net, "admin",   False)
mudsys.add_cmd("shutdown",    None, cmd_shutdown,     "admin",   False)
mudsys.add_cmd("copyove",     None, cmd_copyover_net, "admin",   False)
mudsys.add_cmd("copyover",    None, cmd_copyover,     "admin",   False)
mudsys.add_cmd("at",          None, cmd_at,           "wizard",  False)
mudsys.add_cmd("lockdown",    None, cmd_lockdown,     "admin",   False)
mudsys.add_cmd("pulserate",   None, cmd_pulserate,    "admin",   False)
mudsys.add_cmd("repeat",      None, cmd_repeat,       "wizard",  False)
mudsys.add_cmd("force",       None, cmd_force,        "wizard",  False)
mudsys.add_cmd("goto",        None, cmd_goto,         "wizard",  False)
mudsys.add_cmd("transfer",    None, cmd_transfer,     "wizard",  False)
mudsys.add_cmd("eval",        None, cmd_eval,         "admin",   False)
mudsys.add_cmd("exec",        None, cmd_exec,         "admin",   False)
mudsys.add_cmd("connections", None, cmd_connections,  "admin",   False)
mudsys.add_cmd("disconnect",  None, cmd_disconnect,   "admin",   False)
mudsys.add_cmd("instance",    None, cmd_instance,     "admin",   False)
mudsys.add_cmd("zinstance",   None, cmd_zinstance,    "admin",   False)
mudsys.add_cmd("clone",       None, cmd_clone,        "wizard",  False)
mudsys.add_cmd("load",        None, cmd_clone,        "wizard",  False)
mudsys.add_cmd("purge",       None, cmd_purge,        "wizard",  False)
mudsys.add_cmd("zap",         None, cmd_purge,        "wizard",  False)