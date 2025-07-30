---
layout: default
title: mudsock Module
parent: Modules
grand_parent: API Reference
nav_order: 10
---

# mudsock Module

The `mudsock` module contains the Python wrapper for sockets and utilities for managing network connections. It provides both the PySocket class (EObj) and utility functions (EFuns) for handling player connections, input processing, and network communication.

**Module Type**: Core EFuns (External Functions) + EObjs (External Objects)  
**Import**: `import mudsock`

## Overview

The mudsock module handles:
- Network socket connections and management
- Input handler stacks for different connection states
- Text editor integration
- Prompt management and display
- Connection state tracking
- Socket-specific auxiliary data

Sockets represent the network connection between the MUD server and a player's client. They manage the flow of data in both directions and handle different states of the connection (login, character creation, in-game, etc.).

## PySocket Class (EObj)

The `Mudsock` class represents a network connection to a player's client.

### Constructor

Sockets are created automatically by the MUD server when players connect. They are not typically instantiated directly in Python code.

### Core Methods

#### send(mssg, dict=None, newline=True)

**Returns**: `None`

Sends a message to the socket. Messages can contain embedded scripts using `[` and `]` brackets.

**Parameters**:
- `mssg` (str): The message to send
- `dict` (dict, optional): Variable dictionary for script evaluation
- `newline` (bool, optional): Whether to append a newline (default: True)

**Example**:
```python
import mudsock

socket = mudsock.Mudsock()  # Assume this is a real socket

# Simple message
socket.send("Welcome to the MUD!")

# Message with script
socket.send("Hello, [me.account.name]!")

# Message with custom variables
vars = {'server_name': 'MyMUD', 'players_online': 42}
socket.send("Welcome to [server_name]! [players_online] players online.", vars)
```

#### send_raw(mssg)

**Returns**: `None`

Sends text to the socket with no appended newline.

**Parameters**:
- `mssg` (str): The message to send

#### close()

**Returns**: `None`

Closes the socket's connection.

**Example**:
```python
import mudsock

socket = mudsock.Mudsock()
socket.send("Goodbye!")
socket.close()
```

### Input Handler Stack

#### push_ih(handler_func, prompt_func, state=None)

**Returns**: `None`

Pushes a new input handler and prompt pair onto the socket's input handler stack.

**Parameters**:
- `handler_func` (function): Function to handle input (takes socket and command string)
- `prompt_func` (function): Function to display prompt (takes socket)
- `state` (str, optional): Optional state value for the handler

**Example**:
```python
import mudsock

def login_handler(socket, input_text):
    """Handle login input"""
    username = input_text.strip()
    if username:
        socket.send(f"Hello, {username}!")
        socket.pop_ih()  # Remove this handler
    else:
        socket.send("Please enter a valid username.")

def login_prompt(socket):
    """Display login prompt"""
    socket.send_raw("Username: ")

# Push the login handler
socket = mudsock.Mudsock()
socket.push_ih(login_handler, login_prompt, "login")
```

#### pop_ih()

**Returns**: `None`

Pops the socket's current input handler from its input handler stack.

#### replace_ih(handler_func, prompt_func, state=None)

**Returns**: `None`

Calls `pop_ih()` followed by `push_ih()`. Effectively replaces the current input handler.

**Parameters**:
- `handler_func` (function): Function to handle input
- `prompt_func` (function): Function to display prompt
- `state` (str, optional): Optional state value

### Text Editor

#### edit_text(dflt_value, on_complete, mode='text')

**Returns**: `None`

Enters the text editor with a default value. When editing is complete, calls the completion function.

**Parameters**:
- `dflt_value` (str): Default text to start with
- `on_complete` (function): Function called when editing completes (takes socket and text)
- `mode` (str, optional): Editor mode - 'text' or 'script' (default: 'text')

**Example**:
```python
import mudsock

def description_complete(socket, new_text):
    """Handle completed description editing"""
    if socket.character:
        socket.character.desc = new_text
        socket.send("Description updated!")
    socket.pop_ih()  # Return to previous input handler

socket = mudsock.Mudsock()
current_desc = socket.character.desc if socket.character else ""
socket.edit_text(current_desc, description_complete, 'text')
```

### Prompt Management

#### bust_prompt()

**Returns**: `None`

Busts the socket's prompt so it will be displayed on the next pulse.

**Example**:
```python
import mudsock

socket = mudsock.Mudsock()
# After some action that should trigger a new prompt
socket.bust_prompt()
```

### Auxiliary Data

#### aux(name)

**Returns**: Auxiliary data object or `None`

Alias for `getAuxiliary(name)`. Returns the socket's auxiliary data of the specified name.

**Parameters**:
- `name` (str): The auxiliary data name

#### getAuxiliary(name)

**Returns**: Auxiliary data object or `None`

Returns the socket's auxiliary data of the specified name.

**Parameters**:
- `name` (str): The auxiliary data name

## Socket Properties

### Connection Information

#### hostname
**Type**: `str` (read-only)  
The DNS address that the socket is connected from.

#### uid
**Type**: `int` (read-only)  
The socket's unique identification number.

#### can_use
**Type**: `bool` (read-only)  
True if the socket is ready for use. Socket becomes available after its DNS address resolves.

### Attached Objects

#### account
**Type**: `PyAccount` (read-only)  
The account currently attached to the socket, or None.

#### character
**Type**: `PyChar` (read-only)  
The character currently attached to the socket, or None.

#### char
**Type**: `PyChar` (read-only)  
Alias for `character`.

#### ch
**Type**: `PyChar` (read-only)  
Alias for `character`.

### State Information

#### state
**Type**: `str` (read-only)  
The state that the socket is in. This corresponds to the state parameter passed to input handlers.

#### has_input
**Type**: `bool` (read-only)  
True if the socket has any input pending.

#### idle_time
**Type**: `int` (read-only)  
How long (in seconds) the socket's input handler has been idle.

### Output Management

#### outbound_text
**Type**: `str`  
The socket's outbound text buffer. Can be modified to add text to be sent.

## Module Functions (EFuns)

### Socket Management

#### socket_list()

**Returns**: `list`

Returns a list of all sockets currently connected.

**Example**:
```python
import mudsock

all_sockets = mudsock.socket_list()
print(f"Connected sockets: {len(all_sockets)}")

for socket in all_sockets:
    if socket.character:
        print(f"  {socket.character.name} from {socket.hostname}")
    else:
        print(f"  Unattached socket from {socket.hostname}")
```

## Usage Patterns

### Login System Implementation

```python
import mudsock, mudsys, account

def handle_connection_greeting(socket):
    """Handle initial connection"""
    greeting = mudsys.sys_getval("greeting")
    if greeting:
        socket.send(greeting)
    else:
        socket.send("Welcome to the MUD!")
    
    # Push login name handler
    socket.push_ih(handle_login_name, login_name_prompt, "login_name")

def login_name_prompt(socket):
    """Prompt for login name"""
    socket.send_raw("Account name: ")

def handle_login_name(socket, input_text):
    """Handle account name input"""
    account_name = input_text.strip().lower()
    
    if not account_name:
        socket.send("Please enter an account name.")
        return
    
    if not account_name.isalnum():
        socket.send("Account names must be alphanumeric.")
        return
    
    # Check if account exists
    if mudsys.account_exists(account_name):
        # Existing account - ask for password
        socket.push_ih(
            lambda s, pwd: handle_login_password(s, pwd, account_name),
            lambda s: s.send_raw("Password: "),
            "login_password"
        )
    else:
        # New account - ask if they want to create it
        socket.send(f"Account '{account_name}' does not exist. Create it? (y/n)")
        socket.push_ih(
            lambda s, choice: handle_create_account_choice(s, choice, account_name),
            lambda s: s.send_raw("Create account: "),
            "create_choice"
        )

def handle_login_password(socket, password, account_name):
    """Handle password input for existing account"""
    if not password.strip():
        socket.send("Please enter your password.")
        return
    
    # Load and verify account
    account_obj = mudsys.load_account(account_name)
    if account_obj and mudsys.password_matches(account_obj, password):
        # Successful login
        mudsys.attach_account_socket(account_obj, socket)
        socket.send(f"Welcome back, {account_obj.name}!")
        
        # Move to character selection
        show_character_menu(socket)
    else:
        socket.send("Invalid password.")
        socket.send("Disconnecting...")
        socket.close()

def handle_create_account_choice(socket, choice, account_name):
    """Handle choice to create new account"""
    choice = choice.strip().lower()
    
    if choice in ['y', 'yes']:
        socket.send("Creating new account...")
        socket.send_raw("Choose a password: ")
        socket.push_ih(
            lambda s, pwd: handle_new_account_password(s, pwd, account_name),
            lambda s: s.send_raw("Password: "),
            "new_password"
        )
    else:
        socket.send("Goodbye!")
        socket.close()

def handle_new_account_password(socket, password, account_name):
    """Handle password input for new account"""
    password = password.strip()
    
    if len(password) < 6:
        socket.send("Password must be at least 6 characters long.")
        return
    
    # Create the account
    new_account = mudsys.create_account(account_name)
    if new_account:
        mudsys.set_password(new_account, password)
        mudsys.do_register(new_account)
        mudsys.attach_account_socket(new_account, socket)
        
        socket.send("Account created successfully!")
        socket.send("You'll need to create a character to play.")
        
        # Move to character creation
        start_character_creation(socket)
    else:
        socket.send("Failed to create account.")
        socket.close()
```

### Character Selection Menu

```python
import mudsock, char

def show_character_menu(socket):
    """Display character selection menu"""
    if not socket.account:
        socket.send("No account attached.")
        socket.close()
        return
    
    chars = socket.account.characters()
    
    socket.send("\n--- Character Selection ---")
    if chars:
        for i, char_name in enumerate(chars, 1):
            socket.send(f"{i}. {char_name}")
        socket.send(f"{len(chars) + 1}. Create new character")
    else:
        socket.send("You have no characters.")
        socket.send("1. Create new character")
    
    socket.send("0. Quit")
    socket.send("")
    
    socket.push_ih(handle_character_choice, character_choice_prompt, "char_select")

def character_choice_prompt(socket):
    """Prompt for character choice"""
    socket.send_raw("Choice: ")

def handle_character_choice(socket, input_text):
    """Handle character selection input"""
    try:
        choice = int(input_text.strip())
        chars = socket.account.characters()
        
        if choice == 0:
            socket.send("Goodbye!")
            socket.close()
        elif 1 <= choice <= len(chars):
            # Load existing character
            char_name = chars[choice - 1]
            character = mudsys.get_player(char_name)
            if character:
                mudsys.attach_char_socket(character, socket)
                socket.send(f"Playing as {character.name}.")
                mudsys.try_enter_game(character)
            else:
                socket.send("Character not found.")
                show_character_menu(socket)
        elif choice == len(chars) + 1:
            # Create new character
            start_character_creation(socket)
        else:
            socket.send("Invalid choice.")
    except ValueError:
        socket.send("Please enter a number.")

def start_character_creation(socket):
    """Start character creation process"""
    socket.send("\n--- Character Creation ---")
    socket.send("What would you like to name your character?")
    socket.push_ih(handle_character_name, char_name_prompt, "char_creation")

def char_name_prompt(socket):
    """Prompt for character name"""
    socket.send_raw("Character name: ")

def handle_character_name(socket, input_text):
    """Handle character name input"""
    char_name = input_text.strip()
    
    if not char_name:
        socket.send("Please enter a character name.")
        return
    
    if not char_name.isalpha():
        socket.send("Character names must contain only letters.")
        return
    
    if len(char_name) < 3 or len(char_name) > 15:
        socket.send("Character names must be 3-15 characters long.")
        return
    
    if mudsys.player_exists(char_name):
        socket.send("That character name is already taken.")
        return
    
    # Create the character
    new_char = mudsys.create_player(char_name)
    if new_char:
        new_char.name = char_name
        socket.account.add_char(new_char)
        mudsys.do_register(new_char)
        mudsys.attach_char_socket(new_char, socket)
        
        socket.send(f"Character '{char_name}' created!")
        socket.send("Welcome to the game!")
        mudsys.try_enter_game(new_char)
    else:
        socket.send("Failed to create character.")
        show_character_menu(socket)
```

### Text Editor Integration

```python
import mudsock

def start_description_editor(socket, target_object):
    """Start editing an object's description"""
    if not target_object:
        socket.send("Nothing to edit.")
        return
    
    current_desc = getattr(target_object, 'desc', '')
    
    def description_complete(sock, new_text):
        """Handle completed description editing"""
        target_object.desc = new_text.strip()
        sock.send("Description updated.")
        
        # Return to previous input handler
        sock.pop_ih()
    
    socket.send("Entering description editor...")
    socket.send("Use .h for help, .s to save and exit, .q to quit without saving.")
    socket.edit_text(current_desc, description_complete, 'text')

def start_script_editor(socket, script_name):
    """Start editing a script"""
    # Load existing script content
    current_script = load_script_content(script_name)
    
    def script_complete(sock, new_script):
        """Handle completed script editing"""
        if save_script_content(script_name, new_script):
            sock.send(f"Script '{script_name}' saved.")
        else:
            sock.send("Failed to save script.")
        
        sock.pop_ih()
    
    socket.send(f"Editing script: {script_name}")
    socket.edit_text(current_script, script_complete, 'script')

def load_script_content(script_name):
    """Load script content from file"""
    try:
        with open(f"scripts/{script_name}.py", 'r') as f:
            return f.read()
    except:
        return "# New script\n"

def save_script_content(script_name, content):
    """Save script content to file"""
    try:
        with open(f"scripts/{script_name}.py", 'w') as f:
            f.write(content)
        return True
    except:
        return False
```

### Socket State Management

```python
import mudsock, auxiliary, storage

class SocketSession:
    """Track socket session information"""
    
    def __init__(self, storage_set=None):
        if storage_set:
            self.connect_time = storage_set.readInt("connect_time")
            self.last_activity = storage_set.readInt("last_activity")
            self.commands_entered = storage_set.readInt("commands_entered")
            self.bytes_sent = storage_set.readInt("bytes_sent")
            self.bytes_received = storage_set.readInt("bytes_received")
        else:
            import time
            current_time = int(time.time())
            self.connect_time = current_time
            self.last_activity = current_time
            self.commands_entered = 0
            self.bytes_sent = 0
            self.bytes_received = 0
    
    def update_activity(self):
        """Update last activity time"""
        import time
        self.last_activity = int(time.time())
    
    def add_command(self):
        """Increment command counter"""
        self.commands_entered += 1
        self.update_activity()
    
    def add_bytes_sent(self, count):
        """Add to bytes sent counter"""
        self.bytes_sent += count
    
    def add_bytes_received(self, count):
        """Add to bytes received counter"""
        self.bytes_received += count
        self.update_activity()
    
    def get_session_duration(self):
        """Get session duration in seconds"""
        import time
        return int(time.time()) - self.connect_time
    
    def store(self):
        set = storage.StorageSet()
        set.storeInt("connect_time", self.connect_time)
        set.storeInt("last_activity", self.last_activity)
        set.storeInt("commands_entered", self.commands_entered)
        set.storeInt("bytes_sent", self.bytes_sent)
        set.storeInt("bytes_received", self.bytes_received)
        return set
    
    def copy(self):
        new_session = SocketSession()
        new_session.connect_time = self.connect_time
        new_session.last_activity = self.last_activity
        new_session.commands_entered = self.commands_entered
        new_session.bytes_sent = self.bytes_sent
        new_session.bytes_received = self.bytes_received
        return new_session
    
    def copyTo(self, to):
        to.connect_time = self.connect_time
        to.last_activity = self.last_activity
        to.commands_entered = self.commands_entered
        to.bytes_sent = self.bytes_sent
        to.bytes_received = self.bytes_received

# Install socket session tracking
auxiliary.install("socket_session", SocketSession, "socket")

def get_socket_info(socket):
    """Get detailed socket information"""
    session = socket.aux("socket_session")
    if not session:
        return "No session data available"
    
    duration = session.get_session_duration()
    hours = duration // 3600
    minutes = (duration % 3600) // 60
    
    info = f"""
Socket Information:
  UID: {socket.uid}
  Hostname: {socket.hostname}
  State: {socket.state}
  Connected: {hours}h {minutes}m
  Commands: {session.commands_entered}
  Bytes Sent: {session.bytes_sent}
  Bytes Received: {session.bytes_received}
  Idle: {socket.idle_time}s
"""
    
    if socket.account:
        info += f"  Account: {socket.account.name}\n"
    
    if socket.character:
        info += f"  Character: {socket.character.name}\n"
    
    return info

# Usage
def who_command(ch, cmd, arg):
    """Show connected players"""
    sockets = mudsock.socket_list()
    
    ch.send("Connected Players:")
    ch.send("-" * 50)
    
    for socket in sockets:
        if socket.character:
            session = socket.aux("socket_session")
            idle = f"{socket.idle_time}s" if socket.idle_time > 0 else "active"
            ch.send(f"{socket.character.name:15} {socket.hostname:20} {idle}")
    
    ch.send(f"\nTotal: {len([s for s in sockets if s.character])} players online")
```

### Connection Monitoring

```python
import mudsock, event

def monitor_connections():
    """Monitor socket connections for issues"""
    sockets = mudsock.socket_list()
    
    for socket in sockets:
        # Check for idle connections
        if socket.idle_time > 1800:  # 30 minutes
            socket.send("You have been idle for 30 minutes.")
            socket.send("You will be disconnected in 5 minutes if you remain idle.")
        
        elif socket.idle_time > 2100:  # 35 minutes
            socket.send("Disconnecting due to inactivity.")
            socket.close()
        
        # Check for stuck connections
        if not socket.can_use:
            # Socket DNS hasn't resolved - might be stuck
            continue
        
        # Check for connections without accounts after reasonable time
        session = socket.aux("socket_session")
        if session and session.get_session_duration() > 300:  # 5 minutes
            if not socket.account and socket.state in ["login_name", "login_password"]:
                socket.send("Login timeout. Disconnecting.")
                socket.close()

# Schedule regular connection monitoring
def start_connection_monitor():
    """Start the connection monitoring system"""
    def monitor_event(owner, data, arg):
        monitor_connections()
        # Schedule next check
        event.start_event(None, 60, monitor_event, None, "connection_monitor")
    
    # Start monitoring every minute
    event.start_event(None, 60, monitor_event, None, "connection_monitor")

# Start monitoring when the MUD boots
start_connection_monitor()
```

## See Also

- [account Module](account.md) - Account management and PyAccount class
- [char Module](char.md) - Character manipulation and PyChar class
- [mudsys Module](mudsys.md) - Core system functions for socket management
- [auxiliary Module](auxiliary.md) - Auxiliary data system for socket extensions
- [Core Concepts: Network Architecture](../../core-concepts/network-architecture.md)
- [Tutorials: Socket Programming](../../tutorials/socket-programming.md)