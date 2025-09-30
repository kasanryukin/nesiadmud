# NakedMud Socials Module

A friendly Python module that brings expressive social interactions to your NakedMud world! This module lets players use pre-made emotes like `grin`, `laugh`, `hug`, and many more with smart targeting and customizable modifiers.

## Installation

### Option 1: Download and Extract
1. Download the socials module files
2. Extract to your `lib/pymodules/socials/` directory
3. Restart your MUD or reload Python modules

### Option 2: Git Submodule
```bash
cd lib/pymodules/
git submodule add <repository-url> socials
git submodule update --init --recursive
```

## Commands Added

The module adds these builder/admin commands:

- **`socials`** - List all available socials or view details of a specific social
- **`soclink <new_cmd> <existing_social>`** - Create command aliases for existing socials  
- **`socunlink <cmd>`** - Remove a social command from the system

## Social Data File

Socials are stored in: `lib/misc/socials`

## What It Does

The socials module transforms simple commands into rich, contextual emotes that enhance roleplay. 
You need to modify your emotes to use $X and $x if you want modifiers.

- **Simple usage**: `grin` → "You grin evilly."
- **With targets**: `grin bob` → "You grin evilly at Bob."
- **Custom modifiers**: `grin stupidly` → "You grin stupidly."
- **Advanced syntax**: `grin warmly at alice` → "You grin warmly at Alice."

## Message Placeholders

When creating or editing socials, you can use these special placeholders:

- **`$X`** - Replaced with user modifier (e.g., "evilly", "stupidly") or default adverb
- **`$x`** - Replaced with the social's default adjective
- **Standard placeholders** - `$n` (character name), `$N` (target name), etc.

### Example Social Message:
```
to_char_notgt: "You grin $X."
to_room_notgt: "$n grins $X."
```

With default adverb "evilly":
- `grin` → "You grin evilly."
- `grin stupidly` → "You grin stupidly."

## Backwards Compatibility

This module is fully backwards compatible with the original hardcoded socials system. Existing socials continue to work exactly as before, while gaining the new modifier and targeting features.

