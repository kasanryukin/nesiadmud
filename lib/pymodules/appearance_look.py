'''
appearance_look.py

Formats character appearance for the look command with dynamic spacing.
'''

import mud

WINDOW_WIDTH = 80  # Total width including borders
CONTENT_WIDTH = WINDOW_WIDTH - 4  # Width minus "| " and " |"

def build_appearance_window(ch):
    """
    Build the appearance window for a character.
    Returns formatted string ready to send to player.
    """
    lines = []
    
    # Top border
    lines.append("=" * WINDOW_WIDTH)
    
    # Title line with dynamic padding
    title = getattr(ch, 'title', '') or ''
    name = ch.name or ''
    lastname = getattr(ch, 'lastname', '') or ''
    race = ch.race or ''
    char_class = getattr(ch, 'mob_class', '') or ''
    
    # Build the header content
    header_left = f"{title} {name} {lastname}".strip()
    header_right = f"{race} - {char_class}".strip()
    
    # Calculate spacing needed
    separator = " | "
    header_content = f"{header_left}{separator}{header_right}"
    
    # If it fits on one line, pad it
    if len(header_content) <= CONTENT_WIDTH:
        padding = CONTENT_WIDTH - len(header_content)
        header_line = f"| {header_content}{' ' * padding} |"
    else:
        # If too long, split across lines
        lines.append(f"| {header_left} |")
        header_line = f"| {header_right}{' ' * (CONTENT_WIDTH - len(header_right))} |"
    
    lines.append(header_line)
    
    # Blank line for overflow
    lines.append(f"|{' ' * CONTENT_WIDTH}|")
    
    # Top border
    lines.append("=" * WINDOW_WIDTH)
    
    # Appearance description lines
    appearance_text = build_appearance_description(ch)
    appearance_lines = wrap_text(appearance_text, CONTENT_WIDTH)
    for line in appearance_lines:
        lines.append(f"| {line.ljust(CONTENT_WIDTH)} |")
    
    # Equipment lines
    equipment_text = build_equipment_description(ch)
    equipment_lines = wrap_text(equipment_text, CONTENT_WIDTH)
    for line in equipment_lines:
        lines.append(f"| {line.ljust(CONTENT_WIDTH)} |")
    
    # Bottom border
    lines.append("=" * WINDOW_WIDTH)
    
    return "\n".join(lines)

def wrap_text(text, width):
    """
    Wrap text to fit within a given width.
    Returns list of lines.
    """
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        word_len = len(word)
        # +1 for space between words
        if current_length + word_len + (1 if current_line else 0) <= width:
            current_line.append(word)
            current_length += word_len + (1 if len(current_line) > 1 else 0)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_length = word_len
    
    if current_line:
        lines.append(" ".join(current_line))
    
    return lines

def build_appearance_description(ch):
    """
    Build the appearance text portion of the look window.
    """
    pronoun = get_pronoun_subject(ch)
    capitalized_pronoun = pronoun.capitalize()
    
    # Get appearance attributes with fallbacks to defaults
    fur_color = getattr(ch, 'fur_color', '') or ''
    fur_marking = getattr(ch, 'scale_marking', '') or ''
    feather_color = getattr(ch, 'feather_color', '') or ''
    skin_tone = getattr(ch, 'skin_tone', '') or ''
    hair_color = getattr(ch, 'hair_color', '') or ''
    hair_style = getattr(ch, 'hair_style', '') or ''
    beard_style = getattr(ch, 'beard_style', '') or ''
    tail_style = getattr(ch, 'tail_style', '') or ''
    mane_style = getattr(ch, 'mane_style', '') or ''
    eye_color = getattr(ch, 'eye_color', '') or ''
    eye_color_right = getattr(ch, 'eye_color_right', '') or ''
    heterochromia = getattr(ch, 'heterochromia', 0) or 0
    scale_color = getattr(ch, 'scale_color', '') or ''
    
    appearance_parts = []
    
    # Get race config to determine what to show
    try:
        from char_gen_enhancements import get_race_config, RACE_TO_CONFIG_KEY
        race_key = ch.race.lower()
        config_key = RACE_TO_CONFIG_KEY.get(race_key)
        race_config = get_race_config(ch.race)
    except:
        race_config = None
        config_key = None
    
    # Build appearance string based on race
    if race_config:
        # Fur races
        if race_config["has_fur"]:
            if fur_color:
                appearance_parts.append(f"{fur_color} fur")
            if fur_marking:
                appearance_parts.append(f"with {fur_marking}")
        # Feather races
        elif race_config["has_feathers"]:
            if feather_color:
                appearance_parts.append(f"{feather_color} feathers")
        # Scale races
        elif race_config["has_scales"]:
            if scale_color and fur_marking:
                appearance_parts.append(f"{scale_color} scales with {fur_marking}")
            elif scale_color:
                appearance_parts.append(f"{scale_color} scales")
        # Regular skin tones
        else:
            if skin_tone:
                appearance_parts.append(f"{skin_tone} skin")
    
    # Hair
    if hair_color and hair_style:
        appearance_parts.append(f"{hair_style} {hair_color} hair")
    elif hair_color:
        appearance_parts.append(f"{hair_color} hair")
    elif hair_style:
        appearance_parts.append(f"{hair_style} hair")
    
    # Beard
    if beard_style and beard_style.lower() != "none":
        appearance_parts.append(f"a {beard_style} beard")
    
    # Mane
    if mane_style and mane_style.lower() != "none":
        appearance_parts.append(f"a {mane_style} mane")
    
    # Wings (for Roshinver)
    if config_key == "roshinver" and tail_style:
        appearance_parts.append(f"{tail_style} wings")
    # Tail (for other races)
    elif tail_style and tail_style.lower() != "none":
        appearance_parts.append(f"a {tail_style} tail")
    
    # Eyes
    if heterochromia and eye_color and eye_color_right:
        eye_text = f"one {eye_color} eye and one {eye_color_right} eye"
        appearance_parts.append(eye_text)
    elif eye_color:
        appearance_parts.append(f"one {eye_color} eye")
    
    # Join all parts with commas and "and"
    if len(appearance_parts) == 0:
        appearance_text = f"{capitalized_pronoun} has a nondescript appearance."
    elif len(appearance_parts) == 1:
        appearance_text = f"{capitalized_pronoun} has {appearance_parts[0]}."
    else:
        # Join all but last with commas, then add "and" before last
        appearance_text = f"{capitalized_pronoun} has {', '.join(appearance_parts[:-1])}, and {appearance_parts[-1]}."
    
    return appearance_text

def build_equipment_description(ch):
    """
    Build the equipment text portion of the look window.
    """
    pronoun = get_pronoun_subject(ch)
    
    # Get equipped items
    equipped = []
    try:
        if hasattr(ch, 'eq') and ch.eq:
            for item in ch.eq:
                if item:
                    # Get item name with any extra descriptions
                    item_desc = item.name
                    if hasattr(item, 'rdesc') and item.rdesc:
                        # rdesc might have extra details like "trimmed with gold"
                        item_desc = f"{item.name} ({item.rdesc})"
                    equipped.append(item_desc)
    except:
        pass
    
    if len(equipped) == 0:
        equipment_text = f"{pronoun} is wearing: nothing."
    else:
        # Join equipment with commas and "and"
        if len(equipped) == 1:
            equipment_text = f"{pronoun} is wearing: {equipped[0]}."
        else:
            equipment_text = f"{pronoun} is wearing: {', '.join(equipped[:-1])}, and {equipped[-1]}."
    
    return equipment_text

def get_pronoun_subject(ch):
    """
    Get the subject pronoun for a character (he, she, they, etc.)
    """
    try:
        sex = ch.sex.lower()
        if sex == "male":
            return "he"
        elif sex == "female":
            return "she"
        else:  # non-binary, other
            return "they"
    except:
        return "they"

def get_pronoun_object(ch):
    """
    Get the object pronoun for a character (him, her, them, etc.)
    """
    try:
        sex = ch.sex.lower()
        if sex == "male":
            return "him"
        elif sex == "female":
            return "her"
        else:
            return "them"
    except:
        return "them"