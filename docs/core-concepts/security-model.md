---
title: Security Model
layout: default
nav_order: 4
parent: Core Concepts
description: "Understanding NakedMud's Python security and restricted execution"
---

# Security Model

NakedMud implements a comprehensive security model to ensure that Python scripts can provide rich functionality while protecting the underlying system from malicious or dangerous code. This security model is essential for allowing user-generated content and maintaining system stability.

## Security Philosophy

The security model is built on the principle of **least privilege**: scripts have access to exactly what they need to accomplish their purpose, and no more. This approach provides:

- **Protection**: System resources are protected from abuse
- **Isolation**: Scripts cannot interfere with each other or core systems
- **Stability**: Malicious or buggy scripts cannot crash the MUD
- **Trust**: Administrators can safely allow user-contributed content

## Restricted Execution Environment

All Python scripts in NakedMud run in a restricted execution environment that limits access to potentially dangerous functionality.

### Restricted Builtins

The standard Python builtins are replaced with restricted versions:

```python
# Standard Python builtins are replaced with safe versions
# Located in: lib/pymodules/__restricted_builtin__.py

# Dangerous functions are disabled or restricted:
__import__ = r_import    # Only allows specific modules
open = r_open           # Read-only file access only
eval = r_eval           # Completely disabled
exec = r_exec           # Completely disabled
execfile = r_execfile   # Completely disabled
reload = r_reload       # Completely disabled
```

### Import Restrictions

Only specific, vetted modules can be imported:

```python
# Allowed modules (from __restricted_builtin_funcs__.py)
ok_modules = (
    "mud", "obj", "char", "room", "exit", "account", "mudsock",
    "event", "action", "random", "traceback", "utils",
    "__restricted_builtin__"
)

# Example of what happens with restricted imports:
import mud      # ✓ Allowed - MUD functionality
import random   # ✓ Allowed - Safe randomization
import os       # ✗ Blocked - System access
import socket   # ✗ Blocked - Network access
```

### File System Protection

File system access is heavily restricted:

```python
def r_open(file, mode="r", buf=-1):
    # Only read and read-binary modes allowed
    if mode not in ('r', 'rb'):
        raise IOError("can't open files for writing in restricted mode")
    return open(file, mode, buf)

# Examples:
open("data.txt", "r")    # ✓ Allowed - read access
open("log.txt", "w")     # ✗ Blocked - write access
open("config.txt", "a")  # ✗ Blocked - append access
```

### Code Execution Prevention

Dynamic code execution is completely disabled:

```python
# All of these raise NotImplementedError:
eval("1 + 1")                    # ✗ Blocked
exec("print('hello')")           # ✗ Blocked
execfile("script.py")            # ✗ Blocked
compile("code", "file", "exec")  # ✗ Blocked
```

## Execution Safeguards

Beyond restricting access, NakedMud implements several safeguards to prevent abuse:

### Loop Depth Protection

Prevents infinite recursion in script calls:

```c
#define MAX_LOOP_DEPTH 30
int script_loop_depth = 0;

// Before each script execution:
if(script_loop_depth >= MAX_LOOP_DEPTH) {
    script_ok = FALSE;
    // Script execution is terminated
    return;
}
```

This prevents scenarios like:
```python
# Trigger A calls Trigger B, which calls Trigger A, etc.
# After 30 levels deep, execution stops
```

### Error Isolation

Script errors are contained and logged without affecting the MUD:

```c
// All script execution is wrapped in error handling
PyObject *retval = PyEval_EvalCode(code, dict, dict);
if(retval == NULL && PyErr_Occurred() != PyExc_SystemExit) {
    script_ok = FALSE;
    log_pyerr("Script terminated with an error: %s", script);
    // MUD continues running normally
}
```

### Memory Management

Python objects are carefully managed to prevent memory leaks:

```c
// Reference counting ensures proper cleanup
Py_INCREF(obj);        // Increment when storing
Py_DECREF(obj);        // Decrement when done
Py_XDECREF(obj);       // Safe decrement (handles NULL)

// Borrowed references avoid unnecessary counting
PyObject *borrowed = charGetPyFormBorrowed(ch);
// No need to decrement borrowed references
```

## Security Boundaries

The security model establishes clear boundaries between different privilege levels:

### User Scripts (Highest Restriction)
- Prototype scripts
- Trigger scripts  
- Dynamic descriptions
- User-contributed content

**Restrictions:**
- Restricted builtin modules only
- No file system write access
- No network access
- No system module imports
- Loop depth limits
- Memory usage monitoring

### System Scripts (Medium Restriction)
- Core module initialization
- Administrative commands
- System maintenance scripts

**Additional Access:**
- Some system modules (with care)
- Limited file system access
- Extended execution time

### Core C Code (No Restrictions)
- Game engine
- Network handling
- File I/O operations
- System integration

**Full Access:**
- All system resources
- Direct hardware access
- Unrestricted operations

## Threat Model

The security model protects against several categories of threats:

### Malicious Scripts
**Threat:** Intentionally harmful code trying to damage the system
**Protection:** 
- Import restrictions prevent system access
- File system restrictions prevent data corruption
- Execution limits prevent resource exhaustion

### Buggy Scripts
**Threat:** Unintentionally harmful code with programming errors
**Protection:**
- Error isolation prevents crashes
- Loop detection prevents infinite loops
- Memory management prevents leaks

### Resource Abuse
**Threat:** Scripts consuming excessive system resources
**Protection:**
- Execution time limits
- Memory usage monitoring
- Loop depth restrictions
- Import limitations

### Information Disclosure
**Threat:** Scripts accessing sensitive information
**Protection:**
- File system read restrictions
- Module import limitations
- Isolated execution environments

## Security Best Practices

### For Script Writers

1. **Validate Input**: Always check user input before processing
```python
def handle_command(ch, arg):
    if not arg or len(arg) == 0:
        ch.send("Please provide an argument.")
        return
    # Process validated input
```

2. **Handle Errors Gracefully**: Use try/except for robust error handling
```python
try:
    target = ch.room.get_char(arg)
    target.send("Hello!")
except:
    ch.send("Could not find that person.")
```

3. **Limit Resource Usage**: Be mindful of loops and object creation
```python
# Good: Limited loop
for i in range(min(count, 100)):
    create_object()

# Bad: Unlimited loop
while True:
    create_object()  # Could run forever
```

### For Administrators

1. **Review User Scripts**: Examine user-contributed content before installation
2. **Monitor Logs**: Watch for security violations and errors
3. **Update Regularly**: Keep the security model current with new threats
4. **Test Thoroughly**: Verify scripts work correctly in restricted environment

### For Developers

1. **Principle of Least Privilege**: Only expose necessary functionality
2. **Input Sanitization**: Validate all data crossing C/Python boundary
3. **Error Handling**: Ensure C code handles Python errors gracefully
4. **Security Reviews**: Regularly audit exposed functionality

## Security Configuration

### Customizing Restrictions

Administrators can customize the security model:

```python
# In __restricted_builtin_funcs__.py
ok_modules = (
    "mud", "char", "room", "obj",  # Core modules
    "custom_module",               # Add custom modules
    # "dangerous_module",          # Comment out to disable
)
```

### Monitoring and Logging

Security violations are logged for analysis:

```c
// Security violations are logged
log_string("SECURITY: Attempted import of restricted module: %s", module);
log_string("SECURITY: Script exceeded loop depth limit");
log_string("SECURITY: Attempted file write in restricted mode");
```

### Emergency Procedures

In case of security issues:

1. **Immediate Response**: Disable script execution if necessary
2. **Investigation**: Analyze logs to understand the threat
3. **Containment**: Isolate affected systems
4. **Recovery**: Restore from clean backups if needed
5. **Prevention**: Update security model to prevent recurrence

## Advanced Security Features

### Sandboxing

Each script execution is sandboxed:

```c
// Create isolated dictionary for each script
PyObject *dict = restricted_script_dict();
// Script runs in isolation
run_script(dict, script_code, locale);
// Dictionary is destroyed after execution
Py_DECREF(dict);
```

### Capability-Based Security

Scripts receive only the capabilities they need:

```python
# Prototype scripts get object creation capabilities
me = load_mob("template")  # Can create objects

# Trigger scripts get event handling capabilities  
ch.send("message")         # Can send messages

# Neither gets file system access
# open("file.txt")         # Not available
```

### Audit Trail

All security-relevant operations are logged:

```c
// Function calls are logged
log_security("Script %s called function %s", script_name, func_name);

// Access attempts are logged
log_security("Script %s attempted to access %s", script_name, resource);
```

## See Also

- [Python Integration Overview](python-integration.md) - Understanding the C/Python interface
- [Scripting Best Practices](../tutorials/scripting-best-practices.md) - Safe scripting techniques
- [Administrative Guide](../tutorials/admin-guide.md) - Managing script security