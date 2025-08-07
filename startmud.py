#!/usr/bin/env python3
"""
NakedMud Startup Manager
=======================

This script provides a beautiful, interactive way to start and manage your NakedMud server.
It includes validation, monitoring, and auto-restart capabilities.
"""

import os
import sys
import time
import signal
import subprocess
import shlex
import platform
import argparse
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

# Global variables
mud_process = None
restart_attempts = 0
MAX_RESTART_ATTEMPTS = 3
mud_settings = None


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def get_mud_process():
    """Check if NakedMud is already running and return its process info"""
    if platform.system() == 'Windows':
        try:
            # Windows implementation using tasklist
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq NakedMud*', '/FO', 'CSV', '/NH'],
                capture_output=True, text=True, check=True
            )
            if 'NakedMud' in result.stdout:
                pid = int(result.stdout.split(',')[1].strip('"'))
                return {'pid': pid, 'port': 'UNKNOWN'}
        except (subprocess.SubprocessError, IndexError, ValueError):
            pass
    else:
        # Unix-like systems - check for running (not zombie) processes
        try:
            # Use ps to get non-zombie NakedMud processes
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True, text=True
            )
            
            for line in result.stdout.split('\n'):
                if 'NakedMud' in line and '<defunct>' not in line and 'Z' not in line.split()[7]:
                    parts = line.split()
                    if len(parts) > 1:
                        pid = int(parts[1])
                        # Try to get the port using lsof
                        try:
                            port_result = subprocess.run(
                                ['lsof', '-Pan', '-p', str(pid), '-i'],
                                capture_output=True, text=True
                            )
                            port = 'UNKNOWN'
                            for port_line in port_result.stdout.split('\n'):
                                if 'LISTEN' in port_line:
                                    port = port_line.split(':')[-1].split(' ')[0]
                                    break
                            return {'pid': pid, 'port': port}
                        except subprocess.SubprocessError:
                            return {'pid': pid, 'port': 'UNKNOWN'}
        except subprocess.SubprocessError:
            pass
    return None


def scan_player_files():
    """Scan player files for staff information"""
    pfiles_dir = Path("lib/players/pfiles")
    if not pfiles_dir.exists():
        return [], {'admin': [], 'scripter': [], 'builder': []}
    
    admin_players = []
    staff_players = {'admin': [], 'scripter': [], 'builder': []}
    
    # Debug: count files found
    files_found = 0
    files_processed = 0
    
    # Scan all alphabetic directories
    for letter_dir in pfiles_dir.iterdir():
        if letter_dir.is_dir() and letter_dir.name.isalpha():
            for pfile in letter_dir.glob("*.pfile"):
                files_found += 1
                try:
                    with open(pfile, 'r') as f:
                        content = f.read()
                    
                    files_processed += 1
                    # Extract player name from filename
                    player_name = pfile.stem
                    
                    # Check for uid = 1 (super admin)
                    if 'uid' in content:
                        for line in content.split('\n'):
                            if line.strip().startswith('uid') and ':' in line:
                                uid_value = line.split(':', 1)[1].strip()
                                if uid_value == '1':
                                    admin_players.append(player_name)
                                break
                    
                    # Check for user groups
                    if 'user_groups' in content:
                        for line in content.split('\n'):
                            if 'user_groups' in line and ':' in line:
                                groups_line = line.split(':', 1)[1].strip()
                                # Parse the groups (comma-separated format like "admin, scripter, builder")
                                groups = [g.strip().lower() for g in groups_line.split(',')]
                                for group in groups:
                                    if group in staff_players:
                                        staff_players[group].append(player_name)
                                break
                                
                except Exception as e:
                    # Skip files that can't be read - but let's see what the error is
                    continue
    

    
    return admin_players, staff_players


def print_server_status():
    """Print the current server status"""
    proc = get_mud_process()
    if proc:
        print(f"{Colors.OKGREEN}✓ NakedMud is running{Colors.ENDC}")
        print(f"   • Process ID: {Colors.BOLD}{proc['pid']}{Colors.ENDC}")
        print(f"   • Port: {Colors.BOLD}{proc['port']}{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}✗ NakedMud is not running{Colors.ENDC}")
    
    if mud_settings:
        print(f"\n{Colors.HEADER}MUD Configuration:{Colors.ENDC}")
        print(f"   • MUD Name: {Colors.BOLD}{mud_settings.get('mud_name', 'NakedMud')}{Colors.ENDC}")
        
        # Scan for admin players and display
        admin_players, staff_players = scan_player_files()
        
        if admin_players:
            # Show admin players with their roles
            admin_player_list = []
            for player in admin_players:
                # Collect roles for this admin player
                player_roles = []
                if player in staff_players['admin']:
                    player_roles.append('🔑')  # Key for admin
                if player in staff_players['scripter']:
                    player_roles.append('📜')  # Scroll for scripter
                if player in staff_players['builder']:
                    player_roles.append('🔨')  # Hammer for builder
                
                if player_roles:
                    roles_str = ''.join(player_roles)
                    admin_player_list.append(f"{player} ({roles_str})")
                else:
                    admin_player_list.append(f"{player} (🔑)")  # Default to admin key if no roles found
            
            admin_display = f"{', '.join(admin_player_list)}"
        else:
            admin_display = "No Admin"
            
        print(f"   • Admin: {Colors.BOLD}{admin_display}{Colors.ENDC}")
        
        # Display staff if any found
        all_staff = set()
        for role_list in staff_players.values():
            all_staff.update(role_list)
        
        if all_staff:
            staff_list = []
            
            # Process each unique staff member
            for player in sorted(all_staff):
                if player in admin_players:
                    continue  # Skip puid=1 players (already shown in Admin line)
                
                # Collect all roles for this player
                player_roles = []
                if player in staff_players['admin']:
                    player_roles.append('🔑')  # Key for admin
                if player in staff_players['scripter']:
                    player_roles.append('📜')  # Scroll for scripter
                if player in staff_players['builder']:
                    player_roles.append('🔨')  # Hammer for builder
                
                if player_roles:
                    roles_str = ''.join(player_roles)
                    staff_list.append(f"{player} ({roles_str})")
            
            if staff_list:
                print(f"   • Staff: {Colors.BOLD}{', '.join(staff_list)}{Colors.ENDC}")
        
        print(f"   • Configured Port: {Colors.BOLD}{mud_settings.get('listening_port', '4000')}{Colors.ENDC}")
        print(f"   • World Path: {Colors.BOLD}{mud_settings.get('world_path', 'Not set')}{Colors.ENDC}")
        print(f"   • Start Room: {Colors.BOLD}{mud_settings.get('start_room', 'Not set')}{Colors.ENDC}")
    print()


def print_logo():
    """Display the NakedMud ASCII logo"""
    clear_screen()
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
{Colors.HEADER}{Colors.BOLD}                     NakedMud Server Manager{Colors.ENDC}
{Colors.OKBLUE}            A content-less MUD engine for your creativity{Colors.ENDC}
"""
    print(logo)
    print_server_status()


def print_status(message, status="", color=Colors.OKCYAN):
    """Print a status message with optional status"""
    if status:
        print(f"{color}{message} {Colors.BOLD}{status}{Colors.ENDC}")
    else:
        print(f"{color}{message}{Colors.ENDC}")


def print_success(message):
    """Print a success message"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message):
    """Print an error message"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_warning(message):
    """Print a warning message"""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def load_muddata():
    """Load and parse the muddata file"""
    muddata_path = Path("lib/muddata")
    if not muddata_path.exists():
        print_error(f"MUD data file not found at: {muddata_path}")
        return None
    
    settings = {}
    try:
        with open(muddata_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and ':' in line and not line.startswith('-'):
                    key, value = line.split(':', 1)
                    settings[key.strip()] = value.strip()
        return settings
    except Exception as e:
        print_error(f"Error reading muddata: {e}")
        return None


def validate_muddata():
    """Validate the MUD configuration"""
    global mud_settings
    print_status("Validating MUD configuration...")
    
    # Check muddata file
    settings = load_muddata()
    if not settings:
        print_error("Failed to load muddata configuration")
        return False, None
    
    # Store settings globally
    mud_settings = settings
    
    # Display current configuration
    print(f"{Colors.HEADER}Current MUD Configuration:{Colors.ENDC}")
    print(f"  • MUD Name: {Colors.BOLD}{settings.get('mud_name', 'NakedMud')}{Colors.ENDC}")
    print(f"  • Listening Port: {Colors.BOLD}{settings.get('listening_port', '4000')}{Colors.ENDC}")
    print(f"  • World Path: {Colors.BOLD}{settings.get('world_path', 'Not set')}{Colors.ENDC}")
    print(f"  • Start Room: {Colors.BOLD}{settings.get('start_room', 'Not set')}{Colors.ENDC}")
    
    # Check required fields
    required_fields = ['mud_name', 'start_room', 'world_path', 'listening_port']
    for field in required_fields:
        if field not in settings or not settings[field]:
            print_error(f"Missing required field in muddata: {field}")
            return False, None
    
    # Check world path (relative to src/ directory)
    world_path = Path("src") / settings['world_path']
    if not world_path.exists():
        print_error(f"World path does not exist: {world_path}")
        return False, None
        
    print_success("MUD configuration is valid")
    
    # Check start room prototype
    start_room = settings['start_room']
    if '@' not in start_room:
        print_error(f"Invalid start room format. Should be 'room_name@zone'")
        return False, None
    
    room_name, zone = start_room.split('@', 1)
    room_proto_path = world_path / "zones" / zone / "rproto" / room_name
    if not room_proto_path.exists():
        print_error(f"Room prototype file not found: {room_proto_path}")
        return False, None
    
    # Verify it's a valid room file by checking for room content
    try:
        with open(room_proto_path, 'r') as f:
            content = f.read()
            if not content.strip():
                print_error(f"Room prototype file is empty: {room_proto_path}")
                return False, None
    except Exception as e:
        print_error(f"Error reading room prototype: {e}")
        return False, None
    
    print_success("MUD configuration validated successfully")
    return True, settings


def start_mud(mudlib_path=None):
    """Start the MUD server"""
    global mud_process, restart_attempts
    
    # Check if already running
    if get_mud_process():
        print_warning("NakedMud is already running!")
        time.sleep(1)
        return True
    
    # Save current directory
    original_dir = os.getcwd()
    
    try:
        # Change to src directory
        os.chdir("src")
        
        print_status("Starting NakedMud server...")
        
        # Build command with optional mudlib path
        cmd = ["./NakedMud"]
        if mudlib_path:
            cmd.extend(["--mudlib-path", mudlib_path])
        
        # Start the MUD process in background
        mud_process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid if platform.system() != 'Windows' else None
        )
        
        # Wait a moment to see if it starts successfully
        time.sleep(2)
        
        # Check if the process is still running
        if mud_process.poll() is None:
            print_success(f"Server started successfully with PID: {mud_process.pid}")
            return True
        else:
            print_error("Server failed to start")
            return False
            
    except Exception as e:
        print_error(f"Error starting server: {e}")
        return False
    finally:
        # Always return to original directory
        os.chdir(original_dir)


def tail_logs():
    """Show the last few lines of the latest log file"""
    log_dir = Path("../log")
    if not log_dir.exists():
        print_error("Log directory not found!")
        return
    
    log_files = sorted(log_dir.glob("*.log"), key=os.path.getmtime, reverse=True)
    if not log_files:
        print_warning("No log files found!")
        return
    
    latest_log = log_files[0]
    print_status(f"\nTailing log file: {latest_log.name}")
    print("-" * 50)
    
    try:
        with open(latest_log, 'r') as f:
            # Show last 20 lines
            lines = f.readlines()[-20:]
            print(''.join(lines), end='')
    except Exception as e:
        print_error(f"Error reading log file: {e}")


def show_menu():
    """Show the interactive menu"""
    while True:  # Keep showing the menu until a valid choice is made
        print("\n" + "="*50)
        print(f"{Colors.HEADER}NakedMud Server Manager{Colors.ENDC}")
        print("="*50)
        print(f"1. {Colors.OKBLUE}Start/Restart Server{Colors.ENDC}")
        print(f"2. {Colors.OKCYAN}View Server Logs{Colors.ENDC}")
        print(f"3. {Colors.WARNING}Stop Server{Colors.ENDC}")
        print(f"4. {Colors.FAIL}Exit{Colors.ENDC}")
        
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            if choice in ['1', '2', '3', '4']:
                return choice
                
            print_error("Invalid choice. Please enter a number between 1 and 4.")
            time.sleep(1)
            print_logo()  # Redraw the screen on invalid choice
            
        except KeyboardInterrupt:
            print("\n" + "="*50)
            print("Exiting...")
            sys.exit(0)
            break
        else:
            print_warning("Invalid choice. Please try again.")


def view_logs():
    """View the server logs"""
    log_dir = Path("log")
    if not log_dir.exists():
        print_error(f"Log directory not found: {log_dir}")
        input("\nPress Enter to continue...")
        return
    
    log_files = sorted(log_dir.glob("*.log"), key=os.path.getmtime, reverse=True)
    if not log_files:
        print_error("No log files found")
        input("\nPress Enter to continue...")
        return
    
    # Show most recent log
    log_file = log_files[0]
    print(f"\n{Colors.HEADER}Viewing log: {log_file.name}{Colors.ENDC}")
    print("-" * 50)
    
    try:
        # Use 'tail' to show the end of the log file
        process = subprocess.run(
            ["tail", "-n", "50", str(log_file)],
            capture_output=True,
            text=True
        )
        
        if process.stderr:
            print_error(f"Error reading log: {process.stderr}")
        else:
            print(process.stdout)
    except Exception as e:
        print_error(f"Error reading log file: {e}")
    
    input("\nPress Enter to continue...")


def stop_mud():
    """Stop the MUD server"""
    proc = get_mud_process()
    if not proc:
        print_warning("NakedMud is not running")
        time.sleep(1)
        return
    
    try:
        print_status("Stopping NakedMud server...")
        pid = proc['pid']
        
        if platform.system() == 'Windows':
            subprocess.run(['taskkill', '/PID', str(pid), '/F'], check=True)
        else:
            # Send SIGTERM first
            try:
                os.kill(pid, signal.SIGTERM)
                # Wait for graceful shutdown
                for i in range(5):  # Wait up to 5 seconds
                    time.sleep(1)
                    if not get_mud_process():
                        break
                
                # If still running, force kill
                if get_mud_process():
                    print_warning("Server did not stop gracefully, forcing...")
                    os.kill(pid, signal.SIGKILL)
                    time.sleep(1)
                    
            except OSError as e:
                if e.errno == 3:  # No such process
                    pass  # Process already dead
                else:
                    raise
        
        # Clean up any zombie processes
        try:
            subprocess.run(['pkill', '-9', 'NakedMud'], capture_output=True)
        except subprocess.SubprocessError:
            pass
            
        # Wait a moment for cleanup
        time.sleep(1)
        
        # Verify it's stopped
        if get_mud_process():
            print_warning("Process may still be running")
        else:
            print_success("Server stopped successfully")
            
    except Exception as e:
        print_error(f"Error stopping server: {e}")
    
    time.sleep(1)


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


def main():
    """Main function"""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description='NakedMud Startup Manager')
        parser.add_argument('--mudlib-path', type=str, help='Path to the mudlib directory (relative to src/)')
        args = parser.parse_args()
        
        # Validate mudlib path if provided
        mudlib_path = None
        if args.mudlib_path:
            is_valid, result = validate_mudlib_path(args.mudlib_path)
            if not is_valid:
                print_error(f"Error: {result}")
                sys.exit(1)
            mudlib_path = result
            print_status(f"Using mudlib path: {mudlib_path}")
        
        # Print the logo and status
        print_logo()
        
        # Validate configuration
        valid, settings = validate_muddata()
        if not valid:
            print_error("\nFailed to validate MUD configuration. Please check the errors above.")
            input("\nPress Enter to exit...")
            sys.exit(1)
        
        # Check if server is running, if not start it automatically
        if not get_mud_process():
            print_status("\nNakedMud is not running. Starting server automatically...")
            if start_mud(mudlib_path):
                print_success("Server started successfully!")
                time.sleep(2)
            else:
                print_error("Failed to start server automatically.")
                time.sleep(2)
        
        # Main menu loop
        while True:
            print_logo()
            choice = show_menu()
            
            if choice == '1':
                print_logo()
                print_status("Starting/Restarting NakedMud server...")
                stop_mud()  # Make sure it's stopped first
                if start_mud(mudlib_path):
                    print_success("Server started successfully!")
                    time.sleep(2)
            elif choice == '2':
                print_logo()
                view_logs()
            elif choice == '3':
                print_logo()
                stop_mud()
            elif choice == '4':
                print("\nGoodbye!")
                break
                
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        if mud_process:
            try:
                os.killpg(os.getpgid(mud_process.pid), signal.SIGTERM)
            except:
                pass
        sys.exit(0)
    except Exception as e:
        print_error(f"An error occurred: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()
