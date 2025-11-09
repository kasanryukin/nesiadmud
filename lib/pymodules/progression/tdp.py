"""
TDP (Training Development Points) Management
=============================================
Handles TDP granting for skill rank advancement and level progression.
Integrates with attributes system for TDP storage.
"""

import mud


def grant_tdp_for_skill_rank(ch, old_rank, new_rank):
    """
    Grant TDP for skill rank advancement.
    
    TDP awarded scales with rank:
    - Ranks 0-99: 1 TDP per rank
    - Ranks 100-199: 2 TDP per rank
    - Ranks 200-499: 3 TDP per rank
    - Ranks 500-999: 4 TDP per rank
    - Ranks 1000+: 5 TDP per rank
    
    Args:
        ch: Character
        old_rank: Previous rank (float)
        new_rank: New rank (float)
    
    Returns:
        int: Total TDP granted
    """
    # Get attribute auxiliary for TDP storage
    try:
        from attributes import attribute_aux
        attr_aux = attribute_aux.get_attributes(ch)
        if not attr_aux:
            mud.log_string("ERROR: Cannot grant TDP - no attributes for %s" % ch.name)
            return 0
    except ImportError:
        mud.log_string("ERROR: Cannot grant TDP - attributes module not available")
        return 0
    
    # Calculate TDP for each rank gained
    total_tdp = 0
    old_rank_int = int(old_rank)
    new_rank_int = int(new_rank)
    
    for rank in range(old_rank_int, new_rank_int):
        tdp_for_rank = _get_tdp_for_rank(rank)
        total_tdp += tdp_for_rank
    
    if total_tdp > 0:
        attr_aux.add_tdp(total_tdp)
        mud.log_string("TDP: %s gained %d TDP (rank %d -> %d)" % 
                      (ch.name, total_tdp, old_rank_int, new_rank_int))
    
    return total_tdp


def _get_tdp_for_rank(rank):
    """Get TDP awarded for reaching a specific rank"""
    if rank < 100:
        return 1
    elif rank < 200:
        return 2
    elif rank < 500:
        return 3
    elif rank < 1000:
        return 4
    else:
        return 5


def grant_tdp_for_level(ch, level_num, amount):
    """
    Grant TDP for reaching a level.
    
    Args:
        ch: Character
        level_num: Level reached
        amount: TDP to grant
    
    Returns:
        bool: True if successful
    """
    try:
        from attributes import attribute_aux
        attr_aux = attribute_aux.get_attributes(ch)
        if not attr_aux:
            return False
        
        attr_aux.add_tdp(amount)
        mud.log_string("TDP: %s gained %d TDP from reaching level %d" % 
                      (ch.name, amount, level_num))
        return True
    
    except ImportError:
        mud.log_string("ERROR: Cannot grant level TDP - attributes module not available")
        return False


def get_available_tdp(ch):
    """
    Get character's available TDP.
    
    Args:
        ch: Character
    
    Returns:
        int: Available TDP
    """
    try:
        from attributes import attribute_aux
        attr_aux = attribute_aux.get_attributes(ch)
        if attr_aux:
            return attr_aux.tdp_available
    except ImportError:
        pass
    
    return 0


def get_spent_tdp(ch):
    """
    Get character's spent TDP.
    
    Args:
        ch: Character
    
    Returns:
        int: Spent TDP
    """
    try:
        from attributes import attribute_aux
        attr_aux = attribute_aux.get_attributes(ch)
        if attr_aux:
            return attr_aux.tdp_spent
    except ImportError:
        pass
    
    return 0


def get_total_tdp(ch):
    """
    Get character's total TDP (available + spent).
    
    Args:
        ch: Character
    
    Returns:
        int: Total TDP earned
    """
    return get_available_tdp(ch) + get_spent_tdp(ch)