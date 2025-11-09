"""
Phase 2: Skills System (Refactored for Class-Based Placement)
==============================================================
Skill definitions and SkillGroup management with dynamic class-based placement.

Skills are class-agnostic. Each class/guild/profession defines:
- Which skills are available
- What placement each skill gets (primary/secondary/tertiary/else)
- How the skills group together for pulsing

Old approach: Hard-coded placement in skill system
New approach: Placement defined per-class in class YAML config
"""

from . import yaml_parser as yaml
import mud
import os


CONFIG_DIR = "./config"
SKILLS_CONFIG = os.path.join(CONFIG_DIR, "skills.yaml")

# Skill rank constants
SKILL_MIN_RANK = 0
SKILL_MAX_RANK = 3000


class Skill:
    """
    Represents a single skill with rank and field experience.
    NOTE: Placement is NOT stored here - it's determined by character's class
    """
    
    def __init__(self, name):
        self.name = name
        self.rank = 0.0  # Double with 2 significant digits (e.g., 12.31)
        self.field_exp = 0  # Raw bits in field exp pool
        self.last_trained = None  # Timestamp of last training
    
    def get_bits_to_next_rank(self):
        """
        Calculate bits needed to reach next rank.
        Formula: 200 + current_rank
        """
        current_rank = int(self.rank)
        return 200 + current_rank
    
    def get_total_bits_to_rank(self, target_rank):
        """Calculate total bits from rank 0 to target_rank"""
        total = 0
        for n in range(target_rank):
            total += 200 + n
        return total
    
    def add_field_exp(self, bits):
        """Add bits to field experience pool"""
        self.field_exp = max(0, self.field_exp + bits)
    
    def convert_field_exp_to_rank(self, bits_to_convert):
        """Convert field exp bits to actual rank advancement"""
        if self.field_exp <= 0 or bits_to_convert <= 0:
            return 0
        
        bits_converted = min(bits_to_convert, self.field_exp)
        self.field_exp -= bits_converted
        
        remaining_bits = bits_converted
        ranks_gained = 0
        current_test_rank = int(self.rank)
        
        while remaining_bits >= self.get_bits_to_next_rank():
            bits_needed = 200 + current_test_rank
            remaining_bits -= bits_needed
            ranks_gained += 1
            current_test_rank += 1
        
        self.rank += ranks_gained
        
        bits_to_next = 200 + int(self.rank)
        if bits_to_next > 0:
            self.rank += remaining_bits / bits_to_next
        
        self.rank = min(self.rank, SKILL_MAX_RANK)
        
        return bits_converted
    
    def get_percentage_to_next_rank(self):
        """Get field exp as percentage toward next rank"""
        bits_to_next = self.get_bits_to_next_rank()
        if bits_to_next <= 0:
            return 0
        return int((self.field_exp / bits_to_next) * 100)
    
    def to_dict(self):
        """Serialize to dictionary"""
        return {
            "name": self.name,
            "rank": self.rank,
            "field_exp": self.field_exp,
            "last_trained": self.last_trained,
        }
    
    def from_dict(self, data):
        """Deserialize from dictionary"""
        self.name = data.get("name", self.name)
        self.rank = data.get("rank", 0.0)
        self.field_exp = data.get("field_exp", 0)
        self.last_trained = data.get("last_trained")


class SkillGroup:
    """
    Represents a group of skills that pulse together.
    Placement is now determined dynamically from class config.
    """
    
    def __init__(self, name, skillset_placement="tertiary"):
        self.name = name
        self.skillset_placement = skillset_placement  # primary, secondary, tertiary, else
        self.skills = {}  # skill_name -> Skill object
        self.last_pulse_time = None
        self.pulse_interval = 5 * 60  # Configurable per group (default 5 min)
    
    def add_skill(self, skill_name):
        """Add a skill to this group"""
        if skill_name not in self.skills:
            self.skills[skill_name] = Skill(skill_name)
            return True
        return False
    
    def get_skill(self, skill_name):
        """Get skill by name"""
        return self.skills.get(skill_name)
    
    def get_all_skills(self):
        """Return list of all skills in this group"""
        return list(self.skills.values())
    
    def should_pulse(self, current_time, pulse_interval=None):
        """Check if this group's skills should pulse"""
        if self.last_pulse_time is None:
            return False
        
        time_since_pulse = current_time - self.last_pulse_time
        check_interval = pulse_interval if pulse_interval is not None else self.pulse_interval
        return time_since_pulse >= check_interval
    
    def pulse(self, current_time, wisdom_modifier=0.0):
        """Execute pulse: convert field exp to ranks for all skills"""
        if not self.should_pulse(current_time):
            return
        
        pulse_size = self.calculate_pulse_size(wisdom_modifier)
        
        for skill in self.skills.values():
            if skill.field_exp > 0:
                bits_to_drain = int(pulse_size * skill.field_exp)
                skill.convert_field_exp_to_rank(bits_to_drain)
        
        self.last_pulse_time = current_time
    
    def calculate_pulse_size(self, wisdom_modifier=0.0):
        """Calculate what fraction of the pool drains in this pulse"""
        base_drain_rates = {
            "primary": 0.05,
            "secondary": 0.04,
            "tertiary": 0.03,
            "else": 0.02,
        }
        
        base_rate = base_drain_rates.get(self.skillset_placement, 0.02)
        wisdom_bonus = 1.0 + (wisdom_modifier * 0.5)
        
        return base_rate * wisdom_bonus
    
    def to_dict(self):
        """Serialize to dictionary"""
        return {
            "name": self.name,
            "skillset_placement": self.skillset_placement,
            "skills": {sname: s.to_dict() for sname, s in self.skills.items()},
            "pulse_interval": self.pulse_interval,
            "last_pulse_time": self.last_pulse_time,
        }
    
    def from_dict(self, data):
        """Deserialize from dictionary"""
        self.name = data.get("name", self.name)
        self.skillset_placement = data.get("skillset_placement", "tertiary")
        self.pulse_interval = data.get("pulse_interval", 5 * 60)
        self.last_pulse_time = data.get("last_pulse_time")
        
        for sname, sdata in data.get("skills", {}).items():
            skill = Skill(sname)
            skill.from_dict(sdata)
            self.skills[sname] = skill


class SkillRegistry:
    """
    Global registry of all available skills (class-agnostic).
    Loaded from config/skills.yaml
    """
    
    def __init__(self):
        self.skills = {}  # skill_name -> skill metadata
    
    def load_from_yaml(self, filepath):
        """Load skill definitions from YAML config"""
        try:
            with open(filepath, 'r') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            mud.log_string("ERROR: Failed to load skills config: %s" % str(e))
            return False
    
        if not config or 'skills' not in config:
            mud.log_string("ERROR: Invalid skills config format")
            return False
    
        skills_list = config['skills']
        if not isinstance(skills_list, list):
            mud.log_string("ERROR: skills is not a list, it's: %s" % type(skills_list))
            return False
    
        for idx, skill_data in enumerate(skills_list):
            # Debug: check what we got
            if not isinstance(skill_data, dict):
                mud.log_string("WARNING: Skill item %d is not a dict, it's %s: %s" % 
                              (idx, type(skill_data), skill_data))
                continue
        
            skill_name = skill_data.get('name')
        
            # Debug: check if name is valid
            if skill_name is None:
                mud.log_string("WARNING: Skill item %d has no 'name' key. Keys: %s" % 
                              (idx, list(skill_data.keys())))
                continue
        
            if not isinstance(skill_name, str):
                mud.log_string("WARNING: Skill name is not a string, it's %s: %s (item %d)" % 
                              (type(skill_name), skill_name, idx))
                continue
        
            # Now we know skill_name is a valid string
            self.skills[skill_name] = {
                'name': skill_name,
                'category': skill_data.get('category', 'Miscellaneous'),
                'description': skill_data.get('description', ''),
            }
    
        if self.skills:
            mud.log_string("SKILLS: Loaded %d skill definitions from config" % len(self.skills))
            return True
        else:
            mud.log_string("WARNING: No skills loaded from config (processed %d items)" % len(skills_list))
            return False

    def get_skill_info(self, skill_name):
        """Get skill metadata"""
        return self.skills.get(skill_name)
    
    def list_all_skills(self):
        """Return list of all skill names"""
        return sorted(self.skills.keys())
    
    def skill_exists(self, skill_name):
        """Check if a skill is registered"""
        return skill_name in self.skills


# Global registry instance
_skill_registry = None


def get_skill_registry():
    """Get or initialize the global skill registry"""
    global _skill_registry
    if _skill_registry is None:
        _skill_registry = SkillRegistry()
        if not _skill_registry.load_from_yaml(SKILLS_CONFIG):
            mud.log_string("WARNING: Skill registry initialization failed")
    return _skill_registry


def setup_skills_from_class_config(ch, class_config):
    """
    Initialize skill system for a character based on their class config.
    This is called AFTER the class is chosen for the character.
    
    Args:
        ch: Character to initialize
        class_config: Loaded class YAML config (dict)
    """
    skill_aux = ch.getAuxiliary("skills")
    
    if skill_aux is None:
        skill_aux = ch.createAuxiliary("skills")
    
    skill_aux.groups = {}
    skill_aux.class_name = class_config.get('class_name', 'Unknown')
    
    # Get skill placement from class config
    skills_config = class_config.get('skills', {})
    
    # Create skill groups for each placement tier
    for placement in ['primary', 'secondary', 'tertiary', 'else']:
        skill_names = skills_config.get(placement, [])
        
        if skill_names:
            group = SkillGroup(f"{class_config.get('class_name', 'Class')} {placement.title()}", placement)
            
            for skill_name in skill_names:
                # Verify skill exists in registry
                if get_skill_registry().skill_exists(skill_name):
                    group.add_skill(skill_name)
                else:
                    mud.log_string("WARNING: Skill '%s' not found in registry (class %s)" % 
                                  (skill_name, class_config.get('class_name')))
            
            if group.get_all_skills():  # Only add if group has skills
                skill_aux.groups[placement] = group
    
    mud.log_string("SKILLS: Initialized %d skill groups for %s (class: %s)" % 
                  (len(skill_aux.groups), ch.name, class_config.get('class_name')))


def get_skills(ch):
    """Get character's skill groups dict"""
    skill_aux = ch.getAuxiliary("skills")
    if skill_aux and hasattr(skill_aux, 'groups'):
        return skill_aux.groups
    return {}


def get_skill(ch, skill_name):
    """Get a specific skill by name (searches all groups)"""
    groups = get_skills(ch)
    for group in groups.values():
        skill = group.get_skill(skill_name)
        if skill:
            return skill
    return None


def get_skill_placement(ch, skill_name):
    """Get the placement tier of a skill for this character"""
    groups = get_skills(ch)
    for placement, group in groups.items():
        if group.get_skill(skill_name):
            return placement
    return None


def get_skill_rank(ch, skill_name):
    """Get integer rank of a skill"""
    skill = get_skill(ch, skill_name)
    if skill:
        return int(skill.rank)
    return 0


def get_skill_rank_with_fraction(ch, skill_name):
    """Get full rank with fractional bits (e.g., 12.31)"""
    skill = get_skill(ch, skill_name)
    if skill:
        return skill.rank
    return 0.0


def get_all_skills_for_character(ch):
    """Get all skills available to this character"""
    all_skills = {}
    groups = get_skills(ch)
    for group in groups.values():
        for skill in group.get_all_skills():
            all_skills[skill.name] = skill
    return all_skills


def get_skills_with_progress(ch):
    """
    Get only skills that have any progress (rank > 0 or field_exp > 0).
    Returns dict organized by category.
    
    Returns:
        dict: {category: [skill_objects]}
    """
    registry = get_skill_registry()
    all_char_skills = get_all_skills_for_character(ch)
    
    # Filter to only skills with progress
    skills_with_progress = {}
    for skill_name, skill in all_char_skills.items():
        if skill.rank > 0 or skill.field_exp > 0:
            skills_with_progress[skill_name] = skill
    
    # Organize by category
    by_category = {}
    for skill_name in skills_with_progress:
        skill_info = registry.get_skill_info(skill_name)
        if skill_info:
            category = skill_info.get('category', 'Miscellaneous')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(skills_with_progress[skill_name])
    
    return by_category


def get_skills_by_category(ch, category, all_skills=False):
    """
    Get skills in a specific category.
    
    Args:
        ch: Character
        category: Category name
        all_skills: If True, return all skills in category (even with 0 progress)
                   If False, return only skills with progress
    
    Returns:
        list: Skill objects
    """
    registry = get_skill_registry()
    
    if all_skills:
        # Return all skills in category, add progress data
        skills = []
        for skill_name, skill_info in registry.skills.items():
            if skill_info.get('category', 'Miscellaneous').lower() == category.lower():
                char_skill = get_skill(ch, skill_name)
                if char_skill:
                    skills.append(char_skill)
                else:
                    # Create new skill with 0 progress for display
                    new_skill = Skill(skill_name)
                    skills.append(new_skill)
        return skills
    else:
        # Return only skills with progress
        by_category = get_skills_with_progress(ch)
        return by_category.get(category, [])


def get_total_ranks(ch):
    """Get total of all integer ranks (excluding fractional parts)"""
    all_skills = get_all_skills_for_character(ch)
    return sum(int(skill.rank) for skill in all_skills.values())


def lookup_skill_by_weapon_class(weapon_class):
    """
    Look up skill name by weapon_class metadata.
    
    Args:
        weapon_class: Weapon class identifier (e.g., "long_blades")
    
    Returns:
        str or None: Skill name if found
    
    Example:
        >>> lookup_skill_by_weapon_class("long_blades")
        "Long Blades"
    """
    registry = get_skill_registry()
    
    for skill_name, skill_info in registry.skills.items():
        if skill_info.get('weapon_class') == weapon_class:
            return skill_name
    
    return None


def lookup_skill_by_armor_type(armor_type):
    """
    Look up skill name by armor_type metadata.
    
    Args:
        armor_type: Armor type identifier (e.g., "heavy")
    
    Returns:
        str or None: Skill name if found
    
    Example:
        >>> lookup_skill_by_armor_type("heavy")
        "Heavy Armor"
    """
    registry = get_skill_registry()
    
    for skill_name, skill_info in registry.skills.items():
        if skill_info.get('armor_type') == armor_type:
            return skill_name
    
    return None


def get_skills_in_category(category):
    """
    Get all skills in a specific category.
    
    Args:
        category: Category name (e.g., "Combat", "Crafting")
    
    Returns:
        list: List of skill names in that category
    """
    registry = get_skill_registry()
    result = []
    
    for skill_name, skill_info in registry.skills.items():
        if skill_info.get('category', '').lower() == category.lower():
            result.append(skill_name)
    
    return sorted(result)


def get_weapon_skills():
    """Get all weapon-related skills"""
    return get_skills_in_category("Weapons")


def get_armor_skills():
    """Get all armor-related skills"""
    return get_skills_in_category("Armor")


def get_magic_skills():
    """Get all magic-related skills"""
    return get_skills_in_category("Magic")


def get_crafting_skills():
    """Get all crafting skills"""
    return get_skills_in_category("Crafting")


def get_gathering_skills():
    """Get all gathering skills"""
    return get_skills_in_category("Gathering")


def format_skill_display(skill, width=40):
    """
    Format a skill for display: "Name              Rank.Percent"
    
    Args:
        skill: Skill object
        width: Width to pad skill name to
    
    Returns:
        str: Formatted skill display
    """
    rank_int = int(skill.rank)
    percentage = skill.get_percentage_to_next_rank()
    
    skill_part = skill.name.ljust(width)
    rank_part = "{y%d.%02d{n" % (rank_int, percentage)
    
    return skill_part + rank_part


def get_all_categories():
    """Get sorted list of all skill categories"""
    registry = get_skill_registry()
    categories = set()
    
    for skill_info in registry.skills.values():
        category = skill_info.get('category', 'Miscellaneous')
        categories.add(category)
    
    return sorted(list(categories))