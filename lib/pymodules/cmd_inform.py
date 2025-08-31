'''
cmd_inform.py

Contains various commands that are informative in nature. For instance, look,
equipment, inventory, etc...
'''
import mud, mudsys, inform, utils

# for testing, not actually used in this module
import hooks


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
    
def cmd_look(ch, cmd, arg):
    '''allows players to examine just about anything in the game'''
    if arg == '':
        inform.look_at_room(ch, ch.room)
    else:
        found, type = mud.generic_find(ch, arg, "all", "immediate", False)

        # what did we find?
        if found == None:
            ch.send("What did you want to look at?")
        elif type == "obj" or type == "in":
            inform.look_at_obj(ch, found)
        elif type == "char":
            inform.look_at_char(ch, found)
        elif type == "exit":
            inform.look_at_exit(ch, found)

        # extra descriptions as well
        ############
        # FINISH ME
        ############


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
'''
mudsys.add_cmd("look",      "l",   cmd_look,      "player", False)
'''
