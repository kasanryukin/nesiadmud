"""
Progression: Integration Module
================================
Main API for character progression setup and lifecycle management.
Coordinates skills, experience pools, and leveling systems.
"""

import mud
import time
import hooks
from . import skills as progression_skills
from . import experience as progression_experience
from . import leveling as progression_leveling
from . import yaml_parser

# Configuration
OFFLINE_DRAIN_DELAY = 8 * 60 * 60  # 8 hours before offline drain starts


def setup_progression(ch, class_config):
    """
    Initialize all progression systems for a character.
    
    Call this during character creation after choosing a class.
    Sets up skills, experience pools, and leveling based on class config.
    
    Args:
        ch: Character to initialize
        class_config: Loaded class YAML config (dict) with:
            - class_name: "Warrior"
            - skills: {primary: [...], secondary: [...], ...}
            - levels: {1: {...}, 25: {...}, ...}
    
    Returns:
        bool: True if successful
    """
    if not class_config:
        mud.log_string("ERROR: setup_progression called without class_config")
        return False
    
    mud.log_string("PROGRESSION: Initializing progression for %s (class: %s)" % 
                  (ch.name, class_config.get('class_name', 'Unknown')))
    
    try:
        # 1. Setup experience pools (universal)
        progression_experience.setup_experience(ch)
        
        # 2. Setup skills with class placement
        progression_skills.setup_skills_from_class_config(ch, class_config)
        
        # 3. Setup leveling with class requirements
        progression_leveling.setup_leveling_from_class_config(ch, class_config)
        
        mud.log_string("PROGRESSION: Setup complete for %s" % ch.name)
        return True
        
    except Exception as e:
        mud.log_string("ERROR: Failed to setup progression for %s: %s" % (ch.name, str(e)))
        import traceback
        mud.log_string(traceback.format_exc())
        return False


def on_character_login(ch):
    """
    Called when character logs in.
    Handles offline experience drain calculation.
    
    Args:
        ch: Character logging in
    """
    try:
        exp_manager = progression_experience.get_experience_manager(ch)
        if exp_manager:
            exp_manager.on_login()
    except Exception as e:
        mud.log_string("ERROR: on_character_login failed for %s: %s" % (ch.name, str(e)))


def on_character_logout(ch):
    """
    Called when character logs out.
    Records logout time for offline drain calculation.
    
    Args:
        ch: Character logging out
    """
    try:
        exp_manager = progression_experience.get_experience_manager(ch)
        if exp_manager:
            exp_manager.on_logout()
    except Exception as e:
        mud.log_string("ERROR: on_character_logout failed for %s: %s" % (ch.name, str(e)))


def on_heartbeat(ch):
    """
    Called every heartbeat (typically 1-5 seconds).
    Checks if skill groups should pulse and converts field exp to ranks.
    
    Args:
        ch: Character to pulse
    """
    try:
        exp_manager = progression_experience.get_experience_manager(ch)
        if exp_manager:
            exp_manager.check_pulse_all_groups()
    except Exception as e:
        mud.log_string("ERROR: on_heartbeat failed for %s: %s" % (ch.name, str(e)))


def on_skill_rank_gained(ch, skill_name, old_rank, new_rank):
    """
    Called when a skill gains a rank (from pulse or other source).
    Handles TDP granting and level-up checks.
    
    Args:
        ch: Character
        skill_name: Name of skill that ranked up
        old_rank: Previous rank
        new_rank: New rank
    """
    try:
        from . import tdp as progression_tdp
        
        # Grant TDP for skill rank advancement
        tdp_gained = progression_tdp.grant_tdp_for_skill_rank(ch, old_rank, new_rank)
        
        if tdp_gained > 0:
            ch.send("{g*** You gained %d TDP from ranking up in %s! ***{n" % (tdp_gained, skill_name))
        
        # Check if this triggers a level up
        progression_leveling.check_level_up(ch)
        
        mud.log_string("SKILL_UP: %s's %s ranked up (%.2f -> %.2f, +%d TDP)" % 
                      (ch.name, skill_name, old_rank, new_rank, tdp_gained))
    
    except Exception as e:
        mud.log_string("ERROR: on_skill_rank_gained failed for %s: %s" % (ch.name, str(e)))


def init_progression():
    """
    Called once at MUD startup to initialize progression systems.
    Loads YAML configs and prepares registries.
    """
    mud.log_string("PROGRESSION: Initializing progression module...")
    
    try:
        # Load skill registry from config
        skill_registry = progression_skills.get_skill_registry()
        if not skill_registry.skills:
            mud.log_string("WARNING: No skills loaded. Check config/skills.yaml")
        else:
            mud.log_string("PROGRESSION: Loaded %d skills" % len(skill_registry.skills))
        
        mud.log_string("PROGRESSION: Module initialization complete")
        return True
    
    except Exception as e:
        mud.log_string("ERROR: Failed to initialize progression module: %s" % str(e))
        import traceback
        mud.log_string(traceback.format_exc())
        return False


def register_character_creation_hook():
    """Register progression setup for new characters"""
    hooks.add("on_character_create", on_character_created)
    mud.log_string("PROGRESSION: Character creation hook registered")


def on_character_created(info):
    """
    Called when a new character is created.
    Initializes progression system with a default class config.
    
    Args:
        info: Hook info dict with 'ch' (character) key
    """
    ch = info.get('ch')
    if not ch:
        return
    
    # Create a minimal default class config
    # This will be replaced with actual class selection during char creation
    all_skills = progression_skills.get_skill_registry().list_all_skills()
    
    default_class_config = {
        'class_name': 'Novice',
        'skills': {
            'primary': all_skills[:10] if len(all_skills) > 10 else all_skills,
            'secondary': [],
            'tertiary': [],
            'else': []
        },
        'levels': {
            1: {'tdp': 0, 'requirements': {}}
        }
    }
    
    mud.log_string("PROGRESSION: Setting up default progression for new character %s" % ch.name)
    setup_progression(ch, default_class_config)


# =============================================================================
# SKILL COMMANDS
# =============================================================================

def cmd_skills(ch, cmd, arg):
    """
    Usage: skills [all | <category> | <skill_name>]
    
    Display your current skills and their progress.
    Without arguments: Show only skills with progress.
    all: Show all available skills.
    <category>: Show all skills in a category (even with no progress).
    <skill_name>: Show detailed info for a specific skill.
    """
    arg = arg.strip().lower()
    registry = progression_skills.get_skill_registry()
    
    # Check if showing specific skill details
    if arg and arg not in ['all'] and arg not in [cat.lower() for cat in progression_skills.get_all_categories()]:
        # Try as specific skill name
        skill = progression_skills.get_skill(ch, arg)
        if skill:
            skill_info = registry.get_skill_info(skill.name)
            rank_int = int(skill.rank)
            percentage = skill.get_percentage_to_next_rank()
            bits_to_next = skill.get_bits_to_next_rank()
            
            ch.send("{c" + "=" * 78)
            ch.send("{c%s{n" % skill.name)
            ch.send("{c" + "=" * 78)
            ch.send("{wRank:{n %d.%02d" % (rank_int, percentage))
            ch.send("{wProgress:{n %d / %d bits" % (skill.field_exp, bits_to_next))
            
            if skill_info:
                ch.send("{wCategory:{n %s" % skill_info.get('category', 'Unknown'))
                desc = skill_info.get('description', '')
                if desc:
                    ch.send("{wDescription:{n %s" % desc)
            
            ch.send("{c" + "=" * 78)
            return
        else:
            # Not a skill name or category
            ch.send("Skill '%s' not found. Use 'skills all' to see available skills." % arg)
            return
    
    # Show all categories or specific category
    if arg == 'all':
        # Show all skills
        by_category = {}
        for skill_name in registry.list_all_skills():
            skill_info = registry.get_skill_info(skill_name)
            category = skill_info.get('category', 'Miscellaneous')
            
            if category not in by_category:
                by_category[category] = []
            
            char_skill = progression_skills.get_skill(ch, skill_name)
            if char_skill:
                by_category[category].append(char_skill)
            else:
                # Add skill with 0 progress
                new_skill = progression_skills.Skill(skill_name)
                by_category[category].append(new_skill)
    elif arg and arg in [cat.lower() for cat in progression_skills.get_all_categories()]:
        # Show specific category (all skills in it)
        actual_category = None
        for cat in progression_skills.get_all_categories():
            if cat.lower() == arg:
                actual_category = cat
                break
        
        by_category = {actual_category: progression_skills.get_skills_by_category(ch, actual_category, all_skills=True)}
    else:
        # Show only skills with progress
        by_category = progression_skills.get_skills_with_progress(ch)
    
    # Display the skills
    ch.send("{c" + "*" * 78)
    
    total_ranks = 0
    for category in sorted(by_category.keys()):
        skills_list = by_category[category]
        
        if not skills_list:
            continue
        
        ch.send("{c%s{n" % category.upper())
        
        # Sort skills in this category alphabetically
        skills_list.sort(key=lambda s: s.name)
        
        # Display in two columns, aligned at column 40 and 80
        for i in range(0, len(skills_list), 2):
            skill1 = skills_list[i]
            rank1_int = int(skill1.rank)
            percent1 = skill1.get_percentage_to_next_rank()
            total_ranks += rank1_int
            
            # Left column: skill name padded to 35 chars, then rank.percent
            left_name = skill1.name[:33].ljust(33)
            left_col = " {w%s{n {y%d.%02d{n" % (left_name, rank1_int, percent1)
            
            if i + 1 < len(skills_list):
                skill2 = skills_list[i + 1]
                rank2_int = int(skill2.rank)
                percent2 = skill2.get_percentage_to_next_rank()
                total_ranks += rank2_int
                
                # Right column: skill name padded to 35 chars, then rank.percent
                right_name = skill2.name[:33].ljust(33)
                right_col = " {w%s{n {y%d.%02d{n" % (right_name, rank2_int, percent2)
                
                ch.send(left_col + right_col)
            else:
                ch.send(left_col)
        
        ch.send("")
    
    # Footer
    ch.send("{c" + "*" * 78)
    
    # Get level and class from leveling system
    try:
        current_level = progression_leveling.get_current_level(ch)
        class_name = progression_skills.get_skills(ch).get('primary', None)
        if class_name:
            class_name = class_name.name.split()[0]
        else:
            class_name = "Unknown"
    except:
        current_level = 1
        class_name = "Unknown"
    
    # Get TDP from character attributes
    try:
        from attributes import attribute_aux
        attr_aux = attribute_aux.get_attributes(ch)
        tdp = attr_aux.tdp_available if attr_aux else 0
    except:
        tdp = 0
    
    footer = "|Total Ranks: %-45d TDPs: %-11d|" % (total_ranks, tdp)
    ch.send(footer)
    footer2 = "|Level: %d %s * Favors: None%-45s|" % (current_level, class_name, "")
    ch.send(footer2)
    ch.send("{c" + "*" * 78)


def cmd_init_progression(ch, cmd, arg):
    """
    Usage: init_progression [target]
    Admin command to manually initialize progression for a character.
    If no target specified, initializes self.
    """
    target = ch
    
    if arg and arg.strip():
        # Find target in room by iterating through chars
        target_name = arg.strip().lower()
        target = None
        for char in ch.room.chars:
            if target_name in char.name.lower():
                target = char
                break
        
        if not target:
            ch.send("Character '%s' not found in room." % arg.strip())
            return
    
    if not target:
        ch.send("Target not found.")
        return
    
    # Create default class config
    default_class_config = {
        'class_name': 'Novice',
        'skills': {
            'primary': [],
            'secondary': [],
            'tertiary': [],
            'else': progression_skills.get_skill_registry().list_all_skills()
        },
        'levels': {
            1: {'tdp': 0, 'requirements': {}}
        }
    }
    
    mud.log_string("DEBUG: About to setup_progression for %s" % target.name)
    result = setup_progression(target, default_class_config)
    
    if result:
        ch.send("Progression initialized for %s" % target.name)
        mud.log_string("ADMIN: %s initialized progression for %s" % (ch.name, target.name))
    else:
        ch.send("Failed to initialize progression for %s" % target.name)
        mud.log_string("ERROR: Failed to initialize progression for %s" % target.name)


# =============================================================================
# MODULE INITIALIZATION
# =============================================================================

def register_all_commands():
    """
    Register all progression commands with the MUD.
    Called during module initialization.
    """
    try:
        # Register hooks for character lifecycle
        register_character_creation_hook()
        
        # Register commands
        progression_experience.register_experience_commands()
        progression_leveling.register_leveling_commands()
        register_progression_commands()
        mud.log_string("PROGRESSION: All commands registered")
    except Exception as e:
        mud.log_string("ERROR: Failed to register progression commands: %s" % str(e))


def register_progression_commands():
    """Register progression-specific commands"""
    try:
        import mudsys
        mudsys.add_cmd("skills", None, cmd_skills, "player", False)
        mudsys.add_cmd("init_progression", None, cmd_init_progression, "admin", False)
        mud.log_string("Progression commands registered")
    except Exception as e:
        mud.log_string("ERROR: Failed to register progression commands: %s" % str(e))