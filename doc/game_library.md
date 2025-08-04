# NakedMud Game Library Guide
**Maintainer**: LimpingNinja (Kevin Morgan)

Welcome to the heart of your MUD! The `lib` directory is where all your game content lives - from the Python scripts that define how your world behaves, to the rooms and creatures that populate it. Think of it as your MUD's content management system, all organized in a friendly, logical structure.

## Table of Contents
- [Overview](#overview)
- [Python Game Logic (pymodules)](#python-game-logic-pymodules)
- [World Data](#world-data)
- [Help System](#help-system)
- [Player Data](#player-data)
- [Configuration](#configuration)
- [Getting Started](#getting-started)

## Overview

The `lib` directory contains everything that makes your MUD unique. While the C code in `src` provides the engine, the `lib` directory contains the game itself. Here's what you'll find:

```
lib/
├── pymodules/          # Python game logic and commands
├── world/              # Zones, rooms, objects, and NPCs
├── help/               # In-game help system
├── accounts/           # Player account data
├── players/            # Character save files
├── txt/                # Text files (greeting, motd, etc.)
├── logs/               # Game logs
├── misc/               # Miscellaneous data
└── muddata             # Main configuration file
```

## Python Game Logic (pymodules)

This is where the magic happens! The `pymodules` directory contains all the Python scripts that define how your MUD works. Think of these as the "rules" of your game world.

### Core Game Systems

**Command Modules:**
- `cmd_admin.py` - Administrative commands (shutdown, copyover, etc.)
- `cmd_comm.py` - Communication commands (say, tell, chat)
- `cmd_manip.py` - Object manipulation (get, drop, wear, wield)
- `cmd_misc.py` - Miscellaneous utility commands
- `cmd_inform.py` - Information commands (look, inventory, who)

**Game Systems:**
- `account_handler.py` - Login and account management
- `char_gen.py` - Character creation process
- `movement.py` - How characters move between rooms
- `inform.py` - Message formatting and display
- `display.py` - Screen formatting and layout
- `colour.py` - Color code processing

**Utilities:**
- `utils.py` - Common utility functions
- `routine.py` - Scheduled events and maintenance
- `path.py` - Pathfinding algorithms
- `history.py` - Command history tracking

### Customization Freedom

Here's the beautiful part: **you can modify any of these files** to change how your MUD works! Want to add a new command? Create a new function in the appropriate `cmd_*.py` file. Want to change how movement works? Edit `movement.py`. The Python integration makes customization incredibly flexible.

### Security Note

The `__restricted_builtin*.py` files handle Python security - they control what Python functions are available to scripts. Be careful when modifying these unless you really know what you're doing!

## World Data

The `world` directory contains all your game content - the actual "stuff" players interact with. This is typically created using NakedMud's built-in Online Creation (OLC) system rather than hand-editing files.

### Zone Structure

Each zone (area) in your MUD gets its own directory under `world/zones/`:

```
world/zones/examples/
├── zone                # Zone configuration and metadata
├── rproto/            # Room prototypes
├── mproto/            # Mobile (NPC) prototypes  
├── oproto/            # Object prototypes
├── reset/             # Reset scripts (what spawns where)
└── trigger/           # Trigger scripts (special behaviors)
```

### Understanding Prototypes

**Room Prototypes (`rproto/`):**
- Define the rooms in your world
- Include descriptions, exits, and special properties
- Example: `tavern_entrance` might be a cozy inn room

**Mobile Prototypes (`mproto/`):**
- Define NPCs (Non-Player Characters)
- Include appearance, stats, and behaviors
- Example: `gruff_man` might be a surly bartender

**Object Prototypes (`oproto/`):**
- Define items players can interact with
- Include weapons, armor, furniture, quest items
- Example: `rusty_sword` or `healing_potion`

### The OLC System

Instead of hand-editing these files, you'll typically use in-game commands:

- `redit` - Edit rooms
- `medit` - Edit mobiles/NPCs
- `oedit` - Edit objects
- `zedit` - Edit zones
- `tedit` - Edit triggers

These commands create a user-friendly interface for building your world. The OLC system generates the prototype files automatically, maintaining proper formatting and structure.

## Help System

The `help` directory uses an alphabetical filing system - help files are organized by their first letter:

```
help/
├── A/                 # Help files starting with 'A'
├── B/                 # Help files starting with 'B'
├── C/                 # Help files starting with 'C'
└── ...
```

Each help file contains:
- **Keywords**: What players type to access the help
- **Content**: The actual help text
- **Formatting**: Uses MUD color codes for readability

Players access help with commands like `help movement` or `help commands`.

## Player Data

**Accounts (`accounts/`):**
- Player account information
- Login credentials and account settings
- One account can have multiple characters

**Characters (`players/`):**
- Individual character save files
- Stats, inventory, location, and progress
- Created when players make new characters

**Important**: These directories are automatically managed by the MUD. You typically don't need to edit these files manually.

## Configuration

**`muddata` File:**
The main configuration file that controls:
- Starting room for new players
- Server port and basic settings
- World file paths
- Player UID counter (puid)

**Text Files (`txt/`):**
- `greeting` - What players see when they connect
- `motd` - Message of the day
- Other informational text

## Getting Started

### For New Builders

1. **Start with OLC**: Use the in-game building commands rather than editing files directly
2. **Explore Examples**: Look at the `examples` zone to see how things work
3. **Read Help Files**: Use `help building` and `help olc` in-game
4. **Start Small**: Create a simple room or two before building complex areas

### For Programmers

1. **Study pymodules**: Look at existing command files to understand the patterns
2. **Test Safely**: Make backups before modifying core game logic
3. **Use the Python API**: NakedMud provides extensive Python bindings for game objects
4. **Check Documentation**: See `doc/nakedmud_python.md` for Python scripting details

### Best Practices

- **Backup Everything**: Especially before major changes
- **Test Incrementally**: Make small changes and test them
- **Use Version Control**: Git is your friend for tracking changes
- **Document Custom Changes**: Leave comments for future you (and others)

## Understanding the Flow

Here's how it all works together:

1. **Player connects** → `account_handler.py` manages login
2. **Player types command** → Appropriate `cmd_*.py` file processes it
3. **Command affects world** → Changes saved to `world/` files
4. **Player needs help** → System looks up files in `help/`
5. **Player logs out** → Character saved to `players/`

## Final Thoughts

The beauty of NakedMud's library system is its flexibility. You can:

- **Modify existing systems** by editing Python modules
- **Create new content** using the OLC system
- **Add custom commands** with just a few lines of Python
- **Build complex worlds** without touching C code

Remember: the `lib` directory is *your* creative space. The C engine provides the foundation, but everything in `lib` is where you make your MUD unique and special.

Don't be afraid to experiment! With good backups, you can try new ideas and see what works. The Python integration makes it easy to add features, and the OLC system makes world-building accessible to non-programmers.

*Happy building, and welcome to the wonderful world of MUD creation!*
