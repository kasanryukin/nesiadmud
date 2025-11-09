"""
Phase 2: Level Progression System (Class-Based)
===============================================
Manages character levels and skill requirements for level advancement.
Level requirements are now CLASS-SPECIFIC, loaded from class config.

Old approach: Single global levels.yaml with requirements for all
New approach: Each class has its own level requirements in class config
"""

import mud
from . import skills
from . import yaml_parser

# Level constants
LEVEL_MIN = 1
LEVEL_MAX = 250


class LevelRequirement:
    """Represents a single skill requirement for a level"""
    
    def __init__(self, skill_name, required_rank, count_type="any"):
        self.skill_name = skill_name
        self.required_rank = required_rank
        self.count_type = count_type  # "any" = counts toward total, "bonus" = doesn't count
    
    def is_met(self, character_skill_rank):
        """Check if this requirement is met"""
        return character_skill_rank >= self.required_rank


class LevelDefinition:
    """Represents a single level with all its skill requirements"""
    
    def __init__(self, level_number):
        self.level = level_number
        self.requirements = []
        self.total_required_ranks = 0
        self.tdp_reward = 0  # TDP granted when reaching this level
    
    def add_requirement(self, skill_name, required_rank, count_type="any"):
        """Add a skill requirement"""
        req = LevelRequirement(skill_name, required_rank, count_type)
        self.requirements.append(req)
        if count_type == "any":
            self.total_required_ranks += required_rank
    
    def set_tdp_reward(self, tdp_amount):
        """Set TDP reward for this level"""
        self.tdp_reward = tdp_amount
    
    def check_met(self, ch):
        """
        Check if character meets all requirements for this level.
        
        Returns:
            tuple: (is_met: bool, unmet_skills: list of (skill_name, required, actual))
        """
        unmet = []
        
        for req in self.requirements:
            actual_rank = skills.get_skill_rank(ch, req.skill_name)
            
            if not req.is_met(actual_rank):
                unmet.append((req.skill_name, req.required_rank, actual_rank))
        
        return (len(unmet) == 0, unmet)
    
    def get_progress(self, ch):
        """Get progress toward this level as a percentage"""
        if not self.requirements:
            return 100.0
        
        met_ranks = 0
        for req in self.requirements:
            actual_rank = skills.get_skill_rank(ch, req.skill_name)
            met_ranks += min(actual_rank, req.required_rank)
        
        if self.total_required_ranks <= 0:
            return 100.0
        
        return (met_ranks / self.total_required_ranks) * 100.0
    
    def to_dict(self):
        """Serialize to dictionary"""
        return {
            "level": self.level,
            "requirements": [
                {
                    "skill": req.skill_name,
                    "rank": req.required_rank,
                    "count_type": req.count_type
                }
                for req in self.requirements
            ],
            "tdp_reward": self.tdp_reward,
        }
    
    def from_dict(self, data):
        """Deserialize from dictionary"""
        self.level = data.get("level", self.level)
        self.tdp_reward = data.get("tdp_reward", 0)
        for req_data in data.get("requirements", []):
            self.add_requirement(
                req_data["skill"],
                req_data["rank"],
                req_data.get("count_type", "any")
            )


def setup_leveling_from_class_config(ch, class_config):
    """
    Initialize leveling system for a character based on their class config.
    Called AFTER the class is chosen for the character.
    
    Args:
        ch: Character to initialize
        class_config: Loaded class YAML config (dict)
    """
    level_aux = ch.getAuxiliary("leveling")
    
    if level_aux is None:
        level_aux = ch.createAuxiliary("leveling")
    
    level_aux.current_level = LEVEL_MIN
    level_aux.experience_points = 0
    level_aux.class_name = class_config.get('class_name', 'Unknown')
    
    # Build level definitions from class config
    level_aux.level_definitions = {}
    levels_config = class_config.get('levels', {})
    
    for level_num_str, level_data in levels_config.items():
        try:
            level_num = int(level_num_str)
        except ValueError:
            continue
        
        if level_num < LEVEL_MIN or level_num > LEVEL_MAX:
            continue
        
        level_def = LevelDefinition(level_num)
        level_def.set_tdp_reward(level_data.get('tdp_reward', 0))
        
        for req_data in level_data.get('requirements', []):
            level_def.add_requirement(
                req_data['skill'],
                req_data['rank'],
                req_data.get('count_type', 'any')
            )
        
        level_aux.level_definitions[level_num] = level_def
    
    mud.log_string("LEVELING: Initialized %d level tiers for %s (class: %s)" % 
                  (len(level_aux.level_definitions), ch.name, class_config.get('class_name')))


def setup_leveling(ch):
    """
    Legacy setup for leveling (before class is chosen).
    Creates empty auxiliary that will be populated when class is selected.
    
    Args:
        ch: Character to initialize
    """
    level_aux = ch.getAuxiliary("leveling")
    
    if level_aux is None:
        level_aux = ch.createAuxiliary("leveling")
        level_aux.current_level = LEVEL_MIN
        level_aux.experience_points = 0
        level_aux.class_name = "Unclassed"
        level_aux.level_definitions = {}
        mud.log_string("LEVELING: Initialized leveling system for %s" % ch.name)


def get_current_level(ch):
    """Get character's current level"""
    level_aux = ch.getAuxiliary("leveling")
    if level_aux:
        return level_aux.current_level
    return LEVEL_MIN


def set_current_level(ch, level_num):
    """Set character's level directly (admin use)"""
    level_aux = ch.getAuxiliary("leveling")
    if not level_aux:
        return False
    
    level_num = max(LEVEL_MIN, min(LEVEL_MAX, level_num))
    level_aux.current_level = level_num
    return True


def get_level_definition(ch, level_num):
    """Get a specific level definition for this character"""
    level_aux = ch.getAuxiliary("leveling")
    if not level_aux or not hasattr(level_aux, 'level_definitions'):
        return None
    return level_aux.level_definitions.get(level_num)


def check_level_up(ch):
    """
    Check if character should advance to next level.
    Called periodically (e.g., on skill rank up).
    
    Returns:
        bool: True if character leveled up
    """
    current_level = get_current_level(ch)
    next_level_num = current_level + 1
    
    if next_level_num > LEVEL_MAX:
        return False
    
    next_level_def = get_level_definition(ch, next_level_num)
    
    if not next_level_def:
        return False
    
    is_met, unmet_skills = next_level_def.check_met(ch)
    
    if is_met:
        level_aux = ch.getAuxiliary("leveling")
        old_level = level_aux.current_level
        level_aux.current_level = next_level_num
        
        mud.log_string("LEVEL_UP: %s advanced from level %d to %d" % 
                      (ch.name, old_level, next_level_num))
        
        # Announce to character
        ch.send("\n{y*** You have advanced to level %d! ***{n\n" % next_level_num)
        
        # Grant TDP for level (class-specific amount)
        tdp_reward = next_level_def.tdp_reward
        if tdp_reward > 0:
            try:
                from . import attribute_aux
                attr_aux = attribute_aux.get_attributes(ch)
                if attr_aux:
                    attr_aux.add_tdp(tdp_reward)
                    ch.send("{g*** You gained %d TDP from reaching level %d! ***{n\n" % (tdp_reward, next_level_num))
            except ImportError:
                pass
        
        # Recursively check if they can advance further
        check_level_up(ch)
        
        return True
    
    return False


def get_next_level_progress(ch):
    """
    Get progress toward next level as percentage and unmet requirements.
    
    Returns:
        tuple: (progress_pct: float, unmet_reqs: list)
    """
    current_level = get_current_level(ch)
    next_level_num = current_level + 1
    
    next_level_def = get_level_definition(ch, next_level_num)
    
    if not next_level_def:
        return (100.0, [])
    
    progress = next_level_def.get_progress(ch)
    _, unmet = next_level_def.check_met(ch)
    
    return (progress, unmet)


# Debug/admin commands

def cmd_level(ch, cmd, arg):
    """
    Usage: level [target]
    Display character level and next level requirements.
    """
    target = ch
    
    if arg and arg.strip():
        try:
            target = ch.room.get_character(arg.strip())
        except:
            ch.send("Character '%s' not found." % arg.strip())
            return
    
    current_level = get_current_level(target)
    progress, unmet_reqs = get_next_level_progress(target)
    
    ch.send("{c" + "=" * 60)
    ch.send("{c%s - Level %d{n" % (target.name, current_level))
    ch.send("{c" + "=" * 60)
    
    if current_level >= LEVEL_MAX:
        ch.send("{yMaximum level reached!{n")
        ch.send("{c" + "=" * 60)
        return
    
    next_level_num = current_level + 1
    ch.send("{wProgress to Level %d: {y%.1f%%{n\n" % (next_level_num, progress))
    
    if unmet_reqs:
        ch.send("{rUnmet Requirements:{n")
        for skill_name, required, actual in unmet_reqs:
            ch.send("  {w%-25s {r%3d / %3d{n" % (skill_name, actual, required))
    else:
        ch.send("{gAll requirements met! Type 'advance' to level up.{n")
    
    ch.send("{c" + "=" * 60)


def cmd_advance(ch, cmd, arg):
    """
    Usage: advance
    Attempt to advance to next level if requirements are met.
    """
    if check_level_up(ch):
        ch.send("You have advanced to the next level!")
    else:
        progress, unmet = get_next_level_progress(ch)
        if unmet:
            ch.send("You do not meet the requirements for the next level.")
            ch.send("Type 'level' to see what's needed.")
        else:
            ch.send("You are already at maximum level.")


def cmd_setlevel(ch, cmd, arg):
    """
    Usage: setlevel <target> <level_number>
    Admin command to set character level.
    """
    args = arg.split()
    if len(args) < 2:
        ch.send("Usage: setlevel <target> <level_number>")
        return
    
    target_name = args[0]
    try:
        level_num = int(args[1])
    except ValueError:
        ch.send("Level must be a number.")
        return
    
    try:
        target = ch.room.get_character(target_name)
    except:
        ch.send("Character '%s' not found." % target_name)
        return
    
    if set_current_level(target, level_num):
        ch.send("Set %s to level %d" % (target.name, level_num))
        mud.log_string("ADMIN: %s set %s to level %d" % (ch.name, target.name, level_num))
    else:
        ch.send("Failed to set level.")


def register_leveling_commands():
    """Register leveling commands"""
    import mudsys
    mudsys.add_cmd("level", None, cmd_level, "player", False)
    mudsys.add_cmd("advance", None, cmd_advance, "player", False)
    mudsys.add_cmd("setlevel", None, cmd_setlevel, "admin", False)
    mud.log_string("Leveling commands registered")