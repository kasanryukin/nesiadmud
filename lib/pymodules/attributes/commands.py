"""
Attribute Commands
==================
Player and admin commands for viewing and training attributes.
"""

import mudsys
import mud
from . import attribute_data
from . import attribute_aux

# Store pending training confirmations
_pending_training = {}

"""
Enhanced stats command showing vitality with regeneration rates
"""

def cmd_stats(ch, cmd, arg):
    """
    Display character statistics including HP/SP/EP, attributes, and TDP.
    Now includes regeneration rate information.
    
    Usage: stats
    """
    from . import attribute_aux, attribute_data
    
    # Get auxiliary data
    aux = attribute_aux.get_attributes(ch)
    if not aux:
        ch.send("You don't have any attributes yet.")
        return
    
    # Get vitality data
    try:
        import vitality.vitality_core as vitality_core
        import vitality.vitality_regen as vitality_regen
        vit_aux = vitality_core.get_vitality(ch)
        VITALITY_AVAILABLE = vit_aux is not None
    except ImportError:
        VITALITY_AVAILABLE = False
        vit_aux = None
    
    # Build output with simple ASCII
    lines = [
        "",
        "{c+-----------------------------------------------------------+{n",
        f"{{c|{{C          Character Statistics - {{W{ch.name:^15s}{{C           {{c|{{n",
        "{c+-----------------------------------------------------------+{n"
    ]
    
    # Vitality section (if available)
    if VITALITY_AVAILABLE and vit_aux:
        hp_percent = (vit_aux.hp / vit_aux.max_hp * 100) if vit_aux.max_hp > 0 else 0
        sp_percent = (vit_aux.sp / vit_aux.max_sp * 100) if vit_aux.max_sp > 0 else 0
        ep_percent = (vit_aux.ep / vit_aux.max_ep * 100) if vit_aux.max_ep > 0 else 0
        
        hp_color = vitality_core.get_vitality_color(hp_percent)
        sp_color = vitality_core.get_vitality_color(sp_percent)
        ep_color = vitality_core.get_vitality_color(ep_percent)
        
        # Get regen rates
        position_mod = vitality_regen.get_position_modifier(ch)
        hp_regen = vitality_regen.calculate_hp_regen_rate(ch) * position_mod
        sp_regen = vitality_regen.calculate_sp_regen_rate(ch) * position_mod
        ep_regen = vitality_regen.calculate_ep_regen_rate(ch) * position_mod
        
        lines.extend([
            "{c|{C                  Vitality Pools                        {c|{n",
            "{c+-----------------------------------------------------------+{n",
            f"{{c|{{n  Health:  {hp_color}{vit_aux.hp:6.0f}{{n/{{G{vit_aux.max_hp:<6.0f}{{n "
            f"({hp_color}{hp_percent:5.1f}%{{n) +{{g{hp_regen:4.1f}{{n/tick  {{c|{{n",
            f"{{c|{{n  Spell:   {sp_color}{vit_aux.sp:6.0f}{{n/{{B{vit_aux.max_sp:<6.0f}{{n "
            f"({sp_color}{sp_percent:5.1f}%{{n) +{{b{sp_regen:4.1f}{{n/tick  {{c|{{n",
            f"{{c|{{n  Energy:  {ep_color}{vit_aux.ep:6.0f}{{n/{{Y{vit_aux.max_ep:<6.0f}{{n "
            f"({ep_color}{ep_percent:5.1f}%{{n) +{{y{ep_regen:4.1f}{{n/tick  {{c|{{n",
            "{c+-----------------------------------------------------------+{n"
        ])
    
    # Attributes section
    lines.extend([
        "{c|{C                    Attributes                            {c|{n",
        "{c+-----------------------------------------------------------+{n"
    ])
    
    # Show attributes in pairs
    attr_list = attribute_data.ATTRIBUTE_ORDER
    for i in range(0, len(attr_list), 2):
        attr1_key = attr_list[i]
        attr1_data = attribute_data.ATTRIBUTES[attr1_key]
        attr1_val = aux.get_attribute(attr1_key)
        
        if i + 1 < len(attr_list):
            attr2_key = attr_list[i + 1]
            attr2_data = attribute_data.ATTRIBUTES[attr2_key]
            attr2_val = aux.get_attribute(attr2_key)
            
            line = f"{{c|{{n  {{C{attr1_data['abbr']}{{n {{W{attr1_data['name']:12s}{{n: {{Y{attr1_val:3d}{{n      " \
                   f"{{C{attr2_data['abbr']}{{n {{W{attr2_data['name']:12s}{{n: {{Y{attr2_val:3d}{{n  {{c|{{n"
        else:
            line = f"{{c|{{n  {{C{attr1_data['abbr']}{{n {{W{attr1_data['name']:12s}{{n: {{Y{attr1_val:3d}{{n" + \
                   " " * 28 + "{{c|{{n"
        
        lines.append(line)
    
    # TDP section
    lines.extend([
        "{c+-----------------------------------------------------------+{n",
        f"{{c|{{C  Training Points (TDP):                    {{Y{aux.tdp_available:10d}{{C     {{c|{{n",
        "{c+-----------------------------------------------------------+{n",
        "",
        "Type '{Gtrain{n' to see training costs or '{Gattributes{n' for attribute info.",
        ""
    ])
    
    ch.send("\r\n".join(lines))


def cmd_train(ch, cmd, arg):
    """
    Train an attribute using TDP.
    
    Usage: 
        train                  - Show training information
        train <attribute>      - Train attribute by 1 point
        train <attribute> <#>  - Train attribute by # points
    
    Args:
        ch: Character executing the command
        cmd: The command string used
        arg: Arguments (attribute name and optional points)
    """
    # Get the character's attribute data
    aux = attribute_aux.get_attributes(ch)
    
    if not aux:
        ch.send("You don't have any attributes! This is a bug.")
        return
    
    # If no arguments, show training information
    if not arg or arg.strip() == "":
        show_train_info(ch, aux)
        return
    
    # Parse arguments
    args = arg.split()
    attr_name = args[0].lower()
    
    # Get number of points to train (default 1)
    points = 1
    if len(args) > 1:
        try:
            points = int(args[1])
            if points < 1:
                ch.send("You must train at least 1 point.")
                return
            if points > 50:
                ch.send("You cannot train more than 20 points at once.")
                return
        except ValueError:
            ch.send("Invalid number of points.")
            return
    
    # Validate attribute name
    if attr_name not in attribute_data.get_attribute_names():
        # Try matching abbreviation
        found = False
        for name in attribute_data.get_attribute_names():
            if attribute_data.get_attribute_abbrev(name).lower() == attr_name:
                attr_name = name
                found = True
                break
        
        if not found:
            ch.send(f"'{attr_name}' is not a valid attribute.")
            ch.send(f"Valid attributes: {', '.join(attribute_data.get_attribute_names())}")
            return
    
    # Calculate cost
    current_value = aux.get_attribute(attr_name)
    cost = attribute_data.calculate_tdp_cost(current_value, current_value + points)
    
    # Check if they can afford it
    if cost > aux.tdp_available:
        ch.send(f"{{RInsufficient TDP!{{n")
        ch.send(f"Cost: {{R}}{cost}{{n TDP, Available: {{Y}}{aux.tdp_available}{{n TDP")
        ch.send(f"You need {{R}}{cost - aux.tdp_available}{{n more TDP.")
        return
    
    # Check if at cap
    if current_value + points > 255:
        ch.send(f"{{RThat would exceed the maximum attribute value of 255!{{n")
        return
    
    # Store training info on socket for confirmation
    sock = ch.sock
    if not sock:
        ch.send("You need a socket connection to train attributes.")
        return
        
    # Use character UID as key to store training data
    _pending_training[ch.uid] = {
        'attr': attr_name,
        'points': points,
        'cost': cost
    }
    
    # Push confirmation input handler
    sock.push_ih(train_confirm_handler, train_confirm_prompt)


def show_train_info(ch, aux):
    """
    Display training costs and current attributes.
    
    Args:
        ch: Character to show info to
        aux: Character's attribute data
    """
    output = []
    output.append("{c┌─────────────────────────────────────────────────────────┐{n")
    output.append("{c│{n              {WATTRIBUTE TRAINING{n                      {c│{n")
    output.append("{c├─────────────────────────────────────────────────────────┤{n")
    output.append("{c│{n {YAvailable TDP:{n " + f"{aux.tdp_available:>4}" + " " * 34 + "{c│{n")
    output.append("{c├─────────────────────────────────────────────────────────┤{n")
    output.append("{c│{n Attribute      Current  +1 Cost  +5 Cost  +10 Cost  {c│{n")
    output.append("{c├─────────────────────────────────────────────────────────┤{n")
    
    for attr_name in attribute_data.get_attribute_names():
        current = aux.get_attribute(attr_name)
        cost_1 = attribute_data.calculate_tdp_cost(current, current + 1)
        cost_5 = attribute_data.calculate_tdp_cost(current, current + 5)
        cost_10 = attribute_data.calculate_tdp_cost(current, current + 10)
        
        # Format display
        display_name = attr_name.capitalize()[:12]  # Truncate if needed
        
        # Color code costs based on affordability
        color_1 = "{G" if cost_1 <= aux.tdp_available else "{R"
        color_5 = "{G" if cost_5 <= aux.tdp_available else "{R"
        color_10 = "{G" if cost_10 <= aux.tdp_available else "{R"
        
        output.append(f"{{c│{{n {display_name:<12}   {current:>3}    "
                     f"{color_1}{cost_1:>5}{{n   "
                     f"{color_5}{cost_5:>6}{{n   "
                     f"{color_10}{cost_10:>7}{{n  {{c│{{n")
    
    output.append("{c└─────────────────────────────────────────────────────────┘{n")
    output.append("")
    output.append("{GGreen{n = You can afford  |  {RRed{n = Cannot afford")
    output.append("")
    output.append("Usage: {Wtrain <attribute> [points]{n")
    output.append("Example: {Wtrain strength{n or {Wtrain str 5{n")
    output.append("")
    output.append("{YNote:{n Training costs increase exponentially as attributes get higher.")
    output.append("       Attributes at 75+ cost 300 TDP per point.")
    
    ch.send("\r\n".join(output))

def train_confirm_handler(sock, arg):
    """Handle confirmation for training"""
    choice = arg.strip().upper()
    
    # Retrieve stored training info using character UID
    ch_uid = sock.ch.uid
    if ch_uid not in _pending_training:
        sock.send("Error: Training data not found.")
        sock.pop_ih()
        return
    
    training_data = _pending_training[ch_uid]
    attr_name = training_data['attr']
    points = training_data['points']
    cost = training_data['cost']
    
    if choice in ['Y', 'YES']:
        # Get fresh aux data
        aux = attribute_aux.get_attributes(sock.ch)
        if not aux:
            sock.send("Error: Could not retrieve your attributes.")
            sock.pop_ih()
            del _pending_training[ch_uid]
            return
        
        # Attempt the training
        success, actual_cost, message = aux.train_attribute(attr_name, points)
        
        if success:
            sock.send(f"{{GSuccess!{{n {message}")
            
            # Recalculate vitality from new attributes
            try:
                import vitality.vitality_core as vitality
                vitality.recalculate_vitality(sock.ch)
                sock.send("{cYour vitality has been recalculated based on your new attributes.{n")
            except ImportError:
                pass  # Vitality module not loaded yet
        else:
            sock.send(f"{{RFailed:{{n {message}")
    else:
        sock.send("{YTraining cancelled.{n")
    
    # Clean up
    del _pending_training[ch_uid]
    sock.pop_ih()


def train_confirm_prompt(sock):
    """Display confirmation prompt for training"""
    ch_uid = sock.ch.uid
    if ch_uid not in _pending_training:
        sock.send("Error: Training data not found.")
        return
    
    training_data = _pending_training[ch_uid]
    attr_name = training_data['attr']
    points = training_data['points']
    cost = training_data['cost']
    
    aux = attribute_aux.get_attributes(sock.ch)
    current = aux.get_attribute(attr_name)
    new_value = current + points
    
    sock.send("")
    sock.send("{W╔═══════════════════════════════════════════════╗{n")
    sock.send("{W║{n        {YTRAINING CONFIRMATION{n              {W║{n")
    sock.send("{W╠═══════════════════════════════════════════════╣{n")
    sock.send(f"{{W║{{n Attribute: {{C}}{attr_name.capitalize():<30}{{n {{W║{{n")
    sock.send(f"{{W║{{n Current:   {{Y}}{current:>3}{{n                              {{W║{{n")
    sock.send(f"{{W║{{n New Value: {{G}}{new_value:>3}{{n  {{W(+{points}){{n                    {{W║{{n")
    sock.send(f"{{W║{{n                                               {{W║{{n")
    sock.send(f"{{W║{{n Total Cost: {{R}}{cost:>4}{{n TDP                       {{W║{{n")
    sock.send(f"{{W║{{n Remaining:  {{Y}}{aux.tdp_available - cost:>4}{{n TDP                       {{W║{{n")
    sock.send("{W╚═══════════════════════════════════════════════╝{n")
    sock.send("")
    sock.send_raw("{WProceed with training? (Y/N):{n ")

def cmd_attributes(ch, cmd, arg):
    """
    Display detailed attribute information and descriptions.
    
    Usage:
        attributes              - List all attributes
        attributes <attr>       - Show details about specific attribute
    
    Args:
        ch: Character executing the command
        cmd: The command string used
        arg: Optional attribute name
    """
    # If no argument, show all attributes with descriptions
    if not arg or arg.strip() == "":
        output = []
        output.append("{W┌────────────────────────────────────────────────────────────┐{n")
        output.append("{W│{n                    {YATTRIBUTE GUIDE{n                         {W│{n")
        output.append("{W├────────────────────────────────────────────────────────────┤{n")
        
        for attr_name in attribute_data.get_attribute_names():
            abbrev = attribute_data.get_attribute_abbrev(attr_name)
            desc = attribute_data.get_attribute_description(attr_name)
            
            output.append(f"{{W│{{n {{C}}{abbrev}{{n - {{G}}{attr_name.capitalize():<15}{{n" + " " * 28 + "{{W│{{n")
            output.append(f"{{W│{{n   {desc:<54} {{W│{{n")
            output.append("{W│{n" + " " * 60 + "{W│{n")
        
        output.append("{W└────────────────────────────────────────────────────────────┘{n")
        ch.send("\r\n".join(output))
        return
    
    # Show specific attribute details
    attr_name = arg.strip().lower()
    
    # Validate attribute
    if attr_name not in attribute_data.get_attribute_names():
        # Try abbreviation
        found = False
        for name in attribute_data.get_attribute_names():
            if attribute_data.get_attribute_abbrev(name).lower() == attr_name:
                attr_name = name
                found = True
                break
        
        if not found:
            ch.send(f"'{attr_name}' is not a valid attribute.")
            return
    
    # Get character's value
    aux = attribute_aux.get_attributes(ch)
    current_value = aux.get_attribute(attr_name) if aux else 10
    
    # Display detailed info
    abbrev = attribute_data.get_attribute_abbrev(attr_name)
    desc = attribute_data.get_attribute_description(attr_name)
    
    output = []
    output.append(f"{{W{attr_name.upper()}{{n ({{C}}{abbrev}{{n)")
    output.append(f"Current Value: {{Y}}{current_value}{{n")
    output.append(f"Description: {desc}")
    output.append("")
    output.append("Effects:")
    # TODO: Add specific effect descriptions based on attribute
    # For now, generic
    output.append(f"  - Affects related skill checks")
    output.append(f"  - Modifies certain game mechanics")
    
    ch.send("\r\n".join(output))


def cmd_setattr(ch, cmd, arg):
    """
    Admin command to set a character's attribute.
    
    Usage: setattr <target> <attribute> <value>
    
    Args:
        ch: Character executing the command (must be admin)
        cmd: The command string used
        arg: Target character, attribute, and value
    """
    # Parse arguments
    args = arg.split()
    if len(args) < 3:
        ch.send("Usage: setattr <target> <attribute> <value>")
        return
    
    target_name = args[0]
    attr_name = args[1].lower()
    
    try:
        value = int(args[2])
    except ValueError:
        ch.send("Value must be a number.")
        return
    
    # Find target character
    # First check if targeting self
    if target_name.lower() == "self" or target_name.lower() == ch.name.lower():
        target = ch
    else:
        # Try to find in same room
        target = None
        for char in ch.room.chars:
            if char.name.lower().startswith(target_name.lower()):
                target = char
                break
        
        if not target:
            ch.send(f"Cannot find '{target_name}' in this room.")
            return
    
    # Validate attribute
    if attr_name not in attribute_data.get_attribute_names():
        # Try matching abbreviation
        found = False
        for name in attribute_data.get_attribute_names():
            if attribute_data.get_attribute_abbrev(name).lower() == attr_name:
                attr_name = name
                found = True
                break
        
        if not found:
            ch.send(f"'{attr_name}' is not a valid attribute.")
            ch.send(f"Valid: {', '.join(attribute_data.get_attribute_names())}")
            return
    
    # Get target's attributes
    aux = attribute_aux.ensure_attributes(target)
    
    # Set the attribute
    old_value = aux.get_attribute(attr_name)
    aux.set_attribute(attr_name, value)
    new_value = aux.get_attribute(attr_name)
    
    # Notify
    ch.send(f"Set {target.name}'s {attr_name} from {old_value} to {new_value}.")
    target.send(f"Your {attr_name} has been set to {new_value}.")
    
    # Recalculate vitality if vitality module is loaded
    try:
        import vitality.vitality_core as vitality
        vitality.recalculate_vitality(target)
        ch.send(f"Recalculated {target.name}'s vitality.")
    except ImportError:
        pass


def cmd_grantdp(ch, cmd, arg):
    """
    Admin command to grant TDP to a character.
    
    Usage: grantdp <target> <amount>
    
    Args:
        ch: Character executing the command (must be admin)
        cmd: The command string used
        arg: Target character and TDP amount
    """
    # Parse arguments
    args = arg.split()
    if len(args) < 2:
        ch.send("Usage: grantdp <target> <amount>")
        return
    
    target_name = args[0]
    
    try:
        amount = int(args[1])
    except ValueError:
        ch.send("Amount must be a number.")
        return
    
    # Find target
    # First check if targeting self
    if target_name.lower() == "self" or target_name.lower() == ch.name.lower():
        target = ch
    else:
        # Try to find in same room
        target = None
        for char in ch.room.chars:
            if char.name.lower().startswith(target_name.lower()):
                target = char
                break
        
        if not target:
            ch.send(f"Cannot find '{target_name}' in this room.")
            return
    
    # Get target's attributes
    aux = attribute_aux.ensure_attributes(target)
    
    # Grant TDP
    old_tdp = aux.tdp_available
    aux.add_tdp(amount)
    new_tdp = aux.tdp_available
    
    # Notify
    ch.send(f"Granted {amount} TDP to {target.name}. ({old_tdp} -> {new_tdp})")
    target.send(f"You have been granted {amount} TDP! Total: {new_tdp}")


def register_commands():
    """
    Register all attribute commands with NakedMud.
    Called when the module loads.
    """
    # Player commands
    mudsys.add_cmd("stats", None, cmd_stats, "player", False)
    mudsys.add_cmd("train", None, cmd_train, "player", False)
    mudsys.add_cmd("attributes", None, cmd_attributes, "player", False)
    
    # Admin commands
    mudsys.add_cmd("setattr", None, cmd_setattr, "admin", False)
    mudsys.add_cmd("grantdp", None, cmd_grantdp, "admin", False)
    
    # Add command aliases
    mudsys.add_cmd_check("attr", "attributes")  # 'attr' is shortcut for 'attributes'
    
    mud.log_string("Attribute commands registered successfully")
