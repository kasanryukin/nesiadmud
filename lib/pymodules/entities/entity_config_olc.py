"""
Entity Configuration OLC Editor

Provides an online editor for managing entity configuration data.
Only manipulates in-memory entity_config data, never touches storage directly.
"""
import mud
import olc
import world
from mudsys import add_cmd
from entities.entity_config import get_race_config, get_body_config, save_race_config, save_body_config, BodyPosition, Race

# OLC return values
MENU_CHOICE_INVALID = -1
MENU_NOCHOICE = 0

def entities_config_menu(sock, data):
    """Display the main entities configuration menu"""
    race_config = get_race_config()
    body_config = get_body_config()
    
    # Get all available types from C code
    all_body_types = world.get_bodypos_types()
    all_body_sizes = world.get_bodysizes()
    
    sock.send_raw("""
{g+{n==============================================================================
{cEntities Configuration Editor{n
{g+{n==============================================================================

{c1{n) Body position types ({y%d{n): %s
{c2{n) Body sizes ({y%d{n): %s
{c3{n) Races ({y%d{n): %s

{cQ{n) Quit
""" % (
        len(all_body_types), ", ".join(all_body_types[:5]) + ("..." if len(all_body_types) > 5 else ""),
        len(all_body_sizes), ", ".join(all_body_sizes[:5]) + ("..." if len(all_body_sizes) > 5 else ""),
        len(race_config.get_race_names()), ", ".join(sorted(race_config.get_race_names())[:5]) + ("..." if len(race_config.get_race_names()) > 5 else "")
    ))

def entities_config_chooser(sock, data, choice):
    """Handle main entities config menu choices"""
    if choice == '1':
        olc.do_olc(sock, body_types_menu, body_types_chooser, 
                   body_types_parser, None, data)
        return MENU_NOCHOICE
    elif choice == '2':
        olc.do_olc(sock, body_sizes_menu, body_sizes_chooser,
                   body_sizes_parser, None, data)
        return MENU_NOCHOICE
    elif choice == '3':
        olc.do_olc(sock, races_menu, races_chooser,
                   races_parser, None, data)
        return MENU_NOCHOICE
    return MENU_CHOICE_INVALID

def entities_config_parser(sock, data, choice, arg):
    """Parse entities config menu input"""
    return False



# Helper function for tabular display
def format_tabular_list(items, markers=None, line_width=78):
    """Format a list of items in tabular format with optional markers"""
    if not items:
        return "  (none)\n"
    
    # Calculate the width needed for each item (including marker and spacing)
    max_item_width = max(len(item) for item in items)
    marker_width = 2 if markers else 0  # "* " or "  "
    spacing = 2  # Space between columns
    column_width = max_item_width + marker_width + spacing
    
    # Calculate how many columns fit in the line width
    cols_per_line = max(1, (line_width - 2) // column_width)  # -2 for leading spaces
    
    result = ""
    sorted_items = sorted(items)
    
    for i in range(0, len(sorted_items), cols_per_line):
        line_items = sorted_items[i:i + cols_per_line]
        line = "  "
        
        for item in line_items:
            if markers and item in markers:
                marker = markers[item]
                if marker == "*":
                    # Color the asterisk cyan and the item white
                    formatted_item = ("{c" + marker + "{w" + item).ljust(column_width + 8)  # +8 for color codes
                else:
                    formatted_item = ("{w " + item).ljust(column_width + 4)  # +4 for color codes
            else:
                marker = " " if markers else ""
                formatted_item = ("{w" + marker + item).ljust(column_width + 4)
            
            line += formatted_item
        
        result += line.rstrip() + "{n\n"
    
    return result

# Body Types Menu
def body_types_menu(sock, data):
    """Body position types configuration menu"""
    body_config = get_body_config()
    original_builtin_types = ["floating about head", "about body", "head", "face", "ear", "neck", "torso", "arm", "wing", "wrist", "left hand", "right hand", "finger", "waist", "leg", "left foot", "right foot", "hoof", "claw", "tail", "held"]
    custom_types = body_config.body_types.bodypart_types
    
    # Combine built-in and custom types
    all_types = list(original_builtin_types) + [pos_type for pos_type in custom_types if pos_type not in original_builtin_types]
    
    # Create markers dict for built-in vs custom types
    markers = {}
    for pos_type in all_types:
        markers[pos_type] = "*" if pos_type in original_builtin_types else " "
    
    sock.send_raw("""
{g+{n==============================================================================
{cBody Position Types Configuration{n
{g+{n==============================================================================

Current body position types ({y%d{n):
""" % len(all_types))
    
    sock.send_raw(format_tabular_list(all_types, markers))
    
    sock.send_raw("""
{y*{n = Built-in types

{c1{n) Add body position type
{c2{n) Remove body position type

{cQ{n) Return to main menu
""")

def body_types_chooser(sock, data, choice):
    """Handle body types menu choices"""
    if choice == '1':
        sock.send_raw("Enter new body position type: ")
        return 1
    elif choice == '2':
        sock.send_raw("Enter body position type to remove: ")
        return 2
    return MENU_CHOICE_INVALID

def body_types_parser(sock, data, choice, arg):
    """Parse body types input"""
    body_config = get_body_config()
    
    if choice == 1 and arg:
        type_name = arg.strip()
        builtin_types = world.get_bodypos_types()
        all_types = list(builtin_types) + body_config.body_types.get_bodypos_types()
        if type_name and type_name not in all_types:
            body_config.body_types.add_bodypart_type(type_name)
            # Register with world system immediately
            try:
                world.add_bodypos_type(type_name)
                sock.send_raw(f"Added body position type: {type_name}\n")
            except ValueError:
                sock.send_raw(f"Failed to register body position type: {type_name}\n")
            return True
        else:
            sock.send_raw(f"Body position type '{type_name}' already exists or invalid name.\n")
            return True  # Return to menu instead of staying in parser
    elif choice == 2 and arg:
        type_name = arg.strip()
        # Get original built-in position types (before any custom additions)
        original_builtin_types = ["floating about head", "about body", "head", "face", "ear", "neck", "torso", "arm", "wing", "wrist", "left hand", "right hand", "finger", "waist", "leg", "left foot", "right foot", "hoof", "claw", "tail", "held"]
        mud.log_string(f"Remove attempt: type='{type_name}', in_custom={type_name in body_config.body_types.get_bodypos_types()}, in_original_builtin={type_name in original_builtin_types}")
        
        if type_name in body_config.body_types.get_bodypos_types() and type_name not in original_builtin_types:
            body_config.body_types.remove_bodypart_type(type_name)
            # Remove from world system immediately
            try:
                world.remove_bodypos_type(type_name)
                sock.send_raw(f"Removed body position type: {type_name}\n")
                mud.log_string(f"Successfully removed body position type: {type_name}")
            except ValueError as e:
                sock.send_raw(f"Removed body position type: {type_name} (config only)\n")
                mud.log_string(f"Failed to unregister body position type '{type_name}' from world system: {e}")
            except Exception as e:
                sock.send_raw(f"Removed body position type: {type_name} (config only)\n")
                mud.log_string(f"Error removing body position type '{type_name}' from world system: {e}")
            return True
        else:
            if type_name in original_builtin_types:
                sock.send_raw(f"Cannot remove built-in body position type: {type_name}\n")
                mud.log_string(f"Attempted to remove built-in body position type: {type_name}")
            else:
                sock.send_raw(f"Body position type '{type_name}' not found in custom types.\n")
                mud.log_string(f"Body position type '{type_name}' not found in custom types")
            return True  # Return to menu instead of staying in parser
    return False

# Body Sizes Menu
def body_sizes_menu(sock, data):
    """Body sizes configuration menu"""
    body_config = get_body_config()
    original_builtin_sizes = ["diminuitive", "tiny", "small", "medium", "large", "huge", "gargantuan", "collosal"]
    custom_sizes = body_config.body_types.bodysizes
    
    # Combine built-in and custom sizes
    all_sizes = list(original_builtin_sizes) + [size for size in custom_sizes if size not in original_builtin_sizes]
    
    # Create markers dict for built-in vs custom sizes
    markers = {}
    for size in all_sizes:
        markers[size] = "*" if size in original_builtin_sizes else " "
    
    sock.send_raw("""
{g+{n==============================================================================
{cBody Sizes Configuration{n
{g+{n==============================================================================

Current body sizes ({y%d{n):
""" % len(all_sizes))
    
    sock.send_raw(format_tabular_list(all_sizes, markers))
    
    sock.send_raw("""
{y*{n = Built-in sizes

{c1{n) Add body size
{c2{n) Remove body size

{cQ{n) Return to main menu
""")

def body_sizes_chooser(sock, data, choice):
    """Handle body sizes menu choices"""
    if choice == '1':
        sock.send_raw("Enter new body size: ")
        return 1
    elif choice == '2':
        sock.send_raw("Enter body size to remove: ")
        return 2
    return MENU_CHOICE_INVALID

def body_sizes_parser(sock, data, choice, arg):
    """Parse body sizes input"""
    body_config = get_body_config()
    
    if choice == 1 and arg:
        size = arg.strip()
        builtin_sizes = world.get_bodysizes()
        all_sizes = list(builtin_sizes) + body_config.body_types.get_bodysizes()
        if size and size not in all_sizes:
            body_config.body_types.add_bodysize(size)
            # Register with world system immediately
            try:
                world.add_bodysize(size)
                sock.send_raw(f"Added body size: {size}\n")
            except ValueError:
                sock.send_raw(f"Failed to register body size: {size}\n")
            return True
        else:
            sock.send_raw(f"Body size '{size}' already exists or invalid name.\n")
            return True  # Return to menu instead of staying in parser
    elif choice == 2 and arg:
        size = arg.strip()
        # Get the original built-in sizes (before any custom additions)
        original_builtin_sizes = ["diminuitive", "tiny", "small", "medium", "large", "huge", "gargantuan", "collosal"]
        mud.log_string(f"Remove attempt: size='{size}', in_custom={size in body_config.body_types.get_bodysizes()}, in_original_builtin={size in original_builtin_sizes}")
        
        if size in body_config.body_types.get_bodysizes() and size not in original_builtin_sizes:
            body_config.body_types.remove_bodysize(size)
            # Remove from world system immediately
            try:
                world.remove_bodysize(size)
                sock.send_raw(f"Removed body size: {size}\n")
                mud.log_string(f"Successfully removed body size: {size}")
            except ValueError as e:
                sock.send_raw(f"Removed body size: {size} (config only)\n")
                mud.log_string(f"Failed to unregister body size '{size}' from world system: {e}")
            except Exception as e:
                sock.send_raw(f"Removed body size: {size} (config only)\n")
                mud.log_string(f"Error removing body size '{size}' from world system: {e}")
            return True
        else:
            if size in original_builtin_sizes:
                sock.send_raw(f"Cannot remove built-in body size: {size}\n")
                mud.log_string(f"Attempted to remove built-in body size: {size}")
            else:
                sock.send_raw(f"Body size '{size}' not found in custom sizes.\n")
                mud.log_string(f"Body size '{size}' not found in custom sizes")
            return True  # Return to menu instead of staying in parser
    return False

# Helper function for race display with built-in markers
def format_race_list_with_builtin(all_races, race_config, custom_races, line_width=78):
    """Format races showing built-in vs custom races in two columns"""
    if not all_races:
        return "  (none)\n"
    
    result = ""
    sorted_races = sorted(all_races)
    
    # Calculate column width for two-column layout
    max_race_info_length = 0
    race_info_list = []
    
    for race_name in sorted_races:
        # Check if this is a built-in race or custom race
        is_builtin = race_name not in custom_races
        marker = "*" if is_builtin else " "
        
        if is_builtin:
            # For built-in races, use hardcoded info since world.get_race_info() doesn't work properly
            if race_name == "human":
                abbrev = "hum"
                pc_ok = True
                body_positions = 15  # Approximate - human has standard body
            elif race_name == "hill giant":
                abbrev = "gia"
                pc_ok = False
                body_positions = 15  # Approximate - similar to human but larger
            else:
                abbrev = race_name[:3]
                pc_ok = False
                body_positions = 15
        else:
            # For custom races, get info from config
            race = race_config.get_race(race_name)
            abbrev = race.abbrev
            pc_ok = race.pc_ok
            body_positions = len(race.body_positions)
        
        pc_flag = "PC" if pc_ok else "NPC"
        race_info = f"{marker} {race_name} ({abbrev}) - {pc_flag}, {body_positions} pos"
        race_info_list.append(race_info)
        max_race_info_length = max(max_race_info_length, len(race_info))
    
    # Format in two columns
    column_width = max_race_info_length + 2  # Add padding
    cols_per_line = max(1, (line_width - 2) // column_width)
    
    for i in range(0, len(race_info_list), cols_per_line):
        line_items = race_info_list[i:i + cols_per_line]
        line = "  "
        
        for item in line_items:
            formatted = item.ljust(column_width)
            line += formatted
        
        result += line.rstrip() + "\n"
        
        # Limit display for very long lists
        if i >= 20:
            remaining = len(race_info_list) - i - cols_per_line
            if remaining > 0:
                result += f"   ... and {remaining} more\n"
            break
    
    return result

# Races Menu
def races_menu(sock, data):
    """Races configuration menu"""
    race_config = get_race_config()
    
    # Get custom races from config and built-in races separately
    custom_races = race_config.get_race_names()
    
    # Combine custom races with known built-in races
    builtin_races = ["human", "hill giant"]  # Add other built-in races as needed
    all_races = list(custom_races) + [race for race in builtin_races if race not in custom_races]
    
    sock.send_raw("""
{g+{n==============================================================================
{cRaces Configuration{n
{g+{n==============================================================================

Current races ({y%d{n):
""" % len(all_races))
    
    sock.send_raw(format_race_list_with_builtin(all_races, race_config, custom_races))
    
    sock.send_raw("""
{y*{n = Built-in races

{c1{n) Add race
{c2{n) Remove race
{c3{n) Edit race

{cQ{n) Return to main menu
""")

def races_chooser(sock, data, choice):
    """Handle races menu choices"""
    if choice == '1':
        sock.send_raw("Enter new race name: ")
        return 1
    elif choice == '2':
        sock.send_raw("Enter race name to remove: ")
        return 2
    elif choice == '3':
        sock.send_raw("Enter race name to edit: ")
        return 3
    return MENU_CHOICE_INVALID

def races_parser(sock, data, choice, arg):
    """Parse races input"""
    race_config = get_race_config()
    custom_races = race_config.get_race_names()
    builtin_races = ["human", "hill giant"]
    all_races = list(custom_races) + [race for race in builtin_races if race not in custom_races]
    
    if choice == 1 and arg:
        race_name = arg.strip()
        if race_name and race_name not in all_races:
            race = Race(race_name, race_name[:3].lower(), False)
            race_config.add_race(race)
            sock.send_raw(f"Created new race: {race_name}\n")
            # Start race editing
            olc.do_olc(sock, race_menu, race_chooser, race_parser, race_saver, race)
            return True
        else:
            sock.send_raw(f"Race '{race_name}' already exists or invalid name.\n")
            return True  # Return to menu instead of staying in parser
    elif choice == 2 and arg:
        race_name = arg.strip()
        if race_name in custom_races:
            race_config.remove_race(race_name)
            sock.send_raw(f"Removed race: {race_name}\n")
            return True
        else:
            sock.send_raw(f"Race '{race_name}' not found or is built-in (cannot remove).\n")
            return True  # Return to menu instead of staying in parser
    elif choice == 3 and arg:
        race_name = arg.strip()
        if race_name in custom_races:
            race = race_config.get_race(race_name)
            # Start race editing
            olc.do_olc(sock, race_menu, race_chooser, race_parser, race_saver, race)
            return True
        else:
            sock.send_raw(f"Race '{race_name}' not found or is built-in (cannot edit).\n")
            return True  # Return to menu instead of staying in parser
    return False

# Race OLC Menu Constants
RACE_NAME = 1
RACE_ABBREV = 2
RACE_PC_OK = 3
RACE_BODY_SIZE = 4
RACE_BODY_POSITIONS = 5

def race_menu(sock, race):
    """Display race editing menu."""
    # Calculate total weight
    total_weight = sum(pos.weight for pos in race.body_positions)
    
    sock.send_raw("""
{g+{n==============================================================================
{c%s{n
{g+{n==============================================================================

{c1{n) Name        : {y%s{n
{c2{n) Abbreviation: {y%s{n
{c3{n) PC OK       : {y%s{n
{c4{n) Body Size   : {y%s{n
{c5{n) Body Positions ({y%d{n) - Total weight: {y%d%%{n

{cS{n) Save
{cQ{n) Quit

Enter choice: """ % (
        race.name,
        race.name,
        race.abbrev,
        'Yes' if race.pc_ok else 'No',
        race.body_size,
        len(race.body_positions),
        total_weight
    ))

def race_chooser(sock, race, choice):
    """Handle race menu choices."""
    choice = choice.upper()
    
    if choice == '1':
        sock.send_raw("Enter new race name: ")
        return RACE_NAME
    elif choice == '2':
        sock.send_raw("Enter race abbreviation (3 chars): ")
        return RACE_ABBREV
    elif choice == '3':
        race.pc_ok = not race.pc_ok
        sock.send_raw(f"PC OK set to: {'Yes' if race.pc_ok else 'No'}\n")
        return MENU_NOCHOICE
    elif choice == '4':
        # Display available body sizes
        body_config = get_body_config()
        original_builtin_sizes = ["diminuitive", "tiny", "small", "medium", "large", "huge", "gargantuan", "collosal"]
        custom_sizes = body_config.body_types.bodysizes
        all_sizes = list(original_builtin_sizes) + [size for size in custom_sizes if size not in original_builtin_sizes]
        
        # Create markers dict for built-in vs custom sizes
        markers = {}
        for size in all_sizes:
            markers[size] = "*" if size in original_builtin_sizes else " "
        
        sock.send_raw(f"\nAvailable body sizes ({len(all_sizes)}):\n")
        sock.send_raw(format_tabular_list(all_sizes, markers))
        sock.send_raw("\nEnter body size: ")
        return RACE_BODY_SIZE
    elif choice == '5':
        olc.do_olc(sock, race_positions_menu, race_positions_chooser,
                   race_positions_parser, None, race)
        return MENU_NOCHOICE
    else:
        return MENU_CHOICE_INVALID

def race_parser(sock, race, choice, arg):
    """Parse race input."""
    if choice == RACE_NAME:
        if arg.strip():
            race.name = arg.strip()
            return True
        return False
    
    elif choice == RACE_ABBREV:
        abbrev = arg.strip()[:3].lower()
        if abbrev:
            race.abbrev = abbrev
            return True
        return False
    
    elif choice == RACE_BODY_SIZE:
        size = arg.strip().lower()
        if size:
            # Validate against available sizes
            body_config = get_body_config()
            original_builtin_sizes = ["diminuitive", "tiny", "small", "medium", "large", "huge", "gargantuan", "collosal"]
            custom_sizes = body_config.body_types.bodysizes
            all_sizes = list(original_builtin_sizes) + [size for size in custom_sizes if size not in original_builtin_sizes]
            
            if size in all_sizes:
                race.body_size = size
                return True
            else:
                sock.send_raw(f"Invalid body size '{size}'. Please choose from available sizes.\n")
                return False
        return False
    
    return False

def race_saver(race):
    """Save race configuration."""
    save_race_config()
    return True

# Race Body Positions Menu
def race_positions_menu(sock, race):
    """Display race body positions menu."""
    # Calculate total weight
    total_weight = sum(pos.weight for pos in race.body_positions)
    
    sock.send_raw("""
{g+{n==============================================================================
{c%s - Body Positions{n
{g+{n==============================================================================

Current body positions ({y%d{n) - Total weight: {y%d%%{n:
""" % (race.name, len(race.body_positions), total_weight))
    
    # Format body positions in tabular format
    if race.body_positions:
        position_strings = []
        for pos in race.body_positions:
            # Truncate type to 10 chars with ellipsis if needed
            truncated_type = pos.pos_type[:7] + "..." if len(pos.pos_type) > 10 else pos.pos_type
            position_strings.append(f"{pos.name} ({truncated_type}, {pos.weight}%)")
        
        # Display in two columns
        sock.send_raw(format_tabular_list(position_strings, None, 78))
    else:
        sock.send_raw("  (no body positions defined)\n")
    
    sock.send_raw("""
{c1{n) Add body position
{c2{n) Remove body position
{c3{n) Edit body position

{cQ{n) Return to race menu

Enter choice: """)

# Constants for body position creation states
POS_NAME = 101
POS_TYPE = 102
POS_WEIGHT = 103
POS_EDIT_NAME = 201
POS_EDIT_TYPE = 202
POS_EDIT_WEIGHT = 203

def race_positions_chooser(sock, race, choice):
    """Handle race positions menu choices"""
    if choice == '1':
        # Display available body position types for reference
        body_config = get_body_config()
        original_builtin_types = ["floating about head", "about body", "head", "face", "ear", "neck", "torso", "arm", "wing", "wrist", "left hand", "right hand", "finger", "waist", "leg", "left foot", "right foot", "hoof", "claw", "tail", "held"]
        custom_types = body_config.body_types.bodypart_types
        all_types = list(original_builtin_types) + [pos_type for pos_type in custom_types if pos_type not in original_builtin_types]
        
        # Create markers dict for built-in vs custom types
        markers = {}
        for pos_type in all_types:
            markers[pos_type] = "*" if pos_type in original_builtin_types else " "
        
        sock.send_raw(f"\nAvailable body position types ({len(all_types)}):\n")
        sock.send_raw(format_tabular_list(all_types, markers))
        sock.send_raw("\nEnter position as: <name>, <type>, <weight>\n")
        sock.send_raw("Example: left wing, wing, 8\n")
        sock.send_raw("Position: ")
        return 1
    elif choice == '2':
        sock.send_raw("Enter position name to remove: ")
        return 2
    elif choice == '3':
        sock.send_raw("Enter position name to edit: ")
        return 3
    return MENU_CHOICE_INVALID

def race_positions_parser(sock, race, choice, arg):
    """Parse race positions input"""
    if choice == 1 and arg:
        # Parse format: "name, type, weight" 
        parts = [part.strip() for part in arg.strip().split(',')]
        if len(parts) == 3:
            try:
                name = parts[0]
                pos_type = parts[1]
                weight = int(parts[2])
                
                # Validate position type
                body_config = get_body_config()
                original_builtin_types = ["floating about head", "about body", "head", "face", "ear", "neck", "torso", "arm", "wing", "wrist", "left hand", "right hand", "finger", "waist", "leg", "left foot", "right foot", "hoof", "claw", "tail", "held"]
                custom_types = body_config.body_types.bodypart_types
                all_types = list(original_builtin_types) + [t for t in custom_types if t not in original_builtin_types]
                
                if pos_type not in all_types:
                    sock.send_raw(f"Invalid position type '{pos_type}'.\n")
                    sock.send_raw("Available types: " + ", ".join(all_types) + "\n")
                    return False
                
                position = BodyPosition(name, pos_type, weight)
                race.add_position(position)
                sock.send_raw(f"Added body position: {name} ({pos_type}, {weight}%)\n")
                return True
            except ValueError:
                sock.send_raw("Invalid weight. Must be a number.\n")
                return False
        else:
            sock.send_raw("Usage: <name>, <type>, <weight>\n")
            sock.send_raw("Example: left wing, wing, 8\n")
            return False
    elif choice == 2 and arg:
        name = arg.strip()
        if race.get_position(name):
            race.remove_position(name)
            sock.send_raw(f"Removed position: {name}\n")
            return True
        else:
            sock.send_raw(f"Position '{name}' not found.\n")
        return False
    elif choice == 3 and arg and not hasattr(race, 'temp_edit_name'):
        name = arg.strip()
        position = race.get_position(name)
        if position:
            # Get all available types from C code
            all_body_types = world.get_bodypos_types()
            original_builtin_types = world.get_bodypos_types()
            custom_types = all_body_types
            all_types = list(original_builtin_types) + [pos_type for pos_type in custom_types if pos_type not in original_builtin_types]
            
            # Create markers dict for built-in vs custom types
            markers = {}
            for pos_type in all_types:
                markers[pos_type] = "*" if pos_type in original_builtin_types else " "
            
            sock.send_raw("\n{gEditing position: {w" + name + "{n\n")
            sock.send_raw("{gAvailable body position types (" + str(len(all_types)) + "):{n\n")
            sock.send_raw(format_tabular_list(all_types, markers))
            sock.send_raw("\n{gCurrent: {w" + position.name + " ({y" + position.pos_type + ", " + str(position.weight) + "%{w){n\n")
            sock.send_raw("\n{gEnter new position as: {w<name>, <type>, <weight>{n\n")
            sock.send_raw("Example: left wing, wing, 8\n")
            sock.send_raw("Or press Enter to cancel\n")
            sock.send_raw("New position: ")
            
            # Store the position name being edited
            race.temp_edit_name = name
            return False  # Stay in input mode for next step
        else:
            sock.send_raw(f"Position '{name}' not found.\n")
            return False
    elif choice == 3 and hasattr(race, 'temp_edit_name'):
        # Handle edit mode - single-line input like add mode
        if not arg.strip():
            # Cancel edit
            delattr(race, 'temp_edit_name')
            sock.send_raw("Edit cancelled.\n")
            return True
        
        # Parse format: "name, type, weight" 
        parts = [part.strip() for part in arg.strip().split(',')]
        if len(parts) == 3:
            try:
                new_name = parts[0]
                pos_type = parts[1]
                weight = int(parts[2])
                
                # Validate position type
                body_config = get_body_config()
                original_builtin_types = ["floating about head", "about body", "head", "face", "ear", "neck", "torso", "arm", "wing", "wrist", "left hand", "right hand", "finger", "waist", "leg", "left foot", "right foot", "hoof", "claw", "tail", "held"]
                custom_types = body_config.body_types.bodypart_types
                all_types = list(original_builtin_types) + [t for t in custom_types if t not in original_builtin_types]
                
                if pos_type not in all_types:
                    sock.send_raw(f"Invalid position type '{pos_type}'.\n")
                    sock.send_raw("Available types: " + ", ".join(all_types) + "\n")
                    return False
                
                # Find and update the position
                old_name = race.temp_edit_name
                position = race.get_position(old_name)
                if position:
                    # Remove old position and add updated one
                    race.remove_position(old_name)
                    new_position = BodyPosition(new_name, pos_type, weight)
                    race.add_position(new_position)
                    sock.send_raw(f"Updated position: {new_name} ({pos_type}, {weight}%)\n")
                    delattr(race, 'temp_edit_name')
                    return True
                else:
                    sock.send_raw(f"Position '{old_name}' not found.\n")
                    delattr(race, 'temp_edit_name')
                    return False
            except ValueError:
                sock.send_raw("Invalid weight. Must be a number.\n")
                return False
        else:
            sock.send_raw("Usage: <name>, <type>, <weight>\n")
            sock.send_raw("Example: left wing, wing, 8\n")
            return False
    return False

# Register the main OLC command
def cmd_entityconfig(ch, cmd, arg):
    """
    Syntax: entityconfig
    
    Opens the entities configuration editor for managing body position types,
    body sizes, and races.
    """
    olc.do_olc(ch.sock, entities_config_menu, entities_config_chooser, entities_config_parser, 
               lambda data: (save_race_config(), save_body_config()), None)

# Register command
add_cmd("entityconfig", None, cmd_entityconfig, "admin", False)
