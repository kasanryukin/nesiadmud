*v4.1.1 In progress* **Git commits:** 53143f1..HEAD

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
