'''
char_gen_enhancements.py

Comprehensive character appearance customization for Nesia races.
Drop this file into /lib/pymodules alongside char_gen.py
'''

import mudsys, mud

# ============================================================================
# RACE CONFIGURATION
# ============================================================================

# Mapping from culture/display names to actual stored race keys
CULTURE_TO_RACE = {
    "narakzir": "dwarf",
    "yerionde": "elf",
    "seren": "wolfkin",
    "valinayau": "gnome",
    "memti_halfgiant": "half-giant",
    "memti_halftroll": "half-troll",
    "kitabu": "foxkin",
    "qaluk": "ravenfolk",
    "hidians": "halfling",
    "sraj_es": "lizardfolk",
    "amarunk": "catfolk",
    "roshinver": "pixie",
    "hohap": "human",
    "yttribian": "human",
}

# Reverse mapping: actual race name back to config key
RACE_TO_CONFIG_KEY = {v: k for k, v in CULTURE_TO_RACE.items()}

# For races that are in RACES_CONFIG but not in CULTURE_TO_RACE (like hohap, yttribian)
RACE_TO_CONFIG_KEY.update({
    "dwarf": "narakzir",
    "elf": "yerionde",
    "gnome": "valinayau",
    "halfling": "hidians",
    "human": "yttribian",  # Default human to hohap, though hohap is also valid
    "pixie": "roshinver",
})


RACES_CONFIG = {
    "narakzir": {
        "display_name": "Narakzir",
        "description": "Dwarves - industrial and stoic masters of metallurgy",
        "starting_zone": "khazad@gtyr",
        "has_beard": True,
        "has_fur": False,
        "has_feathers": False,
        "has_scales": False,
        "has_tail": False,
        "has_wings": False,
        "has_mane": False,
    },
    "yerionde": {
        "display_name": "Yerionde",
        "description": "Elves - ancient, scholarly and magical",
        "starting_zone": "silverwood@gtyr",
        "has_beard": False,
        "has_fur": False,
        "has_feathers": False,
        "has_scales": False,
        "has_tail": False,
        "has_wings": False,
        "has_mane": False,
    },
    "seren": {
        "display_name": "Seren",
        "description": "Wolfkin - hardy and spiritual taiga dwellers",
        "starting_zone": "chechia@gtyr",
        "has_beard": False,
        "has_fur": True,
        "has_feathers": False,
        "has_scales": False,
        "has_tail": True,
        "has_wings": False,
        "has_mane": False,
    },
    "valinayau": {
        "display_name": "Valinayau",
        "description": "Gnomes - industrialized tinkerers",
        "starting_zone": "azeia@gtyr",
        "has_beard": True,
        "has_fur": False,
        "has_feathers": False,
        "has_scales": False,
        "has_tail": False,
        "has_wings": False,
        "has_mane": False,
    },
    "memti_halfgiant": {
        "display_name": "Memti (Half-Giant)",
        "description": "Half-Giantoids - laborers found everywhere",
        "starting_zone": "ika@gtyr",
        "has_beard": True,
        "has_fur": False,
        "has_feathers": False,
        "has_scales": False,
        "has_tail": False,
        "has_wings": False,
        "has_mane": False,
    },
    "memti_halftroll": {
        "display_name": "Memti (Half-Troll)",
        "description": "Half-Giantoids - laborers found everywhere",
        "starting_zone": "ika@gtyr",
        "has_beard": True,
        "has_fur": False,
        "has_feathers": False,
        "has_scales": False,
        "has_tail": False,
        "has_wings": False,
        "has_mane": False,
    },
    "kitabu": {
        "display_name": "Kitabu",
        "description": "Foxkin - island dwellers bound by honor and craft",
        "starting_zone": "kawa@gtyr",
        "has_beard": False,
        "has_fur": True,
        "has_feathers": False,
        "has_scales": False,
        "has_tail": True,
        "has_wings": False,
        "has_mane": False,
    },
    "qaluk": {
        "display_name": "Qaluk",
        "description": "Ravenfolk - arctic birdfolk adapted to flight",
        "starting_zone": "kuujjharbor@gtyr",
        "has_beard": False,
        "has_fur": False,
        "has_feathers": True,
        "has_scales": False,
        "has_tail": False,
        "has_wings": True,
        "has_mane": False,
    },
    "hidians": {
        "display_name": "Hidians",
        "description": "Halflings - peaceful agrarian craftspeople",
        "starting_zone": "fay@gtyr",
        "has_beard": True,
        "has_fur": False,
        "has_feathers": False,
        "has_scales": False,
        "has_tail": False,
        "has_wings": False,
        "has_mane": False,
    },
    "sraj_es": {
        "display_name": "Sraj'es",
        "description": "Lizardfolk - desert merchants and mercenaries",
        "starting_zone": "shazah@gtyr",
        "has_beard": False,
        "has_fur": False,
        "has_feathers": False,
        "has_scales": True,
        "has_tail": True,
        "has_wings": False,
        "has_mane": False,
    },
    "amarunk": {
        "display_name": "Amarunk",
        "description": "Catfolk - jungle and savanna dwellers",
        "starting_zone": "gawia@gtyr",
        "has_beard": False,
        "has_fur": True,
        "has_feathers": False,
        "has_scales": False,
        "has_tail": True,
        "has_wings": False,
        "has_mane": True,
    },
    "roshinver": {
        "display_name": "Roshinver",
        "description": "Pixies - reclusive but powerful mages",
        "starting_zone": "myth@gtyr",
        "has_beard": False,
        "has_fur": False,
        "has_feathers": False,
        "has_scales": False,
        "has_tail": False,
        "has_wings": True,
        "has_mane": False,
    },
    "hohap": {
        "display_name": "Hohap",
        "description": "Highland humans - Three Kingdoms era inspired",
        "starting_zone": "xinhui@gtyr",
        "has_beard": True,
        "has_fur": False,
        "has_feathers": False,
        "has_scales": False,
        "has_tail": False,
        "has_wings": False,
        "has_mane": False,
    },
    "yttribian": {
        "display_name": "Yttribian",
        "description": "Baseline humans - versatile and adaptable",
        "starting_zone": "grandaltar@gtyr",
        "has_beard": True,
        "has_fur": False,
        "has_feathers": False,
        "has_scales": False,
        "has_tail": False,
        "has_wings": False,
        "has_mane": False,
    },
}

# ============================================================================
# APPEARANCE TABLES
# ============================================================================

HAIR_COLORS = ["black", "dark brown", "brown", "light brown", "blonde", "white", "grey", "red", "auburn", "raven", "jet black", "silver", "copper"]
HAIR_STYLES = ["short", "shoulder-length", "long", "braided", "in a bun", "wild", "slicked back", "wavy", "curly", "straight", "tousled", "cropped"]
FUR_COLORS = ["black", "dark grey", "grey", "silver", "white", "cream", "tan", "brown", "dark brown", "red", "rust red", "golden", "amber", "white-tipped"]
FEATHER_COLORS = ["midnight blue", "deep blue", "dark blue", "steel blue", "slate blue", "blue-black", "black with blue sheen", "blue-grey", "charcoal"]
SKIN_TONES_GENERAL = ["pale", "fair", "light", "warm", "golden", "olive", "tan", "bronze", "copper", "brown", "dark brown", "ebony"]
SKIN_TONES_TROLL = ["pale green", "sage green", "olive green", "moss green", "greenish-brown", "brown-green", "khaki green", "murky green", "forest green", "swamp green"]
SCALE_COLORS = ["emerald green", "forest green", "jade", "olive", "khaki", "tan", "bronze", "gold", "copper", "rust", "blood red", "crimson", "dark purple", "slate grey"]
SCALE_MARKINGS = ["stripes", "bands", "spots", "blotches", "speckles", "rosettes", "diamonds", "reticulated pattern", "solid"]
MARKING_COLORS = ["black", "dark grey", "white", "cream", "gold", "copper", "red", "dark red"]
SEREN_TAIL_STYLES = ["full and fluffy", "sleek and tapered", "bushy with white tip", "ringed", "shaggy", "long and flowing"]
KITABU_TAIL_STYLES = ["full and brush-like", "sleek and pointed", "bushy with white tip", "ringed", "long and graceful", "plumed"]
AMARUNK_TAIL_STYLES = ["long and elegant", "ringed", "plumed", "tufted", "sleek and tapered", "thick and powerful", "crooked"]
SRAJ_ES_TAIL_STYLES = ["thick and muscular", "finned", "barbed", "smooth and tapered", "ridged", "whip-like"]
NARAKZIR_BEARD_STYLES = ["full and long", "short and neat", "elaborately braided", "forked", "with beads woven in", "natural and wild", "none"]
COMMON_BEARD_STYLES = ["full and thick", "neat and trimmed", "goatee", "stubble", "light scruff", "none"]
AMARUNK_MARKINGS = ["spots", "stripes", "rosettes", "none"]
WING_STYLES = ["dragonfly", "butterfly", "angellike", "batlike", "diaphanous", "birdlike"]
EYE_COLORS = ["black", "dark brown", "brown", "hazel", "amber", "grey", "blue", "green", "violet", "copper", "gold", "silver", "red (albino)"]

# ============================================================================
# INITIALIZE CHARACTER APPEARANCE TO DEFAULTS
# ============================================================================

# Add this new function to initialize all appearance fields to safe defaults
def initialize_appearance_defaults(ch):
    """Initialize all appearance fields to empty strings to prevent NULL pointers"""
    appearance_fields = [
        'hair_color', 'hair_style', 'fur_color', 'feather_color', 
        'scale_color', 'scale_marking', 'marking_color', 'tail_style',
        'mane_style', 'build', 'skin_tone', 'eye_color', 'eye_color_right',
        'beard_style'
    ]
    
    for field in appearance_fields:
        try:
            setattr(ch, field, "")
        except:
            pass  # Some fields might be read-only or not exist
    
    try:
        ch.heterochromia = 0
    except:
        pass

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_race_config(race_key):
    """Get configuration for a race by actual race name"""
    race_key = race_key.lower()
    
    # First try direct lookup (for config keys like "amarunk")
    if race_key in RACES_CONFIG:
        return RACES_CONFIG.get(race_key)
    
    # If not found, try reverse mapping (for actual race names like "catfolk")
    config_key = RACE_TO_CONFIG_KEY.get(race_key)
    if config_key:
        return RACES_CONFIG.get(config_key)
    
    # Special case for memti
    if race_key == "memti":
        return RACES_CONFIG.get("memti_halfgiant")
    
    return None

def apply_race_special_attributes(ch):
    """Apply special attributes based on race (like canfly)"""
    race_key = ch.race.lower()
    if race_key in ["qaluk", "roshinver"]:
        try:
            ch.addBit("canfly")
            mud.log_string("Applied canfly to %s" % ch.name)
        except Exception as e:
            mud.log_string("ERROR: Failed to apply canfly to %s: %s" % (ch.name, str(e)))

# ============================================================================
# RACE HANDLER
# ============================================================================

def cg_show_races(sock):
    """Display all playable races"""
    sock.send("{c" + "="*70)
    sock.send("RACE SELECTION")
    sock.send("="*70 + "{n")
    sock.send("\nAvailable races:\n")
    
    # Track which base races we've already shown (to avoid duplicates)
    shown = set()
    for race_key in sorted(RACES_CONFIG.keys()):
        base_race = race_key.split("_")[0]
        
        # Skip if we've already shown this base race
        if base_race in shown:
            continue
        
        config = RACES_CONFIG[race_key]
        sock.send("  {c%-20s{n - %s\n" % (config["display_name"], config["description"]))
        shown.add(base_race)
    
    sock.send("\n{y[H]{n for detailed help on a race")
    sock.send("{c" + "="*70 + "{n\n")

def cg_enhanced_race_handler(sock, arg):
    """Handle race selection"""
    arg_lower = arg.strip().lower()
    
    if arg_lower in ['h', 'help']:
        cg_show_races(sock)
        sock.send_raw("Choose a race (or enter [H]elp <race> for details): ")
        return
    
    # Try to match the input to a race
    race_found = None
    
    # First try exact match with display names
    for race_key, config in RACES_CONFIG.items():
        if config["display_name"].lower() == arg_lower:
            race_found = race_key
            break
    
    # If no exact match, try partial match with keys or display names
    if not race_found:
        for race_key, config in RACES_CONFIG.items():
            if race_key.startswith(arg_lower) or config["display_name"].lower().startswith(arg_lower):
                race_found = race_key
                break
    
    # Handle special case: "memti" can match either half-giant or half-troll, default to half-giant
    if arg_lower == "memti" and not race_found:
        race_found = "memti_halfgiant"
    
    if not race_found:
        sock.send("{cInvalid race selection, try again.{n\r\n")
        cg_show_races(sock)
        sock.send_raw("Choose a race (or enter [H]elp <race> for details): ")
        return
    
    sock.ch.race = race_found
    sock.pop_ih()

def cg_appearance_entry_prompt(sock):
    """Prompt for race selection - called first time"""
    cg_show_races(sock)
    sock.send_raw("Choose a race (or enter [H]elp <race> for details): ")

def cg_memti_variant_handler(sock, arg):
    """Handle Memti half-giant vs half-troll selection"""
    choice = arg.strip().lower()
    
    if choice in ['1', 'g', 'giant']:
        actual_race = CULTURE_TO_RACE.get("memti_halfgiant", "half-giant")
        sock.ch.race = actual_race
        # Initialize all appearance fields to empty strings
        initialize_appearance_defaults(sock.ch)
        sock.pop_ih()
        # Push eye color handlers to continue appearance customization
        sock.push_ih(cg_heterochromia_handler, cg_heterochromia_prompt)
        sock.push_ih(cg_eye_color_handler, cg_eye_color_prompt)
        return
    elif choice in ['2', 't', 'troll']:
        actual_race = CULTURE_TO_RACE.get("memti_halftroll", "half-troll")
        sock.ch.race = actual_race
        # Initialize all appearance fields to empty strings
        initialize_appearance_defaults(sock.ch)
        sock.pop_ih()
        # Push eye color handlers to continue appearance customization
        sock.push_ih(cg_heterochromia_handler, cg_heterochromia_prompt)
        sock.push_ih(cg_eye_color_handler, cg_eye_color_prompt)
        return
    else:
        sock.send("{cPlease select 1 for half-giant or 2 for half-troll.{n\r\n")
        return

def cg_memti_variant_prompt(sock):
    """Prompt for Memti variant selection"""
    sock.send("\n{c" + "="*70 + "{n")
    sock.send("MEMTI VARIANT SELECTION")
    sock.send("="*70 + "{n\n")
    sock.send("The Memti people come in two variants:\n\n")
    sock.send("{c[1]{n Half-Giant  - Larger, stronger, more ponderous\n")
    sock.send("{c[2]{n Half-Troll  - Regenerative, more aggressive\n\n")
    sock.send("{c" + "="*70 + "{n\r\n")
    sock.send_raw("Select Memti variant (1 or 2): ")


# ============================================================================
# SKIN/FUR/FEATHER/SCALE HANDLERS
# ============================================================================

def cg_skin_tone_handler(sock, arg):
    try:
        choice = int(arg)
        table = SKIN_TONES_TROLL if sock.ch.race == "memti_halftroll" else SKIN_TONES_GENERAL
        if 1 <= choice <= len(table):
            sock.ch.skin_tone = table[choice - 1]
            sock.pop_ih()
            return
    except ValueError:
        pass
    sock.send("{cInvalid selection, try again.{n\r\n")

def cg_skin_tone_prompt(sock):
    table = SKIN_TONES_TROLL if sock.ch.race == "memti_halftroll" else SKIN_TONES_GENERAL
    title = "SKIN TONE SELECTION (Half-Troll)" if sock.ch.race == "memti_halftroll" else "SKIN TONE SELECTION"
    sock.send("\n")
    sock.send("{c" + "="*70)
    sock.send(title)
    sock.send("="*70 + "{n\n")
    for i, tone in enumerate(table, 1):
        sock.send("{c[%d]{n %-20s" % (i, tone))
        if i % 3 == 0: sock.send("")
    if len(table) % 3 != 0: sock.send("")
    sock.send("\n{c" + "="*70 + "{n\r\n")
    sock.send_raw("Select skin tone (1-%d): " % len(table))


def cg_skin_tone_handler_troll(sock, arg):
    """Skin tone handler specifically for half-trolls"""
    try:
        choice = int(arg)
        if 1 <= choice <= len(SKIN_TONES_TROLL):
            sock.ch.skin_tone = SKIN_TONES_TROLL[choice - 1]
            sock.pop_ih()
            return
    except ValueError:
        pass
    sock.send("{cInvalid selection, try again.{n\r\n")


def cg_skin_tone_prompt_troll(sock):
    """Skin tone prompt specifically for half-trolls"""
    sock.send("\n")
    sock.send("{c" + "="*70)
    sock.send("SKIN TONE SELECTION (Half-Troll)")
    sock.send("="*70 + "{n\n")
    for i, tone in enumerate(SKIN_TONES_TROLL, 1):
        sock.send("{c[%d]{n %-20s" % (i, tone))
        if i % 3 == 0: sock.send("")
    if len(SKIN_TONES_TROLL) % 3 != 0: sock.send("")
    sock.send("\n{c" + "="*70 + "{n\r\n")
    sock.send_raw("Select skin tone (1-%d): " % len(SKIN_TONES_TROLL))

def cg_fur_color_handler(sock, arg):
    try:
        choice = int(arg)
        if 1 <= choice <= len(FUR_COLORS):
            sock.ch.fur_color = FUR_COLORS[choice - 1]
            sock.pop_ih()
            return
    except ValueError:
        pass
    sock.send("{cInvalid selection, try again.{n\r\n")

def cg_fur_color_prompt(sock):
    sock.send("\n{c" + "="*70 + "{n")
    sock.send("FUR COLOR SELECTION")
    sock.send("="*70 + "{n\n")
    for i, color in enumerate(FUR_COLORS, 1):
        sock.send("{c[%d]{n %-20s" % (i, color))
        if i % 3 == 0: sock.send("")
    if len(FUR_COLORS) % 3 != 0: sock.send("")
    sock.send("\n{c" + "="*70 + "{n\r\n")
    sock.send_raw("Select fur color (1-%d): " % len(FUR_COLORS))

def cg_feather_color_handler(sock, arg):
    try:
        choice = int(arg)
        if 1 <= choice <= len(FEATHER_COLORS):
            sock.ch.feather_color = FEATHER_COLORS[choice - 1]
            sock.pop_ih()
            return
    except ValueError:
        pass
    sock.send("{cInvalid selection, try again.{n\r\n")

def cg_feather_color_prompt(sock):
    sock.send("\n{c" + "="*70 + "{n")
    sock.send("FEATHER COLOR SELECTION")
    sock.send("="*70 + "{n\n")
    for i, color in enumerate(FEATHER_COLORS, 1):
        sock.send("{c[%d]{n %-20s" % (i, color))
        if i % 3 == 0: sock.send("")
    if len(FEATHER_COLORS) % 3 != 0: sock.send("")
    sock.send("\n{c" + "="*70 + "{n\r\n")
    sock.send_raw("Select feather color (1-%d): " % len(FEATHER_COLORS))

def cg_scale_color_handler(sock, arg):
    try:
        choice = int(arg)
        if 1 <= choice <= len(SCALE_COLORS):
            sock.ch.scale_color = SCALE_COLORS[choice - 1]
            sock.pop_ih()
            return
    except ValueError:
        pass
    sock.send("{cInvalid selection, try again.{n\r\n")

def cg_scale_color_prompt(sock):
    sock.send("\n{c" + "="*70 + "{n")
    sock.send("SCALE COLOR SELECTION")
    sock.send("="*70 + "{n\n")
    for i, color in enumerate(SCALE_COLORS, 1):
        sock.send("{c[%d]{n %-20s" % (i, color))
        if i % 3 == 0: sock.send("")
    if len(SCALE_COLORS) % 3 != 0: sock.send("")
    sock.send("\n{c" + "="*70 + "{n\r\n")
    sock.send_raw("Select scale color (1-%d): " % len(SCALE_COLORS))

def cg_scale_marking_handler(sock, arg):
    try:
        choice = int(arg)
        if 1 <= choice <= len(SCALE_MARKINGS):
            sock.ch.scale_marking = SCALE_MARKINGS[choice - 1]
            sock.pop_ih()
            return
    except ValueError:
        pass
    sock.send("{cInvalid selection, try again.{n\r\n")

def cg_scale_marking_prompt(sock):
    sock.send("\n{c" + "="*70 + "{n")
    sock.send("SCALE MARKING SELECTION")
    sock.send("="*70 + "{n\n")
    for i, marking in enumerate(SCALE_MARKINGS, 1):
        sock.send("{c[%d]{n %-20s" % (i, marking))
        if i % 3 == 0: sock.send("")
    if len(SCALE_MARKINGS) % 3 != 0: sock.send("")
    sock.send("\n{c" + "="*70 + "{n\r\n")
    sock.send_raw("Select marking type (1-%d): " % len(SCALE_MARKINGS))

def cg_marking_color_handler(sock, arg):
    try:
        choice = int(arg)
        if 1 <= choice <= len(MARKING_COLORS):
            sock.ch.marking_color = MARKING_COLORS[choice - 1]
            sock.pop_ih()
            return
    except ValueError:
        pass
    sock.send("{cInvalid selection, try again.{n\r\n")

def cg_marking_color_prompt(sock):
    sock.send("\n{c" + "="*70 + "{n")
    sock.send("MARKING COLOR SELECTION")
    sock.send("="*70 + "{n\n")
    for i, color in enumerate(MARKING_COLORS, 1):
        sock.send("{c[%d]{n %-20s" % (i, color))
        if i % 4 == 0: sock.send("")
    if len(MARKING_COLORS) % 4 != 0: sock.send("")
    sock.send("\n{c" + "="*70 + "{n\r\n")
    sock.send_raw("Select marking color (1-%d): " % len(MARKING_COLORS))

# ============================================================================
# NEW HANDLERS FOR AMARUNK MARKINGS
# ============================================================================

def cg_amarunk_marking_handler(sock, arg):
    try:
        choice = int(arg)
        if 1 <= choice <= len(AMARUNK_MARKINGS):
            sock.ch.scale_marking = AMARUNK_MARKINGS[choice - 1]
            sock.pop_ih()
            return
    except ValueError:
        pass
    sock.send("{cInvalid selection, try again.{n\r\n")

def cg_amarunk_marking_prompt(sock):
    sock.send("\n{c" + "="*70 + "{n")
    sock.send("FUR MARKING PATTERN SELECTION")
    sock.send("="*70 + "{n\n")
    for i, marking in enumerate(AMARUNK_MARKINGS, 1):
        sock.send("{c[%d]{n %-20s" % (i, marking))
        if i % 3 == 0: sock.send("")
    if len(AMARUNK_MARKINGS) % 3 != 0: sock.send("")
    sock.send("\n{c" + "="*70 + "{n\r\n")
    sock.send_raw("Select fur marking (1-%d): " % len(AMARUNK_MARKINGS))

# ============================================================================
# NEW HANDLERS FOR ROSHINVER WINGS
# ============================================================================

def cg_wing_style_handler(sock, arg):
    try:
        choice = int(arg)
        if 1 <= choice <= len(WING_STYLES):
            sock.ch.tail_style = WING_STYLES[choice - 1]  # Repurpose tail_style for wings
            sock.pop_ih()
            return
    except ValueError:
        pass
    sock.send("{cInvalid selection, try again.{n\r\n")

def cg_wing_style_prompt(sock):
    sock.send("\n{c" + "="*70 + "{n")
    sock.send("WING STYLE SELECTION")
    sock.send("="*70 + "{n\n")
    for i, style in enumerate(WING_STYLES, 1):
        sock.send("{c[%d]{n %-20s" % (i, style))
        if i % 2 == 0: sock.send("")
    if len(WING_STYLES) % 2 != 0: sock.send("")
    sock.send("\n{c" + "="*70 + "{n\r\n")
    sock.send_raw("Select wing style (1-%d): " % len(WING_STYLES))

# ============================================================================
# TAIL HANDLERS
# ============================================================================

def cg_tail_style_handler(sock, arg):
    race_key = sock.ch.race.lower()
    
    # Get the config key for this race
    config_key = RACE_TO_CONFIG_KEY.get(race_key)
    
    mud.log_string("DEBUG: cg_tail_style_handler - race_key=%s, config_key=%s" % (race_key, config_key))
    
    # Map config key to tail styles
    if config_key == "amarunk":
        table = AMARUNK_TAIL_STYLES
        title = "CAT TAIL STYLE SELECTION"
    elif config_key == "seren":
        table = SEREN_TAIL_STYLES
        title = "WOLF TAIL STYLE SELECTION"
    elif config_key == "kitabu":
        table = KITABU_TAIL_STYLES
        title = "FOX TAIL STYLE SELECTION"
    elif config_key == "sraj_es":
        table = SRAJ_ES_TAIL_STYLES
        title = "LIZARD TAIL STYLE SELECTION"
    else:
        mud.log_string("DEBUG: No tail styles for race: %s" % race_key)
        sock.pop_ih()
        return
    
    try:
        choice = int(arg)
        if 1 <= choice <= len(table):
            sock.ch.tail_style = table[choice - 1]
            sock.pop_ih()
            return
    except ValueError:
        pass
    sock.send("{cInvalid selection, try again.{n\r\n")

def cg_tail_style_prompt(sock):
    race_key = sock.ch.race.lower()
    
    # Get the config key for this race
    config_key = RACE_TO_CONFIG_KEY.get(race_key)
    
    if config_key == "amarunk":
        table, title = AMARUNK_TAIL_STYLES, "CAT TAIL STYLE SELECTION"
    elif config_key == "seren":
        table, title = SEREN_TAIL_STYLES, "WOLF TAIL STYLE SELECTION"
    elif config_key == "kitabu":
        table, title = KITABU_TAIL_STYLES, "FOX TAIL STYLE SELECTION"
    elif config_key == "sraj_es":
        table, title = SRAJ_ES_TAIL_STYLES, "LIZARD TAIL STYLE SELECTION"
    else:
        return
    
    sock.send("\n{c" + "="*70 + "{n")
    sock.send(title)
    sock.send("="*70 + "{n\n")
    for i, style in enumerate(table, 1):
        sock.send("{c[%d]{n %-25s" % (i, style))
        if i % 2 == 0: sock.send("")
    if len(table) % 2 != 0: sock.send("")
    sock.send("\n{c" + "="*70 + "{n\r\n")
    sock.send_raw("Select tail style (1-%d): " % len(table))

# ============================================================================
# HAIR HANDLERS
# ============================================================================

def cg_hair_color_handler(sock, arg):
    try:
        choice = int(arg)
        if 1 <= choice <= len(HAIR_COLORS):
            sock.ch.hair_color = HAIR_COLORS[choice - 1]
            sock.pop_ih()
            return
    except ValueError:
        pass
    sock.send("{cInvalid selection, try again.{n\r\n")

def cg_hair_color_prompt(sock):
    sock.send("\n")
    sock.send("{c" + "="*70)
    sock.send("HAIR COLOR SELECTION")
    sock.send("="*70 + "{n\n")
    for i, color in enumerate(HAIR_COLORS, 1):
        sock.send("{c[%d]{n %-15s" % (i, color))
        if i % 4 == 0:
            sock.send("")
    if len(HAIR_COLORS) % 4 != 0:
        sock.send("")
    sock.send("\n")
    sock.send("{c" + "="*70 + "{n\r\n")
    sock.send_raw("Select hair color (1-%d): " % len(HAIR_COLORS))

def cg_hair_style_handler(sock, arg):
    try:
        choice = int(arg)
        if 1 <= choice <= len(HAIR_STYLES):
            sock.ch.hair_style = HAIR_STYLES[choice - 1]
            sock.pop_ih()
            return
    except ValueError:
        pass
    sock.send("{cInvalid selection, try again.{n\r\n")

def cg_hair_style_prompt(sock):
    sock.send("\n{c" + "="*70 + "\nHAIR STYLE SELECTION\n" + "="*70 + "{n\n")
    for i, style in enumerate(HAIR_STYLES, 1):
        sock.send("{c[%d]{n %-20s" % (i, style))
        if i % 3 == 0:
            sock.send("")
    if len(HAIR_STYLES) % 3 != 0:
        sock.send("")
    sock.send("\n{c" + "="*70 + "{n\r\n")
    sock.send_raw("Select hair style (1-%d): " % len(HAIR_STYLES))

def cg_mane_style_handler(sock, arg):
    try:
        choice = int(arg)
        if 1 <= choice <= len(HAIR_STYLES):
            sock.ch.mane_style = HAIR_STYLES[choice - 1]
            sock.pop_ih()
            return
    except ValueError:
        pass
    sock.send("{cInvalid selection, try again.{n\r\n")

def cg_mane_style_prompt(sock):
    sock.send("\n{c" + "="*70 + "\nMANE STYLE SELECTION\n" + "="*70 + "{n\n")
    sock.send("Choose how you style your feline mane:\n\n")
    for i, style in enumerate(HAIR_STYLES, 1):
        sock.send("{c[%d]{n %-20s" % (i, style))
        if i % 3 == 0: sock.send("")
    if len(HAIR_STYLES) % 3 != 0: sock.send("")
    sock.send("\n{c" + "="*70 + "{n\r\n")
    sock.send_raw("Select mane style (1-%d): " % len(HAIR_STYLES))

# ============================================================================
# EYE COLOR HANDLERS
# ============================================================================

def cg_eye_color_handler(sock, arg):
    try:
        choice = int(arg)
        if 1 <= choice <= len(EYE_COLORS):
            sock.ch.eye_color = EYE_COLORS[choice - 1]
            sock.pop_ih()
            return
    except ValueError:
        pass
    sock.send("{cInvalid selection, try again.{n\r\n")

def cg_eye_color_prompt(sock):
    sock.send("\n{c" + "="*70 + "\nEYE COLOR SELECTION\n" + "="*70 + "{n\n")
    for i, color in enumerate(EYE_COLORS, 1):
        sock.send("{c[%d]{n %-20s" % (i, color))
        if i % 3 == 0: sock.send("")
    if len(EYE_COLORS) % 3 != 0: sock.send("")
    sock.send("\n{c" + "="*70 + "{n\r\n")
    sock.send_raw("Select eye color (1-%d): " % len(EYE_COLORS))

def cg_heterochromia_handler(sock, arg):
    choice = arg.strip().lower()
    
    if choice in ['y', 'yes']:
        sock.ch.heterochromia = 1
        sock.pop_ih()
        # Push second eye color, which will push remaining handlers after it completes
        sock.push_ih(cg_second_eye_color_handler, cg_second_eye_color_prompt)
        return
    elif choice in ['n', 'no']:
        sock.ch.heterochromia = 0
        sock.pop_ih()
        # Push remaining handlers using the helper
        push_remaining_appearance_handlers(sock)
        return
    else:
        sock.send("{cPlease answer yes or no.{n\r\n")

def cg_heterochromia_prompt(sock):
    sock.send("\n{c" + "="*70 + "\nHETEROCHROMIA - ODD EYES\n" + "="*70 + "{n\n")
    sock.send_raw("Do you want different colored eyes? (Y/N): ")

def cg_second_eye_color_handler(sock, arg):
    try:
        choice = int(arg)
        if 1 <= choice <= len(EYE_COLORS):
            sock.ch.eye_color_right = EYE_COLORS[choice - 1]
            sock.pop_ih()
            # Push remaining handlers using the helper
            push_remaining_appearance_handlers(sock)
            return
    except ValueError:
        pass
    sock.send("{cInvalid selection, try again.{n\r\n")

def cg_second_eye_color_prompt(sock):
    sock.send("\n{c" + "="*70 + "{n")
    sock.send("SECOND EYE COLOR (Right Eye)")
    sock.send("="*70 + "{n\n")
    sock.send("Your left eye: %s\n\n" % sock.ch.eye_color)
    for i, color in enumerate(EYE_COLORS, 1):
        sock.send("{c[%d]{n %-20s" % (i, color))
        if i % 3 == 0: sock.send("")
    if len(EYE_COLORS) % 3 != 0: sock.send("")
    sock.send("\n{c" + "="*70 + "{n\r\n")
    sock.send_raw("Select right eye color (1-%d): " % len(EYE_COLORS))

# ============================================================================
# BEARD HANDLERS
# ============================================================================

def cg_beard_style_handler(sock, arg):
    race_key = sock.ch.race.lower()
    sex = sock.ch.sex.lower()
    
    if race_key == "narakzir":
        table = NARAKZIR_BEARD_STYLES
    elif race_key in ["hidians", "valinayau", "memti_halfgiant", "memti_halftroll", "hohap", "yttribian"]:
        table = COMMON_BEARD_STYLES
    else:
        sock.pop_ih()
        return
    
    if sex == "female" and race_key != "narakzir":
        sock.pop_ih()
        return
    
    try:
        choice = int(arg)
        if 1 <= choice <= len(table):
            sock.ch.beard_style = table[choice - 1]
            sock.pop_ih()
            return
    except ValueError:
        pass
    sock.send("{cInvalid selection, try again.{n\r\n")

def cg_beard_style_prompt(sock):
    race_key = sock.ch.race.lower()
    if race_key == "narakzir":
        table, title = NARAKZIR_BEARD_STYLES, "DWARVEN BEARD STYLE SELECTION"
    elif race_key in ["hidians", "valinayau", "memti_halfgiant", "memti_halftroll", "hohap", "yttribian"]:
        table, title = COMMON_BEARD_STYLES, "BEARD STYLE SELECTION"
    else:
        sock.pop_ih()
        return
    
    sock.send("\n{c" + "="*70 + "\n" + title + "\n" + "="*70 + "{n\n")
    for i, style in enumerate(table, 1):
        sock.send("{c[%d]{n %-20s" % (i, style))
        if i % 3 == 0: sock.send("")
    if len(table) % 3 != 0: sock.send("")
    sock.send("\n{c" + "="*70 + "{n\r\n")
    sock.send_raw("Select beard style (1-%d): " % len(table))

# ============================================================================
# CHARACTER REVIEW
# ============================================================================

def cg_review_appearance(ch):
    """Generate appearance summary"""
    race_config = get_race_config(ch.race)
    display_race = race_config["display_name"] if race_config else ch.race
    
    summary = "\n{G*** Character Customization Complete! ***{n\n"
    summary += "  {CRace:{n       %s\n" % display_race
    summary += "  {CSex:{n        %s\n" % ch.sex.capitalize()
    
    if race_config:
        if race_config["has_fur"]:
            summary += "  {CFur Color:{n  %s\n" % getattr(ch, 'fur_color', 'Not set')
        elif not race_config["has_feathers"] and not race_config["has_scales"]:
            summary += "  {CSkin Tone:{n  %s\n" % getattr(ch, 'skin_tone', 'Not set')
        
        if race_config["has_feathers"]:
            summary += "  {CFeathers:{n   %s\n" % getattr(ch, 'feather_color', 'Not set')
        
        if race_config["has_scales"]:
            summary += "  {CScales:{n     %s %s\n" % (getattr(ch, 'scale_marking', 'Not set'), getattr(ch, 'scale_color', 'Not set'))
            summary += "  {CMarkings:{n   %s\n" % getattr(ch, 'marking_color', 'Not set')
        
        if race_config["has_beard"]:
            summary += "  {CBeard:{n      %s\n" % getattr(ch, 'beard_style', 'Not set')
        elif ch.sex in ["male", "non-binary", "other"]:
            summary += "  {CBeard:{n      %s\n" % getattr(ch, 'beard_style', 'None')
    
    summary += "  {CHair Color:{n %s\n" % getattr(ch, 'hair_color', 'Not set')
    summary += "  {CHair Style:{n %s\n" % getattr(ch, 'hair_style', 'Not set')
    
    if race_config and race_config["has_mane"]:
        summary += "  {CMane Style:{n %s\n" % getattr(ch, 'mane_style', 'Not set')
    
    if race_config and race_config["has_tail"]:
        summary += "  {CTail Style:{n %s\n" % getattr(ch, 'tail_style', 'Not set')
    
    summary += "  {CEye Color:{n  %s" % getattr(ch, 'eye_color', 'Not set')
    if getattr(ch, 'heterochromia', False):
        summary += " (Left), %s (Right)" % getattr(ch, 'eye_color_right', 'Not set')
    summary += "\n"
    
    summary += "{c" + "="*70 + "{n\n"
    return summary

def cg_final_review_handler(sock, arg):
    """Handle final review - now requires yes/no confirmation"""
    choice = arg.strip().lower()
    
    if choice in ['y', 'yes']:
        sock.pop_ih()
        # Character confirmed, finalize them
        return
    elif choice in ['n', 'no']:
        sock.send("\n{cCancelling appearance customization...{n\n")
        sock.send("Starting over with race selection.\n\n")
        # Pop ALL handlers to get back to race selection
        sock.pop_ih()  # Pop the final review handler
        # Push race selection back
        sock.push_ih(cg_appearance_entry_handler, cg_appearance_entry_prompt)
        return
    else:
        sock.send("{cPlease answer yes or no.{n\r\n")

def cg_final_review_prompt(sock):
    """Show final review with confirmation"""
    sock.send(cg_review_appearance(sock.ch))
    sock.send_raw("Accept this appearance? (Y/N): ")


# ============================================================================
# MAIN APPEARANCE ENTRY HANDLER
# ============================================================================

def push_remaining_appearance_handlers(sock):
    """Push all remaining appearance handlers after eye colors"""
    race_config = get_race_config(sock.ch.race)
    race_key = sock.ch.race.lower()
    config_key = RACE_TO_CONFIG_KEY.get(race_key)
    
    mud.log_string("DEBUG: push_remaining_appearance_handlers called for race: %s" % sock.ch.race)
    mud.log_string("DEBUG: race_config = %s" % str(race_config))
    mud.log_string("DEBUG: config_key = %s" % config_key)
    
    # Push in REVERSE order of execution
    sock.push_ih(cg_final_review_handler, cg_final_review_prompt)
    
    if race_config and (race_config["has_beard"] or sock.ch.sex in ["male", "non-binary", "other"]):
        mud.log_string("DEBUG: Pushing beard handler")
        sock.push_ih(cg_beard_style_handler, cg_beard_style_prompt)
    
    if race_config and race_config["has_mane"]:
        mud.log_string("DEBUG: Pushing mane handler")
        sock.push_ih(cg_mane_style_handler, cg_mane_style_prompt)
    
    sock.push_ih(cg_hair_style_handler, cg_hair_style_prompt)
    sock.push_ih(cg_hair_color_handler, cg_hair_color_prompt)
    
    # Special handling for wings (Roshinver)
    if config_key == "roshinver":
        mud.log_string("DEBUG: Pushing wing style handler for Roshinver")
        sock.push_ih(cg_wing_style_handler, cg_wing_style_prompt)
    elif race_config and race_config["has_tail"]:
        mud.log_string("DEBUG: Pushing tail handler")
        sock.push_ih(cg_tail_style_handler, cg_tail_style_prompt)
    
    # Special handling for Amarunk markings
    if config_key == "amarunk":
        mud.log_string("DEBUG: Pushing Amarunk marking handler")
        sock.push_ih(cg_amarunk_marking_handler, cg_amarunk_marking_prompt)
    elif race_config and race_config["has_scales"]:
        mud.log_string("DEBUG: Pushing scale handlers")
        sock.push_ih(cg_marking_color_handler, cg_marking_color_prompt)
        sock.push_ih(cg_scale_marking_handler, cg_scale_marking_prompt)
        sock.push_ih(cg_scale_color_handler, cg_scale_color_prompt)
    
    if race_config and race_config["has_feathers"]:
        mud.log_string("DEBUG: Pushing feather handler")
        sock.push_ih(cg_feather_color_handler, cg_feather_color_prompt)
    
    if race_config:
        if race_config["has_fur"]:
            mud.log_string("DEBUG: Pushing fur handler")
            sock.push_ih(cg_fur_color_handler, cg_fur_color_prompt)
        elif not race_config["has_feathers"] and not race_config["has_scales"]:
            mud.log_string("DEBUG: Pushing skin tone handler")
            sock.push_ih(cg_skin_tone_handler, cg_skin_tone_prompt)


def cg_appearance_entry_handler(sock, arg):
    """
    Entry point for appearance customization.
    """
    arg_lower = arg.strip().lower()
    
    mud.log_string("DEBUG: Race selection input: '%s'" % arg_lower)
    
    # Help option
    if arg_lower in ['h', 'help']:
        cg_show_races(sock)
        sock.send_raw("Choose a race (or enter [H]elp <race> for details): ")
        return
    
    # Special handling for Memti - show variant menu
    if arg_lower == "memti":
        sock.pop_ih()
        sock.push_ih(cg_memti_variant_handler, cg_memti_variant_prompt)
        return
    
    # Try to match the input to a race
    race_found = None
    
    for race_key, config in RACES_CONFIG.items():
        display_name_lower = config["display_name"].lower()
        race_key_base = race_key.split("_")[0].lower()
        
        # Exact match on display name (handles sraj'es)
        if display_name_lower == arg_lower:
            race_found = race_key
            break
        # Exact match on race key base
        if race_key_base == arg_lower:
            race_found = race_key
            break
        # Partial match on display name
        if display_name_lower.startswith(arg_lower):
            race_found = race_key
            break
        # Special handling: "sraj" or "sraj es" or "sraj'es" should all match sraj_es
        if race_key == "sraj_es":
            clean_input = arg_lower.replace("'", "").replace(" ", "")
            clean_display = display_name_lower.replace("'", "").replace(" ", "")
            if clean_display == clean_input or clean_display.startswith(clean_input):
                race_found = race_key
                break
    
    if not race_found:
        sock.send("{cInvalid race selection, try again.{n\r\n")
        cg_show_races(sock)
        sock.send_raw("Choose a race (or enter [H]elp <race> for details): ")
        return
    
    base_race = race_found.split("_")[0]
    actual_race = CULTURE_TO_RACE.get(base_race, base_race)
    
    if not mud.is_race(actual_race, True):
        sock.send("{cThat race is not available.{n\r\n")
        cg_show_races(sock)
        sock.send_raw("Choose a race (or enter [H]elp <race> for details): ")
        return
    
    try:
        sock.ch.race = actual_race
        # Initialize all appearance fields to empty strings
        initialize_appearance_defaults(sock.ch)
    except Exception as e:
        sock.send("{cError setting race. Please try again.{n\r\n")
        cg_show_races(sock)
        sock.send_raw("Choose a race (or enter [H]elp <race> for details): ")
        return
    
    sock.pop_ih()
    
    mud.log_string("DEBUG: Building appearance stack for race: %s" % sock.ch.race)
    
    # Just start with eye colors
    sock.push_ih(cg_heterochromia_handler, cg_heterochromia_prompt)
    sock.push_ih(cg_eye_color_handler, cg_eye_color_prompt)
    
    mud.log_string("DEBUG: Appearance stack built successfully")