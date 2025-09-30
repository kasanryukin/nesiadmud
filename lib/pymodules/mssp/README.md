# NakedMud MSSP Module

A comprehensive MSSP (Mud Server Status Protocol) implementation for NakedMud that provides configurable server information broadcasting and runtime configuration management.

## Installation

### Option 1: Download and Extract
1. Download the MSSP module files
2. Extract to your `lib/pymodules/mssp/` directory
3. Restart your MUD or reload Python modules

### Option 2: Git Submodule
```bash
cd lib/pymodules/
git submodule add <repository-url> mssp
git submodule update --init --recursive
```

## Commands Added

The module adds these admin commands:

- **`msspedit`** - Online configuration editor for MSSP settings (admin level required)

## Configuration Files

- **Default config**: `lib/pymodules/mssp/default.mssp` - Template configuration
- **Runtime config**: `lib/misc/mssp-config` - Active configuration (auto-created from default)

## What It Does and Technical Details

The MSSP module responds to IAC MSSP telnet negotiation sequences (`IAC SB MSSP <data> IAC SE`) and returns structured key-value data packages containing configuration variables loaded from StorageSet `mssp-config` file and dynamic game state from mudsys. It provides an OLC editor that modifies the StorageSet configuration and triggers immediate reload of the in-memory MSSPData instance. The module hooks into the game heartbeat to refresh player counts, uptime statistics, and connection data for real-time accuracy.

### MSSP Response Flow
```
Client Request:  IAC WILL MSSP
Server Response: IAC DO MSSP
Client Query:    IAC SB MSSP IAC SE
Server Data:     IAC SB MSSP
                 NAME<NUL>MyMUD<NUL>
                 PLAYERS<NUL>5<NUL>
                 UPTIME<NUL>12345<NUL>
                 ...
                 IAC SE
```

## Configuration Variables

### Core Settings (from mudsettings)
- **NAME** - Server name
- **PORT** - Server port
- **SCREENWIDTH** - Default screen width

### Optional Settings (from config file)
- **CONTACT** - Admin contact email
- **WEBSITE** - Server website URL
- **FAMILY** - MUD family/codebase
- **GENRE** - Game genre (Fantasy, Sci-Fi, etc.)
- **GAMEPLAY** - Gameplay style (Hack and Slash, Roleplay, etc.)
- **GAMESYSTEM** - Game system used
- **SUBGENRE** - Specific subgenre
- **STATUS** - Server status
- **MINIMUM_AGE** - Minimum player age (integer)
- **INTERMUD** - Intermud connectivity (boolean)
- **LANGUAGE** - Primary language
- **LOCATION** - Server location
- **CREATED** - Server creation date

## Usage Example

```
> msspedit
MSSP Configuration Editor
1) CONTACT: admin@example.com
2) WEBSITE: http://example.com
3) FAMILY: NakedMud
...
Enter choice (1-13, q to quit): 1
Enter new CONTACT: newadmin@example.com
CONTACT updated to: newadmin@example.com
```

## Technical Details

- Uses typed StorageSet methods (`readInt`/`storeInt`, `readBool`/`storeBool`)
- Config changes immediately reload MSSP data
- Admin-level permissions required for configuration
- Maintains backward compatibility with existing installations
