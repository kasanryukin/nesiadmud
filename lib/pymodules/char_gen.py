'''
char_gen.py

The basic character generation module. Allows accounts to create new characters
with basic selection for name, sex, and race.
'''
import mudsys, mud, socket, char, hooks
from char_gen_enhancements import cg_appearance_entry_handler, cg_appearance_entry_prompt, apply_race_special_attributes
# Import attributes module for character initialization
try:
    import attributes.attribute_aux as attribute_aux
    ATTRIBUTES_AVAILABLE = True
except ImportError:
    ATTRIBUTES_AVAILABLE = False
    mud.log_string("char_gen: Attributes module not available")

# Import progression module for character initialization
try:
    import progression
    PROGRESSION_AVAILABLE = True
except ImportError:
    PROGRESSION_AVAILABLE = False
    mud.log_string("char_gen: Progression module not available")

def check_char_name(arg):
    '''checks to make sure the character name is valid. Names are valid if they
       are greater than 2 characters, less than 13, and comprise only alpha
       characters.'''
    return len(arg) >= 3 and len(arg) <= 17 and arg.isalpha()

def cg_name_handler(sock, arg):
    if not check_char_name(arg):
        sock.send("{cIllegal name, please pick another.{n\r\n")
    elif mudsys.player_exists(arg):
        sock.send("{cA player with that name already exists.{n\r\n")
    elif mudsys.player_creating(arg):
        sock.send("{cA player is already being created with that name.{n\r\n")
    elif arg.lower().startswith("guest"):
        sock.send("{cCharacter names cannot begin with 'guest'.{n\r\n")
    else:
        name = arg[0].upper() + arg[1:]
        ch = mudsys.create_player(name)

        if ch == None:
            sock.send("{cIllegal name, please pick another.{n\r\n")
        else:
            mudsys.attach_char_socket(ch, sock)
            ch.rdesc = ch.name + " is here."
            sock.pop_ih()

def cg_sex_handler(sock, arg):
    try:
        result = {
            'M' : 'male',
            'F' : 'female',
            'N' : 'non-binary',
            'O' : 'other',
            }[arg[0].upper()]
        sock.ch.sex = result
        sock.pop_ih()
    except:
        sock.send("{cInvalid sex, try again.{n\r\n")

def cg_race_handler(sock, arg):
    if not mud.is_race(arg, True):
        sock.send("{cInvalid race selection, try again.{n\r\n")
    else:
        sock.ch.race = arg.lower()
        sock.pop_ih()

def cg_finish_handler(sock, arg):
    # pop our input handler for finishing character generation
    sock.pop_ih()

    # log that the character created
    mud.log_string("New player: " + sock.ch.name + " has entered the game.")
    
    # register and save him to disk and to an account
    mud.log_string("Attempting to register new player to disk.")
    mud.log_string(f"DEBUG: Character name: {sock.ch.name}")

    try:
        skills_aux = sock.ch.getAuxiliary('skills')
        mud.log_string(f"DEBUG: Character has skills aux: {skills_aux is not None}")
    except:
        mud.log_string(f"DEBUG: Character has skills aux: False (error getting it)")

    try:
        exp_aux = sock.ch.getAuxiliary('experience')
        mud.log_string(f"DEBUG: Character has experience aux: {exp_aux is not None}")
    except:
        mud.log_string(f"DEBUG: Character has experience aux: False (error getting it)")

    try:
        level_aux = sock.ch.getAuxiliary('leveling')
        mud.log_string(f"DEBUG: Character has leveling aux: {level_aux is not None}")
    except:
        mud.log_string(f"DEBUG: Character has leveling aux: False (error getting it)")
    
    mud.log_string("DEBUG: About to call do_register")
    try:
        mudsys.do_register(sock.ch)
        mud.log_string("Character written to disk.")
    except Exception as e:
        mud.log_string(f"CRITICAL: do_register failed: {str(e)}")
        import traceback
        mud.log_string(traceback.format_exc())
        raise

    # Initialize attributes based on race
    if ATTRIBUTES_AVAILABLE:
        mud.log_string("Attributes availible, starting handler.")
        try:
            aux = attribute_aux.get_attributes(sock.ch)
            if aux and not aux.initialized:
                aux.initialize_for_race(sock.ch.race)
                mud.log_string(f"Initialized attributes for {sock.ch.name} ({sock.ch.race})")
                
                # Initialize vitality from attributes
                try:
                    import vitality.vitality_core as vitality
                    vitality.initialize_vitality(sock.ch)
                    mud.log_string(f"Initialized vitality for {sock.ch.name}")
                except ImportError:
                    pass  # Vitality module not loaded
                
                # Display rolled attributes to the player
                sock.send("\r\n{G*** Your attributes have been determined by your race ***{n\r\n")
                sock.send("{c┌─────────────────────────────────────┐{n\r\n")
                sock.send("{c│{n        {WYOUR ATTRIBUTES{n            {c│{n\r\n")
                sock.send("{c├─────────────────────────────────────┤{n\r\n")
                
                import attributes.attribute_data as attribute_data
                for attr_name in attribute_data.get_attribute_names():
                    abbrev = attribute_data.get_attribute_abbrev(attr_name)
                    value = aux.get_attribute(attr_name)
                    
                    # Color code based on value
                    if value >= 14:
                        color = "{G"  # Green for excellent
                    elif value >= 10:
                        color = "{Y"  # Yellow for average
                    else:
                        color = "{R"  # Red for below average
                    
                    attr_display = attr_name.capitalize()
                    sock.send(f"{{c│{{n {abbrev}: {attr_display:<20} {color}{value:>3}{{n {{c│{{n\r\n")
                
                sock.send("{c└─────────────────────────────────────┘{n\r\n")
                sock.send(f"{{YYou have been granted {aux.tdp_available} TDP (Time Development Points){{n\r\n")
                sock.send("{cUse 'train' to spend TDP and improve your attributes.{n\r\n\r\n")
        except Exception as e:
            mud.log_string(f"Error initializing attributes for {sock.ch.name}: {str(e)}")

    # Initialize progression system (moved outside attributes block)
    if PROGRESSION_AVAILABLE:
        try:
            mud.log_string(f"DEBUG: About to initialize progression for {sock.ch.name}")
            default_class_config = {
                'class_name': 'Novice',
                'skills': {
                    'primary': [],
                    'secondary': [],
                    'tertiary': [],
                    'else': progression.get_skill_registry().list_all_skills()
                },
                'levels': {
                    1: {'tdp': 0, 'requirements': {}}
                }
            }
            progression.setup_progression(sock.ch, default_class_config)
            mud.log_string(f"Initialized progression for {sock.ch.name}")
        except Exception as e:
            mud.log_string(f"Error initializing progression for {sock.ch.name}: {str(e)}")
            import traceback
            mud.log_string(traceback.format_exc())
    
    # make him exist in the game for functions to look him up
    apply_race_special_attributes(sock.ch)
    mudsys.try_enter_game(sock.ch)

    # run the init_player hook
    hooks.run("init_player", hooks.build_info("ch", (sock.ch,)))
    
    # attach him to his account and save the account
    sock.account.add_char(sock.ch)
    mudsys.do_save(sock.account)
    mudsys.do_save(sock.ch)

    # clear their screen
    sock.ch.act("clear")
    
    # send them the motd
    sock.ch.page(mud.get_motd())

    # make him look at the room
    sock.ch.act("look")

    # run our enter hook
    hooks.run("enter", hooks.build_info("ch rm", (sock.ch, sock.ch.room)))

def cg_name_prompt(sock):
    sock.send_raw("What is your character's name? ")

def cg_sex_prompt(sock):
    sock.send_raw("What is your sex (M/F/N/O)? ")

def cg_race_prompt(sock):
    sock.send("Available races are: ")
    sock.send(mud.list_races(True))
    sock.send_raw("\r\nPlease enter your choice: ")

def cg_finish_prompt(sock):
    sock.send_raw("{c*** Press enter to finish character generation:{n ")



################################################################################
# character generation hooks
################################################################################
def char_gen_hook(info):
    '''Put a socket into the character generation menu when character generation
       hooks are called.
    '''
    sock, = hooks.parse_info(info)
    sock.push_ih(mudsys.handle_cmd_input, mudsys.show_prompt, "playing")
    sock.push_ih(cg_finish_handler, cg_finish_prompt)
    sock.push_ih(cg_appearance_entry_handler, cg_appearance_entry_prompt)
    sock.push_ih(cg_sex_handler, cg_sex_prompt)
    sock.push_ih(cg_name_handler, cg_name_prompt)

def guest_gen_hook(info):
    sock, = hooks.parse_info(info)
    sock.push_ih(mudsys.handle_cmd_input, mudsys.show_prompt, "playing")

    # make the guest character
    ch = mudsys.create_player("Guest")

    # oops...
    if ch == None:
        sock.send("Sorry, there were issues creating a guest account.")
        sock.close()

    mudsys.attach_char_socket(ch, sock)
    ch.rdesc = "a guest player is here, exploring the world."
    ch.name  = ch.name + str(ch.uid)
    ch.race  = "human"

    # log that the character created
    mud.log_string("Guest character created (id %d)." % ch.uid)
    
    # Initialize attributes for guest (human baseline)
    if ATTRIBUTES_AVAILABLE:
        try:
            aux = attribute_aux.get_attributes(ch)
            if aux and not aux.initialized:
                aux.initialize_for_race("human")
                mud.log_string(f"Initialized attributes for guest {ch.name}")
                
                # Initialize vitality from attributes
                try:
                    import vitality.vitality_core as vitality
                    vitality.initialize_vitality(ch)
                    mud.log_string(f"Initialized vitality for guest {ch.name}")
                except ImportError:
                    pass  # Vitality module not loaded
        except Exception as e:
            mud.log_string(f"Error initializing attributes for guest {ch.name}: {str(e)}")

    # make him exist in the game for functions to look him up
    mudsys.try_enter_game(ch)

    # run the init_player hook
    hooks.run("init_player", hooks.build_info("ch", (ch,)))

    # clear our screen
    ch.act("clear")

    # send them the motd
    ch.page(mud.get_motd())
    
    # make him look at the room
    ch.act("look")

    # run our enter hook
    hooks.run("enter", hooks.build_info("ch rm", (ch, ch.room)))



################################################################################
# loading and unloading the module
################################################################################
hooks.add("create_character", char_gen_hook)
hooks.add("create_guest",     guest_gen_hook)

def __unload__():
    '''removes the hooks for character generation'''
    hooks.remove("create_character", char_gen_hook)
    hooks.remove("create_guest",     guest_gen_hook)