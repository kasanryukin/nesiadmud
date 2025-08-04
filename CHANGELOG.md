# NakedMud v4.1.0
Compiled and tested on multiple platforms
### ADDED
- Enhanced settings management with better error handling and parameterization
- Support for pyenv across multiple platforms (Linux, Mac, Windows)
- Improved documentation and test organization
### FIXED
- Fixed dictionary clear to use native C API for Python
- Resolved zone creation crash when using Python API
- Corrected Unicode parsing in color hooks
- Fixed IAC MCCP processing to prevent buffer read failures
### MODIFIED
- Reorganized test files into dedicated tests directory
- Updated documentation and removed Python 2.x references
- Improved Python initialization process

---

# NakedMud v4.0.1
Compiled and tested on Debian Linux
### BREAKING CHANGES
- Python 2.x support has been removed in favor of Python 3.9+
- System modified to use Cython for better Python 3.10+ compatibility
### MODIFIED
- SConstruct file updated to automatically include libm for compilation
### FIXED
- Addressed Unicode-related issues during copyover
- Fixed GCC10 compatibility by updating scripts to use proper extern declarations
- Resolved IAC handling in socket communication
- Fixed doc command to properly handle backspace overprints
- Added IAC,GA to fix prompt display issues in various clients

---

# NakedMud v4.0.0
Initial release of the NakedMud 4.x series
### MAJOR CHANGES
- Complete overhaul of the codebase for Python 3.9+ compatibility
- Modernized build system and project structure
- Improved error handling and logging
- Enhanced security model for Python sandboxing
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
