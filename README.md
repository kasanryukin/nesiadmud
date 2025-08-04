# NakedMud 4.1

## INTRO
NakedMud is a modern MUD server written in C with Python 3+ integration, designed for extensibility and performance. This fork continues the development of the original NakedMud 3.8.1 by Geoff Hollis, focusing on stability improvements, modernization, and better Python integration.

## CREDITS
- **Original NakedMud**: Geoff Hollis
- **Current Maintainer**: LimpingNinja
- **Contributors**: See Git commit history for full list of contributors

## COMPILING AND RUNNING

### Prerequisites
- Python 3.9+ (managed via pyenv recommended)
- SCons build system
- GCC/Clang compiler
- Python development headers

### Using pyenv (Recommended)
```bash
# Install pyenv (Linux/Mac)
curl https://pyenv.run | bash

# Install Python version (check .python-version for required version)
pyenv install

# Install build dependencies
pip install setuptools scons
```

### Linux
```bash
# Install build dependencies
sudo apt-get update
sudo apt-get install -y build-essential python3-dev python3-pip

# Install SCons
pip install scons

# Build NakedMud
scons
```

### MacOS
```bash
# Install Xcode command line tools
xcode-select --install

# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install pyenv scons

# Build NakedMud
scons
```

### Windows
```bash
# Install Python 3.9+ from python.org
# Install Visual Studio Build Tools with C++ workload
# Install SCons via pip
pip install scons

# Build NakedMud
scons
```

## FUTURE
- Continue migrating game logic to Python modules
- Improve documentation and create example zones
- Enhance Python sandboxing and security
- Expand test coverage
- Modernize network code and improve performance
- Create a comprehensive developer documentation
- Implement better error handling and logging
- Add support for modern protocols (MCCP, GMCP, etc.)

## LICENSE
NakedMud is open source software. See the LICENSE file for details.
