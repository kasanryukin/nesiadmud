"""
package: socials

socials are commonly used emotes (e.g. smiling, grinning, laughing). Instead
making people have to write out an entire emote every time they would like
to express such an emote, they can simply use one of these simple commands
to perform a pre-made emote. This is essentially a copy of the c module written
in python. There are no changes good or bad.

Description of module concepts:
 cmds are the list of commands that trigger the social. More than one cmd
 can be specified (comma-separated). Assumes cmds != NULL. All other
 arguments can be NULL.

 to_char_notgt is the message sent to the character if no target for
 the social is provided.

 to_room_notgt is the message sent to the room if no target for the
 social is provided.

 to_char_self is the message sent to ourself when the target provided
 was ourself. If to_char_self is not provided, the message will default
 to the same one used for to_char_notgt.

 to_room_self is the message sent to the room when the target provided
 was ourself. If to_room_self is not provided, the message will default
 to the same one used for to_char_notgt.

 to_char_tgt is the message sent to the character when a target is
 provided.

 to_vict_tgt is the message sent to the target when a target is provided

 to_room_tgt is the message sent to the room when a target is provided

 adverbs and adjectives are default modifiers that can be suggested or
 applied to the emote through $X and $x (adjective: evil, adverb: evilly).
 If a player types an override it will override both $X and $x unless they
 clearly specify $X= and/or $x= for advanced usage.

 require_tgt is a boolean describing whether this emote forces the caller
 to have a target.

 min_pos and max_pos are the minimum and maximum positions the socials can
 per performed from, respectively.

"""
from mudsys import add_cmd, remove_cmd
from cmd_checks import chk_conscious, chk_can_move, chk_grounded, chk_supine
import mud, storage, char, auxiliary, time, string, hooks, mudsys

# This stores all the socials themselves, before unlinking
social_table = { }
# This stores all the socials after unlinking
socials = { }
socials_file = "misc/socials"

def ensure_socials_file():
    """Ensure socials file exists, copy from default if not"""
    import os
    
    if not os.path.exists(socials_file):
        # Get the directory where this module is located
        module_dir = os.path.dirname(__file__)
        default_socials = os.path.join(module_dir, "default.socials")
        
        if os.path.exists(default_socials):
            # Create misc directory if it doesn't exist
            os.makedirs(os.path.dirname(socials_file), exist_ok=True)
            
            # Manual file copy - create file directly since we're in mudlib root
            try:
                with open(default_socials, 'r') as src:
                    content = src.read()
                # Write directly to file - we're already in mudlib directory
                with open(socials_file, 'w') as dst:
                    dst.write(content)
                print(f"Created {socials_file} from default template")
            except Exception as e:
                print(f"Error creating socials file: {e}")
        else:
            print(f"Warning: Neither {socials_file} nor {default_socials} exists")

# Initialize socials file on module load
ensure_socials_file()

class Social:
    def __init__(self, cmds = "", to_char_notgt = "", to_room_notgt = "", to_char_self = "",
                 to_room_self = "", to_char_tgt = "", to_vict_tgt = "", to_room_tgt = "",
                 adverb = "", adjective = "", require_tgt = "", min_pos = "", max_pos = "",
                 storeSet = None):
        if not storeSet == None:
            self.cmds = storeSet.readString("cmds")
            self.to_char_notgt = storeSet.readString("to_char_notgt")
            self.to_room_notgt = storeSet.readString("to_room_notgt")
            self.to_char_self = storeSet.readString("to_char_self")
            self.to_room_self = storeSet.readString("to_room_self")
            self.to_char_tgt = storeSet.readString("to_char_tgt")
            self.to_vict_tgt = storeSet.readString("to_vict_tgt")
            self.to_room_tgt = storeSet.readString("to_room_tgt")
            self.adverb = storeSet.readString("adverb")
            self.adjective = storeSet.readString("adjective")
            self.require_tgt = storeSet.readString("require_tgt")
            self.min_pos = storeSet.readString("min_pos")
            self.max_pos = storeSet.readString("max_pos")
        else:
            self.cmds = cmds
            self.to_char_notgt = to_char_notgt
            self.to_room_notgt = to_room_notgt
            self.to_char_self = to_char_self
            self.to_room_self = to_room_self
            self.to_char_tgt = to_char_tgt
            self.to_vict_tgt = to_vict_tgt
            self.to_room_tgt = to_room_tgt
            self.adverb = adverb
            self.adjective = adjective
            self.require_tgt = require_tgt
            self.min_pos = min_pos
            self.max_pos = max_pos

    def store(self):
        set = storage.StorageSet()
        set.storeString("cmds",           self.cmds)
        set.storeString("to_char_notgt",  self.to_char_notgt)
        set.storeString("to_room_notgt",  self.to_room_notgt)
        set.storeString("to_char_self",   self.to_char_self)
        set.storeString("to_room_self",   self.to_room_self)
        set.storeString("to_char_tgt",    self.to_char_tgt)
        set.storeString("to_vict_tgt",    self.to_vict_tgt)
        set.storeString("to_room_tgt",    self.to_room_tgt)
        set.storeString("adjective",      self.adjective)
        set.storeString("adverb",         self.adverb)
        set.storeString("require_tgt",    self.require_tgt)
        set.storeString("min_pos",        self.min_pos)
        set.storeString("max_pos",        self.max_pos)
        return set

    def get_cmds(self): return self.cmds
    def get_to_char_notgt(self): return self.to_char_notgt
    def get_to_char_self(self): return self.to_char_self
    def get_to_char_tgt(self): return self.to_char_tgt
    def get_to_room_notgt(self): return self.to_room_notgt
    def get_to_room_self(self): return self.to_room_self
    def get_to_room_tgt(self): return self.to_room_tgt
    def get_to_vict_tgt(self): return self.to_vict_tgt
    def get_adverb(self): return self.adverb
    def get_adjective(self): return self.adjective
    def get_require_tgt(self): return self.require_tgt
    def get_min_pos(self): return self.min_pos
    def get_max_pos(self): return self.max_pos

    def set_cmds(self, val):
        self.cmds = val
        return self.cmds
    def set_to_char_notgt(self, val):
        self.to_char_notgt = val
        return self.to_char_notgt
    def set_to_char_self(self, val):
        self.to_char_self = val
        return self.to_char_self
    def set_to_char_tgt(self, val):
        self.to_char_tgt = val
        return self.to_char_tgt
    def set_to_room_notgt(self, val):
        self.to_room_notgt = val
        return self.to_room_notgt
    def set_to_room_self(self, val):
        self.to_room_self = val
        return self.to_room_self
    def set_to_room_tgt(self, val):
        self.to_room_tgt = val
        return self.to_room_tgt
    def set_to_vict_tgt(self, val):
        self.to_vict_tgt = val
        return self.to_vict_tgt
    def set_adverb(self, val):
        self.adverb = val
        return self.adverb
    def set_adjective(self, val):
        self.adjective = val
        return self.adjective
    def set_require_tgt(self, val):
        self.require_tgt = val
        return self.require_tgt
    def set_min_pos(self, val):
        self.min_pos = val
        return self.min_pos
    def set_max_pos(self, val):
        import movement  
        # Check if val is a valid position (either string or index)
        if val in movement.positions or (isinstance(val, int) and 0 <= val < len(movement.positions)):
            self.max_pos = val
        return self.max_pos

def link_social(new_cmd, old_cmd, save=True):
    if old_cmd in socials.keys():
        unlink_social(new_cmd, save)
    social_data = get_social(old_cmd)

    cmds = social_data.get_cmds()
    keywords = [x.strip() for x in cmds.split(',')]
    keywords.append(new_cmd)

    # relink all the individual mappings
    new_cmds = ','.join(keywords)
    for k in keywords:
        socials[k] = new_cmds

    # set the new hash, delete the old one and add the new
    social_data.set_cmds(new_cmds)
    del social_table[cmds]
    social_table[new_cmds] = social_data

    # add the command to the system
    add_cmd(new_cmd, None, cmd_social, "player", False)
    # this needs to be rewritten
    if social_data.get_min_pos() == "sitting":
        mudsys.add_cmd_check(new_cmd, chk_conscious)
    elif social_data.get_min_pos() == "standing":
        mudsys.add_cmd_check(new_cmd, chk_can_move)
    elif social_data.get_max_pos() == "standing":
        mudsys.add_cmd_check(new_cmd, chk_grounded)
    elif social_data.get_max_pos() == "sitting":
        mudsys.add_cmd_check(new_cmd, chk_supine)

    if save is True:
        save_socials()


def unlink_social(social_cmd, save=True):
    if social_cmd not in socials.keys():
        return

    social_link = socials[social_cmd]
    if social_link in social_table.keys():
        social_data = social_table.pop(social_link)

        if social_data is not None:
            cmds = social_data.get_cmds()
            result = [x.strip() for x in cmds.split(',')]
            # remove the original cmd from the command list
            result.remove(social_cmd)
            remove_cmd(social_cmd)
            # if there are still commands left re-add
            if len(result) > 0:
                social_data.set_cmds(','.join(result))
                social_table[social_link] = social_data
            else:
                del socials[social_cmd]  # Fixed: was trying to use as index

        if save is True:
            save_socials()

def add_social(social_data, save=True):
    cmds = social_data.get_cmds()
    result = [x.strip() for x in cmds.split(',')]
    for res in result:
        unlink_social(res)
        add_cmd(res, None, cmd_social, "player", False)
        if social_data.get_min_pos() == "sitting":
            mudsys.add_cmd_check(res, chk_conscious)
        elif social_data.get_min_pos() == "standing":
            mudsys.add_cmd_check(res, chk_can_move)
        elif social_data.get_max_pos() == "standing":
            mudsys.add_cmd_check(res, chk_grounded)
        elif social_data.get_max_pos() == "sitting":
            mudsys.add_cmd_check(res, chk_supine)
        socials[res] = cmds
    social_table[cmds] = social_data
    if save:
        save_socials()


def get_social(social):
    if social in socials:
        return social_table[socials[social]]
    return None


def save_socials():
    set = storage.StorageSet()
    socials = storage.StorageList()
    set.storeList("socials", socials)

    for cmd, data in social_table.items():  # Fixed: iteritems() -> items()
        one_set = data.store()
        socials.add(one_set)

    set.write(socials_file)
    set.close()
    return


def save_social(social):
    save_socials()
    return

def load_socials():
    storeSet = storage.StorageSet(socials_file)
    for social_set in storeSet.readList("socials").sets():
        social_data = Social(storeSet=social_set)
        cmds = social_data.get_cmds()
        result = [x.strip() for x in cmds.split(',')]
        social_table[cmds] = social_data
        for res in result:
            add_cmd(res, None, cmd_social, "player", False)
            if social_data.get_min_pos() == "sitting":
                mudsys.add_cmd_check(res, chk_conscious)
            elif social_data.get_min_pos() == "standing":
                mudsys.add_cmd_check(res, chk_can_move)
            elif social_data.get_max_pos() == "standing":
                mudsys.add_cmd_check(res, chk_grounded)
            elif social_data.get_max_pos() == "sitting":
                mudsys.add_cmd_check(res, chk_supine)
            socials[res] = cmds
    storeSet.close()
    return

def cmd_socials(ch, cmd, arg):
    '''
    Syntax: socials, socials <social name>

    Socials are a form of emote, they are prepared emotes that are commands you can use and they
    allow for single use, targeting other people, etc. An example of a social would be the grin social.

    If you type:
        > grin

    You will see the following, while others around you will also see a variation as if you had performed
    the action:
        You grin mischievously.

    If you want to grin at Kevin though, you can do so by typing:
        > grin kevin

    You will see:
        You grin mischievously at Kevin.

    Since these are targeted, Kevin will see it directed at them and the room will see you directing
    this mischievous grin at Kevin. Additionally you can change that mischievous nature of the grin
    by typing your own adverb (or even phrase):

        > grin stupidly
        > grin stupidly at kevin

    There are quite a few defined socials that you can do. The command 'socials' will list all of
    the socials currently available to you. Additionally you can specify a social and see how a
    specific social will look if used, the adverbs, and any synonyms.
    '''
    buf = [ ]
    socs = sorted(__socials__.keys())
    count = 0
    for soc in socs:
        count = count + 1
        buf.append("%-20s" % soc)
        if count % 4 == 0:
            ch.send("".join(buf))
            buf = [ ]

    if count % 4 != 0:
        ch.send("".join(buf))


def cmd_soclink(ch, cmd, arg):
    if arg is None or arg == "":  # Fixed: is "" syntax
        ch.send("Link which social to which?")
        return

    arg = arg.lower()
    arg, new_soc = mud.parse_args(ch, True, cmd, arg, "| word(subcommand) word(arguments)")
    if new_soc is None:
        ch.send("You must provide a new command and an old social to link it to.")
        return

    social_data = get_social(arg)

    if social_data is None:
        ch.send("No social exists for %s" % arg)

    link_social(new_soc, arg)
    ch.send("%s is now linked to %s" % (new_soc, arg))

def cmd_socunlink(ch, cmd, arg):
    if arg is None or arg == "":
        ch.send("Unlink which social?")
        return

    unlink_social(arg)
    ch.send("The %s social was unlinked." % arg)
    mud.log_string("%s unlinked the social %s." % (ch.name, arg))

def process_social_message(msg, modifier, data):
    """Helper function to process social message with proper $X/$x replacement"""
    if not msg:
        return msg
    
    # Replace $x with adjective (always from social data)
    if "$x" in msg and data.get_adjective():
        msg = msg.replace("$x", data.get_adjective())
    
    # Replace $X with modifier (user provided) or default adverb
    if "$X" in msg:
        if modifier:
            msg = msg.replace("$X", modifier)
        elif data.get_adverb():
            msg = msg.replace("$X", data.get_adverb())
    
    return msg


# One generic command for handling socials. Does table lookup on all of
# the existing socials and executes the proper one.
def cmd_social(ch, cmd, arg):
    data = get_social(cmd)
    
    # Parse arguments to extract modifier and target
    # Social syntax supports two formats:
    #   1. Explicit: "modifier at target" (e.g., "grin evilly at mysty")
    #   2. Implicit: "modifier target" (e.g., "grin evilly mysty")
    
    args = arg.split(" at ", 1)
    has_explicit_at = len(args) >= 2
    
    if has_explicit_at:
        # Format: "modifier at target"
        # Everything before " at " becomes the modifier
        # Everything after " at " becomes the target
        modifier = args[0].strip()
        target_name = args[1].strip()
    else:
        # Format: "modifier target" or single word or empty
        # Parse by splitting on spaces and using positional logic
        words = arg.strip().split()
        
        if len(words) >= 2:
            # Multiple words: "very evilly mysty" -> modifier="very evilly", target="mysty"
            # All words except the last become the modifier
            # Last word becomes the target to search for
            modifier = " ".join(words[:-1])
            target_name = words[-1]
        elif len(words) == 1:
            # Single word: "mysty" or "evilly"
            # Try as target first, fallback to modifier if target not found
            modifier = ""
            target_name = words[0]
        else:
            # Empty command: "grin"
            # No modifier, no target - will use social defaults
            modifier = ""
            target_name = ""
    
    # does the social exist? Do we have a problem? DO WE?
    if data:
        # Search for target if we have a target name
        tgt = None
        type = None
        if target_name:
            try:
                tgt, type = mud.generic_find(ch, target_name, "all", "immediate", False)
            except UnicodeDecodeError:
                # mud.generic_find failed due to encoding issues, treat as no target found
                tgt = None
                type = None
            
        # If we found no target, handle fallback logic
        if tgt is None and not has_explicit_at:
            if len(arg.strip().split()) == 1:
                # Single word that wasn't found as target - treat as modifier
                modifier = arg.strip()
                target_name = ""
            # For multi-word cases, modifier and target_name are already set correctly
        elif tgt is not None and type != "char":
            # Found something but it's not a character
            ch.send("That individual does not seem to be here.")
            return

        # Set default modifier if no modifier provided but adverb exists
        # This happens AFTER fallback logic so user modifiers take precedence
        if not modifier and data.get_adverb():
            modifier = data.get_adverb()

        # No target was supplied, the emote is to ourselves.
        if tgt is None:
            if data.get_to_char_notgt():
                msg = process_social_message(data.get_to_char_notgt(), modifier, data)
                mud.message(ch, None, None, None, True, "to_char", msg)
            if data.get_to_room_notgt():
                msg = process_social_message(data.get_to_room_notgt(), modifier, data)
                mud.message(ch, None, None, None, True, "to_room", msg)
            return
        # a target was supplied and it is us
        elif ch == tgt:
            if data.get_to_char_self():
                msg = process_social_message(data.get_to_char_self(), modifier, data)
                mud.message(ch, None, None, None, True, "to_char", msg)
            elif data.get_to_char_notgt():
                msg = process_social_message(data.get_to_char_notgt(), modifier, data)
                mud.message(ch, None, None, None, True, "to_char", msg)
            if data.get_to_room_self():
                msg = process_social_message(data.get_to_room_self(), modifier, data)
                mud.message(ch, None, None, None, True, "to_room", msg)
            elif data.get_to_room_notgt():
                msg = process_social_message(data.get_to_room_notgt(), modifier, data)
                mud.message(ch, None, None, None, True, "to_room", msg)
            return
        # a target was supplied and it is not us
        else:
            if data.get_to_char_tgt():
                msg = process_social_message(data.get_to_char_tgt(), modifier, data)
                mud.message(ch, tgt, None, None, True, "to_char", msg)
            if data.get_to_vict_tgt():
                msg = process_social_message(data.get_to_vict_tgt(), modifier, data)
                mud.message(ch, tgt, None, None, True, "to_vict", msg)
            if data.get_to_room_tgt():
                msg = process_social_message(data.get_to_room_tgt(), modifier, data)
                mud.message(ch, tgt, None, None, True, "to_room", msg)
    else:
        mud.log_string("ERROR: %s tried social, %s, but no such social exists!" % (ch.name, cmd))
    return
            

load_socials()
add_cmd("socials", None, cmd_socials, "player", False)
add_cmd("socunlink", None, cmd_socunlink, "builder", False)
add_cmd("soclink", None, cmd_soclink, "builder", False)