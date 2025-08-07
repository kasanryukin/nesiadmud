#!/usr/bin/env python3
"""
NakedMud Installation Script
============================

This script helps you configure your NakedMud server by setting up the basic
configuration in the muddata file. It will ask you for essential settings
and create or update the configuration as needed.

Author: Kevin Morgan (LimpingNinja)
"""

import os
import sys
from pathlib import Path

# ANSI Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_logo():
    """Display the NakedMud ASCII logo"""
    logo = f"""
{Colors.OKCYAN}{Colors.BOLD}
 ███▄    █  ▄▄▄       ██ ▄█▀▓█████ ▓█████▄     ███▄ ▄███▓ █    ██ ▓█████▄ 
 ██ ▀█   █ ▒████▄     ██▄█▒ ▓█   ▀ ▒██▀ ██▌   ▓██▒▀█▀ ██▒ ██  ▓██▒▒██▀ ██▌
▓██  ▀█ ██▒▒██  ▀█▄  ▓███▄░ ▒███   ░██   █▌   ▓██    ▓██░▓██  ▒██░░██   █▌
▓██▒  ▐▌██▒░██▄▄▄▄██ ▓██ █▄ ▒▓█  ▄ ░▓█▄   ▌   ▒██    ▒██ ▓▓█  ░██░░▓█▄   ▌
▒██░   ▓██░ ▓█   ▓██▒▒██▒ █▄░▒████▒░▒████▓    ▒██▒   ░██▒▒▒█████▓ ░▒████▓ 
░ ▒░   ▒ ▒  ▒▒   ▓▒█░▒ ▒▒ ▓▒░░ ▒░ ░ ▒▒▓  ▒    ░ ▒░   ░  ░░▒▓▒ ▒ ▒  ▒▒▓  ▒ 
░ ░░   ░ ▒░  ▒   ▒▒ ░░ ░▒ ▒░ ░ ░  ░ ░ ▒  ▒    ░  ░      ░░░▒░ ░ ░  ░ ▒  ▒ 
   ░   ░ ░   ░   ▒   ░ ░░ ░    ░    ░ ░  ░    ░      ░    ░░░ ░ ░  ░ ░  ░ 
         ░       ░  ░░  ░      ░  ░   ░              ░      ░        ░     
                                    ░                              ░       
{Colors.ENDC}
{Colors.HEADER}{Colors.BOLD}                    Welcome to NakedMud Setup!{Colors.ENDC}
{Colors.OKBLUE}              A content-less MUD engine for your creativity{Colors.ENDC}
"""
    print(logo)

def get_input_with_default(prompt, default_value, color=Colors.OKCYAN):
    """Get user input with a default value"""
    full_prompt = f"{color}{prompt} [{Colors.BOLD}enter for {default_value}{Colors.ENDC}{color}]{Colors.ENDC}: "
    user_input = input(full_prompt).strip()
    return user_input if user_input else str(default_value)

def validate_port(port_str):
    """Validate that the port is a valid number in the right range"""
    try:
        port = int(port_str)
        if 1024 <= port <= 65535:
            return True, port
        else:
            return False, "Port must be between 1024 and 65535"
    except ValueError:
        return False, "Port must be a valid number"

def validate_mudlib_path(path_str):
    """Validate mudlib path - check if it exists relative to src/ directory"""
    script_dir = Path(__file__).parent
    src_dir = script_dir / "src"
    
    # First try the path as given
    test_path = src_dir / path_str
    if test_path.exists() and test_path.is_dir():
        return True, path_str
    
    # If that doesn't work, try adding ../ prefix
    if not path_str.startswith('../'):
        prefixed_path = f"../{path_str}"
        test_path = src_dir / prefixed_path
        if test_path.exists() and test_path.is_dir():
            return True, prefixed_path
    
    return False, f"Directory '{path_str}' does not exist (checked relative to src/ directory)"

def validate_world_path(world_path_str, mudlib_path):
    """Validate that world path is within the mudlib directory"""
    script_dir = Path(__file__).parent
    src_dir = script_dir / "src"
    
    # Resolve the mudlib path
    mudlib_full_path = (src_dir / mudlib_path).resolve()
    
    # Try the world path as given
    world_full_path = (src_dir / world_path_str).resolve()
    
    # Check if world path is within mudlib path
    try:
        world_full_path.relative_to(mudlib_full_path)
        return True, world_path_str
    except ValueError:
        return False, f"World path must be within the mudlib directory ({mudlib_path})"

def read_existing_muddata(muddata_path):
    """Read existing muddata file and return as a dictionary"""
    settings = {}
    if muddata_path.exists():
        with open(muddata_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and ':' in line and not line.startswith('-'):
                    key, value = line.split(':', 1)
                    settings[key.strip()] = value.strip()
    return settings

def write_muddata(muddata_path, settings):
    """Write the muddata file with proper formatting"""
    with open(muddata_path, 'w') as f:
        # Write settings in a specific order for consistency
        ordered_keys = [
            'start_room', 'paragraph_indent', 'pulses_per_second', 'world_path',
            'listening_port', 'screen_width', 'message_somewhere', 'message_something',
            'message_someone', 'message_nothing_special', 'message_what',
            'mud_name', 'puid'
        ]
        
        # Calculate the maximum key length for alignment
        max_key_length = max(len(key) for key in ordered_keys if key in settings)
        
        for key in ordered_keys:
            if key in settings:
                f.write(f"{key:<{max_key_length}} : {settings[key]}\n")
        
        # Add any additional settings that weren't in our ordered list
        for key, value in settings.items():
            if key not in ordered_keys:
                f.write(f"{key:<{max_key_length}} : {value}\n")
        
        f.write("-\n")

def main():
    """Main installation function"""
    print_logo()
    
    print(f"{Colors.OKGREEN}This script will help you configure your NakedMud server.{Colors.ENDC}")
    print(f"{Colors.OKGREEN}Press Enter to accept default values, or type your own.{Colors.ENDC}\n")
    
    # Get mudlib path first
    print(f"{Colors.HEADER}{Colors.BOLD}=== MUD Library Path Configuration ==={Colors.ENDC}\n")
    print(f"{Colors.OKBLUE}The mudlib path is where NakedMud stores all its data files.{Colors.ENDC}")
    print(f"{Colors.OKBLUE}This path should be relative to the src/ directory.{Colors.ENDC}\n")
    
    mudlib_path = None
    while True:
        mudlib_input = get_input_with_default(
            "Where should the mudlib directory be located?",
            "../lib"
        )
        is_valid, result = validate_mudlib_path(mudlib_input)
        if is_valid:
            mudlib_path = result
            break
        else:
            print(f"{Colors.FAIL}Error: {result}{Colors.ENDC}")
    
    # Determine the muddata file path based on mudlib path
    script_dir = Path(__file__).parent
    src_dir = script_dir / "src"
    muddata_path = src_dir / mudlib_path / "muddata"
    
    # Create mudlib directory if it doesn't exist
    muddata_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Read existing settings
    settings = read_existing_muddata(muddata_path)
    
    # Set default values for all required settings (world_path will be set dynamically)
    default_settings = {
        'start_room': 'tavern_entrance@examples',
        'paragraph_indent': '4',
        'pulses_per_second': '10',
        'world_path': f'{mudlib_path}/world',  # Dynamic based on mudlib path
        'listening_port': '4000',
        'screen_width': '80',
        'message_somewhere': 'somewhere',
        'message_something': 'something',
        'message_someone': 'someone',
        'message_nothing_special': 'You see nothing special.',
        'message_what': 'What?',
        'mud_name': 'NakedMud',
        'puid': '0'
    }
    
    # Merge existing settings with defaults
    for key, default_value in default_settings.items():
        if key not in settings:
            settings[key] = default_value
    
    print(f"{Colors.HEADER}{Colors.BOLD}=== MUD Configuration ==={Colors.ENDC}\n")
    
    # Get MUD name
    settings['mud_name'] = get_input_with_default(
        "What is the name of your MUD?",
        settings.get('mud_name', 'NakedMud')
    )
    
    # Get listening port with validation
    while True:
        port_input = get_input_with_default(
            "What port should the MUD listen on?",
            settings.get('listening_port', '4000')
        )
        is_valid, result = validate_port(port_input)
        if is_valid:
            settings['listening_port'] = str(result)
            break
        else:
            print(f"{Colors.FAIL}Error: {result}{Colors.ENDC}")
    
    # Get world path with validation
    print(f"\n{Colors.OKBLUE}World data must be stored within the mudlib directory ({mudlib_path}).{Colors.ENDC}")
    while True:
        world_input = get_input_with_default(
            "Where should world data be stored?",
            settings.get('world_path', f'{mudlib_path}/world')
        )
        is_valid, result = validate_world_path(world_input, mudlib_path)
        if is_valid:
            settings['world_path'] = result
            break
        else:
            print(f"{Colors.FAIL}Error: {result}{Colors.ENDC}")
    
    # Get start room
    settings['start_room'] = get_input_with_default(
        "What room should new players start in?",
        settings.get('start_room', 'tavern_entrance@examples')
    )
    
    # Reset PUID to 0 for fresh installation
    settings['puid'] = '0'
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== Configuration Summary ==={Colors.ENDC}")
    print(f"{Colors.OKBLUE}Mudlib Path:{Colors.ENDC} {mudlib_path}")
    print(f"{Colors.OKBLUE}MUD Name:{Colors.ENDC} {settings['mud_name']}")
    print(f"{Colors.OKBLUE}Listening Port:{Colors.ENDC} {settings['listening_port']}")
    print(f"{Colors.OKBLUE}World Path:{Colors.ENDC} {settings['world_path']}")
    print(f"{Colors.OKBLUE}Start Room:{Colors.ENDC} {settings['start_room']}")
    
    # Confirm before writing
    print(f"\n{Colors.WARNING}Save this configuration?{Colors.ENDC}", end=" ")
    confirm = input(f"{Colors.OKCYAN}[Y/n]{Colors.ENDC}: ").strip().lower()
    
    if confirm in ('', 'y', 'yes'):
        try:
            write_muddata(muddata_path, settings)
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✓ Configuration saved successfully!{Colors.ENDC}")
            print(f"{Colors.OKGREEN}Configuration written to: {muddata_path}{Colors.ENDC}")
            
            print(f"\n{Colors.HEADER}{Colors.BOLD}=== Important Notes ==={Colors.ENDC}")
            print(f"{Colors.WARNING}• The PUID has been reset to 0{Colors.ENDC}")
            print(f"{Colors.WARNING}• The next player account created will have full administrative privileges{Colors.ENDC}")
            print(f"{Colors.WARNING}• Make sure to create your admin account first!{Colors.ENDC}")
            
            print(f"\n{Colors.HEADER}{Colors.BOLD}=== Next Steps ==={Colors.ENDC}")
            print(f"{Colors.OKBLUE}1. Compile the MUD: {Colors.BOLD}scons{Colors.ENDC}")
            print(f"{Colors.OKBLUE}2. Start the server: {Colors.BOLD}cd src && ./NakedMud{Colors.ENDC}")
            print(f"{Colors.OKBLUE}3. Connect to: {Colors.BOLD}localhost:{settings['listening_port']}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}4. Create your admin account first!{Colors.ENDC}")
            
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}Happy MUDding! 🎉{Colors.ENDC}")
            
        except Exception as e:
            print(f"\n{Colors.FAIL}Error writing configuration: {e}{Colors.ENDC}")
            sys.exit(1)
    else:
        print(f"\n{Colors.WARNING}Configuration cancelled.{Colors.ENDC}")
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Installation cancelled by user.{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.FAIL}Unexpected error: {e}{Colors.ENDC}")
        sys.exit(1)
