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
