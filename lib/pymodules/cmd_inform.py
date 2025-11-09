'''
cmd_inform.py

Contains various commands that are informative in nature. For instance, look,
equipment, inventory, etc...
'''
import mud, mudsys, inform, utils
import obj as mudobj

# for testing, not actually used in this module
import hooks
from appearance_look import build_appearance_window

################################################################################
# utility functions
################################################################################
def cmd_inventory(ch, cmd, arg):
    '''Lists all of the items currently carried in your inventory.'''
    if len(ch.inv) == 0:
        ch.send("You are not carrying anything.")
    else:
        ch.send("You are carrying:")
        visible = utils.find_all_objs(ch, ch.inv, "", None, True)
        utils.show_list(ch, visible, lambda x: x.name, lambda x: x.mname)

def cmd_equipment(ch, cmd, arg):
    '''Displays all of the equipment you are currently wearing.'''
    ch.send("You are wearing:")
    inform.show_equipment(ch, ch)

def cmd_who(ch, cmd, arg):
    '''List all of the players currently online.'''
    ch.page(inform.build_who(ch))
    
def can_see_in_room(ch):
    '''
    Check if character can see in current room.
    Returns True if room is lit or character has a light source.
    Returns False if room is dark and character has no light.
    '''
    if not ch.room:
        return False
    
    # Check if room has darkness bitvector
    try:
        has_dark = ch.room.hasBit("darkness")
        if not has_dark:
            return True  # Room is lit
    except:
        return True  # If we can't check, assume lit
    
    # Room is dark, checking for light sources...
    # Check equipped items
    try:
        if hasattr(ch, 'eq'):
            if ch.eq:
                for eq_item in ch.eq:
                    try:
                        if eq_item:
                            # Check the bits attribute directly
                            if hasattr(eq_item, 'bits'):
                                bits_str = str(eq_item.bits)
                                if "glow" in bits_str.lower():
                                    return True
                    except:
                        pass
    except:
        pass
    
    # Check inventory as fallback
    try:
        if hasattr(ch, 'inv'):
            if ch.inv:
                for inv_item in ch.inv:
                    try:
                        if inv_item:
                            # Check the bits attribute directly
                            if hasattr(inv_item, 'bits'):
                                bits_str = str(inv_item.bits)
                                if "glow" in bits_str.lower():
                                    return True
                    except:
                        pass
    except:
        pass
    
    return False


def cmd_look(ch, cmd, arg):
    '''allows players to examine just about anything in the game'''
    def _screen_width():
        try:
            val = mudsys.sys_getval("screen_width") or "80"
            return int(val)
        except:
            return 80

    def _show_edesc(keyword, target=None, target_type=None):
        desc = None
        # Try EDESC on a specific target first
        if target is not None:
            try:
                if target_type == "obj":
                    desc = target.get_edesc(keyword)
                elif target_type == "room":
                    desc = target.get_edesc(keyword)
                # EDESC-on-char not supported by engine; skip
            except:
                desc = None
        # Fallback: room EDESC
        if desc is None and ch.room is not None:
            try:
                desc = ch.room.get_edesc(keyword)
            except:
                desc = None
        if desc:
            formatted = mud.format_string(desc, True, _screen_width())
            ch.send(formatted)
            return True
        return False

    # DARKNESS CHECK: If no argument, check if we can see the room
    if arg == '' or arg.strip() == '':
        # Check if room is dark
        if not can_see_in_room(ch):
            ch.send("{rThe room is pitch black. You cannot see anything.{n\r\n")
            
            # Players can still "feel" exits in the dark
            try:
                exit_names = ch.room.exits
                if exit_names and len(exit_names) > 0:
                    ch.send("You feel the following exits: ", end="")
                    exit_list = list(exit_names)
                    for i, exit_name in enumerate(exit_list):
                        if i > 0:
                            ch.send(", ", end="")
                        ch.send(exit_name, end="")
                    ch.send("\r\n")
            except:
                pass
            
            return
        
        # Room is visible, proceed with normal look
        mud.look_at_room(ch, ch.room)
        return

    # First, try typed targets via parse_args without spamming usage errors
    try:
        found, found_type = mud.parse_args(ch, False, cmd, arg,
                                           "[at] [the] { exit obj.room.inv.eq ch.room }")
        if found_type == "obj":
            mud.look_at_obj(ch, found)
            return
        elif found_type == "char":
            #mud.look_at_char(ch, found)
            ch.send(build_appearance_window(found))
            return
        elif found_type == "exit":
            mud.look_at_exit(ch, found)
            return
        elif found_type == "room":
            mud.look_at_room(ch, found)
            return
    except:
        pass

    # Next, try nested target: look [at] <word> on/in <target>
    # Try "on" first (primarily for equipment on characters)
    try:
        keyword, tgt, tgt_type = mud.parse_args(
            ch, False, cmd, arg, "[at] [the] word | <on> [the] { obj.room.inv.eq ch.room }")
        if tgt is not None:
            # look for object worn by character
            if tgt_type == "char":
                num, name = utils.get_count(keyword)
                found_eq = utils.find_obj(ch, tgt.eq, num, name)
                if found_eq is not None:
                    mud.look_at_obj(ch, found_eq)
                    return
                # not found on char; try EDESC on char (not supported) then room/target
                if _show_edesc(keyword, tgt, tgt_type):
                    return
                mud.message(ch, tgt, None, None, True, "to_char",
                            "You could not find what you were looking for on $N.")
                return
            # if it's an object target, try EDESC on the object (no nested obj-on-obj search)
            if _show_edesc(keyword, tgt, tgt_type):
                return
    except:
        pass

    # Try "in" (search container, room, or character inventory)
    try:
        keyword, tgt, tgt_type = mud.parse_args(
            ch, False, cmd, arg, "[at] [the] word | <in> [the] { obj.room.inv.eq ch.room }")
        if tgt is not None:
            # search inside an object (container)
            if tgt_type == "obj":
                found = mudobj.find_obj(keyword, tgt, ch)
                if found is not None:
                    mud.look_at_obj(ch, found)
                    return
                # not found in container; try EDESC on container, then message
                if _show_edesc(keyword, tgt, tgt_type):
                    return
                mud.message(ch, None, tgt, None, True, "to_char",
                            "You could not find what you were looking for in $o.")
                return
            # search inside a character (inventory)
            if tgt_type == "char":
                found = mudobj.find_obj(keyword, tgt, ch)
                if found is not None:
                    mud.look_at_obj(ch, found)
                    return
                if _show_edesc(keyword, tgt, tgt_type):
                    return
                mud.message(ch, tgt, None, None, True, "to_char",
                            "You could not find what you were looking for in $N's belongings.")
                return
            # search in a room
            if tgt_type == "room":
                found = mudobj.find_obj(keyword, tgt, ch)
                if found is not None:
                    mud.look_at_obj(ch, found)
                    return
                if _show_edesc(keyword, tgt, tgt_type):
                    return
                ch.send("You could not find that here.")
                return
    except:
        pass

    # Finally, treat the argument as a room EDESC keyword directly
    if _show_edesc(arg.strip()):
        return

    ch.send("What did you want to look at?")


def cmd_test(ch, cmd, arg):

    hooks.run("look_at_room", hooks.build_info("ch rm", (ch.room, ch)))

def cmd_exits(ch, cmd, arg):
    '''Examine all exits from the current room in detail.'''
    # Send header to the character
    ch.send("{WExamining exits from this area...{n")
    ch.send("=" * 40)
    
    # Use the long_room_exits function to show detailed exit information
    inform.long_room_exits(ch, ch.room)
    
    # Send message to room that character is looking around
    mud.message(ch, None, None, None, True, "to_room", "$n looks around with interest, examining the exits.")

################################################################################
# add our commands
################################################################################
mudsys.add_cmd("inventory", "i",   cmd_inventory, "player", False)
mudsys.add_cmd("equipment", "eq",  cmd_equipment, "player", False)
mudsys.add_cmd("worn",      None,  cmd_equipment, "player", False)
mudsys.add_cmd("who",       None,  cmd_who,       "player", False)

mudsys.add_cmd("test",      None,  cmd_test,      "player", False)
mudsys.add_cmd("exits",     None,  cmd_exits,     "player", False)
mudsys.add_cmd("look",      "l",   cmd_look,      "player", False)
