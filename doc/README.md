# NakedMud Documentation

Welcome to NakedMud 4.1! This documentation directory contains everything you need to understand, compile, run, and extend your MUD server. Whether you're a complete newcomer or an experienced developer, we've got you covered.

## Quick Start

New to NakedMud? Start here:

1. **[Compiling and Running](compiling_and_running.md)** - Get your MUD server up and running
2. **[Game Library Guide](game_library.md)** - Understand how your MUD's content is organized
3. **[Credits](../CREDITS.md)** - Learn about the people who made NakedMud possible

## What is NakedMud?

NakedMud is a "content-less" MUD engine - it provides you with a solid, extensible foundation for building your own text-based multiplayer game, but without predefined content. Think of it as a blank canvas for your creativity!

**Key Features:**
- **Python Integration**: Write game logic in Python instead of hard-to-modify C code
- **Modular Design**: Everything is organized into clean, reusable components
- **Online Creation (OLC)**: Build your world from within the game itself
- **Modern Architecture**: Built for Python 3.12+ with contemporary development practices
- **Extensible**: Add new features without touching the core engine

## Documentation Guide

### Getting Started
- **[Compiling and Running](compiling_and_running.md)** - Step-by-step setup guide with friendly explanations
- **[Game Library Guide](game_library.md)** - Understanding the `lib/` directory structure and content organization

### Development
- **[C Coding Conventions](c_coding_conventions.md)** - Essential guide to NakedMud's unique coding style
- **[NakedMud Programming](nakedmud_programming.md)** - Core programming concepts and architecture
- **[Python Scripting](nakedmud_python.md)** - Complete guide to Python integration and scripting
- **[Extending NakedMud](extending_nakedmud.md)** - How to add new features and modules

### Reference
- **[Credits](../CREDITS.md)** - Acknowledgments and project history
- **[Example Code](example-py/)** - Python examples and templates
- **[Archived Documentation](archived/)** - Historical documentation and legacy guides

## Project History

NakedMud began as Geoff Hollis's personal project around 2003-2004, built on top of Brian Graversen's SocketMud. Geoff's vision was to create a MUD engine that separated the technical foundation from game content, allowing creators to focus on building worlds rather than wrestling with socket programming and low-level details.

After Geoff's passing in November 2021, development continues under Kevin Morgan (LimpingNinja) to honor his work and vision, focusing on:

- **Python 3+ Modernization**: Updated from Python 2.x to modern Python
- **Code Stabilization**: Bug fixes and improved reliability  
- **Enhanced Documentation**: Clearer guides and better organization
- **Community Support**: Maintaining the project for current and future builders

## The NakedMud Philosophy

> *"The basic idea behind NakedMud is to provide users with a solid engine for running a MUD, but without the content that goes along with it."* - Geoff Hollis

This philosophy means:

- **You control the content**: No predetermined races, classes, or storylines
- **Python handles game logic**: Write readable, maintainable game systems
- **C provides the engine**: Solid, fast core that you rarely need to touch
- **Modular everything**: Add features without breaking existing systems

## Architecture Overview

```
NakedMud Structure:
├── src/                # C engine (socket handling, core systems)
├── lib/                # Game content and Python logic
│   ├── pymodules/      # Python game systems and commands
│   ├── world/          # Zones, rooms, objects, NPCs
│   ├── help/           # In-game help system
│   └── ...
├── doc/                # This documentation
└── tests/              # Test suites and validation
```

The beauty of this design is that you can create entirely different types of games using the same engine - from traditional fantasy MUDs to sci-fi adventures to social chat environments.

## Getting Help

**Documentation Issues?** Check if there's a more specific guide for your question:
- Building problems? → [Compiling and Running](compiling_and_running.md)
- Code questions? → [C Coding Conventions](c_coding_conventions.md) or [Python Scripting](nakedmud_python.md)
- Content creation? → [Game Library Guide](game_library.md)
- Want to add features? → [Extending NakedMud](extending_nakedmud.md)

**Still stuck?** The NakedMud community is friendly and helpful. Don't hesitate to reach out!

## Contributing

NakedMud thrives on community contributions! Whether you're:
- **Fixing bugs** in the core engine
- **Writing documentation** to help others
- **Creating example content** for new builders
- **Sharing your modifications** with the community

Your contributions help keep Geoff's vision alive and make NakedMud better for everyone.

## Original Foundations

NakedMud builds upon the excellent work of:

**SocketMud by Brian Graversen** - The original foundation that handled all the complex socket programming, allowing NakedMud to focus on the fun stuff. As Brian wrote: *"Little mud project, which has a command interpreter and supports ANSI colors... has a nifty little help file system, and a few commands (say, quit, who, etc). Also supports MCCP version 1 and 2."*

**Code Snippets by Erwin Andreasen** - Various utility functions and improvements that made their way into SocketMud and subsequently into NakedMud.

We maintain these credits not just out of courtesy, but because NakedMud's success stands on the shoulders of these generous developers who shared their work with the community.

---

*Welcome to NakedMud! Whether you're here to build your first MUD or add features to an existing one, we're excited to see what you'll create. The only limit is your imagination.*

**Happy MUDding!**
