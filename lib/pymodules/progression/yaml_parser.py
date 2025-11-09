"""
YAML Parser with PyYAML Integration
====================================
Tries to use PyYAML if available, falls back to custom parser.
"""
#import json

# Try to import PyYAML first
try:
    import yaml
    HAS_PYYAML = True
except ImportError:
    HAS_PYYAML = False


def safe_load(content):
    """
    Parse YAML content using PyYAML if available, otherwise custom parser.
    
    Args:
        content: YAML string or file object
    
    Returns:
        dict: Parsed YAML
    """
    if HAS_PYYAML:
        if isinstance(content, str):
            return yaml.safe_load(content)
        else:
            # It's a file object
            return yaml.safe_load(content)
    else:
        # Use custom parser
        if isinstance(content, str):
            return parse_yaml(content)
        else:
            # It's a file object - read it
            return parse_yaml(content.read())


def load(filepath):
    """
    Load and parse a YAML file.
    
    Args:
        filepath: Path to YAML file
    
    Returns:
        dict: Parsed YAML
    """
    with open(filepath, 'r') as f:
        return safe_load(f)


# =============================================================================
# CUSTOM YAML PARSER (fallback when PyYAML not available)
# =============================================================================

def parse_yaml(content):
    """
    Parse YAML string content using custom parser.
    
    Args:
        content: YAML string
    
    Returns:
        dict or list: Parsed content
    """
    lines = content.split('\n')
    lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
    
    if not lines:
        return {}
    
    result = _parse_lines(lines, 0, None)
    return result[0] if result else {}


def _parse_lines(lines, start_idx, parent_indent):
    """
    Recursively parse lines.
    
    Returns:
        tuple: (parsed_value, next_line_index)
    """
    if start_idx >= len(lines):
        return (None, start_idx)
    
    line = lines[start_idx]
    indent = _get_indent(line)
    stripped = line.strip()
    
    # Check for list item
    if stripped.startswith('- '):
        return _parse_list(lines, start_idx, indent)
    
    # Check for key: value pair
    if ':' in stripped:
        return _parse_dict(lines, start_idx, indent)
    
    return (None, start_idx)


def _parse_list(lines, start_idx, list_indent):
    """Parse a YAML list starting at start_idx"""
    result = []
    idx = start_idx
    
    while idx < len(lines):
        line = lines[idx]
        indent = _get_indent(line)
        stripped = line.strip()
        
        # Stop if we've moved to a different indentation level
        if indent < list_indent and stripped:
            break
        
        # Skip empty lines
        if not stripped:
            idx += 1
            continue
        
        # Must be a list item at same level
        if not stripped.startswith('- '):
            if indent <= list_indent:
                break
        
        # Extract list item value - might be on same line or next lines
        item_content = stripped[2:].strip()  # Remove '- '
        
        # Check if there's content on the same line as the dash
        if item_content:
            # Simple inline item or start of dict: key: value
            if ':' in item_content:
                # It's a dict item that starts on this line
                # Parse it as a single-key dict, then check for continuation
                key, value = item_content.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                item_dict = {key: _convert_value(value)}
                
                # Check for continued keys on following lines
                next_idx = idx + 1
                while next_idx < len(lines):
                    next_line = lines[next_idx]
                    next_indent = _get_indent(next_line)
                    next_stripped = next_line.strip()
                    
                    # Stop if we hit another list item or lower indent
                    if not next_stripped or next_stripped.startswith('- '):
                        break
                    if next_indent <= list_indent:
                        break
                    
                    # This line is part of the current dict
                    if ':' in next_stripped:
                        k, v = next_stripped.split(':', 1)
                        k = k.strip()
                        v = v.strip()
                        
                        # Check if value is nested (next indent > current)
                        if not v:
                            # Value is on following lines
                            peek_idx = next_idx + 1
                            if peek_idx < len(lines):
                                peek_line = lines[peek_idx]
                                peek_indent = _get_indent(peek_line)
                                peek_stripped = peek_line.strip()
                                
                                if peek_indent > next_indent and peek_stripped:
                                    if peek_stripped.startswith('- '):
                                        parsed_val, peek_idx = _parse_list(lines, peek_idx, peek_indent)
                                    else:
                                        parsed_val, peek_idx = _parse_dict(lines, peek_idx, peek_indent)
                                    item_dict[k] = parsed_val
                                    next_idx = peek_idx
                                    continue
                        
                        item_dict[k] = _convert_value(v)
                        next_idx += 1
                    else:
                        break
                
                result.append(item_dict)
                idx = next_idx
            else:
                # Simple scalar value
                result.append(_convert_value(item_content))
                idx += 1
        else:
            # No content on same line as dash, dict/value is on next lines
            next_idx = idx + 1
            
            if next_idx < len(lines):
                next_line = lines[next_idx]
                next_indent = _get_indent(next_line)
                next_stripped = next_line.strip()
                
                if next_indent > list_indent and next_stripped:
                    if next_stripped.startswith('- '):
                        # Nested list
                        parsed_value, next_idx = _parse_list(lines, next_idx, next_indent)
                    else:
                        # Dict with multiple keys
                        parsed_value, next_idx = _parse_dict(lines, next_idx, next_indent)
                    
                    result.append(parsed_value)
                    idx = next_idx
                else:
                    idx += 1
            else:
                idx += 1
    
    return (result, idx)


def _parse_dict(lines, start_idx, dict_indent):
    """Parse a YAML dictionary starting at start_idx"""
    result = {}
    idx = start_idx
    
    while idx < len(lines):
        line = lines[idx]
        indent = _get_indent(line)
        stripped = line.strip()
        
        # Stop if we've moved to a different indentation level
        if indent < dict_indent and stripped:
            break
        
        # Skip empty lines
        if not stripped:
            idx += 1
            continue
        
        # Skip list items (shouldn't be in a dict at same level)
        if stripped.startswith('- '):
            break
        
        # Must be a key: value pair
        if ':' not in stripped:
            idx += 1
            continue
        
        # Extract key and value
        key, value = stripped.split(':', 1)
        key = key.strip()
        value = value.strip()
        
        # Check if there's a value on the same line
        if value:
            result[key] = _convert_value(value)
            idx += 1
        else:
            # Value is on next lines (nested structure)
            next_idx = idx + 1
            
            if next_idx < len(lines):
                next_line = lines[next_idx]
                next_indent = _get_indent(next_line)
                next_stripped = next_line.strip()
                
                if next_indent > indent:
                    # It's nested
                    if next_stripped.startswith('- '):
                        # It's a list
                        parsed_value, next_idx = _parse_list(lines, next_idx, next_indent)
                    else:
                        # It's a dict
                        parsed_value, next_idx = _parse_dict(lines, next_idx, next_indent)
                    
                    result[key] = parsed_value
                    idx = next_idx
                else:
                    idx += 1
            else:
                idx += 1
    
    return (result, idx)


def _parse_value_or_nested(lines, start_idx, value_indent):
    """Parse a value that might be nested"""
    line = lines[start_idx]
    stripped = line.strip()
    
    if stripped.startswith('- '):
        return _parse_list(lines, start_idx, value_indent)
    elif ':' in stripped:
        return _parse_dict(lines, start_idx, value_indent)
    else:
        return (_convert_value(stripped), start_idx + 1)


def _convert_value(value_str):
    """Convert a string value to appropriate Python type"""
    value_str = value_str.strip()
    
    # Empty string
    if not value_str:
        return None
    
    # Boolean
    if value_str.lower() == 'true':
        return True
    if value_str.lower() == 'false':
        return False
    
    # Null
    if value_str.lower() in ('null', 'none', '~'):
        return None
    
    # Number
    try:
        if '.' in value_str:
            return float(value_str)
        else:
            return int(value_str)
    except ValueError:
        pass
    
    # String (remove quotes if present)
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]
    
    return value_str


def _get_indent(line):
    """Get indentation level (spaces at start)"""
    count = 0
    for char in line:
        if char == ' ':
            count += 1
        elif char == '\t':
            count += 4  # Treat tab as 4 spaces
        else:
            break
    return count

