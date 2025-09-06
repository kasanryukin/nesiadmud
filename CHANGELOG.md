# NakedMud v4.3.5
**Git commits:** a576f0d..463850bsc
Compiled and tested on multiple platforms

⚠️ **CRITICAL FIX RELEASE** - This version fixes critical issues in v4.3.0. **DO NOT USE v4.3.0** - upgrade immediately to v4.3.5.
### MAJOR CHANGES
- **Body system overhaul** - removed hardcoded NUM_BODYPOS system, body position types now fully dynamic with string-based identification instead of integer constants
- **Layered equipment system** - equipment positions now support multiple items per body part using lists instead of single object slots
### ADDED
- **Vitality module** with health management and commands: hp, damage (admin), heal (admin), pray
- **Equipment system** with wielded/equipped item types and commands: wield, unwield, equip, gear
- **Python command fallthrough** support (return -1 to pass control to C implementation)
- **Admin configuration commands:** entityconfig, gearconfig, msspedit, mssp
- **Python look command implementation** with full C parity including nested searches and EDESC support
- **Enhanced Python bindings** for look functions and extra descriptions: mud.look_at_*(), room.get_edesc(), obj.get_edesc()
### FIXED
- Broken gear and entities submodule integration from v4.3.0
- Body position type expansion and equipment layering functionality
- Submodule stability across entities, gear, MSSP, and Ardne modules
### MODIFIED
- Body part data structure changed from single equipment slot to equipment list
- Position types changed from integer constants to dynamic string identifiers
- Enhanced cmd_manip.py with expanded equipment handling
### UPGRADE NOTES
- **CRITICAL:** v4.3.0 was broken - upgrade immediately to v4.3.5
- Run `git submodule update --init --recursive` to get fixed submodule versions
- **New commands available:**
  - Vitality: hp, damage (admin), heal (admin), pray
  - Equipment: wield, unwield, equip, gear
- Body system now fully dynamic with layered equipment support

---

# NakedMud v4.3.0 [BROKEN - DO NOT USE]
**Git commits:** 3dabceb..a576f0d
Compiled and tested on multiple platforms
### MAJOR CHANGES
- **New git submodules baseline** - entities, gear, MSSP, and Ardne zone modules establish the new standard for NakedMud modularity
- **Dynamic body system enhancement** - body position types and sizes now use dynamic lists instead of hardcoded arrays
### ADDED
- **Git submodules:** entities, gear, MSSP, and Ardne zone modules
- **Python hook support** - item type initialization hooks for enhanced extensibility
- **Short-look option** - quality of life improvement for room descriptions
### FIXED
- **Buffer overflow and formatting** - resolved critical crash and edge cases in character descriptions
- **Generic find return value** - corrected Py_BuildValue format from "Os" to "OO" (closes #7)
- **Socket compilation** - added missing pyplugs.h include in pysocket.c
### MODIFIED
- Updated zone structure and organization
- Improved documentation in compiling_and_running.md
- Updated README.md with logo
### UPGRADE NOTES
- **Git submodules:** Run `git submodule update --init --recursive` to initialize all new submodules
- **New Python APIs:** Enhanced body system with dynamic position types and sizes
- **MSSP Protocol:** Binary data support added for telnet protocol compliance
- **New commands:**
  - `entityconfig` (admin) - comprehensive entities configuration editor for body position types, body sizes, and races
  - `gearconfig` (admin) - equipment and item management configuration editor
  - `msspedit` (admin) - MSSP protocol configuration editor
  - `mssp` (admin) - display current MSSP status and information

---

# NakedMud v4.2.0
**Git commits:** a1332c9..3dabceb
Compiled and tested on multiple platforms
### MAJOR CHANGES
- **Python module management system** - enhanced Python integration with startup hooks and module management
- **Socials Module Conversion from C to Python** - **BREAKING CHANGE** socials system rewritten in Python and removed from C codebase, see upgrade notes for details
- **Race and body system Python exposure** - comprehensive Python API for character races and body mechanics
- **Git Submodules for Python modules** - started using git submodules to expose extensibility beyond the core codebase
### ADDED
- cmd_exists function to check command existence in Python
- @@@ prefix for preserving original text formatting in buffer output
- Python startup hooks and module management infrastructure
- Enhanced race and body system Python bindings
### MODIFIED
- Refactored socials system to use git submodule architecture for p
- Updated README.md with improved documentation
- Clarified attribution requirements and reorganized license content
### REMOVED
- Legacy socials module dependencies in favor of Python implementation
### UPGRADE NOTES
- **New Python APIs available:**
  - `mudsys.cmd_exists(cmd_name)` - check if command exists in master table
  - `world` module with 15+ functions for body/race/worn system management
  - Body functions: `add_bodysize()`, `remove_bodysize()`, `get_bodysizes()`, `add_bodypos_type()`, `remove_bodypos_type()`, `get_bodypos_types()`
  - Race functions: `add_race()`, `remove_race()`, `get_races()`, `get_race_info()`
  - Worn functions: `get_worn_types()`, `get_worn_type_positions()`, `remove_worn_type()`, `worn_type_exists()`, `get_worn_type_count()`
- **Socials system migration:** C socials module completely removed - now uses Python submodule at `lib/pymodules/socials/`
- **Git submodules:** Run `git submodule update --init lib/pymodules/socials` to initialize just the socials submodule, or `git submodule update --init --recursive` if you want all modules
- **BREAKING CHANGE - Build changes:** Socials no longer compiled from C source - ensure Python socials submodule is properly initialized by running `git submodule update --init lib/pymodules/socials` (for socials only) or `git submodule update --init --recursive` (for all modules) OR manually download and unarchive https://github.com/NakedMud/socials into `lib/pymodules/socials/`. Upgrading from previous versions will lose the socials system until this step is completed.

---

# NakedMud v4.1.3
**Git commits:** c3cf689..69fff5b
Compiled and tested on multiple platforms
### ADDED
- **Character bodysize property** - new Python-accessible character attribute for size-based mechanics
### FIXED
- **Copyover mudlib path preservation** - custom mudlib paths now persist through server restarts
### MODIFIED
- Enhanced greeting screen and MOTD with improved visual formatting and updated content
### UPGRADE NOTES
- **Critical copyover fix:** Previous versions had a major bug where copyovers would fail for servers running with custom mudlib paths (using `--mudlib-path`). This has been resolved - custom mudlib paths now persist correctly through copyovers.

---

# NakedMud v4.1.2
**Git commits:** e0d4174..c3cf689
Compiled and tested on multiple platforms
### MAJOR CHANGES
- **Live reload system** - reload prototypes and help files with safe, in-place instance replacement
### ADDED
- Reload commands for prototypes and help files with live replacement
- Configurable mudlib path support in server manager with dynamic file path resolution
- Enhanced help system with ASCII header and organized command categories
### FIXED
- startmud.py mudlib_path argument handling not working correctly
### MODIFIED
- Improved mudlib path validation (accept absolute paths, normalize relative paths)
- Reorganized resettable room order in example zone data
- Improved help command behavior with role-based footer and organized display
### UPGRADE NOTES
- **New reload commands (builder):**
  - `rreload <room>`
  - `mreload <mobile> [room|all]`
  - `oreload <object> [room|all]`
  - `hreload <keyword>`
- **Behavior:** Reloads from disk without reboot; `room|all` replaces live instances safely.
- **Mudlib path:** You can now pass `--mudlib-path <path>` to `startmud.py`; absolute paths are accepted and relative paths are normalized. Ensure `muddata` and `world/` are under the mudlib directory.

---
# NakedMud v4.1.1
**Git commits:** 53143f1..e0d4174
Compiled and tested on multiple platforms
### MAJOR CHANGES
- **Trigger system expansion** - pre-command interception and heartbeat automation for NPCs and objects
### ADDED
- Pre-command trigger system with command blocking and priority-based execution
- Heartbeat triggers for automated NPC and object behaviors
- ISSUES.md tracking for known bugs and limitations
### FIXED
- Enhanced Python error handling in OLC prototype loading
### MODIFIED
- Improved trigger attachment error messages and validation
- Updated trigger system documentation with comprehensive examples

---
# NakedMud v4.1.0
**Git commits:** d29252c..53143f1
Compiled and tested on multiple platforms
### MAJOR CHANGES
- **Python-based MUD server manager** (`startmud.py`) with monitoring and auto-restart capabilities
- **Interactive installation script** (`install.py`) for streamlined MUD setup
- **Complete documentation reorganization** - converted to markdown format and consolidated structure
### ADDED
- **MUD identity settings** - configurable mud_name and admin_name in muddata
- **Parameterized default settings** - expanded muddata with configurable messages and defaults
- Enhanced settings management with better error handling and port configuration
- Support for pyenv across multiple platforms (Linux, Mac, Windows)
### FIXED
- Fixed LIBDIR configuration issues
### MODIFIED
- Reorganized test files into dedicated tests directory
- Improved Python initialization process
- Removed old Python 2.x stub commentary references from documentation
### REMOVED
- Removed wizard_name setting in favor of admin_name for consistency

---

# NakedMud v4.0.1
**Git commits:** 8e14c7b..d29252c
Compiled and tested on Debian Linux
### FIXED
- Fixed dictionary clear to use native C API for Python (Issue #5)
- Resolved zone creation crash when using Python API (Issue #4)
- Corrected Unicode parsing in color hooks
- Fixed IAC MCCP processing to prevent buffer read failures
- Fixed LIBDIR configuration issues
- Fixed doc command to properly handle backspace overprints
- Added IAC,GA to fix prompt display issues in various clients
- Improved IAC handling in socket communication
### ADDED
- Support for pyenv across multiple platforms (Linux, Mac, Windows)

---

# NakedMud v4.0.0
**Git commits:** up to 8e14c7b
Initial release of the NakedMud 4.x series
### MAJOR CHANGES
- **[breaking] Complete codebase overhaul** - full Python 3.9+ compatibility rewrite
- **Modernized build system** - updated project structure and compilation
- **Enhanced security model** - improved Python sandboxing architecture
### ADDED
- Support for modern Python features and syntax
- Better integration with Python's type system
- Improved documentation and examples
### REMOVED
- Python 2.x compatibility layer
- Deprecated and legacy code paths
### FIXED
- Various memory leaks and stability issues
- Improved handling of network connections
- Better error recovery mechanisms
