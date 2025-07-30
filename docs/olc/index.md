---
layout: default
title: Online Creation (OLC)
nav_order: 4
has_children: true
permalink: /olc/
---

# Online Creation (OLC)

The Online Creation (OLC) system allows authorized users to create and modify game content directly within the MUD environment. This powerful system enables real-time content creation without requiring server restarts or file editing.

## What is OLC?

OLC stands for "Online Creation" and refers to the suite of commands and interfaces that allow builders and administrators to create, modify, and manage game content while the MUD is running. This includes:

- **Triggers and Scripts**: Python code that defines object behavior
- **Prototypes**: Templates for characters, rooms, and objects
- **Content Organization**: Managing and organizing created content
- **Real-time Testing**: Immediate testing of created content

## Key Concepts

### Triggers
Triggers are Python scripts that define how game objects respond to events. They can be attached to characters, rooms, or objects to create interactive behaviors.

### Prototypes
Prototypes are templates that define the properties and behaviors of game objects. They use inheritance to share common properties and can be instantiated multiple times.

### Security Model
OLC operations require appropriate permissions. The system includes built-in security measures to prevent unauthorized access and maintain system stability.

## Getting Started

If you're new to OLC, start with these guides:

1. **[OLC Commands](commands/)** - Learn the basic commands for content creation
2. **[Editor System](editor/)** - Understand the text editor interface
3. **[Best Practices](best-practices/)** - Follow recommended workflows and guidelines

## Quick Reference

### Essential Commands
- `tedit <trigger_name>` - Create or edit a trigger
- `attach <trigger> <target>` - Attach a trigger to an object
- `detach <trigger> <target>` - Remove a trigger from an object
- `tstat <trigger>` - View trigger information
- `tlist` - List available triggers

### Common Workflows
1. **Creating an NPC**: Create trigger → Edit behavior → Attach to character prototype
2. **Building a Room**: Create room prototype → Add triggers for interactions → Test functionality
3. **Scripting Objects**: Create object prototype → Add interaction triggers → Test behaviors

## Advanced Topics

- **[Complex Trigger Interactions](advanced/trigger-interactions/)** - Managing multiple triggers
- **[Performance Optimization](advanced/performance/)** - Writing efficient OLC code
- **[Debugging Techniques](advanced/debugging/)** - Troubleshooting OLC issues

## Reference Materials

- **[Command Reference](commands/)** - Complete command documentation
- **[Error Messages](troubleshooting/)** - Common errors and solutions
- **[Examples](examples/)** - Working code examples

## Prerequisites

To use OLC effectively, you should have:
- Basic understanding of [Python Integration](/core-concepts/python-integration/)
- Familiarity with [Prototypes](/core-concepts/prototypes/)
- Knowledge of [Auxiliary Data](/core-concepts/auxiliary-data/)
- Appropriate wizard-level permissions

## Support

If you encounter issues with OLC:
1. Check the [Troubleshooting Guide](troubleshooting/)
2. Review the [Best Practices](best-practices/)
3. Consult the [API Reference](/reference/) for function details
4. Test your code incrementally to isolate problems