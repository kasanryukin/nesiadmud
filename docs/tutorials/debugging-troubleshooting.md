---
layout: default
title: Debugging and Troubleshooting
parent: Create Systems
grand_parent: Tutorials
nav_order: 3
permalink: /tutorials/debugging-troubleshooting/
---

# Debugging and Troubleshooting

*This tutorial is currently being developed and will be available soon.*

## Coming Soon

This tutorial will cover debugging techniques and troubleshooting strategies for complex NakedMud systems, including:

- Systematic debugging approaches
- Common issues and solutions
- Performance optimization techniques
- Interactive debugging tools

## Prerequisites

- Completed [Start with the Basics](../start-with-basics/) tutorials
- Experience with complex NakedMud scripting
- Basic knowledge of Python debugging concepts

## What You'll Learn

- Setting up debug infrastructure
- Identifying and resolving common issues
- Performance profiling and optimization
- Creating debugging tools and utilities

*Check back soon for the complete tutorial, or see the [Examples section](/examples/debugging/) for working code examples.*

## Debugging Fundamentals

### Setting Up Debug Infrastructure

```python
# File: lib/pymodules/debug_utils.py

import mudsys
import auxiliary
import json
import time
import traceback
import sys

class DebugLogger:
    """Comprehensive debugging and logging system."""
    
    def __init__(self):
        self.debug_enabled = True
        self.log_levels = {
            "ERROR": 0,
            "WARNING": 1,
            "INFO": 2,
            "DEBUG": 3,
            "TRACE": 4
        }
        self.current_log_level = 2  # INFO level
        self.log_history = []
        self.max_log_history = 1000
        self.performance_tracking = {}
    
    def log(self, level, message, context=None):
        """Log a message with specified level."""
        
        if not self.debug_enabled:
            return
        
        level_num = self.log_levels.get(level.upper(), 2)
        if level_num > self.current_log_level:
            return
        
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Format message
        log_entry = f"[{timestamp}] {level}: {message}"
        
        if context:
            log_entry += f" | Context: {context}"
        
        # Add to history
        self.log_history.append({
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "context": context
        })
        
        # Trim history if too long
        if len(self.log_history) > self.max_log_history:
            self.log_history = self.log_history[-self.max_log_history:]
        
        # Output to MUD log
        mudsys.log_string(log_entry)
    
    def error(self, message, context=None):
        """Log an error message."""
        self.log("ERROR", message, context)
    
    def warning(self, message, context=None):
        """Log a warning message."""
        self.log("WARNING", message, context)
    
    def info(self, message, context=None):
        """Log an info message."""
        self.log("INFO", message, context)
    
    def debug(self, message, context=None):
        """Log a debug message."""
        self.log("DEBUG", message, context)
    
    def trace(self, message, context=None):
        """Log a trace message."""
        self.log("TRACE", message, context)
    
    def log_exception(self, exception, context=None):
        """Log an exception with full traceback."""
        
        exc_type, exc_value, exc_traceback = sys.exc_info()
        
        if exc_traceback:
            tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            tb_string = ''.join(tb_lines)
            
            self.error(f"Exception occurred: {str(exception)}", context)
            self.error(f"Traceback: {tb_string}", context)
        else:
            self.error(f"Exception: {str(exception)}", context)
    
    def start_performance_tracking(self, operation_name):
        """Start tracking performance for an operation."""
        
        self.performance_tracking[operation_name] = {
            "start_time": time.time(),
            "call_count": self.performance_tracking.get(operation_name, {}).get("call_count", 0) + 1
        }
    
    def end_performance_tracking(self, operation_name):
        """End performance tracking and log results."""
        
        if operation_name not in self.performance_tracking:
            self.warning(f"Performance tracking not started for: {operation_name}")
            return
        
        tracking_data = self.performance_tracking[operation_name]
        duration = time.time() - tracking_data["start_time"]
        
        self.debug(f"Performance: {operation_name} took {duration:.4f}s (call #{tracking_data['call_count']})")
        
        # Store historical data
        if "history" not in tracking_data:
            tracking_data["history"] = []
        
        tracking_data["history"].append(duration)
        
        # Keep only last 100 measurements
        if len(tracking_data["history"]) > 100:
            tracking_data["history"] = tracking_data["history"][-100:]
    
    def get_performance_stats(self, operation_name):
        """Get performance statistics for an operation."""
        
        if operation_name not in self.performance_tracking:
            return None
        
        tracking_data = self.performance_tracking[operation_name]
        history = tracking_data.get("history", [])
        
        if not history:
            return None
        
        return {
            "call_count": tracking_data["call_count"],
            "average_time": sum(history) / len(history),
            "min_time": min(history),
            "max_time": max(history),
            "recent_calls": len(history)
        }
    
    def dump_debug_info(self, character=None):
        """Dump comprehensive debug information."""
        
        debug_info = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "log_level": self.current_log_level,
            "recent_logs": self.log_history[-50:],  # Last 50 entries
            "performance_stats": {}
        }
        
        # Add performance stats
        for op_name in self.performance_tracking:
            stats = self.get_performance_stats(op_name)
            if stats:
                debug_info["performance_stats"][op_name] = stats
        
        # Save to auxiliary data if character provided
        if character:
            auxiliary.charSetAuxiliaryData(character, "debug_dump", json.dumps(debug_info))
        
        return debug_info

# Global debug logger
debug_logger = DebugLogger()

def debug_function(func):
    """Decorator to add debug logging to functions."""
    
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        debug_logger.debug(f"Entering function: {func_name}")
        debug_logger.start_performance_tracking(func_name)
        
        try:
            result = func(*args, **kwargs)
            debug_logger.debug(f"Function {func_name} completed successfully")
            return result
        except Exception as e:
            debug_logger.log_exception(e, f"Function: {func_name}")
            raise
        finally:
            debug_logger.end_performance_tracking(func_name)
    
    return wrapper

def safe_execute(func, *args, **kwargs):
    """Safely execute a function with error handling."""
    
    try:
        return func(*args, **kwargs)
    except Exception as e:
        debug_logger.log_exception(e, f"Safe execution of {func.__name__}")
        return None
```

### Auxiliary Data Debugging

```python
# File: lib/pymodules/aux_data_debug.py

import auxiliary
import json
import char
import room
import obj

class AuxiliaryDataDebugger:
    """Tools for debugging auxiliary data issues."""
    
    def __init__(self):
        self.data_validators = {}
        self.access_log = []
    
    def validate_aux_data(self, target, key, expected_schema=None):
        """Validate auxiliary data structure and content."""
        
        # Get the data
        data_str = self.get_aux_data_safe(target, key)
        
        if not data_str:
            return {
                "valid": False,
                "error": "No data found",
                "data": None
            }
        
        # Try to parse JSON
        try:
            data = json.loads(data_str)
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "error": f"Invalid JSON: {str(e)}",
                "data": data_str
            }
        
        # Schema validation if provided
        if expected_schema:
            schema_errors = self.validate_against_schema(data, expected_schema)
            if schema_errors:
                return {
                    "valid": False,
                    "error": f"Schema validation failed: {'; '.join(schema_errors)}",
                    "data": data
                }
        
        return {
            "valid": True,
            "error": None,
            "data": data
        }
    
    def get_aux_data_safe(self, target, key):
        """Safely get auxiliary data with error handling."""
        
        try:
            if hasattr(target, 'charGetAuxiliaryData'):
                return auxiliary.charGetAuxiliaryData(target, key)
            elif hasattr(target, 'roomGetAuxiliaryData'):
                return auxiliary.roomGetAuxiliaryData(target, key)
            elif hasattr(target, 'objGetAuxiliaryData'):
                return auxiliary.objGetAuxiliaryData(target, key)
            else:
                return auxiliary.worldGetAuxiliaryData(key)
        except Exception as e:
            debug_logger.error(f"Error getting auxiliary data: {str(e)}")
            return None
    
    def validate_against_schema(self, data, schema):
        """Basic schema validation."""
        
        errors = []
        
        # Check required fields
        if "required" in schema:
            for field in schema["required"]:
                if field not in data:
                    errors.append(f"Missing required field: {field}")
        
        # Check field types
        if "properties" in schema:
            for field, field_schema in schema["properties"].items():
                if field in data:
                    expected_type = field_schema.get("type")
                    actual_value = data[field]
                    
                    if expected_type == "string" and not isinstance(actual_value, str):
                        errors.append(f"Field {field} should be string, got {type(actual_value).__name__}")
                    elif expected_type == "number" and not isinstance(actual_value, (int, float)):
                        errors.append(f"Field {field} should be number, got {type(actual_value).__name__}")
                    elif expected_type == "array" and not isinstance(actual_value, list):
                        errors.append(f"Field {field} should be array, got {type(actual_value).__name__}")
                    elif expected_type == "object" and not isinstance(actual_value, dict):
                        errors.append(f"Field {field} should be object, got {type(actual_value).__name__}")
        
        return errors
    
    def diagnose_aux_data_issues(self, target, key):
        """Comprehensive diagnosis of auxiliary data issues."""
        
        diagnosis = {
            "target_type": self.get_target_type(target),
            "key": key,
            "issues": [],
            "recommendations": []
        }
        
        # Check if data exists
        data_str = self.get_aux_data_safe(target, key)
        
        if not data_str:
            diagnosis["issues"].append("No auxiliary data found")
            diagnosis["recommendations"].append("Ensure data is being set before retrieval")
            return diagnosis
        
        # Check JSON validity
        try:
            data = json.loads(data_str)
            diagnosis["data_size"] = len(data_str)
            diagnosis["data_type"] = type(data).__name__
        except json.JSONDecodeError as e:
            diagnosis["issues"].append(f"Invalid JSON format: {str(e)}")
            diagnosis["recommendations"].append("Check for malformed JSON strings")
            diagnosis["raw_data"] = data_str[:200] + "..." if len(data_str) > 200 else data_str
            return diagnosis
        
        # Check for common issues
        if isinstance(data, dict):
            # Check for deeply nested structures
            max_depth = self.calculate_dict_depth(data)
            if max_depth > 5:
                diagnosis["issues"].append(f"Very deep nesting (depth: {max_depth})")
                diagnosis["recommendations"].append("Consider flattening data structure")
            
            # Check for large arrays
            for field, value in data.items():
                if isinstance(value, list) and len(value) > 100:
                    diagnosis["issues"].append(f"Large array in field '{field}': {len(value)} items")
                    diagnosis["recommendations"].append(f"Consider paginating or limiting array size in '{field}'")
        
        # Check data size
        if len(data_str) > 10000:  # 10KB
            diagnosis["issues"].append(f"Large data size: {len(data_str)} bytes")
            diagnosis["recommendations"].append("Consider splitting data or using references")
        
        return diagnosis
    
    def get_target_type(self, target):
        """Determine the type of target object."""
        
        if hasattr(target, 'charGetName'):
            return "character"
        elif hasattr(target, 'roomGetKey'):
            return "room"
        elif hasattr(target, 'objGetKeywords'):
            return "object"
        else:
            return "world"
    
    def calculate_dict_depth(self, d, current_depth=0):
        """Calculate maximum depth of nested dictionary."""
        
        if not isinstance(d, dict):
            return current_depth
        
        if not d:
            return current_depth
        
        return max(self.calculate_dict_depth(v, current_depth + 1) for v in d.values())
    
    def log_aux_data_access(self, target, key, operation, success=True):
        """Log auxiliary data access for debugging."""
        
        log_entry = {
            "timestamp": time.time(),
            "target_type": self.get_target_type(target),
            "target_id": self.get_target_id(target),
            "key": key,
            "operation": operation,
            "success": success
        }
        
        self.access_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.access_log) > 1000:
            self.access_log = self.access_log[-1000:]
    
    def get_target_id(self, target):
        """Get a unique identifier for the target."""
        
        try:
            if hasattr(target, 'charGetName'):
                return char.charGetName(target)
            elif hasattr(target, 'roomGetKey'):
                return room.roomGetKey(target)
            elif hasattr(target, 'objGetKeywords'):
                return obj.objGetKeywords(target)
            else:
                return "world"
        except:
            return "unknown"

# Global auxiliary data debugger
aux_debugger = AuxiliaryDataDebugger()
```

## Common Issues and Solutions

### Issue 1: Auxiliary Data Corruption

```python
# Common auxiliary data corruption patterns and fixes

def fix_corrupted_aux_data(target, key, backup_data=None):
    """Attempt to fix corrupted auxiliary data."""
    
    debug_logger.info(f"Attempting to fix corrupted auxiliary data: {key}")
    
    # Get current data
    current_data = aux_debugger.get_aux_data_safe(target, key)
    
    if not current_data:
        debug_logger.warning(f"No data found for key: {key}")
        if backup_data:
            # Restore from backup
            aux_debugger.set_aux_data_safe(target, key, json.dumps(backup_data))
            debug_logger.info(f"Restored data from backup for key: {key}")
            return True
        return False
    
    # Try to parse and fix common issues
    try:
        data = json.loads(current_data)
        debug_logger.info(f"Data is valid JSON for key: {key}")
        return True
    except json.JSONDecodeError as e:
        debug_logger.error(f"JSON decode error for key {key}: {str(e)}")
        
        # Attempt common fixes
        fixed_data = attempt_json_fixes(current_data)
        
        if fixed_data:
            aux_debugger.set_aux_data_safe(target, key, fixed_data)
            debug_logger.info(f"Applied JSON fixes for key: {key}")
            return True
        
        # If all else fails, use backup
        if backup_data:
            aux_debugger.set_aux_data_safe(target, key, json.dumps(backup_data))
            debug_logger.info(f"Restored from backup after failed fixes for key: {key}")
            return True
    
    return False

def attempt_json_fixes(json_string):
    """Attempt to fix common JSON formatting issues."""
    
    fixes_applied = []
    
    # Fix 1: Remove trailing commas
    import re
    fixed = re.sub(r',(\s*[}\]])', r'\1', json_string)
    if fixed != json_string:
        fixes_applied.append("removed trailing commas")
        json_string = fixed
    
    # Fix 2: Fix single quotes to double quotes
    fixed = json_string.replace("'", '"')
    if fixed != json_string:
        fixes_applied.append("converted single quotes to double quotes")
        json_string = fixed
    
    # Fix 3: Remove control characters
    fixed = ''.join(char for char in json_string if ord(char) >= 32 or char in '\t\n\r')
    if fixed != json_string:
        fixes_applied.append("removed control characters")
        json_string = fixed
    
    # Test if fixes worked
    try:
        json.loads(json_string)
        debug_logger.info(f"JSON fixes successful: {', '.join(fixes_applied)}")
        return json_string
    except json.JSONDecodeError:
        debug_logger.error(f"JSON fixes failed: {', '.join(fixes_applied)}")
        return None
```

### Issue 2: Performance Problems

```python
# Performance debugging and optimization tools

class PerformanceProfiler:
    """Profile performance of NakedMud operations."""
    
    def __init__(self):
        self.profiles = {}
        self.active_profiles = {}
    
    def start_profile(self, profile_name):
        """Start profiling an operation."""
        
        self.active_profiles[profile_name] = {
            "start_time": time.time(),
            "start_memory": self.get_memory_usage(),
            "operations": []
        }
    
    def add_operation(self, profile_name, operation_name, duration=None):
        """Add an operation to the current profile."""
        
        if profile_name not in self.active_profiles:
            return
        
        operation_data = {
            "name": operation_name,
            "timestamp": time.time(),
            "duration": duration
        }
        
        self.active_profiles[profile_name]["operations"].append(operation_data)
    
    def end_profile(self, profile_name):
        """End profiling and store results."""
        
        if profile_name not in self.active_profiles:
            return None
        
        profile_data = self.active_profiles[profile_name]
        end_time = time.time()
        end_memory = self.get_memory_usage()
        
        result = {
            "total_duration": end_time - profile_data["start_time"],
            "memory_delta": end_memory - profile_data["start_memory"],
            "operation_count": len(profile_data["operations"]),
            "operations": profile_data["operations"]
        }
        
        # Store in profiles history
        if profile_name not in self.profiles:
            self.profiles[profile_name] = []
        
        self.profiles[profile_name].append(result)
        
        # Clean up active profile
        del self.active_profiles[profile_name]
        
        return result
    
    def get_memory_usage(self):
        """Get current memory usage (simplified)."""
        # This is a placeholder - actual implementation would depend on system
        return 0
    
    def analyze_performance(self, profile_name, threshold_ms=100):
        """Analyze performance data for bottlenecks."""
        
        if profile_name not in self.profiles:
            return None
        
        recent_profiles = self.profiles[profile_name][-10:]  # Last 10 runs
        
        analysis = {
            "average_duration": sum(p["total_duration"] for p in recent_profiles) / len(recent_profiles),
            "max_duration": max(p["total_duration"] for p in recent_profiles),
            "min_duration": min(p["total_duration"] for p in recent_profiles),
            "slow_operations": [],
            "recommendations": []
        }
        
        # Find slow operations
        threshold_seconds = threshold_ms / 1000.0
        
        for profile in recent_profiles:
            for op in profile["operations"]:
                if op.get("duration", 0) > threshold_seconds:
                    analysis["slow_operations"].append({
                        "name": op["name"],
                        "duration": op["duration"],
                        "timestamp": op["timestamp"]
                    })
        
        # Generate recommendations
        if analysis["average_duration"] > 1.0:  # More than 1 second
            analysis["recommendations"].append("Consider optimizing overall algorithm")
        
        if len(analysis["slow_operations"]) > 0:
            analysis["recommendations"].append("Focus on optimizing slow operations")
        
        return analysis

# Global performance profiler
performance_profiler = PerformanceProfiler()

def profile_function(profile_name):
    """Decorator to profile function performance."""
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            operation_name = f"{func.__name__}"
            
            # Start timing
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Record operation
                duration = time.time() - start_time
                performance_profiler.add_operation(profile_name, operation_name, duration)
        
        return wrapper
    return decorator

# Example usage
@profile_function("character_creation")
def create_character_with_profiling(character_data):
    """Example of profiled character creation."""
    
    performance_profiler.start_profile("character_creation")
    
    try:
        # Character creation steps
        setup_base_character(character_data)
        apply_character_class(character_data)
        initialize_skills(character_data)
        setup_starting_equipment(character_data)
        
        return True
    finally:
        profile_result = performance_profiler.end_profile("character_creation")
        debug_logger.info(f"Character creation took {profile_result['total_duration']:.3f}s")
```

### Issue 3: Memory Leaks and Resource Management

```python
# Memory leak detection and resource management

class ResourceTracker:
    """Track resource usage and detect potential leaks."""
    
    def __init__(self):
        self.tracked_resources = {}
        self.resource_history = []
        self.leak_thresholds = {
            "auxiliary_data": 1000,  # Max aux data entries per object
            "event_handlers": 100,   # Max event handlers
            "cached_objects": 500    # Max cached objects
        }
    
    def track_resource(self, resource_type, resource_id, size=1):
        """Track a resource allocation."""
        
        if resource_type not in self.tracked_resources:
            self.tracked_resources[resource_type] = {}
        
        self.tracked_resources[resource_type][resource_id] = {
            "size": size,
            "allocated_time": time.time(),
            "access_count": 0
        }
    
    def untrack_resource(self, resource_type, resource_id):
        """Untrack a resource (when freed)."""
        
        if resource_type in self.tracked_resources:
            if resource_id in self.tracked_resources[resource_type]:
                del self.tracked_resources[resource_type][resource_id]
    
    def access_resource(self, resource_type, resource_id):
        """Record resource access."""
        
        if resource_type in self.tracked_resources:
            if resource_id in self.tracked_resources[resource_type]:
                self.tracked_resources[resource_type][resource_id]["access_count"] += 1
    
    def detect_leaks(self):
        """Detect potential memory leaks."""
        
        leaks = []
        current_time = time.time()
        
        for resource_type, resources in self.tracked_resources.items():
            threshold = self.leak_thresholds.get(resource_type, 100)
            
            if len(resources) > threshold:
                leaks.append({
                    "type": "count_threshold",
                    "resource_type": resource_type,
                    "count": len(resources),
                    "threshold": threshold
                })
            
            # Check for old, unused resources
            for resource_id, resource_data in resources.items():
                age = current_time - resource_data["allocated_time"]
                access_count = resource_data["access_count"]
                
                # Resource older than 1 hour with no access
                if age > 3600 and access_count == 0:
                    leaks.append({
                        "type": "unused_resource",
                        "resource_type": resource_type,
                        "resource_id": resource_id,
                        "age": age,
                        "access_count": access_count
                    })
        
        return leaks
    
    def cleanup_unused_resources(self, max_age=3600):
        """Clean up unused resources older than max_age seconds."""
        
        current_time = time.time()
        cleaned_count = 0
        
        for resource_type, resources in self.tracked_resources.items():
            to_remove = []
            
            for resource_id, resource_data in resources.items():
                age = current_time - resource_data["allocated_time"]
                access_count = resource_data["access_count"]
                
                if age > max_age and access_count == 0:
                    to_remove.append(resource_id)
            
            for resource_id in to_remove:
                del resources[resource_id]
                cleaned_count += 1
        
        debug_logger.info(f"Cleaned up {cleaned_count} unused resources")
        return cleaned_count
    
    def get_resource_stats(self):
        """Get comprehensive resource usage statistics."""
        
        stats = {}
        
        for resource_type, resources in self.tracked_resources.items():
            total_size = sum(r["size"] for r in resources.values())
            total_accesses = sum(r["access_count"] for r in resources.values())
            
            stats[resource_type] = {
                "count": len(resources),
                "total_size": total_size,
                "total_accesses": total_accesses,
                "average_size": total_size / len(resources) if resources else 0,
                "average_accesses": total_accesses / len(resources) if resources else 0
            }
        
        return stats

# Global resource tracker
resource_tracker = ResourceTracker()
```

## Advanced Debugging Techniques

### Debugging Complex State Machines

```python
# State machine debugging tools

class StateMachineDebugger:
    """Debug complex state machines and behavior trees."""
    
    def __init__(self):
        self.state_history = {}
        self.transition_log = {}
        self.state_validators = {}
    
    def log_state_transition(self, entity_id, old_state, new_state, trigger=None):
        """Log a state transition."""
        
        if entity_id not in self.state_history:
            self.state_history[entity_id] = []
        
        transition = {
            "timestamp": time.time(),
            "old_state": old_state,
            "new_state": new_state,
            "trigger": trigger
        }
        
        self.state_history[entity_id].append(transition)
        
        # Keep only last 100 transitions per entity
        if len(self.state_history[entity_id]) > 100:
            self.state_history[entity_id] = self.state_history[entity_id][-100:]
        
        debug_logger.debug(f"State transition: {entity_id} {old_state} -> {new_state} (trigger: {trigger})")
    
    def validate_state_transition(self, entity_id, old_state, new_state):
        """Validate if a state transition is legal."""
        
        if entity_id in self.state_validators:
            validator = self.state_validators[entity_id]
            
            if old_state in validator:
                valid_transitions = validator[old_state]
                
                if new_state not in valid_transitions:
                    debug_logger.warning(f"Invalid state transition: {entity_id} {old_state} -> {new_state}")
                    return False
        
        return True
    
    def register_state_validator(self, entity_id, state_transitions):
        """Register valid state transitions for an entity."""
        
        self.state_validators[entity_id] = state_transitions
    
    def analyze_state_patterns(self, entity_id):
        """Analyze state transition patterns for anomalies."""
        
        if entity_id not in self.state_history:
            return None
        
        history = self.state_history[entity_id]
        
        if len(history) < 2:
            return None
        
        analysis = {
            "total_transitions": len(history),
            "unique_states": set(),
            "transition_frequency": {},
            "rapid_transitions": [],
            "stuck_states": [],
            "anomalies": []
        }
        
        # Analyze transitions
        for i, transition in enumerate(history):
            analysis["unique_states"].add(transition["old_state"])
            analysis["unique_states"].add(transition["new_state"])
            
            transition_key = f"{transition['old_state']} -> {transition['new_state']}"
            
            if transition_key not in analysis["transition_frequency"]:
                analysis["transition_frequency"][transition_key] = 0
            
            analysis["transition_frequency"][transition_key] += 1
            
            # Check for rapid transitions (multiple transitions in short time)
            if i > 0:
                time_diff = transition["timestamp"] - history[i-1]["timestamp"]
                if time_diff < 1.0:  # Less than 1 second
                    analysis["rapid_transitions"].append({
                        "transition": transition_key,
                        "time_diff": time_diff,
                        "timestamp": transition["timestamp"]
                    })
        
        # Check for stuck states (same state for long periods)
        current_state = None
        state_start_time = None
        
        for transition in history:
            if current_state != transition["new_state"]:
                if current_state and state_start_time:
                    duration = transition["timestamp"] - state_start_time
                    if duration > 300:  # More than 5 minutes
                        analysis["stuck_states"].append({
                            "state": current_state,
                            "duration": duration,
                            "start_time": state_start_time
                        })
                
                current_state = transition["new_state"]
                state_start_time = transition["timestamp"]
        
        return analysis

# Global state machine debugger
state_debugger = StateMachineDebugger()
```

### Interactive Debugging Commands

```python
# Interactive debugging commands for wizards

def cmd_debug_info(ch, cmd, arg):
    """Display comprehensive debug information."""
    
    if not arg:
        char.charSend(ch, "Usage: debug_info <target> [key]")
        return
    
    parts = arg.split()
    target_name = parts[0]
    key = parts[1] if len(parts) > 1 else None
    
    # Find target
    target = char.charGetCharInRoom(ch, target_name)
    if not target:
        target = room.roomGetRoom(ch, target_name)
    
    if not target:
        char.charSend(ch, f"Target '{target_name}' not found.")
        return
    
    if key:
        # Debug specific auxiliary data key
        diagnosis = aux_debugger.diagnose_aux_data_issues(target, key)
        
        char.charSend(ch, f"=== Debug Info for {target_name}.{key} ===")
        char.charSend(ch, f"Target Type: {diagnosis['target_type']}")
        
        if diagnosis["issues"]:
            char.charSend(ch, "Issues Found:")
            for issue in diagnosis["issues"]:
                char.charSend(ch, f"  - {issue}")
        else:
            char.charSend(ch, "No issues found.")
        
        if diagnosis["recommendations"]:
            char.charSend(ch, "Recommendations:")
            for rec in diagnosis["recommendations"]:
                char.charSend(ch, f"  - {rec}")
    else:
        # General debug info
        debug_info = debug_logger.dump_debug_info(ch)
        
        char.charSend(ch, f"=== Debug Info for {target_name} ===")
        char.charSend(ch, f"Recent log entries: {len(debug_info['recent_logs'])}")
        char.charSend(ch, f"Performance stats available for: {len(debug_info['performance_stats'])} operations")
        
        # Show performance stats
        for op_name, stats in debug_info["performance_stats"].items():
            char.charSend(ch, f"  {op_name}: avg {stats['average_time']:.3f}s ({stats['call_count']} calls)")

def cmd_debug_performance(ch, cmd, arg):
    """Display performance analysis."""
    
    if not arg:
        # Show all tracked operations
        stats = {}
        for op_name in performance_profiler.profiles:
            analysis = performance_profiler.analyze_performance(op_name)
            if analysis:
                stats[op_name] = analysis
        
        char.charSend(ch, "=== Performance Analysis ===")
        for op_name, analysis in stats.items():
            char.charSend(ch, f"{op_name}:")
            char.charSend(ch, f"  Average: {analysis['average_duration']:.3f}s")
            char.charSend(ch, f"  Range: {analysis['min_duration']:.3f}s - {analysis['max_duration']:.3f}s")
            char.charSend(ch, f"  Slow operations: {len(analysis['slow_operations'])}")
    else:
        # Show specific operation analysis
        analysis = performance_profiler.analyze_performance(arg)
        
        if not analysis:
            char.charSend(ch, f"No performance data found for '{arg}'")
            return
        
        char.charSend(ch, f"=== Performance Analysis: {arg} ===")
        char.charSend(ch, f"Average Duration: {analysis['average_duration']:.3f}s")
        char.charSend(ch, f"Min Duration: {analysis['min_duration']:.3f}s")
        char.charSend(ch, f"Max Duration: {analysis['max_duration']:.3f}s")
        
        if analysis["slow_operations"]:
            char.charSend(ch, "Slow Operations:")
            for op in analysis["slow_operations"][-5:]:  # Last 5
                char.charSend(ch, f"  {op['name']}: {op['duration']:.3f}s")
        
        if analysis["recommendations"]:
            char.charSend(ch, "Recommendations:")
            for rec in analysis["recommendations"]:
                char.charSend(ch, f"  - {rec}")

def cmd_debug_memory(ch, cmd, arg):
    """Display memory usage and leak detection."""
    
    # Run leak detection
    leaks = resource_tracker.detect_leaks()
    stats = resource_tracker.get_resource_stats()
    
    char.charSend(ch, "=== Memory Usage Analysis ===")
    
    # Show resource stats
    for resource_type, stat_data in stats.items():
        char.charSend(ch, f"{resource_type}:")
        char.charSend(ch, f"  Count: {stat_data['count']}")
        char.charSend(ch, f"  Total Size: {stat_data['total_size']}")
        char.charSend(ch, f"  Average Size: {stat_data['average_size']:.2f}")
        char.charSend(ch, f"  Total Accesses: {stat_data['total_accesses']}")
    
    # Show potential leaks
    if leaks:
        char.charSend(ch, "\\nPotential Memory Leaks:")
        for leak in leaks:
            if leak["type"] == "count_threshold":
                char.charSend(ch, f"  {leak['resource_type']}: {leak['count']} items (threshold: {leak['threshold']})")
            elif leak["type"] == "unused_resource":
                char.charSend(ch, f"  Unused {leak['resource_type']}: {leak['resource_id']} (age: {leak['age']:.0f}s)")
    else:
        char.charSend(ch, "\\nNo memory leaks detected.")

# Register debug commands
mudsys.add_cmd("debug_info", None, cmd_debug_info, "wizard", 1)
mudsys.add_cmd("debug_performance", None, cmd_debug_performance, "wizard", 1)
mudsys.add_cmd("debug_memory", None, cmd_debug_memory, "wizard", 1)
```

## Best Practices for Debugging

### 1. Defensive Programming

```python
# Always validate inputs and handle edge cases

def safe_get_character_data(character, data_key, default=None):
    """Safely get character data with comprehensive error handling."""
    
    if not character:
        debug_logger.warning("safe_get_character_data called with None character")
        return default
    
    try:
        data_str = auxiliary.charGetAuxiliaryData(character, data_key)
        
        if not data_str:
            debug_logger.debug(f"No data found for key: {data_key}")
            return default
        
        data = json.loads(data_str)
        return data
        
    except json.JSONDecodeError as e:
        debug_logger.error(f"JSON decode error for key {data_key}: {str(e)}")
        return default
    except Exception as e:
        debug_logger.error(f"Unexpected error getting character data: {str(e)}")
        return default

def validate_character_stats(stats_data):
    """Validate character stats data structure."""
    
    required_fields = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
    
    if not isinstance(stats_data, dict):
        return False, "Stats data must be a dictionary"
    
    for field in required_fields:
        if field not in stats_data:
            return False, f"Missing required field: {field}"
        
        if not isinstance(stats_data[field], int):
            return False, f"Field {field} must be an integer"
        
        if stats_data[field] < 1 or stats_data[field] > 100:
            return False, f"Field {field} must be between 1 and 100"
    
    return True, "Valid"
```

### 2. Comprehensive Logging

```python
# Log important events and state changes

def log_important_event(event_type, details, severity="INFO"):
    """Log important game events for debugging."""
    
    event_data = {
        "event_type": event_type,
        "timestamp": time.time(),
        "details": details,
        "severity": severity
    }
    
    debug_logger.log(severity, f"Event: {event_type}", event_data)
    
    # Store in world auxiliary data for persistence
    events_str = auxiliary.worldGetAuxiliaryData("important_events")
    
    if events_str:
        try:
            events = json.loads(events_str)
        except json.JSONDecodeError:
            events = []
    else:
        events = []
    
    events.append(event_data)
    
    # Keep only last 1000 events
    if len(events) > 1000:
        events = events[-1000:]
    
    auxiliary.worldSetAuxiliaryData("important_events", json.dumps(events))
```

### 3. Testing and Validation

```python
# Create comprehensive test suites

def run_system_tests():
    """Run comprehensive system tests."""
    
    test_results = {
        "passed": 0,
        "failed": 0,
        "errors": []
    }
    
    # Test auxiliary data system
    try:
        test_aux_data_system()
        test_results["passed"] += 1
    except Exception as e:
        test_results["failed"] += 1
        test_results["errors"].append(f"Auxiliary data test failed: {str(e)}")
    
    # Test prototype system
    try:
        test_prototype_system()
        test_results["passed"] += 1
    except Exception as e:
        test_results["failed"] += 1
        test_results["errors"].append(f"Prototype test failed: {str(e)}")
    
    # Test performance
    try:
        test_performance_benchmarks()
        test_results["passed"] += 1
    except Exception as e:
        test_results["failed"] += 1
        test_results["errors"].append(f"Performance test failed: {str(e)}")
    
    return test_results

def test_aux_data_system():
    """Test auxiliary data system functionality."""
    
    # Create test data
    test_data = {"test_field": "test_value", "number": 42}
    
    # Test world auxiliary data
    auxiliary.worldSetAuxiliaryData("test_key", json.dumps(test_data))
    retrieved = auxiliary.worldGetAuxiliaryData("test_key")
    
    if not retrieved:
        raise Exception("Failed to retrieve world auxiliary data")
    
    parsed = json.loads(retrieved)
    
    if parsed != test_data:
        raise Exception("Retrieved data doesn't match stored data")
    
    debug_logger.info("Auxiliary data system test passed")
```

## Summary

This comprehensive debugging guide covers:

1. **Debug Infrastructure** - Logging, profiling, and monitoring systems
2. **Common Issues** - Data corruption, performance problems, memory leaks
3. **Advanced Techniques** - State machine debugging, resource tracking
4. **Interactive Tools** - Wizard commands for real-time debugging
5. **Best Practices** - Defensive programming, comprehensive logging, testing

Master these techniques to build robust, maintainable NakedMud systems that are easy to debug and optimize.

## Next Steps

- Apply these debugging techniques to your existing systems
- Set up comprehensive logging in your development environment
- Create test suites for your custom systems
- Use performance profiling to optimize critical code paths