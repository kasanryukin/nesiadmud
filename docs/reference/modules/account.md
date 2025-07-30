---
layout: default
title: account Module
parent: Modules
grand_parent: API Reference
nav_order: 5
---

# account Module

The `account` module contains the Python wrapper for player accounts. It provides the PyAccount class (EObj) for managing player account information, character lists, and account-specific data.

**Module Type**: EObjs (External Objects)  
**Import**: `import account`

## Overview

The account module handles:
- Player account management and authentication
- Character registration and listing
- Account-specific auxiliary data
- Multi-character account systems
- Account persistence and storage

In NakedMud, accounts serve as the top-level container for player information, with individual characters belonging to accounts. This allows players to have multiple characters under a single login.

## PyAccount Class (EObj)

The `Account` class represents a player account that can contain multiple characters.

### Constructor

Accounts are typically created through the `mudsys.create_account()` function rather than direct instantiation.

### Core Methods

#### add_char(name_or_char)

**Returns**: `None`

Adds a new character to the account's list of registered characters.

**Parameters**:
- `name_or_char` (str or PyChar): The character name or character object to add

**Example**:
```python
import account, char, mudsys

# Create an account
new_account = mudsys.create_account("player123")

# Create a character
hero = char.load_mob("player_template", room)
hero.name = "Aragorn"

# Add character to account
new_account.add_char(hero)

# Or add by name
new_account.add_char("Legolas")
```

#### characters()

**Returns**: `list`

Returns a list of character names registered to the account.

**Example**:
```python
import account

player_account = account.Account()  # Assume this is a loaded account
char_names = player_account.characters()

for char_name in char_names:
    print(f"Character: {char_name}")
```

### Auxiliary Data

#### aux(name)

**Returns**: Auxiliary data object or `None`

Alias for `getAuxiliary(name)`. Returns the account's auxiliary data of the specified name.

**Parameters**:
- `name` (str): The auxiliary data name

#### getAuxiliary(name)

**Returns**: Auxiliary data object or `None`

Returns the account's auxiliary data of the specified name.

**Parameters**:
- `name` (str): The auxiliary data name

**Example**:
```python
import account, auxiliary

# Define account preferences auxiliary data
class AccountPreferences:
    def __init__(self, storage_set=None):
        if storage_set:
            self.color_enabled = storage_set.readBool("color_enabled")
            self.sound_enabled = storage_set.readBool("sound_enabled")
            self.email = storage_set.readString("email")
        else:
            self.color_enabled = True
            self.sound_enabled = False
            self.email = ""
    
    def store(self):
        import storage
        set = storage.StorageSet()
        set.storeBool("color_enabled", self.color_enabled)
        set.storeBool("sound_enabled", self.sound_enabled)
        set.storeString("email", self.email)
        return set
    
    def copy(self):
        new_prefs = AccountPreferences()
        new_prefs.color_enabled = self.color_enabled
        new_prefs.sound_enabled = self.sound_enabled
        new_prefs.email = self.email
        return new_prefs
    
    def copyTo(self, to):
        to.color_enabled = self.color_enabled
        to.sound_enabled = self.sound_enabled
        to.email = self.email

# Install the auxiliary data
auxiliary.install("account_prefs", AccountPreferences, "account")

# Use with an account
player_account = account.Account()
prefs = player_account.aux("account_prefs")
if prefs:
    prefs.color_enabled = False
    prefs.email = "player@example.com"
```

## Account Properties

### Basic Information

#### name
**Type**: `str` (read-only)  
The account's name/username. This is immutable once set.

**Example**:
```python
import account

player_account = account.Account()
print(f"Account name: {player_account.name}")
```

## Usage Patterns

### Account Creation and Management

```python
import mudsys, account

def create_new_player_account(username, password):
    """Create a new player account with validation"""
    
    # Check if account already exists
    if mudsys.account_exists(username):
        return None, "Account already exists"
    
    # Create the account
    new_account = mudsys.create_account(username)
    if not new_account:
        return None, "Failed to create account"
    
    # Set password
    mudsys.set_password(new_account, password)
    
    # Register the account
    mudsys.do_register(new_account)
    
    return new_account, "Account created successfully"

# Usage
account_obj, message = create_new_player_account("newplayer", "securepassword")
if account_obj:
    print(f"Created account: {account_obj.name}")
else:
    print(f"Error: {message}")
```

### Character Management

```python
import account, char, mudsys

def create_character_for_account(account_obj, char_name, race="human"):
    """Create a new character and add it to an account"""
    
    # Check if character name is available
    if mudsys.player_exists(char_name):
        return None, "Character name already exists"
    
    # Create the character
    new_char = mudsys.create_player(char_name)
    if not new_char:
        return None, "Failed to create character"
    
    # Set character properties
    new_char.race = race
    new_char.name = char_name
    
    # Add to account
    account_obj.add_char(new_char)
    
    # Register the character
    mudsys.do_register(new_char)
    
    return new_char, "Character created successfully"

def list_account_characters(account_obj):
    """List all characters belonging to an account"""
    char_names = account_obj.characters()
    
    characters_info = []
    for char_name in char_names:
        char_obj = mudsys.get_player(char_name)
        if char_obj:
            info = {
                'name': char_obj.name,
                'race': char_obj.race,
                'level': getattr(char_obj, 'level', 1),  # Assuming level exists
                'last_login': getattr(char_obj, 'last_login', 'Never')
            }
            characters_info.append(info)
    
    return characters_info

# Usage
player_account = mudsys.load_account("player123")
if player_account:
    # Create a new character
    new_char, message = create_character_for_account(player_account, "Gandalf", "human")
    
    # List all characters
    chars = list_account_characters(player_account)
    for char_info in chars:
        print(f"Character: {char_info['name']} ({char_info['race']})")
```

### Account Preferences System

```python
import account, auxiliary, storage

class AccountSettings:
    """Comprehensive account settings system"""
    
    def __init__(self, storage_set=None):
        if storage_set:
            # Load settings from storage
            self.color_enabled = storage_set.readBool("color_enabled")
            self.sound_enabled = storage_set.readBool("sound_enabled")
            self.auto_save = storage_set.readBool("auto_save")
            self.email = storage_set.readString("email")
            self.timezone = storage_set.readString("timezone")
            self.language = storage_set.readString("language")
            
            # Load notification preferences
            notify_set = storage_set.readSet("notifications")
            self.notify_login = notify_set.readBool("login")
            self.notify_tells = notify_set.readBool("tells")
            self.notify_channels = notify_set.readBool("channels")
        else:
            # Default settings
            self.color_enabled = True
            self.sound_enabled = False
            self.auto_save = True
            self.email = ""
            self.timezone = "UTC"
            self.language = "english"
            
            # Default notifications
            self.notify_login = True
            self.notify_tells = True
            self.notify_channels = False
    
    def store(self):
        set = storage.StorageSet()
        set.storeBool("color_enabled", self.color_enabled)
        set.storeBool("sound_enabled", self.sound_enabled)
        set.storeBool("auto_save", self.auto_save)
        set.storeString("email", self.email)
        set.storeString("timezone", self.timezone)
        set.storeString("language", self.language)
        
        # Store notification preferences
        notify_set = storage.StorageSet()
        notify_set.storeBool("login", self.notify_login)
        notify_set.storeBool("tells", self.notify_tells)
        notify_set.storeBool("channels", self.notify_channels)
        set.storeSet("notifications", notify_set)
        
        return set
    
    def copy(self):
        new_settings = AccountSettings()
        new_settings.color_enabled = self.color_enabled
        new_settings.sound_enabled = self.sound_enabled
        new_settings.auto_save = self.auto_save
        new_settings.email = self.email
        new_settings.timezone = self.timezone
        new_settings.language = self.language
        new_settings.notify_login = self.notify_login
        new_settings.notify_tells = self.notify_tells
        new_settings.notify_channels = self.notify_channels
        return new_settings
    
    def copyTo(self, to):
        to.color_enabled = self.color_enabled
        to.sound_enabled = self.sound_enabled
        to.auto_save = self.auto_save
        to.email = self.email
        to.timezone = self.timezone
        to.language = self.language
        to.notify_login = self.notify_login
        to.notify_tells = self.notify_tells
        to.notify_channels = self.notify_channels

# Install the settings system
auxiliary.install("account_settings", AccountSettings, "account")

def update_account_setting(account_obj, setting_name, value):
    """Update a specific account setting"""
    settings = account_obj.aux("account_settings")
    if not settings:
        return False, "Settings not found"
    
    if hasattr(settings, setting_name):
        setattr(settings, setting_name, value)
        return True, f"Updated {setting_name} to {value}"
    else:
        return False, f"Unknown setting: {setting_name}"

# Usage
player_account = mudsys.load_account("player123")
if player_account:
    success, message = update_account_setting(player_account, "color_enabled", False)
    print(message)
```

### Account Statistics and Tracking

```python
import account, auxiliary, storage, time

class AccountStats:
    """Track account statistics and activity"""
    
    def __init__(self, storage_set=None):
        if storage_set:
            self.creation_date = storage_set.readInt("creation_date")
            self.last_login = storage_set.readInt("last_login")
            self.total_playtime = storage_set.readInt("total_playtime")
            self.login_count = storage_set.readInt("login_count")
            self.characters_created = storage_set.readInt("characters_created")
        else:
            current_time = int(time.time())
            self.creation_date = current_time
            self.last_login = 0
            self.total_playtime = 0
            self.login_count = 0
            self.characters_created = 0
    
    def record_login(self):
        """Record a login event"""
        self.last_login = int(time.time())
        self.login_count += 1
    
    def add_playtime(self, seconds):
        """Add playtime in seconds"""
        self.total_playtime += seconds
    
    def increment_characters(self):
        """Increment character creation count"""
        self.characters_created += 1
    
    def get_account_age_days(self):
        """Get account age in days"""
        current_time = int(time.time())
        return (current_time - self.creation_date) // 86400
    
    def store(self):
        set = storage.StorageSet()
        set.storeInt("creation_date", self.creation_date)
        set.storeInt("last_login", self.last_login)
        set.storeInt("total_playtime", self.total_playtime)
        set.storeInt("login_count", self.login_count)
        set.storeInt("characters_created", self.characters_created)
        return set
    
    def copy(self):
        new_stats = AccountStats()
        new_stats.creation_date = self.creation_date
        new_stats.last_login = self.last_login
        new_stats.total_playtime = self.total_playtime
        new_stats.login_count = self.login_count
        new_stats.characters_created = self.characters_created
        return new_stats
    
    def copyTo(self, to):
        to.creation_date = self.creation_date
        to.last_login = self.last_login
        to.total_playtime = self.total_playtime
        to.login_count = self.login_count
        to.characters_created = self.characters_created

# Install the stats system
auxiliary.install("account_stats", AccountStats, "account")

def get_account_summary(account_obj):
    """Get a summary of account information"""
    stats = account_obj.aux("account_stats")
    if not stats:
        return "No statistics available"
    
    chars = account_obj.characters()
    
    summary = f"""
Account: {account_obj.name}
Created: {stats.get_account_age_days()} days ago
Characters: {len(chars)} ({stats.characters_created} total created)
Logins: {stats.login_count}
Total Playtime: {stats.total_playtime // 3600} hours
Last Login: {time.ctime(stats.last_login) if stats.last_login else 'Never'}

Characters:
"""
    
    for char_name in chars:
        summary += f"  - {char_name}\n"
    
    return summary

# Usage
player_account = mudsys.load_account("player123")
if player_account:
    print(get_account_summary(player_account))
```

### Account Security and Validation

```python
import account, mudsys, time

def validate_account_access(account_obj, password, ip_address=None):
    """Validate account access with security checks"""
    
    # Check password
    if not mudsys.password_matches(account_obj, password):
        return False, "Invalid password"
    
    # Check if account is locked (example using auxiliary data)
    security = account_obj.aux("account_security")
    if security and hasattr(security, 'locked') and security.locked:
        return False, "Account is locked"
    
    # Check for suspicious activity (example)
    if security and hasattr(security, 'failed_attempts'):
        if security.failed_attempts >= 5:
            return False, "Too many failed login attempts"
    
    return True, "Access granted"

def record_login_attempt(account_obj, success, ip_address=None):
    """Record login attempt for security tracking"""
    security = account_obj.aux("account_security")
    if not security:
        # Create security data if it doesn't exist
        return
    
    current_time = int(time.time())
    
    if success:
        security.last_successful_login = current_time
        security.failed_attempts = 0  # Reset failed attempts on success
        if ip_address:
            security.last_login_ip = ip_address
    else:
        security.failed_attempts += 1
        security.last_failed_attempt = current_time

# Usage in login system
def attempt_account_login(username, password, ip_address=None):
    """Attempt to log into an account"""
    
    # Load the account
    account_obj = mudsys.load_account(username)
    if not account_obj:
        return None, "Account not found"
    
    # Validate access
    valid, message = validate_account_access(account_obj, password, ip_address)
    
    # Record the attempt
    record_login_attempt(account_obj, valid, ip_address)
    
    if valid:
        # Update login statistics
        stats = account_obj.aux("account_stats")
        if stats:
            stats.record_login()
        
        return account_obj, "Login successful"
    else:
        return None, message

# Usage
account_obj, message = attempt_account_login("player123", "password", "192.168.1.100")
if account_obj:
    print(f"Welcome back, {account_obj.name}!")
else:
    print(f"Login failed: {message}")
```

## Integration with Other Systems

### Socket Integration

```python
import account, mudsock

def attach_account_to_socket(account_obj, socket):
    """Attach an account to a socket connection"""
    mudsys.attach_account_socket(account_obj, socket)
    
    # Send welcome message
    socket.send(f"Welcome, {account_obj.name}!")
    
    # Show character selection menu
    show_character_menu(socket, account_obj)

def show_character_menu(socket, account_obj):
    """Display character selection menu"""
    chars = account_obj.characters()
    
    if not chars:
        socket.send("You have no characters. Create a new character? (y/n)")
        socket.push_ih(handle_new_character, lambda s: s.send_raw("Create character: "))
        return
    
    socket.send("Select a character:")
    for i, char_name in enumerate(chars, 1):
        socket.send(f"{i}. {char_name}")
    socket.send(f"{len(chars) + 1}. Create new character")
    socket.send("0. Quit")
    
    socket.push_ih(
        lambda s, cmd: handle_character_choice(s, cmd, account_obj, chars),
        lambda s: s.send_raw("Choice: ")
    )

def handle_character_choice(socket, choice, account_obj, char_list):
    """Handle character selection"""
    try:
        choice_num = int(choice.strip())
        
        if choice_num == 0:
            socket.send("Goodbye!")
            socket.close()
        elif 1 <= choice_num <= len(char_list):
            # Load selected character
            char_name = char_list[choice_num - 1]
            character = mudsys.get_player(char_name)
            if character:
                mudsys.attach_char_socket(character, socket)
                mudsys.try_enter_game(character)
            else:
                socket.send("Character not found.")
                show_character_menu(socket, account_obj)
        elif choice_num == len(char_list) + 1:
            # Create new character
            start_character_creation(socket, account_obj)
        else:
            socket.send("Invalid choice.")
            show_character_menu(socket, account_obj)
    except ValueError:
        socket.send("Please enter a number.")
        show_character_menu(socket, account_obj)
```

## See Also

- [mudsys Module](mudsys.md) - Core system functions for account management
- [char Module](char.md) - Character management and PyChar class
- [mudsock Module](mudsock.md) - Socket handling for account connections
- [auxiliary Module](auxiliary.md) - Auxiliary data system for account extensions
- [Core Concepts: Account System](../../core-concepts/account-system.md)
- [Tutorials: Account Management](../../tutorials/account-management.md)