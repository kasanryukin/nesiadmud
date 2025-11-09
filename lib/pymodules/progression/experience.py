"""
Phase 2: Experience Pool and Pulsing System
============================================
Manages field experience generation, pool sizing, and skill rank advancement.
Integrates with existing Attributes system (Intelligence, Wisdom, Discipline).

Pulse system converts field exp to ranks periodically.
Uses your 8-attribute system for calculations.
"""

import time
import math
import mud
from . import skills
from . import tdp
from . import yaml_parser


# Configuration
OFFLINE_DRAIN_DELAY = 8 * 60 * 60  # 8 hours before offline experience drain
OFFLINE_DRAIN_RATE = 0.6  # 60% per 6 hours (full pool in 8 hours)

# Pulse timing constants
PULSE_TIME_BASELINE = 5 * 60  # 5 minutes in seconds
PULSE_TIME_MINIMUM = 2 * 60   # 2 minutes minimum


class ExperienceManager:
    """
    Manages character experience tracking and pool draining.
    Integrates with existing Attributes system.
    """
    
    def __init__(self, ch):
        self.ch = ch
        self.last_login = time.time()
        self.last_logout = None
        self.last_offline_drain = time.time()
    
    def add_field_exp(self, skill_name, amount):
        """
        Add field experience to a skill's pool.
        Automatically starts pulse timer if not already running.
        
        Args:
            skill_name: Name of skill to train
            amount: Bits of field exp to add
        
        Returns:
            bool: True if successful
        """
        skill = skills.get_skill(self.ch, skill_name)
        if not skill:
            mud.log_string("ERROR: Skill '%s' not found for %s" % (skill_name, self.ch.name))
            return False
        
        # Add field exp to skill's pool
        skill.add_field_exp(amount)
        skill.last_trained = time.time()
        
        # Start pulse timer if not already running
        group = skills.get_skill_registry().get_group_for_skill(skill_name)
        if group and group.last_pulse_time is None:
            group.last_pulse_time = time.time()
        
        return True
    
    def calculate_pool_size(self, skill):
        """
        Calculate maximum pool size for a skill based on its rank and character attributes.
        
        Pool size scales with:
        - Skillset placement (primary > secondary > tertiary > else)
        - Current rank (higher ranks = larger pools)
        - Intelligence (primary effect: increases pool size)
        - Discipline (minor effect: 10% efficiency)
        
        Args:
            skill: Skill object
        
        Returns:
            int: Maximum bits that can be held in pool
        """
        rank = int(skill.rank)
        placement = skill.skillset_placement
        
        # Base pool sizes - function of rank
        # Formula: base_size = (rank_constant * rank) / (rank + placement_divisor) + base_offset
        placement_constants = {
            "primary": {"constant": 15000, "divisor": 900, "offset": 1000},
            "secondary": {"constant": 12750, "divisor": 900, "offset": 850},
            "tertiary": {"constant": 10500, "divisor": 900, "offset": 700},
            "else": {"constant": 8000, "divisor": 900, "offset": 500},
        }
        
        const_data = placement_constants.get(placement, placement_constants["tertiary"])
        constant = const_data["constant"]
        divisor = const_data["divisor"]
        offset = const_data["offset"]
        
        base_pool = (constant * rank) / (rank + divisor) + offset
        
        # Get character's attributes for modifiers
        try:
            from . import attribute_aux
            attr_aux = attribute_aux.get_attributes(self.ch)
            if not attr_aux:
                # No attributes? Use baseline (shouldn't happen)
                int_value = 10
                disc_value = 10
            else:
                int_value = attr_aux.intelligence
                disc_value = attr_aux.discipline
        except ImportError:
            # Attributes not available
            int_value = 10
            disc_value = 10
        
        # Intelligence bonus: linear (0-100% bonus at attr 10-100)
        # Formula: (int - 10) / 90 = modifier, then base_pool *= (1 + modifier * 0.3)
        int_modifier = max(0.0, (int_value - 10) / 90.0)
        int_bonus = int_modifier * 0.3  # Up to 30% bonus from Intelligence
        
        # Discipline bonus: 10% efficiency (so at most 3% bonus if discipline were 100)
        disc_modifier = max(0.0, (disc_value - 10) / 90.0)
        disc_bonus = (disc_modifier * 0.3) * 0.1  # 10% efficiency = up to 3% bonus
        
        # Apply modifiers
        final_pool = base_pool * (1.0 + int_bonus + disc_bonus)
        
        return int(final_pool)
    
    def calculate_pulse_time(self):
        """
        Calculate pulse time based on character's Wisdom and Discipline.
        Range: 5 minutes (baseline) down to 2 minutes (high Wisdom/Discipline).
        
        Returns:
            int: Pulse time in seconds
        """
        try:
            from . import attribute_aux
            attr_aux = attribute_aux.get_attributes(self.ch)
            if not attr_aux:
                wis_value = 10
                disc_value = 10
            else:
                wis_value = attr_aux.wisdom
                disc_value = attr_aux.discipline
        except ImportError:
            wis_value = 10
            disc_value = 10
        
        # Wisdom modifier: linear (0-100% bonus at attr 10-100)
        wis_modifier = max(0.0, (wis_value - 10) / 90.0)
        
        # Discipline modifier: 10% efficiency
        disc_modifier = max(0.0, (disc_value - 10) / 90.0)
        disc_contribution = (disc_modifier * 0.1)  # 10% efficiency
        
        # Total reduction: Wisdom + Discipline (weighted)
        total_modifier = wis_modifier + disc_contribution
        
        # Reduce pulse time by up to 3 minutes based on modifier
        time_reduction = total_modifier * (PULSE_TIME_BASELINE - PULSE_TIME_MINIMUM)
        pulse_time = PULSE_TIME_BASELINE - time_reduction
        
        # Clamp to valid range
        pulse_time = max(PULSE_TIME_MINIMUM, min(PULSE_TIME_BASELINE, pulse_time))
        
        return int(pulse_time)
    
    def check_pulse_all_groups(self):
        """
        Check if any skill groups should pulse and execute pulse if needed.
        Called from character heartbeat.
        """
        groups = skills.get_skills(self.ch)
        current_time = time.time()
        pulse_time = self.calculate_pulse_time()
        
        # Get Wisdom modifier for pulse drain calculation
        try:
            from . import attribute_aux
            attr_aux = attribute_aux.get_attributes(self.ch)
            if attr_aux:
                wis_value = attr_aux.wisdom
                disc_value = attr_aux.discipline
            else:
                wis_value = 10
                disc_value = 10
        except ImportError:
            wis_value = 10
            disc_value = 10
        
        wis_mod = max(0.0, (wis_value - 10) / 90.0)
        disc_mod = max(0.0, (disc_value - 10) / 90.0) * 0.1
        
        for group in groups.values():
            if group.should_pulse(current_time, pulse_time):
                group.pulse(current_time, wis_mod + disc_mod)
                mud.log_string("PULSE: %s's %s group pulsed (field exp -> ranks)" % 
                             (self.ch.name, group.name))
    
    def check_offline_drain(self):
        """
        Check if character should drain experience while offline.
        Offline drain is 60% pool per 6 hours, starting after 8 hours offline.
        
        Called when character logs in.
        """
        if not self.last_logout:
            return
        
        current_time = time.time()
        time_offline = current_time - self.last_logout
        
        # Only drain if offline for more than 8 hours
        if time_offline < OFFLINE_DRAIN_DELAY:
            return
        
        # Calculate how much to drain (60% per 6 hours)
        hours_over_delay = (time_offline - OFFLINE_DRAIN_DELAY) / 3600.0
        drain_multiplier = (OFFLINE_DRAIN_RATE) * (hours_over_delay / 6.0)
        drain_multiplier = min(drain_multiplier, 1.0)  # Cap at 100% drain
        
        groups = skills.get_skills(self.ch)
        
        for group in groups.values():
            for skill in group.get_all_skills():
                if skill.field_exp > 0:
                    # Drain field exp at flat rate (not through normal pulse)
                    bits_to_drain = int(skill.field_exp * drain_multiplier)
                    old_rank = skill.rank
                    skill.convert_field_exp_to_rank(bits_to_drain)
                    
                    # Grant TDP if ranked up
                    if skill.rank > old_rank:
                        tdp.grant_tdp_for_skill_rank(self.ch, old_rank, skill.rank)
        
        self.last_offline_drain = current_time
        mud.log_string("OFFLINE_DRAIN: %s drained %.1f%% experience pools after %.1f hours offline" % 
                      (self.ch.name, drain_multiplier * 100, hours_over_delay))
    
    def on_login(self):
        """Called when character logs in"""
        self.check_offline_drain()
        self.last_login = time.time()
        self.last_logout = None
    
    def on_logout(self):
        """Called when character logs out"""
        self.last_logout = time.time()


def setup_experience(ch):
    """
    Initialize experience system for a character.
    
    Args:
        ch: Character to initialize
    """
    exp_aux = ch.getAuxiliary("experience")
    
    if exp_aux is None:
        exp_aux = ch.createAuxiliary("experience")
        exp_aux.manager = ExperienceManager(ch)
        mud.log_string("EXPERIENCE: Initialized experience system for %s" % ch.name)


def get_experience_manager(ch):
    """Get character's ExperienceManager"""
    exp_aux = ch.getAuxiliary("experience")
    if exp_aux and hasattr(exp_aux, 'manager'):
        return exp_aux.manager
    return None


def add_skill_exp(ch, skill_name, amount, source="unknown"):
    """
    Add field experience to a skill.
    
    Args:
        ch: Character
        skill_name: Name of skill
        amount: Bits of field exp
        source: Where exp came from (combat, crafting, etc.)
    
    Returns:
        bool: True if successful
    """
    manager = get_experience_manager(ch)
    if not manager:
        return False
    
    return manager.add_field_exp(skill_name, amount)


def get_skill_field_exp(ch, skill_name):
    """Get current field exp bits in a skill's pool"""
    skill = skills.get_skill(ch, skill_name)
    if skill:
        return skill.field_exp
    return 0


def get_pool_status(ch, skill_name):
    """
    Get a descriptive status of a skill's pool (empty/low/medium/full/mindlock).
    
    Returns:
        str: Status description
    """
    skill = skills.get_skill(ch, skill_name)
    if not skill:
        return "unknown"
    
    manager = get_experience_manager(ch)
    if not manager:
        return "unknown"
    
    max_pool = manager.calculate_pool_size(skill)
    if max_pool <= 0:
        return "clear"
    
    percentage = (skill.field_exp / max_pool) * 100
    
    if percentage == 0:
        return "clear"
    elif percentage < 25:
        return "low"
    elif percentage < 50:
        return "medium"
    elif percentage < 75:
        return "high"
    elif percentage < 100:
        return "very high"
    else:
        return "mind lock"


# Debug/admin commands

def cmd_exp(ch, cmd, arg):
    """
    Usage: exp [skill_name]
    Display experience pools and learning progress.
    """
    groups = skills.get_skills(ch)
    manager = get_experience_manager(ch)
    
    if not groups or not manager:
        ch.send("Experience system not initialized.")
        return
    
    if arg and arg.strip():
        # Show specific skill
        skill_name = arg.strip()
        skill = skills.get_skill(ch, skill_name)
        if not skill:
            ch.send("Skill '%s' not found." % skill_name)
            return
        
        max_pool = manager.calculate_pool_size(skill)
        status = get_pool_status(ch, skill_name)
        bits_to_next = skill.get_bits_to_next_rank()
        
        ch.send("{c" + "=" * 60)
        ch.send("{c%s{n" % skill.name)
        ch.send("{c" + "=" * 60)
        ch.send("{wRank:           {y%.2f{n" % skill.rank)
        ch.send("{wField Exp:      {y%d / %d bits{n (%s)" % (skill.field_exp, max_pool, status))
        ch.send("{wBits to next:   {y%d{n" % bits_to_next)
        ch.send("{wProgress:       {y%.1f%%{n" % ((skill.field_exp / bits_to_next) * 100))
        ch.send("{c" + "=" * 60)
        return
    
    # Show all skills grouped
    ch.send("{c" + "=" * 80)
    ch.send("{c%-30s %-8s %-15s %-20s{n" % ("Skill", "Rank", "Pool Status", "Group"))
    ch.send("{c" + "=" * 80)
    
    for group_name, group in sorted(groups.items()):
        for skill in sorted(group.get_all_skills(), key=lambda s: s.name):
            status = get_pool_status(ch, skill.name)
            ch.send("{w%-30s {y%7.2f  {g%-15s {b%-20s{n" % 
                   (skill.name[:29], skill.rank, status, group_name))
    
    ch.send("{c" + "=" * 80)
    
    # Show pulse time
    pulse_time = manager.calculate_pulse_time()
    ch.send("{wPulse Interval: {y%.1f minutes{n" % (pulse_time / 60.0))


def cmd_add_exp(ch, cmd, arg):
    """
    Usage: add_exp <skill_name> <amount>
    Admin command to add field experience to a skill for testing.
    """
    args = arg.split()
    if len(args) < 2:
        ch.send("Usage: add_exp <skill_name> <amount>")
        return
    
    skill_name = " ".join(args[:-1])  # Handle multi-word skill names
    try:
        amount = int(args[-1])
    except ValueError:
        ch.send("Amount must be a number.")
        return
    
    if add_skill_exp(ch, skill_name, amount, "admin_command"):
        ch.send("Added %d bits to %s" % (amount, skill_name))
        mud.log_string("ADMIN: %s added %d bits to %s's %s" % 
                      (ch.name, amount, ch.name, skill_name))
    else:
        ch.send("Failed to add experience.")


def register_experience_commands():
    """Register experience commands"""
    import mudsys
    mudsys.add_cmd("exp", None, cmd_exp, "player", False)
    mudsys.add_cmd("add_exp", None, cmd_add_exp, "admin", False)
    mud.log_string("Experience commands registered")